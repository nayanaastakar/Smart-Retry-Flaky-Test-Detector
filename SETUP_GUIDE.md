# Setup and Execution Guide

## Complete Setup Instructions

### 1. Initial Setup

#### Step 1.1: Clone/Download the Project
```bash
# If using Git
git clone <repository-url>
cd "STA project- Smart Retry & Flaky Test Detector"

# Or extract the downloaded zip file
# Navigate to the project directory
cd "d:\Projects\STA project- Smart Retry & Flaky Test Detector"
```

#### Step 1.2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate
```

#### Step 1.3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 1.4: Verify Installation
```bash
# Check Python version
python --version  # Should be 3.12+

# Check Selenium installation
python -c "import selenium; print(selenium.__version__)"

# Check PyTest installation
pytest --version
```

### 2. Configuration Setup

#### Step 2.1: Configure AI (Optional)

**Option A: OpenAI (Cloud)**
```bash
# Set OpenAI API key as environment variable
set OPENAI_API_KEY=your_openai_api_key_here

# Or add to system environment variables
# Windows: System Properties → Environment Variables
# Linux/Mac: Add to ~/.bashrc or ~/.zshrc
```

**Option B: Ollama (Local)**
```bash
# Download and install Ollama from https://ollama.ai

# Start Ollama server
ollama serve

# Pull the model
ollama pull llama3

# Verify installation
ollama list
```

#### Step 2.2: Configure Framework Settings
Edit `config/config.py` to customize:
```python
# Browser settings
BROWSER = "chrome"
HEADLESS_MODE = False  # Set to True for CI/CD

# Retry settings
MAX_RETRY_COUNT = 3
RETRY_DELAY = 2.0

# AI settings
AI_ANALYSIS_ENABLED = True  # Set to False to disable AI
```

### 3. Execution Commands

#### Basic Execution

**Run all tests with framework:**
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

#### AI Configuration

**Use OpenAI for AI analysis:**
```bash
python main.py  # Default uses OpenAI
```

**Use Ollama for AI analysis:**
```bash
python main.py --use-ollama
```

**Disable AI analysis:**
```bash
python main.py --no-ai
```

#### Retry Configuration

**Custom retry count:**
```bash
python main.py --max-retries 5
```

#### Report Configuration

**Specify custom report output:**
```bash
python main.py --output reports/custom_report.html
```

### 4. PyTest Execution Commands

#### Basic PyTest Commands

**Run all tests:**
```bash
pytest tests/
```

 **Run specific test file:**
```bash
pytest tests/test_login.py
```

**Run specific test function:**
```bash
pytest tests/test_login.py::TestLogin::test_successful_login
```

**Run with verbose output:**
```bash
pytest tests/ -v
```

**Run with markers:**
```bash
pytest tests/ -m login
pytest tests/ -m smoke
pytest tests/ -m flaky
```

#### Advanced PyTest Commands

**Run with coverage:**
```bash
pytest tests/ --cov=. --cov-report=html
```

**Run with HTML report:**
```bash
pytest tests/ --html=reports/pytest_report.html --self-contained-html
```

**Run in parallel:**
```bash
pytest tests/ -n 2  # Requires pytest-xdist
```

**Stop on first failure:**
```bash
pytest tests/ -x
```

**Run failed tests only:**
```bash
pytest tests/ --lf
```

### 5. Running Unit Tests

**Run framework unit tests:**
```bash
pytest tests/test_framework.py -v
```

**Run specific unit test class:**
```bash
pytest tests/test_framework.py::TestRetryEngine -v
```

**Run specific unit test method:**
```bash
pytest tests/test_framework.py::TestRetryEngine::test_successful_execution_no-retry -v
```

### 6. Troubleshooting Commands

#### Check Installation
```bash
# Check all installed packages
pip list

# Check specific package versions
pip show selenium
pip show pytest
pip show openai
```

#### Verify Directory Structure
```bash
# List all directories
dir /B  # Windows
ls -la  # Linux/Mac

# Verify all required directories exist
dir tests pages core ai utils config reports screenshots logs
```

#### Check Logs
```bash
# View latest execution log
type logs\test_execution.log  # Windows
cat logs/test_execution.log  # Linux/Mac

# View framework unit test log
type logs\pytest_execution.log  # Windows
```

#### Clean Up
```bash
# Clean old screenshots
# Manually delete files in screenshots/ directory

# Clean old logs
# Manually delete files in logs/ directory

# Clean old reports
# Manually delete files in reports/ directory
```

### 7. Development Commands

#### Run in Development Mode
```bash
# Run with maximum verbosity
python main.py --verbose --test-path tests/test_login.py

# Run with headless mode disabled
python main.py --test-path tests/test_login.py

# Run with custom retry count for debugging
python main.py --max-retries 1 --test-path tests/test_login.py
```

#### Debug Mode
```bash
# Run with PyTest debugger
pytest tests/ --pdb

# Run with PyTest trace
pytest tests/ --trace

# Run with PyTest verbose output
pytest tests/ -vv
```

### 8. CI/CD Integration Commands

#### GitHub Actions Example
```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python main.py --headless --no-ai
```

#### Jenkins Pipeline Example
```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh 'python -m venv venv'
                sh '. venv/bin/activate'
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'python main.py --headless --no-ai'
            }
        }
    }
}
```

### 9. Quick Start Commands

**First-time setup (one-time):**
```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure AI (optional)
set OPENAI_API_KEY=your_key_here
```

**Daily execution:**
```bash
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Run tests
python main.py

# 3. View report
# Open reports/test_report_*.html in browser
```

### 10. Common Issues and Solutions

#### Issue: ChromeDriver not found
```bash
# Solution: webdriver-manager handles this automatically
# If still fails, manually install:
pip install webdriver-manager --upgrade
```

#### Issue: Module not found
```bash
# Solution: Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Issue: OpenAI API key error
```bash
# Solution: Set environment variable
set OPENAI_API_KEY=your_key_here

# Or disable AI
python main.py --no-ai
```

#### Issue: Ollama connection error
```bash
# Solution: Ensure Ollama server is running
ollama serve

# Verify model is downloaded
ollama list
```

#### Issue: Port already in use
```bash
# Solution: Kill existing Chrome processes
taskkill /F /IM chrome.exe /T  # Windows
pkill -9 chrome  # Linux/Mac
```

### 11. Performance Optimization

**Run tests in parallel:**
```bash
pytest tests/ -n auto
```

**Run with timeout:**
```bash
pytest tests/ --timeout=300
```

**Run without browser (mocking):**
```bash
# For unit tests only
pytest tests/test_framework.py
```

### 12. Verification Commands

**Verify framework is working:**
```bash
# Run unit tests
pytest tests/test_framework.py -v

# Run a simple Selenium test
pytest tests/test_login.py::TestLogin::test_page_load_verification -v

# Check report generation
python main.py --test-path tests/test_login.py
dir reports
```

### 13. Complete Execution Workflow

**Full workflow from scratch:**
```bash
# 1. Navigate to project
cd "d:\Projects\STA project- Smart Retry & Flaky Test Detector"

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure AI (optional)
set OPENAI_API_KEY=your_key_here

# 5. Run framework unit tests
pytest tests/test_framework.py -v

# 6. Run sample tests
python main.py --verbose

# 7. View generated report
# Open reports/test_report_*.html in browser

# 8. Check logs
type logs\test_execution.log

# 9. Deactivate virtual environment
deactivate
```

### 14. Command Reference Summary

| Command | Description |
|---------|-------------|
| `python main.py` | Run all tests with framework |
| `python main.py --verbose` | Run with verbose output |
| `python main.py --headless` | Run in headless mode |
| `python main.py --use-ollama` | Use Ollama for AI |
| `python main.py --no-ai` | Disable AI analysis |
| `pytest tests/` | Run tests with PyTest |
| `pytest tests/ -v` | Run with verbose output |
| `pytest tests/ -m login` | Run with marker |
| `pytest tests/test_framework.py` | Run unit tests |
| `pip install -r requirements.txt` | Install dependencies |
| `python -m venv venv` | Create virtual environment |
| `venv\Scripts\activate` | Activate virtual environment |
