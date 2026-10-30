"""
database/db_manager.py
=======================
Lightweight SQLite access layer. No heavy ORM is used on purpose -- this is a
QA tooling project, not a transactional banking system, so raw SQL behind a
small, well-typed helper keeps things transparent and dependency-light while
still being safe (parameterized queries everywhere).
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from config import settings

_local = threading.local()

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    full_name       TEXT,
    avatar_color    TEXT DEFAULT '#6366f1',
    role            TEXT DEFAULT 'engineer',
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    last_login_at   TEXT
);

CREATE TABLE IF NOT EXISTS projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT UNIQUE NOT NULL,
    url             TEXT NOT NULL,
    browser         TEXT DEFAULT 'chrome',
    tags            TEXT DEFAULT '[]',
    notes           TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS website_profiles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT UNIQUE NOT NULL,
    base_url        TEXT NOT NULL,
    description     TEXT,
    icon            TEXT DEFAULT 'fa-globe',
    config_json     TEXT NOT NULL,
    is_builtin      INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_cases (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    module          TEXT NOT NULL,
    website_profile TEXT,
    project_id      INTEGER,
    steps_json      TEXT DEFAULT '[]',
    description     TEXT,
    tags            TEXT DEFAULT '[]',
    group_name      TEXT DEFAULT 'default',
    enabled         INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS executions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT NOT NULL,
    test_name           TEXT NOT NULL,
    module              TEXT,
    website_profile     TEXT,
    status              TEXT NOT NULL,           -- PASS | FAIL | FLAKY | RUNNING | SKIPPED
    attempt_count       INTEGER DEFAULT 1,
    max_retries         INTEGER DEFAULT 0,
    retry_success       INTEGER DEFAULT 0,        -- 1 if it passed only after retrying
    duration_ms         INTEGER DEFAULT 0,
    browser             TEXT,
    os_name             TEXT,
    exception_type      TEXT,
    exception_message   TEXT,
    stack_trace         TEXT,
    console_logs        TEXT,
    screenshot_path     TEXT,
    browser_version     TEXT,
    started_at          TEXT DEFAULT CURRENT_TIMESTAMP,
    finished_at         TEXT,
    ai_analysis_id      INTEGER,
    FOREIGN KEY (ai_analysis_id) REFERENCES ai_analyses(id)
);

CREATE TABLE IF NOT EXISTS retry_attempts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id    INTEGER NOT NULL,
    attempt_number  INTEGER NOT NULL,
    status          TEXT NOT NULL,
    duration_ms     INTEGER DEFAULT 0,
    error_message   TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS flaky_history (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name           TEXT NOT NULL,
    module              TEXT,
    flaky_score         REAL DEFAULT 0,
    total_runs          INTEGER DEFAULT 0,
    pass_count          INTEGER DEFAULT 0,
    fail_count          INTEGER DEFAULT 0,
    flip_count          INTEGER DEFAULT 0,
    classification       TEXT DEFAULT 'STABLE',   -- STABLE | FLAKY | CHRONIC_FAILURE
    last_evaluated_at   TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_name, module)
);

CREATE TABLE IF NOT EXISTS ai_analyses (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id            INTEGER NOT NULL,
    root_cause              TEXT,
    severity                TEXT,
    possible_reason         TEXT,
    recommended_fix         TEXT,
    prevention               TEXT,
    confidence_score        REAL,
    suggested_code          TEXT,
    raw_model_output        TEXT,
    model_name              TEXT,
    created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    report_type     TEXT NOT NULL,   -- html | pdf | json | csv
    file_path       TEXT NOT NULL,
    total_tests     INTEGER DEFAULT 0,
    passed          INTEGER DEFAULT 0,
    failed          INTEGER DEFAULT 0,
    flaky           INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_executions_test_name ON executions(test_name);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_started_at ON executions(started_at);
CREATE INDEX IF NOT EXISTS idx_retry_attempts_execution ON retry_attempts(execution_id);
"""


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=30.0, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_connection() -> sqlite3.Connection:
    """Return a thread-local SQLite connection (SQLite connections are not
    safe to share across threads, so each thread gets its own)."""
    if not hasattr(_local, "conn"):
        _local.conn = _connect(settings.DATABASE_PATH)
    return _local.conn


@contextmanager
def get_cursor(commit: bool = False) -> Iterator[sqlite3.Cursor]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def _migrate_existing_schema(conn: sqlite3.Connection) -> None:
    """Add columns/tables introduced after a database's initial creation.

    SQLite's CREATE TABLE IF NOT EXISTS won't retrofit new columns onto a
    table that already exists from an older version of this app, so any
    database created before the `projects` feature needs an explicit
    ALTER TABLE. This is deliberately simple (PRAGMA-check then ALTER)
    rather than a full migration framework, since the schema is small and
    changes infrequently.
    """
    existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(test_cases)").fetchall()}
    if "project_id" not in existing_cols:
        conn.execute("ALTER TABLE test_cases ADD COLUMN project_id INTEGER")
    if "steps_json" not in existing_cols:
        conn.execute("ALTER TABLE test_cases ADD COLUMN steps_json TEXT DEFAULT '[]'")
    exec_cols = {row[1] for row in conn.execute("PRAGMA table_info(executions)").fetchall()}
    if "browser_version" not in exec_cols:
        conn.execute("ALTER TABLE executions ADD COLUMN browser_version TEXT")
    conn.commit()


def init_db() -> None:
    """Create all tables/indexes if they do not already exist. Idempotent."""
    settings.ensure_directories()
    conn = _connect(settings.DATABASE_PATH)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        _migrate_existing_schema(conn)
    finally:
        conn.close()


def execute(query: str, params: tuple[Any, ...] = ()) -> int:
    """Execute an INSERT/UPDATE/DELETE and return lastrowid."""
    with get_cursor(commit=True) as cur:
        cur.execute(query, params)
        return cur.lastrowid


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()
