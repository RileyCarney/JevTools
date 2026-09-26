#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py - Localhost Web Dashboard Server for JevTools System One Cockpit.

Serves the interactive cyber/dark UI on http://localhost:8089 (or next available port),
provides REST API endpoints connecting directly to jev_demo.py, and opens the browser.
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import pathlib
import socket
import socketserver
import sys
import urllib.parse
import webbrowser
from http import HTTPStatus
from typing import Any, Optional, TypedDict, cast

# Ensure this directory is in sys.path so jev_demo can be imported cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import database
import jev_demo

DEFAULT_PORT = 8089
MAX_REQUEST_BODY_BYTES = 1 * 1024 * 1024  # 1 MB
MAX_BENCHMARK_RUNS = 10

_ALLOWED_CORS_ORIGINS = {
    f"http://localhost:{DEFAULT_PORT}",
    f"http://127.0.0.1:{DEFAULT_PORT}",
    "null",  # file:// origin
}

_BLOCKED_EXTENSIONS: frozenset[str] = frozenset({
    ".db", ".db-journal", ".db-shm", ".db-wal",
    ".sqlite", ".sqlite3",
    ".env", ".pem", ".key", ".crt",
    ".py", ".pyi", ".pyc",
    ".toml", ".cfg", ".ini",
    ".bat", ".sh", ".ps1",
    ".json", ".yaml", ".yml",
})
_ALLOWED_DIR: pathlib.Path = pathlib.Path(CURRENT_DIR).resolve()


class RuntimeState(TypedDict):
    api_key: str
    mock: bool
    provider: str
    model: str
    endpoint: str
    tested_latency_ms: float
    tested_ttft_ms: float


# Server runtime state
RUNTIME_STATE: RuntimeState = {
    "api_key": "",
    "mock": True,
    "provider": "openrouter",
    "model": jev_demo.OPENROUTER_DEFAULT_MODEL,
    "endpoint": jev_demo.OPENROUTER_API_URL,
    "tested_latency_ms": float(jev_demo.OPENROUTER_TESTED_LATENCY_MS),
    "tested_ttft_ms": float(jev_demo.OPENROUTER_TESTED_TTFT_MS),
}


def init_server_state(cli_key: str | None = None, force_mock: bool = False) -> None:
    """Initialize active API key, mock status, and provider."""
    # Try resolving key from environment or CLI
    resolved_key = ""
    for env_var in ("OPENROUTER_API_KEY", "TYPESAFE_API_KEY", "OPENROUTER_KEY", "JEV_API_KEY"):
        val = os.environ.get(env_var, "").strip()
        if val:
            resolved_key = val
            break

    if cli_key:
        resolved_key = cli_key

    if force_mock or not resolved_key:
        RUNTIME_STATE["mock"] = True
        RUNTIME_STATE["api_key"] = resolved_key or "mock-key-for-testing"
    else:
        RUNTIME_STATE["mock"] = False
        RUNTIME_STATE["api_key"] = resolved_key

    prov, ep, mdl = jev_demo.get_provider_config(RUNTIME_STATE["api_key"])
    RUNTIME_STATE["provider"] = prov
    RUNTIME_STATE["endpoint"] = ep
    RUNTIME_STATE["model"] = mdl


_init_server_state = init_server_state


class JevDashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler supporting both static dashboard assets and Jev REST APIs."""

    def __init__(
        self,
        request: socket.socket | tuple[bytes, socket.socket],
        client_address: tuple[str, int] | str,
        server: socketserver.BaseServer,
        directory: str | None = None,
    ) -> None:
        super().__init__(request, client_address, server, directory=CURRENT_DIR)

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default HTTP access logging to prevent query string exposure in terminal."""
        pass

    @staticmethod
    def is_safe_path(raw_path: str) -> bool:
        """Return True only if the path resolves inside CURRENT_DIR and is not a blocked type."""
        if "\x00" in raw_path:
            return False
        decoded = urllib.parse.unquote(raw_path)
        if "\x00" in decoded or "\x00" in urllib.parse.unquote(decoded):
            return False

        lower = decoded.lower().replace("\\", "/")
        if lower.startswith("/.") or "/." in lower:
            return False
        suffix = pathlib.PurePosixPath(lower).suffix
        if suffix in _BLOCKED_EXTENSIONS:
            return False
        try:
            clean = decoded.replace("\\", "/").lstrip("/")
            resolved = (_ALLOWED_DIR / clean).resolve()
            resolved.relative_to(_ALLOWED_DIR)
            if resolved.suffix.lower() in _BLOCKED_EXTENSIONS or any(s.lower() in _BLOCKED_EXTENSIONS for s in resolved.suffixes):
                return False
        except (ValueError, OSError):
            return False
        return True

    _is_safe_path = is_safe_path

    def end_headers(self) -> None:
        origin = self.headers.get("Origin", "")
        # Check if origin is allowed (null, or http://localhost:<port>, http://127.0.0.1:<port>)
        is_allowed = False
        if origin in _ALLOWED_CORS_ORIGINS:
            is_allowed = True
        elif origin:
            try:
                parsed_origin = urllib.parse.urlsplit(origin)
                if parsed_origin.scheme in ("http", "https") and parsed_origin.hostname in ("localhost", "127.0.0.1"):
                    is_allowed = True
            except Exception:
                pass

        cors_origin = origin if is_allowed else f"http://localhost:{DEFAULT_PORT}"
        self.send_header("Access-Control-Allow-Origin", cors_origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https://repository-images.githubusercontent.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.OK)
        self.end_headers()

    def _send_json_response(self, data: dict[str, Any], status: int = 200) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        if getattr(self, "close_connection", False):
            self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)
        self.wfile.flush()

    def _send_json_error(self, message: str, status: int = 400) -> None:
        self._send_json_response({"error": message, "status": status}, status=status)

    def _parse_json_body(self) -> dict[str, Any]:
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            return {}
        if content_length <= 0:
            return {}
        if content_length > MAX_REQUEST_BODY_BYTES:
            self.close_connection = True
            try:
                drain = min(content_length, 2 * 1024 * 1024)
                while drain > 0:
                    chunk = self.rfile.read(min(drain, 65536))
                    if not chunk:
                        break
                    drain -= len(chunk)
            except Exception:
                pass
            raise ValueError(
                f"Request body too large: {content_length} bytes "
                f"(maximum: {MAX_REQUEST_BODY_BYTES} bytes)"
            )
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            parsed: Any = json.loads(body)
            if not isinstance(parsed, dict):
                raise ValueError("JSON payload must be an object")
            return cast(dict[str, Any], parsed)
        except json.JSONDecodeError as err:
            raise ValueError(f"Invalid JSON payload: {err}") from err

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/status":
            prov, ep, mdl = jev_demo.get_provider_config(
                RUNTIME_STATE["api_key"],
                provider=RUNTIME_STATE["provider"],
                model=RUNTIME_STATE["model"],
                endpoint=RUNTIME_STATE["endpoint"],
            )
            data: dict[str, Any] = {
                "status": "online",
                "mock": RUNTIME_STATE["mock"],
                "provider": prov,
                "model": mdl,
                "endpoint": ep if not RUNTIME_STATE["mock"] else "[OFFLINE MOCK]",
                "api_key_masked": jev_demo.mask_key(RUNTIME_STATE["api_key"]),
                "has_real_key": bool(RUNTIME_STATE["api_key"] and not RUNTIME_STATE["api_key"].startswith("mock-")),
                "tested_inference_latency_ms": RUNTIME_STATE["tested_latency_ms"],
                "tested_ttft_ms": RUNTIME_STATE["tested_ttft_ms"],
                "tested_inference_latency_str": f"{round(RUNTIME_STATE['tested_latency_ms'])} ms",
                "tested_ttft_str": f"{round(RUNTIME_STATE['tested_ttft_ms'])} ms",
                "benchmarks": {
                    "reviews_count": len(jev_demo.REVIEW_CASES),
                    "topics_count": len(jev_demo.TOPIC_CASES),
                },
            }
            self._send_json_response(data)
            return

        if path == "/api/benchmark-ttft":
            runs = 3
            stats = jev_demo.measure_openrouter_ttft(runs=runs, api_key=RUNTIME_STATE["api_key"], client_info="web_ui")
            if stats.get("avg_latency_ms"):
                RUNTIME_STATE["tested_latency_ms"] = float(stats["avg_latency_ms"])
            if stats.get("avg_ttft_ms"):
                RUNTIME_STATE["tested_ttft_ms"] = float(stats["avg_ttft_ms"])
            self._send_json_response(stats)
            return

        if path == "/api/history":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            req_id_list = query_params.get("id")
            if req_id_list:
                try:
                    entry = database.get_request(int(req_id_list[0]))
                    if entry:
                        self._send_json_response(entry)
                    else:
                        self._send_json_error("Log entry not found", status=404)
                except ValueError:
                    self._send_json_error("Invalid ID format", status=400)
                return

            limit_list = query_params.get("limit")
            limit = int(limit_list[0]) if limit_list and limit_list[0].isdigit() else 50

            offset_list = query_params.get("offset")
            offset = int(offset_list[0]) if offset_list and offset_list[0].isdigit() else 0

            action_type_list = query_params.get("action_type")
            action_type = action_type_list[0] if action_type_list else None

            status_list = query_params.get("status")
            status_filter = status_list[0] if status_list else None

            search_list = query_params.get("search")
            raw_search = search_list[0] if search_list else None
            search = raw_search[:200] if raw_search else None

            items = database.get_history(
                limit=limit,
                offset=offset,
                action_type=action_type,
                status=status_filter,
                search=search,
            )
            stats = database.get_stats()
            self._send_json_response({
                "items": items,
                "count": len(items),
                "limit": limit,
                "offset": offset,
                "stats": stats,
            })
            return

        if path == "/api/history/stats":
            self._send_json_response(database.get_stats())
            return

        # Block access to hidden files, databases, credentials, config, and source files
        if not self.is_safe_path(path):
            self._send_json_error("Forbidden: access to protected file or directory is restricted", status=403)
            return

        # Serve index.html for root path, and assets/favicon.ico for favicon requests
        if path in ("", "/"):
            self.path = "/index.html"
        elif path == "/favicon.ico":
            self.path = "/assets/favicon.ico"

        super().do_GET()

    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        try:
            body = self._parse_json_body()
        except ValueError as err:
            self._send_json_error(str(err), status=400)
            return

        if path == "/api/config":
            # Update session key, mock mode, or provider
            if "api_key" in body:
                key = str(body["api_key"]).strip()
                if key:
                    RUNTIME_STATE["api_key"] = key
            if "mock" in body:
                RUNTIME_STATE["mock"] = bool(body["mock"])
            if "provider" in body:
                RUNTIME_STATE["provider"] = str(body["provider"]).strip()
            if "model" in body:
                RUNTIME_STATE["model"] = str(body["model"]).strip()

            prov, ep, mdl = jev_demo.get_provider_config(
                RUNTIME_STATE["api_key"],
                provider=RUNTIME_STATE["provider"],
                model=RUNTIME_STATE["model"],
            )
            RUNTIME_STATE["provider"] = prov
            RUNTIME_STATE["endpoint"] = ep
            RUNTIME_STATE["model"] = mdl

            self._send_json_response({
                "message": "Configuration updated successfully",
                "mock": RUNTIME_STATE["mock"],
                "provider": prov,
                "model": mdl,
                "api_key_masked": jev_demo.mask_key(RUNTIME_STATE["api_key"]),
                "has_real_key": bool(RUNTIME_STATE["api_key"] and not RUNTIME_STATE["api_key"].startswith("mock-")),
            })
            return

        if path == "/api/history/clear":
            count = database.clear_history()
            self._send_json_response({
                "message": f"Successfully cleared {count} interaction logs",
                "cleared": count,
            })
            return

        if path == "/api/analyze-review":
            review_text = str(body.get("review", "")).strip()
            product_val = body.get("product")
            product_name = str(product_val).strip() if product_val is not None and str(product_val).strip() else "Wireless Earbuds Pro"
            override_mock = body.get("mock")
            use_mock: bool = RUNTIME_STATE["mock"] if override_mock is None else bool(override_mock)

            if not review_text:
                self._send_json_error("Missing required field 'review'", status=400)
                return

            try:
                result = jev_demo.analyze_review(
                    api_key=RUNTIME_STATE["api_key"],
                    review_text=review_text,
                    product_name=product_name,
                    mock=use_mock,
                    provider=RUNTIME_STATE["provider"],
                    model=RUNTIME_STATE["model"],
                    endpoint=RUNTIME_STATE["endpoint"],
                    client_info="web_ui",
                )
                self._send_json_response(result.to_dict())
            except Exception as exc:
                self._send_json_error(f"Review analysis failed: {exc}", status=500)
            return

        if path == "/api/classify-topic":
            paragraph = str(body.get("paragraph", "")).strip()
            override_mock = body.get("mock")
            use_mock: bool = RUNTIME_STATE["mock"] if override_mock is None else bool(override_mock)

            if not paragraph:
                self._send_json_error("Missing required field 'paragraph'", status=400)
                return

            try:
                result = jev_demo.classify_topic(
                    api_key=RUNTIME_STATE["api_key"],
                    paragraph=paragraph,
                    mock=use_mock,
                    provider=RUNTIME_STATE["provider"],
                    model=RUNTIME_STATE["model"],
                    endpoint=RUNTIME_STATE["endpoint"],
                    client_info="web_ui",
                )
                self._send_json_response(result.to_dict())
            except Exception as exc:
                self._send_json_error(f"Topic classification failed: {exc}", status=500)
            return

        if path == "/api/custom-decision":
            state = body.get("state")
            questions = body.get("questions")
            override_mock = body.get("mock")
            use_mock: bool = RUNTIME_STATE["mock"] if override_mock is None else bool(override_mock)

            if state is None:
                self._send_json_error("Missing required field 'state'", status=400)
                return
            if not isinstance(questions, dict) or not questions:
                self._send_json_error("Field 'questions' must be a non-empty dictionary", status=400)
                return

            typed_questions = cast(dict[str, Any], questions)

            try:
                res = jev_demo.evaluate_custom_decision(
                    api_key=RUNTIME_STATE["api_key"],
                    state=state,
                    questions=typed_questions,
                    mock=use_mock,
                    provider=RUNTIME_STATE["provider"],
                    model=RUNTIME_STATE["model"],
                    endpoint=RUNTIME_STATE["endpoint"],
                    client_info="web_ui",
                )
                self._send_json_response(res)
            except Exception as exc:
                self._send_json_error(f"Custom evaluation failed: {exc}", status=500)
            return

        if path == "/api/benchmark-ttft":
            raw_runs = body.get("runs")
            try:
                runs = max(1, min(MAX_BENCHMARK_RUNS, int(raw_runs))) if raw_runs is not None else 3
            except (ValueError, TypeError):
                runs = 3
            stats = jev_demo.measure_openrouter_ttft(runs=runs, api_key=RUNTIME_STATE["api_key"], client_info="web_ui")
            if stats.get("avg_latency_ms"):
                RUNTIME_STATE["tested_latency_ms"] = float(stats["avg_latency_ms"])
            if stats.get("avg_ttft_ms"):
                RUNTIME_STATE["tested_ttft_ms"] = float(stats["avg_ttft_ms"])
            self._send_json_response(stats)
            return

        self._send_json_error(f"Endpoint not found: {path}", status=404)

    def do_DELETE(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/history":
            count = database.clear_history()
            self._send_json_response({
                "message": f"Successfully cleared {count} interaction logs",
                "cleared": count,
            })
            return

        self._send_json_error(f"Endpoint not found: {path}", status=404)


is_safe_path = JevDashboardRequestHandler.is_safe_path


class LocalhostTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


_LocalhostTCPServer = LocalhostTCPServer


def main() -> None:
    parser = argparse.ArgumentParser(description="JevTools System One Localhost Web Dashboard Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to serve dashboard on (default: {DEFAULT_PORT})")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser")
    parser.add_argument("--mock", action="store_true", help="Force offline mock mode without making live API requests")
    parser.add_argument("--api-key", default=None, help="OpenRouter or TypeSafe API key")
    args = parser.parse_args()

    cli_key = cast(Optional[str], getattr(args, "api_key", None))
    force_mock = bool(getattr(args, "mock", False))
    init_server_state(cli_key=cli_key, force_mock=force_mock)

    os.chdir(CURRENT_DIR)

    port = int(getattr(args, "port", DEFAULT_PORT))
    handler = JevDashboardRequestHandler

    while port < int(getattr(args, "port", DEFAULT_PORT)) + 25:
        try:
            with LocalhostTCPServer(("127.0.0.1", port), handler) as httpd:
                url = f"http://localhost:{port}/index.html"
                print("=" * 64)
                print(" [>] JevTools System One Cockpit Active")
                print("=" * 64)
                print(f" URL             : {url}")
                print(f" Root Directory  : {CURRENT_DIR}")
                print(f" Active Provider : {RUNTIME_STATE['provider'].title()}")
                print(f" Active Model    : {RUNTIME_STATE['model']}")
                print(f" Mock Mode       : {'ENABLED (Zero Credits/Offline)' if RUNTIME_STATE['mock'] else 'LIVE API'}")
                print(f" Key Loaded      : {jev_demo.mask_key(RUNTIME_STATE['api_key'])}")
                print(" Press Ctrl+C to stop the dashboard server.")
                print("=" * 64)

                if not bool(getattr(args, "no_browser", False)):
                    webbrowser.open(url)

                httpd.serve_forever()
                break
        except OSError:
            print(f"[*] Port {port} is in use, trying port {port + 1}...")
            port += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] JevTools dashboard server stopped.")
        sys.exit(0)
