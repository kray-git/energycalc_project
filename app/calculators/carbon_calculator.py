class CarbonCalculator:

    @staticmethod
    def calculate_emissions(source, profile, period_years: int) -> float:
        return source.calculate_emissions(profile, period_years)

    @classmethod
    def calculate_avoided_emissions(cls, baseline_source, alternative_source,
                                     profile, period_years: int) -> float:
        baseline_emissions = cls.calculate_emissions(baseline_source, profile, period_years)
        alternative_emissions = cls.calculate_emissions(alternative_source, profile, period_years)
        return baseline_emissions - alternative_emissions

    @classmethod
    def calculate_lifetime_environmental_impact(cls, source, profile,
                                                  period_years: int) -> float:
        effective_years = min(period_years, source.expected_lifespan_years)
        return cls.calculate_emissions(source, profile, effective_years)
