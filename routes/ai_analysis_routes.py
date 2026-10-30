"""routes/ai_analysis_routes.py - Module 6 browsing UI: list/filter AI analyses, bulk-run."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from database.db_manager import fetch_all
from routes.auth_routes import login_required

ai_analysis_bp = Blueprint("ai_analysis", __name__, url_prefix="/ai-analysis")

MAX_BULK_RUN = 15  # cap per click so a single request can't run indefinitely


@ai_analysis_bp.route("/")
@login_required
def index():
    severity_filter = request.args.get("severity", "")
    where = []
    params: list = []
    if severity_filter:
        where.append("a.severity = ?")
        params.append(severity_filter)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    rows = fetch_all(
        f"""SELECT a.*, e.test_name, e.module, e.status AS execution_status
            FROM ai_analyses a JOIN executions e ON e.id = a.execution_id
            {where_sql} ORDER BY a.id DESC LIMIT 100""",
        tuple(params),
    )

    pending_row = fetch_all(
        """SELECT COUNT(*) c FROM executions
           WHERE status IN ('FAIL','FLAKY') AND ai_analysis_id IS NULL"""
    )
    pending_count = pending_row[0]["c"] if pending_row else 0

    severity_counts = {
        r["severity"]: r["c"]
        for r in fetch_all("SELECT severity, COUNT(*) c FROM ai_analyses GROUP BY severity")
    }

    return render_template(
        "ai_analysis/index.html",
        analyses=[dict(r) for r in rows],
        severity_filter=severity_filter,
        pending_count=pending_count,
        severity_counts=severity_counts,
        max_bulk_run=MAX_BULK_RUN,
        active_page="ai_analysis",
    )


@ai_analysis_bp.route("/bulk-run", methods=["POST"])
@login_required
def bulk_run():
    from ai.analyzer import AIAnalysisError, AIFailureAnalyzer

    targets = fetch_all(
        """SELECT id FROM executions
           WHERE status IN ('FAIL','FLAKY') AND ai_analysis_id IS NULL
           ORDER BY id DESC LIMIT ?""",
        (MAX_BULK_RUN,),
    )

    if not targets:
        flash("No unanalyzed FAIL/FLAKY executions to process.", "info")
        return redirect(url_for("ai_analysis.index"))

    analyzer = AIFailureAnalyzer()
    succeeded, failed = 0, 0
    for row in targets:
        try:
            analyzer.analyze_execution_with_fallback(row["id"])
            succeeded += 1
        except AIAnalysisError:
            failed += 1

    flash(f"Bulk analysis complete: {succeeded} analyzed, {failed} skipped.", "success" if succeeded else "error")
    return redirect(url_for("ai_analysis.index"))
