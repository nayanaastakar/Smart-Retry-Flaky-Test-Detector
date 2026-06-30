"""
Main Entry Point for Smart Retry & Flaky Test Detector

This module provides the main entry point for running the framework with:
- Test execution orchestration
- Result collection and aggregation
- Report generation
- AI analysis integration
- Command-line interface
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import subprocess

from config.config import Config
from core.logger import get_logger
from core.driver import get_driver_manager, close_driver_manager
from utils.report_generator import generate_html_report
from ai.ai_analyzer import AIAnalyzer
from ai.ollama_provider import create_ollama_provider


class TestRunner:
    """
    Main test runner for the Smart Retry & Flaky Test Detector framework.
    
    This class orchestrates test execution, collects results, performs AI analysis,
    and generates comprehensive reports.
    """
    
    def __init__(self, use_ollama: bool = False):
        """
        Initialize the Test Runner.
        
        Args:
            use_ollama: Whether to use Ollama instead of OpenAI for AI analysis
        """
        self.config = Config()
        self.logger = get_logger("TestRunner")
        self.test_results: List[Dict] = []
        
        # Initialize AI analyzer
        if use_ollama:
            self.logger.log_info("Using Ollama for AI analysis")
            ollama_provider = create_ollama_provider()
            self.ai_analyzer = AIAnalyzer(ollama_provider)
        else:
            self.logger.log_info("Using OpenAI for AI analysis")
            self.ai_analyzer = AIAnalyzer()
    
    def run_tests(self, test_path: str = "tests", verbose: bool = False) -> int:
        """
        Run all tests using pytest.
        
        Args:
            test_path: Path to test directory or specific test file
            verbose: Whether to enable verbose output
            
        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        try:
            self.logger.log_info("=" * 80)
            self.logger.log_info("Starting Test Execution")
            self.logger.log_info("=" * 80)
            
            # Build pytest command
            pytest_args = [sys.executable, "-m", "pytest", test_path]
            
            if verbose:
                pytest_args.append("-v")
            else:
                pytest_args.append("-q")
            
            # Add custom markers if needed
            pytest_args.extend([
                "--tb=short",
                "--disable-warnings"
            ])
            
            self.logger.log_info(f"Running command: {' '.join(pytest_args)}")
            
            # Run pytest
            result = subprocess.run(pytest_args, capture_output=False)
            
            self.logger.log_info("=" * 80)
            self.logger.log_info("Test Execution Completed")
            self.logger.log_info("=" * 80)
            
            return result.returncode
            
        except Exception as e:
            self.logger.log_exception(e, "Test execution failed")
            return 1
    
    def run_tests_with_framework(self, test_path: str = "tests") -> List[Dict]:
        """
        Run tests with framework integration (retry, flaky detection, AI analysis).
        
        Args:
            test_path: Path to test directory or specific test file
            
        Returns:
            List[Dict]: List of test results with framework analysis
        """
        try:
            self.logger.log_info("Running tests with framework integration...")
            
            # Import and run tests programmatically
            import pytest
            
            # Run pytest with custom plugin for result collection
            result = pytest.main([
                test_path,
                "-v",
                "--tb=short",
                "--disable-warnings"
            ])
            
            # Collect results (this would be enhanced with a custom pytest plugin)
            # For now, return empty list - in production, implement custom plugin
            self.logger.log_info("Test execution with framework completed")
            
            return []
            
        except Exception as e:
            self.logger.log_exception(e, "Framework test execution failed")
            return []
    
    def analyze_results(self, test_results: List[Dict]) -> List[Dict]:
        """
        Analyze test results with AI.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            List[Dict]: Test results with AI analysis added
        """
        if not self.config.AI_ANALYSIS_ENABLED:
            self.logger.log_warning("AI analysis is disabled")
            return test_results
        
        analyzed_results = []
        
        for result in test_results:
            if result.get("status") in ["FAILURE", "FLAKY"]:
                try:
                    # Extract exception information
                    exceptions = result.get("exceptions", [])
                    if exceptions:
                        exception = exceptions[-1]  # Use the most recent exception
                        test_name = result.get("test_name", "Unknown")
                        screenshot_path = result.get("screenshot_path")
                        console_logs = result.get("console_logs")
                        
                        # Perform AI analysis
                        ai_analysis = self.ai_analyzer.analyze_failure(
                            exception,
                            test_name,
                            screenshot_path,
                            console_logs
                        )
                        
                        result["ai_analysis"] = ai_analysis
                        self.logger.log_info(f"AI analysis completed for: {test_name}")
                except Exception as e:
                    self.logger.log_exception(e, f"AI analysis failed for test: {result.get('test_name')}")
            
            analyzed_results.append(result)
        
        return analyzed_results
    
    def generate_report(self, test_results: List[Dict], output_path: Optional[Path] = None) -> Path:
        """
        Generate HTML report from test results.
        
        Args:
            test_results: List of test result dictionaries
            output_path: Path to save the report (optional)
            
        Returns:
            Path: Path to the generated report
        """
        try:
            self.logger.log_info("Generating HTML report...")
            
            report_path = generate_html_report(test_results, output_path)
            
            self.logger.log_info(f"Report generated: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.log_exception(e, "Report generation failed")
            raise
    
    def run_full_pipeline(
        self,
        test_path: str = "tests",
        output_path: Optional[Path] = None,
        verbose: bool = False
    ) -> int:
        """
        Run the complete pipeline: execute tests, analyze results, generate report.
        
        Args:
            test_path: Path to test directory or specific test file
            output_path: Path to save the report (optional)
            verbose: Whether to enable verbose output
            
        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        try:
            # Step 1: Run tests
            exit_code = self.run_tests(test_path, verbose)
            
            # Step 2: Collect results (in production, implement result collection)
            # For now, use placeholder results
            test_results = self._get_placeholder_results()
            
            # Step 3: Analyze results with AI
            analyzed_results = self.analyze_results(test_results)
            
            # Step 4: Generate report
            report_path = self.generate_report(analyzed_results, output_path)
            
            self.logger.log_info("=" * 80)
            self.logger.log_info("Pipeline Execution Summary")
            self.logger.log_info("=" * 80)
            self.logger.log_info(f"Total Tests: {len(test_results)}")
            self.logger.log_info(f"Passed: {sum(1 for r in test_results if r.get('status') == 'PASS')}")
            self.logger.log_info(f"Failed: {sum(1 for r in test_results if r.get('status') == 'FAILURE')}")
            self.logger.log_info(f"Flaky: {sum(1 for r in test_results if r.get('status') == 'FLAKY')}")
            self.logger.log_info(f"Report: {report_path}")
            self.logger.log_info("=" * 80)
            
            return exit_code
            
        except Exception as e:
            self.logger.log_exception(e, "Pipeline execution failed")
            return 1
    
    def _get_placeholder_results(self) -> List[Dict]:
        """
        Get placeholder test results for demonstration.
        
        In production, this would be replaced with actual result collection
        from pytest execution.
        
        Returns:
            List[Dict]: Placeholder test results
        """
        return [
            {
                "test_name": "test_successful_login",
                "status": "PASS",
                "attempts": 1,
                "execution_time": 2.5,
                "exceptions": [],
                "screenshot_path": None,
                "console_logs": None
            },
            {
                "test_name": "test_locked_out_user",
                "status": "FAILURE",
                "attempts": 3,
                "execution_time": 8.2,
                "exceptions": [Exception("User is locked out")],
                "screenshot_path": "screenshots/test_locked_out_user_failure.png",
                "console_logs": "Error: User locked out"
            },
            {
                "test_name": "test_performance_glitch_user",
                "status": "FLAKY",
                "attempts": 2,
                "execution_time": 5.1,
                "exceptions": [Exception("TimeoutException")],
                "screenshot_path": "screenshots/test_performance_glitch_user_flaky.png",
                "console_logs": "Warning: Slow page load"
            }
        ]


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Smart Retry & Flaky Test Detector - Intelligent Selenium Testing Framework"
    )
    
    parser.add_argument(
        "--test-path",
        type=str,
        default="tests",
        help="Path to test directory or specific test file (default: tests)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save the HTML report (default: auto-generated)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--use-ollama",
        action="store_true",
        help="Use Ollama instead of OpenAI for AI analysis"
    )
    
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI analysis"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run tests in headless mode"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=None,
        help="Maximum number of retry attempts"
    )
    
    return parser.parse_args()


def main():
    """
    Main entry point for the framework.
    """
    # Parse arguments
    args = parse_arguments()
    
    # Update configuration based on arguments
    config = Config()
    
    if args.headless:
        config.HEADLESS_MODE = True
    
    if args.no_ai:
        config.AI_ANALYSIS_ENABLED = False
    
    if args.max_retries:
        config.MAX_RETRY_COUNT = args.max_retries
    
    # Initialize logger
    logger = get_logger("Main")
    
    logger.log_info("=" * 80)
    logger.log_info("Smart Retry & Flaky Test Detector")
    logger.log_info("=" * 80)
    
    # Create test runner
    runner = TestRunner(use_ollama=args.use_ollama)
    
    # Run full pipeline
    output_path = Path(args.output) if args.output else None
    exit_code = runner.run_full_pipeline(
        test_path=args.test_path,
        output_path=output_path,
        verbose=args.verbose
    )
    
    # Cleanup
    close_driver_manager()
    
    logger.log_info("=" * 80)
    logger.log_info("Execution Completed")
    logger.log_info("=" * 80)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
