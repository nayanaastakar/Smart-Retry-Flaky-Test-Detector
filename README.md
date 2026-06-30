# Smart Retry & Flaky Test Detector - Module 1

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Selenium](https://img.shields.io/badge/selenium-4.23.1-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0.3-red.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-module--1-complete-success.svg)

**Module 1: Project Setup, Flask Dashboard & Selenium Integration**

A professional Selenium-based automation testing framework with a Flask web interface. Module 1 provides the foundation for running Selenium tests on SauceDemo through a modern web dashboard.

## 🎯 Module 1 Overview

Module 1 establishes the core infrastructure for the Smart Retry & Flaky Test Detector project. It includes:
- Flask web application with professional Bootstrap 5 dashboard
- Selenium WebDriver integration with automatic ChromeDriver management
- Page Object Model for SauceDemo login page
- Basic login test execution
- Professional blue-themed responsive UI

## ✨ Module 1 Features

- **Flask Dashboard**: Professional Bootstrap 5 interface with blue theme
- **Selenium Integration**: Automatic ChromeDriver management using webdriver-manager
- **Page Object Model**: Clean, maintainable test architecture for login page
- **Login Test**: Automated login test on SauceDemo
- **Loading Spinner**: Visual feedback during test execution
- **Result Display**: Shows test status (PASS/FAIL), execution time, and message
- **Responsive Design**: Mobile-friendly interface
- **Type Hints & Docstrings**: Professional code documentation
- **OOP & PEP8**: Industry-standard coding practices

## 🏗️ Module 1 Folder Structure

```
SmartRetryFlakyDetector/
│
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── README.md                # This file
│
├── config/
│   └── config.py            # Configuration settings
│
├── core/
│   └── driver.py            # WebDriver manager
│
├── pages/
│   └── login_page.py        # Login page object model
│
├── tests/
│   └── test_login.py        # Login test function
│
├── templates/
│   ├── index.html           # Home page with dashboard
│   └── result.html          # Test result page
│
└── static/
    ├── css/
    │   └── style.css        # Custom CSS styling
    └── js/
        └── main.js          # JavaScript for dashboard
```

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- Chrome browser (latest version)
- Windows operating system

### Setup Steps

1. **Navigate to the project directory:**
   ```bash
   cd "d:\Projects\STA project- Smart Retry & Flaky Test Detector"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - Flask 3.0.3
   - Flask-Cors 4.0.1
   - Selenium 4.23.1
   - webdriver-manager 4.0.1

## 🚀 Usage

### Starting the Flask Application

1. **Run the Flask app:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://127.0.0.1:5000
   ```

### Running the Login Test

1. On the dashboard, you will see:
   - Project Name: Smart Retry & Flaky Test Detector
   - Website: SauceDemo
   - "Run Login Test" button

2. Click the "Run Login Test" button

3. The application will:
   - Show a loading spinner
   - Launch Chrome browser
   - Navigate to https://www.saucedemo.com
   - Login with credentials (standard_user / secret_sauce)
   - Verify successful login
   - Close the browser
   - Display the result

4. View the result page showing:
   - Test Status: PASS or FAIL
   - Execution Time: in seconds
   - Message: Success or error details
   - Options to "Run Again" or "Back to Home"

## 🔧 Configuration

Configuration settings are in `config/config.py`:

```python
# Browser Configuration
BROWSER: str = "chrome"
HEADLESS_MODE: bool = False
BROWSER_WINDOW_SIZE: str = "1920,1080"

# Timeout Configurations (in seconds)
IMPLICIT_WAIT: int = 10
EXPLICIT_WAIT: int = 20
PAGE_LOAD_TIMEOUT: int = 30

# Base URL for SauceDemo
SAUCE_DEMO_URL: str = "https://www.saucedemo.com"

# SauceDemo Login Credentials
SAUCE_DEMO_USERNAME: str = "standard_user"
SAUCE_DEMO_PASSWORD: str = "secret_sauce"
```

## 🧪 Test Details

### Login Test

The login test performs the following steps:
1. Initializes Chrome WebDriver
2. Navigates to SauceDemo login page
3. Enters username: `standard_user`
4. Enters password: `secret_sauce`
5. Clicks the login button
6. Verifies the inventory page loads
7. Returns PASS if successful, FAIL otherwise

### Expected Output

**Successful Test:**
- Status: PASS
- Message: "Login successful - Inventory page loaded"
- Execution Time: ~5-10 seconds

**Failed Test:**
- Status: FAIL
- Message: Error details (e.g., "Login failed: Epic sadface: Username and password do not match")
- Execution Time: ~5-10 seconds

## 🎨 UI/UX Features

- **Professional Design**: Modern Bootstrap 5 interface
- **Blue Theme**: Consistent blue gradient color scheme
- **Responsive**: Works on desktop and mobile devices
- **Loading Spinner**: Visual feedback during test execution
- **Smooth Animations**: Hover effects and transitions
- **Clear Results**: Easy-to-read test results with color-coded status

## 📝 Module 1 Limitations

Module 1 is a foundational module with basic functionality. It does NOT include:
- Retry mechanism (added in Module 2)
- Flaky test detection (added in Module 2)
- AI analysis (added in Module 3)
- Screenshot capture (added in Module 2)
- Logging (added in Module 2)
- HTML reports (added in Module 2)
- Dashboard charts (added in Module 2)

These features will be added in subsequent modules.

## 🔮 Next Steps

After completing Module 1, the following modules will be implemented:
- **Module 2**: Retry Engine, Flaky Detection, Screenshot Capture, Logging, HTML Reports
- **Module 3**: AI Analysis Integration
- **Module 4**: Advanced Test Scenarios

## 🛠️ Technology Stack

- **Python 3.12**: Programming language
- **Flask 3.0.3**: Web framework
- **Selenium 4.23.1**: Browser automation
- **webdriver-manager 4.0.1**: Automatic ChromeDriver management
- **Bootstrap 5**: CSS framework
- **Font Awesome**: Icon library
- **Chrome**: Target browser

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Developed as a final-year lab project following industry best practices and coding standards.

---

**Module 1 Status: ✅ Complete**
