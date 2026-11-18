class FinancialCalculator:

    @staticmethod
    def calculate_installation_cost(source) -> float:
        return source.installation_cost

    @staticmethod
    def calculate_own_annual_cost(source, profile) -> float:
        if hasattr(source, "tariff_rate"):
            raise ValueError(
                "Grid running cost is banded - use TariffService."
                "calculate_annual_cost(demand) instead."
            )

        maintenance = source.calculate_maintenance(1)

        feedstock_cost = 0.0
        if hasattr(source, "feedstock_cost_ghs_per_kwh"):
            generated = source.calculate_energy(profile, 1)
            used = min(generated, profile.annual_demand)
            feedstock_cost = used * source.feedstock_cost_ghs_per_kwh

        return maintenance + feedstock_cost

    @staticmethod
    def calculate_annual_operating_cost(source, profile, year: int) -> float:
        if hasattr(source, "tariff_rate"):

            if profile.annual_demand == 0 and (profile.appliances or profile.direct_monthly_kwh):
                profile.calculate_total_energy()
            return profile.annual_demand * source.tariff_rate


        maintenance = source.calculate_maintenance(1)
        feedstock_cost = 0.0
        if hasattr(source, "feedstock_cost_ghs_per_kwh"):
            energy_generated = source.calculate_energy(profile, 1)
            feedstock_cost = energy_generated * source.feedstock_cost_ghs_per_kwh
        return maintenance + feedstock_cost

    @classmethod
    def calculate_annual_savings(cls, source_a, source_b, profile, year: int) -> float:
        cost_a = cls.calculate_annual_operating_cost(source_a, profile, year)
        cost_b = cls.calculate_annual_operating_cost(source_b, profile, year)
        return cost_a - cost_b

    @classmethod
    def calculate_payback_period(cls, extra_capital_cost: float,
                                  annual_savings: float,
                                  max_years: int = 30,
                                  escalation: float = 0.0,
                                  _year: int = 1,
                                  _cumulative: float = 0.0) -> float:
        if extra_capital_cost <= 0:
            return 0.0
        if annual_savings <= 0:
            return float("inf")
        if _year > max_years:
            return float("inf")

        this_year = annual_savings * ((1 + escalation) ** (_year - 1))
        new_cumulative = _cumulative + this_year

        if new_cumulative >= extra_capital_cost:
            remaining = extra_capital_cost - _cumulative
            fraction = remaining / this_year
            return (_year - 1) + fraction

        return cls.calculate_payback_period(
            extra_capital_cost, annual_savings, max_years,
            escalation, _year + 1, new_cumulative
        )

    @classmethod
    def calculate_lifetime_savings(cls, source_a, source_b, profile,
                                    period_years: int) -> float:
        total_operating_savings = 0.0
        for year in range(1, period_years + 1):
            total_operating_savings += cls.calculate_annual_savings(
                source_a, source_b, profile, year
            )

        installation_cost_difference = source_b.installation_cost - source_a.installation_cost
        return total_operating_savings - installation_cost_difference
