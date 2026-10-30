# Smart Retry & Flaky Test Detection Framework

An enterprise-grade Selenium test automation and observability platform with automatic retries, statistical flaky-test detection, a visual test builder, AI root-cause failure analysis, execution history, a live Flask dashboard, and a REST API.

---

## Key Highlights

- **Dynamic Projects (Any Website):** Not bound to predefined sites or hardcoded dropdowns. Define any project with a name and URL, and build locator-driven step sequences visually.
- **Visual Test Builder (22 Step Types):** Low-code test authoring (navigation, click, type text, select, wait, scroll, hover, key press, switch frame/window, screenshot checkpoints, 6 assertion types, custom JS).
- **Smart Retry Engine:** Configurable retry-with-backoff (`attempts = 1 + max_retries`), preserving every attempt's telemetry to measure true retry-save ROI.
- **Statistical Flaky Test Detection:** Evaluates sliding execution windows using flip-rate and retry-save frequency to classify tests as `STABLE`, `FLAKY`, or `CHRONIC_FAILURE`.
- **AI Failure Analysis (Ollama Llama 3.1):** Automatically triages failed tests into root causes, severity ratings (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and Selenium code fixes, with a rule-based heuristic fallback if Ollama is offline.
- **Real-Time Analytics Dashboard:** 8 KPI tiles, 4 interactive Chart.js visualizations (dark/light theme reactive), and 30-second live background polling.
- **Multi-Format Reporting:** Generates self-contained HTML (with base64 screenshots), PDF (via ReportLab), JSON, and CSV reports.
- **Full Automated Test Suite:** 25 pytest integration and unit tests covering retry logic, flaky algorithms, step execution, and API endpoints.

---

## Flaky Test Detection & Scoring Algorithm

Rather than treating a test as simply "pass or fail", the framework evaluates test stability over a configurable sliding window of recent executions (default: last 10 runs):

### 1. Flip Rate (70% weight)
Measures how often consecutive runs change state between passing and failing:
$$\text{Flip Rate} = \frac{\text{flip\_count}}{\max(\text{total\_runs} - 1, 1)}$$

*(A test alternating PASS $\to$ FAIL $\to$ PASS $\to$ FAIL has a flip rate of 1.0)*

### 2. Retry-Save Rate (30% weight)
Measures tests that eventually pass, but only after consuming retry attempts:
$$\text{Retry Save Rate} = \frac{\text{retry\_saves}}{\text{total\_runs}}$$

### 3. Composite Flaky Score (0 to 100%)
$$\text{Flaky Score} = (\text{Flip Rate} \times 0.70 + \text{Retry Save Rate} \times 0.30) \times 100$$

### 4. Tri-State Classification
- **`STABLE`**: Flaky score is below threshold (default $< 20\%$) and behavior is consistent.
- **`FLAKY`**: State flips or repeated retry-saves meet or exceed threshold ($\ge 20\%$).
- **`CHRONIC_FAILURE`**: 100% failure rate over 3 or more consecutive runs (distinguishes outright broken tests from intermittent flakiness).

---

## Analytics & Dashboard Architecture

The dashboard at `/` is powered by SQL aggregations in `services/analytics_service.py`:

- **8 Executive KPI Tiles:**
  - **Total Executions:** Complete history counter.
  - **Passed Tests & Pass Rate:** Overall pass percentage.
  - **Failed Tests:** Hard failures needing immediate attention.
  - **Flaky Tests:** Intermittent tests flagged for quarantine/triage.
  - **Retry Success Rate:** Percentage of retried tests saved by the retry engine.
  - **Avg Execution Time:** Test duration in seconds and milliseconds.
  - **AI Analyses Run:** Total AI/heuristic root cause diagnoses generated.
  - **Last Execution:** Real-time indicator of the latest test run.
- **Interactive Visualizations (Chart.js):**
  - **Execution Trend (Line Chart):** 14-day timeline tracking Pass, Fail, and Flaky counts.
  - **Status Distribution (Doughnut Chart):** All-time outcome proportion breakdown.
  - **Retry Trend (Bar Chart):** Daily average retry attempts per test run.
  - **Top Flaky & Failed Tests:** Ranked list with proportional progress indicators.

---

## Visual Test Builder & Step Executor

Located in `core/step_definitions.py` and `core/step_executor.py`:
- Test cases are JSON-serialized lists of step actions executed against any Selenium WebDriver.
- **22 Dynamic Actions:** `open_url` (supports relative URLs auto-joined with project URL), `click`, `double_click`, `right_click`, `type_text`, `clear`, `select_dropdown`, `check_checkbox`, `wait`, `scroll_to`, `hover`, `press_keys`, `switch_frame`, `switch_window`, `screenshot` (checkpoint), `assert_url_contains`, `assert_title_contains`, `assert_text_present`, `assert_element_visible`, `assert_element_exists`, `assert_attribute`, and `custom_js`.
- **Security:** Arbitrary host-side Python execution is deliberately omitted to prevent remote-code execution. JavaScript is run strictly inside the browser sandbox via `driver.execute_script`.

---

## Quick Start

### 1. Clone & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/nayanaastakar/Smart-Retry-Flaky-Test-Detector.git
cd Smart-Retry-Flaky-Test-Detector

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` (already created by default):
```bash
cp .env.example .env
```

### 3. Initialize Database & Seed Defaults
Initializes the SQLite schema, runs migrations, seeds default website profiles, settings, and default admin user:
```bash
python app.py --init-db
```

### 4. (Optional) Generate Demo Execution Data
Populates the database with 180 simulated test executions across 12 realistic test profiles to immediately experience the dashboard, flaky scores, and trend charts:
```bash
python -m utils.generate_demo_data
```

### 5. Start the Application
```bash
python app.py
```
Open **http://localhost:5000** in your browser and log in:
- **Username:** `admin`
- **Password:** `Admin@123`

---

## Running the Automated Test Suite

The project includes 25 unit and integration tests covering the retry engine, flaky detection algorithm, step execution, evidence collection, reporting, and Flask API routes:

```bash
# Run full test suite
pytest

# Run tests with verbose output
pytest -v
```

All 25 tests run cleanly without external dependencies or live network connections:
```text
============================= 25 passed in 7.23s ==============================
```

---

## REST API Reference

All API routes return JSON and are registered under `/api/v1`:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/health` | `GET` | Health status check (`{"status": "ok"}`) |
| `/api/v1/analytics/summary` | `GET` | Executive metrics (total, passed, pass rate, retry success rate, avg duration) |
| `/api/v1/analytics/status-distribution` | `GET` | Counts for `PASS`, `FAIL`, `FLAKY`, and `SKIPPED` |
| `/api/v1/analytics/execution-trend` | `GET` | Daily 14-day buckets (`?days=14`) |
| `/api/v1/analytics/retry-trend` | `GET` | Average daily retry attempts |
| `/api/v1/flaky-tests` | `GET` | Ranked list of flaky tests (`?limit=20`) |
| `/api/v1/flaky-tests/evaluate` | `POST` | Triggers complete re-evaluation of test flakiness |
| `/api/v1/history` | `GET` | Raw execution history list (`?limit=50`) |
| `/api/v1/history/<id>` | `GET` | Detailed record of a specific execution |
| `/api/v1/settings` | `GET` | Current application configuration key-value map |
| `/api/v1/reports` | `GET` | List of generated reports |

---

## Project Structure

```text
smart-retry-framework/
├── ai/
│   ├── analyzer.py            # AI failure analyzer with heuristic fallback
│   ├── ollama_client.py       # Local Ollama HTTP client (Llama 3.1)
│   └── prompts.py             # Prompt templates for root cause diagnosis
├── core/
│   ├── driver_factory.py      # Selenium driver factory (Chrome/Edge/Firefox + Selenium Manager)
│   ├── evidence_collector.py  # Screenshots, console logs, stack traces, browser/OS capture
│   ├── flaky_detector.py      # Flip-rate and retry-save scoring engine (STABLE/FLAKY/CHRONIC)
│   ├── generic_test_suite.py  # URL-agnostic smoke check battery for Quick Run
│   ├── job_manager.py         # Threaded background job manager with live polling
│   ├── project_runner.py      # Test execution orchestrator
│   ├── retry_engine.py        # Smart retry engine with exponential backoff & attempt logging
│   ├── step_definitions.py    # Metadata for 22 visual step builder actions
│   └── step_executor.py       # Runtime step interpreter against Selenium WebDriver
├── database/
│   ├── db_manager.py          # SQLite database connection & migrations
│   └── seed.py                # Initial database seeder (profiles, admin, settings)
├── routes/
│   ├── ai_analysis_routes.py  # AI browsing & bulk analysis
│   ├── api_routes.py          # REST API (/api/v1/...)
│   ├── auth_routes.py         # Login, logout, session guards
│   ├── console_routes.py      # Real-time console log tailing
│   ├── dashboard_routes.py    # Main analytics dashboard
│   ├── history_routes.py      # Execution history, filters, screenshot serving, CSV export
│   ├── profile_routes.py      # User profile & password management
│   ├── projects_routes.py     # Projects CRUD & test execution
│   ├── reports_routes.py      # Report generation & downloads
│   ├── run_routes.py          # Quick Run execution & live progress
│   ├── settings_routes.py     # Runtime configuration settings
│   ├── test_cases_routes.py   # Test builder, duplication, toggle, edit
│   └── website_profiles_routes.py # Legacy profile management
├── services/
│   ├── analytics_service.py   # SQL aggregation layer for dashboard metrics & charts
│   ├── auth_service.py        # User authentication & PBKDF2 password hashing
│   ├── report_service.py      # Multi-format report generator (HTML, PDF, JSON, CSV)
│   └── settings_service.py    # Single source of truth for runtime database settings
├── static/
│   ├── css/main.css           # Modern dark/light responsive styling
│   └── js/
│       ├── app.js             # Toasts, command palette (Ctrl+K), auto-refresh
│       ├── dashboard_charts.js# Chart.js visualizations
│       └── theme.js           # Instant dark/light theme switching
├── templates/                 # Jinja2 templates for all views
├── tests/                     # 25 automated pytest tests
├── utils/
│   └── generate_demo_data.py  # Generates realistic simulated execution history
├── app.py                     # Flask application entry point
├── config.py                  # Central configuration
├── pytest.ini                 # Pytest configuration
└── requirements.txt           # Python dependencies
```

---

## License

This project is licensed under the MIT License.
