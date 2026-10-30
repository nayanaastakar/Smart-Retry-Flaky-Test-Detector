"""
routes/api_routes.py
=====================
REST API surface for the framework (Module 15). All routes return JSON.
Prefixed with /api/v1 by the blueprint registration in app.py.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from database.db_manager import fetch_all, fetch_one
from services import analytics_service
from core.flaky_detector import FlakyDetector

api_bp = Blueprint("api", __name__)


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "smart-retry-framework"})


@api_bp.route("/analytics/summary")
def analytics_summary():
    return jsonify(analytics_service.get_summary_metrics())


@api_bp.route("/analytics/status-distribution")
def status_distribution():
    return jsonify(analytics_service.get_status_distribution())


@api_bp.route("/analytics/execution-trend")
def execution_trend():
    days = request.args.get("days", default=14, type=int)
    return jsonify(analytics_service.get_execution_trend(days=days))


@api_bp.route("/analytics/retry-trend")
def retry_trend():
    days = request.args.get("days", default=14, type=int)
    return jsonify(analytics_service.get_retry_trend(days=days))


@api_bp.route("/history")
def history():
    limit = request.args.get("limit", default=50, type=int)
    rows = fetch_all(
        "SELECT * FROM executions ORDER BY id DESC LIMIT ?", (limit,)
    )
    return jsonify([dict(r) for r in rows])


@api_bp.route("/history/<int:execution_id>")
def history_detail(execution_id: int):
    row = fetch_one("SELECT * FROM executions WHERE id = ?", (execution_id,))
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))


@api_bp.route("/flaky-tests")
def flaky_tests():
    return jsonify(FlakyDetector.top_flaky_tests(limit=request.args.get("limit", default=20, type=int)))


@api_bp.route("/flaky-tests/evaluate", methods=["POST"])
def evaluate_flaky():
    detector = FlakyDetector()
    reports = detector.evaluate_all()
    return jsonify([r.__dict__ for r in reports])


@api_bp.route("/settings")
def get_settings():
    rows = fetch_all("SELECT key, value FROM settings")
    return jsonify({r["key"]: r["value"] for r in rows})


@api_bp.route("/reports")
def reports():
    rows = fetch_all("SELECT * FROM reports ORDER BY id DESC LIMIT 50")
    return jsonify([dict(r) for r in rows])
