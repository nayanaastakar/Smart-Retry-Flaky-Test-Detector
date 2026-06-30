"""
Execution History Model - Module 7

Data model for an execution history entry.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionHistory:
    """
    Represents a single test suite execution event.
    """
    execution_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    flaky: int = 0
    execution_time: str = "0.0 sec"
    report_path: str = ""
    ai_analysis_count: int = 0
    exceptions: list = field(default_factory=list)
    root_causes: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    flaky_tests: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "execution_id": self.execution_id,
            "timestamp": self.timestamp,
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "flaky": self.flaky,
            "execution_time": self.execution_time,
            "report_path": self.report_path,
            "ai_analysis_count": self.ai_analysis_count,
            "exceptions": self.exceptions,
            "root_causes": self.root_causes,
            "recommendations": self.recommendations,
            "flaky_tests": self.flaky_tests
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionHistory":
        return cls(
            execution_id=data.get("execution_id", ""),
            timestamp=data.get("timestamp", ""),
            total_tests=data.get("total_tests", 0),
            passed=data.get("passed", 0),
            failed=data.get("failed", 0),
            flaky=data.get("flaky", 0),
            execution_time=data.get("execution_time", "0.0 sec"),
            report_path=data.get("report_path", ""),
            ai_analysis_count=data.get("ai_analysis_count", 0),
            exceptions=data.get("exceptions", []),
            root_causes=data.get("root_causes", []),
            recommendations=data.get("recommendations", []),
            flaky_tests=data.get("flaky_tests", [])
        )
