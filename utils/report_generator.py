"""
HTML Report Generator Module for Smart Retry & Flaky Test Detector

This module provides comprehensive HTML report generation with:
- Professional styling with CSS
- Test execution statistics
- Pass/Fail/Flaky breakdown
- AI analysis integration
- Screenshot embedding
- Console log display
- Charts and visualizations
- Dashboard metrics
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json
import base64

from config.config import Config
from core.logger import get_logger


class HTMLReportGenerator:
    """
    Generator for professional HTML test reports.
    
    This class creates comprehensive HTML reports with test execution results,
    statistics, AI analysis, screenshots, and visualizations.
    """
    
    def __init__(self):
        """
        Initialize the HTML Report Generator.
        
        Sets up configuration and logger instance.
        """
        self.config = Config()
        self.logger = get_logger("HTMLReportGenerator")
    
    def generate_report(
        self,
        test_results: List[Dict],
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate a comprehensive HTML report.
        
        Args:
            test_results: List of test result dictionaries
            output_path: Path to save the report (uses config default if not provided)
            
        Returns:
            Path: Path to the generated report file
        """
        try:
            # Generate output path if not provided
            if output_path is None:
                output_path = self.config.get_report_path()
            
            # Calculate statistics
            stats = self._calculate_statistics(test_results)
            
            # Generate HTML content
            html_content = self._generate_html_content(test_results, stats)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.log_info(f"HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.log_exception(e, "Failed to generate HTML report")
            raise
    
    def _calculate_statistics(self, test_results: List[Dict]) -> Dict:
        """
        Calculate test execution statistics.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            Dict: Statistics dictionary
        """
        total_tests = len(test_results)
        passed = sum(1 for r in test_results if r.get("status") == "PASS")
        failed = sum(1 for r in test_results if r.get("status") == "FAILURE")
        flaky = sum(1 for r in test_results if r.get("status") == "FLAKY")
        
        total_retries = sum(r.get("attempts", 1) - 1 for r in test_results)
        avg_retries = total_retries / total_tests if total_tests > 0 else 0
        
        total_duration = sum(r.get("execution_time", 0) for r in test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "flaky": flaky,
            "pass_percentage": round((passed / total_tests * 100) if total_tests > 0 else 0, 2),
            "fail_percentage": round((failed / total_tests * 100) if total_tests > 0 else 0, 2),
            "flaky_percentage": round((flaky / total_tests * 100) if total_tests > 0 else 0, 2),
            "total_retries": total_retries,
            "avg_retries": round(avg_retries, 2),
            "total_duration": round(total_duration, 2),
            "avg_duration": round(avg_duration, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_html_content(self, test_results: List[Dict], stats: Dict) -> str:
        """
        Generate the complete HTML content.
        
        Args:
            test_results: List of test result dictionaries
            stats: Statistics dictionary
            
        Returns:
            str: Complete HTML content
        """
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.REPORT_TITLE}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{self.config.REPORT_TITLE}</h1>
            <p class="timestamp">Generated: {stats['timestamp']}</p>
        </header>
        
        {self._generate_dashboard(stats)}
        
        {self._generate_test_summary_table(test_results)}
        
        {self._generate_detailed_test_results(test_results)}
        
        <footer>
            <p>Smart Retry & Flaky Test Detector Framework</p>
        </footer>
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
"""
        return html
    
    def _get_css_styles(self) -> str:
        """
        Get CSS styles for the report.
        
        Returns:
            str: CSS styles
        """
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .timestamp {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric-card.pass .metric-value { color: #28a745; }
        .metric-card.fail .metric-value { color: #dc3545; }
        .metric-card.flaky .metric-value { color: #ffc107; }
        .metric-card.info .metric-value { color: #17a2b8; }
        
        .section {
            padding: 30px;
        }
        
        .section h2 {
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .status-pass {
            background: #d4edda;
            color: #155724;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: 600;
        }
        
        .status-fail {
            background: #f8d7da;
            color: #721c24;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: 600;
        }
        
        .status-flaky {
            background: #fff3cd;
            color: #856404;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: 600;
        }
        
        .test-details {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        
        .test-details.show {
            display: block;
        }
        
        .toggle-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9em;
        }
        
        .toggle-btn:hover {
            background: #764ba2;
        }
        
        .screenshot {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            margin-top: 10px;
        }
        
        .console-logs {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            max-height: 300px;
            overflow-y: auto;
            margin-top: 10px;
        }
        
        .ai-analysis {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
            border-left: 4px solid #667eea;
        }
        
        .ai-analysis h4 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        
        .chart-container {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 8px;
        }
        
        .progress-bar {
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-fill {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            transition: width 0.5s;
        }
        
        .progress-fill.pass { background: #28a745; }
        .progress-fill.fail { background: #dc3545; }
        .progress-fill.flaky { background: #ffc107; }
        """
    
    def _generate_dashboard(self, stats: Dict) -> str:
        """
        Generate the dashboard section with metrics.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            str: Dashboard HTML
        """
        return f"""
        <div class="dashboard">
            <div class="metric-card pass">
                <div class="metric-value">{stats['passed']}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric-card fail">
                <div class="metric-value">{stats['failed']}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card flaky">
                <div class="metric-value">{stats['flaky']}</div>
                <div class="metric-label">Flaky</div>
            </div>
            <div class="metric-card info">
                <div class="metric-value">{stats['total_tests']}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-card info">
                <div class="metric-value">{stats['pass_percentage']}%</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric-card info">
                <div class="metric-value">{stats['total_retries']}</div>
                <div class="metric-label">Total Retries</div>
            </div>
            <div class="metric-card info">
                <div class="metric-value">{stats['avg_duration']}s</div>
                <div class="metric-label">Avg Duration</div>
            </div>
            <div class="metric-card info">
                <div class="metric-value">{stats['avg_retries']}</div>
                <div class="metric-label">Avg Retries</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Test Distribution</h2>
            <div class="chart-container">
                <div class="progress-bar">
                    <div class="progress-fill pass" style="width: {stats['pass_percentage']}%">
                        {stats['pass_percentage']}% Pass
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill fail" style="width: {stats['fail_percentage']}%">
                        {stats['fail_percentage']}% Fail
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill flaky" style="width: {stats['flaky_percentage']}%">
                        {stats['flaky_percentage']}% Flaky
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_test_summary_table(self, test_results: List[Dict]) -> str:
        """
        Generate the test summary table.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            str: Summary table HTML
        """
        rows = ""
        for i, result in enumerate(test_results):
            status_class = f"status-{result.get('status', 'unknown').lower()}"
            rows += f"""
            <tr>
                <td>{i + 1}</td>
                <td>{result.get('test_name', 'Unknown')}</td>
                <td><span class="{status_class}">{result.get('status', 'Unknown')}</span></td>
                <td>{result.get('attempts', 1)}</td>
                <td>{result.get('execution_time', 0):.2f}s</td>
                <td>
                    <button class="toggle-btn" onclick="toggleDetails({i})">View Details</button>
                </td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>Test Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Attempts</th>
                        <th>Duration</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_detailed_test_results(self, test_results: List[Dict]) -> str:
        """
        Generate detailed test results section.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            str: Detailed results HTML
        """
        details = ""
        for i, result in enumerate(test_results):
            details += f"""
            <div class="test-details" id="details-{i}">
                <h3>{result.get('test_name', 'Unknown')}</h3>
                <p><strong>Status:</strong> {result.get('status', 'Unknown')}</p>
                <p><strong>Attempts:</strong> {result.get('attempts', 1)}</p>
                <p><strong>Duration:</strong> {result.get('execution_time', 0):.2f}s</p>
                
                {self._generate_exception_section(result)}
                {self._generate_screenshot_section(result)}
                {self._generate_console_logs_section(result)}
                {self._generate_ai_analysis_section(result)}
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>Detailed Test Results</h2>
            {details}
        </div>
        """
    
    def _generate_exception_section(self, result: Dict) -> str:
        """
        Generate exception information section.
        
        Args:
            result: Test result dictionary
            
        Returns:
            str: Exception section HTML
        """
        exceptions = result.get('exceptions', [])
        if not exceptions:
            return ""
        
        exception_text = "<br>".join(str(e) for e in exceptions)
        return f"""
        <h4>Exceptions</h4>
        <div class="console-logs">{exception_text}</div>
        """
    
    def _generate_screenshot_section(self, result: Dict) -> str:
        """
        Generate screenshot section.
        
        Args:
            result: Test result dictionary
            
        Returns:
            str: Screenshot section HTML
        """
        if not self.config.INCLUDE_SCREENSHOTS:
            return ""
        
        screenshot_path = result.get('screenshot_path')
        if not screenshot_path:
            return ""
        
        try:
            # Try to embed screenshot as base64
            with open(screenshot_path, 'rb') as f:
                screenshot_data = base64.b64encode(f.read()).decode('utf-8')
            
            return f"""
            <h4>Screenshot</h4>
            <img src="data:image/png;base64,{screenshot_data}" class="screenshot" alt="Failure Screenshot">
            """
        except Exception:
            return f"""
            <h4>Screenshot</h4>
            <p>Screenshot saved at: {screenshot_path}</p>
            """
    
    def _generate_console_logs_section(self, result: Dict) -> str:
        """
        Generate console logs section.
        
        Args:
            result: Test result dictionary
            
        Returns:
            str: Console logs section HTML
        """
        if not self.config.INCLUDE_CONSOLE_LOGS:
            return ""
        
        console_logs = result.get('console_logs')
        if not console_logs:
            return ""
        
        return f"""
        <h4>Console Logs</h4>
        <div class="console-logs">{console_logs}</div>
        """
    
    def _generate_ai_analysis_section(self, result: Dict) -> str:
        """
        Generate AI analysis section.
        
        Args:
            result: Test result dictionary
            
        Returns:
            str: AI analysis section HTML
        """
        if not self.config.INCLUDE_AI_ANALYSIS:
            return ""
        
        ai_analysis = result.get('ai_analysis')
        if not ai_analysis:
            return ""
        
        analysis_html = f"""
        <p><strong>Classification:</strong> {ai_analysis.get('classification', 'N/A')}</p>
        <p><strong>Root Cause:</strong> {ai_analysis.get('root_cause', 'N/A')}</p>
        <p><strong>Suggested Fix:</strong> {ai_analysis.get('suggested_fix', 'N/A')}</p>
        <p><strong>Confidence:</strong> {ai_analysis.get('confidence_score', 0):.2f}</p>
        """
        
        return f"""
        <h4>AI Analysis</h4>
        <div class="ai-analysis">
            {analysis_html}
        </div>
        """
    
    def _get_javascript(self) -> str:
        """
        Get JavaScript for interactive features.
        
        Returns:
            str: JavaScript code
        """
        return """
        function toggleDetails(index) {
            var details = document.getElementById('details-' + index);
            details.classList.toggle('show');
        }
        """


def generate_html_report(test_results: List[Dict], output_path: Optional[Path] = None) -> Path:
    """
    Convenience function to generate an HTML report.
    
    Args:
        test_results: List of test result dictionaries
        output_path: Path to save the report (optional)
        
    Returns:
        Path: Path to the generated report file
    """
    generator = HTMLReportGenerator()
    return generator.generate_report(test_results, output_path)
