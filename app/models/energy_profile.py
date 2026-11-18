from typing import List, Optional
from app.models.appliance import Appliance


class EnergyProfile:

    def __init__(self):
        self.appliances: List[Appliance] = []
        self.direct_monthly_kwh: Optional[float] = None
        self.direct_peak_kw: Optional[float] = None

        self.daily_demand: float = 0.0
        self.monthly_demand: float = 0.0
        self.annual_demand: float = 0.0
        self.peak_load_kw: float = 0.0

    def add_appliance(self, appliance: Appliance) -> None:
        self.appliances.append(appliance)

    def remove_appliance(self, appliance: Appliance) -> None:
        if appliance in self.appliances:
            self.appliances.remove(appliance)

    def calculate_total_energy(self) -> None:
        if self.appliances:
            total_daily = 0.0
            for appliance in self.appliances:
                total_daily += appliance.calculate_daily_energy()
            self.daily_demand = total_daily
        else:
            monthly = self.direct_monthly_kwh or 0.0
            self.daily_demand = monthly / 30

        self.monthly_demand = self.daily_demand * 30
        self.annual_demand = self.daily_demand * 365

    def calculate_peak_load(self) -> None:
        if self.appliances:
            total_peak_w = 0.0
            for appliance in self.appliances:
                total_peak_w += appliance.power_rating_w * appliance.quantity
            self.peak_load_kw = total_peak_w / 1000
        else:
            self.peak_load_kw = self.direct_peak_kw or 0.0

    def __repr__(self) -> str:
        return (f"<EnergyProfile appliances={len(self.appliances)} "
                f"annual_demand={self.annual_demand:.1f}kWh>")
