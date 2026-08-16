"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/models/energy_source.py  -  The EnergySource Hierarchy
========================================================================
  Owner:  ____________________
  Build order: STAGE 1 - but this is the biggest file. Consider
               splitting the subclasses between two people (e.g. one
               takes Grid+Solar, the other Wind+Biomass+Hydro) while
               ONE person owns the abstract base class.

  *** THIS FILE IS WHERE ALL FOUR OOP PILLARS LIVE ***
  Your report will point at this file. Make sure you can explain it.

    ABSTRACTION   EnergySource defines WHAT every source must do
                  (produce energy, cost money, emit carbon) without
                  saying HOW. You can never instantiate it directly.

    INHERITANCE   Grid, Solar, Wind, Biomass and Hydropower each extend
                  it, reusing the shared attributes and helper methods.

    POLYMORPHISM  ComparisonEngine calls source.calculate_energy() on
                  whatever it is handed and the right version runs. The
                  engine contains no if/elif chain over source types -
                  that is the whole point.

    ENCAPSULATION Each subclass hides its own physics. Nobody outside
                  Wind needs to know about swept area or the Betz limit.

  RUBRIC COVERAGE
    [x] OOP - all four pillars    [x] Files (catalogue lookups)
    [x] Conditionals - if/else, match-case, ternary
    [x] Collections - dicts, lists, tuples
    [x] Loops       [x] Library import - math (trig)

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.models.energy_source
========================================================================
"""

import math
from abc import ABC, abstractmethod

from app.data.data_loader import (
    load_emission_factors,
    load_solar_panels,
    load_wind_turbines,
    load_biomass_systems,
    load_hydro_systems,
)


# ======================================================================
#  ABSTRACT BASE CLASS
# ======================================================================

class EnergySource(ABC):
    """
    The contract every energy source must satisfy.

    WHAT ABC AND @abstractmethod ACTUALLY DO
        Inheriting from ABC ("Abstract Base Class") plus marking methods
        @abstractmethod means Python REFUSES to instantiate this class,
        and refuses to instantiate any subclass that has not overridden
        every abstract method.

        Try it once you have implemented things - EnergySource("x") will
        raise TypeError. That enforcement is the difference between
        abstraction as a real language feature and abstraction as a
        comment saying "please override this".
    """

    HOURS_PER_YEAR = 8760          # 365 * 24
    DAYS_PER_YEAR = 365

    def __init__(self, name, capacity_kw=0.0, capital_cost=0.0,
                 lifespan_years=20, maintenance_cost_per_year=0.0):
        """
        Shared setup for every source.

        Args:
            name (str): display name, e.g. "Solar PV"
            capacity_kw (float): installed/rated capacity in kW
            capital_cost (float): upfront cost in GHS (0 for grid)
            lifespan_years (int): expected service life
            maintenance_cost_per_year (float): GHS/year

        ALSO SET
            self.emission_factor - look it up now via
            load_emission_factors() using self.source_key(), so each
            subclass does not repeat the file read. Use .get(key, 0.0)
            so an unknown key degrades to zero rather than crashing.

        NOTE
            Subclasses call this with super().__init__(...) and then add
            their own attributes. That is inheritance doing real work -
            five subclasses, one copy of this setup.
        """
        # [IMPLEMENT ME]  (~8 lines)
        raise NotImplementedError("EnergySource.__init__")

    # ---------------- abstract methods - each subclass MUST override --

    @abstractmethod
    def source_key(self):
        """
        The short lowercase identifier for this source.

        Returns:
            str: one of "grid", "solar", "wind", "biomass", "hydro"

        Used for emission-factor lookup and for matching the source_a /
        source_b strings the frontend sends.
        """

    @abstractmethod
    def calculate_energy(self, days=365, context=None):
        """
        How much energy this source can SUPPLY over the period.

        Args:
            days (int): length of the period
            context (dict, optional): environmental inputs the source
                may need, e.g.
                    {"peak_sun_hours": 5.2, "wind_speed_ms": 4.1,
                     "latitude": 5.75, "day_of_year": 200}
                Every subclass must cope with context=None by falling
                back to a documented default. The app has to work when
                the weather API is unreachable.

        Returns:
            float: kWh available over the period

        THIS IS THE POLYMORPHIC METHOD. Same call, five different
        physics implementations behind it.
        """

    @abstractmethod
    def calculate_cost(self, kwh, days=365):
        """
        Cost of supplying `kwh` over the period.

        Args:
            kwh (float): energy actually consumed
            days (int)

        Returns:
            dict: {"capital": float, "running": float, "total": float}
                  all in GHS.

        WHY A DICT RATHER THAN ONE NUMBER
            Grid is nearly all running cost; solar is nearly all
            capital. Collapsing them to a single figure hides exactly
            the difference the user is trying to see.
        """

    def calculate_emissions(self, kwh):
        """
        CO2 attributable to `kwh` from this source.

        Args:
            kwh (float)

        Returns:
            float: kg CO2

        FORMULA
            kg_co2 = kwh * self.emission_factor

        NOT ABSTRACT - the formula is identical for every source; only
        the factor differs, and that already lives on the instance. A
        concrete method on the base class is inheritance doing its job.
        Do not copy this into the subclasses.
        """
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("EnergySource.calculate_emissions")

    # ---------------- shared concrete helpers -------------------------

    def annual_maintenance(self, days=365):
        """
        Maintenance cost pro-rated to the period.

        FORMULA
            maintenance_cost_per_year * (days / 365)
        """
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("EnergySource.annual_maintenance")

    def lifetime_cost(self, annual_kwh):
        """
        Total cost of ownership across the full lifespan.

        Args:
            annual_kwh (float): yearly consumption

        Returns:
            float: GHS over lifespan_years

        HINT
            capital (paid once) + lifespan_years * (one year's running
            cost + one year's maintenance). Get the running cost by
            calling self.calculate_cost(annual_kwh, 365)["running"] -
            polymorphism means this line works for all five subclasses
            without change.

        SIMPLIFICATION TO DECLARE IN YOUR REPORT
            This ignores inflation, tariff escalation, discount rates
            and mid-life equipment replacement (inverters typically need
            replacing around year 10-12). Say so explicitly rather than
            letting a marker find it.
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("EnergySource.lifetime_cost")

    def is_renewable(self):
        """
        Returns:
            bool: True for everything except grid.

        HINT - one line with a ternary or a direct comparison:
            return self.source_key() != "grid"
        """
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("EnergySource.is_renewable")

    def to_dict(self):
        """
        JSON-safe description of this source.

        Returns:
            dict: {"name", "key", "capacity_kw", "capital_cost",
                   "lifespan_years", "renewable", "emission_factor"}
        """
        # [IMPLEMENT ME]  (~9 lines)
        raise NotImplementedError("EnergySource.to_dict")

    def __str__(self):
        """e.g. "Solar PV (3.15 kW, renewable)"."""
        # [IMPLEMENT ME]  (~3 lines)
        raise NotImplementedError("EnergySource.__str__")


# ======================================================================
#  SUBCLASS 1 - GRID ELECTRICITY
# ======================================================================

class GridElectricity(EnergySource):
    """
    Mains supply from ECG/NEDCo.

    The baseline every other source is measured against. Zero capital
    cost, unlimited supply, but metered running cost and the highest
    emission factor - plus the reliability problem below.
    """

    # Rough allowance for outages. 0.92 means the grid is assumed
    # available 92% of the time. VERIFY against published SAIDI/SAIFI
    # figures for your region before using this in the report.
    DEFAULT_RELIABILITY = 0.92

    def __init__(self, tariff_service=None, reliability=None):
        """
        Args:
            tariff_service (TariffService, optional): supplies banded
                pricing. If None, fall back to FLAT_RATE below and note
                the approximation.
            reliability (float, optional): 0-1 availability.

        HINT
            super().__init__(name="Grid Electricity", capacity_kw=0.0,
                             capital_cost=0.0, lifespan_years=1,
                             maintenance_cost_per_year=0.0)
            then set self.tariff_service and self.reliability.

        WHY capacity_kw = 0
            The grid has no user-side installed capacity. Guard against
            dividing by it anywhere.
        """
        FLAT_RATE = 1.42   # GHS/kWh fallback - illustrative only
        # [IMPLEMENT ME]  (~5 lines)
        raise NotImplementedError("GridElectricity.__init__")

    def source_key(self):
        """Returns "grid"."""
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("GridElectricity.source_key")

    def calculate_energy(self, days=365, context=None):
        """
        Energy the grid can deliver.

        The grid is not capacity-limited from the user's side, so it
        supplies whatever is demanded - EXCEPT during outages.

        Args:
            context (dict): should contain "demand_kwh" - the demand it
                is being asked to meet. Without it, return 0.0, since
                an unlimited source with no demand figure has no
                meaningful answer.

        FORMULA
            supplied = demand_kwh * reliability

        DESIGN NOTE
            This is why calculate_energy takes a context dict rather
            than a fixed parameter list - grid needs demand, solar needs
            sunlight, hydro needs flow. A shared signature with a
            flexible payload is what lets the engine treat them alike.
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("GridElectricity.calculate_energy")

    def calculate_cost(self, kwh, days=365):
        """
        Metered cost of `kwh`.

        HINT
            if self.tariff_service is not None:
                use it to price kwh across the bands
            else:
                kwh * FLAT_RATE          <- store FLAT_RATE on self

            capital is 0.0, running is the metered cost, total = running.
        """
        # [IMPLEMENT ME]  (~8 lines)
        raise NotImplementedError("GridElectricity.calculate_cost")


# ======================================================================
#  SUBCLASS 2 - SOLAR PV
# ======================================================================

class Solar(EnergySource):
    """
    Rooftop photovoltaic array.

    Ghana sits near the equator with strong, consistent insolation -
    typically 4.5-6.0 peak sun hours a day. This is the source most
    likely to win a comparison here, which is exactly why the maths
    must be honest.
    """

    # Losses between panel nameplate rating and delivered AC energy:
    # inverter losses, wiring, dust/soiling, high-temperature derating.
    # 0.75 is the standard PVWatts default - cite it.
    SYSTEM_DERATE = 0.75
    DEFAULT_PEAK_SUN_HOURS = 5.0   # conservative Ghana average

    def __init__(self, panel_model=None, num_panels=1, battery_kwh=0.0):
        """
        Args:
            panel_model (str, optional): must match a 'model' in
                data/solar_panels.csv. If None, use the first row.
            num_panels (int)
            battery_kwh (float): storage capacity, 0 for none.

        WHY BATTERY IS AN ATTRIBUTE AND NOT ITS OWN CLASS HIERARCHY
            A battery never exists independently of the system it serves
            in this app. A parallel EnergyStorage/Battery class tree
            would add inheritance with nothing to inherit. If you later
            need battery chemistry, cycle life and depth-of-discharge,
            revisit - but do not build it speculatively.

        HINT
            1. panels = load_solar_panels()
            2. find the matching row (or take panels[0] if None)
            3. capacity_kw = row["rated_watts"] * num_panels / 1000
            4. capital_cost = row["cost_ghs"] * num_panels
                              + battery cost if battery_kwh > 0
                              (assume ~2500 GHS/kWh - declare this)
            5. maintenance ~ 1% of capital per year (cleaning, checks)
            6. super().__init__(...) then store panel_model, num_panels,
               battery_kwh, efficiency, area
        """
        # [IMPLEMENT ME]  (~18 lines)
        raise NotImplementedError("Solar.__init__")

    def source_key(self):
        """Returns "solar"."""
        # [IMPLEMENT ME]
        raise NotImplementedError("Solar.source_key")

    def estimate_peak_sun_hours(self, latitude, day_of_year):
        """
        Estimate daily peak sun hours from geometry alone.

        *** THIS IS YOUR math-MODULE / TRIGONOMETRY REQUIREMENT ***

        This is the fallback used when the weather API is unreachable.
        It is astronomy, not meteorology - it gives clear-sky potential
        and takes no account of cloud cover, so it will read optimistic
        during the rainy season. Say so in the report.

        Args:
            latitude (float): degrees, positive north (Accra ~ 5.6)
            day_of_year (int): 1-365

        Returns:
            float: estimated peak sun hours per day

        THE MATHS - work through it in this order

        1. Solar declination (Cooper's equation), in degrees:
               decl = 23.45 * sin(radians(360 * (284 + n) / 365))

           Earth's axial tilt is 23.45 degrees; this tracks where the
           sun sits relative to the equator on day n.

        2. Sunset hour angle, in degrees:
               ws = degrees(acos(-tan(radians(lat)) * tan(radians(decl))))

           CLAMP the argument to acos into [-1, 1] before calling it.
           Near the poles it legitimately exceeds that range (polar day
           or night) and acos raises ValueError. Ghana never triggers
           it, but a crash on an out-of-range input is still a bug:
               arg = max(-1.0, min(1.0, arg))

        3. Daylight hours:
               daylight = (2.0 / 15.0) * ws

           15 because the Earth turns 15 degrees per hour.

        4. Peak sun hours are NOT daylight hours. "Peak sun hour" means
           one hour at 1000 W/m2. The sun is only near that intensity
           around midday, so scale down:
               psh = daylight * 0.45

           0.45 is an empirical clear-sky factor. State that it is
           empirical rather than derived.

        5. Clamp the result to a sane range, e.g. 3.0 to 7.0, so a
           strange input cannot produce a nonsense system size.

        SANITY CHECK
            Accra (lat 5.6) in June should give roughly 5.4-5.6 PSH.
            If you get 12, you forgot step 4. If you get 0.09, you fed
            degrees into a function expecting radians.
        """
        # [IMPLEMENT ME]  (~12 lines)
        raise NotImplementedError("Solar.estimate_peak_sun_hours")

    def calculate_energy(self, days=365, context=None):
        """
        Energy the array generates over the period.

        FORMULA
            daily_kwh = capacity_kw * peak_sun_hours * SYSTEM_DERATE
            total     = daily_kwh * days

        CHOOSING peak_sun_hours - in this order of preference:
            1. context["peak_sun_hours"]  (live, from WeatherService)
            2. estimate_peak_sun_hours(context["latitude"],
                                       context["day_of_year"])
            3. DEFAULT_PEAK_SUN_HOURS

        HINT
            Nested if/elif/else over what context actually contains.
            Remember context may be None - check that first.
        """
        # [IMPLEMENT ME]  (~12 lines)
        raise NotImplementedError("Solar.calculate_energy")

    def calculate_cost(self, kwh, days=365):
        """
        Cost of solar over the period.

        Args:
            kwh: consumption. Note solar's cost barely depends on this -
                the array costs what it costs whether you use its output
                or waste it. That asymmetry versus the grid is the core
                economic insight of the whole project.

        HINT
            capital = self.capital_cost (charged once, at year 0)
            running = self.annual_maintenance(days)
            total   = capital + running
        """
        # [IMPLEMENT ME]  (~5 lines)
        raise NotImplementedError("Solar.calculate_cost")


# ======================================================================
#  SUBCLASS 3 - WIND
# ======================================================================

class Wind(EnergySource):
    """
    Small wind turbine.

    HONEST CONTEXT FOR YOUR REPORT: most of Ghana has poor wind
    resource inland (annual means around 3-4 m/s, below many turbines'
    rated speed). Viable sites are mainly coastal - the Ada Foah and
    Anloga corridor. Do not let the model imply otherwise; a comparison
    tool that flatters a bad option is worse than useless.
    """

    AIR_DENSITY = 1.225        # kg/m3 at sea level, 15 C
    BETZ_LIMIT = 0.593         # theoretical max fraction of wind
                               # kinetic energy any turbine can extract
    PRACTICAL_CP = 0.35        # real small turbines - well under Betz
    DEFAULT_WIND_SPEED = 3.5   # m/s, conservative inland Ghana

    def __init__(self, turbine_model=None, num_turbines=1):
        """
        HINT - same shape as Solar.__init__:
            load_wind_turbines(), find the row, capacity =
            rated_kw * num_turbines, capital = cost * num_turbines,
            maintenance ~3% of capital (turbines have moving parts and
            need far more upkeep than panels), then super().__init__().
            Store rotor_diameter_m, cut_in, rated and cut_out speeds.
        """
        # [IMPLEMENT ME]  (~16 lines)
        raise NotImplementedError("Wind.__init__")

    def source_key(self):
        """Returns "wind"."""
        # [IMPLEMENT ME]
        raise NotImplementedError("Wind.source_key")

    def swept_area(self):
        """
        Rotor swept area in m2.

        FORMULA
            A = pi * (diameter / 2) ** 2

        Use math.pi. This is also a second, simpler home for the math
        module if the trig in Solar is being handled by someone else.
        """
        # [IMPLEMENT ME]  (1 line)
        raise NotImplementedError("Wind.swept_area")

    def power_output(self, wind_speed):
        """
        Instantaneous power at a given wind speed, in kW.

        Args:
            wind_speed (float): m/s

        Returns:
            float: kW (0.0 outside the operating window)

        THE PHYSICS
            P = 0.5 * rho * A * v^3 * Cp        (watts)

            Note v CUBED. Doubling wind speed gives EIGHT times the
            power. This is why a site averaging 3 m/s is not "a bit
            worse" than one averaging 6 m/s - it is eight times worse.
            Make this point in your report.

        *** THIS METHOD IS A GOOD HOME FOR match-case ***
            The turbine has four operating regimes. Express them as a
            match on a computed regime string, or as if/elif:

              below cut-in        -> 0.0     (not enough wind to turn)
              cut-in to rated     -> the cubic formula, capped at rated
              rated to cut-out    -> rated_kw (turbine is limited)
              above cut-out       -> 0.0     (shuts down for safety)

        HINT
            watts = 0.5 * AIR_DENSITY * self.swept_area()
                    * wind_speed**3 * PRACTICAL_CP
            then / 1000 for kW, then min(that, rated) per turbine, then
            multiply by num_turbines.
        """
        # [IMPLEMENT ME]  (~15 lines)
        raise NotImplementedError("Wind.power_output")

    def calculate_energy(self, days=365, context=None):
        """
        Energy generated over the period.

        FORMULA
            kWh = power_output(v) * 24 * days * CAPACITY_ADJUST

        THE TRAP TO AVOID
            Using power_output(mean_wind_speed) directly UNDERESTIMATES
            real output, because power depends on v^3 and the average of
            cubes exceeds the cube of the average. Proper treatment uses
            a Weibull distribution over the wind speed histogram.

            That is beyond this project's scope. Use the mean speed,
            apply a modest correction factor (~1.9 is a common Rayleigh
            approximation), and DOCUMENT the simplification. A stated
            simplification is good engineering; an unstated one is an
            error.

        Wind speed source: context["wind_speed_ms"], else DEFAULT.
        """
        # [IMPLEMENT ME]  (~10 lines)
        raise NotImplementedError("Wind.calculate_energy")

    def calculate_cost(self, kwh, days=365):
        """Same structure as Solar.calculate_cost."""
        # [IMPLEMENT ME]  (~5 lines)
        raise NotImplementedError("Wind.calculate_cost")


# ======================================================================
#  SUBCLASS 4 - BIOMASS
# ======================================================================

class Biomass(EnergySource):
    """
    Biogas digester or gasifier running on agricultural residue.

    Unlike solar and wind this is DISPATCHABLE - it runs on demand, day
    or night, no storage needed. That is a genuine advantage the report
    should credit it with. The catch is a continuous feedstock supply,
    which turns an energy problem into a logistics problem.
    """

    MJ_PER_KWH = 3.6           # 1 kWh = 3.6 megajoules
    DEFAULT_FEEDSTOCK_KG_DAY = 50.0
    DEFAULT_AVAILABILITY = 0.85   # downtime for maintenance/feed gaps

    def __init__(self, system_model=None, feedstock_kg_per_day=None):
        """
        HINT
            load_biomass_systems(), select the row, capacity =
            rated_kw, capital = cost_ghs, maintenance ~5% of capital
            (highest of any source - daily feeding, ash removal,
            digester servicing). Store calorific value and conversion
            efficiency from the row.
        """
        # [IMPLEMENT ME]  (~14 lines)
        raise NotImplementedError("Biomass.__init__")

    def source_key(self):
        """Returns "biomass"."""
        # [IMPLEMENT ME]
        raise NotImplementedError("Biomass.source_key")

    def energy_from_feedstock(self, kg):
        """
        Electrical energy obtainable from `kg` of feedstock.

        Returns:
            float: kWh

        FORMULA
            MJ_in   = kg * calorific_value_mj_per_kg
            MJ_out  = MJ_in * (conversion_efficiency_percent / 100)
            kWh     = MJ_out / MJ_PER_KWH

        SANITY CHECK
            50 kg of cow dung at 18 MJ/kg and 22% efficiency:
            50*18 = 900 MJ, *0.22 = 198 MJ, /3.6 = 55 kWh.
            If you get 198 you forgot the /3.6 conversion.
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("Biomass.energy_from_feedstock")

    def calculate_energy(self, days=365, context=None):
        """
        Energy over the period - the LOWER of two limits:

            a) feedstock limit: energy_from_feedstock(daily_kg) * days
            b) capacity limit:  capacity_kw * 24 * days * availability

        Take min() of the two. A generator cannot exceed its rating no
        matter how much you feed it, and cannot exceed its fuel no
        matter how big it is. Whichever binds first is the real answer.

        context may override "feedstock_kg_per_day".
        """
        # [IMPLEMENT ME]  (~10 lines)
        raise NotImplementedError("Biomass.calculate_energy")

    def calculate_cost(self, kwh, days=365):
        """
        Unlike solar/wind, biomass has a REAL ongoing fuel cost - unless
        the feedstock is farm waste the user already has, in which case
        the cost is labour rather than cash.

        HINT
            capital = self.capital_cost
            fuel    = feedstock_kg_per_day * days * FEEDSTOCK_COST_PER_KG
            running = fuel + self.annual_maintenance(days)

            Set FEEDSTOCK_COST_PER_KG as a class constant (try 0.15 GHS
            for purchased residue, or 0.0 for own-farm waste) and expose
            it as a constructor option if you have time.
        """
        # [IMPLEMENT ME]  (~7 lines)
        raise NotImplementedError("Biomass.calculate_cost")


# ======================================================================
#  SUBCLASS 5 - HYDROPOWER
# ======================================================================

class Hydropower(EnergySource):
    """
    Micro/pico hydro on a stream or river.

    The most site-dependent source of the five: without falling water
    on the property it is not an option at any price. When the site
    does exist it is often the best of the five - highest capacity
    factor, longest lifespan, lowest emissions.
    """

    WATER_DENSITY = 1000.0     # kg/m3
    GRAVITY = 9.81             # m/s2
    DEFAULT_HEAD_M = 5.0
    DEFAULT_FLOW_M3S = 0.1
    DEFAULT_CAPACITY_FACTOR = 0.5   # allows for dry-season flow drop

    def __init__(self, system_model=None, head_m=None, flow_m3s=None):
        """
        Args:
            head_m (float): vertical drop available, metres
            flow_m3s (float): water flow, cubic metres per second

        HINT
            load_hydro_systems(), pick the row, use head/flow from the
            arguments where given else the row's minimums. Maintenance
            ~2% of capital. Store turbine_efficiency_percent.
        """
        # [IMPLEMENT ME]  (~14 lines)
        raise NotImplementedError("Hydropower.__init__")

    def source_key(self):
        """Returns "hydro"."""
        # [IMPLEMENT ME]
        raise NotImplementedError("Hydropower.source_key")

    def hydraulic_power(self):
        """
        Electrical power available from the site, in kW.

        FORMULA
            P(watts) = rho * g * Q * H * efficiency
                rho = 1000 kg/m3, g = 9.81, Q = flow m3/s,
                H = head m, efficiency as a fraction

            then / 1000 for kW.

        SANITY CHECK
            5 m head, 0.1 m3/s, 70% efficient:
            1000 * 9.81 * 0.1 * 5 * 0.7 = 3433 W = 3.43 kW
            If you get 3,433,500 you forgot to convert efficiency from
            percent to a fraction.

        NOTE
            No trig here, but this is a clean derivation from potential
            energy: mgh per second, with mass flow = rho * Q. Worth
            explaining that way in the report.
        """
        # [IMPLEMENT ME]  (~4 lines)
        raise NotImplementedError("Hydropower.hydraulic_power")

    def calculate_energy(self, days=365, context=None):
        """
        FORMULA
            kWh = hydraulic_power() * 24 * days * capacity_factor

        The capacity factor is doing important work: streams in Ghana
        run much lower in the January-March dry season. A design based
        on wet-season flow will disappoint its owner every year.
        context may supply "capacity_factor" or "flow_m3s".
        """
        # [IMPLEMENT ME]  (~8 lines)
        raise NotImplementedError("Hydropower.calculate_energy")

    def calculate_cost(self, kwh, days=365):
        """
        Same shape as Solar/Wind, but note that real micro-hydro civil
        works (intake, penstock, tailrace) often cost more than the
        turbine itself. The catalogue cost_ghs is equipment-only -
        flag this limitation in the report.
        """
        # [IMPLEMENT ME]  (~5 lines)
        raise NotImplementedError("Hydropower.calculate_cost")


# ======================================================================
#  SOURCE REGISTRY
# ======================================================================
#  Maps the string keys the frontend sends ("source_a": "solar") to the
#  classes above.
#
#  *** USE THIS INSTEAD OF WRITING AN if/elif CHAIN IN THE ROUTE. ***
#  Adding a sixth source later should mean adding one line here, not
#  editing branching logic in three files.
#
#      cls = SOURCE_REGISTRY["solar"]
#      source = cls()
# ======================================================================

SOURCE_REGISTRY = {
    "grid": GridElectricity,
    "solar": Solar,
    "wind": Wind,
    "biomass": Biomass,
    "hydro": Hydropower,
}


def create_source(key, **kwargs):
    """
    Build a source instance from its string key.

    Args:
        key (str): a key in SOURCE_REGISTRY (case-insensitive)
        **kwargs: passed to the class constructor

    Returns:
        EnergySource

    Raises:
        ValueError: listing the valid keys, if `key` is unknown.

    HINT
        key = key.strip().lower()
        if key not in SOURCE_REGISTRY: raise ValueError(...)
        return SOURCE_REGISTRY[key](**kwargs)
    """
    # [IMPLEMENT ME]  (~5 lines)
    raise NotImplementedError("create_source")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":

    def check(label, fn, expected=None, tol=0.05):
        try:
            result = fn()
            note = ""
            if expected is not None and isinstance(result, (int, float)):
                note = "  [OK]" if abs(result - expected) <= tol * max(
                    1.0, abs(expected)) else "  [CHECK - expected ~" + str(expected) + "]"
            print("  " + label.ljust(32) + str(result) + note)
        except NotImplementedError as e:
            print("  " + label.ljust(32) + "not yet implemented")
        except Exception as e:
            print("  " + label.ljust(32) + "ERROR: " + type(e).__name__ + ": " + e.__str__())

    print("=" * 62)
    print("ENERGY SOURCE SELF-TEST")
    print("=" * 62)

    print("\n[0] Abstraction - EnergySource must NOT be instantiable")
    try:
        EnergySource("Generic")
        print("  [PROBLEM] abstract class was instantiated")
    except TypeError:
        print("  [OK] TypeError - abstract class correctly blocked")
    except NotImplementedError:
        print("  __init__ not implemented yet (expected at this stage)")

    print("\n[1] Grid")
    check("energy for 300 kWh demand",
          lambda: GridElectricity().calculate_energy(
              30, {"demand_kwh": 300}), 276.0)
    check("cost of 300 kWh", lambda: GridElectricity().calculate_cost(300))
    check("renewable?", lambda: GridElectricity().is_renewable(), None)
    check("emissions of 300 kWh",
          lambda: GridElectricity().calculate_emissions(300), 114.0)

    print("\n[2] Solar - 10 x Mono-350 = 3.5 kW")
    check("capacity kW", lambda: Solar("Mono-350", 10).capacity_kw, 3.5)
    check("PSH Accra, day 172",
          lambda: Solar("Mono-350", 10).estimate_peak_sun_hours(5.6, 172), 5.4)
    check("annual kWh",
          lambda: Solar("Mono-350", 10).calculate_energy(365), 4790.0)
    check("cost", lambda: Solar("Mono-350", 10).calculate_cost(3000))

    print("\n[3] Wind - 1 x Small-3000")
    check("swept area m2", lambda: Wind("Small-3000").swept_area(), 10.75)
    check("power at 3.5 m/s", lambda: Wind("Small-3000").power_output(3.5))
    check("power at 7.0 m/s (8x more)",
          lambda: Wind("Small-3000").power_output(7.0))
    check("power at 30 m/s (cut-out)",
          lambda: Wind("Small-3000").power_output(30.0), 0.0)
    check("annual kWh", lambda: Wind("Small-3000").calculate_energy(365))

    print("\n[4] Biomass - BioGas-5, 50 kg/day")
    check("kWh from 50 kg",
          lambda: Biomass("BioGas-5", 50).energy_from_feedstock(50), 60.0)
    check("annual kWh", lambda: Biomass("BioGas-5", 50).calculate_energy(365))

    print("\n[5] Hydro - 5 m head, 0.1 m3/s")
    check("hydraulic power kW",
          lambda: Hydropower("Pico-5", 5.0, 0.1).hydraulic_power(), 3.43)
    check("annual kWh",
          lambda: Hydropower("Pico-5", 5.0, 0.1).calculate_energy(365))

    print("\n[6] Polymorphism - same call, five behaviours")
    print("    (this loop is the proof for your report)")
    for key in SOURCE_REGISTRY:
        try:
            src = create_source(key)
            kwh = src.calculate_energy(365, {"demand_kwh": 3000})
            print("    " + key.ljust(10) + str(round(kwh, 1)).rjust(10) +
                  " kWh/yr   " + str(src))
        except NotImplementedError:
            print("    " + key.ljust(10) + "not yet implemented")
        except Exception as e:
            print("    " + key.ljust(10) + "ERROR: " + type(e).__name__)

    print("\n[7] Registry - unknown key SHOULD raise ValueError")
    try:
        create_source("nuclear")
        print("  [PROBLEM] no error raised")
    except ValueError as e:
        print("  [OK] ValueError: " + e.__str__())
    except NotImplementedError:
        print("  create_source not yet implemented")

    print("\n" + "=" * 62)
