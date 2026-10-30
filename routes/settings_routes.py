"""routes/settings_routes.py - Persistent application settings."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from routes.auth_routes import login_required
from database.db_manager import execute, fetch_all

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

EDITABLE_KEYS = [
    "browser", "retry_count", "retry_delay", "headless",
    "theme", "ai_enabled", "execution_timeout",
]


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        # headless / ai_enabled are booleans mirrored into hidden inputs by
        # inline JS on the toggle switches, so they always arrive as an
        # explicit "true"/"false" string rather than being absent when unchecked.
        for key in EDITABLE_KEYS:
            value = request.form.get(key)
            if value is not None:
                execute(
                    """INSERT INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
                       ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP""",
                    (key, value),
                )
        flash("Settings saved successfully.", "success")
        return redirect(url_for("settings.index"))

    rows = fetch_all("SELECT key, value FROM settings")
    current = {r["key"]: r["value"] for r in rows}
    return render_template("settings/index.html", settings=current, active_page="settings")
