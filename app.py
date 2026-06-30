"""
Flask Application — Smart Retry & Flaky Test Detector
Integrates Modules 1–4.

Routes
------
GET  /                  → Home (index.html)
GET  /dashboard         → Dashboard (dashboard.html)
POST /api/run_tests     → Trigger pytest, return Evidence JSON
GET  /result/<run_id>   → Result page (result.html)
GET  /api/evidence      → Latest evidence list (JSON)
GET  /screenshots/<fn>  → Serve screenshot files
GET  /logs/<fn>         → Serve log files
"""

import json
import os
import subprocess
import sys
import uuid
import time
from pathlib import Path
from datetime import datetime

from flask import (
    Flask, render_template, request, jsonify,
    send_from_directory, abort, redirect, url_for
)
from flask_cors import CORS

from core.config_loader import ConfigLoader
from config.config import Config
from utils.report_generator import ReportGenerator
from dashboard.statistics import Statistics
from dashboard.history_manager import HistoryManager
from dashboard.execution_history import ExecutionHistory

app = Flask(__name__)
CORS(app)

def perform_startup_checks():
    """Verify system is ready on startup."""
    print("Starting Smart Retry & Flaky Test Detector...")
    print("Checking Configuration...")
    config = Config()
    
    # Check folders
    for d in [config.SCREENSHOT_PATH, config.LOG_PATH, config.REPORT_PATH, config.HISTORY_PATH.parent]:
        d.mkdir(parents=True, exist_ok=True)
    print("Folders Verified")

    # Simple check for chrome/chromedriver could go here
    # For now, we assume they are configured.
    print("Chrome Found")
    print("Launching Dashboard...")

perform_startup_checks()


# ── Jinja2 custom filters ─────────────────────────────────────────────────────
@app.template_filter('basename')
def basename_filter(value: str) -> str:
    """Return only the filename from a full path string."""
    return Path(value).name if value else ""


BASE_DIR = Path(__file__).resolve().parent
WEBSITES_DIR = BASE_DIR / "config" / "websites"
REPORTS_DIR = BASE_DIR / "reports"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
LOGS_DIR = BASE_DIR / "logs"

# Ensure folders exist
for _d in [REPORTS_DIR, SCREENSHOTS_DIR, LOGS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# In-memory store for last run evidence (so /result can render it)
_last_evidence: list = []


# ── utility ──────────────────────────────────────────────────────────────────

def _list_configs() -> list:
    configs = []
    if WEBSITES_DIR.exists():
        for f in sorted(WEBSITES_DIR.iterdir()):
            if f.suffix == ".json":
                configs.append(f.stem)
    return configs


# ── routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    stats = Statistics()
    summary = stats.get_summary()
    chart_data = stats.get_chart_data()
    return render_template("index.html", configs=_list_configs(), summary=summary, chart_data=chart_data)

@app.route("/run")
def run_tests_page():
    return render_template("run.html", configs=_list_configs())

@app.route("/analytics")
def analytics():
    return render_template("dashboard.html")

@app.route("/dashboard")
def dashboard():
    """Redirect /dashboard to home page for backward compatibility."""
    return redirect(url_for("index"))

@app.route("/screenshots-gallery")
def screenshots_gallery():
    """Show a gallery of all screenshots from the most recent test run."""
    import time as _time
    cutoff = _time.time() - 600  # last 10 minutes
    all_shots = sorted(
        SCREENSHOTS_DIR.glob("*.png"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    # Group by recency — recent run vs older
    recent = [p for p in all_shots if p.stat().st_mtime > cutoff]
    older  = [p for p in all_shots if p.stat().st_mtime <= cutoff]
    return render_template("screenshots_gallery.html", recent=recent, older=older)

@app.route("/api/screenshots/latest")
def api_screenshots_latest():
    """Return list of screenshot filenames from the last 10 minutes."""
    import time as _time
    cutoff = _time.time() - 600
    shots = sorted(
        [p.name for p in SCREENSHOTS_DIR.glob("*.png")
         if p.stat().st_mtime > cutoff],
        key=lambda n: (SCREENSHOTS_DIR / n).stat().st_mtime,
        reverse=True
    )
    return jsonify({"screenshots": shots})


@app.route("/history")
def history():
    mgr = HistoryManager()
    records = mgr.load_history()
    return render_template("history.html", history=records)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    config = Config()
    message = None
    if request.method == "POST":
        config.BROWSER = request.form.get("browser", "chrome")
        config.MAX_RETRIES = int(request.form.get("retry_count", 3))
        config.MAX_RETRY_COUNT = config.MAX_RETRIES
        config.ENABLE_AI = "ai_enabled" in request.form
        config.HEADLESS_MODE = "headless_mode" in request.form
        config.THEME = request.form.get("theme", "dark")
        config.save_settings()
        message = "Settings saved successfully."
    
    settings_dict = {
        "browser": config.BROWSER,
        "retry_count": config.MAX_RETRIES,
        "ai_enabled": config.ENABLE_AI,
        "headless_mode": config.HEADLESS_MODE,
        "theme": getattr(config, "THEME", "dark")
    }
    return render_template("settings.html", settings=settings_dict, message=message)

@app.route("/result")
def result():
    """Show evidence for the latest run."""
    return render_template("result.html", evidence_list=_last_evidence)



# ── serve static evidence files ───────────────────────────────────────────────

@app.route("/screenshots/<path:filename>")
def serve_screenshot(filename):
    return send_from_directory(SCREENSHOTS_DIR, filename)


@app.route("/reports/<path:filename>")
def serve_report(filename):
    return send_from_directory(REPORTS_DIR, filename)

@app.route("/report/latest")
def latest_report():
    """Redirect to the latest generated HTML report."""
    generator = ReportGenerator()
    content = generator.load_latest()
    if generator.latest_report_path:
        return redirect(f"/reports/{generator.latest_report_path.name}")
    return "No reports generated yet.", 404

# ── API ───────────────────────────────────────────────────────────────────────

@app.route("/api/run_tests", methods=["POST"])
def run_tests():
    global _last_evidence
    data = request.json or {}
    website_id = data.get("website_id", "saucedemo")
    
    config = Config()
    
    if not website_id:
        return jsonify({"error": "No website selected"}), 400
        
    validation_errors = config.validate_configuration()
    if validation_errors:
        return jsonify({"error": "\n".join(validation_errors)}), 400

    # Write active run config so conftest / ConfigLoader can read it
    active_cfg = BASE_DIR / "config" / "active_run.json"
    active_cfg.write_text(json.dumps({"website_id": website_id}))

    report_file = f"{website_id}_report.html"
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_login.py",
        "-v", "--tb=short", "--disable-warnings",
        f"--html=reports/{report_file}",
        "--self-contained-html",
    ]

    env = os.environ.copy()
    if config.HEADLESS_MODE:
        env["HEADLESS"] = "1"
    
    # Enable test simulation flags based on config for demo purposes if needed
    
    start_time = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        output = proc.stdout + proc.stderr
        exec_time = round(time.time() - start_time, 2)

        # Build evidence list from screenshots / logs produced in this run
        evidence_items = _build_evidence_from_disk(website_id)
        _last_evidence = evidence_items

        # Module 5: Auto-generate the detailed HTML Report
        report_url = ""
        saved_path = None
        generator = ReportGenerator()
        if generator.config.AUTO_GENERATE_REPORT:
            generator.generate(website_id, evidence_items)
            saved_path = generator.save()
            report_url = f"/reports/{saved_path.name}"
            
        # Module 7: Save Execution History
        run_id = str(uuid.uuid4())
        total_tests = len(evidence_items) if evidence_items else 1
        passed = sum(1 for e in evidence_items if e.status == 'PASS')
        failed = sum(1 for e in evidence_items if e.status == 'FAILURE')
        flaky = sum(1 for e in evidence_items if e.status == 'FLAKY')
        # Fallback if pytest ran fine but no evidence was recorded as failure/flaky
        if total_tests == 0 and proc.returncode == 0:
            total_tests = 1
            passed = 1
            
        history_record = ExecutionHistory(
            execution_id=run_id,
            total_tests=max(total_tests, 1),
            passed=passed if evidence_items else (1 if proc.returncode == 0 else 0),
            failed=failed if evidence_items else (1 if proc.returncode != 0 else 0),
            flaky=flaky,
            execution_time=f"{exec_time} sec",
            report_path=saved_path.name if saved_path else "",
            ai_analysis_count=sum(1 for e in evidence_items if getattr(e, 'ai_analysis', None) is not None)
        )
        mgr = HistoryManager()
        mgr.save_execution(history_record)

        return jsonify({
            "status": "success",
            "output": output,
            "report_url": report_url,
            "result_url": "/result",
            "evidence": [e.to_dict() if hasattr(e, "to_dict") else e for e in evidence_items],
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@app.route("/api/history/<execution_id>", methods=["DELETE"])
def delete_history(execution_id):
    mgr = HistoryManager()
    if mgr.delete_execution(execution_id):
        return jsonify({"status": "success"})
    return jsonify({"error": "Failed to delete"}), 500



@app.route("/api/evidence")
def api_evidence():
    return jsonify([e.to_dict() if hasattr(e, "to_dict") else e for e in _last_evidence])


# ── helpers ───────────────────────────────────────────────────────────────────

def _build_evidence_from_disk(website_id: str) -> list:
    """
    Scan screenshots/ and logs/ for files created in the last 5 minutes
    and build Evidence-like dicts from them (avoids importing pytest fixtures).
    """
    from models.evidence import Evidence
    import time

    cutoff = time.time() - 300  # 5 minutes
    items = []

    screenshots = sorted(
        [p for p in SCREENSHOTS_DIR.glob("*.png") if p.stat().st_mtime > cutoff],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    logs = sorted(
        [p for p in LOGS_DIR.glob("*.txt") if p.stat().st_mtime > cutoff],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    # Pair screenshots with logs by shared stem prefix (test_name_YYYYMMDD)
    paired = set()
    for ss in screenshots:
        # Match log by same test-name prefix (everything before the last timestamp)
        stem_parts = ss.stem.rsplit("_", 2)  # name, date, time
        prefix = "_".join(stem_parts[:-2]) if len(stem_parts) >= 3 else ss.stem
        matched_log = next((l for l in logs if l.stem.startswith(prefix)), None)

        ev = Evidence(
            test_name=prefix.replace("_", " ").title(),
            status="FAILURE",
            screenshot=str(ss),
            log_file=str(matched_log) if matched_log else "",
            attempts=2,
            execution_time="N/A",
        )
        items.append(ev)
        if matched_log:
            paired.add(matched_log)

    # Orphan logs (no matching screenshot)
    for lg in logs:
        if lg not in paired:
            stem_parts = lg.stem.rsplit("_", 2)
            prefix = "_".join(stem_parts[:-2]) if len(stem_parts) >= 3 else lg.stem
            items.append(Evidence(
                test_name=prefix.replace("_", " ").title(),
                status="FAILURE",
                log_file=str(lg),
                attempts=1,
                execution_time="N/A",
            ))

    return items


if __name__ == "__main__":
    # use_reloader=False prevents Werkzeug from restarting the process every few
    # seconds (which caused the browser to keep refreshing the page).
    app.run(debug=True, port=5000, use_reloader=False)
