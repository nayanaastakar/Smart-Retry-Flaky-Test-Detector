# Smart Retry & Flaky Test Detector

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Selenium](https://img.shields.io/badge/selenium-4.23.1-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0.3-red.svg)
![Ollama](https://img.shields.io/badge/AI-Ollama%20%7C%20Llama3-purple)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

An intelligent, AI-powered Selenium automation testing framework equipped with a robust web dashboard, smart retry mechanisms, flaky test detection, and automated root-cause analysis using LLMs (Ollama).

## 🌟 Overview

The **Smart Retry & Flaky Test Detector** takes traditional Selenium testing to the next level by introducing intelligence and resilience. Instead of tests failing blindly, the framework analyzes failures, determines if a test is flaky, captures rich evidence, and uses AI to recommend fixes. 

All of this is manageable from a sleek, dark-themed Flask web dashboard.

## 🚀 Key Features by Module

### Module 1: Core Framework & Web Dashboard
- **Flask Web Interface:** Modern, responsive dashboard to run tests and view results.
- **Selenium Integration:** Automatic ChromeDriver management (`webdriver-manager`).
- **Page Object Model (POM):** Clean and maintainable test architecture.

### Module 2: Smart Retry Engine
- Automatically retries failing tests based on configurable thresholds.
- Reduces false negatives caused by temporary network glitches or slow page loads.

### Module 3: Flaky Test Detection
- Classifies test results into **PASS**, **FAILURE**, or **FLAKY**.
- If a test fails initially but passes on a retry, it is flagged as FLAKY to warn developers of instability.

### Module 4: Evidence Collection
- **Screenshots:** Automatically captures screenshots on test failures or flakiness.
- **Browser Logs:** Extracts browser console logs to provide deep technical context for the failure.

### Module 5: HTML Report Generation
- Generates detailed, standalone HTML reports for every test run.
- Reports include execution time, status breakdowns, and embedded screenshots.

### Module 6: AI-Powered Failure Analysis
- Integrates with local LLMs via **Ollama** (e.g., Llama 3.1).
- Feeds exception traces, browser logs, and test context to the AI.
- Returns actionable insights including **Root Cause**, **Code Recommendations**, and **Prevention Strategies**.

### Module 7: Analytics & Execution History
- Tracks historical test runs and aggregates statistics.
- Visualizes pass/fail/flaky trends over time using interactive charts.
- Stores historical evidence and reports for auditing.

## 🏗️ Project Structure

```
Smart-Retry-Flaky-Test-Detector/
│
├── ai/                      # AI analysis & Ollama client (Module 6)
├── config/                  # Global configuration & website profiles
├── core/                    # Core engines (Driver, Retry, Flaky, Evidence)
├── dashboard/               # Analytics and history management (Module 7)
├── models/                  # Data models (Evidence, AI Analysis)
├── pages/                   # Page Object Models
├── tests/                   # Pytest test suites
├── static/                  # CSS/JS assets for the dashboard
├── templates/               # HTML templates for Flask UI
│
├── app.py                   # Main Flask Application
├── main.py                  # CLI Entry point (alternative to web dashboard)
└── requirements.txt         # Project dependencies
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Google Chrome (latest)
- [Ollama](https://ollama.ai/) installed and running locally (for AI Analysis)
- `llama3.1` model pulled in Ollama (`ollama run llama3.1`)

### 1. Clone & Install
```bash
git clone https://github.com/nayanaastakar/Smart-Retry-Flaky-Test-Detector.git
cd Smart-Retry-Flaky-Test-Detector
pip install -r requirements.txt
```

### 2. Configure AI (Optional but Recommended)
Ensure Ollama is running on your machine:
```bash
ollama serve
```

### 3. Start the Dashboard
```bash
python app.py
```
Open your browser and navigate to: **http://127.0.0.1:5000**

## ⚙️ Configuration

Configuration can be managed directly through the Web UI (Settings tab) or via `config/config.py`:
- `MAX_RETRIES`: Number of times to retry a failed test.
- `HEADLESS_MODE`: Run Chrome without a visible UI.
- `ENABLE_AI`: Toggle Ollama AI analysis on/off.
- `IMPLICIT_WAIT` / `EXPLICIT_WAIT`: Timeout configurations.

## 💻 Usage

1. Open the Dashboard (`http://127.0.0.1:5000`).
2. Navigate to **Run Tests**.
3. Select a website profile (e.g., SauceDemo) and click **Start Test Run**.
4. The framework will execute the tests, apply retry logic if failures occur, and capture evidence.
5. If a test fails, the AI Analyzer will automatically generate a root-cause report.
6. Review the results, screenshots, and AI insights on the **Result** page.
7. Navigate to the **Dashboard/Analytics** page to view your historical trends.

## 📄 License
This project is licensed under the MIT License.
