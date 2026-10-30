"""
database/seed.py
=================
Populates first-run data: built-in website profiles (SauceDemo, OrangeHRM,
DemoQA, Automation Exercise, ParaBank) and a default admin user so the app is
usable immediately after `python app.py --init-db`.

Run directly:  python -m database.seed
"""

from __future__ import annotations

import json

from werkzeug.security import generate_password_hash

from database.db_manager import execute, fetch_one, init_db

BUILTIN_PROFILES = [
    {
        "name": "SauceDemo",
        "base_url": "https://www.saucedemo.com",
        "description": "Sample e-commerce site widely used for Selenium practice (login, cart, checkout).",
        "icon": "fa-cart-shopping",
        "config": {
            "login_url": "/",
            "valid_user": "standard_user",
            "valid_password": "secret_sauce",
            "locators": {
                "username": "#user-name",
                "password": "#password",
                "login_button": "#login-button",
            },
        },
    },
    {
        "name": "OrangeHRM",
        "base_url": "https://opensource-demo.orangehrmlive.com",
        "description": "Open-source HR management demo used for form-heavy, multi-page test flows.",
        "icon": "fa-building",
        "config": {
            "login_url": "/web/index.php/auth/login",
            "valid_user": "Admin",
            "valid_password": "admin123",
            "locators": {
                "username": "input[name='username']",
                "password": "input[name='password']",
                "login_button": "button[type='submit']",
            },
        },
    },
    {
        "name": "DemoQA",
        "base_url": "https://demoqa.com",
        "description": "Widget-rich playground (forms, alerts, frames, tables) for UI interaction coverage.",
        "icon": "fa-vial",
        "config": {"login_url": "/login", "locators": {}},
    },
    {
        "name": "Automation Exercise",
        "base_url": "https://automationexercise.com",
        "description": "Full e-commerce flow including signup, cart, checkout and invoice download.",
        "icon": "fa-store",
        "config": {"login_url": "/login", "locators": {}},
    },
    {
        "name": "ParaBank",
        "base_url": "https://parabank.parasoft.com/parabank",
        "description": "Simulated online banking app for negative-testing and transaction flows.",
        "icon": "fa-building-columns",
        "config": {"login_url": "/index.htm", "locators": {}},
    },
]


def seed_website_profiles() -> None:
    for profile in BUILTIN_PROFILES:
        existing = fetch_one("SELECT id FROM website_profiles WHERE name = ?", (profile["name"],))
        if existing:
            continue
        execute(
            """INSERT INTO website_profiles (name, base_url, description, icon, config_json, is_builtin)
               VALUES (?, ?, ?, ?, ?, 1)""",
            (
                profile["name"],
                profile["base_url"],
                profile["description"],
                profile["icon"],
                json.dumps(profile["config"]),
            ),
        )


def seed_admin_user(username: str = "admin", password: str = "Admin@123", email: str = "admin@smartretry.local") -> None:
    existing = fetch_one("SELECT id FROM users WHERE username = ?", (username,))
    if existing:
        return
    execute(
        """INSERT INTO users (username, email, password_hash, full_name, role, avatar_color)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (username, email, generate_password_hash(password), "Administrator", "admin", "#6366f1"),
    )


def seed_default_settings() -> None:
    defaults = {
        "browser": "chrome",
        "retry_count": "3",
        "retry_delay": "2",
        "headless": "true",
        "theme": "dark",
        "ai_enabled": "true",
        "execution_timeout": "120",
    }
    for key, value in defaults.items():
        existing = fetch_one("SELECT key FROM settings WHERE key = ?", (key,))
        if not existing:
            execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))


def run_all() -> None:
    init_db()
    seed_website_profiles()
    seed_admin_user()
    seed_default_settings()
    print("[seed] Database initialized with default profiles, admin user (admin / Admin@123), and settings.")


if __name__ == "__main__":
    run_all()
