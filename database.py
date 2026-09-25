# -*- coding: utf-8 -*-
"""
database.py - Personal device SQLite database for tracking requests and responses in JevTools.

Provides zero-dependency, local-first request/response audit logging and persistence:
  - Tracks all outgoing requests sent to Jev / TypeSafe / OpenRouter
  - Tracks all incoming responses, decisions, probabilities, and errors
  - Measures and persists TTFT (Time To First Token) and total inference latency
  - Stores data locally on the user's personal device in a gitignored SQLite database
  - Provides thread-safe connection pooling, WAL mode, queries, and analytics
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator, Optional
import json
import logging
import os
import sqlite3

logger = logging.getLogger("jevtools.database")

# Default database location in the project directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_FILENAME = "jevtools.db"


def get_default_db_path() -> str:
    """Return the absolute path to the local personal device database file."""
    return os.environ.get("JEV_DB_PATH", os.path.join(CURRENT_DIR, DEFAULT_DB_FILENAME))


@contextmanager
def get_connection(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager yielding a thread-safe SQLite connection configured with
    Write-Ahead Logging (WAL) and Row dictionary factory.
    """
    path = db_path or get_default_db_path()
    dir_name = os.path.dirname(os.path.abspath(path))
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    conn = sqlite3.connect(path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initialize the database schema, creating tables and indexes if they do not exist.
    """
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                provider TEXT,
                model TEXT,
                endpoint TEXT,
                status TEXT DEFAULT 'success',
                ttft_ms REAL DEFAULT 0.0,
                elapsed_ms REAL DEFAULT 0.0,
                is_mock INTEGER DEFAULT 0,
                request_payload TEXT,
                response_payload TEXT,
                error_message TEXT,
                client_info TEXT
            );
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_request_logs_timestamp
            ON request_logs(timestamp DESC);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_request_logs_action
            ON request_logs(action_type);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_request_logs_status
            ON request_logs(status);
        """)


def _safe_serialize(obj: Any) -> str:
    """Serialize an object or primitive to formatted JSON, gracefully handling non-serializables."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except Exception:
        return str(obj)


def log_interaction(
    action_type: str,
    request_payload: Any,
    response_payload: Any = None,
    provider: str = "openrouter",
    model: str = "",
    endpoint: str = "",
    status: str = "success",
    ttft_ms: float = 0.0,
    elapsed_ms: float = 0.0,
    is_mock: bool = False,
    error_message: Optional[str] = None,
    client_info: str = "web_ui",
    db_path: Optional[str] = None,
) -> Optional[int]:
    """
    Log an outgoing request and its incoming response or error to the local SQLite database.
    Fails safely without interrupting the primary application logic if DB writes fail.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    req_json = _safe_serialize(request_payload)
    resp_json = _safe_serialize(response_payload) if response_payload is not None else None
    err_str = str(error_message) if error_message is not None else None

    try:
        init_db(db_path)
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO request_logs (
                    timestamp, action_type, provider, model, endpoint,
                    status, ttft_ms, elapsed_ms, is_mock,
                    request_payload, response_payload, error_message, client_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                timestamp,
                action_type,
                provider or "openrouter",
                model or "",
                endpoint or "",
                status,
                float(ttft_ms or 0.0),
                float(elapsed_ms or 0.0),
                1 if is_mock else 0,
                req_json,
                resp_json,
                err_str,
                client_info or "unknown",
            ))
            return cursor.lastrowid
    except Exception as exc:
        logger.warning(f"Failed to log interaction to local database ({db_path or get_default_db_path()}): {exc}")
        return None


def get_history(
    limit: int = 50,
    offset: int = 0,
    action_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db_path: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Query logged requests and responses from the local database, ordered newest first.
    Supports filtering by action_type, status, search term, and pagination.
    """
    init_db(db_path)
    query = "SELECT * FROM request_logs WHERE 1=1"
    params: list[Any] = []

    if action_type:
        query += " AND action_type = ?"
        params.append(action_type)

    if status:
        query += " AND status = ?"
        params.append(status)

    if search:
        query += " AND (request_payload LIKE ? OR response_payload LIKE ? OR error_message LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([max(1, limit), max(0, offset)])

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    results: list[dict[str, Any]] = []
    for r in rows:
        item = dict(r)
        # Parse JSON payloads if possible for structured client consumption
        for field_name in ("request_payload", "response_payload"):
            val = item.get(field_name)
            if val and isinstance(val, str):
                try:
                    item[field_name] = json.loads(val)
                except Exception:
                    pass
        item["is_mock"] = bool(item.get("is_mock"))
        results.append(item)

    return results


def get_request(request_id: int, db_path: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Retrieve a single request/response log entry by its primary key."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM request_logs WHERE id = ?;", (request_id,))
        row = cursor.fetchone()
        if not row:
            return None

        item = dict(row)
        for field_name in ("request_payload", "response_payload"):
            val = item.get(field_name)
            if val and isinstance(val, str):
                try:
                    item[field_name] = json.loads(val)
                except Exception:
                    pass
        item["is_mock"] = bool(item.get("is_mock"))
        return item


def clear_history(db_path: Optional[str] = None) -> int:
    """Clear all request/response history from the local database. Returns deleted count."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM request_logs;")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM request_logs;")

    # VACUUM must run outside an explicit transaction with isolation_level=None (autocommit)
    try:
        path = db_path or get_default_db_path()
        vacuum_conn = sqlite3.connect(path, isolation_level=None)
        vacuum_conn.execute("VACUUM;")
        vacuum_conn.close()
    except Exception as exc:
        logger.debug(f"VACUUM skipped or encountered non-critical error: {exc}")

    return count


def get_stats(db_path: Optional[str] = None) -> dict[str, Any]:
    """
    Calculate summary statistics across all logged requests on the personal device.
    """
    init_db(db_path)
    path = db_path or get_default_db_path()
    file_size_bytes = os.path.getsize(path) if os.path.exists(path) else 0

    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_count,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success_count,
                SUM(CASE WHEN status != 'success' THEN 1 ELSE 0 END) AS error_count,
                SUM(CASE WHEN is_mock = 1 THEN 1 ELSE 0 END) AS mock_count,
                SUM(CASE WHEN is_mock = 0 THEN 1 ELSE 0 END) AS live_count,
                AVG(CASE WHEN ttft_ms > 0 THEN ttft_ms ELSE NULL END) AS avg_ttft_ms,
                AVG(CASE WHEN elapsed_ms > 0 THEN elapsed_ms ELSE NULL END) AS avg_latency_ms
            FROM request_logs;
        """)
        row = cursor.fetchone()

        cursor.execute("""
            SELECT action_type, COUNT(*) as count
            FROM request_logs
            GROUP BY action_type;
        """)
        action_breakdown = {r["action_type"]: r["count"] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT provider, COUNT(*) as count
            FROM request_logs
            GROUP BY provider;
        """)
        provider_breakdown = {r["provider"]: r["count"] for r in cursor.fetchall()}

    return {
        "db_path": path,
        "db_filename": os.path.basename(path),
        "db_size_bytes": file_size_bytes,
        "db_size_kb": round(file_size_bytes / 1024, 2),
        "total_requests": row["total_count"] or 0,
        "success_count": row["success_count"] or 0,
        "error_count": row["error_count"] or 0,
        "mock_count": row["mock_count"] or 0,
        "live_count": row["live_count"] or 0,
        "avg_ttft_ms": round(row["avg_ttft_ms"] or 0.0, 2),
        "avg_latency_ms": round(row["avg_latency_ms"] or 0.0, 2),
        "action_breakdown": action_breakdown,
        "provider_breakdown": provider_breakdown,
    }
