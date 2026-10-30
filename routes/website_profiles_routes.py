"""routes/website_profiles_routes.py - Module 12: Website Profiles."""

from __future__ import annotations

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for

from database.db_manager import execute, fetch_all, fetch_one
from routes.auth_routes import login_required

website_profiles_bp = Blueprint("website_profiles", __name__, url_prefix="/website-profiles")

ICON_CHOICES = ["fa-globe", "fa-cart-shopping", "fa-building", "fa-vial", "fa-store",
                "fa-building-columns", "fa-user-shield", "fa-server"]


@website_profiles_bp.route("/")
@login_required
def index():
    rows = fetch_all("SELECT * FROM website_profiles ORDER BY is_builtin DESC, name ASC")
    profiles = []
    for r in rows:
        p = dict(r)
        try:
            p["config"] = json.loads(p["config_json"] or "{}")
        except (json.JSONDecodeError, TypeError):
            p["config"] = {}
        # count test cases attached to this profile for a useful stat
        count_row = fetch_one("SELECT COUNT(*) c FROM test_cases WHERE website_profile = ?", (p["name"],))
        p["test_case_count"] = count_row["c"] if count_row else 0
        profiles.append(p)

    return render_template(
        "website_profiles/index.html", profiles=profiles, icon_choices=ICON_CHOICES, active_page="website_profiles"
    )


@website_profiles_bp.route("/create", methods=["POST"])
@login_required
def create():
    name = request.form.get("name", "").strip()
    base_url = request.form.get("base_url", "").strip()
    description = request.form.get("description", "").strip()
    icon = request.form.get("icon", "fa-globe")
    config_raw = request.form.get("config_json", "").strip() or "{}"

    if not name or not base_url:
        flash("Name and Base URL are required.", "error")
        return redirect(url_for("website_profiles.index"))

    existing = fetch_one("SELECT id FROM website_profiles WHERE name = ?", (name,))
    if existing:
        flash(f"A profile named '{name}' already exists.", "error")
        return redirect(url_for("website_profiles.index"))

    try:
        parsed_config = json.loads(config_raw)
    except json.JSONDecodeError as exc:
        flash(f"Config JSON is invalid: {exc}", "error")
        return redirect(url_for("website_profiles.index"))

    execute(
        """INSERT INTO website_profiles (name, base_url, description, icon, config_json, is_builtin)
           VALUES (?, ?, ?, ?, ?, 0)""",
        (name, base_url, description, icon, json.dumps(parsed_config)),
    )
    flash(f"Website profile '{name}' created.", "success")
    return redirect(url_for("website_profiles.index"))


@website_profiles_bp.route("/<int:profile_id>/delete", methods=["POST"])
@login_required
def delete(profile_id: int):
    profile = fetch_one("SELECT * FROM website_profiles WHERE id = ?", (profile_id,))
    if not profile:
        flash("Profile not found.", "error")
    elif profile["is_builtin"]:
        flash("Built-in profiles can't be deleted.", "error")
    else:
        execute("DELETE FROM website_profiles WHERE id = ?", (profile_id,))
        flash(f"Deleted '{profile['name']}'.", "info")
    return redirect(url_for("website_profiles.index"))
