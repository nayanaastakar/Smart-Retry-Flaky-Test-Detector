"""
services/report_service.py
============================
Module 5: Professional Reporting.

Generates a report from a batch of executions (by run_id, by date range, or
"all"). Every format shares the same underlying data assembly so the HTML,
PDF, JSON, and CSV outputs never drift out of sync with each other.
"""

from __future__ import annotations

import base64
import csv
import io
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from flask import render_template
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak,
)

from config import settings
from database.db_manager import execute, fetch_all

ReportType = Literal["html", "pdf", "json", "csv"]


def _gather_executions(run_id: str | None = None, limit: int = 200) -> list[dict]:
    if run_id:
        rows = fetch_all(
            "SELECT * FROM executions WHERE run_id = ? ORDER BY id ASC", (run_id,)
        )
    else:
        rows = fetch_all(
            "SELECT * FROM executions ORDER BY id DESC LIMIT ?", (limit,)
        )
    executions = []
    for r in rows:
        e = dict(r)
        ai = fetch_all("SELECT * FROM ai_analyses WHERE execution_id = ? LIMIT 1", (e["id"],))
        e["ai_analysis"] = dict(ai[0]) if ai else None
        e["screenshot_b64"] = _embed_screenshot(e.get("screenshot_path"))
        executions.append(e)
    return executions


def _embed_screenshot(rel_path: str | None, max_bytes: int = 1_500_000) -> str | None:
    """Return the screenshot as a base64 string so HTML reports are self-contained.
    Skips missing files and anything outside the screenshots dir or over max_bytes."""
    if not rel_path:
        return None
    try:
        full = (settings.BASE_DIR / rel_path).resolve()
        if settings.SCREENSHOTS_DIR.resolve() not in full.parents or not full.is_file():
            return None
        if full.stat().st_size > max_bytes:
            return None
        return base64.b64encode(full.read_bytes()).decode("ascii")
    except OSError:
        return None


def _summarize(executions: list[dict]) -> dict:
    total = len(executions)
    passed = sum(1 for e in executions if e["status"] in ("PASS", "FLAKY"))
    failed = sum(1 for e in executions if e["status"] == "FAIL")
    flaky = sum(1 for e in executions if e["status"] == "FLAKY")
    return {"total": total, "passed": passed, "failed": failed, "flaky": flaky}


class ReportService:
    def __init__(self) -> None:
        settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    def generate(self, report_type: ReportType, run_id: str | None = None, limit: int = 200) -> dict:
        executions = _gather_executions(run_id=run_id, limit=limit)
        summary = _summarize(executions)
        batch_id = run_id or f"batch-{uuid.uuid4().hex[:8]}"

        if report_type == "html":
            file_path = self._generate_html(executions, summary, batch_id)
        elif report_type == "pdf":
            file_path = self._generate_pdf(executions, summary, batch_id)
        elif report_type == "json":
            file_path = self._generate_json(executions, summary, batch_id)
        elif report_type == "csv":
            file_path = self._generate_csv(executions, summary, batch_id)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

        report_id = execute(
            """INSERT INTO reports (run_id, report_type, file_path, total_tests, passed, failed, flaky)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (batch_id, report_type, str(file_path.relative_to(settings.BASE_DIR)),
             summary["total"], summary["passed"], summary["failed"], summary["flaky"]),
        )
        return {"report_id": report_id, "file_path": str(file_path), "batch_id": batch_id, "summary": summary}

    # ------------------------------------------------------------------ #
    def _generate_html(self, executions: list[dict], summary: dict, batch_id: str) -> Path:
        html = render_template(
            "reports/report.html",
            report_title="Test Execution Report",
            company_name=settings.COMPANY_NAME,
            logo_text=settings.REPORT_LOGO_TEXT,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            run_id=batch_id,
            summary=summary,
            executions=executions,
        )
        path = settings.REPORTS_DIR / f"{batch_id}.html"
        path.write_text(html, encoding="utf-8")
        return path

    def _generate_pdf(self, executions: list[dict], summary: dict, batch_id: str) -> Path:
        path = settings.REPORTS_DIR / f"{batch_id}.pdf"
        doc = SimpleDocTemplate(
            str(path), pagesize=A4,
            leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontSize=18, spaceAfter=4)
        sub_style = ParagraphStyle("SubX", parent=styles["Normal"], textColor=colors.HexColor("#5A6480"), fontSize=9)
        section_style = ParagraphStyle("SectionX", parent=styles["Heading2"], fontSize=12.5, spaceBefore=16, spaceAfter=8)
        mono_style = ParagraphStyle("MonoX", parent=styles["Code"], fontSize=7.5, leading=9.5, textColor=colors.HexColor("#B0304A"))
        body_style = ParagraphStyle("BodyX", parent=styles["Normal"], fontSize=9)

        story = [
            Paragraph(f"{settings.REPORT_LOGO_TEXT} &mdash; Test Execution Report", title_style),
            Paragraph(f"{settings.COMPANY_NAME} &middot; Run ID: {batch_id} &middot; "
                      f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", sub_style),
            Spacer(1, 14),
        ]

        summary_table = Table(
            [["Total", "Passed", "Failed", "Flaky"],
             [str(summary["total"]), str(summary["passed"]), str(summary["failed"]), str(summary["flaky"])]],
            colWidths=[100] * 4,
        )
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#171F30")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F4F6FB")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D3D9E6")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Paragraph("Execution Timeline", section_style))

        rows = [["Test", "Module", "Status", "Attempts", "Duration", "Browser"]]
        for e in executions:
            rows.append([
                e["test_name"][:38], e["module"] or "-", e["status"], str(e["attempt_count"]),
                f"{(e['duration_ms'] or 0) / 1000:.2f}s", e["browser"] or "-",
            ])
        exec_table = Table(rows, colWidths=[150, 65, 55, 50, 55, 60], repeatRows=1)
        status_colors = {"PASS": colors.HexColor("#22C88E"), "FAIL": colors.HexColor("#F4506B"), "FLAKY": colors.HexColor("#F5A623")}
        table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#171F30")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D3D9E6")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
        for idx, e in enumerate(executions, start=1):
            color = status_colors.get(e["status"])
            if color:
                table_style.append(("TEXTCOLOR", (2, idx), (2, idx), color))
        exec_table.setStyle(TableStyle(table_style))
        story.append(exec_table)

        failed_or_flaky = [e for e in executions if e["status"] in ("FAIL", "FLAKY")]
        if failed_or_flaky:
            story.append(Paragraph("Failure &amp; Flaky Details", section_style))
            for e in failed_or_flaky[:25]:
                story.append(Paragraph(f"<b>{e['test_name']}</b> &mdash; {e['status']}", body_style))
                if e.get("exception_message"):
                    story.append(Paragraph(e["exception_message"][:300], mono_style))
                if e.get("ai_analysis"):
                    ai = e["ai_analysis"]
                    story.append(Paragraph(
                        f"<b>AI Root Cause:</b> {ai.get('root_cause','-')}<br/>"
                        f"<b>Recommended Fix:</b> {ai.get('recommended_fix','-')}", body_style))
                story.append(Spacer(1, 8))

        doc.build(story)
        return path

    def _generate_json(self, executions: list[dict], summary: dict, batch_id: str) -> Path:
        path = settings.REPORTS_DIR / f"{batch_id}.json"
        payload = {
            "batch_id": batch_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "executions": executions,
        }
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return path

    def _generate_csv(self, executions: list[dict], summary: dict, batch_id: str) -> Path:
        path = settings.REPORTS_DIR / f"{batch_id}.csv"
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Test Name", "Module", "Status", "Attempts", "Retry Saved",
                          "Duration (ms)", "Browser", "OS", "Started At", "Exception"])
        for e in executions:
            writer.writerow([
                e["test_name"], e["module"], e["status"], e["attempt_count"], e["retry_success"],
                e["duration_ms"], e["browser"], e["os_name"], e["started_at"], e.get("exception_message") or "",
            ])
        path.write_text(buffer.getvalue(), encoding="utf-8")
        return path
