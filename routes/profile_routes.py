"""routes/profile_routes.py - User profile and password management."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.auth_routes import login_required
from services.auth_service import AuthService

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    user = AuthService.get_user(session["user_id"])

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        AuthService.update_profile(session["user_id"], full_name, email)
        session["full_name"] = full_name
        flash("Profile updated.", "success")
        return redirect(url_for("profile.index"))

    return render_template("profile/index.html", user=user, active_page="profile")


@profile_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    old_password = request.form.get("old_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if new_password != confirm_password:
        flash("New password and confirmation do not match.", "error")
        return redirect(url_for("profile.index"))

    success, message = AuthService.change_password(session["user_id"], old_password, new_password)
    flash(message, "success" if success else "error")
    return redirect(url_for("profile.index"))
