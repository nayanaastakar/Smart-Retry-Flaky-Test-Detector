"""
core/flaky_detector.py
=======================
Flaky Test Detection Engine.

Classifies each test into one of three states based on its recent execution
window:

    STABLE            - consistently passes (or consistently fails outright
                         with no flips -> that's CHRONIC_FAILURE instead)
    FLAKY             - result "flips" between pass and fail across recent
                         runs, or required a retry to pass, beyond the
                         configured threshold
    CHRONIC_FAILURE   - fails consistently with no recent passes at all

The core signal is the *flip rate*: how often consecutive runs disagree on
pass/fail. A test that alternates PASS/FAIL/PASS/FAIL is maximally flaky
(flip rate = 1.0). A test that is always PASS or always FAIL has a flip rate
of 0 and is classified by its outcome instead.
"""

from __future__ import annotations

from dataclasses import dataclass

from config import settings
from database.db_manager import execute, fetch_all, fetch_one


@dataclass
class FlakyReport:
    test_name: str
    module: str
    total_runs: int
    pass_count: int
    fail_count: int
    flip_count: int
    flaky_score: float          # 0-100, higher = flakier
    classification: str         # STABLE | FLAKY | CHRONIC_FAILURE


class FlakyDetector:
    def __init__(self, window_size: int | None = None, threshold_pct: float | None = None) -> None:
        self.window_size = window_size if window_size is not None else settings.FLAKY_WINDOW_SIZE
        self.threshold_pct = threshold_pct if threshold_pct is not None else settings.FLAKY_THRESHOLD_PCT

    def evaluate_test(self, test_name: str, module: str = "general") -> FlakyReport:
        rows = fetch_all(
            """SELECT status, retry_success FROM executions
               WHERE test_name = ? AND module = ?
               ORDER BY id DESC LIMIT ?""",
            (test_name, module, self.window_size),
        )

        if not rows:
            return FlakyReport(test_name, module, 0, 0, 0, 0, 0.0, "STABLE")

        # Effective pass/fail sequence, oldest first, treating a retry-saved
        # execution as a fail-then-pass signal (it's evidence of instability
        # even though the overall run is reported as FLAKY, not FAIL).
        sequence = list(reversed([r["status"] for r in rows]))
        retry_saves = sum(1 for r in rows if r["retry_success"])

        total_runs = len(sequence)
        pass_count = sum(1 for s in sequence if s in ("PASS", "FLAKY"))
        fail_count = sum(1 for s in sequence if s == "FAIL")

        flip_count = 0
        for i in range(1, len(sequence)):
            prev_pass = sequence[i - 1] in ("PASS", "FLAKY")
            curr_pass = sequence[i] in ("PASS", "FLAKY")
            if prev_pass != curr_pass:
                flip_count += 1

        max_possible_flips = max(total_runs - 1, 1)
        flip_rate = flip_count / max_possible_flips

        retry_save_rate = retry_saves / total_runs
        # Weight flip_rate 70%, retry_save_rate 30%, scaled to 0-100
        flaky_score = round((flip_rate * 0.7 + retry_save_rate * 0.3) * 100, 2)

        if fail_count == total_runs and total_runs >= 3:
            classification = "CHRONIC_FAILURE"
        elif flaky_score >= self.threshold_pct:
            classification = "FLAKY"
        else:
            classification = "STABLE"

        report = FlakyReport(
            test_name=test_name,
            module=module,
            total_runs=total_runs,
            pass_count=pass_count,
            fail_count=fail_count,
            flip_count=flip_count,
            flaky_score=flaky_score,
            classification=classification,
        )
        self._persist(report)
        return report

    def evaluate_all(self) -> list[FlakyReport]:
        """Re-evaluate every distinct (test_name, module) pair seen in history."""
        pairs = fetch_all("SELECT DISTINCT test_name, module FROM executions")
        return [self.evaluate_test(p["test_name"], p["module"] or "general") for p in pairs]

    @staticmethod
    def _persist(report: FlakyReport) -> None:
        existing = fetch_one(
            "SELECT id FROM flaky_history WHERE test_name = ? AND module = ?",
            (report.test_name, report.module),
        )
        if existing:
            execute(
                """UPDATE flaky_history SET flaky_score=?, total_runs=?, pass_count=?, fail_count=?,
                   flip_count=?, classification=?, last_evaluated_at=CURRENT_TIMESTAMP
                   WHERE id=?""",
                (
                    report.flaky_score,
                    report.total_runs,
                    report.pass_count,
                    report.fail_count,
                    report.flip_count,
                    report.classification,
                    existing["id"],
                ),
            )
        else:
            execute(
                """INSERT INTO flaky_history
                   (test_name, module, flaky_score, total_runs, pass_count, fail_count, flip_count, classification)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    report.test_name,
                    report.module,
                    report.flaky_score,
                    report.total_runs,
                    report.pass_count,
                    report.fail_count,
                    report.flip_count,
                    report.classification,
                ),
            )

    @staticmethod
    def top_flaky_tests(limit: int = 10) -> list[dict]:
        rows = fetch_all(
            """SELECT test_name, module, flaky_score, classification, total_runs
               FROM flaky_history WHERE classification = 'FLAKY'
               ORDER BY flaky_score DESC LIMIT ?""",
            (limit,),
        )
        return [dict(r) for r in rows]
