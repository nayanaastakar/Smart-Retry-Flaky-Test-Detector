"""
scripts/capture_screenshots.py
==============================
Generates high-resolution screenshots of the Smart Retry & Flaky Test Detection
Framework web interface for the GitHub README documentation, modelled after KubeSight.

This script:
1. Wipes and re-seeds the database with clean, internally consistent demo data.
2. Generates AI failure analyses using the heuristic fallback engine.
3. Generates multi-format reports.
4. Launches Flask in a background thread.
5. Captures 11 carefully chosen screenshots showing professional application states.

Run:  python scripts/capture_screenshots.py
"""

import json
import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

os.chdir(BASE_DIR)

from app import app
from database.db_manager import init_db, execute, fetch_one, fetch_all
from database.seed import run_all as seed_all

DOCS_IMG_DIR = BASE_DIR / "docs" / "images"
DOCS_IMG_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "data" / "smart_retry.db"


def _wipe_and_reseed():
    """Drop all data tables and reseed from scratch for a clean slate."""
    print("[0/6] Wiping existing data for a clean reseed...")
    # Disable foreign keys for the wipe, then re-enable
    from database.db_manager import get_connection
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = OFF")
    for tbl in ["ai_analyses", "retry_attempts", "executions", "flaky_history",
                 "reports", "test_cases", "projects"]:
        conn.execute(f"DELETE FROM {tbl}")
    # Reset auto-increment counters
    for tbl in ["ai_analyses", "retry_attempts", "executions", "flaky_history",
                 "reports", "test_cases", "projects"]:
        try:
            conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{tbl}'")
        except Exception:
            pass
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    seed_all()


def seed_showcase_data():
    """Populates realistic data across projects, test cases, AI analyses, and reports."""
    _wipe_and_reseed()

    print("[1/6] Generating execution history with proper Selenium exception types...")
    # Import here so the patched generate_demo_data is used
    from utils.generate_demo_data import generate as generate_demo_data
    generate_demo_data(num_runs_per_test=15)

    print("[2/6] Seeding showcase projects with Visual Test Builder steps...")
    # --- Project: SauceDemo E-Commerce ---
    p1_id = execute(
        "INSERT INTO projects (name, url, browser, tags, notes) VALUES (?, ?, ?, ?, ?)",
        (
            "SauceDemo E-Commerce",
            "https://www.saucedemo.com",
            "chrome",
            json.dumps(["production", "e-commerce", "smoke", "checkout", "regression"]),
            "Primary end-to-end regression suite covering catalog browsing, cart operations, and checkout validation against the SauceDemo demo store.",
        ),
    )

    # --- Project: OrangeHRM Portal ---
    p2_id = execute(
        "INSERT INTO projects (name, url, browser, tags, notes) VALUES (?, ?, ?, ?, ?)",
        (
            "OrangeHRM Portal",
            "https://opensource-demo.orangehrmlive.com",
            "chrome",
            json.dumps(["internal", "hr", "auth", "rbac", "admin"]),
            "Enterprise HR workflow suite covering admin login, role-based access control, and employee record management.",
        ),
    )

    # --- Project: DemoQA Interactions ---
    p3_id = execute(
        "INSERT INTO projects (name, url, browser, tags, notes) VALUES (?, ?, ?, ?, ?)",
        (
            "DemoQA Interactions",
            "https://demoqa.com",
            "chrome",
            json.dumps(["ui", "forms", "widgets", "interactions"]),
            "UI component and interaction testing suite for form elements, drag-and-drop, resizable widgets, and keyboard interactions.",
        ),
    )

    # --- Test Cases for SauceDemo ---
    steps_login = [
        {"action": "open_url", "input_value": "https://www.saucedemo.com", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Open SauceDemo home page"},
        {"action": "type_text", "input_value": "standard_user", "locator_type": "css", "locator_value": "#user-name", "timeout": 10, "description": "Enter username"},
        {"action": "type_text", "input_value": "secret_sauce", "locator_type": "css", "locator_value": "#password", "timeout": 10, "description": "Enter password"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#login-button", "timeout": 10, "description": "Click Login button"},
        {"action": "assert_url_contains", "input_value": "/inventory.html", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Verify redirect to inventory"},
        {"action": "assert_element_visible", "input_value": None, "locator_type": "css", "locator_value": ".inventory_list", "timeout": 10, "description": "Confirm product grid is loaded"},
        {"action": "screenshot", "input_value": "logged-in-state", "locator_type": "css", "locator_value": None, "timeout": 5, "description": "Checkpoint: inventory page loaded"},
    ]

    steps_cart = [
        {"action": "open_url", "input_value": "/inventory.html", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Navigate to product inventory"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#add-to-cart-sauce-labs-backpack", "timeout": 10, "description": "Add Backpack to cart"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#add-to-cart-sauce-labs-bike-light", "timeout": 10, "description": "Add Bike Light to cart"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#add-to-cart-sauce-labs-bolt-t-shirt", "timeout": 10, "description": "Add Bolt T-Shirt to cart"},
        {"action": "assert_text_present", "input_value": "3", "locator_type": "css", "locator_value": ".shopping_cart_badge", "timeout": 10, "description": "Confirm cart counter shows 3"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": ".shopping_cart_link", "timeout": 10, "description": "Open cart page"},
        {"action": "assert_url_contains", "input_value": "/cart.html", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Verify cart URL"},
        {"action": "screenshot", "input_value": "cart-with-items", "locator_type": "css", "locator_value": None, "timeout": 5, "description": "Checkpoint: cart loaded with items"},
    ]

    steps_checkout = [
        {"action": "open_url", "input_value": "/checkout-step-one.html", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Navigate to checkout step 1"},
        {"action": "type_text", "input_value": "Jane", "locator_type": "css", "locator_value": "#first-name", "timeout": 10, "description": "Enter first name"},
        {"action": "type_text", "input_value": "Doe", "locator_type": "css", "locator_value": "#last-name", "timeout": 10, "description": "Enter last name"},
        {"action": "type_text", "input_value": "90210", "locator_type": "css", "locator_value": "#postal-code", "timeout": 10, "description": "Enter postal code"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#continue", "timeout": 10, "description": "Click Continue"},
        {"action": "assert_url_contains", "input_value": "/checkout-step-two.html", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Verify order review page"},
        {"action": "assert_element_visible", "input_value": None, "locator_type": "css", "locator_value": ".summary_total_label", "timeout": 10, "description": "Verify order total is visible"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#finish", "timeout": 10, "description": "Complete order"},
        {"action": "assert_text_present", "input_value": "Thank you", "locator_type": "css", "locator_value": ".complete-header", "timeout": 10, "description": "Verify order confirmation message"},
    ]

    steps_sort = [
        {"action": "open_url", "input_value": "/inventory.html", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Navigate to inventory"},
        {"action": "select_dropdown", "input_value": "Price (low to high)", "locator_type": "css", "locator_value": ".product_sort_container", "timeout": 10, "description": "Sort by price low to high"},
        {"action": "assert_element_visible", "input_value": None, "locator_type": "css", "locator_value": ".inventory_item:first-child .inventory_item_price", "timeout": 10, "description": "Verify sort applied"},
        {"action": "hover", "input_value": None, "locator_type": "css", "locator_value": ".inventory_item:first-child", "timeout": 10, "description": "Hover over first item"},
        {"action": "screenshot", "input_value": "sorted-inventory", "locator_type": "css", "locator_value": None, "timeout": 5, "description": "Checkpoint: sorted product list"},
        {"action": "assert_attribute", "input_value": "product_sort_container", "locator_type": "css", "locator_value": ".product_sort_container", "attribute": "class", "timeout": 10, "description": "Verify sort element present"},
    ]

    # Insert test cases for SauceDemo
    for tc_name, steps, desc, tags, group in [
        ("User Authentication - Valid Credentials", steps_login, "Validates successful auth with standard_user and redirect to dashboard.", ["smoke", "p0", "auth"], "authentication"),
        ("Cart Operations - Multi-Item Addition", steps_cart, "Adds 3 items to cart and validates counter and cart page integrity.", ["cart", "p1", "regression"], "checkout"),
        ("Checkout Flow - Complete Order", steps_checkout, "Full checkout journey: form fill, order review, and confirmation validation.", ["checkout", "p0", "critical"], "checkout"),
        ("Product Catalog - Sort Validation", steps_sort, "Validates product sorting by price (low-to-high) with visual checkpoint.", ["catalog", "p2", "ui"], "catalog"),
    ]:
        execute(
            "INSERT INTO test_cases (name, module, project_id, steps_json, description, tags, group_name, enabled) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
            (tc_name, "SauceDemo E-Commerce", p1_id, json.dumps(steps), desc, json.dumps(tags), group),
        )

    # Test cases for OrangeHRM
    steps_hrm_login = [
        {"action": "open_url", "input_value": "https://opensource-demo.orangehrmlive.com", "locator_type": "css", "locator_value": None, "timeout": 15, "description": "Open OrangeHRM portal"},
        {"action": "type_text", "input_value": "Admin", "locator_type": "css", "locator_value": "input[name='username']", "timeout": 10, "description": "Enter admin username"},
        {"action": "type_text", "input_value": "admin123", "locator_type": "css", "locator_value": "input[name='password']", "timeout": 10, "description": "Enter admin password"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "button[type='submit']", "timeout": 10, "description": "Click Login"},
        {"action": "assert_url_contains", "input_value": "/dashboard", "locator_type": "css", "locator_value": None, "timeout": 15, "description": "Verify dashboard redirect"},
        {"action": "assert_element_visible", "input_value": None, "locator_type": "css", "locator_value": ".oxd-topbar-header-breadcrumb", "timeout": 10, "description": "Confirm admin header visible"},
    ]

    steps_hrm_search = [
        {"action": "open_url", "input_value": "/web/index.php/pim/viewEmployeeList", "locator_type": "css", "locator_value": None, "timeout": 15, "description": "Navigate to employee list"},
        {"action": "type_text", "input_value": "Tim", "locator_type": "css", "locator_value": "input[placeholder='Type for hints...']", "timeout": 10, "description": "Search for employee by name"},
        {"action": "wait", "input_value": "2", "locator_type": "css", "locator_value": None, "timeout": 5, "description": "Wait for search results"},
        {"action": "screenshot", "input_value": "employee-search", "locator_type": "css", "locator_value": None, "timeout": 5, "description": "Checkpoint: search results"},
    ]

    for tc_name, steps, desc, tags, group in [
        ("Admin Login - Valid Credentials", steps_hrm_login, "Validates admin authentication and dashboard redirect on OrangeHRM.", ["smoke", "auth", "p0"], "authentication"),
        ("Employee Directory - Name Search", steps_hrm_search, "Searches employee directory by first name and verifies results display.", ["pim", "search", "p1"], "employees"),
    ]:
        execute(
            "INSERT INTO test_cases (name, module, project_id, steps_json, description, tags, group_name, enabled) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
            (tc_name, "OrangeHRM Portal", p2_id, json.dumps(steps), desc, json.dumps(tags), group),
        )

    # Test cases for DemoQA
    steps_demoqa_forms = [
        {"action": "open_url", "input_value": "https://demoqa.com/text-box", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Open text box form"},
        {"action": "type_text", "input_value": "Alex Johnson", "locator_type": "css", "locator_value": "#userName", "timeout": 10, "description": "Enter full name"},
        {"action": "type_text", "input_value": "alex.j@example.com", "locator_type": "css", "locator_value": "#userEmail", "timeout": 10, "description": "Enter email"},
        {"action": "type_text", "input_value": "123 Main St, Springfield", "locator_type": "css", "locator_value": "#currentAddress", "timeout": 10, "description": "Enter current address"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#submit", "timeout": 10, "description": "Submit form"},
        {"action": "assert_element_visible", "input_value": None, "locator_type": "css", "locator_value": "#output", "timeout": 10, "description": "Verify output section appears"},
        {"action": "assert_text_present", "input_value": "Alex Johnson", "locator_type": "css", "locator_value": "#output", "timeout": 10, "description": "Confirm name in output"},
        {"action": "custom_js", "input_value": "return document.getElementById('output').offsetHeight > 0;", "locator_type": "css", "locator_value": None, "timeout": 5, "description": "JS assertion: output is rendered"},
    ]

    execute(
        "INSERT INTO test_cases (name, module, project_id, steps_json, description, tags, group_name, enabled) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
        ("Text Box Form - Submission & Output Validation", "DemoQA Interactions", p3_id, json.dumps(steps_demoqa_forms), "Fills out the DemoQA text box form and verifies output rendering.", json.dumps(["forms", "ui", "assertions"]), "forms"),
    )

    # Seed AI analyses for FAIL/FLAKY executions (heuristic fallback)
    print("[3/6] Generating AI failure analyses (heuristic fallback)...")
    from ai.analyzer import AIFailureAnalyzer
    analyzer = AIFailureAnalyzer()
    # Find FAIL/FLAKY executions not yet analyzed - up to 20
    fail_execs = fetch_all(
        "SELECT id FROM executions WHERE status IN ('FAIL','FLAKY') AND ai_analysis_id IS NULL LIMIT 20"
    )
    for row in fail_execs:
        try:
            analyzer._heuristic_fallback(row["id"])
        except Exception as e:
            print(f"  Warning: analysis for execution {row['id']}: {e}")

    # Generate multi-format reports
    print("[4/6] Generating multi-format reports (HTML, PDF, JSON, CSV)...")
    with app.app_context():
        from services.report_service import ReportService
        report_svc = ReportService()
        for rtype in ["html", "pdf", "json", "csv"]:
            try:
                report_svc.generate(rtype, limit=50)
                print(f"  Generated {rtype} report")
            except Exception as e:
                print(f"  Note: {rtype} report: {e}")

    # Verify data quality
    print("[5/6] Verifying data quality...")
    total = fetch_one("SELECT COUNT(*) c FROM executions")["c"]
    passed = fetch_one("SELECT COUNT(*) c FROM executions WHERE status='PASS'")["c"]
    failed = fetch_one("SELECT COUNT(*) c FROM executions WHERE status='FAIL'")["c"]
    flaky = fetch_one("SELECT COUNT(*) c FROM executions WHERE status='FLAKY'")["c"]
    ai_count = fetch_one("SELECT COUNT(*) c FROM ai_analyses")["c"]
    projects_count = fetch_one("SELECT COUNT(*) c FROM projects")["c"]
    test_cases_count = fetch_one("SELECT COUNT(*) c FROM test_cases")["c"]
    flaky_hist = fetch_one("SELECT COUNT(*) c FROM flaky_history WHERE classification='FLAKY'")["c"]

    print(f"  Executions: {total} total ({passed} pass / {failed} fail / {flaky} flaky)")
    print(f"  AI analyses: {ai_count}")
    print(f"  Projects: {projects_count}, Test cases: {test_cases_count}")
    print(f"  Flaky tests detected: {flaky_hist}")

    # Get project IDs for screenshot URLs
    saucedemo_proj = fetch_one("SELECT id FROM projects WHERE name = 'SauceDemo E-Commerce'")
    return {
        "saucedemo_id": saucedemo_proj["id"] if saucedemo_proj else 1
    }


def capture_all_screenshots(context: dict):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    port = 5055
    server_url = f"http://127.0.0.1:{port}"

    # Start Flask server in background thread
    print("[6/6] Starting Flask application server...")
    server_thread = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    server_thread.start()
    time.sleep(3)

    # Setup headless Chrome at 1920x1080
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--disable-web-security")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)

    saucedemo_id = context.get("saucedemo_id", 1)

    try:
        print("\n[+] Authenticating into the platform...")
        driver.get(f"{server_url}/login")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("Admin@123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/"))
        time.sleep(1.5)

        # Set dark theme for professional enterprise look
        driver.execute_script(
            "localStorage.setItem('smart-retry-theme','dark');"
            "document.documentElement.setAttribute('data-theme','dark');"
        )
        time.sleep(0.3)

        # Look up an execution with AI analysis and retry attempts for the deep-dive screenshot
        exec_with_analysis = fetch_one(
            "SELECT id FROM executions WHERE ai_analysis_id IS NOT NULL AND attempt_count > 1 LIMIT 1"
        )
        if not exec_with_analysis:
            exec_with_analysis = fetch_one(
                "SELECT id FROM executions WHERE ai_analysis_id IS NOT NULL LIMIT 1"
            )
        exec_detail_id = exec_with_analysis["id"] if exec_with_analysis else 1

        # Look up a FLAKY execution for the flaky verdict page (module must have flaky_history)
        flaky_module_row = fetch_one(
            "SELECT module FROM flaky_history WHERE classification='FLAKY' ORDER BY flaky_score DESC LIMIT 1"
        )
        flaky_domain = flaky_module_row["module"] if flaky_module_row else "cart"

        screenshots_to_take = [
            (
                "01-dashboard-overview.png",
                f"{server_url}/",
                "Real-time analytics dashboard: 8 KPI tiles, Chart.js trend, distribution, retry and flaky charts",
                3.5,  # extra wait for Chart.js animations
            ),
            (
                "02-flaky-test-verdict.png",
                f"{server_url}/run/results/{flaky_domain}",
                "Flaky test verdict: tri-state classification, flip counts, and retry-save scores",
                1.5,
            ),
            (
                "03-projects-management.png",
                f"{server_url}/projects/",
                "Multi-project portfolio: project cards with URLs, tags, test counts, and health",
                1.0,
            ),
            (
                "04-project-detail.png",
                f"{server_url}/projects/{saucedemo_id}",
                "Project detail: test suite orchestration, flaky summary, and recent execution history",
                1.5,
            ),
            (
                "05-visual-test-builder.png",
                f"{server_url}/projects/{saucedemo_id}/tests/new",
                "Visual test builder: 22 step-action selector, locator fields, and step sequencer",
                1.5,
            ),
            (
                "06-execution-history.png",
                f"{server_url}/history/",
                "Execution history: sortable audit log with status badges, attempt counts, and CSV export",
                1.0,
            ),
            (
                "06b-execution-detail.png",
                f"{server_url}/history/{exec_detail_id}",
                "Execution deep-dive: retry timeline, stack trace evidence, and AI failure triage",
                1.5,
            ),
            (
                "07-ai-failure-analysis.png",
                f"{server_url}/ai-analysis/",
                "AI analysis hub: severity KPI tiles, root cause table, model/heuristic badge",
                1.0,
            ),
            (
                "08-realtime-console.png",
                f"{server_url}/console/",
                "Real-time console: live execution event streaming and retry attempt log",
                1.0,
            ),
            (
                "09-reporting-engine.png",
                f"{server_url}/reports/",
                "Enterprise reporting: multi-format report archive (HTML, PDF, JSON, CSV)",
                1.0,
            ),
            (
                "10-settings-configuration.png",
                f"{server_url}/settings/",
                "Platform settings: retry limits, backoff, browser engine, and AI toggle",
                1.0,
            ),
        ]

        for filename, url, label, delay in screenshots_to_take:
            print(f"  [-] Capturing: {filename}")
            print(f"      {label}")
            driver.get(url)

            # If redirected away (e.g. 404 for a results page with no data), log warning
            if driver.current_url != url and "login" in driver.current_url:
                print(f"      WARN: redirected to login (session lost?), skipping")
                continue

            time.sleep(delay)

            # Clean up transient UI elements (toasts, spinners)
            driver.execute_script(
                "document.querySelectorAll('.toast-stack, .toast, .spinner-overlay').forEach(e => e.remove());"
            )
            time.sleep(0.3)

            out_path = DOCS_IMG_DIR / filename
            driver.save_screenshot(str(out_path))
            size_kb = out_path.stat().st_size // 1024
            print(f"      Saved: {filename} ({size_kb} KB)")

        print(f"\n[OK] All {len(screenshots_to_take)} screenshots captured in: {DOCS_IMG_DIR}")

    finally:
        driver.quit()


if __name__ == "__main__":
    print("=" * 70)
    print("Smart Retry & Flaky Test Detector - Screenshot Generator")
    print("=" * 70)
    context = seed_showcase_data()
    capture_all_screenshots(context)
    print("\nDone! All screenshots saved to docs/images/")
