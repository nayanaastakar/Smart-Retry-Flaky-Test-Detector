# Sample Output Examples

## Console Output Example

### Test Execution Console Output
```
================================================================================
Smart Retry & Flaky Test Detector
================================================================================

2026-06-29 21:41:00 - INFO - Starting Test Execution
2026-06-29 21:41:00 - INFO - WebDriver initialized successfully
2026-06-29 21:41:00 - INFO - Navigated to: https://www.saucedemo.com

================================================================================
TEST STARTED: test_successful_login
================================================================================
Timestamp: 2026-06-29 21:41:05
================================================================================
2026-06-29 21:41:05 - INFO - Attempt 1/4 for test: test_successful_login
2026-06-29 21:41:06 - INFO - Entered username: standard_user
2026-06-29 21:41:06 - INFO - Entered password
2026-06-29 21:41:06 - INFO - Clicked login button
2026-06-29 21:41:07 - INFO - TEST PASSED: test_successful_login

================================================================================
TEST FINISHED: test_successful_login
================================================================================
Status: PASS
Timestamp: 2026-06-29 21:41:07
Duration: 2.15 seconds
================================================================================

================================================================================
TEST STARTED: test_locked_out_user
================================================================================
Timestamp: 2026-06-29 21:41:07
================================================================================
2026-06-29 21:41:07 - INFO - Attempt 1/4 for test: test_locked_out_user
2026-06-29 21:41:07 - INFO - Entered username: locked_out_user
2026-06-29 21:41:07 - INFO - Entered password
2026-06-29 21:41:07 - INFO - Clicked login button
2026-06-29 21:41:08 - ERROR - TEST FAILED: test_locked_out_user
2026-06-29 21:41:08 - ERROR - Exception Type: AssertionError
2026-06-29 21:41:08 - ERROR - Exception Message: Locked out user should not be able to login
2026-06-29 21:41:08 - WARNING - RETRY ATTEMPT 1/3 for test: test_locked_out_user
2026-06-29 21:41:10 - INFO - Attempt 2/4 for test: test_locked_out_user
2026-06-29 21:41:10 - INFO - Entered username: locked_out_user
2026-06-29 21:41:10 - INFO - Entered password
2026-06-29 21:41:10 - INFO - Clicked login button
2026-06-29 21:41:11 - ERROR - TEST FAILED: test_locked_out_user
2026-06-29 21:41:11 - WARNING - RETRY ATTEMPT 2/3 for test: test_locked_out_user
2026-06-29 21:41:13 - INFO - Attempt 3/4 for test: test_locked_out_user
2026-06-29 21:41:13 - INFO - Entered username: locked_out_user
2026-06-29 21:41:13 - INFO - Entered password
2026-06-29 21:41:13 - INFO - Clicked login button
2026-06-29 21:41:14 - ERROR - TEST FAILED: test_locked_out_user
2026-06-29 21:41:14 - INFO - Screenshot saved for test 'test_locked_out_user': screenshots\test_locked_out_user_failure_20260629_214114.png
2026-06-29 21:41:14 - INFO - Console logs saved for test 'test_locked_out_user': logs\test_locked_out_user_console_20260629_214114.txt

================================================================================
TEST FINISHED: test_locked_out_user
================================================================================
Status: FAILURE
Timestamp: 2026-06-29 21:41:14
Duration: 7.23 seconds
================================================================================

================================================================================
TEST STARTED: test_performance_glitch_user
================================================================================
Timestamp: 2026-06-29 21:41:14
================================================================================
2026-06-29 21:41:14 - INFO - Attempt 1/4 for test: test_performance_glitch_user
2026-06-29 21:41:14 - INFO - Entered username: performance_glitch_user
2026-06-29 21:41:14 - INFO - Entered password
2026-06-29 21:41:14 - INFO - Clicked login button
2026-06-29 21:41:16 - ERROR - TEST FAILED: test_performance_glitch_user
2026-06-29 21:41:16 - ERROR - Exception Type: TimeoutException
2026-06-29 21:41:16 - ERROR - Exception Message: Element not interactable
2026-06-29 21:41:16 - WARNING - RETRY ATTEMPT 1/3 for test: test_performance_glitch_user
2026-06-29 21:41:18 - INFO - Attempt 2/4 for test: test_performance_glitch_user
2026-06-29 21:41:18 - INFO - Entered username: performance_glitch_user
2026-06-29 21:41:18 - INFO - Entered password
2026-06-29 21:41:18 - INFO - Clicked login button
2026-06-29 21:41:19 - INFO - TEST PASSED: test_performance_glitch_user
2026-06-29 21:41:19 - WARNING - FLAKY TEST DETECTED: test_performance_glitch_user
2026-06-29 21:41:19 - WARNING - Test passed after 1 retry attempts
2026-06-29 21:41:19 - INFO - AI Analysis started for test: test_performance_glitch_user
2026-06-29 21:41:24 - INFO - AI Analysis completed for test: test_performance_glitch_user
2026-06-29 21:41:24 - INFO - Classification: Timeout Issue
2026-06-29 21:41:24 - INFO - Root Cause: Element loaded slowly on first attempt
2026-06-29 21:41:24 - INFO - Confidence Score: 0.9

================================================================================
TEST FINISHED: test_performance_glitch_user
================================================================================
Status: FLAKY
Timestamp: 2026-06-29 21:41:24
Duration: 5.08 seconds
================================================================================

================================================================================
Pipeline Execution Summary
================================================================================
Total Tests: 3
Passed: 1
Failed: 1
Flaky: 1
Report: reports\test_report_20260629_214124.html
================================================================================

Execution Completed
================================================================================
```

## Log File Example

### test_execution.log
```
2026-06-29 21:41:00 - TestLogger - INFO - WebDriver initialized successfully
2026-06-29 21:41:00 - TestLogger - INFO - Navigated to: https://www.saucedemo.com
2026-06-29 21:41:05 - TestLogger - INFO - ================================================================================
2026-06-29 21:41:05 - TestLogger - INFO - TEST STARTED: test_successful_login
2026-06-29 21:41:05 - TestLogger - INFO - ================================================================================
2026-06-29 21:41:05 - TestLogger - INFO - Timestamp: 2026-06-29 21:41:05
2026-06-29 21:41:05 - TestLogger - INFO - ================================================================================
2026-06-29 21:41:05 - TestLogger - INFO - Attempt 1/4 for test: test_successful_login
2026-06-29 21:41:06 - TestLogger - INFO - Entered username: standard_user
2026-06-29 21:41:06 - TestLogger - INFO - Entered password
2026-06-29 21:41:06 - TestLogger - INFO - Clicked login button
2026-06-29 21:41:07 - TestLogger - INFO - TEST PASSED: test_successful_login
2026-06-29 21:41:07 - TestLogger - INFO - ================================================================================
2026-06-29 21:41:07 - TestLogger - INFO - TEST FINISHED: test_successful_login
2026-06-29 21:41:07 - TestLogger - INFO - ================================================================================
2026-06-29 21:41:07 - TestLogger - INFO - Status: PASS
2026-06-29 21:41:07 - TestLogger - INFO - Timestamp: 2026-06-29 21:41:07
2026-06-29 21:41:07 - TestLogger - INFO - Duration: 2.15 seconds
2026-06-29 21:41:07 - TestLogger - INFO - ================================================================================
2026-06-29 21:41:07 - TestLogger - INFO - Attempt 1/4 for test: test_locked_out_user
2026-06-29 21:41:08 - TestLogger - ERROR - TEST FAILED: test_locked_out_user
2026-06-29 21:41:08 - TestLogger - ERROR - Exception Type: AssertionError
2026-06-29 21:41:08 - TestLogger - ERROR - Exception Message: Locked out user should not be able to login
2026-06-29 21:41:08 - TestLogger - WARNING - RETRY ATTEMPT 1/3 for test: test_locked_out_user
2026-06-29 21:41:14 - TestLogger - INFO - Screenshot saved for test 'test_locked_out_user': screenshots\test_locked_out_user_failure_20260629_214114.png
2026-06-29 21:41:14 - TestLogger - INFO - Console logs saved for test 'test_locked_out_user': logs\test_locked_out_user_console_20260629_214114.txt
2026-06-29 21:41:19 - TestLogger - WARNING - FLAKY TEST DETECTED: test_performance_glitch_user
2026-06-29 21:41:19 - TestLogger - WARNING - Test passed after 1 retry attempts
2026-06-29 21:41:19 - TestLogger - INFO - AI Analysis started for test: test_performance_glitch_user
2026-06-29 21:41:24 - TestLogger - INFO - AI Analysis completed for test: test_performance_glitch_user
2026-06-29 21:41:24 - TestLogger - INFO - Classification: Timeout Issue
2026-06-29 21:41:24 - TestLogger - INFO - Root Cause: Element loaded slowly on first attempt
2026-06-29 21:41:24 - TestLogger - INFO - Confidence Score: 0.9
```

## Console Log File Example

### test_locked_out_user_console_20260629_214114.txt
```
================================================================================
BROWSER CONSOLE LOGS
================================================================================
Total Entries: 3
================================================================================

Entry #1
Timestamp: 2026-06-29 21:41:07
Level: WARNING
Source: javascript
Message: This page uses the non standard property "zoom". Consider using Math.clamp() instead.

Entry #2
Timestamp: 2026-06-29 21:41:08
Level: ERROR
Source: javascript
Message: Epic sadface: Username and password do not match any user in this service

Entry #3
Timestamp: 2026-06-29 21:41:08
Level: INFO
Source: network
Message: POST https://www.saucedemo.com/api/login 401 (Unauthorized)
```

## AI Analysis Response Example

### OpenAI Analysis Response
```json
{
  "classification": "Timeout Issue",
  "root_cause": "Element loaded slowly on first attempt due to performance glitch",
  "why_it_happened": "The performance_glitch_user account simulates slow page loading, causing the login button to not be immediately interactable. This is a timing issue that resolves on retry.",
  "suggested_fix": "Increase explicit wait timeout for the login button or use WebDriverWait with element_to_be_clickable condition. Consider adding a retry mechanism for performance-sensitive tests.",
  "severity": "Medium",
  "confidence_score": 0.9,
  "best_practices": [
    "Use explicit waits instead of implicit waits for better control",
    "Add retry mechanisms for tests that are known to have performance issues",
    "Monitor page load times and adjust timeouts accordingly",
    "Use stable locators that don't depend on timing"
  ],
  "is_flaky": true,
  "retry_recommendation": true
}
```

### Ollama Analysis Response
```json
{
  "classification": "Timeout Issue",
  "root_cause": "Performance glitch causing slow element loading",
  "why_it_happened": "The test uses performance_glitch_user which intentionally slows down page response time, causing the element to not be immediately available for interaction.",
  "suggested_fix": "Implement WebDriverWait with expected_conditions.element_to_be_clickable() and increase timeout to 15 seconds. Alternatively, add retry logic for this specific test case.",
  "severity": "Medium",
  "confidence_score": 0.85,
  "best_practices": [
    "Always use explicit waits for dynamic elements",
    "Configure appropriate timeouts based on application performance",
    "Implement retry logic for known flaky scenarios",
    "Monitor and optimize application performance"
  ]
}
```

## HTML Report Structure Example

### Dashboard Section
```html
<div class="dashboard">
    <div class="metric-card pass">
        <div class="metric-value">1</div>
        <div class="metric-label">Passed</div>
    </div>
    <div class="metric-card fail">
        <div class="metric-value">1</div>
        <div class="metric-label">Failed</div>
    </div>
    <div class="metric-card flaky">
        <div class="metric-value">1</div>
        <div class="metric-label">Flaky</div>
    </div>
    <div class="metric-card info">
        <div class="metric-value">3</div>
        <div class="metric-label">Total Tests</div>
    </div>
    <div class="metric-card info">
        <div class="metric-value">33.33%</div>
        <div class="metric-label">Pass Rate</div>
    </div>
</div>
```

### Test Summary Table
```html
<table>
    <thead>
        <tr>
            <th>#</th>
            <th>Test Name</th>
            <th>Status</th>
            <th>Attempts</th>
            <th>Duration</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>test_successful_login</td>
            <td><span class="status-pass">PASS</span></td>
            <td>1</td>
            <td>2.15s</td>
            <td><button class="toggle-btn">View Details</button></td>
        </tr>
        <tr>
            <td>2</td>
            <td>test_locked_out_user</td>
            <td><span class="status-fail">FAILURE</span></td>
            <td>3</td>
            <td>7.23s</td>
            <td><button class="toggle-btn">View Details</button></td>
        </tr>
        <tr>
            <td>3</td>
            <td>test_performance_glitch_user</td>
            <td><span class="status-flaky">FLAKY</span></td>
            <td>2</td>
            <td>5.08s</td>
            <td><button class="toggle-btn">View Details</button></td>
        </tr>
    </tbody>
</table>
```

### Detailed Test Result Section
```html
<div class="test-details" id="details-1">
    <h3>test_performance_glitch_user</h3>
    <p><strong>Status:</strong> FLAKY</p>
    <p><strong>Attempts:</strong> 2</p>
    <p><strong>Duration:</strong> 5.08s</p>
    
    <h4>Exceptions</h4>
    <div class="console-logs">
        TimeoutException: Element not interactable
    </div>
    
    <h4>Screenshot</h4>
    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..." class="screenshot" alt="Failure Screenshot">
    
    <h4>Console Logs</h4>
    <div class="console-logs">
        Warning: Slow page load detected
        Error: Element not interactable
    </div>
    
    <h4>AI Analysis</h4>
    <div class="ai-analysis">
        <p><strong>Classification:</strong> Timeout Issue</p>
        <p><strong>Root Cause:</strong> Element loaded slowly on first attempt</p>
        <p><strong>Suggested Fix:</strong> Increase explicit wait timeout</p>
        <p><strong>Confidence:</strong> 0.9</p>
    </div>
</div>
```

## PyTest Output Example

### PyTest Console Output
```
============================= test session starts =============================
collected 3 items

tests/test_login.py::TestLogin::test_successful_login PASSED [ 33%]
tests/test_login.py::TestLogin::test_locked_out_user FAILED [ 66%]
tests/test_login.py::TestLogin::test_performance_glitch_user PASSED [100%]

============================== FAILURES ===============================
________________________ TestLogin.test_locked_out_user ________________________

    def test_locked_out_user(self):
        def _test_locked_login():
            self.login_page.login_with_locked_user()
>           assert self.login_page.is_login_successful(), "Locked out user should not be able to login"
    E           AssertionError: Locked out user should not be able to login

tests/test_login.py:48: AssertionError

========================= short test summary info ==========================
PASSED: 2
FAILED: 1
======================== 1 failed, 2 passed in 14.46s =========================
```

## Unit Test Output Example

### Framework Unit Tests
```
============================= test session starts =============================
collected 15 items

tests/test_framework.py::TestRetryEngine::test_successful_execution_no-retry PASSED [  6%]
tests/test_framework.py::TestRetryEngine::test_failure_all_retries PASSED       [ 13%]
tests/test_framework.py::TestRetryEngine::test_flaky_detection_pass_after_retry PASSED [ 20%]
tests/test_framework.py::TestRetryEngine::test_retry_delay PASSED             [ 26%]
tests/test_framework.py::TestRetryEngine::test_result_to_dict PASSED           [ 33%]
tests/test_framework.py::TestFlakyDetector::test_analyze_pass_result PASSED     [ 40%]
tests/test_framework.py::TestFlakyDetector::test_analyze_failure_result PASSED   [ 46%]
tests/test_framework.py::TestFlakyDetector::test_analyze_flaky_result PASSED    [ 53%]
tests/test_framework.py::TestFlakyDetector::test_timeout_classification PASSED     [ 60%]
tests/test_framework.py::TestFlakyDetector::test_flaky_statistics PASSED         [ 66%]
tests/test_framework.py::TestLogger::test_logger_initialization PASSED          [ 73%]
tests/test_framework.py::TestLogger::test_log_info PASSED                      [ 80%]
tests/test_framework.py::TestLogger::test_log_error PASSED                      [ 86%]
tests/test_framework.py::TestLogger::test_log_exception PASSED                  [ 93%]
tests/test_framework.py::TestLogger::test_log_manager PASSED                      [100%]

========================= 15 passed in 2.34s ===========================
```

## Statistics Summary Example

### Execution Statistics
```json
{
  "total_tests": 3,
  "passed": 1,
  "failed": 1,
  "flaky": 1,
  "pass_percentage": 33.33,
  "fail_percentage": 33.33,
  "flaky_percentage": 33.33,
  "total_retries": 4,
  "avg_retries": 1.33,
  "total_duration": 14.46,
  "avg_duration": 4.82,
  "timestamp": "2026-06-29 21:41:24"
}
```

## Error Messages Example

### TimeoutException
```
2026-06-29 21:41:16 - ERROR - TEST FAILED: test_performance_glitch_user
2026-06-29 21:41:16 - ERROR - Exception Type: TimeoutException
2026-06-29 21:41:16 - ERROR - Exception Message: Message: 
2026-06-29 21:41:16 - ERROR - Stack Trace: 
Traceback (most recent call last):
  File "core/retry_engine.py", line 45, in execute_with_retry
    result = test_func(*args, **kwargs)
  File "tests/test_login.py", line 75, in test_performance_glitch_user
    assert self.login_page.is_login_successful(), "Performance glitch user should eventually login"
  File "pages/login_page.py", line 85, in is_login_successful
    return "inventory.html" in current_url
```

### NoSuchElementException
```
2026-06-29 21:41:20 - ERROR - TEST FAILED: test_search_product
2026-06-29 21:41:20 - ERROR - Exception Type: NoSuchElementException
2026-06-29 21:41:20 - ERROR - Exception Message: Unable to locate element: [id="search-input"]
```

### StaleElementReferenceException
```
2026-06-29 21:41:25 - ERROR - TEST FAILED: test_add_to_cart
2026-06-29 21:41:25 - ERROR - Exception Type: StaleElementReferenceException
2026-06-29 21:41:25 - ERROR - Exception Message: stale element reference: element is not attached to the page document
```

## Report File Naming Example

### Generated Files
```
screenshots/
├── test_successful_login_20260629_214105.png
├── test_locked_out_user_failure_20260629_214114.png
└── test_performance_glitch_user_flaky_20260629_214119.png

logs/
├── test_execution.log
├── test_successful_login_20260629_214105.log
├── test_locked_out_user_20260629_214114.log
├── test_performance_glitch_user_20260629_214119.log
├── test_locked_out_user_console_20260629_214114.txt
└── test_performance_glitch_user_console_20260629_214119.txt

reports/
├── test_report_20260629_214124.html
└── pytest_report.html
```

## Configuration Example

### config/config.py Settings
```python
# Browser Configuration
BROWSER = "chrome"
HEADLESS_MODE = False
BROWSER_WINDOW_SIZE = "1920,1080"

# Timeout Configuration
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 20
PAGE_LOAD_TIMEOUT = 30
SCRIPT_TIMEOUT = 30

# Retry Configuration
MAX_RETRY_COUNT = 3
RETRY_DELAY = 2.0

# AI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"
AI_ANALYSIS_ENABLED = True

# File Paths
SCREENSHOT_PATH = Path("screenshots")
LOG_PATH = Path("logs")
REPORT_PATH = Path("reports")
```

## Command Line Arguments Example

### main.py Arguments
```bash
# Basic execution
python main.py

# With options
python main.py --test-path tests/test_login.py --verbose --headless --max-retries 5

# AI options
python main.py --use-ollama  # Use Ollama instead of OpenAI
python main.py --no-ai       # Disable AI analysis

# Report options
python main.py --output reports/custom_report.html
```

## Summary

This document provides comprehensive examples of:
- Console output during test execution
- Log file contents with timestamps
- Browser console log captures
- AI analysis responses from both OpenAI and Ollama
- HTML report structure and components
- PyTest execution output
- Unit test results
- Statistics and metrics
- Error messages and stack traces
- Generated file naming conventions
- Configuration settings
- Command-line argument usage

These examples demonstrate the complete functionality of the Smart Retry & Flaky Test Detector framework in action.
