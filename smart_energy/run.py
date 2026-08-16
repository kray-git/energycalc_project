"""
========================================================================
  SMART ENERGY SOURCE COMPARISON SYSTEM
  run.py  -  Application Entry Point
========================================================================
  Status: FULLY WRITTEN - nothing to implement here.

  START THE APP
      cd smart_energy
      pip install -r requirements.txt
      python3 run.py

  then open  http://127.0.0.1:5000

  WHY THIS FILE IS SO SHORT
    An entry point should do one thing: assemble the app and start it.
    Business logic here is logic that can never be imported or tested
    by anything else. Keep it thin.
========================================================================
"""

from flask import Flask

from app.config import DEBUG, HOST, PORT
from app.routes.api import api


def create_app():
    """
    Build and configure the Flask application.

    Returns:
        Flask: the configured app

    THIS PATTERN IS CALLED AN "APPLICATION FACTORY"
        Building the app inside a function rather than at module level
        means tests can create a fresh instance with different settings,
        and nothing happens merely because someone imported the file.
        It is the standard Flask structure - worth naming in your report.
    """
    app = Flask(
        __name__,
        template_folder="app/templates",
        static_folder="app/static",
    )

    # JSON keys stay in the order we built them, rather than being
    # alphabetised. Makes responses far easier to read while debugging.
    app.json.sort_keys = False

    app.register_blueprint(api)
    return app


if __name__ == "__main__":
    application = create_app()

    print("=" * 60)
    print("  SMART ENERGY SOURCE COMPARISON SYSTEM")
    print("=" * 60)
    print("  Running at:  http://" + str(HOST) + ":" + str(PORT))
    print("  Debug mode:  " + str(DEBUG))
    print()
    print("  Endpoints:")
    print("    GET  /                  main page")
    print("    GET  /api/health        liveness check")
    print("    GET  /api/appliances    appliance catalogue")
    print("    GET  /api/sources       available energy sources")
    print("    POST /api/compare       run a comparison")
    print("    POST /api/location      resolve a location")
    print()
    print("  Stop with Ctrl+C")
    print("=" * 60)

    application.run(debug=DEBUG, host=HOST, port=PORT)
