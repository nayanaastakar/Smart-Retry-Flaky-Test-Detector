"""
services/analytics_service.py
==============================
Aggregation layer between raw `executions` rows and the dashboard/API. All
SQL aggregation lives here so routes stay thin and templates stay dumb.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from database.db_manager import fetch_all, fetch_one


def get_summary_metrics() -> dict:
    """Top-level KPI tiles shown at the top of the dashboard."""
    total = fetch_one("SELECT COUNT(*) c FROM executions")["c"]
    passed = fetch_one("SELECT COUNT(*) c FROM executions WHERE status IN ('PASS','FLAKY')")["c"]
    failed = fetch_one("SELECT COUNT(*) c FROM executions WHERE status = 'FAIL'")["c"]
    flaky = fetch_one("SELECT COUNT(*) c FROM executions WHERE status = 'FLAKY'")["c"]

    retried = fetch_one("SELECT COUNT(*) c FROM executions WHERE attempt_count > 1")["c"]
    retry_saved = fetch_one("SELECT COUNT(*) c FROM executions WHERE retry_success = 1")["c"]
    retry_success_rate = round((retry_saved / retried) * 100, 1) if retried else 0.0

    avg_duration = fetch_one("SELECT AVG(duration_ms) a FROM executions")["a"] or 0
    ai_count = fetch_one("SELECT COUNT(*) c FROM ai_analyses")["c"]

    today = datetime.now(timezone.utc).date().isoformat()
    today_count = fetch_one(
        "SELECT COUNT(*) c FROM executions WHERE date(started_at) = date(?)", (today,)
    )["c"]

    last_exec = fetch_one("SELECT test_name, status, started_at FROM executions ORDER BY id DESC LIMIT 1")

    pass_rate = round((passed / total) * 100, 1) if total else 0.0

    return {
        "total_executions": total,
        "passed": passed,
        "failed": failed,
        "flaky": flaky,
        "pass_rate": pass_rate,
        "retry_success_rate": retry_success_rate,
        "avg_duration_ms": round(avg_duration, 0),
        "avg_duration_s": round(avg_duration / 1000, 2),
        "ai_analysis_count": ai_count,
        "today_executions": today_count,
        "last_execution": dict(last_exec) if last_exec else None,
    }


def get_status_distribution() -> dict:
    """For the pie chart: PASS vs FAIL vs FLAKY counts."""
    rows = fetch_all("SELECT status, COUNT(*) c FROM executions GROUP BY status")
    dist = {"PASS": 0, "FAIL": 0, "FLAKY": 0, "SKIPPED": 0}
    for r in rows:
        if r["status"] in dist:
            dist[r["status"]] = r["c"]
        elif r["status"] == "RUNNING":
            continue
    return dist


def get_execution_trend(days: int = 14) -> dict:
    """For the line chart: daily pass/fail/flaky counts over the last N days."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    rows = fetch_all(
        """SELECT date(started_at) d, status, COUNT(*) c
           FROM executions WHERE date(started_at) >= date(?)
           GROUP BY d, status ORDER BY d ASC""",
        (since,),
    )
    days_list = [(datetime.now(timezone.utc).date() - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]
    series = {"PASS": {d: 0 for d in days_list}, "FAIL": {d: 0 for d in days_list}, "FLAKY": {d: 0 for d in days_list}}
    for r in rows:
        if r["status"] in series and r["d"] in series[r["status"]]:
            series[r["status"]][r["d"]] = r["c"]
    return {
        "labels": days_list,
        "pass": [series["PASS"][d] for d in days_list],
        "fail": [series["FAIL"][d] for d in days_list],
        "flaky": [series["FLAKY"][d] for d in days_list],
    }


def get_retry_trend(days: int = 14) -> dict:
    """Average retry attempts per day, for the retry-trend bar chart."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    rows = fetch_all(
        """SELECT date(started_at) d, AVG(attempt_count) avg_attempts
           FROM executions WHERE date(started_at) >= date(?)
           GROUP BY d ORDER BY d ASC""",
        (since,),
    )
    return {"labels": [r["d"] for r in rows], "values": [round(r["avg_attempts"], 2) for r in rows]}


def get_module_breakdown() -> list[dict]:
    rows = fetch_all(
        """SELECT module,
                  COUNT(*) total,
                  SUM(CASE WHEN status IN ('PASS','FLAKY') THEN 1 ELSE 0 END) passed,
                  SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) failed
           FROM executions GROUP BY module ORDER BY total DESC"""
    )
    return [dict(r) for r in rows]


def get_top_failed_tests(limit: int = 8) -> list[dict]:
    rows = fetch_all(
        """SELECT test_name, module, COUNT(*) fail_count
           FROM executions WHERE status = 'FAIL'
           GROUP BY test_name, module ORDER BY fail_count DESC LIMIT ?""",
        (limit,),
    )
    return [dict(r) for r in rows]


def get_recent_executions(limit: int = 12) -> list[dict]:
    rows = fetch_all(
        """SELECT id, run_id, test_name, module, status, attempt_count, duration_ms, browser, started_at
           FROM executions ORDER BY id DESC LIMIT ?""",
        (limit,),
    )
    return [dict(r) for r in rows]


def get_recent_reports(limit: int = 6) -> list[dict]:
    rows = fetch_all(
        """SELECT id, run_id, report_type, file_path, total_tests, passed, failed, flaky, created_at
           FROM reports ORDER BY id DESC LIMIT ?""",
        (limit,),
    )
    return [dict(r) for r in rows]
