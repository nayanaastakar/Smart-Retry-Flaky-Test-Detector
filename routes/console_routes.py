"""
routes/console_routes.py
==========================
Module 14: Real-Time Console.

True push-based streaming (WebSocket/SSE) is on the roadmap; for now this
delivers the same end-user experience -- an auto-scrolling, color-coded,
continuously-updating log -- via short-interval polling of real data
(retry_attempts + executions), which is simpler to run reliably behind
plain WSGI and works identically from the user's point of view.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from database.db_manager import fetch_all
from routes.auth_routes import login_required

console_bp = Blueprint("console", __name__, url_prefix="/console")


@console_bp.route("/")
@login_required
def index():
    return render_template("console/index.html", active_page="console")


@console_bp.route("/tail")
@login_required
def tail():
    """Return log lines with id > since_id, oldest first, for polling."""
    since_id = request.args.get("since_id", default=0, type=int)
    limit = request.args.get("limit", default=100, type=int)

    rows = fetch_all(
        """SELECT ra.id, ra.attempt_number, ra.status, ra.duration_ms, ra.error_message, ra.created_at,
                  e.test_name, e.module, e.browser
           FROM retry_attempts ra
           JOIN executions e ON e.id = ra.execution_id
           WHERE ra.id > ?
           ORDER BY ra.id ASC LIMIT ?""",
        (since_id, limit),
    )

    lines = []
    max_id = since_id
    for r in rows:
        max_id = max(max_id, r["id"])
        lines.append({
            "id": r["id"],
            "timestamp": r["created_at"],
            "test_name": r["test_name"],
            "module": r["module"],
            "browser": r["browser"],
            "attempt_number": r["attempt_number"],
            "status": r["status"],
            "duration_ms": r["duration_ms"],
            "error_message": r["error_message"],
        })

    return jsonify({"lines": lines, "last_id": max_id})
