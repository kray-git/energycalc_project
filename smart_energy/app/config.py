"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/config.py  -  Central Configuration
========================================================================
  Owner:  ____________________  (whoever owns the Flask app)
  Status: FULLY WRITTEN - just edit values, no implementation needed.

  WHY EVERY SETTING LIVES IN ONE FILE
    A URL hardcoded in three modules gets changed in two of them. One
    file means one place to look and one place to break.

  *** API KEYS ARE EMPTY STRINGS ON PURPOSE ***
    The whole app runs without a single key. Only optional extras need
    one, and each has a documented fallback.

    NEVER commit a real key. If a key reaches GitHub - even in a commit
    you later delete - treat it as compromised and rotate it. Git keeps
    history; the deletion does not remove it.

    For real keys, use an environment variable instead:
        import os
        OPENCAGE_API_KEY = os.environ.get("OPENCAGE_API_KEY", "")
    then each teammate sets it locally and nothing sensitive is tracked.
========================================================================
"""

# ----------------------------------------------------------------------
#  API KEYS - leave as "" unless you deliberately add one
# ----------------------------------------------------------------------

# Open-Meteo needs NO key. This is here only for symmetry.
WEATHER_API_KEY = ""

# OpenCage geocoding - OPTIONAL. Without it, LocationService falls back
# to its built-in KNOWN_LOCATIONS table, which covers the major
# Ghanaian towns. Only needed for arbitrary place-name lookup.
OPENCAGE_API_KEY = ""

# NREL PVWatts - OPTIONAL. A more sophisticated solar model than ours.
# Without it, Solar uses its own trig-based estimate. If you add this,
# say so in the report; a validated model is a genuine strength.
PVWATTS_API_KEY = ""

# Electricity Maps - OPTIONAL. Live grid carbon intensity rather than
# our static emission factor. Without it we use emission_factors.csv.
ELECTRICITY_MAPS_API_KEY = ""


# ----------------------------------------------------------------------
#  API ENDPOINTS
# ----------------------------------------------------------------------

WEATHER_API_BASE = "https://api.open-meteo.com"
GEOCODE_API_BASE = "https://api.opencagedata.com/geocode/v1"
PVWATTS_API_BASE = "https://developer.nrel.gov/api/pvwatts/v8.json"


# ----------------------------------------------------------------------
#  NETWORK BEHAVIOUR
# ----------------------------------------------------------------------

# Seconds before an API call is abandoned. Keep this SHORT. A long
# timeout on a bad connection makes the app look frozen during a demo -
# far worse than falling back to an estimate quickly.
REQUEST_TIMEOUT = 8

# How many past days of weather to average. Longer smooths out an
# unusually cloudy week; too long stops reflecting the current season.
WEATHER_LOOKBACK_DAYS = 7


# ----------------------------------------------------------------------
#  FLASK
# ----------------------------------------------------------------------

DEBUG = True          # MUST be False for any public deployment - debug
                      # mode exposes an interactive console to anyone
                      # who can trigger an error
HOST = "127.0.0.1"    # use "0.0.0.0" to reach it from your phone on the
                      # same wifi, which is handy for demoing
PORT = 5000


# ----------------------------------------------------------------------
#  DEFAULTS AND ASSUMPTIONS
#  Every one of these is a modelling choice. If a marker asks "why 30
#  days a month?" or "why 8% escalation?", you need an answer. Keeping
#  them here, named and commented, makes them defensible instead of
#  looking like magic numbers scattered through the code.
# ----------------------------------------------------------------------

DEFAULT_LOCATION = "Accra"
DEFAULT_LATITUDE = 5.6037
DEFAULT_LONGITUDE = -0.1870

DAYS_PER_MONTH = 30
DAYS_PER_YEAR = 365

CURRENCY = "GHS"
CURRENCY_SYMBOL = "GHS "

# Annual tariff escalation used in payback calculations.
# VERIFY against historical PURC adjustments and cite your source.
TARIFF_ESCALATION_RATE = 0.08

# Assumed grid availability. VERIFY against published reliability data
# if you can find it.
GRID_RELIABILITY = 0.92
