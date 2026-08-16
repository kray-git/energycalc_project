"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/calculators/energy_calculator.py  -  Energy Balance
========================================================================
  Owner:  ____________________
  Build order: STAGE 3 (needs EnergyProfile and EnergySource working)

  WHAT THIS CLASS ANSWERS
    "Will this source actually meet my needs?"

    Not cost, not carbon - just supply versus demand. Kept separate
    from the other two calculators because a source can be cheap and
    clean and still be useless if it cannot keep the fridge running.

  WHY A CLASS OF STATIC-ISH METHODS RATHER THAN LOOSE FUNCTIONS
    Grouping keeps the namespace tidy and lets ComparisonEngine hold
    one calculator object per concern. If your team prefers plain
    functions, that is defensible - but decide once, together, and
    apply it to all three calculators.

  RUBRIC COVERAGE
    [x] Functions   [x] Conditionals (if/elif/else, ternary)
    [x] Collections (dict return, list of monthly figures)
    [x] Loops

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.calculators.energy_calculator
========================================================================
"""


class EnergyCalculator:
    """Compares what a source supplies against what a profile demands."""

    # Coverage thresholds used for the verdict wording. Tune together as
    # a team so the report and the UI agree.
    FULLY_MET = 100.0
    MOSTLY_MET = 80.0
    PARTIALLY_MET = 50.0

    def calculate_balance(self, profile, source, days=365, context=None):
        """
        Core supply-vs-demand comparison.

        Args:
            profile (EnergyProfile)
            source (EnergySource)
            days (int): period length
            context (dict, optional): environmental data passed straight
                through to source.calculate_energy()

        Returns:
            dict:
                demand_kwh    (float)
                supply_kwh    (float)
                coverage_pct  (float)  supply/demand * 100, capped at 100
                deficit_kwh   (float)  0.0 if supply >= demand
                surplus_kwh   (float)  0.0 if supply <= demand
                status        (str)    "full"/"mostly"/"partial"/"poor"
                meets_demand  (bool)

        IMPORTANT - THE GRID SPECIAL CASE
            GridElectricity.calculate_energy() needs "demand_kwh" in its
            context, since the grid supplies whatever is asked of it.
            So build the context here:

                ctx = dict(context) if context else {}
                ctx["demand_kwh"] = demand

            Copy the dict rather than mutating the caller's - a function
            that quietly modifies its arguments is a debugging nightmare
            when two sources share one context object.

        GUARD
            If demand is 0, coverage is undefined (division by zero).
            Return 100.0 and status "full" - nothing needed, nothing
            missing.

        HINT for status - if/elif chain against the three thresholds.
        """
        # [IMPLEMENT ME]  (~25 lines)
        raise NotImplementedError("EnergyCalculator.calculate_balance")

    def calculate_coverage_percentage(self, supply_kwh, demand_kwh):
        """
        Returns:
            float: percentage of demand met, 0-100.

        HINT
            Guard demand == 0 first, then
                return min(100.0, supply / demand * 100)
            A ternary reads well here.
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("EnergyCalculator.calculate_coverage_percentage")

    def calculate_independence_score(self, profile, source, days=365,
                                     context=None):
        """
        How far this source frees the user from the grid, 0-100.

        Returns:
            float

        SCORING
            base = coverage_pct
            if the source is NOT renewable (i.e. it IS the grid), the
            score is 0 by definition - you cannot become independent of
            the grid by using the grid.
            If it is renewable, independence = coverage, with a bonus of
            up to 10 points for surplus (over-generation gives headroom
            for future load growth). Cap at 100.

        This is a DESIGNED metric, not a standard one. Define it clearly
        in the report and own the choices - a marker will accept a
        defended definition and penalise an undefended one.
        """
        # [IMPLEMENT ME]  (~12 lines)
        raise NotImplementedError("EnergyCalculator.calculate_independence_score")

    def monthly_breakdown(self, profile, source, context=None):
        """
        Twelve monthly supply/demand figures.

        Returns:
            list[dict]: one per month, each
                {"month": int 1-12, "days": int,
                 "demand_kwh": float, "supply_kwh": float,
                 "coverage_pct": float}

        WHY THIS MATTERS
            An annual total can hide a seasonal failure. A solar system
            that averages 105% coverage across the year may still sit at
            70% through the harmattan. Only a monthly view exposes it.

        HINT
            month_days = [31,28,31,30,31,30,31,31,30,31,30,31]
            Loop with enumerate, call calculate_balance for each month.
            If context carries a latitude, set context["day_of_year"] to
            roughly the middle of each month so Solar's trig fallback
            varies seasonally rather than returning the same number 12
            times. Mid-month day numbers: 15,46,74,105,135,166,196,
            227,258,288,319,349.

        *** THIS IS A STRONG LOOP + COLLECTIONS DEMONSTRATION ***
        """
        # [IMPLEMENT ME]  (~20 lines)
        raise NotImplementedError("EnergyCalculator.monthly_breakdown")

    def size_recommendation(self, profile, source, context=None):
        """
        How much bigger would this source need to be to hit 100%?

        Returns:
            dict: {"current_capacity_kw", "required_multiplier",
                   "suggested_capacity_kw", "note"}

        HINT
            multiplier = demand / supply  (guard supply == 0)
            suggested  = current_capacity_kw * multiplier

        EDGE CASE
            The grid has capacity_kw = 0, so this is meaningless for it.
            Return a note saying so rather than dividing by zero.
        """
        # [IMPLEMENT ME]  (~14 lines)
        raise NotImplementedError("EnergyCalculator.size_recommendation")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":
    from app.models.appliance import Appliance
    from app.models.energy_profile import EnergyProfile
    from app.models.energy_source import Solar, GridElectricity

    print("=" * 62)
    print("ENERGY CALCULATOR SELF-TEST")
    print("=" * 62)
    print("\nRequires Appliance, EnergyProfile and EnergySource to be")
    print("implemented first. Until then everything below reports as")
    print("blocked - that is expected, not a failure.\n")

    calc = EnergyCalculator()

    def check(label, fn):
        try:
            print("  " + label.ljust(30) + str(fn()))
        except NotImplementedError as e:
            print("  " + label.ljust(30) + "blocked: " + e.__str__())
        except Exception as e:
            print("  " + label.ljust(30) + "ERROR: " + type(e).__name__ + ": " + e.__str__())

    try:
        profile = EnergyProfile("Berekuso")
        profile.add_appliance(Appliance("Refrigerator", 150, 1, 24))
        profile.add_appliance(Appliance("Ceiling Fan", 75, 3, 10))
        profile.add_appliance(Appliance("LED Bulb", 10, 8, 6))
        # 6.33 kWh/day -> 2310 kWh/year

        print("[1] Solar (10 x Mono-350) vs 2310 kWh/year demand")
        solar = Solar("Mono-350", 10)
        ctx = {"latitude": 5.6, "day_of_year": 172}
        check("balance", lambda: calc.calculate_balance(profile, solar, 365, ctx))
        check("independence",
              lambda: calc.calculate_independence_score(profile, solar, 365, ctx))
        check("size recommendation",
              lambda: calc.size_recommendation(profile, solar, ctx))

        print("\n[2] Grid vs the same demand (expect ~92% - outages)")
        check("balance", lambda: calc.calculate_balance(profile, GridElectricity(), 365))
        check("independence (expect 0)",
              lambda: calc.calculate_independence_score(profile, GridElectricity()))

        print("\n[3] Monthly breakdown (first 3 months)")
        try:
            months = calc.monthly_breakdown(profile, solar, ctx)
            for m in months[:3]:
                print("   ", m)
        except NotImplementedError:
            print("    blocked")
        except Exception as e:
            print("    ERROR:", type(e).__name__, e)

    except NotImplementedError:
        print("  Models not implemented yet - build STAGE 1 first.")

    print("\n[4] Direct maths checks (no models needed)")
    check("coverage 900/1000 -> 90.0",
          lambda: calc.calculate_coverage_percentage(900, 1000))
    check("coverage 1500/1000 -> 100.0 (capped)",
          lambda: calc.calculate_coverage_percentage(1500, 1000))
    check("coverage x/0 -> no crash",
          lambda: calc.calculate_coverage_percentage(500, 0))

    print("\n" + "=" * 62)
