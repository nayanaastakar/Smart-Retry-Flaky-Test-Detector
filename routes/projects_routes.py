"""
routes/projects_routes.py
===========================
Projects are the generalized replacement for "website profiles": instead of
picking from a dropdown of pre-baked sites, a user creates a Project with
just a name and a URL, then builds Test Cases (ordered step sequences, see
core/step_executor.py) against it. No site is special-cased anywhere in
this code path.
"""

from __future__ import annotations

import json
import logging
from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for

from database.db_manager import execute, fetch_all, fetch_one
from routes.auth_routes import login_required

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")
logger = logging.getLogger("smart_retry.projects")


def _normalize_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        raise ValueError("Website URL is required.")
    if not raw_url.startswith(("http://", "https://")):
        raw_url = f"https://{raw_url}"
    if not urlparse(raw_url).netloc:
        raise ValueError(f"'{raw_url}' doesn't look like a valid URL.")
    return raw_url


@projects_bp.route("/")
@login_required
def index():
    rows = fetch_all("SELECT * FROM projects ORDER BY id DESC")
    projects = []
    for r in rows:
        p = dict(r)
        try:
            p["tags_list"] = json.loads(p["tags"] or "[]")
        except (json.JSONDecodeError, TypeError):
            p["tags_list"] = []
        test_count = fetch_one("SELECT COUNT(*) c FROM test_cases WHERE project_id = ?", (p["id"],))
        p["test_case_count"] = test_count["c"] if test_count else 0
        exec_count = fetch_one("SELECT COUNT(*) c FROM executions WHERE module = ?", (p["name"],))
        p["execution_count"] = exec_count["c"] if exec_count else 0
        flaky_count = fetch_one(
            "SELECT COUNT(*) c FROM flaky_history WHERE module = ? AND classification = 'FLAKY'", (p["name"],)
        )
        p["flaky_count"] = flaky_count["c"] if flaky_count else 0
        projects.append(p)

    return render_template("projects/index.html", projects=projects, active_page="projects")


@projects_bp.route("/create", methods=["POST"])
@login_required
def create():
    name = request.form.get("name", "").strip()
    raw_url = request.form.get("url", "")
    browser = request.form.get("browser", "chrome")
    notes = request.form.get("notes", "").strip()
    tags_raw = request.form.get("tags", "").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    if not name:
        flash("Project name is required.", "error")
        return redirect(url_for("projects.index"))

    try:
        url = _normalize_url(raw_url)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("projects.index"))

    existing = fetch_one("SELECT id FROM projects WHERE name = ?", (name,))
    if existing:
        flash(f"A project named '{name}' already exists.", "error")
        return redirect(url_for("projects.index"))

    project_id = execute(
        "INSERT INTO projects (name, url, browser, tags, notes) VALUES (?, ?, ?, ?, ?)",
        (name, url, browser, json.dumps(tags), notes),
    )
    flash(f"Project '{name}' created.", "success")
    return redirect(url_for("projects.detail", project_id=project_id))


@projects_bp.route("/<int:project_id>/update", methods=["POST"])
@login_required
def update(project_id: int):
    project = fetch_one("SELECT * FROM projects WHERE id = ?", (project_id,))
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("projects.index"))

    name = request.form.get("name", "").strip()
    raw_url = request.form.get("url", "")
    browser = request.form.get("browser", "chrome")
    notes = request.form.get("notes", "").strip()
    tags_raw = request.form.get("tags", "").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    if not name:
        flash("Project name is required.", "error")
        return redirect(url_for("projects.detail", project_id=project_id))

    try:
        url = _normalize_url(raw_url)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("projects.detail", project_id=project_id))

    duplicate = fetch_one("SELECT id FROM projects WHERE name = ? AND id != ?", (name, project_id))
    if duplicate:
        flash(f"A project named '{name}' already exists.", "error")
        return redirect(url_for("projects.detail", project_id=project_id))

    execute(
        "UPDATE projects SET name = ?, url = ?, browser = ?, tags = ?, notes = ? WHERE id = ?",
        (name, url, browser, json.dumps(tags), notes, project_id),
    )
    flash(f"Project '{name}' updated.", "success")
    return redirect(url_for("projects.detail", project_id=project_id))


@projects_bp.route("/<int:project_id>")
@login_required
def detail(project_id: int):
    project = fetch_one("SELECT * FROM projects WHERE id = ?", (project_id,))
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("projects.index"))

    project = dict(project)
    try:
        project["tags_list"] = json.loads(project["tags"] or "[]")
    except (json.JSONDecodeError, TypeError):
        project["tags_list"] = []

    test_rows = fetch_all("SELECT * FROM test_cases WHERE project_id = ? ORDER BY id DESC", (project_id,))
    test_cases = []
    for r in test_rows:
        tc = dict(r)
        try:
            tc["steps_list"] = json.loads(tc["steps_json"] or "[]")
        except (json.JSONDecodeError, TypeError):
            tc["steps_list"] = []
        test_cases.append(tc)

    recent_executions = fetch_all(
        """SELECT id, test_name, status, attempt_count, duration_ms, started_at
           FROM executions WHERE module = ? ORDER BY id DESC LIMIT 15""",
        (project["name"],),
    )
    flaky_summary = fetch_all(
        "SELECT * FROM flaky_history WHERE module = ? ORDER BY flaky_score DESC", (project["name"],)
    )

    return render_template(
        "projects/detail.html",
        project=project,
        test_cases=test_cases,
        recent_executions=[dict(r) for r in recent_executions],
        flaky_summary=[dict(r) for r in flaky_summary],
        active_page="projects",
    )


@projects_bp.route("/<int:project_id>/tests/new")
@login_required
def new_test_case(project_id: int):
    from core.step_definitions import LOCATOR_TYPES, STEP_ACTIONS

    project = fetch_one("SELECT * FROM projects WHERE id = ?", (project_id,))
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("projects.index"))

    return render_template(
        "test_cases/builder.html",
        project=dict(project),
        test_case=None,
        step_actions=STEP_ACTIONS,
        locator_types=LOCATOR_TYPES,
        active_page="projects",
    )


@projects_bp.route("/<int:project_id>/tests/create", methods=["POST"])
@login_required
def create_test_case(project_id: int):
    project = fetch_one("SELECT * FROM projects WHERE id = ?", (project_id,))
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("projects.index"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    group_name = request.form.get("group_name", "default").strip() or "default"
    tags_raw = request.form.get("tags", "").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    steps_raw = request.form.get("steps_json", "[]")

    if not name:
        flash("Test case name is required.", "error")
        return redirect(url_for("projects.new_test_case", project_id=project_id))

    try:
        steps = json.loads(steps_raw)
        if not isinstance(steps, list):
            raise ValueError("Steps must be a list.")
    except (json.JSONDecodeError, ValueError) as exc:
        flash(f"Step data was malformed: {exc}", "error")
        return redirect(url_for("projects.new_test_case", project_id=project_id))

    execute(
        """INSERT INTO test_cases (name, module, project_id, steps_json, description, tags, group_name, enabled)
           VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
        (name, project["name"], project_id, json.dumps(steps), description, json.dumps(tags), group_name),
    )
    flash(f"Test case '{name}' created with {len(steps)} step(s).", "success")
    return redirect(url_for("projects.detail", project_id=project_id))


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
def delete(project_id: int):
    project = fetch_one("SELECT * FROM projects WHERE id = ?", (project_id,))
    if not project:
        flash("Project not found.", "error")
    else:
        execute("DELETE FROM projects WHERE id = ?", (project_id,))
        flash(f"Deleted project '{project['name']}' and its test cases.", "info")
    return redirect(url_for("projects.index"))


@projects_bp.route("/<int:project_id>/run", methods=["POST"])
@login_required
def run_all(project_id: int):
    """Run every enabled test case in this project as a background job and
    send the user to a live progress page."""
    from core.job_manager import start_job
    from core.project_runner import run_project

    project = fetch_one("SELECT * FROM projects WHERE id = ?", (project_id,))
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("projects.index"))
    project = dict(project)

    enabled = fetch_one(
        "SELECT COUNT(*) c FROM test_cases WHERE project_id = ? AND enabled = 1", (project_id,)
    )["c"]
    if not enabled:
        flash("This project has no enabled test cases yet. Add one first.", "info")
        return redirect(url_for("projects.detail", project_id=project_id))

    try:
        import core.driver_factory  # noqa: F401
        import core.step_executor  # noqa: F401
    except ImportError as exc:
        flash(f"Selenium isn't installed in this environment ({exc}). Run `pip install -r requirements.txt`.", "error")
        return redirect(url_for("projects.detail", project_id=project_id))

    result_url = url_for("run.results", domain=project["name"])  # resolved here: no request context in the thread

    def target(job):
        summary = run_project(project, job=job)
        job.log(
            "success" if summary["fail"] == 0 else "error",
            f"{summary['total']} test case(s): {summary['pass']} passed, {summary['fail']} failed, {summary['flaky']} flaky",
        )
        return result_url

    job = start_job(f"Project run: {project['name']}", target)
    return redirect(url_for("run.progress", job_id=job.id))
