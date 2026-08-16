"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/models/appliance.py  -  The Appliance Model
========================================================================
  Owner:  ____________________
  Build order: STAGE 1 (no dependencies except data_loader)

  INSTRUCTIONS
    - Implement every method marked  # [IMPLEMENT ME].
    - Do NOT change method names, parameter names, or return types -
      other people's modules are already written against them.
    - Run this file's self-test after each method you finish.

  WHAT THIS CLASS IS
    One appliance the user owns: a fridge, three ceiling fans, an AC.
    It knows how much energy IT uses. It knows nothing about the user's
    total, about other appliances, or about energy sources. Keeping it
    ignorant is deliberate - it makes the class trivial to test.

  RUBRIC COVERAGE
    [x] OOP - Encapsulation  (attributes bundled with the methods that
                              act on them; validation guards them)
    [x] Conditionals         (if/else validation, ternary in __str__)
    [x] Collections          (from_name searches a list of dicts)
    [x] Files                (from_name reads via data_loader)

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.models.appliance

    Note the -m and the dotted path. Running
      python3 app/models/appliance.py
    fails with "No module named 'app'" - Python needs the package root
    on its path, which -m handles for you.
========================================================================
"""

from app.data.data_loader import load_appliances


class Appliance:
    """A single electrical appliance in the user's home."""

    # Hours in a day / days in a month - named constants beat magic
    # numbers scattered through the methods.
    DAYS_PER_MONTH = 30
    DAYS_PER_YEAR = 365

    def __init__(self, name, power_rating, quantity=1, hours_of_use=1.0):
        """
        Create an appliance.

        Args:
            name (str): e.g. "Refrigerator"
            power_rating (float): power draw of ONE unit, in watts
            quantity (int): how many the user owns
            hours_of_use (float): average hours ONE unit runs per day

        Raises:
            ValueError: if power_rating < 0, quantity < 1, or
                        hours_of_use is outside 0-24.

        WHY VALIDATE HERE?
            This is the encapsulation pillar in practice. If a bad value
            can never enter the object, no downstream calculator has to
            defend against negative kWh. Catch it at the boundary once.

        HINT
            Assign the four attributes, then check each constraint with
            an if and raise ValueError with a message that says which
            value was wrong and what it was.
        """
        # [IMPLEMENT ME]  (~8 lines)
        raise NotImplementedError("Appliance.__init__")

    def calculate_daily_energy(self):
        """
        Energy this appliance consumes in one day.

        Returns:
            float: kilowatt-hours per day (kWh/day)

        FORMULA
            kWh/day = (watts * quantity * hours_of_use) / 1000

            The /1000 converts watt-hours to kilowatt-hours. Forgetting
            it is the single most common bug in this project - your
            numbers come out 1000x too big and every downstream cost
            looks absurd.

        WORKED EXAMPLE
            Three 75 W ceiling fans, 10 hours a day:
            (75 * 3 * 10) / 1000 = 2.25 kWh/day
        """
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("Appliance.calculate_daily_energy")

    def calculate_monthly_energy(self):
        """
        Energy consumed in one month.

        Returns:
            float: kWh/month

        HINT
            Call calculate_daily_energy() and multiply by
            DAYS_PER_MONTH. Do NOT re-derive the daily formula here -
            if the /1000 ever needs fixing you want exactly one place
            to fix it.
        """
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("Appliance.calculate_monthly_energy")

    def calculate_annual_energy(self):
        """
        Energy consumed in one year.

        Returns:
            float: kWh/year

        HINT
            Same pattern as monthly, with DAYS_PER_YEAR.
        """
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("Appliance.calculate_annual_energy")

    def calculate_peak_power(self):
        """
        Maximum instantaneous power draw of all units of this appliance.

        Returns:
            float: kilowatts (kW)

        WHY THIS IS NOT THE SAME AS DAILY ENERGY
            Energy is power x time (how much you consume). Peak power is
            the instantaneous draw (how big your system must be). A
            2000 W kettle used 30 minutes a day is tiny on energy but
            huge on peak - and it is peak that decides whether an
            inverter can start it at all.

        FORMULA
            kW = (watts * quantity) / 1000        <- no hours term
        """
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("Appliance.calculate_peak_power")

    def to_dict(self):
        """
        Represent this appliance as a plain dictionary.

        Returns:
            dict: {"name", "power_rating", "quantity", "hours_of_use",
                   "daily_kwh"}

        WHY THIS EXISTS
            Flask can convert dicts and lists to JSON, but it cannot
            convert your custom Appliance object. Any object that ever
            travels to the frontend needs a to_dict().

        HINT
            Include the computed daily_kwh - the frontend displays it
            and should not have to recompute the formula in JavaScript.
        """
        # [IMPLEMENT ME]  (~7 lines)
        raise NotImplementedError("Appliance.to_dict")

    @classmethod
    def from_name(cls, name, quantity=1, hours_of_use=None):
        """
        Build an Appliance by looking its defaults up in the catalogue.

        Args:
            name (str): must match a 'name' in data/appliances.csv
                        (case-insensitive)
            quantity (int)
            hours_of_use (float, optional): if None, use the catalogue's
                typical_hours_per_day.

        Returns:
            Appliance

        Raises:
            ValueError: if no catalogue row matches `name`. Include the
                        attempted name in the message.

        WHAT IS A @classmethod?
            A second way to build the object. Regular __init__ needs you
            to know the wattage; this one looks it up for you. `cls` is
            the class itself, so `cls(...)` calls the constructor. This
            is called a "factory method".

        HINT
            1. rows = load_appliances()
            2. loop over rows, compare row["name"].lower() to name.lower()
            3. on a match: decide hours (ternary is neat here - use the
               passed value if it is not None, else the catalogue's)
            4. return cls(name=..., power_rating=row["default_watts"], ...)
            5. after the loop with no match, raise ValueError
        """
        # [IMPLEMENT ME]  (~10 lines)
        raise NotImplementedError("Appliance.from_name")

    def __str__(self):
        """
        Human-readable one-liner, e.g.
            "3x Ceiling Fan (75W, 10.0h/day) = 2.25 kWh/day"

        WHY OVERRIDE __str__?
            It is what print(appliance) uses. Without it you get the
            useless <app.models.appliance.Appliance object at 0x7f...>.
            This is polymorphism in its smallest form - your class
            supplying its own version of a behaviour Python already has.

        HINT - use a ternary for the plural, e.g.
            unit = "unit" if self.quantity == 1 else "units"
        """
        # [IMPLEMENT ME]  (~3 lines)
        raise NotImplementedError("Appliance.__str__")

    def __repr__(self):
        """Unambiguous form, shown when an Appliance sits inside a list."""
        # [IMPLEMENT ME]  (1 line)  e.g. return "Appliance('Fan', 75, 3, 10)"
        raise NotImplementedError("Appliance.__repr__")


# ======================================================================
#  SELF-TEST
#  Every check is wrapped so unimplemented methods report cleanly
#  instead of crashing the run. Expected values are stated so you can
#  verify correctness, not just absence of errors.
# ======================================================================
if __name__ == "__main__":

    def check(label, fn, expected=None):
        """Run fn(), print the result or why it could not run."""
        try:
            result = fn()
            note = ""
            if expected is not None:
                ok = abs(result - expected) < 0.001 if isinstance(
                    result, (int, float)) else result == expected
                note = "  [OK]" if ok else "  [WRONG - expected " + str(expected) + "]"
            print("  " + label.ljust(28) + str(result) + note)
        except NotImplementedError:
            print("  " + label.ljust(28) + "not yet implemented")
        except Exception as e:
            print("  " + label.ljust(28) + "ERROR: " + type(e).__name__ + ": " + e.__str__())

    print("=" * 60)
    print("APPLIANCE SELF-TEST")
    print("=" * 60)

    print("\n[1] Three 75W ceiling fans, 10 h/day")
    try:
        fan = Appliance("Ceiling Fan", 75, 3, 10)
        check("daily kWh", fan.calculate_daily_energy, 2.25)
        check("monthly kWh", fan.calculate_monthly_energy, 67.5)
        check("annual kWh", fan.calculate_annual_energy, 821.25)
        check("peak kW", fan.calculate_peak_power, 0.225)
        check("to_dict", fan.to_dict)
        check("str", lambda: str(fan))
    except NotImplementedError:
        print("  __init__ not yet implemented - nothing else can run")

    print("\n[2] One fridge, 150W, 24 h/day")
    try:
        fridge = Appliance("Refrigerator", 150, 1, 24)
        check("daily kWh", fridge.calculate_daily_energy, 3.6)
    except NotImplementedError:
        print("  __init__ not yet implemented")

    print("\n[3] Catalogue lookup (from_name)")
    check("from_name('LED Bulb', 10)",
          lambda: str(Appliance.from_name("LED Bulb", 10)))
    check("case-insensitive",
          lambda: str(Appliance.from_name("ceiling fan", 1)))

    print("\n[4] Validation - these SHOULD raise ValueError")
    for label, args in [("negative watts", ("Bad", -5, 1, 1)),
                        ("zero quantity", ("Bad", 100, 0, 1)),
                        ("25 hours/day", ("Bad", 100, 1, 25))]:
        try:
            Appliance(*args)
            print("  " + label.ljust(28) + "[PROBLEM] no error raised")
        except ValueError as e:
            print("  " + label.ljust(28) + "[OK] ValueError: " + e.__str__())
        except NotImplementedError:
            print("  " + label.ljust(28) + "not yet implemented")

    print("\n" + "=" * 60)
