"""
Evidence Model — Module 4

A dataclass that represents all debug evidence collected for a single
test execution (screenshot path, browser-log path, timing, exception, etc.)

This model is returned by ScreenshotManager / BrowserLogManager and is
passed up to the Flask layer for display on the Result page.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.ai_analysis import AIAnalysis


@dataclass
class Evidence:
    """
    Immutable record of all evidence collected for one test run.

    Attributes
    ----------
    test_name       : Human-readable test identifier
    status          : "PASS" | "FLAKY" | "FAILURE"
    screenshot      : Absolute path to the .png file (empty string if not captured)
    log_file        : Absolute path to the browser-console .txt file
    timestamp       : ISO-format string of when evidence was collected
    attempts        : How many execution attempts were made (1 = no retry)
    execution_time  : Formatted string, e.g. "4.2 sec"
    exception_type  : Class name of the thrown exception, or ""
    exception_msg   : Short exception message for display
    ai_analysis     : Optional AI-generated summary/analysis
    """

    test_name: str
    status: str
    screenshot: str = ""
    log_file: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    attempts: int = 1
    execution_time: str = "0.0 sec"
    exception_type: str = ""
    exception_msg: str = ""
    ai_analysis: Optional[AIAnalysis] = None

    # ── helpers ──────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a plain dict (JSON-serialisable)."""
        return asdict(self)

    def to_json(self) -> str:
        """Return a pretty-printed JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "Evidence":
        """Re-hydrate an Evidence from a plain dict."""
        return cls(**data)

    @property
    def has_screenshot(self) -> bool:
        """True when a screenshot file exists on disk."""
        return bool(self.screenshot) and Path(self.screenshot).exists()

    @property
    def has_log(self) -> bool:
        """True when a browser-log file exists on disk."""
        return bool(self.log_file) and Path(self.log_file).exists()

    @property
    def is_failure(self) -> bool:
        return self.status in ("FAILURE", "FLAKY")

    def __str__(self) -> str:
        return (
            f"Evidence(test={self.test_name!r}, status={self.status!r}, "
            f"attempts={self.attempts}, time={self.execution_time})"
        )
