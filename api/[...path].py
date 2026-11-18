import os
import sys

# 1. Calculate project root properly and add it to sys.path BEFORE importing `app`
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from app.extensions import cache
from app.routes.api import api_bp

PUBLIC_DIR = os.path.join(ROOT_DIR, "public")


def create_app() -> Flask:
    application = Flask(__name__)

    # Initialize in-memory cache
    cache.init_app(application)

    # Vercel reverse proxy headers
    application.wsgi_app = ProxyFix(
        application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    application.register_blueprint(api_bp)

    @application.route("/")
    def serve_frontend():
        return send_from_directory(PUBLIC_DIR, "index.html")

    @application.route("/api/health")
    def health_check():
        return {"status": "ok"}, 200

    return application


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
