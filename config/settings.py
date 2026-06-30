import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
WEBSITES_DIR = CONFIG_DIR / "websites"
REPORTS_DIR = BASE_DIR / "reports"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for directory in [REPORTS_DIR, SCREENSHOTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Default Browser Settings
DEFAULT_BROWSER = "chrome"
HEADLESS_MODE = False
BROWSER_WINDOW_SIZE = "1920,1080"

# Default Timing & Retry (Can be overridden by website config)
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 20
PAGE_LOAD_TIMEOUT = 30
MAX_RETRY_COUNT = 3
RETRY_DELAY = 2.0

# AI Configuration
AI_ANALYSIS_ENABLED = True
AI_PROVIDER = "openai" # 'openai' or 'ollama'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"
