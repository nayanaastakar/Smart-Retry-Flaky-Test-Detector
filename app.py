"""
app.py
======
Application entry point. Run with:

    python app.py                 # normal start
    python app.py --init-db       # (re)initialize schema + seed data, then start
    flask --app app run           # alternative launch via Flask CLI

The app factory pattern is used so tests can spin up isolated app instances.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import timedelta

from flask import Flask, render_template

from config import settings
from database.db_manager import init_db


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(settings.LOGS_DIR / "app.log"),
        ],
    )


def create_app() -> Flask:
    configure_logging()
    settings.ensure_directories()

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=settings.SESSION_LIFETIME_DAYS)
    app.config["JSON_SORT_KEYS"] = False

    # --- Blueprints ------------------------------------------------------
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.history_routes import history_bp
    from routes.settings_routes import settings_bp
    from routes.api_routes import api_bp
    from routes.profile_routes import profile_bp
    from routes.reports_routes import reports_bp
    from routes.run_routes import run_bp
    from routes.test_cases_routes import test_cases_bp
    from routes.website_profiles_routes import website_profiles_bp
    from routes.console_routes import console_bp
    from routes.ai_analysis_routes import ai_analysis_bp
    from routes.projects_routes import projects_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(profile_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(run_bp)
    app.register_blueprint(test_cases_bp)
    app.register_blueprint(website_profiles_bp)
    app.register_blueprint(console_bp)
    app.register_blueprint(ai_analysis_bp)
    app.register_blueprint(projects_bp)

    # --- Context processors ------------------------------------------------
    @app.context_processor
    def inject_globals():
        return {
            "company_name": settings.COMPANY_NAME,
            "app_name": settings.REPORT_LOGO_TEXT,
        }

    # --- Error handlers ------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        logging.getLogger("smart_retry.app").exception("Unhandled server error")
        return render_template("errors/500.html"), 500

    return app


app = create_app()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init-db", action="store_true", help="Initialize schema and seed default data")
    args = parser.parse_args()

    if args.init_db:
        from database.seed import run_all

        run_all()

    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
