"""
core/job_manager.py
=====================
Runs long test executions on a background thread so the browser request
returns immediately, and exposes progress (percentage + colored log events)
that the progress page polls.

Design notes / honest limits:
- Jobs live in process memory. That is fine for the Flask dev server or a
  single-process deployment; with multiple gunicorn workers a job started in
  one worker would not be visible from another. Use one worker, or move this
  to a shared store (Redis/DB) if you scale out.
- Finished jobs are pruned (oldest first) once MAX_JOBS is exceeded.
- Each thread gets its own SQLite connection (db_manager uses thread-local
  connections), so running DB writes from the job thread is safe.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger("smart_retry.jobs")

MAX_JOBS = 50
MAX_EVENTS = 1000


@dataclass
class Job:
    id: str
    title: str
    status: str = "queued"          # queued | running | done | error
    total: int = 0
    done: int = 0
    events: list[dict] = field(default_factory=list)
    result_url: str | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def log(self, level: str, message: str) -> None:
        with self._lock:
            if len(self.events) < MAX_EVENTS:
                self.events.append(
                    {"id": len(self.events) + 1, "ts": time.strftime("%H:%M:%S"), "level": level, "message": message}
                )

    def set_total(self, total: int) -> None:
        self.total = max(0, total)

    def advance(self, n: int = 1) -> None:
        self.done += n
        if self.total:
            self.done = min(self.done, self.total)

    @property
    def percent(self) -> int:
        if self.status == "done":
            return 100
        if not self.total:
            return 0
        return min(100, int(self.done * 100 / self.total))

    def snapshot(self, since_event_id: int = 0) -> dict:
        with self._lock:
            new_events = [e for e in self.events if e["id"] > since_event_id]
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "percent": self.percent,
            "done": self.done,
            "total": self.total,
            "events": new_events,
            "result_url": self.result_url,
            "error": self.error,
        }


_jobs: dict[str, Job] = {}
_jobs_lock = threading.Lock()


def _prune() -> None:
    if len(_jobs) <= MAX_JOBS:
        return
    finished = sorted((j for j in _jobs.values() if j.status in ("done", "error")), key=lambda j: j.created_at)
    for job in finished[: len(_jobs) - MAX_JOBS]:
        _jobs.pop(job.id, None)


def start_job(title: str, target: Callable[[Job], str | None]) -> Job:
    """Start `target(job)` on a daemon thread. `target` may return a URL to
    redirect to when finished; raising an exception marks the job as errored."""
    job = Job(id=uuid.uuid4().hex[:16], title=title)
    with _jobs_lock:
        _jobs[job.id] = job
        _prune()

    def runner() -> None:
        job.status = "running"
        job.log("info", f"Started: {title}")
        try:
            job.result_url = target(job)
            job.status = "done"
            job.log("success", "Run complete.")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Background job %s failed", job.id)
            job.error = str(exc)
            job.status = "error"
            job.log("error", f"Run failed: {exc}")

    threading.Thread(target=runner, name=f"job-{job.id}", daemon=True).start()
    return job


def get_job(job_id: str) -> Job | None:
    with _jobs_lock:
        return _jobs.get(job_id)
