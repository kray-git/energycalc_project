"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/services/weather_service.py  -  Open-Meteo Integration
========================================================================
  Owner:  ____________________
  Build order: STAGE 2 (can be built in parallel with the models)

  *** THIS FILE IS YOUR "FETCHES DATA FROM AN API" REQUIREMENT ***

  WHY OPEN-METEO
    No API key, no sign-up, no billing page, generous free tier for
    non-commercial use, and it publishes shortwave radiation and wind
    speed - exactly the two variables solar and wind need. NASA POWER
    and PVWatts are alternatives; PVWatts needs a key, which is why it
    is optional here.

    Docs: https://open-meteo.com/en/docs

  THE RULE THIS FILE MUST OBEY
    Every method either returns usable data or raises a clear
    ConnectionError. It NEVER returns None quietly, and it NEVER lets
    a raw requests exception escape to the caller. ComparisonEngine
    catches ConnectionError and falls back; it should not need to know
    what library you used.

  RUBRIC COVERAGE
    [x] API data fetching   [x] Library import (requests)
    [x] Conditionals   [x] Collections   [x] Loops   [x] Functions

  RUN THIS FILE'S SELF-TEST
      cd smart_energy
      python3 -m app.services.weather_service

    Needs internet. On a blocked network you should see clean
    ConnectionErrors - that IS the correct behaviour, not a failure.
========================================================================
"""

import requests

from app.config import WEATHER_API_BASE, REQUEST_TIMEOUT


class WeatherService:
    """Fetches solar irradiance and wind speed for a coordinate."""

    # Peak sun hours are derived from shortwave radiation. Under
    # standard test conditions 1 peak sun hour = 1000 W/m2 for an hour
    # = 1 kWh/m2. So PSH = daily radiation in kWh/m2. Open-Meteo returns
    # MJ/m2 or W/m2 depending on the variable you request - CHECK THE
    # UNITS IN THE RESPONSE before dividing. Getting this wrong by a
    # factor of 3.6 is the classic bug here.
    MJ_PER_KWH = 3.6

    def __init__(self, base_url=None, timeout=None):
        """
        HINT
            self.base_url = base_url or WEATHER_API_BASE
            self.timeout  = timeout or REQUEST_TIMEOUT
        """
        # [IMPLEMENT ME]  (~3 lines)
        raise NotImplementedError("WeatherService.__init__")

    def _get(self, endpoint, params):
        """
        One place where every HTTP call happens.

        Args:
            endpoint (str): path appended to base_url
            params (dict): query string parameters

        Returns:
            dict: the parsed JSON body

        Raises:
            ConnectionError: for ANY failure - no internet, timeout,
                non-200 status, unparseable JSON. One exception type
                out means callers write one except clause.

        WHY A PRIVATE HELPER
            Timeout handling, error wrapping and status checking are
            identical for every endpoint. Writing them once means a fix
            applies everywhere. The leading underscore is the Python
            convention for "internal - do not call from outside".

        HINT
            try:
                response = requests.get(url, params=params,
                                        timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                raise ConnectionError("Weather API timed out after Ns")
            except requests.exceptions.RequestException as e:
                raise ConnectionError("Weather API unreachable: " + str(e))
            except ValueError:
                raise ConnectionError("Weather API returned invalid JSON")

        ALWAYS PASS timeout. Without it, requests waits indefinitely and
        your Flask route hangs forever on a bad network - which in a
        live demo looks exactly like a crash.
        """
        # [IMPLEMENT ME]  (~14 lines)
        raise NotImplementedError("WeatherService._get")

    def get_solar_radiation(self, latitude, longitude, days=7):
        """
        Recent daily solar radiation, converted to peak sun hours.

        Args:
            latitude, longitude (float)
            days (int): how many past days to average

        Returns:
            dict: {"peak_sun_hours": float, "daily_values": list[float],
                   "days_sampled": int, "source": "open-meteo"}

        Raises:
            ConnectionError

        THE REQUEST
            endpoint: "/v1/forecast"
            params: {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "shortwave_radiation_sum",
                "past_days": days,
                "forecast_days": 1,
                "timezone": "auto",
            }

        THE RESPONSE SHAPE
            {"daily": {"time": [...],
                       "shortwave_radiation_sum": [18.2, 19.4, ...]}}

            Those values are MJ/m2/day. Convert:
                psh = mj_value / 3.6

        DEFENSIVE PARSING
            Do not assume the keys exist. A changed API, a rate limit
            or an error body will not have them. Use .get() with
            defaults and raise ConnectionError with a useful message if
            the expected structure is missing.

            Also filter out None entries before averaging - Open-Meteo
            returns null for days it has no data, and sum() on a list
            containing None raises TypeError.

        SANITY CHECK
            Anywhere in Ghana should give roughly 4.5-6.0 PSH. If you
            get 18, you skipped the /3.6. If you get 0.5, you divided
            twice.
        """
        # [IMPLEMENT ME]  (~22 lines)
        raise NotImplementedError("WeatherService.get_solar_radiation")

    def get_wind_speed(self, latitude, longitude, days=7):
        """
        Recent average wind speed.

        Returns:
            dict: {"wind_speed_ms": float, "max_wind_speed_ms": float,
                   "daily_values": list[float], "source": "open-meteo"}

        THE REQUEST
            "daily": "wind_speed_10m_max"

        *** THE HUB-HEIGHT PROBLEM - IMPORTANT FOR YOUR REPORT ***
            Open-Meteo reports wind at 10 m. Small turbines often sit
            at 12-20 m, where wind is faster. The standard correction
            is the wind profile power law:

                v2 = v1 * (h2 / h1) ** alpha

            with alpha about 0.14 over open terrain, higher over trees
            and buildings. Since power goes as v^3, skipping this
            correction understates output significantly.

            Implement it if you have time, or state the omission
            explicitly. Do not silently ignore it.

        ALSO NOTE
            Open-Meteo returns wind in km/h by default. Divide by 3.6
            for m/s, or add "wind_speed_unit": "ms" to the params.
            Check which you did - a turbine "seeing" 12 km/h as 12 m/s
            will look four times better than reality.
        """
        # [IMPLEMENT ME]  (~20 lines)
        raise NotImplementedError("WeatherService.get_wind_speed")

    def get_solar_and_wind(self, latitude, longitude, days=7):
        """
        Both variables in ONE request.

        Returns:
            dict: {"peak_sun_hours", "wind_speed_ms", "days_sampled",
                   "source"}

        WHY COMBINE
            Open-Meteo accepts several comma-separated daily variables
            per call. One request instead of two halves the latency and
            the rate-limit usage. This is the method ComparisonEngine
            should actually call.

            "daily": "shortwave_radiation_sum,wind_speed_10m_max"
        """
        # [IMPLEMENT ME]  (~25 lines)
        raise NotImplementedError("WeatherService.get_solar_and_wind")


# ======================================================================
#  SELF-TEST
# ======================================================================
if __name__ == "__main__":
    print("=" * 62)
    print("WEATHER SERVICE SELF-TEST")
    print("=" * 62)
    print("\nNeeds internet. A ConnectionError here means the network")
    print("is blocked, NOT that your code is wrong - that is the")
    print("designed fallback path.\n")

    LOCATIONS = [
        ("Berekuso", 5.7594, -0.2196),
        ("Accra", 5.6037, -0.1870),
        ("Tamale", 9.4008, -0.8393),
        ("Ada Foah (coastal - best wind)", 5.7833, 0.6333),
    ]

    try:
        service = WeatherService()
    except NotImplementedError:
        service = None
        print("  __init__ not yet implemented - nothing else can run")

    if service is not None:
        for name, lat, lon in LOCATIONS:
            print("\n[" + name + "]")
            for label, fn in [
                ("solar", lambda: service.get_solar_radiation(lat, lon)),
                ("wind", lambda: service.get_wind_speed(lat, lon)),
                ("combined", lambda: service.get_solar_and_wind(lat, lon)),
            ]:
                try:
                    print("  " + label.ljust(10) + str(fn()))
                except NotImplementedError:
                    print("  " + label.ljust(10) + "not yet implemented")
                except ConnectionError as e:
                    print("  " + label.ljust(10) + "[OK - handled] " + e.__str__()[:70])
                except Exception as e:
                    print("  " + label.ljust(10) + "[BUG] unwrapped " +
                          type(e).__name__ + " - wrap it as ConnectionError")

        print("\n[Bad coordinates - should fail cleanly, not crash]")
        try:
            print("  ", service.get_solar_and_wind(999, 999))
        except NotImplementedError:
            print("   not yet implemented")
        except ConnectionError as e:
            print("   [OK] ConnectionError: " + e.__str__()[:70])
        except Exception as e:
            print("   [CHECK] " + type(e).__name__ + ": " + e.__str__()[:70])

    print("\n" + "=" * 62)
