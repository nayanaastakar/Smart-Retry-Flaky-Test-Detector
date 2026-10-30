"""routes/dashboard_routes.py - Main dashboard page."""

from __future__ import annotations

from flask import Blueprint, render_template

from routes.auth_routes import login_required
from services import analytics_service
from core.flaky_detector import FlakyDetector

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    metrics = analytics_service.get_summary_metrics()
    status_distribution = analytics_service.get_status_distribution()
    execution_trend = analytics_service.get_execution_trend(days=14)
    retry_trend = analytics_service.get_retry_trend(days=14)
    module_breakdown = analytics_service.get_module_breakdown()
    top_failed = analytics_service.get_top_failed_tests(limit=6)
    recent_executions = analytics_service.get_recent_executions(limit=10)
    recent_reports = analytics_service.get_recent_reports(limit=5)
    top_flaky = FlakyDetector.top_flaky_tests(limit=6)

    return render_template(
        "dashboard/index.html",
        metrics=metrics,
        status_distribution=status_distribution,
        execution_trend=execution_trend,
        retry_trend=retry_trend,
        module_breakdown=module_breakdown,
        top_failed=top_failed,
        recent_executions=recent_executions,
        recent_reports=recent_reports,
        top_flaky=top_flaky,
        active_page="dashboard",
    )
