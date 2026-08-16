"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/calculators/carbon_calculator.py  -  Emissions
========================================================================
  Owner:  ____________________
  Build order: STAGE 3

  WHAT THIS CLASS ANSWERS
    "What is the climate cost of each option?"

  THE HONESTY REQUIREMENT
    Renewables are NOT zero-carbon. Manufacturing panels, forging
    turbine towers and pouring concrete for a hydro intake all emit
    CO2. Our emission_factors.csv uses LIFECYCLE factors, which is why
    solar reads 0.045 rather than 0.000. A model that prints "0" for
    solar is wrong and a marker will notice. Defend the lifecycle
    choice explicitly in your report.

  RUBRIC COVERAGE
    [x] Functions  [x] Files (emission factors)
    [x] Conditionals  [x] Collections  [x] Loops

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.calculators.carbon_calculator
========================================================================
"""

from app.data.data_loader import load_emission_factors


class CarbonCalculator:
    """Emissions accounting and human-readable equivalences."""

    # A mature tree absorbs roughly 21 kg CO2 a year. Widely cited,
    # widely simplified - species, age and climate all matter. Use it
    # for intuition only and say so.
    KG_CO2_PER_TREE_YEAR = 21.0

    # Average petrol car: about 0.19 kg CO2 per km.
    KG_CO2_PER_KM_DRIVEN = 0.19

    def __init__(self, factors=None):
        """
        Args:
            factors (dict, optional): {source_key: kg_co2_per_kwh}.
                If None, load from data/emission_factors.csv.

        WHY ALLOW INJECTING FACTORS?
            So tests can pass round numbers (grid 1.0, solar 0.1) and
            check the arithmetic by hand. Depending directly on a file
            makes a class awkward to test - accepting an override is a
            small change that pays for itself.

        HINT
            self.factors = factors if factors is not None else load_emission_factors()
        """
        # [IMPLEMENT ME]  (~2 lines)
        raise NotImplementedError("CarbonCalculator.__init__")

    def calculate_emissions(self, source_key, kwh):
        """
        CO2 from generating `kwh` with a given source.

        Args:
            source_key (str): "grid", "solar", "wind", "biomass", "hydro"
            kwh (float)

        Returns:
            float: kg CO2

        FORMULA
            kwh * factor

        UNKNOWN KEY
            Use .get(key, 0.0) rather than factors[key]. An unfamiliar
            source should not crash a comparison - but DO note the
            trade-off: a silent 0.0 could hide a typo. Consider printing
            a warning so the failure is visible without being fatal.
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("CarbonCalculator.calculate_emissions")

    def calculate_avoided_emissions(self, baseline_key, alternative_key, kwh):
        """
        CO2 avoided by switching from baseline to alternative.

        Returns:
            float: kg CO2 avoided. Can be NEGATIVE if the "alternative"
                   is dirtier - let that show. Biomass at 0.230 against
                   a hydro-heavy grid could plausibly come out worse,
                   and the tool must be able to say so.

        FORMULA
            (baseline_factor - alternative_factor) * kwh
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("CarbonCalculator.calculate_avoided_emissions")

    def to_tree_equivalent(self, kg_co2):
        """
        Trees needed for a year to absorb this much CO2.

        Returns:
            float

        WHY BOTHER
            "Avoids 878 kg CO2 a year" means little to most people.
            "Equivalent to planting 42 trees" lands. This is a
            communication device for the pitch, not a scientific claim -
            label it as such in the UI.
        """
        # [IMPLEMENT ME]  (~2 lines)
        raise NotImplementedError("CarbonCalculator.to_tree_equivalent")

    def to_driving_equivalent(self, kg_co2):
        """
        Kilometres of driving producing the same CO2.

        Returns:
            float: km
        """
        # [IMPLEMENT ME]  (~2 lines)
        raise NotImplementedError("CarbonCalculator.to_driving_equivalent")

    def lifetime_emissions(self, source, annual_kwh):
        """
        CO2 across the source's whole lifespan.

        Args:
            source (EnergySource): the object, not the key - we need its
                lifespan_years and source_key()

        Returns:
            dict: {"annual_kg", "lifetime_kg", "lifespan_years",
                   "trees_equivalent"}
        """
        # [IMPLEMENT ME]  (~10 lines)
        raise NotImplementedError("CarbonCalculator.lifetime_emissions")

    def compare_emissions(self, source_a, source_b, annual_kwh):
        """
        Carbon head-to-head between two sources.

        Returns:
            dict:
                source_a / source_b : {"name", "key", "annual_kg",
                                       "lifetime_kg"}
                annual_avoided_kg   : float (a minus b)
                lifetime_avoided_kg : float
                cleaner             : str - name of the lower-emitting one
                trees_equivalent    : float
                driving_equivalent_km : float
                verdict             : str - one plain sentence

        LIFETIME COMPARISON SUBTLETY
            The two sources may have different lifespans (grid is
            modelled as 1 year, solar as 25). Comparing raw lifetime
            totals across unequal periods is meaningless. Normalise to
            the LONGER of the two lifespans - i.e. ask what the grid
            would emit over the same 25 years. Note this decision in
            the report; it is the kind of thing markers probe.
        """
        # [IMPLEMENT ME]  (~22 lines)
        raise NotImplementedError("CarbonCalculator.compare_emissions")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":
    print("=" * 62)
    print("CARBON CALCULATOR SELF-TEST")
    print("=" * 62)

    def check(label, fn, expected=None):
        try:
            result = fn()
            note = ""
            if expected is not None and isinstance(result, (int, float)):
                note = "  [OK]" if abs(result - expected) < 0.01 else \
                       "  [WRONG - expected " + str(expected) + "]"
            print("  " + label.ljust(34) + str(result) + note)
        except NotImplementedError:
            print("  " + label.ljust(34) + "not yet implemented")
        except Exception as e:
            print("  " + label.ljust(34) + "ERROR: " + type(e).__name__ + ": " + e.__str__())

    print("\n[1] Injected round-number factors (hand-checkable)")
    print("    grid = 1.0 kg/kWh, solar = 0.1 kg/kWh")
    try:
        calc = CarbonCalculator({"grid": 1.0, "solar": 0.1})
        check("1000 kWh grid -> 1000 kg",
              lambda: calc.calculate_emissions("grid", 1000), 1000.0)
        check("1000 kWh solar -> 100 kg",
              lambda: calc.calculate_emissions("solar", 1000), 100.0)
        check("avoided by switching -> 900 kg",
              lambda: calc.calculate_avoided_emissions("grid", "solar", 1000), 900.0)
        check("unknown key -> 0.0, no crash",
              lambda: calc.calculate_emissions("fusion", 1000), 0.0)
        check("900 kg -> trees", lambda: calc.to_tree_equivalent(900), 42.857)
        check("900 kg -> km driven", lambda: calc.to_driving_equivalent(900), 4736.84)
    except NotImplementedError:
        print("  __init__ not yet implemented")

    print("\n[2] Real factors from data/emission_factors.csv")
    try:
        real = CarbonCalculator()
        for key in ["grid", "solar", "wind", "biomass", "hydro"]:
            check(key + " - 2310 kWh/yr",
                  lambda k=key: real.calculate_emissions(k, 2310))
        print("\n  Sanity: solar/wind/hydro should be well under grid,")
        print("  biomass noticeably higher than the other renewables,")
        print("  and NONE of them exactly 0.")
    except NotImplementedError:
        print("  not yet implemented")

    print("\n[3] Source-object methods (need STAGE 1 models)")
    try:
        from app.models.energy_source import Solar, GridElectricity
        calc = CarbonCalculator()
        check("solar lifetime",
              lambda: calc.lifetime_emissions(Solar("Mono-350", 10), 2310))
        check("grid vs solar",
              lambda: calc.compare_emissions(GridElectricity(),
                                             Solar("Mono-350", 10), 2310))
    except NotImplementedError:
        print("  blocked - models not implemented yet")
    except Exception as e:
        print("  ERROR:", type(e).__name__, e)

    print("\n" + "=" * 62)
