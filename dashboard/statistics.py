"""
Statistics Module - Module 7

Calculates analytics across all historical runs.
"""

from dashboard.history_manager import HistoryManager


class Statistics:
    """
    Calculates execution analytics.
    """

    def __init__(self):
        self.manager = HistoryManager()
        self.records = self.manager.load_history()

    def get_summary(self) -> dict:
        """Returns overall execution summary."""
        if not self.records:
            return {
                "total_executions": 0,
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "flaky": 0,
                "avg_pass_rate": 0.0,
                "avg_exec_time": "0.0s"
            }

        total_execs = len(self.records)
        total_tests = sum(r.total_tests for r in self.records)
        passed = sum(r.passed for r in self.records)
        failed = sum(r.failed for r in self.records)
        flaky = sum(r.flaky for r in self.records)

        avg_pass = (passed / total_tests * 100) if total_tests > 0 else 0.0

        total_time = 0.0
        for r in self.records:
            try:
                total_time += float(r.execution_time.replace(" sec", ""))
            except:
                pass
        
        avg_time = (total_time / total_execs) if total_execs > 0 else 0.0

        return {
            "total_executions": total_execs,
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "flaky": flaky,
            "avg_pass_rate": round(avg_pass, 1),
            "avg_exec_time": f"{round(avg_time, 2)}s"
        }

    def get_chart_data(self) -> dict:
        """Returns data structures for Chart.js."""
        # execution trend (last 10 runs)
        recent = list(reversed(self.records[:10]))
        
        labels = [r.timestamp.split(" ")[1] for r in recent] # Just time
        passed_data = [r.passed for r in recent]
        failed_data = [r.failed for r in recent]
        flaky_data = [r.flaky for r in recent]

        return {
            "trend": {
                "labels": labels,
                "passed": passed_data,
                "failed": failed_data,
                "flaky": flaky_data
            },
            "pie": {
                "passed": sum(r.passed for r in self.records),
                "failed": sum(r.failed for r in self.records),
                "flaky": sum(r.flaky for r in self.records)
            }
        }
