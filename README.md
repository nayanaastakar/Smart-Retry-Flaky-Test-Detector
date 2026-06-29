# Smart Retry & Flaky Test Detector

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Selenium](https://img.shields.io/badge/selenium-4.23.1-green.svg)
![PyTest](https://img.shields.io/badge/pytest-8.3.2-red.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production--ready-success.svg)

An intelligent Selenium-based automation testing framework that automatically retries failed tests, detects flaky tests, distinguishes them from genuine application failures, analyzes failure logs using AI, and generates detailed HTML reports.

## 🎯 Project Overview

This framework is designed for M.Tech/B.E final-year lab projects and follows industry coding standards. It provides a comprehensive solution for test automation with intelligent retry mechanisms, AI-powered failure analysis, and professional reporting.

## ✨ Features

- **Automatic Test Retry**: Configurable retry logic for failed tests
- **Flaky Test Detection**: Distinguishes between flaky tests and genuine failures
- **AI-Powered Analysis**: Uses OpenAI or Ollama to analyze Selenium exceptions
- **Screenshot Capture**: Automatic screenshot capture on test failures
- **Console Log Collection**: Captures browser console logs for debugging
- **Professional HTML Reports**: Comprehensive reports with charts and visualizations
- **Page Object Model**: Clean, maintainable test architecture
- **Configurable Settings**: Extensive configuration options
- **Type Hints & Docstrings**: Professional code documentation
- **SOLID Principles**: Object-oriented design patterns

## 🏗️ Architecture

### Folder Structure

```
SmartRetryFlakyDetector/
│
├── tests/                    # Selenium test cases
│   ├── test_login.py
│   ├── test_search.py
│   ├── test_checkout.py
│   └── test_framework.py     # Unit tests
│
├── pages/                    # Page Object Model
│   ├── login_page.py
│   ├── search_page.py
│   └── checkout_page.py
│
├── core/                     # Core framework components
│   ├── driver.py            # Selenium WebDriver manager
│   ├── retry_engine.py      # Retry logic implementation
│   ├── flaky_detector.py    # Flaky test detection
│   ├── logger.py            # Logging system
│   ├── screenshot.py        # Screenshot utility
│   └── console_logs.py      # Console log capture
│
├── ai/                       # AI analysis components
│   ├── ai_analyzer.py       # AI analyzer interface
│   ├── ollama_provider.py   # Ollama implementation
│   └── prompts.py           # AI prompt templates
│
├── utils/                    # Utility functions
│   └── report_generator.py  # HTML report generator
│
├── reports/                  # Generated HTML reports
├── screenshots/             # Failure screenshots
├── logs/                     # Execution logs
├── config/                   # Configuration files
│   └── config.py
│
├── requirements.txt          # Python dependencies
├── pytest.ini               # PyTest configuration
├── main.py                  # Entry point
└── README.md                # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.12 or higher
- Google Chrome browser
- Windows OS (primary), supports Linux/Mac

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SmartRetryFlakyDetector
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AI (optional)**
   
   For OpenAI:
   ```bash
   set OPENAI_API_KEY=your_api_key_here
   ```
   
   For Ollama (local):
   ```bash
   # Install Ollama from https://ollama.ai
   ollama serve
   ollama pull llama3
   ```

## 📖 Usage

### Running Tests

**Run all tests:**
```bash
python main.py
```

**Run specific test file:**
```bash
python main.py --test-path tests/test_login.py
```

**Run with verbose output:**
```bash
python main.py --verbose
```

**Run in headless mode:**
```bash
python main.py --headless
```

**Use Ollama for AI analysis:**
```bash
python main.py --use-ollama
```

**Disable AI analysis:**
```bash
python main.py --no-ai
```

**Custom retry count:**
```bash
python main.py --max-retries 5
```

### Using PyTest Directly

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_login.py

# Run with markers
pytest tests/ -m login

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 🔧 Configuration

Edit `config/config.py` to customize:

```python
# Browser settings
BROWSER = "chrome"
HEADLESS_MODE = False
BROWSER_WINDOW_SIZE = "1920,1080"

# Timeout settings
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 20
PAGE_LOAD_TIMEOUT = 30

# Retry settings
MAX_RETRY_COUNT = 3
RETRY_DELAY = 2.0

# AI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_ANALYSIS_ENABLED = True

# File paths
SCREENSHOT_PATH = Path("screenshots")
LOG_PATH = Path("logs")
REPORT_PATH = Path("reports")
```

## 📊 Reports

The framework generates professional HTML reports with:

- **Dashboard Metrics**: Pass/Fail/Flaky counts, percentages
- **Test Summary Table**: Overview of all test executions
- **Detailed Results**: Exception details, screenshots, console logs
- **AI Analysis**: Root cause analysis and suggested fixes
- **Visual Charts**: Progress bars and statistics

Reports are saved in the `reports/` directory with timestamps.

## 🧪 Test Scenarios

The framework includes sample tests for:

1. **Login Tests**
   - Successful login
   - Locked out user (failure)
   - Performance glitch user (flaky)
   - Invalid credentials

2. **Search Tests**
   - Product listing
   - Product search
   - Add to cart
   - Sorting

3. **Checkout Tests**
   - Cart review
   - Checkout form
   - Order completion
   - Navigation

## 🤖 AI Analysis

### OpenAI Integration

Uses GPT-4 to analyze:
- Exception classification
- Root cause identification
- Suggested fixes
- Best practices
- Confidence scoring

### Ollama Integration

Local AI inference using:
- Llama3 model
- No API keys required
- Offline execution
- Privacy-focused

## 🎨 Design Patterns

- **Strategy Pattern**: AI provider selection (OpenAI/Ollama)
- **Page Object Model**: Test page abstraction
- **Singleton Pattern**: Driver manager
- **Factory Pattern**: Provider creation
- **Template Method**: Retry engine workflow

## 📝 Code Quality

- **Type Hints**: Full type annotations
- **Docstrings**: Comprehensive documentation
- **PEP 8**: Code style compliance
- **SOLID Principles**: Object-oriented design
- **Modular Design**: Reusable components
- **Error Handling**: Comprehensive exception handling

## 🔍 Flaky Test Detection

The framework detects flaky tests by analyzing:

- **Timeout Exceptions**: Slow element loading
- **Element Not Found**: Dynamic content issues
- **Stale Elements**: DOM updates
- **Element Interaction**: Animation/overlay blocks
- **Network Issues**: Temporary connectivity problems
- **Retry Patterns**: Success after retry

## 🛠️ Exception Handling

Handles all common Selenium exceptions:

- `TimeoutException`
- `NoSuchElementException`
- `StaleElementReferenceException`
- `WebDriverException`
- `ElementClickInterceptedException`
- `ElementNotInteractableException`

## 📈 Statistics

The framework tracks:

- Total tests executed
- Passed/Failed/Flaky counts
- Pass/Fail/Flaky percentages
- Total retry attempts
- Average execution time
- Average retry count

## 🚧 Future Scope

- [ ] Parallel test execution
- [ ] Mobile testing support
- [ ] CI/CD integration
- [ ] Database testing
- [ ] API testing integration
- [ ] Performance metrics
- [ ] Test data management
- [ ] Custom report templates
- [ ] Email notifications
- [ ] Slack/Discord integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is created for educational purposes. Feel free to use and modify as needed.

## 👨‍💻 Author

Created as an M.Tech/B.E final-year lab project demonstrating advanced test automation techniques.

## 🙏 Acknowledgments

- Selenium WebDriver
- PyTest Framework
- OpenAI API
- Ollama
- Saucedemo (demo website)

## 📞 Support

For issues or questions:
- Check the documentation
- Review test examples
- Examine logs in `logs/` directory
- Review generated reports

## 🎓 Educational Value

This project demonstrates:
- Advanced test automation concepts
- AI integration in testing
- Design pattern implementation
- Professional coding standards
- Industry best practices
- Problem-solving skills

---

**Built with ❤️ for Quality Assurance Excellence**
