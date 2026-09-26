#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_server.py - Tests for server.py and frontend default payloads in index.html.
"""

from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
import unittest
from typing import Any, cast

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

import server


class TestIndexHtmlPayloads(unittest.TestCase):
    """Test that default payloads embedded in index.html are valid JSON."""

    def setUp(self):
        index_path = os.path.join(PARENT_DIR, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_custom_state_default_is_valid_json(self):
        pattern = r'<textarea[^>]+id=["\']custom-state["\'][^>]*>(.*?)</textarea>'
        match = re.search(pattern, self.html, re.DOTALL)
        self.assertIsNotNone(match, "custom-state textarea must be present in index.html")
        assert match is not None
        val = match.group(1).strip()
        parsed = json.loads(val)
        self.assertIsInstance(parsed, dict)
        self.assertIn("ticket_id", parsed)

    def test_custom_questions_default_is_valid_json(self):
        pattern = r'<textarea[^>]+id=["\']custom-questions["\'][^>]*>(.*?)</textarea>'
        match = re.search(pattern, self.html, re.DOTALL)
        self.assertIsNotNone(match, "custom-questions textarea must be present in index.html")
        assert match is not None
        val = match.group(1).strip()
        parsed = json.loads(val)
        self.assertIsInstance(parsed, dict)
        self.assertIn("requests_refund", parsed)
        self.assertIn("charge_type", parsed)
        self.assertIn("frustration_level", parsed)

    def test_stats_banner_has_actual_tested_latency_and_no_100ms_placeholder(self):
        self.assertNotIn('<div class="stat-val">~100 ms</div>', self.html)
        pattern = r'<div class="stat-val"[^>]*>\s*287 ms\s*</div>'
        self.assertRegex(self.html, pattern, "Stats banner must display tested 287 ms inference latency")


class TestServerEndpoints(unittest.TestCase):
    """Test HTTP API endpoints in server.py using a test server instance."""

    server_thread = None
    httpd = None
    port = 8899

    @classmethod
    def setUpClass(cls):
        server.init_server_state(force_mock=True)

        handler = server.JevDashboardRequestHandler
        cls.httpd = server.socketserver.TCPServer(("127.0.0.1", cls.port), handler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        if cls.httpd:
            cls.httpd.shutdown()
            cls.httpd.server_close()

    def _post(self, path: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.getcode()
                body = json.loads(resp.read().decode("utf-8"))
                return status, body
        except urllib.error.HTTPError as err:
            body = json.loads(err.read().decode("utf-8"))
            return err.code, body

    def _delete(self, path: str) -> tuple[int, dict[str, Any]]:
        url = f"http://127.0.0.1:{self.port}{path}"
        req = urllib.request.Request(url, method="DELETE")
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.getcode()
                body = json.loads(resp.read().decode("utf-8"))
                return status, body
        except urllib.error.HTTPError as err:
            body = json.loads(err.read().decode("utf-8"))
            return err.code, body

    def _get(self, path: str) -> tuple[int, Any]:
        url = f"http://127.0.0.1:{self.port}{path}"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.getcode()
                content_type = resp.headers.get("Content-Type", "")
                raw = resp.read()
                if "application/json" in content_type:
                    return status, json.loads(raw.decode("utf-8"))
                if "text/" in content_type or "svg" in content_type or "xml" in content_type:
                    return status, raw.decode("utf-8")
                return status, raw
        except urllib.error.HTTPError as err:
            raw = err.read()
            try:
                body = json.loads(raw.decode("utf-8"))
                return err.code, body
            except Exception:
                return err.code, raw

    def test_status_endpoint(self):
        status, body = self._get("/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(body.get("status"), "online")
        self.assertTrue(body.get("mock"))

    def test_get_root_serves_index_html(self):
        status, html = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("JevTools", html)
        self.assertIn("https://github.com/RileyCarney/JevTools", html)
        self.assertIn("https://repository-images.githubusercontent.com/1379027574/d9770636-5e32-4332-a030-72d119b8227f", html)
        self.assertIn("DYNAMIC PCB CIRCUIT BOARD MATRIX ENGINE", html)

    def test_serves_assets_cleanly(self):
        # Card PNG
        status, data = self._get("/assets/jevtools_card.png")
        self.assertEqual(status, 200)
        self.assertIsInstance(data, bytes)
        self.assertGreater(len(data), 1000)

        # SVG Favicon
        status, svg_text = self._get("/assets/favicon.svg")
        self.assertEqual(status, 200)
        self.assertIn("<svg", svg_text)
        self.assertIn("M12 0C5.37 0", svg_text) # Octocat path

        # App Icon
        status, icon_data = self._get("/assets/icon.png")
        self.assertEqual(status, 200)
        self.assertIsInstance(icon_data, bytes)

        # Standalone SVG Logo
        status, logo_text = self._get("/assets/jevtools_logo.svg")
        self.assertEqual(status, 200)
        self.assertIn("JEVTOOLS", logo_text)

        # Root Favicon route
        status, fav_data = self._get("/favicon.ico")
        self.assertEqual(status, 200)
        self.assertIsInstance(fav_data, bytes)

    def test_analyze_review_endpoint(self):
        status, body = self._post("/api/analyze-review", {
            "review": "Fantastic battery life and great build quality.",
            "product": "Test Earbuds"
        })
        self.assertEqual(status, 200)
        self.assertIn("overall_sentiment", body)
        self.assertIn("composite_score", body)

    def test_classify_topic_endpoint(self):
        status, body = self._post("/api/classify-topic", {
            "paragraph": "Researchers have discovered new water ice formations beneath Martian polar caps."
        })
        self.assertEqual(status, 200)
        self.assertEqual(body.get("primary_topic"), "science")

    def test_custom_decision_endpoint(self):
        state = {
            "ticket_id": "T-9042",
            "message": "I was charged $49.99 twice on my visa card. Please refund the duplicate immediately.",
            "plan": "Pro Annual"
        }
        questions = {
            "requests_refund": {
                "type": "noul",
                "instructions": "Does message request a refund?"
            }
        }
        status, body = self._post("/api/custom-decision", {
            "state": state,
            "questions": questions
        })
        self.assertEqual(status, 200)
        self.assertIn("answers", body)
        self.assertIn("requests_refund", body["answers"])

    def test_custom_decision_invalid_questions(self):
        status, body = self._post("/api/custom-decision", {
            "state": "some state",
            "questions": "not a dictionary"
        })
        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_status_endpoint_returns_ttft_and_latency(self):
        status, body = self._get("/api/status")
        self.assertEqual(status, 200)
        self.assertIn("tested_inference_latency_ms", body)
        self.assertIn("tested_ttft_ms", body)
        self.assertIn("tested_inference_latency_str", body)
        self.assertTrue(body["tested_inference_latency_str"].endswith(" ms"))
        self.assertGreater(body["tested_inference_latency_ms"], 0)
        self.assertGreater(body["tested_ttft_ms"], 0)

    def test_benchmark_ttft_endpoint(self):
        status, body = self._get("/api/benchmark-ttft")
        self.assertEqual(status, 200)
        self.assertIn("avg_ttft_ms", body)
        self.assertIn("avg_latency_ms", body)
        self.assertGreater(body["avg_ttft_ms"], 0)

    def test_analyze_review_endpoint_returns_ttft(self):
        status, body = self._post("/api/analyze-review", {
            "review": "Fantastic battery life and great build quality.",
            "product": "Test Earbuds"
        })
        self.assertEqual(status, 200)
        self.assertIn("ttft_ms", body)
        self.assertIn("elapsed_ms", body)
        self.assertGreater(body["ttft_ms"], 0)

    def test_classify_topic_endpoint_returns_ttft(self):
        status, body = self._post("/api/classify-topic", {
            "paragraph": "Researchers have discovered new water ice formations beneath Martian polar caps."
        })
        self.assertEqual(status, 200)
        self.assertIn("ttft_ms", body)
        self.assertIn("elapsed_ms", body)
        self.assertGreater(body["ttft_ms"], 0)

    def test_custom_decision_endpoint_returns_ttft(self):
        status, body = self._post("/api/custom-decision", {
            "state": {"ticket": "123"},
            "questions": {"is_urgent": {"type": "noul", "instructions": "Is it urgent?"}}
        })
        self.assertEqual(status, 200)
        self.assertIn("metadata", body)
        self.assertIn("ttft_ms", body["metadata"])
        self.assertIn("elapsed_ms", body["metadata"])
        self.assertGreater(body["metadata"]["ttft_ms"], 0)

    def test_history_endpoints_and_stats(self):
        # Clear first
        self._delete("/api/history")

        # GET /api/history when empty
        status, body = self._get("/api/history")
        self.assertEqual(status, 200)
        self.assertIn("items", body)
        self.assertIn("stats", body)
        self.assertEqual(body["count"], 0)

        # GET /api/history/stats
        status_s, body_s = self._get("/api/history/stats")
        self.assertEqual(status_s, 200)
        self.assertIn("total_requests", body_s)
        self.assertIn("db_path", body_s)
        self.assertIn("db_size_kb", body_s)

    def test_api_requests_are_logged_to_database(self):
        # Clear history
        self._delete("/api/history")

        # Perform review analysis
        status, _ = self._post("/api/analyze-review", {
            "review": "Fast delivery and exceptional audio clarity.",
            "product": "Audiophile Pro"
        })
        self.assertEqual(status, 200)

        # Verify history reflects the request
        status_h, body_h = self._get("/api/history")
        self.assertEqual(status_h, 200)
        self.assertGreaterEqual(body_h["count"], 1)

        item = body_h["items"][0]
        self.assertEqual(item["action_type"], "review_analysis")
        self.assertEqual(item["status"], "success")
        self.assertEqual(item["client_info"], "web_ui")
        self.assertIn("Audiophile Pro", json.dumps(item["request_payload"]))

        # Query single item by id
        status_single, single = self._get(f"/api/history?id={item['id']}")
        self.assertEqual(status_single, 200)
        self.assertEqual(single["id"], item["id"])

    def test_history_clear_and_delete(self):
        # Seed an item
        self._post("/api/classify-topic", {
            "paragraph": "Advances in neural network architectures."
        })

        # Test POST /api/history/clear
        status_c, body_c = self._post("/api/history/clear", {})
        self.assertEqual(status_c, 200)
        self.assertIn("cleared", body_c)

        # Verify count is 0
        _, body_empty = self._get("/api/history")
        self.assertEqual(body_empty["count"], 0)

        # Seed again and test DELETE /api/history
        self._post("/api/classify-topic", {
            "paragraph": "Stock market fluctuations."
        })
        status_d, body_d = self._delete("/api/history")
        self.assertEqual(status_d, 200)
        self.assertIn("cleared", body_d)
        self.assertGreater(body_d["cleared"], 0)

    def test_sensitive_files_blocked(self):
        """Verify that server blocks access to sensitive files like .env, .git, .db, and python sources."""
        for path in (
            "/jevtools.db",
            "/.env",
            "/.git/config",
            "/server.py",
            "/database.py",
            "/pyproject.toml",
            "/pyright_output.json",
            "/server.py%00.jpg",
        ):
            status, body = self._get(path)
            self.assertEqual(status, 403, f"Path {path} must be rejected with 403 Forbidden")
            self.assertIsInstance(body, dict)
            self.assertIn("error", body)

    def test_security_hardening_headers(self):
        """Verify that security hardening response headers are sent on responses (VUL-007)."""
        url = f"http://127.0.0.1:{self.port}/api/status"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            headers = resp.headers
            self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(headers.get("X-Frame-Options"), "DENY")
            self.assertEqual(headers.get("Referrer-Policy"), "no-referrer")
            csp = headers.get("Content-Security-Policy", "")
            self.assertIn("default-src 'self'", csp)
            self.assertIn("frame-ancestors 'none'", csp)
            self.assertEqual(headers.get("Vary"), "Origin")

    def test_cors_origin_allowlist(self):
        """Verify CORS headers only reflect permitted origins, falling back to localhost (VUL-003)."""
        url = f"http://127.0.0.1:{self.port}/api/status"

        # Allowed Origin: localhost with port
        req_local = urllib.request.Request(url, headers={"Origin": f"http://localhost:{self.port}"})
        with urllib.request.urlopen(req_local) as resp:
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), f"http://localhost:{self.port}")

        # Allowed Origin: 127.0.0.1
        req_ip = urllib.request.Request(url, headers={"Origin": f"http://127.0.0.1:{server.DEFAULT_PORT}"})
        with urllib.request.urlopen(req_ip) as resp:
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), f"http://127.0.0.1:{server.DEFAULT_PORT}")

        # Disallowed Origin: untrusted external origin falls back to default localhost
        req_bad = urllib.request.Request(url, headers={"Origin": "https://malicious-external-site.com"})
        with urllib.request.urlopen(req_bad) as resp:
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), f"http://localhost:{server.DEFAULT_PORT}")

    def test_request_body_size_limit(self):
        """Verify that oversized request bodies are rejected with 400 (VUL-004)."""
        url = f"http://127.0.0.1:{self.port}/api/config"
        oversized_payload = json.dumps({"overflow": "A" * (server.MAX_REQUEST_BODY_BYTES + 50)}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=oversized_payload,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(oversized_payload)),
            },
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertIn("Request body too large", body.get("error", ""))

    def test_benchmark_runs_parameter_cap(self):
        """Verify that benchmark runs parameter is capped at MAX_BENCHMARK_RUNS (VUL-005)."""
        from unittest.mock import patch
        with patch.object(server.jev_demo, "measure_openrouter_ttft") as mock_measure:
            mock_measure.return_value = {"avg_ttft_ms": 120.0, "avg_latency_ms": 250.0, "runs": 10}
            status, _ = self._post("/api/benchmark-ttft", {"runs": 99999})
            self.assertEqual(status, 200)
            mock_measure.assert_called_once()
            _, kwargs = mock_measure.call_args
            self.assertEqual(kwargs.get("runs"), server.MAX_BENCHMARK_RUNS)

    def test_history_search_length_cap(self):
        """Verify that search query parameter is capped at 200 chars (VUL-010)."""
        long_search = "Q" * 350
        status, body = self._get(f"/api/history?search={long_search}")
        self.assertEqual(status, 200)
        self.assertIn("items", body)

    def test_server_architecture_subclass_and_reuse_address(self):
        """Verify TCPServer subclassing and allow_reuse_address (VUL-001 & GAP-003)."""
        self.assertTrue(issubclass(cast(type[Any], server.LocalhostTCPServer), server.socketserver.TCPServer))
        self.assertTrue(server.LocalhostTCPServer.allow_reuse_address)

    def test_path_traversal_safety_checker(self):
        """Verify is_safe_path blocks traversal and blocked extensions (VUL-008)."""
        handler = server.JevDashboardRequestHandler
        self.assertTrue(handler.is_safe_path("/"))
        self.assertTrue(handler.is_safe_path("/index.html"))
        self.assertTrue(handler.is_safe_path("/assets/icon.png"))
        self.assertFalse(handler.is_safe_path("/server.py"))
        self.assertFalse(handler.is_safe_path("/database.py"))
        self.assertFalse(handler.is_safe_path("/jevtools.db"))
        self.assertFalse(handler.is_safe_path("/.env"))
        self.assertFalse(handler.is_safe_path("/.git/config"))
        self.assertFalse(handler.is_safe_path("/pyproject.toml"))
        self.assertFalse(handler.is_safe_path("/pyright_output.json"))
        self.assertFalse(handler.is_safe_path("/server.py%00.jpg"))
        self.assertFalse(handler.is_safe_path("/server.py\x00.jpg"))
        self.assertFalse(handler.is_safe_path("/server.py."))
        self.assertFalse(handler.is_safe_path("/server.py "))
        self.assertFalse(handler.is_safe_path("/assets/../server.py"))
        self.assertFalse(handler.is_safe_path("/../../etc/passwd"))

    def test_log_message_suppression(self):
        """Verify default access logging is suppressed (GAP-001)."""
        import io
        import sys
        dummy = object.__new__(server.JevDashboardRequestHandler)
        captured = io.StringIO()
        old_stderr = sys.stderr
        try:
            sys.stderr = captured
            dummy.log_message("test format %s", "arg")
            self.assertEqual(captured.getvalue(), "")
        finally:
            sys.stderr = old_stderr


if __name__ == "__main__":
    unittest.main(verbosity=2)
