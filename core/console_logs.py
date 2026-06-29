"""
Browser Console Logs Module for Smart Retry & Flaky Test Detector

This module provides browser console log capture functionality with:
- Automatic console log capture
- Multiple log type filtering (log, error, warning, info)
- Timestamped log files
- Structured log storage
- JSON format support
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json

from selenium import webdriver
from config.config import Config
from core.logger import get_logger


class ConsoleLogManager:
    """
    Manages browser console log capture and storage.
    
    This class provides methods to capture, filter, and store browser console logs
    during test execution, particularly useful for debugging JavaScript errors.
    """
    
    def __init__(self):
        """
        Initialize the ConsoleLogManager.
        
        Sets up configuration and logger instance.
        """
        self.config = Config()
        self.logger = get_logger("ConsoleLogManager")
    
    def capture_console_logs(
        self,
        driver: webdriver.Chrome,
        test_name: str
    ) -> Path:
        """
        Capture browser console logs and save to file.
        
        This method retrieves all browser console logs, filters them based on
        configuration, and saves them to a timestamped text file.
        
        Args:
            driver: Selenium WebDriver instance
            test_name: Name of the test case
            
        Returns:
            Path: Path to the saved console log file
        """
        try:
            # Retrieve browser logs
            logs = driver.get_log('browser')
            
            # Filter logs based on configuration
            filtered_logs = self._filter_logs(logs)
            
            # Generate file path
            log_path = self.config.get_console_log_path(test_name)
            
            # Ensure log directory exists
            self.config.LOG_PATH.mkdir(parents=True, exist_ok=True)
            
            # Save logs to file
            self._save_logs_to_file(filtered_logs, log_path)
            
            self.logger.log_console_logs_saved(test_name, log_path)
            self.logger.log_info(f"Captured {len(filtered_logs)} console log entries")
            
            return log_path
            
        except Exception as e:
            self.logger.log_exception(e, f"Failed to capture console logs for test: {test_name}")
            # Return empty path if capture fails
            return Path()
    
    def _filter_logs(self, logs: List[Dict]) -> List[Dict]:
        """
        Filter logs based on configured log types.
        
        Args:
            logs: List of log entries from browser
            
        Returns:
            List[Dict]: Filtered log entries
        """
        if not self.config.CAPTURE_CONSOLE_LOGS:
            return []
        
        filtered = []
        for log in logs:
            log_level = log.get('level', '').lower()
            if log_level in self.config.CONSOLE_LOG_TYPES:
                filtered.append(log)
        
        return filtered
    
    def _save_logs_to_file(self, logs: List[Dict], log_path: Path) -> None:
        """
        Save logs to a text file with formatting.
        
        Args:
            logs: List of log entries to save
            log_path: Path to save the log file
        """
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BROWSER CONSOLE LOGS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total Entries: {len(logs)}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, log in enumerate(logs, 1):
                timestamp = datetime.fromtimestamp(log.get('timestamp', 0) / 1000)
                level = log.get('level', 'UNKNOWN')
                message = log.get('message', '')
                source = log.get('source', 'unknown')
                
                f.write(f"Entry #{i}\n")
                f.write(f"Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Level: {level.upper()}\n")
                f.write(f"Source: {source}\n")
                f.write(f"Message: {message}\n")
                f.write("-" * 80 + "\n\n")
    
    def save_logs_as_json(self, logs: List[Dict], test_name: str) -> Path:
        """
        Save logs as JSON file for programmatic analysis.
        
        Args:
            logs: List of log entries to save
            test_name: Name of the test case
            
        Returns:
            Path: Path to the saved JSON file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = self.config.LOG_PATH / f"{test_name}_console_{timestamp}.json"
            
            # Add metadata
            log_data = {
                "test_name": test_name,
                "timestamp": timestamp,
                "total_entries": len(logs),
                "logs": logs
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2)
            
            self.logger.log_info(f"Console logs saved as JSON: {json_path}")
            return json_path
            
        except Exception as e:
            self.logger.log_exception(e, "Failed to save logs as JSON")
            return Path()
    
    def get_error_logs(self, logs: List[Dict]) -> List[Dict]:
        """
        Filter and return only error-level logs.
        
        Args:
            logs: List of log entries
            
        Returns:
            List[Dict]: Error log entries only
        """
        return [log for log in logs if log.get('level', '').lower() == 'error']
    
    def get_warning_logs(self, logs: List[Dict]) -> List[Dict]:
        """
        Filter and return only warning-level logs.
        
        Args:
            logs: List of log entries
            
        Returns:
            List[Dict]: Warning log entries only
        """
        return [log for log in logs if log.get('level', '').lower() == 'warning']
    
    def analyze_logs(self, logs: List[Dict]) -> Dict:
        """
        Analyze console logs and provide summary statistics.
        
        Args:
            logs: List of log entries
            
        Returns:
            Dict: Summary statistics of the logs
        """
        if not logs:
            return {
                "total": 0,
                "errors": 0,
                "warnings": 0,
                "info": 0,
                "log": 0
            }
        
        summary = {
            "total": len(logs),
            "errors": 0,
            "warnings": 0,
            "info": 0,
            "log": 0
        }
        
        for log in logs:
            level = log.get('level', '').lower()
            if level in summary:
                summary[level] += 1
        
        return summary
    
    def has_errors(self, logs: List[Dict]) -> bool:
        """
        Check if logs contain any errors.
        
        Args:
            logs: List of log entries
            
        Returns:
            bool: True if errors are present
        """
        return any(log.get('level', '').lower() == 'error' for log in logs)
    
    def has_warnings(self, logs: List[Dict]) -> bool:
        """
        Check if logs contain any warnings.
        
        Args:
            logs: List of log entries
            
        Returns:
            bool: True if warnings are present
        """
        return any(log.get('level', '').lower() == 'warning' for log in logs)
    
    def get_log_summary_text(self, logs: List[Dict]) -> str:
        """
        Generate a human-readable summary of console logs.
        
        Args:
            logs: List of log entries
            
        Returns:
            str: Formatted summary text
        """
        summary = self.analyze_logs(logs)
        
        summary_text = f"""
Console Log Summary:
===================
Total Entries: {summary['total']}
Errors: {summary['errors']}
Warnings: {summary['warnings']}
Info: {summary['info']}
Log: {summary['log']}
"""
        
        if self.has_errors(logs):
            summary_text += "\n⚠️  ERRORS DETECTED IN CONSOLE LOGS\n"
            error_logs = self.get_error_logs(logs)
            for error in error_logs[:5]:  # Show first 5 errors
                summary_text += f"  - {error.get('message', 'No message')}\n"
        
        if self.has_warnings(logs):
            summary_text += "\n⚠️  WARNINGS DETECTED IN CONSOLE LOGS\n"
            warning_logs = self.get_warning_logs(logs)
            for warning in warning_logs[:5]:  # Show first 5 warnings
                summary_text += f"  - {warning.get('message', 'No message')}\n"
        
        return summary_text
    
    def cleanup_old_logs(self, days_to_keep: int = 7) -> int:
        """
        Clean up console log files older than specified days.
        
        Args:
            days_to_keep: Number of days to keep logs
            
        Returns:
            int: Number of log files deleted
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            deleted_count = 0
            for log_file in self.config.LOG_PATH.glob("*console*.txt"):
                if log_file.is_file():
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
            
            self.logger.log_info(f"Cleaned up {deleted_count} old console log files")
            return deleted_count
            
        except Exception as e:
            self.logger.log_exception(e, "Failed to cleanup old console logs")
            return 0


def capture_console_logs(
    driver: webdriver.Chrome,
    test_name: str
) -> Path:
    """
    Convenience function to capture console logs.
    
    Args:
        driver: Selenium WebDriver instance
        test_name: Name of the test case
        
    Returns:
        Path: Path to the saved console log file
    """
    manager = ConsoleLogManager()
    return manager.capture_console_logs(driver, test_name)
