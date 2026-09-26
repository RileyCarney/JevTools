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
from typing import Any, Generator, Optional, TypedDict, cast
import json
import logging
import os
import sqlite3

logger = logging.getLogger("jevtools.database")

# Default database location in the project directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_FILENAME = "jevtools.db"

MAX_SEARCH_LENGTH = 200
MAX_QUERY_LIMIT = 500

# Backward compatibility aliases
_MAX_SEARCH_LENGTH = MAX_SEARCH_LENGTH
_MAX_QUERY_LIMIT = MAX_QUERY_LIMIT


class ColumnInfo(TypedDict):
    cid: int
    name: str
    type: str
    notnull: bool
    default_value: Any
    primary_key: bool
    non_null_count: int
    null_count: int
    distinct_count: Optional[int]
    sample_values: list[str]


class IndexInfo(TypedDict):
    name: str
    unique: bool
    columns: list[str]


class SchemaInfo(TypedDict):
    table_name: str
    all_tables: list[str]
    db_path: str
    db_filename: str
    db_size_bytes: int
    db_size_kb: float
    journal_mode: str
    page_size: int
    page_count: int
    total_records: int
    columns: list[ColumnInfo]
    structure: dict[str, ColumnInfo]
    indexes: list[IndexInfo]


class RequestLog(TypedDict):
    id: int
    timestamp: str
    action_type: str
    provider: str
    model: str
    endpoint: str
    status: str
    ttft_ms: float
    elapsed_ms: float
    is_mock: bool
    request_payload: Any
    response_payload: Any
    error_message: Optional[str]
    client_info: str


class FilterCountItem(TypedDict):
    name: str
    count: int


class FilterOptions(TypedDict):
    action_types: list[FilterCountItem]
    providers: list[FilterCountItem]
    models: list[FilterCountItem]
    statuses: list[FilterCountItem]
    modes: list[FilterCountItem]
    client_infos: list[FilterCountItem]
    endpoints: list[FilterCountItem]
    min_timestamp: Optional[str]
    max_timestamp: Optional[str]
    min_latency_ms: float
    max_latency_ms: float
    min_ttft_ms: float
    max_ttft_ms: float
    min_id: Optional[int]
    max_id: Optional[int]
    total_count: int


class DatabaseStats(TypedDict):
    db_path: str
    db_filename: str
    db_size_bytes: int
    db_size_kb: float
    total_requests: int
    success_count: int
    error_count: int
    mock_count: int
    live_count: int
    avg_ttft_ms: float
    avg_latency_ms: float
    action_breakdown: dict[str, int]
    provider_breakdown: dict[str, int]


__all__ = [
    "ColumnInfo",
    "DatabaseStats",
    "FilterCountItem",
    "FilterOptions",
    "IndexInfo",
    "RequestLog",
    "SchemaInfo",
    "clear_history",
    "count_history",
    "get_connection",
    "get_default_db_path",
    "get_filter_options",
    "get_history",
    "get_request",
    "get_schema_info",
    "get_stats",
    "init_db",
    "log_interaction",
]


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
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_request_logs_provider
            ON request_logs(provider);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_request_logs_mock
            ON request_logs(is_mock);
        """)


ALL_TABLE_COLUMNS: frozenset[str] = frozenset({
    "id", "timestamp", "action_type", "provider", "model", "endpoint",
    "status", "ttft_ms", "elapsed_ms", "is_mock", "request_payload",
    "response_payload", "error_message", "client_info"
})

ALLOWED_SORT_COLUMNS: dict[str, str] = {
    "id": "id",
    "timestamp": "timestamp",
    "elapsed_ms": "elapsed_ms",
    "latency": "elapsed_ms",
    "ttft_ms": "ttft_ms",
    "ttft": "ttft_ms",
    "action_type": "action_type",
    "action": "action_type",
    "provider": "provider",
    "model": "model",
    "endpoint": "endpoint",
    "status": "status",
    "is_mock": "is_mock",
    "mode": "is_mock",
    "client_info": "client_info",
    "client": "client_info",
    "error_message": "error_message",
    "error": "error_message",
}


def _build_filter_clause(
    action_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
    is_mock: Optional[bool | int] = None,
    client_info: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_latency: Optional[float] = None,
    max_latency: Optional[float] = None,
    min_ttft: Optional[float] = None,
    max_ttft: Optional[float] = None,
    id: Optional[int] = None,
    min_id: Optional[int] = None,
    max_id: Optional[int] = None,
    has_error: Optional[bool] = None,
    error_contains: Optional[str] = None,
    column_filters: Optional[list[dict[str, Any]]] = None,
) -> tuple[str, list[Any]]:
    """Build a parameterized SQL WHERE clause and parameter list from filter specifications."""
    clauses: list[str] = ["1=1"]
    params: list[Any] = []

    if id is not None:
        clauses.append("id = ?")
        params.append(int(id))

    if min_id is not None:
        clauses.append("id >= ?")
        params.append(int(min_id))

    if max_id is not None:
        clauses.append("id <= ?")
        params.append(int(max_id))

    if action_type:
        clauses.append("action_type = ?")
        params.append(action_type.strip())

    if status:
        clauses.append("status = ?")
        params.append(status.strip())

    if provider:
        clauses.append("provider = ?")
        params.append(provider.strip())

    if model:
        clauses.append("model = ?")
        params.append(model.strip())

    if endpoint:
        clean_ep = endpoint.strip()
        clauses.append("endpoint LIKE ?")
        params.append(f"%{clean_ep}%" if not ("%" in clean_ep or "_" in clean_ep) else clean_ep)

    if is_mock is not None:
        clauses.append("is_mock = ?")
        params.append(1 if bool(is_mock) else 0)

    if client_info:
        clauses.append("client_info = ?")
        params.append(client_info.strip())

    if start_date:
        clean_start = start_date.strip()
        clauses.append("timestamp >= ?")
        params.append(clean_start)

    if end_date:
        clean_end = end_date.strip()
        # If date only (YYYY-MM-DD), include through end of day
        if len(clean_end) == 10 and clean_end.count("-") == 2:
            clean_end = f"{clean_end}T23:59:59.999999Z"
        clauses.append("timestamp <= ?")
        params.append(clean_end)

    if min_latency is not None:
        clauses.append("elapsed_ms >= ?")
        params.append(float(min_latency))

    if max_latency is not None:
        clauses.append("elapsed_ms <= ?")
        params.append(float(max_latency))

    if min_ttft is not None:
        clauses.append("ttft_ms >= ?")
        params.append(float(min_ttft))

    if max_ttft is not None:
        clauses.append("ttft_ms <= ?")
        params.append(float(max_ttft))

    if has_error is not None:
        if bool(has_error):
            clauses.append("(status != 'success' OR error_message IS NOT NULL)")
        else:
            clauses.append("(status = 'success' AND (error_message IS NULL OR error_message = ''))")

    if error_contains:
        clauses.append("error_message LIKE ?")
        params.append(f"%{error_contains.strip()}%")

    # Dynamic arbitrary structural column filters
    if column_filters:
        for cf in column_filters:
            col_name = str(cf.get("column", "")).lower().strip()
            if col_name not in ALL_TABLE_COLUMNS:
                continue
            op = str(cf.get("operator", cf.get("op", "contains"))).lower().strip()
            val = cf.get("value", cf.get("val", ""))

            if op in ("eq", "=", "equals"):
                clauses.append(f"{col_name} = ?")
                params.append(val)
            elif op in ("neq", "!=", "not_equals"):
                clauses.append(f"{col_name} != ?")
                params.append(val)
            elif op in ("contains", "like"):
                clauses.append(f"{col_name} LIKE ?")
                params.append(f"%{val}%")
            elif op in ("starts_with", "startswith"):
                clauses.append(f"{col_name} LIKE ?")
                params.append(f"{val}%")
            elif op in ("ends_with", "endswith"):
                clauses.append(f"{col_name} LIKE ?")
                params.append(f"%{val}")
            elif op in ("gt", ">"):
                clauses.append(f"{col_name} > ?")
                params.append(val)
            elif op in ("gte", ">="):
                clauses.append(f"{col_name} >= ?")
                params.append(val)
            elif op in ("lt", "<"):
                clauses.append(f"{col_name} < ?")
                params.append(val)
            elif op in ("lte", "<="):
                clauses.append(f"{col_name} <= ?")
                params.append(val)
            elif op in ("is_null", "null", "empty"):
                clauses.append(f"({col_name} IS NULL OR {col_name} = '')")
            elif op in ("is_not_null", "not_null", "not_empty"):
                clauses.append(f"({col_name} IS NOT NULL AND {col_name} != '')")

    if search:
        clean_search = search.strip()
        if len(clean_search) > MAX_SEARCH_LENGTH:
            clean_search = clean_search[:MAX_SEARCH_LENGTH]
        wildcard = f"%{clean_search}%"
        clauses.append(
            "(request_payload LIKE ? OR response_payload LIKE ? OR error_message LIKE ? OR endpoint LIKE ? OR model LIKE ?)"
        )
        params.extend([wildcard, wildcard, wildcard, wildcard, wildcard])

    where_sql = " WHERE " + " AND ".join(clauses)
    return where_sql, params


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
    limit: Optional[int] = 50,
    offset: int = 0,
    action_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
    is_mock: Optional[bool | int] = None,
    client_info: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_latency: Optional[float] = None,
    max_latency: Optional[float] = None,
    min_ttft: Optional[float] = None,
    max_ttft: Optional[float] = None,
    id: Optional[int] = None,
    min_id: Optional[int] = None,
    max_id: Optional[int] = None,
    has_error: Optional[bool] = None,
    error_contains: Optional[str] = None,
    column_filters: Optional[list[dict[str, Any]]] = None,
    sort_by: str = "id",
    sort_order: str = "DESC",
    allow_unlimited: bool = False,
    db_path: Optional[str] = None,
    **kwargs: Any,
) -> list[RequestLog]:
    """
    Query logged requests and responses from the local database.
    Supports comprehensive multi-column filtering, full-text search, custom sorting, and pagination.
    """
    init_db(db_path)
    where_sql, params = _build_filter_clause(
        action_type=action_type,
        status=status,
        search=search,
        provider=provider,
        model=model,
        endpoint=endpoint,
        is_mock=is_mock,
        client_info=client_info,
        start_date=start_date,
        end_date=end_date,
        min_latency=min_latency,
        max_latency=max_latency,
        min_ttft=min_ttft,
        max_ttft=max_ttft,
        id=id,
        min_id=min_id,
        max_id=max_id,
        has_error=has_error,
        error_contains=error_contains,
        column_filters=column_filters,
    )

    col = ALLOWED_SORT_COLUMNS.get(sort_by.lower().strip(), "id")
    order = "ASC" if sort_order.upper().strip() == "ASC" else "DESC"

    query = f"SELECT * FROM request_logs {where_sql} ORDER BY {col} {order}"

    if allow_unlimited or limit is None or limit <= 0:
        query += " LIMIT 50000"
    else:
        capped_limit = min(max(1, limit), MAX_QUERY_LIMIT)
        query += " LIMIT ? OFFSET ?"
        params.extend([capped_limit, max(0, offset)])

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    results: list[RequestLog] = []
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
        results.append(cast(RequestLog, item))

    return results


def count_history(
    action_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
    is_mock: Optional[bool | int] = None,
    client_info: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_latency: Optional[float] = None,
    max_latency: Optional[float] = None,
    min_ttft: Optional[float] = None,
    max_ttft: Optional[float] = None,
    id: Optional[int] = None,
    min_id: Optional[int] = None,
    max_id: Optional[int] = None,
    has_error: Optional[bool] = None,
    error_contains: Optional[str] = None,
    column_filters: Optional[list[dict[str, Any]]] = None,
    db_path: Optional[str] = None,
    **kwargs: Any,
) -> int:
    """Count the total number of logged requests matching filter criteria across the entire database."""
    init_db(db_path)
    where_sql, params = _build_filter_clause(
        action_type=action_type,
        status=status,
        search=search,
        provider=provider,
        model=model,
        endpoint=endpoint,
        is_mock=is_mock,
        client_info=client_info,
        start_date=start_date,
        end_date=end_date,
        min_latency=min_latency,
        max_latency=max_latency,
        min_ttft=min_ttft,
        max_ttft=max_ttft,
        id=id,
        min_id=min_id,
        max_id=max_id,
        has_error=has_error,
        error_contains=error_contains,
        column_filters=column_filters,
    )
    query = f"SELECT COUNT(*) FROM request_logs {where_sql};"
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row[0] if row else 0


def get_filter_options(db_path: Optional[str] = None) -> FilterOptions:
    """Retrieve distinct column values and metadata to dynamically populate filtering controls."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Distinct action types
        cursor.execute("""
            SELECT action_type, COUNT(*) as count 
            FROM request_logs 
            WHERE action_type IS NOT NULL AND action_type != '' 
            GROUP BY action_type 
            ORDER BY count DESC;
        """)
        action_types: list[FilterCountItem] = [{"name": str(r[0]), "count": int(r[1])} for r in cursor.fetchall()]

        # Distinct providers
        cursor.execute("""
            SELECT provider, COUNT(*) as count 
            FROM request_logs 
            WHERE provider IS NOT NULL AND provider != '' 
            GROUP BY provider 
            ORDER BY count DESC;
        """)
        providers: list[FilterCountItem] = [{"name": str(r[0]), "count": int(r[1])} for r in cursor.fetchall()]

        # Distinct models
        cursor.execute("""
            SELECT model, COUNT(*) as count 
            FROM request_logs 
            WHERE model IS NOT NULL AND model != '' 
            GROUP BY model 
            ORDER BY count DESC;
        """)
        models: list[FilterCountItem] = [{"name": str(r[0]), "count": int(r[1])} for r in cursor.fetchall()]

        # Distinct statuses
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM request_logs 
            GROUP BY status 
            ORDER BY count DESC;
        """)
        statuses: list[FilterCountItem] = [{"name": str(r[0]), "count": int(r[1])} for r in cursor.fetchall()]

        # Modes breakdown
        cursor.execute("""
            SELECT is_mock, COUNT(*) as count 
            FROM request_logs 
            GROUP BY is_mock 
            ORDER BY is_mock ASC;
        """)
        modes: list[FilterCountItem] = [{"name": "mock" if r[0] else "live", "count": int(r[1])} for r in cursor.fetchall()]

        # Distinct client_info
        cursor.execute("""
            SELECT client_info, COUNT(*) as count 
            FROM request_logs 
            WHERE client_info IS NOT NULL AND client_info != '' 
            GROUP BY client_info 
            ORDER BY count DESC;
        """)
        client_infos: list[FilterCountItem] = [{"name": str(r[0]), "count": int(r[1])} for r in cursor.fetchall()]

        # Distinct endpoints
        cursor.execute("""
            SELECT endpoint, COUNT(*) as count 
            FROM request_logs 
            WHERE endpoint IS NOT NULL AND endpoint != '' 
            GROUP BY endpoint 
            ORDER BY count DESC;
        """)
        endpoints: list[FilterCountItem] = [{"name": str(r[0]), "count": int(r[1])} for r in cursor.fetchall()]

        # Min and max timestamp & latency
        cursor.execute("""
            SELECT 
                MIN(timestamp), MAX(timestamp),
                MIN(elapsed_ms), MAX(elapsed_ms),
                MIN(ttft_ms), MAX(ttft_ms),
                MIN(id), MAX(id),
                COUNT(*)
            FROM request_logs;
        """)
        ranges = cursor.fetchone()

    return cast(FilterOptions, {
        "action_types": action_types,
        "providers": providers,
        "models": models,
        "statuses": statuses,
        "modes": modes,
        "client_infos": client_infos,
        "endpoints": endpoints,
        "min_timestamp": ranges[0] if ranges else None,
        "max_timestamp": ranges[1] if ranges else None,
        "min_latency_ms": round(ranges[2], 1) if ranges and ranges[2] is not None else 0.0,
        "max_latency_ms": round(ranges[3], 1) if ranges and ranges[3] is not None else 0.0,
        "min_ttft_ms": round(ranges[4], 1) if ranges and ranges[4] is not None else 0.0,
        "max_ttft_ms": round(ranges[5], 1) if ranges and ranges[5] is not None else 0.0,
        "min_id": ranges[6] if ranges else None,
        "max_id": ranges[7] if ranges else None,
        "total_count": ranges[8] if ranges else 0,
    })


def get_schema_info(db_path: Optional[str] = None) -> SchemaInfo:
    """Inspect and return the complete SQLite table schema, columns, datatypes, and index structure."""
    init_db(db_path)
    path = db_path or get_default_db_path()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # All tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        all_tables = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*) FROM request_logs;")
        row_count_row = cursor.fetchone()
        row_count = row_count_row[0] if row_count_row else 0

        # Columns
        cursor.execute("PRAGMA table_info(request_logs);")
        raw_cols = cursor.fetchall()
        cols: list[ColumnInfo] = []
        structure_map: dict[str, ColumnInfo] = {}

        for r in raw_cols:
            col_name = r[1]
            col_type = r[2]
            not_null = bool(r[3])
            default_val = r[4]
            is_pk = bool(r[5])

            # Profiling for this column
            cursor.execute(f"SELECT COUNT(*) FROM request_logs WHERE {col_name} IS NOT NULL AND {col_name} != '';")
            nn_row = cursor.fetchone()
            non_null_count = nn_row[0] if nn_row else 0
            null_count = max(0, row_count - non_null_count)

            distinct_count = None
            sample_values: list[str] = []
            if col_name not in ("request_payload", "response_payload"):
                try:
                    cursor.execute(f"SELECT COUNT(DISTINCT {col_name}) FROM request_logs WHERE {col_name} IS NOT NULL AND {col_name} != '';")
                    d_row = cursor.fetchone()
                    distinct_count = d_row[0] if d_row else 0

                    cursor.execute(f"SELECT DISTINCT {col_name} FROM request_logs WHERE {col_name} IS NOT NULL AND {col_name} != '' LIMIT 4;")
                    sample_values = [str(sr[0])[:50] for sr in cursor.fetchall() if sr[0] is not None]
                except Exception:
                    pass

            col_entry: ColumnInfo = {
                "cid": r[0],
                "name": col_name,
                "type": col_type,
                "notnull": not_null,
                "default_value": default_val,
                "primary_key": is_pk,
                "non_null_count": non_null_count,
                "null_count": null_count,
                "distinct_count": distinct_count,
                "sample_values": sample_values,
            }
            cols.append(col_entry)
            structure_map[col_name] = col_entry

        # Indexes
        cursor.execute("PRAGMA index_list(request_logs);")
        indexes: list[IndexInfo] = []
        for r in cursor.fetchall():
            idx_name = r[1]
            cursor.execute(f"PRAGMA index_info({idx_name});")
            idx_cols = [ir[2] for ir in cursor.fetchall()]
            indexes.append({
                "name": idx_name,
                "unique": bool(r[2]),
                "columns": idx_cols,
            })

        cursor.execute("PRAGMA journal_mode;")
        journal_row = cursor.fetchone()
        journal_mode = journal_row[0] if journal_row else "unknown"

        cursor.execute("PRAGMA page_size;")
        page_size_row = cursor.fetchone()
        page_size = page_size_row[0] if page_size_row else 4096

        cursor.execute("PRAGMA page_count;")
        page_count_row = cursor.fetchone()
        page_count = page_count_row[0] if page_count_row else 0

    file_size_bytes = os.path.getsize(path) if os.path.exists(path) else 0

    return cast(SchemaInfo, {
        "table_name": "request_logs",
        "all_tables": all_tables,
        "db_path": path,
        "db_filename": os.path.basename(path),
        "db_size_bytes": file_size_bytes,
        "db_size_kb": round(file_size_bytes / 1024, 2),
        "journal_mode": journal_mode,
        "page_size": page_size,
        "page_count": page_count,
        "total_records": row_count,
        "columns": cols,
        "structure": structure_map,
        "indexes": indexes,
    })


def get_request(request_id: int, db_path: Optional[str] = None) -> Optional[RequestLog]:
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
        return cast(RequestLog, item)


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


def get_stats(db_path: Optional[str] = None) -> DatabaseStats:
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

    return cast(DatabaseStats, {
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
    })


__all__ = [
    "ColumnInfo",
    "IndexInfo",
    "SchemaInfo",
    "RequestLog",
    "FilterCountItem",
    "FilterOptions",
    "DatabaseStats",
    "get_default_db_path",
    "get_connection",
    "init_db",
    "log_interaction",
    "get_history",
    "count_history",
    "get_filter_options",
    "get_schema_info",
    "get_request",
    "clear_history",
    "get_stats",
    "ALL_TABLE_COLUMNS",
    "ALLOWED_SORT_COLUMNS",
    "MAX_SEARCH_LENGTH",
    "MAX_QUERY_LIMIT",
]
