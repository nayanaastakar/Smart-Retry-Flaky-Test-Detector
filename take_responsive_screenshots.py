"""
Responsive screenshot capture script.
Captures the app at desktop, tablet-landscape, tablet-portrait, and mobile viewports.
Saves to docs/images/responsive/
"""
import os, time, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5050"
OUT_DIR  = r"D:\Projects\smart-retry-framework\docs\images\responsive"
os.makedirs(OUT_DIR, exist_ok=True)

VIEWPORTS = [
    {"name": "desktop",          "w": 1440, "h": 900},
    {"name": "tablet-landscape", "w": 1024, "h": 768},
    {"name": "tablet-portrait",  "w": 768,  "h": 1024},
    {"name": "mobile",           "w": 390,  "h": 844},
]

PAGES = [
    ("01-dashboard",       "/dashboard"),
    ("02-projects",        "/projects"),
    ("03-history",         "/history"),
    ("04-ai-analysis",     "/ai-analysis"),
    ("05-reports",         "/reports"),
    ("06-test-cases",      "/test-cases"),
    ("07-settings",        "/settings"),
    ("08-login",           "/logout"),   # will redirect to login
]

def make_driver(w, h):
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"--window-size={w},{h}")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--hide-scrollbars")
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(w, h)
    return driver

def login(driver):
    driver.get(f"{BASE_URL}/login")
    time.sleep(1.5)
    try:
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        time.sleep(2)
    except Exception:
        pass

def screenshot(driver, path, w, h):
    # Set body overflow for full-height capture at mobile to avoid clipping
    driver.execute_script("document.documentElement.style.overflow='visible';")
    time.sleep(0.5)
    # For pages that are taller than viewport, take a full-page screenshot
    full_h = driver.execute_script("return document.body.scrollHeight")
    capture_h = max(h, min(full_h, h * 3))  # cap at 3x viewport height
    driver.set_window_size(w, capture_h)
    time.sleep(0.3)
    driver.save_screenshot(path)
    driver.set_window_size(w, h)

def main():
    total = 0
    for vp in VIEWPORTS:
        w, h = vp["w"], vp["h"]
        print(f"\n=== {vp['name']} ({w}x{h}) ===")
        driver = make_driver(w, h)
        try:
            login(driver)
            for slug, url in PAGES:
                if url == "/logout":
                    # Capture login page directly
                    driver2 = make_driver(w, h)
                    driver2.get(f"{BASE_URL}/login")
                    time.sleep(2)
                    fname = f"{slug}--{vp['name']}.png"
                    path  = os.path.join(OUT_DIR, fname)
                    driver2.save_screenshot(path)
                    driver2.quit()
                    print(f"  [OK] login ({w}x{h})")
                    total += 1
                    continue

                driver.get(f"{BASE_URL}{url}")
                time.sleep(2.5)

                # For mobile, also open the sidebar to capture drawer state on first page
                if vp["name"] == "mobile" and slug == "01-dashboard":
                    try:
                        hamburger = driver.find_element(By.ID, "navHamburger")
                        hamburger.click()
                        time.sleep(0.8)
                        fname_open = f"{slug}--{vp['name']}--sidebar-open.png"
                        driver.save_screenshot(os.path.join(OUT_DIR, fname_open))
                        # close again
                        overlay = driver.find_element(By.ID, "sidebarOverlay")
                        overlay.click()
                        time.sleep(0.5)
                        print(f"  [OK] {slug} sidebar-open ({w}x{h})")
                        total += 1
                    except Exception as e:
                        print(f"  [!] sidebar open capture failed: {e}")

                fname = f"{slug}--{vp['name']}.png"
                path  = os.path.join(OUT_DIR, fname)
                screenshot(driver, path, w, h)
                print(f"  [OK] {slug} ({w}x{h})")
                total += 1
        finally:
            driver.quit()

    print(f"\n[DONE] Done -- {total} screenshots saved to {OUT_DIR}")

if __name__ == "__main__":
    main()
