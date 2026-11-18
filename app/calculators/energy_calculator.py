class EnergyCalculator:

    @staticmethod
    def calculate_energy_balance(demand_kwh: float, supply_kwh: float) -> float:
        return supply_kwh - demand_kwh

    @staticmethod
    def calculate_energy_independence(renewable_kwh_used: float,
                                       total_demand_kwh: float) -> float:
        if total_demand_kwh == 0:
            return 0.0
        return (renewable_kwh_used / total_demand_kwh) * 100
