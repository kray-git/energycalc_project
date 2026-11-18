from flask import Flask, send_from_directory

from app.routes.api import api_bp
import os


def create_app() -> Flask:
    application = Flask(__name__)
    application.register_blueprint(api_bp)
    return application


app = create_app()
frontend_DIR = os.path.join(os.path.dirname(__file__), "frontend")

@app.route("/")
def serve_frontend():
    return send_from_directory(frontend_DIR, "index.html")

if __name__ == "__main__":
    app.run()

