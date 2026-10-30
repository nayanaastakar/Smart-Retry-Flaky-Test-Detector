"""routes/history_routes.py - Execution history: search, filter, sort, delete, export."""

from __future__ import annotations

import csv
import io

from flask import Blueprint, Response, render_template, request, redirect, url_for, flash

from routes.auth_routes import login_required
from database.db_manager import execute, fetch_all

history_bp = Blueprint("history", __name__, url_prefix="/history")

SORT_COLUMNS = {
    "date": "started_at",
    "name": "test_name",
    "status": "status",
    "duration": "duration_ms",
    "attempts": "attempt_count",
}


@history_bp.route("/")
@login_required
def index():
    query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")
    module_filter = request.args.get("module", "")
    sort_key = request.args.get("sort", "date")
    direction = request.args.get("dir", "desc").upper()
    direction = "DESC" if direction not in ("ASC", "DESC") else direction
    sort_col = SORT_COLUMNS.get(sort_key, "started_at")

    where = []
    params: list = []
    if query:
        where.append("test_name LIKE ?")
        params.append(f"%{query}%")
    if status_filter:
        where.append("status = ?")
        params.append(status_filter)
    if module_filter:
        where.append("module = ?")
        params.append(module_filter)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    rows = fetch_all(
        f"""SELECT id, run_id, test_name, module, status, attempt_count, retry_success,
                   duration_ms, browser, os_name, started_at
            FROM executions {where_sql}
            ORDER BY {sort_col} {direction} LIMIT 300""",
        tuple(params),
    )

    modules = [r["module"] for r in fetch_all("SELECT DISTINCT module FROM executions WHERE module IS NOT NULL")]

    return render_template(
        "history/index.html",
        executions=[dict(r) for r in rows],
        query=query,
        status_filter=status_filter,
        module_filter=module_filter,
        modules=modules,
        sort_key=sort_key,
        direction=direction.lower(),
        active_page="history",
    )


@history_bp.route("/<int:execution_id>")
@login_required
def detail(execution_id: int):
    from database.db_manager import fetch_one

    execution = fetch_one("SELECT * FROM executions WHERE id = ?", (execution_id,))
    if not execution:
        flash("Execution not found.", "error")
        return redirect(url_for("history.index"))

    attempts = fetch_all(
        "SELECT * FROM retry_attempts WHERE execution_id = ? ORDER BY attempt_number ASC", (execution_id,)
    )
    ai_analysis = None
    if execution["ai_analysis_id"]:
        ai_analysis = fetch_one("SELECT * FROM ai_analyses WHERE id = ?", (execution["ai_analysis_id"],))
    else:
        ai_analysis = fetch_one("SELECT * FROM ai_analyses WHERE execution_id = ?", (execution_id,))

    return render_template(
        "history/detail.html",
        execution=dict(execution),
        attempts=[dict(a) for a in attempts],
        ai_analysis=dict(ai_analysis) if ai_analysis else None,
        active_page="history",
    )


@history_bp.route("/<int:execution_id>/screenshot")
@login_required
def screenshot(execution_id: int):
    """Serve the stored screenshot for an execution. The path is resolved and
    must stay inside the project's screenshots directory (blocks path traversal)."""
    from flask import abort, send_file

    from config import settings as cfg
    from database.db_manager import fetch_one

    row = fetch_one("SELECT screenshot_path FROM executions WHERE id = ?", (execution_id,))
    if not row or not row["screenshot_path"]:
        abort(404)
    full = (cfg.BASE_DIR / row["screenshot_path"]).resolve()
    allowed_root = cfg.SCREENSHOTS_DIR.resolve()
    if allowed_root not in full.parents or not full.is_file():
        abort(404)
    return send_file(full, mimetype="image/png")


@history_bp.route("/<int:execution_id>/analyze", methods=["POST"])
@login_required
def analyze(execution_id: int):
    from ai.analyzer import AIFailureAnalyzer, AIAnalysisError

    try:
        analyzer = AIFailureAnalyzer()
        result = analyzer.analyze_execution_with_fallback(execution_id)
        label = "AI" if result.get("model_name") not in (None, "heuristic-fallback") else "Heuristic (Ollama unreachable)"
        flash(f"{label} analysis complete — severity {result['severity']}.", "success")
    except AIAnalysisError as exc:
        flash(f"Analysis failed: {exc}", "error")

    return redirect(url_for("history.detail", execution_id=execution_id))


@history_bp.route("/<int:execution_id>/delete", methods=["POST"])
@login_required
def delete(execution_id: int):
    execute("DELETE FROM executions WHERE id = ?", (execution_id,))
    flash("Execution deleted.", "info")
    return redirect(url_for("history.index"))


@history_bp.route("/export.csv")
@login_required
def export_csv():
    rows = fetch_all(
        """SELECT run_id, test_name, module, status, attempt_count, retry_success,
                  duration_ms, browser, os_name, started_at
           FROM executions ORDER BY id DESC"""
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Run ID", "Test Name", "Module", "Status", "Attempts", "Retry Saved",
                      "Duration (ms)", "Browser", "OS", "Started At"])
    for r in rows:
        writer.writerow([r["run_id"], r["test_name"], r["module"], r["status"], r["attempt_count"],
                          r["retry_success"], r["duration_ms"], r["browser"], r["os_name"], r["started_at"]])

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=execution_history.csv"},
    )
