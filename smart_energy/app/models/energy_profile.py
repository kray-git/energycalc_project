"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/models/energy_profile.py  -  The EnergyProfile Model
========================================================================
  Owner:  ____________________
  Build order: STAGE 1 (depends only on Appliance)

  WHAT THIS CLASS IS
    The user's total energy demand. It is the aggregator that sits
    between individual appliances and everything downstream.

    There is deliberately NO User class in this system. A "user" here
    has no login, no saved history, no name - all they are, as far as
    the maths is concerned, is a demand figure. EnergyProfile IS the
    user, expressed as the only thing about them the system needs.

  THE TWO INPUT PATHS
    Path A (appliance-based): user picks appliances from the dropdown,
           the profile sums them.
    Path B (direct):          user already knows they use 450 kWh a
           month and types that in.

    Both paths must end with the same attributes populated, because
    ComparisonEngine must not care which one was used. That is the
    encapsulation boundary this class exists to provide.

  RUBRIC COVERAGE
    [x] OOP - Encapsulation  (internal appliance list; controlled access)
    [x] Collections          (list of Appliance, dict summary, set of
                              categories)
    [x] Loops                (summing over appliances)
    [x] Conditionals         (if/else on input path, ternary)
    [x] Functions            (methods calling other methods)

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.models.energy_profile
========================================================================
"""

from app.models.appliance import Appliance


class EnergyProfile:
    """Total household energy demand, built from appliances or directly."""

    DAYS_PER_MONTH = 30
    DAYS_PER_YEAR = 365

    # Not every appliance runs at once. A house with 10 kW of installed
    # appliances might never draw more than 6 kW simultaneously. This is
    # a standard engineering allowance - cite it in your report.
    DIVERSITY_FACTOR = 0.6

    def __init__(self, location=None):
        """
        Create an empty profile.

        Args:
            location (str, optional): place name, e.g. "Berekuso".
                Used later by WeatherService to fetch solar/wind data.

        ATTRIBUTES TO SET UP
            self.location          - the argument
            self.appliances        - empty list []
            self.daily_demand      - 0.0
            self.monthly_demand    - 0.0
            self.annual_demand     - 0.0
            self.peak_load         - 0.0
            self.input_method      - None  (becomes "appliances" or
                                     "direct" once populated)

        WHY INITIALISE TOTALS TO 0.0 AND NOT None?
            So that a freshly-created profile is still a valid thing to
            do arithmetic on. A None here means every downstream
            calculator needs a None-check.
        """
        # [IMPLEMENT ME]  (~7 lines)
        raise NotImplementedError("EnergyProfile.__init__")

    # ------------------------------------------------------------------
    #  PATH A - APPLIANCE-BASED INPUT
    # ------------------------------------------------------------------

    def add_appliance(self, appliance):
        """
        Add an appliance and refresh the totals.

        Args:
            appliance (Appliance)

        Returns:
            EnergyProfile: self, so calls can be chained -
                profile.add_appliance(a).add_appliance(b)

        Raises:
            TypeError: if `appliance` is not an Appliance instance.
                       Use isinstance(). This stops someone passing a
                       raw dict from the frontend and getting a confusing
                       AttributeError three modules later.

        HINT
            append, set self.input_method = "appliances", call
            self.calculate_total_energy() and self.calculate_peak_load()
            so the totals are never stale, then return self.
        """
        # [IMPLEMENT ME]  (~7 lines)
        raise NotImplementedError("EnergyProfile.add_appliance")

    def remove_appliance(self, name):
        """
        Remove the first appliance whose name matches (case-insensitive).

        Args:
            name (str)

        Returns:
            bool: True if something was removed, False if no match.

        WHY RETURN A BOOL RATHER THAN RAISE?
            Removing something that is not there is not an error the
            user needs an exception for - the API route just reports
            "nothing removed". Reserve exceptions for genuinely broken
            states.

        HINT
            Loop with an index or use enumerate, compare lowercased
            names, pop the match, recalculate the totals, return True.
            Return False after the loop finishes with no match.
        """
        # [IMPLEMENT ME]  (~9 lines)
        raise NotImplementedError("EnergyProfile.remove_appliance")

    def calculate_total_energy(self):
        """
        Sum every appliance's consumption into the profile totals.

        Returns:
            float: daily demand in kWh/day

        SIDE EFFECT (intentional)
            Sets self.daily_demand, self.monthly_demand and
            self.annual_demand.

        IMPORTANT - THE DIRECT-INPUT CASE
            If self.input_method == "direct", the totals were set by
            set_direct_consumption() and there are no appliances to sum.
            This method must NOT wipe them. Return self.daily_demand
            unchanged in that case - this is the "pass-through" branch
            described in the architecture doc.

        HINT
            1. if self.input_method == "direct": return self.daily_demand
            2. total = 0.0
            3. for appliance in self.appliances: total += its daily energy
            4. set the three totals, return daily
        """
        # [IMPLEMENT ME]  (~10 lines)
        raise NotImplementedError("EnergyProfile.calculate_total_energy")

    def calculate_peak_load(self):
        """
        Estimate the largest simultaneous power draw, in kW.

        Returns:
            float: peak load in kW

        SIDE EFFECT
            Sets self.peak_load.

        WHY THIS MATTERS
            Energy totals size the panels/battery. Peak load sizes the
            INVERTER. A system that meets the daily kWh but cannot start
            a 3 kW water heater has failed the user - so the comparison
            report needs both numbers.

        FORMULA
            raw_peak = sum of every appliance's calculate_peak_power()
            peak     = raw_peak * DIVERSITY_FACTOR

        DIRECT-INPUT CASE
            With no appliance list there is nothing to sum. Fall back to
            an estimate: assume the daily energy is drawn over roughly
            8 effective peak-hours, i.e.
                peak = daily_demand / 8.0
            Document this assumption in your report - it is a rough
            heuristic, not a measurement.
        """
        # [IMPLEMENT ME]  (~10 lines)
        raise NotImplementedError("EnergyProfile.calculate_peak_load")

    # ------------------------------------------------------------------
    #  PATH B - DIRECT INPUT
    # ------------------------------------------------------------------

    def set_direct_consumption(self, kwh, period="monthly"):
        """
        Populate the profile from a known consumption figure.

        Args:
            kwh (float): the figure the user typed in
            period (str): "daily", "monthly" or "annual" - what that
                          figure represents

        Returns:
            EnergyProfile: self

        Raises:
            ValueError: if kwh < 0, or period is not one of the three.

        *** THIS METHOD IS YOUR match-case REQUIREMENT ***
            Use match/case on `period` to convert to a daily figure:

                match period:
                    case "daily":   daily = kwh
                    case "monthly": daily = kwh / self.DAYS_PER_MONTH
                    case "annual":  daily = kwh / self.DAYS_PER_YEAR
                    case _:         raise ValueError(...)

            match/case needs Python 3.10 or newer. Check with
            `python3 --version` and tell the team if anyone is older.

        HINT
            After deriving daily, set all three totals from it, set
            self.input_method = "direct", call calculate_peak_load(),
            return self.
        """
        # [IMPLEMENT ME]  (~15 lines)
        raise NotImplementedError("EnergyProfile.set_direct_consumption")

    # ------------------------------------------------------------------
    #  REPORTING
    # ------------------------------------------------------------------

    def get_appliance_categories(self):
        """
        Every distinct category present in the profile.

        Returns:
            set: e.g. {"Kitchen", "Cooling", "Lighting"}

        *** THIS IS YOUR set REQUIREMENT ***
            A set, not a list, because duplicates are meaningless here -
            five Kitchen appliances still means one category.

        CAVEAT
            Appliance does not store a category. Either add one as an
            optional attribute in Appliance.__init__/from_name, or match
            the name back against load_appliances(). Agree which with
            whoever owns appliance.py BEFORE writing this - do not let
            two people solve it two different ways.
        """
        # [IMPLEMENT ME]  (~6 lines)
        raise NotImplementedError("EnergyProfile.get_appliance_categories")

    def get_largest_consumers(self, n=3):
        """
        The n appliances using the most energy, biggest first.

        Args:
            n (int)

        Returns:
            list[tuple]: [(name, daily_kwh), ...] - tuples, not dicts,
                because the pairing is fixed and ordered.

        *** THIS IS YOUR tuple REQUIREMENT ***

        HINT
            Build a list of (name, daily_kwh) tuples, then
                pairs.sort(key=lambda pair: pair[1], reverse=True)
            and return pairs[:n]. Slicing past the end is safe in Python
            - a 2-item list sliced [:3] just gives you 2 items.
        """
        # [IMPLEMENT ME]  (~6 lines)
        raise NotImplementedError("EnergyProfile.get_largest_consumers")

    def summary(self):
        """
        The whole profile as a JSON-safe dictionary.

        Returns:
            dict with keys:
                location, input_method, appliance_count,
                daily_demand_kwh, monthly_demand_kwh,
                annual_demand_kwh, peak_load_kw,
                categories (list - sets are NOT JSON-serialisable, so
                    convert with sorted(...)),
                largest_consumers (list of [name, kwh])

        THIS IS THE OBJECT THE FRONTEND RECEIVES.
            Round the floats to 2 decimals here rather than in
            JavaScript - keep display formatting on the side that owns
            the numbers.
        """
        # [IMPLEMENT ME]  (~14 lines)
        raise NotImplementedError("EnergyProfile.summary")

    def __len__(self):
        """How many appliances - lets you write len(profile)."""
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("EnergyProfile.__len__")

    def __str__(self):
        """e.g. "EnergyProfile(Berekuso): 5 appliances, 12.40 kWh/day"."""
        # [IMPLEMENT ME]  (~3 lines)
        raise NotImplementedError("EnergyProfile.__str__")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":

    def check(label, fn, expected=None):
        try:
            result = fn()
            note = ""
            if expected is not None:
                ok = abs(result - expected) < 0.01 if isinstance(
                    result, (int, float)) else result == expected
                note = "  [OK]" if ok else "  [WRONG - expected " + str(expected) + "]"
            print("  " + label.ljust(30) + str(result) + note)
        except NotImplementedError as e:
            print("  " + label.ljust(30) + "not yet implemented (" + e.__str__() + ")")
        except Exception as e:
            print("  " + label.ljust(30) + "ERROR: " + type(e).__name__ + ": " + e.__str__())

    print("=" * 60)
    print("ENERGY PROFILE SELF-TEST")
    print("=" * 60)

    print("\n[1] Appliance-based path")
    print("    fridge 150W x1 x24h  = 3.60 kWh/day")
    print("    fans    75W x3 x10h  = 2.25 kWh/day")
    print("    bulbs   10W x8 x6h   = 0.48 kWh/day")
    print("    ---------------------------------")
    print("    expected total       = 6.33 kWh/day")
    try:
        profile = EnergyProfile("Berekuso")
        profile.add_appliance(Appliance("Refrigerator", 150, 1, 24))
        profile.add_appliance(Appliance("Ceiling Fan", 75, 3, 10))
        profile.add_appliance(Appliance("LED Bulb", 10, 8, 6))

        check("daily demand", profile.calculate_total_energy, 6.33)
        check("monthly demand", lambda: profile.monthly_demand, 189.9)
        check("annual demand", lambda: profile.annual_demand, 2310.45)
        check("peak load kW", profile.calculate_peak_load, 0.303)
        check("appliance count", lambda: len(profile), 3)
        check("largest consumers", lambda: profile.get_largest_consumers(2))
        check("categories", profile.get_appliance_categories)
        check("str", lambda: str(profile))
    except NotImplementedError:
        print("  __init__ or add_appliance not implemented yet")

    print("\n[2] Removal")
    try:
        profile.remove_appliance("Ceiling Fan")
        check("after removing fans", profile.calculate_total_energy, 4.08)
        check("removing missing item",
              lambda: profile.remove_appliance("Submarine"), False)
    except (NotImplementedError, NameError):
        print("  not implemented yet")

    print("\n[3] Direct-input path (300 kWh/month -> 10.00 kWh/day)")
    try:
        direct = EnergyProfile("Accra")
        direct.set_direct_consumption(300, "monthly")
        check("daily demand", lambda: direct.daily_demand, 10.0)
        check("annual demand", lambda: direct.annual_demand, 3650.0)
        check("recalc is pass-through",
              direct.calculate_total_energy, 10.0)
        check("summary", direct.summary)
    except NotImplementedError:
        print("  not implemented yet")

    print("\n[4] Validation - these SHOULD raise")
    for label, fn in [
        ("negative kWh",
         lambda: EnergyProfile().set_direct_consumption(-5, "monthly")),
        ("bad period",
         lambda: EnergyProfile().set_direct_consumption(300, "fortnightly")),
        ("adding a non-Appliance",
         lambda: EnergyProfile().add_appliance({"name": "dict"})),
    ]:
        try:
            fn()
            print("  " + label.ljust(30) + "[PROBLEM] no error raised")
        except (ValueError, TypeError) as e:
            print("  " + label.ljust(30) + "[OK] " + type(e).__name__)
        except NotImplementedError:
            print("  " + label.ljust(30) + "not yet implemented")

    print("\n" + "=" * 60)
