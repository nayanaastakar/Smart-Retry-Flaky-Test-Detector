"""
core/project_runner.py
========================
Orchestrates a full project run: one real Selenium session, every enabled
test case's step sequence executed in turn through SmartRetryEngine +
EvidenceCollector, then FlakyDetector re-scored for the whole batch. This is
the dynamic-project equivalent of the Quick Run feature (routes/run_routes.py)
-- same pipeline, but driven by user-authored steps instead of a fixed
generic check battery.
"""

from __future__ import annotations

import json
import logging

from database.db_manager import fetch_all
from core.evidence_collector import EvidenceCollector
from core.flaky_detector import FlakyDetector
from core.retry_engine import SmartRetryEngine

logger = logging.getLogger("smart_retry.project_runner")


def run_project(project: dict, job=None) -> dict:
    """Run every enabled test case belonging to `project`. Returns a summary
    dict: {total, pass, fail, flaky, skipped_no_tests}."""
    test_rows = fetch_all(
        "SELECT * FROM test_cases WHERE project_id = ? AND enabled = 1 ORDER BY id ASC",
        (project["id"],),
    )
    if not test_rows:
        return {"total": 0, "pass": 0, "fail": 0, "flaky": 0, "skipped_no_tests": True}

    # Deferred on purpose: only import Selenium once we know there's actually
    # something to run, so an empty project doesn't require Selenium to be
    # installed just to tell you it has no test cases yet.
    from core.driver_factory import create_driver, quit_driver
    from core.step_executor import execute_steps

    emit = (lambda lvl, msg: job.log(lvl, msg)) if job else None
    if job:
        job.set_total(len(test_rows))
        job.log("info", f"Starting browser ({project.get('browser') or 'chrome'}) for {project['url']}")

    driver = create_driver(browser=project.get("browser") or "chrome")
    engine = SmartRetryEngine()
    results = {"PASS": 0, "FAIL": 0, "FLAKY": 0}
    checked_names: set[str] = set()

    try:
        for row in test_rows:
            test_case = dict(row)
            try:
                steps = json.loads(test_case["steps_json"] or "[]")
            except (json.JSONDecodeError, TypeError):
                steps = []

            def evidence_collector(exc, _name=test_case["name"]):
                collector = EvidenceCollector(driver, run_id=project["name"], test_name=_name)
                return collector.capture(exc)

            def run_this_test_case(_steps=steps, _url=project["url"]):
                execute_steps(driver, _steps, project_url=_url)

            result = engine.run(
                run_this_test_case,
                test_name=test_case["name"],
                module=project["name"],
                website_profile=project["url"],
                browser=project.get("browser") or "chrome",
                os_name=None,
                evidence_collector=evidence_collector,
                on_event=emit,
            )
            results[result.status.value] = results.get(result.status.value, 0) + 1
            checked_names.add(test_case["name"])
            if job:
                job.advance()
    finally:
        quit_driver(driver)

    detector = FlakyDetector()
    for name in checked_names:
        detector.evaluate_test(name, module=project["name"])

    return {
        "total": sum(results.values()),
        "pass": results.get("PASS", 0),
        "fail": results.get("FAIL", 0),
        "flaky": results.get("FLAKY", 0),
        "skipped_no_tests": False,
    }


def run_single_test_case(test_case_id: int, job=None) -> dict:
    """Run exactly one test case's step sequence, looking up its parent
    project for the URL/browser. Returns the same summary shape as
    run_project() but for a batch of one."""
    from database.db_manager import fetch_one

    test_case = fetch_one("SELECT * FROM test_cases WHERE id = ?", (test_case_id,))
    if not test_case:
        raise ValueError(f"Test case {test_case_id} not found.")
    test_case = dict(test_case)

    if not test_case.get("project_id"):
        raise ValueError("This test case isn't linked to a project, so there's no URL to run it against.")

    project = fetch_one("SELECT * FROM projects WHERE id = ?", (test_case["project_id"],))
    if not project:
        raise ValueError("The project this test case belongs to no longer exists.")
    project = dict(project)

    from core.driver_factory import create_driver, quit_driver
    from core.step_executor import execute_steps

    try:
        steps = json.loads(test_case["steps_json"] or "[]")
    except (json.JSONDecodeError, TypeError):
        steps = []

    if job:
        job.set_total(1)
        job.log("info", f"Starting browser ({project.get('browser') or 'chrome'}) for {project['url']}")
    driver = create_driver(browser=project.get("browser") or "chrome")
    engine = SmartRetryEngine()

    try:
        def evidence_collector(exc):
            collector = EvidenceCollector(driver, run_id=project["name"], test_name=test_case["name"])
            return collector.capture(exc)

        def run_it():
            execute_steps(driver, steps, project_url=project["url"])

        result = engine.run(
            run_it,
            test_name=test_case["name"],
            module=project["name"],
            website_profile=project["url"],
            browser=project.get("browser") or "chrome",
            os_name=None,
            evidence_collector=evidence_collector,
            on_event=(lambda lvl, msg: job.log(lvl, msg)) if job else None,
        )
        if job:
            job.advance()
    finally:
        quit_driver(driver)

    detector = FlakyDetector()
    detector.evaluate_test(test_case["name"], module=project["name"])

    return {
        "total": 1,
        "pass": 1 if result.status.value == "PASS" else 0,
        "fail": 1 if result.status.value == "FAIL" else 0,
        "flaky": 1 if result.status.value == "FLAKY" else 0,
        "skipped_no_tests": False,
        "project_name": project["name"],
    }
