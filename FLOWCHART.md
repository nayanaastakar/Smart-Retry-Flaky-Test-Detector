# Test Execution Flowchart

```text
Start
│
├─► Initialize Framework
│   ├─► Load Configuration
│   ├─► Setup Logger
│   └─► Initialize WebDriver
│
├─► Run Test
│   ├─► Navigate to Page
│   ├─► Execute Test Actions
│   ├─► Verify Expected Result
│   │
│   ├─► Test Passed?
│   │   ├─► YES → Log Success
│   │   │          Status = PASS
│   │   │          Continue to Next Test
│   │   │
│   │   └─► NO → Capture Screenshot
│   │              Capture Console Logs
│   │              Log Failure
│   │
│   │              ├─► Retry Count < Max Retries?
│   │              │   ├─► YES → Wait (Retry Delay)
│   │              │           Retry Test
│   │              │
│   │              └─► NO → Classify Failure
│   │                       Status = FAILURE
│   │
│   └─► Test Passed After Retry?
│       ├─► YES → Log Flaky Detection
│       │          Status = FLAKY
│       │          AI Analysis
│       │          Generate Fix Suggestions
│       │
│       └─► NO → Status = FAILURE
│
├─► AI Analysis (if enabled)
│   ├─► Send Exception to AI
│   ├─► Get Classification
│   ├─► Get Root Cause
│   ├─► Get Suggested Fix
│   └─► Get Best Practices
│
├─► Collect Results
│   ├─► Test Status
│   ├─► Execution Time
│   ├─► Retry Count
│   ├─► Screenshot Path
│   ├─► Console Logs
│   └─► AI Analysis
│
├─► All Tests Completed?
│   ├─► NO → Run Next Test
│   │
│   └─► YES → Generate Report
│           ├─► Calculate Statistics
│           ├─► Create Dashboard
│           ├─► Generate HTML Report
│           └─► Save Report
│
└─► Finish
    ├─► Cleanup WebDriver
    ├─► Close Logger
    └─► Display Summary
```

## Retry Logic Flowchart

```text
Test Execution Start
│
├─► Attempt 1
│   ├─► Execute Test
│   ├─► Success?
│   │   ├─► YES → Status = PASS
│   │   │          Return Result
│   │   │
│   │   └─► NO → Capture Exception
│   │              Log Failure
│   │
│   │              ├─► Retry Count >= Max Retries?
│   │              │   ├─► YES → Status = FAILURE
│   │              │   │          Return Result
│   │              │   │
│   │              │   └─► NO → Increment Retry Count
│   │                       Wait (Retry Delay)
│   │
│   └─► Retry Attempt 1
│       ├─► Execute Test
│       ├─► Success?
│       │   ├─► YES → Status = FLAKY
│       │   │          Log Flaky Detection
│       │   │          Return Result
│       │   │
│       │   └─► NO → Capture Exception
│       │                  Log Failure
│       │
│       │                  ├─► Retry Count >= Max Retries?
│       │                  │   ├─► YES → Status = FAILURE
│       │                  │   │          Return Result
│       │                  │   │
│       │                  │   └─► NO → Increment Retry Count
│       │                           Wait (Retry Delay)
│       │
│       └─► Retry Attempt 2
│           ├─► Execute Test
│           ├─► Success?
│           │   ├─► YES → Status = FLAKY
│           │   │          Log Flaky Detection
│           │   │          Return Result
│           │   │
│           │   └─► NO → Capture Exception
│           │                  Log Failure
│           │
│           │                  └─► Status = FAILURE
│           │                      Return Result
│
└─► Return Final Result
```
