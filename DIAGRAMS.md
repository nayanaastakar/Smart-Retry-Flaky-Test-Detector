# Flowchart and Architecture Diagrams

## Test Execution Flowchart

```
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

```
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

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface                             │
│                  (Command Line / PyTest)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Main Entry Point                            │
│                         (main.py)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Test Runner  │  │ Config Mgr   │  │ Logger Mgr   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Core Layer  │ │  Pages Layer │ │   AI Layer   │
└──────────────┘ └──────────────┘ └──────────────┘
│              │ │              │ │              │
│ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │
│ │  Driver  │ │ │ │  Login   │ │ │ │ Analyzer │ │
│ │ Manager  │ │ │ │  Page    │ │ │ │          │ │
│ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │
│ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │
│ │  Retry   │ │ │ │  Search  │ │ │ │  OpenAI  │ │
│ │  Engine  │ │ │ │  Page    │ │ │ │ Provider │ │
│ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │
│ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │
│ │  Flaky   │ │ │ │Checkout  │ │ │ │  Ollama  │ │
│ │ Detector │ │ │ │  Page    │ │ │ │ Provider │ │
│ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │
│ ┌──────────┐ │ │              │ │ ┌──────────┐ │
│ │  Logger  │ │ │              │ │ │  Prompts │ │
│ │          │ │ │              │ │ │          │ │
│ └──────────┘ │ │              │ │ └──────────┘ │
│ ┌──────────┐ │ │              │ │              │
│ │Screenshot│ │ │              │ │              │
│ │ Manager  │ │ │              │ │              │
│ └──────────┘ │ │              │ │              │
│ ┌──────────┐ │ │              │ │              │
│ │ Console  │ │ │              │ │              │
│ │  Logs    │ │ │              │ │              │
│ └──────────┘ │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Utility Layer                               │
│                    (utils/report_generator.py)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│ │              HTML Report Generator                          │  │
│ │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│ │  │ Dashboard│  │  Summary  │  │  Details │              │  │
│ │  └──────────┘  └──────────┘  └──────────┘              │  │
│ │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│ │  │  Charts  │  │  Screenshots│ │  AI Analysis│           │  │
│ │  └──────────┘  └──────────┘  └──────────┘              │  │
│ └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Output Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│ │ HTML Report│ │ Screenshots│ │  Logs    │ │ Console Logs│    │
│ └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
┌─────────────┐
│   PyTest    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Test Case  │
└──────┬──────┘
       │
       ├─────────────────────────────────────────────────┐
       │                                                 │
       ▼                                                 ▼
┌─────────────┐                                   ┌─────────────┐
│ Page Object │                                   │ Retry Engine│
└──────┬──────┘                                   └──────┬──────┘
       │                                                 │
       ▼                                                 │
┌─────────────┐                                         │
│ Driver Mgr  │◄────────────────────────────────────────┘
└──────┬──────┘
       │
       ├─────────────────────────────────────────────────┐
       │                                                 │
       ▼                                                 ▼
┌─────────────┐                                   ┌─────────────┐
│   Browser   │                                   │  Logger     │
└─────────────┘                                   └──────┬──────┘
                                                         │
                                                         ▼
                                                  ┌─────────────┐
                                                  │  Log File   │
                                                  └─────────────┘

On Failure:
       │
       ▼
┌─────────────┐
│ Screenshot  │
│   Manager   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Screenshot   │
│   File      │
└─────────────┘

       │
       ▼
┌─────────────┐
│Console Logs │
│   Manager   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Console Log │
│   File      │
└─────────────┘

       │
       ▼
┌─────────────┐
│Flaky Detector│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ AI Analyzer │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐ ┌─────────────┐
│   OpenAI    │ │   Ollama    │
└──────┬──────┘ └──────┬──────┘
       │              │
       └──────┬───────┘
              │
              ▼
┌─────────────┐
│  AnalysisResult│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Report Generator│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ HTML Report │
└─────────────┘
```

## Data Flow Diagram

```
Test Execution → Result Collection → Analysis → Reporting

┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Test   │───►│  Result │───►│  AI     │───►│  Report │
│ Execution│   │ Collection│  Analysis│   │Generation│
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│Status   │    │Status   │    │Classification│ │Dashboard│
│Attempts │    │Time     │    │Root Cause│    │Summary  │
│Exceptions│    │Screenshots│  │Suggested Fix│ │Details │
└─────────┘    │Console Logs│  │Best Practices│ │Charts  │
               └─────────┘    └─────────┘    └─────────┘
```

## Class Hierarchy Diagram

```
AIProvider (Abstract)
├── OpenAIProvider
└── OllamaProvider

PageObject (Abstract)
├── LoginPage
├── SearchPage
└── CheckoutPage

TestStatus (Enum)
├── PASS
├── FLAKY
└── FAILURE

FlakyClassification (Enum)
├── TIMEOUT
├── ELEMENT_NOT_FOUND
├── STALE_ELEMENT
├── ELEMENT_NOT_INTERACTABLE
├── NETWORK_ISSUE
├── TEMPORARY_FAILURE
├── GENUINE_FAILURE
└── UNKNOWN
```

## Deployment Architecture

```
Development Environment:
┌─────────────────────────────────────────┐
│         Developer Machine               │
│  ┌─────────────────────────────────┐  │
│  │  Python Environment             │  │
│  │  - Virtual Environment          │  │
│  │  - Dependencies                 │  │
│  │  - Framework Code               │  │
│  │  - Test Cases                   │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │  Browser (Chrome)               │  │
│  │  - ChromeDriver                 │  │
│  │  - WebDriver                   │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │  AI Services (Optional)         │  │
│  │  - OpenAI API (Cloud)           │  │
│  │  - Ollama (Local)               │  │
│  └─────────────────────────────────┘  │
└─────────────────────────────────────────┘

CI/CD Integration (Future):
┌─────────────────────────────────────────┐
│         CI/CD Pipeline                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │  Build  │──►│  Test   │──►│ Report  │  │
│  └─────────┘  └─────────┘  └─────────┘  │
│                                    │    │
│                                    ▼    │
│                            ┌─────────┐    │
│                            │ Deploy  │    │
│                            └─────────┘    │
└─────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│         Security Layers                  │
│  ┌─────────────────────────────────┐  │
│  │  API Key Management              │  │
│  │  - Environment Variables         │  │
│  │  - No Hardcoding                 │  │
│  │  - Secure Storage                │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │  Data Privacy                   │  │
│  │  - Local AI Option (Ollama)      │  │
│  │  - No Sensitive Data in Logs     │  │
│  │  - Screenshot Management         │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │  Browser Security                │  │
│  │  - Secure WebDriver Options     │  │
│  │  - No Extension Auto-install     │  │
│  │  - Headless Mode Option         │  │
│  └─────────────────────────────────┘  │
└─────────────────────────────────────────┘
```
