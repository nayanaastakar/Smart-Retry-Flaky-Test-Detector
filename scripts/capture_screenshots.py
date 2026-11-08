"""
scripts/capture_screenshots.py
==============================
Generates high-resolution screenshots of the Smart Retry & Flaky Test Detection
Framework web interface for the GitHub README documentation, modeled after KubeSight.
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

from app import app
from database.db_manager import init_db, execute, fetch_one, fetch_all
from database.seed import run_all as seed_all
from utils.generate_demo_data import generate as generate_demo_data
from services.report_service import ReportService
from ai.analyzer import AIFailureAnalyzer

DOCS_IMG_DIR = BASE_DIR / "docs" / "images"
DOCS_IMG_DIR.mkdir(parents=True, exist_ok=True)


def seed_rich_showcase_data():
    """Populates realistic data across projects, test cases, AI analyses, and reports."""
    print("[1/5] Initializing database and default seeds...")
    init_db()
    seed_all()

    print("[2/5] Generating execution history and flaky detection profiles...")
    generate_demo_data(num_runs_per_test=12)

    print("[3/5] Seeding showcase projects and visual test builder steps...")
    # Project 1: SauceDemo
    p1 = fetch_one("SELECT id FROM projects WHERE name = 'SauceDemo E-Commerce'")
    if not p1:
        p1_id = execute(
            """INSERT INTO projects (name, url, browser, tags, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (
                "SauceDemo E-Commerce",
                "https://www.saucedemo.com",
                "chrome",
                json.dumps(["production", "e-commerce", "smoke", "checkout"]),
                "Primary end-to-end regression suite covering catalog browsing, cart operations, and checkout validation.",
            ),
        )
    else:
        p1_id = p1["id"]

    # Project 2: OrangeHRM
    p2 = fetch_one("SELECT id FROM projects WHERE name = 'OrangeHRM Portal'")
    if not p2:
        p2_id = execute(
            """INSERT INTO projects (name, url, browser, tags, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (
                "OrangeHRM Portal",
                "https://opensource-demo.orangehrmlive.com",
                "chrome",
                json.dumps(["internal", "hr", "auth", "rbac"]),
                "Enterprise HR workflow covering administrative logins, role management, and employee records.",
            ),
        )
    else:
        p2_id = p2["id"]

    # Test cases for SauceDemo
    steps_login = [
        {"action": "open_url", "input_value": "https://www.saucedemo.com", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Open SauceDemo home page"},
        {"action": "type_text", "input_value": "standard_user", "locator_type": "css", "locator_value": "#user-name", "timeout": 10, "description": "Enter username"},
        {"action": "type_text", "input_value": "secret_sauce", "locator_type": "css", "locator_value": "#password", "timeout": 10, "description": "Enter password"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#login-button", "timeout": 10, "description": "Click Login button"},
        {"action": "assert_url_contains", "input_value": "/inventory.html", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Verify redirect to inventory"},
        {"action": "assert_element_visible", "input_value": None, "locator_type": "css", "locator_value": ".inventory_list", "timeout": 10, "description": "Ensure product grid is loaded"},
    ]

    steps_cart = [
        {"action": "open_url", "input_value": "/inventory.html", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Navigate to inventory"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#add-to-cart-sauce-labs-backpack", "timeout": 10, "description": "Add backpack to cart"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": "#add-to-cart-sauce-labs-bike-light", "timeout": 10, "description": "Add bike light to cart"},
        {"action": "assert_text_present", "input_value": "2", "locator_type": "css", "locator_value": ".shopping_cart_badge", "timeout": 10, "description": "Confirm cart counter shows 2"},
        {"action": "click", "input_value": None, "locator_type": "css", "locator_value": ".shopping_cart_link", "timeout": 10, "description": "Open cart page"},
        {"action": "assert_url_contains", "input_value": "/cart.html", "locator_type": "css", "locator_value": None, "timeout": 10, "description": "Verify cart URL"},
    ]

    existing_tc1 = fetch_one("SELECT id FROM test_cases WHERE name = 'User Authentication - Valid Credentials'")
    if not existing_tc1:
        execute(
            """INSERT INTO test_cases (name, module, project_id, steps_json, description, tags, group_name, enabled)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                "User Authentication - Valid Credentials",
                "SauceDemo E-Commerce",
                p1_id,
                json.dumps(steps_login),
                "Validates successful authentication with standard user credentials and redirect to dashboard.",
                json.dumps(["smoke", "p0", "auth"]),
                "authentication",
            ),
        )

    existing_tc2 = fetch_one("SELECT id FROM test_cases WHERE name = 'Cart Operations - Multi-Item Addition'")
    if not existing_tc2:
        execute(
            """INSERT INTO test_cases (name, module, project_id, steps_json, description, tags, group_name, enabled)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                "Cart Operations - Multi-Item Addition",
                "SauceDemo E-Commerce",
                p1_id,
                json.dumps(steps_cart),
                "Adds multiple items to cart and asserts counter and cart page integrity.",
                json.dumps(["cart", "p1"]),
                "checkout",
            ),
        )

    # Seed rich AI analyses directly using heuristic fallback (instant)
    print("[4/5] Generating AI failure analyses...")
    analyzer = AIFailureAnalyzer()
    fail_execs = fetch_all("SELECT id FROM executions WHERE status IN ('FAIL', 'FLAKY') AND ai_analysis_id IS NULL LIMIT 8")
    for row in fail_execs:
        try:
            analyzer._heuristic_fallback(row["id"])
        except Exception:
            pass

    # Generate sample reports
    print("[5/5] Generating multi-format reports (HTML, PDF, JSON, CSV)...")
    with app.app_context():
        report_svc = ReportService()
        for rtype in ["html", "pdf", "json", "csv"]:
            try:
                report_svc.generate(rtype, limit=50)
            except Exception as e:
                print(f"  Note: {rtype} report generation: {e}")


def capture_all_screenshots():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    port = 5055
    server_url = f"http://127.0.0.1:{port}"

    # Start Flask server in background thread
    server_thread = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    server_thread.start()
    time.sleep(2)

    # Setup headless Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--force-device-scale-factor=1")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)

    try:
        print("\n[+] Logging into web platform...")
        driver.get(f"{server_url}/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("Admin@123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1.5)

        # Ensure theme is dark for modern enterprise look
        driver.execute_script("localStorage.setItem('smart-retry-theme', 'dark'); document.documentElement.setAttribute('data-theme', 'dark');")
        time.sleep(0.5)

        screenshots_to_take = [
            (
                "01-dashboard-overview.png",
                f"{server_url}/",
                "Overview Dashboard with 8 KPI tiles and live Chart.js charts",
                2.5,  # wait for charts to animate
            ),
            (
                "02-flaky-test-verdict.png",
                f"{server_url}/run/results/cart",
                "Flaky test stability verdict with per-check flaky score and flip counts",
                1.0,
            ),
            (
                "03-projects-management.png",
                f"{server_url}/projects/",
                "Projects management interface for generalized web automation",
                1.0,
            ),
            (
                "04-project-detail.png",
                f"{server_url}/projects/1",
                "Project dashboard with test cases, flaky summary, and recent runs",
                1.0,
            ),
            (
                "05-visual-test-builder.png",
                f"{server_url}/projects/1/tests/new",
                "Visual Test Builder with 22 dynamic step actions, locators, and timeouts",
                1.5,
            ),
            (
                "06-execution-history.png",
                f"{server_url}/history/",
                "Execution History with search, status filters, duration, and CSV export",
                1.0,
            ),
            (
                "07-ai-failure-analysis.png",
                f"{server_url}/ai-analysis/",
                "AI Failure Analysis dashboard with severity breakdown and root causes",
                1.0,
            ),
            (
                "08-realtime-console.png",
                f"{server_url}/console/",
                "Real-Time Console streaming live retry attempts and execution events",
                1.0,
            ),
            (
                "09-reporting-engine.png",
                f"{server_url}/reports/",
                "Reporting Engine with downloadable HTML, PDF, JSON, and CSV reports",
                1.0,
            ),
            (
                "10-settings-configuration.png",
                f"{server_url}/settings/",
                "Runtime settings for retries, exponential backoff, browser, and AI switch",
                1.0,
            ),
        ]

        # Look up an execution ID with AI analysis for detailed forensic view
        exec_row = fetch_one("SELECT id FROM executions WHERE ai_analysis_id IS NOT NULL LIMIT 1")
        if exec_row:
            screenshots_to_take.insert(6, (
                "06b-execution-detail.png",
                f"{server_url}/history/{exec_row['id']}",
                "Execution Detail with retry timeline, stack trace, and AI diagnosis",
                1.0,
            ))

        for filename, url, label, delay in screenshots_to_take:
            print(f"  [-] Capturing: {filename} ({label})...")
            driver.get(url)
            time.sleep(delay)
            # Remove any transient toasts for a clean screenshot
            driver.execute_script("document.querySelectorAll('.toast-stack, .toast').forEach(e => e.remove());")
            time.sleep(0.2)
            out_path = DOCS_IMG_DIR / filename
            driver.save_screenshot(str(out_path))
            print(f"     Saved: {out_path} ({out_path.stat().st_size // 1024} KB)")

        print(f"\n[OK] All {len(screenshots_to_take)} screenshots captured successfully in: {DOCS_IMG_DIR}")

    finally:
        driver.quit()


if __name__ == "__main__":
    seed_rich_showcase_data()
    capture_all_screenshots()
