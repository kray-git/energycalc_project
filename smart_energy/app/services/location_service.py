"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/services/location_service.py  -  Place Names <-> Coordinates
========================================================================
  Owner:  ____________________
  Build order: STAGE 2

  WHAT THIS SOLVES
    The user types "Berekuso" or lets the browser share their GPS
    position. WeatherService needs decimal coordinates. This class
    converts between the two, in both directions.

      geocode()          "Berekuso"      -> (5.7594, -0.2196)
      reverse_geocode()  (5.75, -0.21)   -> "Berekuso, Eastern Region"

  THE API-KEY SITUATION
    OPENCAGE_API_KEY in config.py is deliberately an empty string. The
    app MUST work without it - that is why KNOWN_LOCATIONS below
    exists. Only add a key if you want arbitrary place-name lookup
    beyond the built-in table.

    NEVER commit a real key to GitHub. If one ever lands in a commit,
    treat it as public and rotate it - deleting the line in a later
    commit does not remove it from history.

  RUBRIC COVERAGE
    [x] APIs   [x] Collections (dict lookup table, tuples)
    [x] Conditionals   [x] Loops   [x] Functions

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.services.location_service
========================================================================
"""

import requests

from app.config import OPENCAGE_API_KEY, GEOCODE_API_BASE, REQUEST_TIMEOUT


class LocationService:
    """Resolves Ghanaian place names and coordinates."""

    # Offline fallback table. Covers the places most likely to be typed
    # in a demo, so the app never depends on a key or a network.
    # ADD YOUR OWN TOWNS - if a teammate is demoing from home, put
    # their town in here so the demo works on their machine.
    KNOWN_LOCATIONS = {
        "accra": (5.6037, -0.1870),
        "berekuso": (5.7594, -0.2196),
        "kumasi": (6.6885, -1.6244),
        "tamale": (9.4008, -0.8393),
        "takoradi": (4.8845, -1.7554),
        "cape coast": (5.1053, -1.2466),
        "ho": (6.6008, 0.4713),
        "sunyani": (7.3390, -2.3268),
        "koforidua": (6.0940, -0.2591),
        "bolgatanga": (10.7856, -0.8514),
        "wa": (10.0601, -2.5099),
        "tema": (5.6698, -0.0166),
        "ada foah": (5.7833, 0.6333),
        "anloga": (5.7947, 0.8975),
        "akosombo": (6.2969, 0.0592),
    }

    DEFAULT_COORDINATES = (5.6037, -0.1870)   # Accra
    GHANA_BOUNDS = {"lat_min": 4.5, "lat_max": 11.2,
                    "lon_min": -3.3, "lon_max": 1.3}

    def __init__(self, api_key=None):
        """
        HINT
            self.api_key = api_key if api_key is not None else OPENCAGE_API_KEY
            self.has_api_key = bool(self.api_key)   # "" is falsy

        Storing has_api_key once means the rest of the class asks a
        boolean rather than re-testing a string everywhere.
        """
        # [IMPLEMENT ME]  (~3 lines)
        raise NotImplementedError("LocationService.__init__")

    def geocode(self, place_name):
        """
        Place name -> coordinates.

        Args:
            place_name (str)

        Returns:
            tuple: (latitude, longitude)

        Raises:
            ValueError: if the place cannot be resolved by any method.

        *** RETURNS A TUPLE - one of your tuple demonstrations ***
            A coordinate pair is fixed in length and order and should
            never be mutated. That is precisely what tuples are for.

        THE LOOKUP ORDER
            1. KNOWN_LOCATIONS, lowercased and stripped. Free, instant,
               works offline.
            2. Partial match - loop the table and check whether the key
               is contained in the input or vice versa, so "Accra,
               Ghana" still resolves. Watch out: "wa" is a substring of
               an enormous number of words. Guard short keys, e.g. only
               allow partial matching for keys longer than 3 characters.
            3. If self.has_api_key: call the geocoding API.
            4. Otherwise raise ValueError listing a few known places, so
               the user gets a usable next step rather than a dead end.
        """
        # [IMPLEMENT ME]  (~20 lines)
        raise NotImplementedError("LocationService.geocode")

    def reverse_geocode(self, latitude, longitude):
        """
        Coordinates -> nearest known place name.

        Returns:
            str: a place name, or a formatted coordinate string if
                 nothing is close.

        WHY THIS EXISTS
            The browser's Geolocation API gives raw lat/lng. Showing
            "5.7594, -0.2196" back to a user is unhelpful; showing
            "Berekuso" is not. The frontend currently overwrites the
            location box with raw coordinates - this method is the fix.

        APPROACH WITHOUT AN API KEY - nearest neighbour:
            Loop KNOWN_LOCATIONS, compute the distance to each, keep
            the smallest. Straight-line Pythagoras on lat/lon degrees is
            good enough here:

                d = ((lat1-lat2)**2 + (lon1-lon2)**2) ** 0.5

            (Strictly this is wrong - a degree of longitude is shorter
            than a degree of latitude away from the equator, and the
            proper tool is the haversine formula. Near Ghana's latitude
            the error is small. Mention the simplification.)

            If the nearest match is more than ~0.5 degrees away, return
            a formatted coordinate string instead of a misleading name.
        """
        # [IMPLEMENT ME]  (~20 lines)
        raise NotImplementedError("LocationService.reverse_geocode")

    def validate_coordinates(self, latitude, longitude):
        """
        Check a coordinate pair is usable.

        Returns:
            dict: {"valid": bool, "in_ghana": bool, "message": str}

        WHY NOT JUST RETURN A BOOL
            "Valid but outside Ghana" is a real, useful state - the app
            can still run a comparison for Lagos, it just cannot use
            Ghanaian tariffs. A bool cannot express that; a dict can.

        CHECKS
            - latitude between -90 and 90, longitude between -180 and 180
            - is it inside GHANA_BOUNDS?
            - are they numbers at all? A frontend can send "" or None.
              Guard with isinstance before comparing, or a TypeError
              surfaces as a 500 error in the route.
        """
        # [IMPLEMENT ME]  (~16 lines)
        raise NotImplementedError("LocationService.validate_coordinates")

    def resolve(self, place_name=None, latitude=None, longitude=None):
        """
        One convenient entry point for whatever the frontend sent.

        Returns:
            dict: {"latitude", "longitude", "location", "method",
                   "in_ghana"}
                where method is "coordinates", "geocoded" or "default".

        PRECEDENCE
            Explicit coordinates beat a typed name (GPS is more precise
            than "Accra", which covers 200 km2). Name beats nothing.
            Nothing falls back to DEFAULT_COORDINATES with method
            "default" - and the UI should say so rather than silently
            reporting on the wrong city.

        This is the method ComparisonEngine.build_context() calls.
        """
        # [IMPLEMENT ME]  (~22 lines)
        raise NotImplementedError("LocationService.resolve")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":
    print("=" * 62)
    print("LOCATION SERVICE SELF-TEST")
    print("=" * 62)

    def check(label, fn):
        try:
            print("  " + label.ljust(34) + str(fn()))
        except NotImplementedError:
            print("  " + label.ljust(34) + "not yet implemented")
        except ValueError as e:
            print("  " + label.ljust(34) + "ValueError: " + e.__str__()[:40])
        except Exception as e:
            print("  " + label.ljust(34) + "ERROR: " + type(e).__name__ + ": " + e.__str__()[:40])

    try:
        service = LocationService()
        print("\n  API key configured:", bool(OPENCAGE_API_KEY),
              "(empty string is expected and fine)")
    except NotImplementedError:
        service = None
        print("\n  __init__ not yet implemented")

    if service is not None:
        print("\n[1] Geocoding known places")
        for place in ["Berekuso", "accra", "ACCRA", "  Kumasi  ",
                      "Accra, Ghana", "Ada Foah"]:
            check(repr(place), lambda p=place: service.geocode(p))

        print("\n[2] Unknown place - should raise ValueError")
        check("'Atlantis'", lambda: service.geocode("Atlantis"))

        print("\n[3] Reverse geocoding")
        for lat, lon, note in [
            (5.7594, -0.2196, "exactly Berekuso"),
            (5.7600, -0.2200, "very near Berekuso"),
            (6.6885, -1.6244, "Kumasi"),
            (51.5074, -0.1278, "London - far from everything known"),
        ]:
            check(note, lambda a=lat, b=lon: service.reverse_geocode(a, b))

        print("\n[4] Coordinate validation")
        for lat, lon, note in [
            (5.6037, -0.1870, "Accra - valid, in Ghana"),
            (51.5074, -0.1278, "London - valid, not in Ghana"),
            (999, 999, "out of range"),
            (None, None, "None values from an empty form"),
            ("abc", "def", "strings from a text input"),
        ]:
            check(note, lambda a=lat, b=lon: service.validate_coordinates(a, b))

        print("\n[5] resolve() precedence")
        check("coords only", lambda: service.resolve(latitude=5.75, longitude=-0.21))
        check("name only", lambda: service.resolve(place_name="Kumasi"))
        check("both - coords should win",
              lambda: service.resolve(place_name="Kumasi",
                                      latitude=5.6037, longitude=-0.1870))
        check("neither - default", lambda: service.resolve())

    print("\n" + "=" * 62)
