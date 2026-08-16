"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  app/routes/api.py  -  Flask Routes
========================================================================
  Owner:  ____________________
  Build order: CAN START IMMEDIATELY. This is the one module that does
               NOT have to wait for the others.

  WHY YOU CAN START HERE ON DAY ONE
    Routes only care about the SHAPE of the classes - what you call and
    what comes back - not whether the maths inside works. Write the
    routes against the stubs, return fake data at first, and swap in
    the real calls as each module lands. Whoever owns this file should
    not be sitting idle waiting for the calculators.

  *** THIS FILE IS YOUR "GUI, PREFERABLY HTML" REQUIREMENT ***
    Flask serves an HTML page; the page talks to these JSON endpoints.
    That is a web GUI, which satisfies the rubric more strongly than
    the console interface the requirement would also accept.

  THE ROUTES
    GET  /                  the app page itself
    GET  /api/appliances    catalogue for the dropdown  (CSV -> JSON)
    GET  /api/sources       the five selectable sources
    POST /api/compare       THE MAIN ONE - run a comparison
    POST /api/location      resolve a place name or coordinates
    GET  /api/health        is the server alive

  RUBRIC COVERAGE
    [x] GUI (HTML)  [x] Library import (Flask)  [x] Files (via loader)
    [x] Functions   [x] Conditionals   [x] Collections

  RUN
      cd smart_energy
      python3 run.py
      then open http://127.0.0.1:5000
========================================================================
"""

from flask import Blueprint, jsonify, request, render_template

from app.data.data_loader import load_appliances
from app.models.appliance import Appliance
from app.models.energy_profile import EnergyProfile
from app.models.energy_source import SOURCE_REGISTRY
from app.calculators.comparison_engine import ComparisonEngine
from app.recommendations.recommendation_engine import RecommendationEngine

# A Blueprint is a group of routes registered onto the app later. It
# keeps run.py tiny and means routes can be split across several files
# if this one grows.
api = Blueprint("api", __name__)


# ======================================================================
#  PAGE
# ======================================================================

@api.route("/")
def index():
    """
    Serve the main page.

    HINT
        return render_template("index.html")

    Flask looks in app/templates/ automatically. Put the frontend HTML
    there. Static CSS/JS goes in app/static/ and is referenced as
        {{ url_for('static', filename='style.css') }}
    """
    # [IMPLEMENT ME]  (1 line)
    raise NotImplementedError("index")


# ======================================================================
#  GET ENDPOINTS
# ======================================================================

@api.route("/api/health")
def health():
    """
    Liveness check.

    Returns:
        JSON: {"status": "ok", "sources": [...]}

    WHY BOTHER
        When the frontend will not load, this tells you in one second
        whether the server is down or your JavaScript is wrong. Two
        minutes to write, saves an hour during integration week.
    """
    # [IMPLEMENT ME]  (~5 lines)
    raise NotImplementedError("health")


@api.route("/api/appliances")
def get_appliances():
    """
    The appliance catalogue as JSON.

    Returns:
        JSON: [{"name", "category", "default_watts",
                "typical_hours_per_day"}, ...]

    *** THIS IS THE CSV -> FRONTEND BRIDGE ***
        The dropdown must be built from THIS, not from a hardcoded
        <option> list in the HTML. Adding a row to appliances.csv should
        make a new appliance appear with no code change anywhere.

    HINT
        return jsonify(load_appliances())

    ERROR HANDLING
        Wrap in try/except FileNotFoundError and return a 500 with a
        clear message. A missing data file is the single most likely
        deployment problem - usually because someone ran the server
        from the wrong directory.
    """
    # [IMPLEMENT ME]  (~7 lines)
    raise NotImplementedError("get_appliances")


@api.route("/api/sources")
def get_sources():
    """
    The five selectable sources, for both dropdowns.

    Returns:
        JSON: [{"key": "solar", "label": "Solar PV",
                "renewable": true}, ...]

    HINT
        Build from SOURCE_REGISTRY so this can never drift out of sync
        with the classes that actually exist. Hardcoding the list here
        guarantees that one day someone adds a sixth source and the UI
        silently does not show it.
    """
    # [IMPLEMENT ME]  (~12 lines)
    raise NotImplementedError("get_sources")


# ======================================================================
#  POST ENDPOINTS
# ======================================================================

@api.route("/api/compare", methods=["POST"])
def compare():
    """
    *** THE MAIN ENDPOINT. ***

    Expects JSON:
        {
          "input_method": "appliances" | "direct",
          "appliances": [                      (if appliance-based)
             {"name": "Refrigerator", "watts": 150,
              "quantity": 1, "hours": 24}, ...
          ],
          "direct_kwh": 300,                   (if direct)
          "direct_period": "monthly",
          "location": "Berekuso",
          "latitude": 5.7594,                  (optional)
          "longitude": -0.2196,                (optional)
          "source_a": "grid",
          "source_b": "solar",
          "period_days": 365,
          "priority": "balanced",
          "source_a_options": {},              (optional)
          "source_b_options": {"num_panels": 10}
        }

    Returns:
        JSON: ComparisonEngine.compare() output with the
              "recommendation" key filled in by RecommendationEngine.

    THE STEPS
        1. data = request.get_json()
           Guard against None - a request without the JSON content-type
           header gives you None, and .get() on None is a 500 error.
        2. VALIDATE (see the rules below) and return 400 on failure.
        3. Build the EnergyProfile from whichever input method.
        4. engine.compare(...) -> result
        5. RecommendationEngine(priority).recommend(result)
        6. Attach it and jsonify.

    VALIDATION RULES - return HTTP 400 with a clear message for each
        - missing source_a or source_b
        - source_a == source_b            "Pick two different sources"
        - a source key not in SOURCE_REGISTRY
        - appliance method with an empty appliance list
        - direct method with a missing or non-numeric direct_kwh
        - negative numbers anywhere

    STATUS CODES MATTER
        400 = the client sent something wrong (their fault, fixable)
        500 = the server broke (our fault)
        Returning 200 with an "error" field inside makes the frontend
        parse success responses to discover failure. Do not do that.

    NEVER LET A RAW EXCEPTION REACH THE USER
        In DEBUG mode Flask renders a full traceback in the browser -
        including source code. Fine locally, unacceptable in a demo.
        Catch broadly at the end, log the detail server-side, return a
        generic message.

    *** SECURITY NOTE - READ THIS ***
        Everything in the request came from outside. Never trust it:
        check types before arithmetic, check keys are in SOURCE_REGISTRY
        before lookup, and never pass user strings into eval(), exec(),
        or a file path. Using the registry dict rather than building a
        class name from user input is not just tidier - it is what
        stops someone constructing arbitrary objects through your API.
    """
    # [IMPLEMENT ME]  (~60 lines - the biggest route)
    raise NotImplementedError("compare")


@api.route("/api/location", methods=["POST"])
def resolve_location():
    """
    Resolve a place name or coordinate pair.

    Expects JSON:
        {"location": "Berekuso"}
        or {"latitude": 5.75, "longitude": -0.21}

    Returns:
        JSON: LocationService.resolve() output.

    WHY THE FRONTEND NEEDS THIS
        The browser's Geolocation API returns raw coordinates. Writing
        "5.759400, -0.219600" into the location box is not helpful to a
        user. Call this endpoint, get "Berekuso" back, show that.
    """
    # [IMPLEMENT ME]  (~18 lines)
    raise NotImplementedError("resolve_location")


# ======================================================================
#  ERROR HANDLERS
# ======================================================================

@api.app_errorhandler(404)
def not_found(error):
    """
    Return JSON for unknown routes, not Flask's HTML 404 page.

    A frontend calling response.json() on an HTML error page gets a
    confusing parse error instead of a useful message. Consistent JSON
    everywhere makes debugging far quicker.

    HINT
        return jsonify({"error": "Endpoint not found"}), 404
    """
    # [IMPLEMENT ME]  (~2 lines)
    raise NotImplementedError("not_found")


@api.app_errorhandler(500)
def server_error(error):
    """
    Generic JSON 500.

    Log the real error server-side; send the user something generic.
    Never echo an exception message to the client - they can contain
    file paths and internal details.
    """
    # [IMPLEMENT ME]  (~3 lines)
    raise NotImplementedError("server_error")


# ======================================================================
#  SELF-TEST
#  Uses Flask's test client, so no browser and no running server needed.
#  This is how you check routes work before the frontend exists.
# ======================================================================
if __name__ == "__main__":
    print("=" * 62)
    print("API ROUTES SELF-TEST")
    print("=" * 62)
    print("\nUses Flask's test client - no server, no browser needed.\n")
    print("EXPECT THIS AT FIRST: every line reporting")
    print("  'NotImplementedError: server_error'")
    print("That is misleading but correct. The route raises, Flask hands")
    print("the error to the 500 handler, and THAT is a stub too - so its")
    print("exception is the one you see, hiding the real one underneath.")
    print("Implement server_error() first and the true errors appear.\n")

    try:
        import logging
        from flask import Flask

        # Flask logs a full traceback for every unhandled exception.
        # While the routes are still stubs that means a screen of noise
        # per call, so we silence it here. This affects the SELF-TEST
        # ONLY - the real server keeps its logging.
        logging.getLogger("app.routes.api").setLevel(logging.CRITICAL)

        app = Flask(__name__,
                    template_folder="../templates",
                    static_folder="../static")
        app.logger.disabled = True
        app.register_blueprint(api)
        client = app.test_client()

        def hit(method, path, payload=None, expect=200):
            try:
                if method == "GET":
                    r = client.get(path)
                else:
                    r = client.post(path, json=payload)
                ok = "[OK]" if r.status_code == expect else \
                     "[expected " + str(expect) + "]"
                body = r.get_data(as_text=True)[:110]
                print("  " + (method + " " + path).ljust(24) +
                      str(r.status_code) + " " + ok)
                print("      " + body)
            except Exception as e:
                print("  " + (method + " " + path).ljust(24) +
                      "ERROR: " + type(e).__name__ + ": " + e.__str__()[:60])

        print("[1] GET endpoints")
        hit("GET", "/api/health")
        hit("GET", "/api/appliances")
        hit("GET", "/api/sources")

        print("\n[2] POST /api/compare - valid request")
        hit("POST", "/api/compare", {
            "input_method": "appliances",
            "appliances": [
                {"name": "Refrigerator", "watts": 150, "quantity": 1, "hours": 24},
                {"name": "Ceiling Fan", "watts": 75, "quantity": 3, "hours": 10},
            ],
            "location": "Berekuso",
            "source_a": "grid",
            "source_b": "solar",
            "period_days": 365,
            "priority": "balanced",
        })

        print("\n[3] POST /api/compare - direct input")
        hit("POST", "/api/compare", {
            "input_method": "direct",
            "direct_kwh": 300,
            "direct_period": "monthly",
            "location": "Accra",
            "source_a": "grid",
            "source_b": "wind",
        })

        print("\n[4] Validation - all of these SHOULD return 400")
        hit("POST", "/api/compare",
            {"source_a": "solar", "source_b": "solar"}, expect=400)
        hit("POST", "/api/compare",
            {"source_a": "solar"}, expect=400)
        hit("POST", "/api/compare",
            {"source_a": "solar", "source_b": "nuclear"}, expect=400)
        hit("POST", "/api/compare",
            {"input_method": "appliances", "appliances": [],
             "source_a": "grid", "source_b": "solar"}, expect=400)
        hit("POST", "/api/compare",
            {"input_method": "direct", "direct_kwh": -50,
             "source_a": "grid", "source_b": "solar"}, expect=400)

        print("\n[5] Location resolution")
        hit("POST", "/api/location", {"location": "Kumasi"})
        hit("POST", "/api/location", {"latitude": 5.7594, "longitude": -0.2196})

        print("\n[6] Unknown route -> JSON 404, not an HTML page")
        hit("GET", "/api/does-not-exist", expect=404)

    except ImportError:
        print("  Flask is not installed. Run:  pip install flask")
    except Exception as e:
        print("  Setup error:", type(e).__name__, e)

    print("\n" + "=" * 62)
