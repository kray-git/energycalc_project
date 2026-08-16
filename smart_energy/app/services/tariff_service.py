"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/services/tariff_service.py  -  Banded Electricity Pricing
========================================================================
  Owner:  ____________________
  Build order: STAGE 2

  WHAT THIS SOLVES - AND WHY IT IS TRICKIER THAN IT LOOKS
    Ghanaian residential tariffs are BANDED and CUMULATIVE. A household
    using 350 kWh does NOT pay 350 x the band-2 rate. They pay:

        the first 30 kWh   at the lifeline rate
        the next  270 kWh  at the band-1 rate
        the last  50 kWh   at the band-2 rate
        plus a fixed service charge

    Applying one flat rate to the whole total - the mistake almost
    everyone makes first - overcharges low users and undercharges high
    ones, and it distorts the entire solar comparison, because the
    savings from solar come off the TOP band, which is the expensive
    one. Get this right and the whole model gets more honest.

  *** DATA ACCURACY WARNING ***
    data/tariffs.csv ships with ILLUSTRATIVE rates for development.
    Before any figure goes in your report or pitch, look up the current
    published PURC residential tariff schedule, update the file, and
    cite the source and effective date. Quoting invented tariffs as
    fact is the kind of error that undermines an otherwise good project.

  RUBRIC COVERAGE
    [x] Files   [x] Loops   [x] Conditionals   [x] Collections
    [x] Functions

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.services.tariff_service
========================================================================
"""

from app.data.data_loader import load_tariffs


class TariffService:
    """Prices electricity consumption against banded tariffs."""

    def __init__(self, bands=None):
        """
        Args:
            bands (list[dict], optional): pre-loaded band definitions.
                If None, load from data/tariffs.csv.

        HINT
            self.bands = bands if bands is not None else load_tariffs()

        This one runs REAL code at construction - it is not a stub even
        in the skeleton stage, because every test needs bands present.

        NOTE
            load_tariffs() already returns the bands sorted by min_kwh.
            Do not re-sort, but DO rely on that order - the cumulative
            algorithm below only works on sorted bands.
        """
        # [IMPLEMENT ME]  (~2 lines)
        raise NotImplementedError("TariffService.__init__")

    def get_band(self, kwh):
        """
        Which single band a consumption figure falls in.

        Args:
            kwh (float)

        Returns:
            dict: the matching band, or the highest band if kwh exceeds
                  every range.

        Used for display ("You are a Band 2 customer"), NOT for costing
        - costing must use the cumulative method below.

        HINT
            Loop the bands; return the first where
            min_kwh <= kwh <= max_kwh. Fall through to self.bands[-1].
        """
        # [IMPLEMENT ME]  (~6 lines)
        raise NotImplementedError("TariffService.get_band")

    def calculate_cost(self, kwh, include_service_charge=True):
        """
        *** THE IMPORTANT METHOD. Cumulative banded pricing. ***

        Args:
            kwh (float): monthly consumption
            include_service_charge (bool)

        Returns:
            float: GHS

        THE ALGORITHM - work through it slowly

            remaining = kwh
            total = 0.0
            previous_ceiling = 0

            for band in self.bands:
                if remaining <= 0: break

                # How many kWh fit inside THIS band?
                band_width = band["max_kwh"] - previous_ceiling
                units_in_band = min(remaining, band_width)

                total += units_in_band * band["rate_ghs_per_kwh"]
                remaining -= units_in_band
                previous_ceiling = band["max_kwh"]

            if include_service_charge:
                total += self.bands[0]["service_charge_ghs"]

            return total

        WHY previous_ceiling AND NOT band["min_kwh"]
            The bands are written as 0-30, 31-300, 301-600. Band 2's
            width is 300-30 = 270, not 300-31 = 269. Using min_kwh
            loses one unit per band - small, but wrong, and it compounds
            across every calculation in the app.

        HAND-CHECK WITH THE TEST FIXTURE
            tests/test_data/tariffs_test.csv uses bands 0-100 at GHS 1,
            101-200 at GHS 2, 201+ at GHS 3, zero service charge.
                 50 kWh -> 50            (50 in band 1)
                100 kWh -> 100
                150 kWh -> 100 + 100     = 200   (100@1 + 50@2)
                250 kWh -> 100 + 200 + 150 = 450 (100@1 + 100@2 + 50@3)
            If your 150 comes out as 300, you applied one flat rate.
        """
        # [IMPLEMENT ME]  (~18 lines)
        raise NotImplementedError("TariffService.calculate_cost")

    def calculate_annual_cost(self, annual_kwh):
        """
        Yearly bill from a yearly consumption figure.

        *** THE TRAP ***
            Do NOT call calculate_cost(annual_kwh). Bands are MONTHLY.
            Feeding 3600 kWh into a monthly band structure puts nearly
            all of it in the top band and massively overstates the bill.

            Convert to a monthly figure, price that, multiply by 12:

                monthly = annual_kwh / 12
                return self.calculate_cost(monthly) * 12

        REMAINING SIMPLIFICATION
            This assumes even consumption across the year. Real usage
            peaks in the hot dry months when fans and AC run hardest,
            and because bands are progressive, an uneven year costs more
            than an even one. Note it in the report.
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("TariffService.calculate_annual_cost")

    def effective_rate(self, kwh):
        """
        Average GHS per kWh actually paid at this consumption level.

        Returns:
            float

        WHY THIS IS INTERESTING
            Because bands are progressive, the effective rate RISES with
            consumption. Plotting it makes an excellent chart for the
            report - and it explains why solar saves a heavy user
            proportionally more than a light one.

        GUARD kwh == 0 (division by zero) -> return 0.0.
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("TariffService.effective_rate")

    def marginal_rate(self, kwh):
        """
        Rate charged on the NEXT kWh at this consumption level.

        Returns:
            float

        *** THIS IS THE RATE THAT MATTERS FOR SOLAR SAVINGS ***
            Solar displaces the LAST kWh you would have bought, not an
            average one. A household at 550 kWh/month saves at the
            band-2 rate on every unit solar covers, not at their lower
            effective rate. Using the effective rate here would
            understate solar's benefit - a real modelling error worth
            explaining in your report.

        HINT
            return self.get_band(kwh)["rate_ghs_per_kwh"]
        """
        # [IMPLEMENT ME]  (~2 lines)
        raise NotImplementedError("TariffService.marginal_rate")

    def breakdown(self, kwh):
        """
        Itemised bill, band by band.

        Returns:
            dict:
                {"total_kwh", "total_cost", "service_charge",
                 "effective_rate", "marginal_rate",
                 "bands": [{"band_name", "units", "rate", "subtotal"}]}

        This is what the frontend shows when a user clicks "how is my
        bill calculated?" - the transparency that makes the tool
        trustworthy rather than a black box.

        HINT
            Same loop as calculate_cost, but append a dict per band
            instead of only accumulating a running total.
        """
        # [IMPLEMENT ME]  (~24 lines)
        raise NotImplementedError("TariffService.breakdown")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":
    from pathlib import Path
    from app.data.data_loader import PROJECT_ROOT

    print("=" * 62)
    print("TARIFF SERVICE SELF-TEST")
    print("=" * 62)

    def check(label, fn, expected=None):
        try:
            result = fn()
            note = ""
            if expected is not None and isinstance(result, (int, float)):
                note = "  [OK]" if abs(result - expected) < 0.01 else \
                       "  [WRONG - expected " + str(expected) + "]"
            print("  " + label.ljust(30) + str(result) + note)
        except NotImplementedError:
            print("  " + label.ljust(30) + "not yet implemented")
        except Exception as e:
            print("  " + label.ljust(30) + "ERROR: " + type(e).__name__ + ": " + e.__str__())

    print("\n[1] TEST FIXTURE - hand-checkable round numbers")
    print("    Bands: 0-100 @ 1.00, 101-200 @ 2.00, 201+ @ 3.00, no charge")
    try:
        fixtures = PROJECT_ROOT / "tests" / "test_data"
        test_bands = load_tariffs(base_dir=fixtures, filename="tariffs_test.csv")
        svc = TariffService(test_bands)

        check("50 kWh  -> 50", lambda: svc.calculate_cost(50, False), 50.0)
        check("100 kWh -> 100", lambda: svc.calculate_cost(100, False), 100.0)
        check("150 kWh -> 200", lambda: svc.calculate_cost(150, False), 200.0)
        check("200 kWh -> 300", lambda: svc.calculate_cost(200, False), 300.0)
        check("250 kWh -> 450", lambda: svc.calculate_cost(250, False), 450.0)
        check("0 kWh   -> 0", lambda: svc.calculate_cost(0, False), 0.0)

        print("\n    If 150 gives 300, you used one flat rate for the")
        print("    whole amount instead of filling bands cumulatively.")

        check("effective rate at 150", lambda: svc.effective_rate(150), 1.333)
        check("marginal rate at 150", lambda: svc.marginal_rate(150), 2.0)
        check("marginal rate at 50", lambda: svc.marginal_rate(50), 1.0)
    except NotImplementedError:
        print("  __init__ not yet implemented")
    except Exception as e:
        print("  setup error:", type(e).__name__, e)

    print("\n[2] REAL bands from data/tariffs.csv")
    print("    (illustrative rates - verify against PURC before use)")
    try:
        real = TariffService()
        for kwh in [25, 100, 250, 400, 650, 1000]:
            check(str(kwh) + " kWh/month", lambda k=kwh: real.calculate_cost(k))

        print("\n    Effective rate should RISE across that list -")
        print("    that is the progressive band structure working.")
        for kwh in [25, 100, 250, 400, 650, 1000]:
            check("effective @ " + str(kwh), lambda k=kwh: real.effective_rate(k))

        print("\n[3] Annual costing (must NOT feed 12x into monthly bands)")
        check("3600 kWh/yr", lambda: real.calculate_annual_cost(3600))
        check("  vs wrong way (bands applied to 3600 at once)",
              lambda: real.calculate_cost(3600))
        print("    The first should be MUCH lower. If they match, you")
        print("    forgot to divide by 12 before pricing.")

        print("\n[4] Itemised breakdown for 400 kWh")
        try:
            b = real.breakdown(400)
            print("   ", b)
        except NotImplementedError:
            print("    not yet implemented")
    except NotImplementedError:
        print("  not yet implemented")
    except Exception as e:
        print("  ERROR:", type(e).__name__, e)

    print("\n" + "=" * 62)
