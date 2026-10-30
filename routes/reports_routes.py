"""routes/reports_routes.py - Report generation and downloads (Module 5)."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for

from config import settings
from routes.auth_routes import login_required
from database.db_manager import fetch_all
from services.report_service import ReportService

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@login_required
def index():
    reports = fetch_all("SELECT * FROM reports ORDER BY id DESC LIMIT 50")
    return render_template("reports/index.html", reports=[dict(r) for r in reports], active_page="reports")


@reports_bp.route("/generate", methods=["POST"])
@login_required
def generate():
    report_type = request.form.get("report_type", "html")
    run_id = request.form.get("run_id") or None
    limit = request.form.get("limit", type=int) or 200

    try:
        service = ReportService()
        result = service.generate(report_type=report_type, run_id=run_id, limit=limit)
        flash(f"{report_type.upper()} report generated ({result['summary']['total']} tests).", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Report generation failed: {exc}", "error")

    return redirect(url_for("reports.index"))


@reports_bp.route("/<int:report_id>/download")
@login_required
def download(report_id: int):
    from database.db_manager import fetch_one

    report = fetch_one("SELECT * FROM reports WHERE id = ?", (report_id,))
    if not report:
        flash("Report not found.", "error")
        return redirect(url_for("reports.index"))

    file_path = settings.BASE_DIR / report["file_path"]
    if not file_path.exists():
        flash("Report file is missing on disk.", "error")
        return redirect(url_for("reports.index"))

    return send_file(file_path, as_attachment=(report["report_type"] in ("csv", "json", "pdf")))
