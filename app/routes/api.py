from flask import Blueprint, jsonify, request
from app.extensions import cache

from app.data.data_loader import (
    load_appliances, load_solar_panels, load_wind_turbines,
    load_biomass_systems, load_hydro_systems, load_tariffs,
)
from app.models.appliance import Appliance
from app.models.energy_profile import EnergyProfile
from app.models.energy_source import source_registry
from app.calculators.comparison_engine import ComparisonEngine
from app.recommendations.recommendation_engine import RecommendationEngine
from app.services.location_service import (
    LocationService,
    LocationNotFound,
    LocationServiceUnavailable,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _sanitize_for_json(value):
    if isinstance(value, float) and (value == float("inf") or value == float("-inf")):
        return None
    if isinstance(value, dict):
        return {k: _sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_for_json(v) for v in value]
    return value


@api_bp.route("/appliances", methods=["GET"])
@cache.cached(timeout=3600)
def get_appliances():
    return jsonify(load_appliances())


@api_bp.route("/location", methods=["POST"])
@cache.cached(timeout=3600)
def resolve_location():
    payload = request.get_json(force=True, silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    text = payload.get("location_text") or payload.get("location")

    try:
        if latitude is not None and longitude is not None:
            result = LocationService.reverse_geocode(
                float(latitude), float(longitude)
            )
        elif text:
            result = LocationService.geocode(text)
        else:
            return jsonify({
                "error": "Provide either latitude/longitude or location_text"
            }), 400

        return jsonify(result)

    except (TypeError, ValueError) as e:
        return jsonify({"error": str(e)}), 400
    except ConnectionError as e:
        return jsonify({"error": f"Location service unavailable: {e}"}), 503


@api_bp.route("/location/validate", methods=["POST"])
@cache.cached(timeout=3600)
def validate_location():
    payload = request.get_json(force=True, silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    text = payload.get("location_text") or payload.get("location")
    if not text or not str(text).strip():
        return jsonify({
            "valid": False,
            "message": "Enter a town or area name",
            "location": None,
        })

    return jsonify(LocationService.validate(str(text)))


def _validate_compare_payload(payload):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."

    for key in ("source_a", "source_b"):
        value = payload.get(key)
        if value is None:
            return f"{key} is required."
        if not isinstance(value, str):
            return f"{key} must be a source name, not {type(value).__name__}."
        if value.strip().lower() not in source_registry:
            return (f"Unknown energy source {value!r}. Choose from: "
                    f"{', '.join(sorted(source_registry))}.")

    if payload["source_a"].strip().lower() == payload["source_b"].strip().lower():
        return "Choose two different energy sources to compare."

    profile = payload.get("energy_profile")
    if not isinstance(profile, dict):
        return "energy_profile must be an object."

    mode = profile.get("mode", "appliance")
    if mode not in ("direct", "appliance", "appliances"):
        return f"Unknown input mode {mode!r}. Use 'direct' or 'appliances'."

    if mode == "direct":
        kwh = profile.get("monthly_kwh")
        if kwh is None:
            return "Enter your monthly consumption in kWh."
        try:
            kwh = float(kwh)
        except (TypeError, ValueError):
            return "Monthly consumption must be a number."
        if kwh != kwh or kwh in (float("inf"), float("-inf")):
            return "Monthly consumption must be a real number."
        if kwh <= 0:
            return "Monthly consumption must be greater than zero."
        if kwh > 100000:
            return "Monthly consumption looks too high. Check the figure."
    else:
        appliances = profile.get("appliances")
        if not isinstance(appliances, list) or not appliances:
            return "Add at least one appliance, or switch to direct entry."
        for index, item in enumerate(appliances, start=1):
            if not isinstance(item, dict):
                return f"Appliance {index} is not valid."
            try:
                watts = float(item.get("watts", 0))
                quantity = float(item.get("quantity", 1))
                hours = float(item.get("hours", 0))
            except (TypeError, ValueError):
                return f"Appliance {index} has a non-numeric value."
            name = item.get("name") or f"Appliance {index}"
            if watts <= 0:
                return f"{name}: wattage must be greater than zero."
            if quantity < 1:
                return f"{name}: quantity must be at least 1."
            if not 0 < hours <= 24:
                return f"{name}: hours per day must be between 0 and 24."

    years = payload.get("period_years", 10)
    try:
        years = int(years)
    except (TypeError, ValueError):
        return "Assessment period must be a whole number of years."
    if not 1 <= years <= 50:
        return "Assessment period must be between 1 and 50 years."

    return None


@api_bp.route("/compare", methods=["POST"])
def compare_sources():
    payload = request.get_json(force=True, silent=True)

    error = _validate_compare_payload(payload)
    if error:
        return jsonify({"error": error, "error_type": "invalid_input"}), 400

    try:
        profile = _build_profile(payload.get("energy_profile", {}))
        profile.calculate_total_energy()
        profile.calculate_peak_load()


        source_a = _build_source(payload["source_a"], profile)
        source_b = _build_source(payload["source_b"], profile)

        engine = ComparisonEngine(
            source_a=source_a,
            source_b=source_b,
            profile=profile,
            location=payload.get("location", ""),
            period_years=int(payload.get("period_years", 10)),
        )


        if payload.get("latitude") and payload.get("longitude"):
            try:
                engine.explicit_coordinates = (
                    float(payload["latitude"]), float(payload["longitude"])
                )
            except (TypeError, ValueError):
                pass

        if not engine.validate_matchup():
            return jsonify({"error": "source_a and source_b must be different sources"}), 400

        results = engine.run_comparison()

        recommender = RecommendationEngine()
        priority = payload.get("priority", "balanced")
        results["recommendation"] = recommender.recommend_source(results, priority)

        return jsonify(_sanitize_for_json(results))

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except LocationNotFound as e:


        return jsonify({
            "error": str(e),
            "error_type": "location_not_found",
            "field": "location",
        }), 400

    except LocationServiceUnavailable as e:


        return jsonify({
            "error": str(e),
            "error_type": "location_unavailable",
            "field": "location",
        }), 503

    except ConnectionError as e:


        return jsonify({
            "error": str(e),
            "error_type": "weather_unavailable",
        }), 503

    except ValueError as e:
        return jsonify({"error": str(e), "error_type": "invalid_input"}), 400


def _build_profile(profile_payload: dict) -> EnergyProfile:
    profile = EnergyProfile()
    mode = profile_payload.get("mode", "appliance")

    if mode == "appliance":
        for item in profile_payload.get("appliances", []):
            appliance = Appliance(
                name=item["name"],
                power_rating_w=float(item["watts"]),
                quantity=int(item["quantity"]),
                hours_per_day=float(item["hours"]),
            )
            profile.add_appliance(appliance)
    else:
        profile.direct_monthly_kwh = float(profile_payload.get("monthly_kwh", 0))
        profile.direct_peak_kw = float(profile_payload.get("peak_kw", 0))

    return profile


def _annual_generation(source, profile) -> float:
    try:
        return source.calculate_energy(profile, 1)
    except Exception:
        return 0.0


def _build_source(source_key: str, profile=None):
    if source_key not in source_registry:
        raise ValueError(f"Unknown source: {source_key!r}")

    source_class = source_registry[source_key]

    if source_key == "grid":


        tariffs = load_tariffs()
        rate = tariffs[0]["rate_ghs_per_kwh"] if tariffs else 1.24
        grid = source_class(tariff_rate=rate)
        grid.selected_model = {
            "name": "ECG Residential supply",
            "capacity_kw": None,
            "cost_ghs": 0.0,
            "lifespan_years": None,
            "annual_generation_kwh": None,
            "coverage_percent": 100.0,
            "selection_reason": "mains electricity, billed on PURC residential bands",
            "specs": ["no equipment to buy", "billed on cumulative tariff bands"],
            "alternatives": [],
        }
        return grid

    if source_key == "solar":
        rows = load_solar_panels()
        builder = lambda r: source_class(
            panel_capacity_kw=r["capacity_kw"],
            installation_cost=r["cost_ghs"],
            maintenance_rate=r["maintenance_rate"],
            expected_lifespan_years=r["expected_lifespan_years"],
            system_losses=r.get("system_losses", 0.14),
        )
    elif source_key == "wind":
        rows = load_wind_turbines()
        builder = lambda r: source_class(
            rated_capacity_kw=r["rated_capacity_kw"],
            installation_cost=r["cost_ghs"],
            maintenance_rate=r["maintenance_rate"],
            expected_lifespan_years=r["expected_lifespan_years"],
            capacity_factor=r["capacity_factor"],
        )
    elif source_key == "biomass":
        rows = load_biomass_systems()
        builder = lambda r: source_class(
            feedstock_type=r["feedstock_type"],
            conversion_efficiency=r["conversion_efficiency"],
            installation_cost=r["cost_ghs"],
            maintenance_rate=r["maintenance_rate"],
            expected_lifespan_years=r["expected_lifespan_years"],
            rated_capacity_kw=r["rated_capacity_kw"],
        )
    elif source_key == "hydro":
        rows = load_hydro_systems()
        builder = lambda r: source_class(
            flow_rate_m3s=r["typical_flow_m3s"],
            head_height_m=r["typical_head_m"],
            installation_cost=r["cost_ghs"],
            maintenance_rate=r["maintenance_rate"],
            expected_lifespan_years=r["expected_lifespan_years"],
            turbine_efficiency=r["turbine_efficiency"],
        )
    else:
        raise ValueError(f"No builder implemented for source: {source_key!r}")

    if not rows:
        raise ValueError(f"No catalogue rows for {source_key!r}")

    if profile is None or not getattr(profile, "annual_demand", 0):
        chosen = builder(rows[0])
        chosen.selected_model = _describe_model(
            rows[0], chosen, 0.0, 0.0, "default", []
        )
        return chosen

    demand = profile.annual_demand

    candidates = []
    for row in rows:
        source = builder(row)
        generation = _annual_generation(source, profile)
        candidates.append({
            "row": row,
            "source": source,
            "generation": generation,
            "coverage": (generation / demand * 100) if demand else 0.0,
        })

    adequate = [c for c in candidates if c["generation"] >= demand]

    if adequate:
        adequate.sort(key=lambda c: c["source"].installation_cost)
        winner = adequate[0]
        reason = "smallest option that fully meets your demand"
    else:
        candidates.sort(key=lambda c: c["generation"], reverse=True)
        winner = candidates[0]
        reason = "largest option available, but it still cannot meet your demand on its own"

    alternatives = [
        {
            "name": _model_name(c["row"]),
            "cost_ghs": round(c["source"].installation_cost, 2),
            "annual_generation_kwh": round(c["generation"], 1),
            "coverage_percent": round(c["coverage"], 1),
            "chosen": c is winner,
        }
        for c in candidates
    ]

    chosen = winner["source"]
    chosen.selected_model = _describe_model(
        winner["row"], chosen, winner["generation"], winner["coverage"],
        reason, alternatives,
    )
    return chosen


def _model_name(row: dict) -> str:
    return row.get("model") or row.get("system_type") or "Unnamed model"


def _describe_model(row, source, generation, coverage, reason, alternatives):
    return {
        "name": _model_name(row),
        "capacity_kw": row.get("capacity_kw") or row.get("rated_capacity_kw"),
        "cost_ghs": round(getattr(source, "installation_cost", 0.0), 2),
        "lifespan_years": row.get("expected_lifespan_years"),
        "annual_generation_kwh": round(generation, 1),
        "coverage_percent": round(coverage, 1),
        "selection_reason": reason,
        "specs": _model_specs(row),
        "alternatives": alternatives,
    }


def _model_specs(row: dict) -> list:
    specs = []
    if row.get("capacity_kw"):
        specs.append(f"{row['capacity_kw']} kW panel array")
    if row.get("rated_capacity_kw"):
        specs.append(f"{row['rated_capacity_kw']} kW rated output")
    if row.get("efficiency"):
        specs.append(f"{float(row['efficiency']) * 100:.0f}% panel efficiency")
    if row.get("capacity_factor"):
        specs.append(f"{float(row['capacity_factor']) * 100:.0f}% capacity factor")
    if row.get("feedstock_type"):
        specs.append(f"runs on {row['feedstock_type'].lower()}")
    if row.get("conversion_efficiency"):
        specs.append(f"{float(row['conversion_efficiency']) * 100:.0f}% conversion efficiency")
    if row.get("typical_head_m"):
        specs.append(f"needs {row['typical_head_m']} m head, "
                     f"{row['typical_flow_m3s']} m3/s flow")
    if row.get("expected_lifespan_years"):
        specs.append(f"{row['expected_lifespan_years']}-year expected life")
    return specs
