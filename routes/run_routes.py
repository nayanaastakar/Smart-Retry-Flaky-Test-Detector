"""
routes/run_routes.py
======================
The "paste a link and run tests" feature -- fully generalized, not tied to
any specific site. Takes a URL from the dashboard modal, spins up a real
Selenium WebDriver, and runs the generic smoke-check battery from
core/generic_test_suite.py *N times in a row* (N chosen by the user) through
the same SmartRetryEngine, EvidenceCollector, and FlakyDetector that the rest
of the platform uses.

Why N runs, not one: flakiness is a run-to-run property. A single execution
can only ever be PASS or FAIL (or "FLAKY" in the narrow sense of "needed a
retry within that one run"); to say a check on a given site *flips* between
passing and failing across attempts, you need several independent
executions to compare. This route drives exactly that, then hands you a
dedicated results page with a real flaky score per check -- not a guess.
"""

from __future__ import annotations

import logging
from urllib.parse import quote, urlparse

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from config import settings
from core.evidence_collector import EvidenceCollector
from core.flaky_detector import FlakyDetector
from core.job_manager import get_job, start_job
from core.retry_engine import SmartRetryEngine
from database.db_manager import fetch_all
from routes.auth_routes import login_required

run_bp = Blueprint("run", __name__, url_prefix="/run")
logger = logging.getLogger("smart_retry.run")

MIN_ITERATIONS = 1
MAX_ITERATIONS = 20
DEFAULT_ITERATIONS = 5


def _normalize_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        raise ValueError("Please enter a URL.")
    if not raw_url.startswith(("http://", "https://")):
        raw_url = f"https://{raw_url}"
    parsed = urlparse(raw_url)
    if not parsed.netloc:
        raise ValueError(f"'{raw_url}' doesn't look like a valid URL.")
    return raw_url


def _quick_run_job(job, url: str, domain: str, browser: str, iterations: int) -> str:
    """Background body of a Quick Run. Returns the results-page URL."""
    from core.driver_factory import create_driver, quit_driver
    from core.generic_test_suite import build_generic_checks

    job.log("info", f"Starting {browser} browser for {url}")
    driver = create_driver(browser=browser)
    engine = SmartRetryEngine()
    results = {"PASS": 0, "FAIL": 0, "FLAKY": 0}
    checked_names: set[str] = set()
    emit = lambda lvl, msg: job.log(lvl, msg)  # noqa: E731

    try:
        checks_per_round = len(build_generic_checks(driver, url))
        job.set_total(iterations * checks_per_round)
        for round_no in range(1, iterations + 1):
            job.log("info", f"Round {round_no}/{iterations}")
            for check in build_generic_checks(driver, url):
                def evidence_collector(exc, _check_name=check.name):
                    return EvidenceCollector(driver, run_id=domain, test_name=_check_name).capture(exc)

                result = engine.run(
                    check.fn,
                    test_name=check.name,
                    module=domain,
                    website_profile=url,
                    browser=browser,
                    os_name=None,
                    evidence_collector=evidence_collector,
                    on_event=emit,
                )
                results[result.status.value] = results.get(result.status.value, 0) + 1
                checked_names.add(check.name)
                job.advance()
    finally:
        quit_driver(driver)

    detector = FlakyDetector(window_size=max(settings.FLAKY_WINDOW_SIZE, iterations))
    for name in checked_names:
        detector.evaluate_test(name, module=domain)

    job.log(
        "success" if results["FAIL"] == 0 else "error",
        f"{iterations}x run on {domain}: {results['PASS']} passed, {results['FAIL']} failed, {results['FLAKY']} flaky",
    )
    return "/run/results/" + quote(domain, safe="")


@run_bp.route("/execute", methods=["POST"])
@login_required
def execute():
    from services.settings_service import get_runtime_settings

    raw_url = request.form.get("url", "")
    browser = request.form.get("browser") or get_runtime_settings()["browser"]
    iterations = request.form.get("iterations", type=int) or DEFAULT_ITERATIONS
    iterations = max(MIN_ITERATIONS, min(MAX_ITERATIONS, iterations))

    try:
        url = _normalize_url(raw_url)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("dashboard.index"))

    try:
        import core.driver_factory  # noqa: F401
        import core.generic_test_suite  # noqa: F401
    except ImportError as exc:
        logger.exception("Selenium is not installed / importable")
        flash(
            f"Selenium isn't installed in this environment ({exc}). "
            f"Run `pip install -r requirements.txt` and try again.",
            "error",
        )
        return redirect(url_for("dashboard.index"))

    domain = urlparse(url).netloc or "custom-run"
    job = start_job(
        f"Quick Run: {domain} x{iterations}",
        lambda j: _quick_run_job(j, url, domain, browser, iterations),
    )
    return redirect(url_for("run.progress", job_id=job.id))


@run_bp.route("/progress/<job_id>")
@login_required
def progress(job_id: str):
    job = get_job(job_id)
    if job is None:
        flash("That run is no longer available (server restarted or job expired).", "info")
        return redirect(url_for("dashboard.index"))
    return render_template("run/progress.html", job=job.snapshot(), active_page="console")


@run_bp.route("/status/<job_id>")
@login_required
def status(job_id: str):
    job = get_job(job_id)
    if job is None:
        return jsonify({"status": "gone", "error": "Job not found"}), 404
    return jsonify(job.snapshot(since_event_id=request.args.get("since", default=0, type=int)))


@run_bp.route("/results/<domain>")
@login_required
def results(domain: str):
    """Dedicated flakiness verdict page for a single pasted URL/domain --
    the direct answer to "is this site flaky", independent of any
    site-specific profile."""
    flaky_rows = fetch_all(
        "SELECT * FROM flaky_history WHERE module = ? ORDER BY flaky_score DESC", (domain,)
    )
    execution_rows = fetch_all(
        """SELECT id, test_name, status, attempt_count, retry_success, duration_ms, started_at
           FROM executions WHERE module = ? ORDER BY id DESC LIMIT 60""",
        (domain,),
    )

    if not flaky_rows and not execution_rows:
        flash(f"No run history found for {domain} yet.", "info")
        return redirect(url_for("dashboard.index"))

    checks = [dict(r) for r in flaky_rows]
    flaky_checks = [c for c in checks if c["classification"] == "FLAKY"]
    chronic_checks = [c for c in checks if c["classification"] == "CHRONIC_FAILURE"]

    if chronic_checks:
        overall_verdict = "CHRONIC_FAILURE"
    elif flaky_checks:
        overall_verdict = "FLAKY"
    else:
        overall_verdict = "STABLE"

    return render_template(
        "run/results.html",
        domain=domain,
        checks=checks,
        executions=[dict(r) for r in execution_rows],
        overall_verdict=overall_verdict,
        flaky_checks=flaky_checks,
        chronic_checks=chronic_checks,
        active_page="run_results",
    )
