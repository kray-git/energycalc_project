import math
from abc import ABC, abstractmethod

from app.data.data_loader import load_emission_factors


water_density_kg_m3 = 1000
gravity_m_s2 = 9.81
ghana_default_latitude_deg = 5.6
biomass_capacity_factor = 0.65


def estimate_peak_sun_hours(latitude_deg: float = ghana_default_latitude_deg,
                             day_of_year: int = 172) -> float:
    declination_deg = 23.45 * math.sin(math.radians((360 / 365) * (284 + day_of_year)))
    solar_elevation_deg = max(0.0, 90 - abs(latitude_deg - declination_deg))
    irradiance_factor = math.sin(math.radians(solar_elevation_deg))

    psh = irradiance_factor * 7.0
    return max(3.0, min(psh, 7.0))


class EnergySource(ABC):

    def __init__(self, name: str, installation_cost: float,
                 maintenance_rate: float, expected_lifespan_years: int):
        self.name = name
        self.installation_cost = installation_cost
        self.maintenance_rate = maintenance_rate
        self.expected_lifespan_years = expected_lifespan_years

    @abstractmethod
    def calculate_energy(self, profile: "EnergyProfile", period_years: int) -> float:
        raise NotImplementedError

    @abstractmethod
    def calculate_cost(self, profile: "EnergyProfile", period_years: int) -> float:
        raise NotImplementedError

    @abstractmethod
    def calculate_maintenance(self, period_years: int) -> float:
        raise NotImplementedError

    @abstractmethod
    def calculate_emissions(self, profile: "EnergyProfile", period_years: int) -> float:
        raise NotImplementedError

    def _source_key(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"


class GridElectricity(EnergySource):

    def __init__(self, tariff_rate: float):
        super().__init__(
            name="Grid Electricity",
            installation_cost=0.0,
            maintenance_rate=0.0,
            expected_lifespan_years=999,
        )
        self.tariff_rate = tariff_rate

    def _ensure_profile_calculated(self, profile) -> None:
        if profile.annual_demand == 0 and (profile.appliances or profile.direct_monthly_kwh):
            profile.calculate_total_energy()

    def calculate_energy(self, profile, period_years):
        self._ensure_profile_calculated(profile)
        return profile.annual_demand * period_years

    def calculate_cost(self, profile, period_years):
        energy_supplied = self.calculate_energy(profile, period_years)
        return energy_supplied * self.tariff_rate

    def calculate_maintenance(self, period_years):
        return 0.0

    def calculate_emissions(self, profile, period_years):
        energy_supplied = self.calculate_energy(profile, period_years)
        factor = load_emission_factors()[self._source_key()]
        return energy_supplied * factor

    def _source_key(self):
        return "grid"


class Solar(EnergySource):

    def __init__(self, panel_capacity_kw: float, installation_cost: float,
                 maintenance_rate: float, expected_lifespan_years: int,
                 system_losses: float = 0.14,
                 latitude_deg: float = ghana_default_latitude_deg):
        super().__init__("Solar PV", installation_cost, maintenance_rate,
                          expected_lifespan_years)
        self.panel_capacity_kw = panel_capacity_kw
        self.system_losses = system_losses
        self.latitude_deg = latitude_deg
        self.avg_solar_radiation_kwh_m2_day = None
        self.battery = None

    def calculate_energy(self, profile, period_years):
        if self.avg_solar_radiation_kwh_m2_day is not None:
            peak_sun_hours = self.avg_solar_radiation_kwh_m2_day
        else:
            peak_sun_hours = estimate_peak_sun_hours(self.latitude_deg)

        daily_energy_kwh = self.panel_capacity_kw * peak_sun_hours * (1 - self.system_losses)
        return daily_energy_kwh * 365 * period_years

    def calculate_cost(self, profile, period_years):
        return self.installation_cost + self.calculate_maintenance(period_years)

    def calculate_maintenance(self, period_years):
        return self.installation_cost * self.maintenance_rate * period_years

    def calculate_emissions(self, profile, period_years):
        energy_generated = self.calculate_energy(profile, period_years)
        factor = load_emission_factors()[self._source_key()]
        return energy_generated * factor

    def _source_key(self):
        return "solar"


class Wind(EnergySource):

    def __init__(self, rated_capacity_kw: float, installation_cost: float,
                 maintenance_rate: float, expected_lifespan_years: int,
                 capacity_factor: float = 0.20):
        super().__init__("Small Wind Turbine", installation_cost,
                          maintenance_rate, expected_lifespan_years)
        self.rated_capacity_kw = rated_capacity_kw
        self.capacity_factor = capacity_factor
        self.avg_capacity_factor_override = None

    def calculate_energy(self, profile, period_years):
        effective_capacity_factor = (
            self.avg_capacity_factor_override
            if self.avg_capacity_factor_override is not None
            else self.capacity_factor
        )
        daily_energy_kwh = self.rated_capacity_kw * effective_capacity_factor * 24
        return daily_energy_kwh * 365 * period_years

    def calculate_cost(self, profile, period_years):
        return self.installation_cost + self.calculate_maintenance(period_years)

    def calculate_maintenance(self, period_years):
        return self.installation_cost * self.maintenance_rate * period_years

    def calculate_emissions(self, profile, period_years):
        energy_generated = self.calculate_energy(profile, period_years)
        factor = load_emission_factors()[self._source_key()]
        return energy_generated * factor

    def _source_key(self):
        return "wind"


class Biomass(EnergySource):

    def __init__(self, feedstock_type: str, conversion_efficiency: float,
                 installation_cost: float, maintenance_rate: float,
                 expected_lifespan_years: int, rated_capacity_kw: float = 1.5,
                 feedstock_cost_ghs_per_kwh: float = 0.15):
        super().__init__("Biomass", installation_cost, maintenance_rate,
                          expected_lifespan_years)
        self.feedstock_type = feedstock_type
        self.conversion_efficiency = conversion_efficiency
        self.rated_capacity_kw = rated_capacity_kw
        self.feedstock_cost_ghs_per_kwh = feedstock_cost_ghs_per_kwh

    def calculate_energy(self, profile, period_years):
        daily_energy_kwh = self.rated_capacity_kw * biomass_capacity_factor * 24
        return daily_energy_kwh * 365 * period_years

    def calculate_cost(self, profile, period_years):
        energy_generated = self.calculate_energy(profile, period_years)
        feedstock_cost = energy_generated * self.feedstock_cost_ghs_per_kwh
        return self.installation_cost + self.calculate_maintenance(period_years) + feedstock_cost

    def calculate_maintenance(self, period_years):
        return self.installation_cost * self.maintenance_rate * period_years

    def calculate_emissions(self, profile, period_years):
        energy_generated = self.calculate_energy(profile, period_years)
        factor = load_emission_factors()[self._source_key()]
        return energy_generated * factor

    def _source_key(self):
        return "biomass"


class Hydropower(EnergySource):

    def __init__(self, flow_rate_m3s: float, head_height_m: float,
                 installation_cost: float, maintenance_rate: float,
                 expected_lifespan_years: int, turbine_efficiency: float = 0.75):
        super().__init__("Hydropower", installation_cost, maintenance_rate,
                          expected_lifespan_years)
        self.flow_rate_m3s = flow_rate_m3s
        self.head_height_m = head_height_m
        self.turbine_efficiency = turbine_efficiency

    def _rated_power_kw(self) -> float:
        power_watts = (water_density_kg_m3 * gravity_m_s2 * self.flow_rate_m3s
                       * self.head_height_m * self.turbine_efficiency)
        return power_watts / 1000

    def calculate_energy(self, profile, period_years):


        daily_energy_kwh = self._rated_power_kw() * 24
        return daily_energy_kwh * 365 * period_years

    def calculate_cost(self, profile, period_years):
        return self.installation_cost + self.calculate_maintenance(period_years)

    def calculate_maintenance(self, period_years):
        return self.installation_cost * self.maintenance_rate * period_years

    def calculate_emissions(self, profile, period_years):
        energy_generated = self.calculate_energy(profile, period_years)
        factor = load_emission_factors()[self._source_key()]
        return energy_generated * factor

    def _source_key(self):
        return "hydro"


source_registry = {
    "grid": GridElectricity,
    "solar": Solar,
    "wind": Wind,
    "biomass": Biomass,
    "hydro": Hydropower,
}
