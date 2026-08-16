"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/calculators/comparison_engine.py  -  The Orchestrator
========================================================================
  Owner:  ____________________
  Build order: STAGE 4 - BUILD THIS LAST.
               It depends on everything else. Starting here means
               debugging five unfinished modules at once.

  WHAT THIS CLASS IS
    The single entry point the Flask route calls. It takes a profile,
    two source keys and a location, and returns one dictionary
    containing the entire comparison.

  DESIGN NOTE - WHY THERE IS NO CalculationSession CLASS
    An earlier draft had a separate session object holding the inputs
    and calling the engine. With no user accounts and no persistence,
    that class stored the engine's own state and forwarded its own
    methods - pure indirection. It was merged in here. If you are ever
    asked to justify a design decision in your report, this is a good
    one: we removed a class because it earned nothing.

  *** THIS CLASS IS WHERE POLYMORPHISM PAYS OFF ***
    Read compare() when it is done and notice what is NOT there: no
    if source == "solar" branch anywhere. It calls calculate_energy()
    on two objects and the right physics runs. Point at this in your
    report.

  RUBRIC COVERAGE
    [x] OOP - polymorphism in action   [x] Collections (nested dicts)
    [x] Conditionals   [x] Loops   [x] Functions
    [x] APIs (via WeatherService)

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.calculators.comparison_engine
========================================================================
"""

from datetime import datetime

from app.models.energy_source import create_source
from app.calculators.energy_calculator import EnergyCalculator
from app.calculators.financial_calculator import FinancialCalculator
from app.calculators.carbon_calculator import CarbonCalculator
from app.services.weather_service import WeatherService
from app.services.location_service import LocationService
from app.services.tariff_service import TariffService


class ComparisonEngine:
    """Runs a full two-source comparison against an energy profile."""

    def __init__(self, weather_service=None, location_service=None,
                 tariff_service=None):
        """
        Args:
            weather_service, location_service, tariff_service:
                optional injected services. If None, construct the real
                ones.

        WHY ALLOW INJECTION AGAIN?
            Same reason as CarbonCalculator - a test can pass a fake
            weather service returning fixed values, so the test suite
            does not depend on the internet being up or on Open-Meteo
            returning the same numbers next week.

        ALSO CREATE
            self.energy_calc, self.financial_calc, self.carbon_calc
        """
        # [IMPLEMENT ME]  (~8 lines)
        raise NotImplementedError("ComparisonEngine.__init__")

    def build_context(self, location=None, latitude=None, longitude=None):
        """
        Gather the environmental data both sources may need.

        Args:
            location (str, optional): place name, e.g. "Berekuso"
            latitude, longitude (float, optional): used directly if given

        Returns:
            dict: {"latitude", "longitude", "location", "day_of_year",
                   "peak_sun_hours", "wind_speed_ms", "data_source"}

        *** THIS METHOD MUST NEVER RAISE ON NETWORK FAILURE ***
            The whole app has to work offline, on campus wifi, in a
            demo room with no internet. Wrap every external call in
            try/except and fall back to defaults.

        THE SEQUENCE
            1. Coordinates:
                 - lat/lon given? use them
                 - else location name? self.location_service.geocode()
                 - else default to Accra (5.6037, -0.1870)
            2. day_of_year = datetime.now().timetuple().tm_yday
            3. try: weather = self.weather_service.get_solar_and_wind(
                        lat, lon)
                    fill in peak_sun_hours and wind_speed_ms
                    data_source = "live"
               except (ConnectionError, TimeoutError, Exception):
                    leave them out of the dict entirely so each source
                    falls back to its own documented default
                    data_source = "estimated"

        WHY data_source MATTERS
            The frontend should tell the user whether they are seeing
            live weather or a seasonal estimate. Presenting a fallback
            as if it were measured data is a small dishonesty that
            undermines the whole tool.

        CAUTION ON BARE except
            Catching everything hides real bugs (a typo in an attribute
            name would look like a network failure). Catch the specific
            exceptions where you can, and if you do use a broad except,
            print the exception so it is visible in the console.
        """
        # [IMPLEMENT ME]  (~28 lines)
        raise NotImplementedError("ComparisonEngine.build_context")

    def compare(self, profile, source_a_key, source_b_key,
                location=None, days=365, priority="balanced",
                source_a_options=None, source_b_options=None):
        """
        THE MAIN METHOD. Run a full comparison.

        Args:
            profile (EnergyProfile): the user's demand
            source_a_key, source_b_key (str): "grid", "solar", "wind",
                "biomass", "hydro"
            location (str, optional)
            days (int): comparison period
            priority (str): "cost", "environment", "reliability" or
                "balanced" - passed to the recommendation engine
            source_a_options, source_b_options (dict, optional):
                constructor kwargs, e.g. {"num_panels": 12}

        Returns:
            dict:
                {
                  "meta": {"generated_at", "days", "location",
                           "data_source", "priority"},
                  "profile": profile.summary(),
                  "context": the context dict,
                  "sources": {
                      "a": {"info": ..., "energy": ..., "cost": ...,
                            "emissions": ...},
                      "b": {same shape}
                  },
                  "financial": compare_costs output,
                  "carbon": compare_emissions output,
                  "recommendation": None   <- filled by
                                              RecommendationEngine
                }

        Raises:
            ValueError: if source_a_key == source_b_key. Comparing a
                source with itself is meaningless; fail loudly and
                early rather than returning a table of identical rows.

        THE STEPS
            1. Validate the two keys differ (case-insensitively).
            2. context = self.build_context(location=location)
            3. Build both sources with create_source(key, **options).
               Grid needs the tariff service passed in - handle that
               case when constructing it.
            4. demand = profile.annual_demand scaled to `days`.
            5. For each source: energy balance, cost, emissions - via
               the three calculators. A LOOP over the two sources reads
               better than copy-pasting the block twice.
            6. Financial and carbon head-to-heads.
            7. Assemble and return the dict.

        KEEP THE RETURN SHAPE STABLE
            The frontend and the recommendation engine both read this
            dictionary by key. Changing a key name here silently breaks
            them. If you must change it, tell the team and grep for the
            old key first.
        """
        # [IMPLEMENT ME]  (~55 lines - the biggest method in the project)
        raise NotImplementedError("ComparisonEngine.compare")

    def compare_all_sources(self, profile, location=None, days=365):
        """
        Rank ALL FIVE sources against the profile at once.

        Returns:
            list[dict]: one summary per source, sorted best-first by
                lifetime cost.

        WHY THIS IS WORTH BUILDING
            The core UI is a two-source matchup, but a "show me
            everything" view makes a strong demo and costs little once
            compare() works. Treat it as a stretch goal - do not let it
            delay the required path.

        HINT
            Loop over SOURCE_REGISTRY keys, run each against the grid
            as baseline, collect the summaries, sort.
        """
        # [IMPLEMENT ME]  (~18 lines) - OPTIONAL, build after compare()
        raise NotImplementedError("ComparisonEngine.compare_all_sources")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":
    print("=" * 62)
    print("COMPARISON ENGINE SELF-TEST")
    print("=" * 62)
    print("\nThis is the LAST module to implement. Everything below")
    print("stays blocked until stages 1-3 are done. That is expected.\n")

    try:
        from app.models.appliance import Appliance
        from app.models.energy_profile import EnergyProfile

        engine = ComparisonEngine()

        profile = EnergyProfile("Berekuso")
        profile.add_appliance(Appliance("Refrigerator", 150, 1, 24))
        profile.add_appliance(Appliance("Ceiling Fan", 75, 3, 10))
        profile.add_appliance(Appliance("LED Bulb", 10, 8, 6))

        print("[1] Context building (may take a moment - network call)")
        ctx = engine.build_context(location="Berekuso")
        print("   ", ctx)
        print("    NOTE: data_source 'estimated' just means the weather")
        print("    API was unreachable. That is a correct fallback, not")
        print("    a failure.")

        print("\n[2] Grid vs Solar")
        result = engine.compare(profile, "grid", "solar",
                                location="Berekuso",
                                source_b_options={"panel_model": "Mono-350",
                                                  "num_panels": 10})
        print("    top-level keys:", list(result.keys()))
        print("    financial:", result.get("financial"))
        print("    carbon:", result.get("carbon"))

        print("\n[3] Every pairing that matters")
        for a, b in [("grid", "solar"), ("grid", "wind"),
                     ("grid", "biomass"), ("grid", "hydro"),
                     ("solar", "wind")]:
            try:
                r = engine.compare(profile, a, b, location="Berekuso")
                fin = r["financial"]
                print("    " + (a + " vs " + b).ljust(18) +
                      "cheaper over life: " + str(fin.get("cheaper_lifetime")))
            except NotImplementedError:
                print("    " + (a + " vs " + b).ljust(18) + "blocked")
            except Exception as e:
                print("    " + (a + " vs " + b).ljust(18) +
                      "ERROR: " + type(e).__name__ + ": " + e.__str__())

    except NotImplementedError as e:
        print("  BLOCKED: " + e.__str__())
        print("  Implement stages 1-3 first.")
    except Exception as e:
        print("  ERROR:", type(e).__name__, e)

    print("\n[4] Same-source guard - SHOULD raise ValueError")
    try:
        from app.models.energy_profile import EnergyProfile
        ComparisonEngine().compare(EnergyProfile(), "solar", "solar")
        print("  [PROBLEM] no error raised")
    except ValueError as e:
        print("  [OK] ValueError: " + e.__str__())
    except NotImplementedError:
        print("  not yet implemented")
    except Exception as e:
        print("  " + type(e).__name__ + ": " + e.__str__())

    print("\n" + "=" * 62)
