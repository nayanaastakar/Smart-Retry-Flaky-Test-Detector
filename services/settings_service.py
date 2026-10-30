"""
services/settings_service.py
==============================
Single source of truth for *runtime* settings. The Settings page writes to the
`settings` table; this module reads them back so they actually change
behaviour. Anything not saved in the database falls back to config.py / .env.

Values are read fresh on every call (no caching) so a change on the Settings
page takes effect on the very next run without restarting the server.
"""

from __future__ import annotations

from config import settings as cfg
from database.db_manager import fetch_all


def _raw() -> dict[str, str]:
    try:
        return {r["key"]: r["value"] for r in fetch_all("SELECT key, value FROM settings")}
    except Exception:  # noqa: BLE001 - DB not initialised yet; fall back to config
        return {}


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: str | None, default: int) -> int:
    try:
        return int(float(value)) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _to_float(value: str | None, default: float) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def get_runtime_settings() -> dict:
    raw = _raw()
    return {
        "browser": (raw.get("browser") or cfg.DEFAULT_BROWSER).lower(),
        "headless": _to_bool(raw.get("headless"), cfg.HEADLESS),
        "retry_count": max(0, _to_int(raw.get("retry_count"), cfg.MAX_RETRIES)),
        "retry_delay": max(0.0, _to_float(raw.get("retry_delay"), cfg.RETRY_DELAY_SECONDS)),
        "execution_timeout": max(5, _to_int(raw.get("execution_timeout"), cfg.EXECUTION_TIMEOUT)),
        "ai_enabled": _to_bool(raw.get("ai_enabled"), cfg.AI_ENABLED),
        "theme": raw.get("theme", "dark"),
    }
