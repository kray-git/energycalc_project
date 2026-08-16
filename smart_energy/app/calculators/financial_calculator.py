"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/calculators/financial_calculator.py  -  Cost, Savings, Payback
========================================================================
  Owner:  ____________________
  Build order: STAGE 3

  *** THIS FILE CONTAINS YOUR RECURSION REQUIREMENT ***
      calculate_payback_period() MUST stay recursive.
      Do not "tidy it up" into a while loop. If a teammate flattens it
      in a pull request, reject the PR and point them here.

  WHAT THIS CLASS ANSWERS
    "What does each option cost me, and when does the expensive one
     start paying for itself?"

  RUBRIC COVERAGE
    [x] Recursion  <-- the important one
    [x] Functions  [x] Conditionals  [x] Collections  [x] Loops

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.calculators.financial_calculator
========================================================================
"""


class FinancialCalculator:
    """All money-related comparisons between two sources."""

    # Cap on the payback recursion. Without a hard limit, a source that
    # never pays back would recurse until Python's stack gives out.
    MAX_PAYBACK_YEARS = 50

    # Annual electricity tariff escalation. Ghana's tariffs have risen
    # substantially over the past decade; assuming 0% would flatter the
    # grid unfairly. VERIFY a defensible figure and cite it.
    DEFAULT_TARIFF_ESCALATION = 0.08   # 8% per year

    def calculate_annual_cost(self, source, annual_kwh):
        """
        One year's cost for a source.

        Args:
            source (EnergySource)
            annual_kwh (float)

        Returns:
            dict: {"capital", "running", "total"} in GHS

        HINT
            One line - source.calculate_cost(annual_kwh, 365). This
            wrapper exists so ComparisonEngine talks to the calculator
            rather than reaching into the source directly, which keeps
            one seam to change if costing ever gets more complex.
        """
        # [IMPLEMENT ME]  (1-2 lines)
        raise NotImplementedError("FinancialCalculator.calculate_annual_cost")

    def calculate_annual_savings(self, baseline_source, alternative_source,
                                 annual_kwh):
        """
        Yearly RUNNING-cost saving from switching.

        Args:
            baseline_source (EnergySource): usually the grid
            alternative_source (EnergySource): usually solar/wind/etc.
            annual_kwh (float)

        Returns:
            float: GHS saved per year. NEGATIVE if the alternative costs
                   more to run - and you must let that negative through
                   rather than clamping it to zero. A tool that cannot
                   report a bad deal is not a comparison tool.

        CRITICAL - RUNNING COSTS ONLY
            Do NOT include capital here. Capital is what the savings
            have to pay BACK; counting it as a saving would double-count
            and make payback meaningless.

        FORMULA
            baseline_running - alternative_running
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("FinancialCalculator.calculate_annual_savings")

    # ------------------------------------------------------------------
    #  RECURSION - the rubric requirement
    # ------------------------------------------------------------------

    def calculate_payback_period(self, capital_cost, annual_savings,
                                 year=1, accumulated=0.0,
                                 escalation=None):
        """
        Years until cumulative savings repay the upfront cost.

        *** RECURSIVE BY DESIGN - DO NOT CONVERT TO A LOOP ***

        Args:
            capital_cost (float): upfront cost to recover, GHS
            annual_savings (float): first year's saving, GHS
            year (int): current year - the recursion counter
            accumulated (float): savings so far - the running total
                carried down the recursion
            escalation (float, optional): yearly savings growth as a
                fraction. Defaults to DEFAULT_TARIFF_ESCALATION.

        Returns:
            float: years to payback (fractional, e.g. 8.4), or
                   float('inf') if it never pays back within
                   MAX_PAYBACK_YEARS.

        HOW TO THINK ABOUT THE RECURSION

          BASE CASES - always write these FIRST. A recursive function
          with no base case is an infinite loop with extra steps.

            1. annual_savings <= 0  -> return float('inf')
               Nothing is being saved, so nothing is ever repaid.
               (Catch this before recursing at all.)

            2. year > MAX_PAYBACK_YEARS -> return float('inf')
               The guard that stops runaway recursion.

            3. accumulated + this_year_savings >= capital_cost
               -> we cross the line during THIS year. Return the
                  fractional year, not a whole one:

                    remaining = capital_cost - accumulated
                    fraction  = remaining / this_year_savings
                    return (year - 1) + fraction

                  Why year - 1: at the start of year 1, zero full years
                  have elapsed. If you return year + fraction you will
                  be exactly one year pessimistic on every result.

          RECURSIVE CASE - not repaid yet, so move to next year:

                this_year = annual_savings * ((1 + escalation) ** (year - 1))
                return self.calculate_payback_period(
                    capital_cost,
                    annual_savings,
                    year + 1,
                    accumulated + this_year,
                    escalation)

            Note we pass the ORIGINAL annual_savings down and re-derive
            each year's figure from `year`. Passing an already-escalated
            value down compounds it twice - a subtle bug that shows up
            as a suspiciously short payback.

        WORKED EXAMPLE TO CHECK AGAINST
            capital 20000, savings 3000/yr, escalation 0:
              year 1 -> 3000    year 2 -> 6000    year 3 -> 9000
              year 4 -> 12000   year 5 -> 15000   year 6 -> 18000
              year 7 -> 21000 which passes 20000
              remaining at start of year 7 = 20000 - 18000 = 2000
              fraction = 2000/3000 = 0.667
              answer = 6 + 0.667 = 6.67 years

        FOR YOUR REPORT
            Be ready to explain WHY recursion suits this problem: each
            year's state depends only on the previous year's cumulative
            total, which is the shape recursion expresses naturally.
            Also be honest that an iterative version would be equally
            valid and use less stack - "we chose recursion and here is
            the trade-off" is a stronger answer than pretending it was
            the only option.
        """
        # [IMPLEMENT ME]  (~20 lines)
        raise NotImplementedError("FinancialCalculator.calculate_payback_period")

    # ------------------------------------------------------------------

    def calculate_lifetime_cost(self, source, annual_kwh):
        """
        Total cost of ownership over the source's full lifespan.

        HINT
            source.lifetime_cost(annual_kwh) - another thin wrapper,
            same reasoning as calculate_annual_cost.
        """
        # [IMPLEMENT ME]  (1-2 lines)
        raise NotImplementedError("FinancialCalculator.calculate_lifetime_cost")

    def calculate_lcoe(self, source, annual_kwh):
        """
        Levelised Cost of Energy - GHS per kWh over the whole lifespan.

        Returns:
            float: GHS/kWh

        FORMULA
            lifetime_total_cost / (annual_kwh * lifespan_years)

        WHY LCOE IS THE FAIREST SINGLE NUMBER
            It puts a 25-year solar array and a monthly grid bill on the
            same footing: what did each kilowatt-hour actually cost,
            all-in, across the asset's life. If you present one headline
            figure in your pitch, this is the defensible one.

        SIMPLIFICATION TO DECLARE
            Real LCOE discounts future cash flows to present value. This
            version does not. Say so.

        GUARD: annual_kwh or lifespan of 0 -> return float('inf').
        """
        # [IMPLEMENT ME]  (~7 lines)
        raise NotImplementedError("FinancialCalculator.calculate_lcoe")

    def cumulative_cost_series(self, source, annual_kwh, years=25):
        """
        Year-by-year cumulative spend - the data behind the crossover
        chart on the results page.

        Returns:
            list[dict]: [{"year": 0, "cumulative_cost": capital}, ...]

        Year 0 is capital only (money spent before any energy flows).
        Each later year adds running + maintenance, escalated.

        WHY THIS IS THE MOST PERSUASIVE OUTPUT IN THE WHOLE PROJECT
            Plot grid and solar cumulative cost on one axis and the
            crossover point is visible instantly - far more convincing
            than a table. Build this carefully; it is your key visual.

        *** THIS IS A LOOP, NOT RECURSION. ***
            Deliberately so - the contrast between this method and
            calculate_payback_period is worth a line in your report:
            same domain, two techniques, chosen per problem shape.
        """
        # [IMPLEMENT ME]  (~14 lines)
        raise NotImplementedError("FinancialCalculator.cumulative_cost_series")

    def compare_costs(self, source_a, source_b, annual_kwh):
        """
        Full financial head-to-head between two sources.

        Returns:
            dict:
                source_a / source_b : each {"name", "annual", "lifetime",
                                            "lcoe", "capital"}
                annual_savings      : float (a minus b, running only)
                payback_years       : float or None
                cheaper_lifetime    : str - name of the lower-lifetime one
                verdict             : str - one plain sentence

        HINT ON PAYBACK DIRECTION
            Payback only makes sense when comparing a cheaper-to-run but
            expensive-to-buy option against a cheap-to-buy but
            expensive-to-run one. Work out which of the two has the
            higher capital cost, compute savings in that direction, and
            return None when neither has meaningful capital (e.g. grid
            vs grid, which the route should have blocked anyway).

        WRITE THE VERDICT AS ONE HONEST SENTENCE, e.g.
            "Solar PV costs GHS 15,000 upfront but pays that back in
             6.7 years and is GHS 42,000 cheaper over 25 years."
        """
        # [IMPLEMENT ME]  (~25 lines)
        raise NotImplementedError("FinancialCalculator.compare_costs")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":
    print("=" * 62)
    print("FINANCIAL CALCULATOR SELF-TEST")
    print("=" * 62)

    calc = FinancialCalculator()

    print("\n[1] RECURSION - payback, no escalation")
    print("    Hand-worked expectations:")
    cases = [
        ("20000 capital, 3000/yr", 20000, 3000, 6.67),
        ("10000 capital, 2500/yr", 10000, 2500, 3.0),
        ("15000 capital, 5000/yr", 15000, 5000, 2.0),
        ("20000 capital, 0/yr", 20000, 0, float("inf")),
        ("20000 capital, -500/yr", 20000, -500, float("inf")),
        ("999999 capital, 10/yr", 999999, 10, float("inf")),
    ]
    for label, capital, savings, expected in cases:
        try:
            result = calc.calculate_payback_period(capital, savings,
                                                   escalation=0.0)
            ok = "[OK]" if (result == expected or
                            (isinstance(result, float) and
                             abs(result - expected) < 0.02)) else \
                 "[WRONG - expected " + str(expected) + "]"
            print("  " + label.ljust(28) + str(result).ljust(10) + ok)
        except NotImplementedError:
            print("  " + label.ljust(28) + "not yet implemented")
        except RecursionError:
            print("  " + label.ljust(28) +
                  "[BUG] RecursionError - your base case is not firing")
        except Exception as e:
            print("  " + label.ljust(28) + "ERROR: " + type(e).__name__ + ": " + e.__str__())

    print("\n[2] Payback WITH 8% escalation (should be FASTER)")
    try:
        flat = calc.calculate_payback_period(20000, 3000, escalation=0.0)
        esc = calc.calculate_payback_period(20000, 3000, escalation=0.08)
        print("  flat        ", flat)
        print("  escalated   ", esc)
        print("  faster?     ", "[OK]" if esc < flat else "[CHECK your escalation term]")
    except NotImplementedError:
        print("  not yet implemented")
    except Exception as e:
        print("  ERROR:", type(e).__name__, e)

    print("\n[3] Confirm it is genuinely recursive")
    print("    (a loop-based version would pass [1] too - this catches")
    print("     a teammate quietly rewriting it)")
    try:
        import inspect
        src = inspect.getsource(FinancialCalculator.calculate_payback_period)
        body = src.split('"""')[-1]
        calls_itself = "calculate_payback_period" in body
        if "NotImplementedError" in body:
            print("    not yet implemented")
        elif calls_itself:
            print("    [OK] method calls itself - recursion present")
        else:
            print("    [PROBLEM] no self-call found. The rubric needs")
            print("              recursion here - restore it.")
    except Exception as e:
        print("    could not inspect:", e)

    print("\n[4] Source-dependent methods (need STAGE 1 models)")
    try:
        from app.models.energy_source import Solar, GridElectricity
        solar = Solar("Mono-350", 10)
        grid = GridElectricity()
        for label, fn in [
            ("grid annual cost", lambda: calc.calculate_annual_cost(grid, 2310)),
            ("solar annual cost", lambda: calc.calculate_annual_cost(solar, 2310)),
            ("annual savings", lambda: calc.calculate_annual_savings(grid, solar, 2310)),
            ("solar LCOE", lambda: calc.calculate_lcoe(solar, 2310)),
            ("grid LCOE", lambda: calc.calculate_lcoe(grid, 2310)),
            ("full comparison", lambda: calc.compare_costs(grid, solar, 2310)),
        ]:
            try:
                print("  " + label.ljust(22) + str(fn()))
            except NotImplementedError as e:
                print("  " + label.ljust(22) + "blocked: " + e.__str__())
            except Exception as e:
                print("  " + label.ljust(22) + "ERROR: " + type(e).__name__)
    except NotImplementedError:
        print("  models not implemented yet")

    print("\n" + "=" * 62)
