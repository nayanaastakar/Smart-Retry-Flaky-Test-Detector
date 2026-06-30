"""
Report Generator - Module 5

Generates professional HTML reports using Jinja2 templates based on execution evidence.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from config.config import Config


class ReportGenerator:
    """
    Manages generation of HTML execution reports.
    
    Methods:
        generate(website_id, evidence_list)
        save()
        load_latest()
        open_report()
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config.REPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        template_dir = self.config.PROJECT_ROOT / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Add basename filter
        def basename_filter(value):
            return Path(value).name if value else ""
        self.jinja_env.filters['basename'] = basename_filter
        
        self.latest_report_path = None
        self.html_content = None

    def generate(self, website_id: str, evidence_list: list) -> str:
        """
        Generate the HTML report content based on evidence.
        
        Args:
            website_id: The website configured
            evidence_list: List of Evidence objects (or dicts)
            
        Returns:
            String of HTML content
        """
        print("\nGenerating HTML Report...")
        
        # Calculate Statistics
        total_tests = len(evidence_list)
        passed_tests = sum(1 for e in evidence_list if e.get('status') == 'PASS') if evidence_list and isinstance(evidence_list[0], dict) else \
                       sum(1 for e in evidence_list if e.status == 'PASS')
                       
        failed_tests = sum(1 for e in evidence_list if e.get('status') == 'FAILURE') if evidence_list and isinstance(evidence_list[0], dict) else \
                       sum(1 for e in evidence_list if e.status == 'FAILURE')
                       
        flaky_tests = sum(1 for e in evidence_list if e.get('status') == 'FLAKY') if evidence_list and isinstance(evidence_list[0], dict) else \
                      sum(1 for e in evidence_list if e.status == 'FLAKY')
        
        pass_percent = round((passed_tests / total_tests * 100) if total_tests else 0, 1)
        fail_percent = round((failed_tests / total_tests * 100) if total_tests else 0, 1)
        flaky_percent = round((flaky_tests / total_tests * 100) if total_tests else 0, 1)
        
        def get_attr(e, attr):
            return e.get(attr) if isinstance(e, dict) else getattr(e, attr)
            
        total_retries = sum(int(get_attr(e, 'attempts') or 1) - 1 for e in evidence_list)
        avg_retry_count = round((total_retries / total_tests) if total_tests else 0, 1)
        
        total_exec_time = 0.0
        for e in evidence_list:
            time_str = get_attr(e, 'execution_time')
            if time_str and 'sec' in time_str:
                try:
                    total_exec_time += float(time_str.replace(' sec', ''))
                except:
                    pass
        avg_exec_time = round((total_exec_time / total_tests) if total_tests else 0, 1)
        
        # Read CSS content to embed in HTML for portability
        css_content = ""
        css_path = self.config.PROJECT_ROOT / "static" / "css" / "report.css"
        if css_path.exists():
            css_content = css_path.read_text(encoding='utf-8')
            
        # Context data for template
        context = {
            "project_name": "Smart Retry & Flaky Test Detector",
            "website": website_id.capitalize(),
            "execution_date": datetime.now().strftime("%Y-%m-%d"),
            "execution_time": datetime.now().strftime("%H:%M:%S"),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "flaky_tests": flaky_tests,
            "pass_percent": pass_percent,
            "fail_percent": fail_percent,
            "flaky_percent": flaky_percent,
            "avg_retry_count": avg_retry_count,
            "avg_exec_time": avg_exec_time,
            "evidence_list": [e if isinstance(e, dict) else e.to_dict() for e in evidence_list],
            "css_content": css_content
        }
        
        template = self.jinja_env.get_template("report_template.html")
        self.html_content = template.render(**context)
        return self.html_content

    def save(self) -> Path:
        """
        Save the generated HTML to the reports directory.
        """
        if not self.html_content:
            raise ValueError("No report content generated. Call generate() first.")
            
        print("Saving Report...")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{ts}.html"
        self.latest_report_path = self.config.REPORT_PATH / filename
        
        with open(self.latest_report_path, "w", encoding="utf-8") as f:
            f.write(self.html_content)
            
        print(f"{self.config.REPORT_FOLDER}/{filename}")
        print("Report Generated Successfully")
        return self.latest_report_path

    def load_latest(self) -> str:
        """
        Return the HTML content of the latest report.
        """
        reports = sorted(
            self.config.REPORT_PATH.glob("report_*.html"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if reports:
            self.latest_report_path = reports[0]
            return reports[0].read_text(encoding="utf-8")
        return ""

    def open_report(self) -> None:
        """
        Open the latest report in the default web browser.
        """
        import webbrowser
        if self.latest_report_path and self.latest_report_path.exists():
            webbrowser.open(self.latest_report_path.absolute().as_uri())
        else:
            self.logger.warning("No report path available to open.")
