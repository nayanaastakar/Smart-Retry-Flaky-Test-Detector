"""
History Manager - Module 7

Handles reading/writing of execution records.
"""

import json
import logging
from typing import List

from config.config import Config
from dashboard.execution_history import ExecutionHistory


class HistoryManager:
    """
    Manages historical records of test executions.
    """

    def __init__(self):
        self.config = Config()
        self.history_file = self.config.HISTORY_PATH
        self.logger = logging.getLogger(self.__class__.__name__)
        self._ensure_file()

    def _ensure_file(self):
        """Ensure the JSON file exists."""
        if not self.history_file.exists():
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def load_history(self) -> List[ExecutionHistory]:
        """Load all historical executions."""
        if not self.config.ENABLE_HISTORY:
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ExecutionHistory.from_dict(item) for item in data]
        except Exception as e:
            self.logger.error(f"Failed to load history: {str(e)}")
            return []

    def save_execution(self, history: ExecutionHistory) -> bool:
        """Save a new execution to history."""
        if not self.config.ENABLE_HISTORY:
            return False

        try:
            records = self.load_history()
            records.insert(0, history)  # Add newest at the top
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([r.to_dict() for r in records], f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save history: {str(e)}")
            return False

    def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution by ID."""
        try:
            records = self.load_history()
            records = [r for r in records if r.execution_id != execution_id]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([r.to_dict() for r in records], f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete history: {str(e)}")
            return False
