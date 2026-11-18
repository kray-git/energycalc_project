import csv
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent.parent
data_dir = project_root / "data"


def _read_delimited_file(filename: str, base_dir: Path = None) -> list:
    directory = base_dir if base_dir is not None else data_dir
    path = directory / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Expected data file not found: {path}. "
            f"Check that the directory points at the right data folder."
        )

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(row) for row in reader]
    return rows


def load_appliances(base_dir: Path = None) -> list:
    rows = _read_delimited_file("appliances.csv", base_dir)
    for row in rows:
        row["default_watts"] = float(row["default_watts"])
        row["typical_hours_per_day"] = float(row["typical_hours_per_day"])
    return rows


def load_tariffs(base_dir: Path = None) -> list:
    rows = _read_delimited_file("tariffs.csv", base_dir)
    for row in rows:
        row["min_kwh"] = float(row["min_kwh"])
        row["max_kwh"] = float(row["max_kwh"])
        row["rate_ghs_per_kwh"] = float(row["rate_ghs_per_kwh"])
    return rows


def load_solar_panels(base_dir: Path = None) -> list:
    rows = _read_delimited_file("solar_panels.csv", base_dir)
    for row in rows:
        row["capacity_kw"] = float(row["capacity_kw"])
        row["cost_ghs"] = float(row["cost_ghs"])
        row["efficiency"] = float(row["efficiency"])
        row["system_losses"] = float(row["system_losses"])
        row["expected_lifespan_years"] = int(row["expected_lifespan_years"])
        row["maintenance_rate"] = float(row["maintenance_rate"])
    return rows


def load_wind_turbines(base_dir: Path = None) -> list:
    rows = _read_delimited_file("wind_turbines.csv", base_dir)
    for row in rows:
        row["rated_capacity_kw"] = float(row["rated_capacity_kw"])
        row["cost_ghs"] = float(row["cost_ghs"])
        row["capacity_factor"] = float(row["capacity_factor"])
        row["expected_lifespan_years"] = int(row["expected_lifespan_years"])
        row["maintenance_rate"] = float(row["maintenance_rate"])
    return rows


def load_biomass_systems(base_dir: Path = None) -> list:
    rows = _read_delimited_file("biomass_systems.csv", base_dir)
    for row in rows:
        row["rated_capacity_kw"] = float(row["rated_capacity_kw"])
        row["conversion_efficiency"] = float(row["conversion_efficiency"])
        row["cost_ghs"] = float(row["cost_ghs"])
        row["expected_lifespan_years"] = int(row["expected_lifespan_years"])
        row["maintenance_rate"] = float(row["maintenance_rate"])
    return rows


def load_hydro_systems(base_dir: Path = None) -> list:
    rows = _read_delimited_file("hydro_systems.csv", base_dir)
    for row in rows:
        row["typical_head_m"] = float(row["typical_head_m"])
        row["typical_flow_m3s"] = float(row["typical_flow_m3s"])
        row["turbine_efficiency"] = float(row["turbine_efficiency"])
        row["cost_ghs"] = float(row["cost_ghs"])
        row["expected_lifespan_years"] = int(row["expected_lifespan_years"])
        row["maintenance_rate"] = float(row["maintenance_rate"])
    return rows


def load_emission_factors(base_dir: Path = None) -> dict:
    rows = _read_delimited_file("emission_factors.csv", base_dir)
    factors = {}
    for row in rows:
        factors[row["source"]] = float(row["kg_co2_per_kwh"])
    return factors
