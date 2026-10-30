"""routes/test_cases_routes.py - Module 13: Test Case Management."""

from __future__ import annotations

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for

from database.db_manager import execute, fetch_all, fetch_one
from routes.auth_routes import login_required

test_cases_bp = Blueprint("test_cases", __name__, url_prefix="/test-cases")


@test_cases_bp.route("/")
@login_required
def index():
    query = request.args.get("q", "").strip()
    module_filter = request.args.get("module", "")
    group_filter = request.args.get("group", "")

    where, params = [], []
    if query:
        where.append("name LIKE ?")
        params.append(f"%{query}%")
    if module_filter:
        where.append("module = ?")
        params.append(module_filter)
    if group_filter:
        where.append("group_name = ?")
        params.append(group_filter)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    rows = fetch_all(f"SELECT * FROM test_cases {where_sql} ORDER BY id DESC", tuple(params))
    test_cases = []
    for r in rows:
        tc = dict(r)
        try:
            tc["tags_list"] = json.loads(tc["tags"] or "[]")
        except (json.JSONDecodeError, TypeError):
            tc["tags_list"] = []
        test_cases.append(tc)

    modules = [r["module"] for r in fetch_all("SELECT DISTINCT module FROM test_cases")]
    groups = [r["group_name"] for r in fetch_all("SELECT DISTINCT group_name FROM test_cases")]
    website_profiles = fetch_all("SELECT name FROM website_profiles ORDER BY name")

    return render_template(
        "test_cases/index.html",
        test_cases=test_cases,
        modules=modules,
        groups=groups,
        website_profiles=[dict(w) for w in website_profiles],
        query=query,
        module_filter=module_filter,
        group_filter=group_filter,
        active_page="test_cases",
    )


@test_cases_bp.route("/create", methods=["POST"])
@login_required
def create():
    name = request.form.get("name", "").strip()
    module = request.form.get("module", "general").strip() or "general"
    website_profile = request.form.get("website_profile") or None
    description = request.form.get("description", "").strip()
    group_name = request.form.get("group_name", "default").strip() or "default"
    tags_raw = request.form.get("tags", "").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    if not name:
        flash("Test case name is required.", "error")
        return redirect(url_for("test_cases.index"))

    execute(
        """INSERT INTO test_cases (name, module, website_profile, description, tags, group_name, enabled)
           VALUES (?, ?, ?, ?, ?, ?, 1)""",
        (name, module, website_profile, description, json.dumps(tags), group_name),
    )
    flash(f"Test case '{name}' created.", "success")
    return redirect(url_for("test_cases.index"))


@test_cases_bp.route("/<int:test_id>/edit")
@login_required
def edit(test_id: int):
    from core.step_definitions import LOCATOR_TYPES, STEP_ACTIONS

    tc = fetch_one("SELECT * FROM test_cases WHERE id = ?", (test_id,))
    if not tc:
        flash("Test case not found.", "error")
        return redirect(url_for("test_cases.index"))
    tc = dict(tc)
    try:
        tc["steps_list"] = json.loads(tc["steps_json"] or "[]")
    except (json.JSONDecodeError, TypeError):
        tc["steps_list"] = []
    try:
        tc["tags_list"] = json.loads(tc["tags"] or "[]")
    except (json.JSONDecodeError, TypeError):
        tc["tags_list"] = []

    project = None
    if tc.get("project_id"):
        project = fetch_one("SELECT * FROM projects WHERE id = ?", (tc["project_id"],))
        project = dict(project) if project else None

    return render_template(
        "test_cases/builder.html",
        project=project,
        test_case=tc,
        step_actions=STEP_ACTIONS,
        locator_types=LOCATOR_TYPES,
        active_page="test_cases" if not project else "projects",
    )


@test_cases_bp.route("/<int:test_id>/update", methods=["POST"])
@login_required
def update(test_id: int):
    tc = fetch_one("SELECT * FROM test_cases WHERE id = ?", (test_id,))
    if not tc:
        flash("Test case not found.", "error")
        return redirect(url_for("test_cases.index"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    group_name = request.form.get("group_name", "default").strip() or "default"
    tags_raw = request.form.get("tags", "").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    steps_raw = request.form.get("steps_json", "[]")

    if not name:
        flash("Test case name is required.", "error")
        return redirect(url_for("test_cases.edit", test_id=test_id))

    try:
        steps = json.loads(steps_raw)
        if not isinstance(steps, list):
            raise ValueError("Steps must be a list.")
    except (json.JSONDecodeError, ValueError) as exc:
        flash(f"Step data was malformed: {exc}", "error")
        return redirect(url_for("test_cases.edit", test_id=test_id))

    execute(
        """UPDATE test_cases SET name = ?, description = ?, group_name = ?, tags = ?, steps_json = ?
           WHERE id = ?""",
        (name, description, group_name, json.dumps(tags), json.dumps(steps), test_id),
    )
    flash(f"'{name}' updated with {len(steps)} step(s).", "success")

    if tc["project_id"]:
        return redirect(url_for("projects.detail", project_id=tc["project_id"]))
    return redirect(url_for("test_cases.index"))


@test_cases_bp.route("/<int:test_id>/run", methods=["POST"])
@login_required
def run(test_id: int):
    from core.job_manager import start_job
    from core.project_runner import run_single_test_case

    tc = fetch_one("SELECT * FROM test_cases WHERE id = ?", (test_id,))
    if not tc:
        flash("Test case not found.", "error")
        return redirect(url_for("test_cases.index"))
    if not tc["project_id"]:
        flash("This test case isn't linked to a project, so there's no URL to run it against.", "error")
        return redirect(url_for("test_cases.index"))

    try:
        import core.driver_factory  # noqa: F401
        import core.step_executor  # noqa: F401
    except ImportError as exc:
        flash(f"Selenium isn't installed in this environment ({exc}). Run `pip install -r requirements.txt`.", "error")
        return redirect(url_for("projects.detail", project_id=tc["project_id"]))

    parent = fetch_one("SELECT name FROM projects WHERE id = ?", (tc["project_id"],))
    result_url = url_for("run.results", domain=parent["name"]) if parent else url_for("dashboard.index")

    def target(job):
        run_single_test_case(test_id, job=job)
        return result_url

    job = start_job(f"Test case: {tc['name']}", target)
    return redirect(url_for("run.progress", job_id=job.id))


@test_cases_bp.route("/<int:test_id>/toggle", methods=["POST"])
@login_required
def toggle(test_id: int):
    tc = fetch_one("SELECT * FROM test_cases WHERE id = ?", (test_id,))
    if not tc:
        flash("Test case not found.", "error")
        return redirect(url_for("test_cases.index"))
    new_state = 0 if tc["enabled"] else 1
    execute("UPDATE test_cases SET enabled = ? WHERE id = ?", (new_state, test_id))
    flash(f"'{tc['name']}' {'enabled' if new_state else 'disabled'}.", "success")
    return redirect(url_for("test_cases.index"))


@test_cases_bp.route("/<int:test_id>/duplicate", methods=["POST"])
@login_required
def duplicate(test_id: int):
    tc = fetch_one("SELECT * FROM test_cases WHERE id = ?", (test_id,))
    if not tc:
        flash("Test case not found.", "error")
        return redirect(url_for("test_cases.index"))
    execute(
        """INSERT INTO test_cases (name, module, website_profile, project_id, steps_json, description, tags, group_name, enabled)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (f"{tc['name']} (Copy)", tc["module"], tc["website_profile"], tc["project_id"],
         tc["steps_json"], tc["description"], tc["tags"], tc["group_name"], tc["enabled"]),
    )
    flash(f"Duplicated '{tc['name']}'.", "success")
    if tc["project_id"]:
        return redirect(url_for("projects.detail", project_id=tc["project_id"]))
    return redirect(url_for("test_cases.index"))


@test_cases_bp.route("/<int:test_id>/delete", methods=["POST"])
@login_required
def delete(test_id: int):
    tc = fetch_one("SELECT project_id FROM test_cases WHERE id = ?", (test_id,))
    execute("DELETE FROM test_cases WHERE id = ?", (test_id,))
    flash("Test case deleted.", "info")
    if tc and tc["project_id"]:
        return redirect(url_for("projects.detail", project_id=tc["project_id"]))
    return redirect(url_for("test_cases.index"))
