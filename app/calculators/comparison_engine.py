from dataclasses import dataclass, asdict, field
from typing import Any, Dict

from app.models.energy_source import Solar, Wind
from app.calculators.energy_calculator import EnergyCalculator
from app.calculators.financial_calculator import FinancialCalculator
from app.calculators.carbon_calculator import CarbonCalculator
from app.services.weather_service import WeatherService
from app.services.location_service import (
    LocationService,
    LocationNotFound,
    LocationServiceUnavailable,
)
from app.services.tariff_service import TariffService
from app.data.data_loader import load_emission_factors


@dataclass
class ComparisonResult:
    source_name: str

    energy_supplied_kwh: float = 0.0

    energy_generated_kwh: float = 0.0
    energy_delivered_kwh: float = 0.0
    energy_shortfall_kwh: float = 0.0
    energy_surplus_kwh: float = 0.0
    coverage_percent: float = 0.0
    installation_cost_ghs: float = 0.0
    annual_operating_cost_ghs: float = 0.0
    maintenance_cost_ghs: float = 0.0
    grid_topup_cost_ghs: float = 0.0
    total_cost_ghs: float = 0.0
    emissions_kg: float = 0.0
    grid_topup_emissions_kg: float = 0.0
    total_emissions_kg: float = 0.0
    selected_model: dict = None
    payback_years: float = float("inf")
    lifetime_savings_ghs: float = 0.0
    notes: list = field(default_factory=list)


class ComparisonEngine:

    def __init__(self, source_a, source_b, profile, location: str,
                 period_years: int, tariff_service=None):
        self.source_a = source_a
        self.source_b = source_b
        self.profile = profile
        self.location = location
        self.period_years = period_years

        self.energy_calc = EnergyCalculator()
        self.financial_calc = FinancialCalculator()
        self.carbon_calc = CarbonCalculator()
        self.tariffs = tariff_service or TariffService()

        self.emission_factors = load_emission_factors()
        self.grid_factor = self.emission_factors.get("grid", 0.42)


        self.weather_source = "estimated"
        self.resolved_location = None


        self.explicit_coordinates = None

    def _inject_weather_data(self) -> None:
        if self.explicit_coordinates:
            latitude, longitude = self.explicit_coordinates
            self.resolved_location = LocationService.reverse_geocode(
                latitude, longitude
            )
        else:
            if not self.location or not str(self.location).strip():
                raise LocationNotFound(
                    "A location is required. Enter a town or use your "
                    "current location."
                )
            location_data = LocationService.geocode(self.location)
            latitude = location_data["latitude"]
            longitude = location_data["longitude"]
            self.resolved_location = location_data

        weather = WeatherService()
        history = weather.get_historical_weather(latitude, longitude, days=365)

        if not history or not history.get("avg_radiation_kwh_m2_day"):
            raise ConnectionError(
                "Could not fetch solar and wind data for this location. "
                "Check your internet connection and try again."
            )

        self.weather_source = "historical"

        for source in (self.source_a, self.source_b):
            if isinstance(source, Solar):
                source.latitude_deg = latitude
                source.avg_solar_radiation_kwh_m2_day = history["avg_radiation_kwh_m2_day"]
            elif isinstance(source, Wind):
                factor = history.get("avg_capacity_factor")
                if factor is None:
                    raise ConnectionError(
                        "Wind resource data unavailable for this location."
                    )
                source.avg_capacity_factor_override = factor

    def validate_matchup(self) -> bool:
        return type(self.source_a) is not type(self.source_b)

    def _is_grid(self, source) -> bool:
        return hasattr(source, "tariff_rate")

    def _build_result(self, source) -> ComparisonResult:
        demand = self.profile.annual_demand * self.period_years
        generated = source.calculate_energy(self.profile, self.period_years)

        if self._is_grid(source):


            delivered = demand
            shortfall = 0.0
            surplus = 0.0
        else:
            delivered = min(generated, demand)
            shortfall = max(0.0, demand - generated)
            surplus = max(0.0, generated - demand)

        coverage = self.energy_calc.calculate_energy_independence(delivered, demand)


        installation = self.financial_calc.calculate_installation_cost(source)
        maintenance = source.calculate_maintenance(self.period_years)

        annual_shortfall = shortfall / self.period_years if self.period_years else 0.0
        annual_topup_cost = self.tariffs.calculate_annual_cost(annual_shortfall)
        topup_cost_total = annual_topup_cost * self.period_years

        if self._is_grid(source):

            annual_running = self.tariffs.calculate_annual_cost(self.profile.annual_demand)
        else:
            own_annual = self.financial_calc.calculate_own_annual_cost(source, self.profile)
            annual_running = own_annual + annual_topup_cost

        total_cost = installation + (annual_running * self.period_years)


        own_factor = self.emission_factors.get(source._source_key(), 0.0)
        own_emissions = delivered * own_factor
        topup_emissions = shortfall * self.grid_factor


        notes = []
        if not self._is_grid(source):
            if coverage < 99.5:
                notes.append(
                    f"Covers {coverage:.0f}% of demand; the remaining "
                    f"{annual_shortfall:,.0f} kWh/year is still bought from the grid."
                )
            if surplus > 0:
                notes.append(
                    f"Generates {surplus / self.period_years:,.0f} kWh/year more than "
                    f"needed. Counted as wasted - Ghana has no residential feed-in "
                    f"tariff, and this system has no battery."
                )

        return ComparisonResult(
            source_name=source.name,
            selected_model=getattr(source, "selected_model", None),
            energy_supplied_kwh=round(delivered, 2),
            energy_generated_kwh=round(generated, 2),
            energy_delivered_kwh=round(delivered, 2),
            energy_shortfall_kwh=round(shortfall, 2),
            energy_surplus_kwh=round(surplus, 2),
            coverage_percent=round(coverage, 1),
            installation_cost_ghs=round(installation, 2),
            annual_operating_cost_ghs=round(annual_running, 2),
            maintenance_cost_ghs=round(maintenance, 2),
            grid_topup_cost_ghs=round(topup_cost_total, 2),
            total_cost_ghs=round(total_cost, 2),
            emissions_kg=round(own_emissions, 2),
            grid_topup_emissions_kg=round(topup_emissions, 2),
            total_emissions_kg=round(own_emissions + topup_emissions, 2),
            notes=notes,
        )

    def cost_series(self, result_a, result_b) -> dict:
        years = list(range(0, self.period_years + 1))

        series_a = [result_a.installation_cost_ghs
                    + result_a.annual_operating_cost_ghs * year
                    for year in years]
        series_b = [result_b.installation_cost_ghs
                    + result_b.annual_operating_cost_ghs * year
                    for year in years]

        crossover = None
        for index in range(1, len(years)):
            previous = series_a[index - 1] - series_b[index - 1]
            current = series_a[index] - series_b[index]


            if previous < 0 <= current or previous > 0 >= current:
                if current != previous:
                    fraction = abs(previous) / abs(current - previous)
                    crossover = round(years[index - 1] + fraction, 2)
                else:
                    crossover = years[index]
                break

        return {
            "years": years,
            "series_a": [round(value, 2) for value in series_a],
            "series_b": [round(value, 2) for value in series_b],
            "crossover_year": crossover,
            "label_a": result_a.source_name,
            "label_b": result_b.source_name,
        }

    def run_comparison(self) -> Dict[str, Any]:
        if not self.validate_matchup():
            raise ValueError("source_a and source_b must be different source types")

        if self.profile.annual_demand == 0 and (
            self.profile.appliances or self.profile.direct_monthly_kwh
        ):
            self.profile.calculate_total_energy()
            self.profile.calculate_peak_load()

        self._inject_weather_data()

        result_a = self._build_result(self.source_a)
        result_b = self._build_result(self.source_b)


        annual_a = result_a.annual_operating_cost_ghs
        annual_b = result_b.annual_operating_cost_ghs
        annual_savings = annual_a - annual_b

        extra_capital = result_b.installation_cost_ghs - result_a.installation_cost_ghs
        lifetime_savings = (annual_savings * self.period_years) - extra_capital

        payback_years = self.financial_calc.calculate_payback_period(
            extra_capital, annual_savings
        )

        result_b.lifetime_savings_ghs = round(lifetime_savings, 2)
        result_b.payback_years = (
            round(payback_years, 2) if payback_years != float("inf") else payback_years
        )

        avoided = result_a.total_emissions_kg - result_b.total_emissions_kg

        return {
            "source_a": asdict(result_a),
            "source_b": asdict(result_b),
            "cost_series": self.cost_series(result_a, result_b),
            "avoided_emissions_kg": round(avoided, 2),
            "lifetime_savings_ghs": round(lifetime_savings, 2),
            "annual_savings_ghs": round(annual_savings, 2),
            "payback_years": result_b.payback_years,
            "demand_kwh": round(self.profile.annual_demand * self.period_years, 2),
            "annual_demand_kwh": round(self.profile.annual_demand, 2),
            "location": self.location,
            "resolved_location": self.resolved_location,
            "weather_data_source": self.weather_source,
            "period_years": self.period_years,
        }
