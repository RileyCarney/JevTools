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
        val = match.group(1).strip()
        parsed = json.loads(val)
        self.assertIsInstance(parsed, dict)
        self.assertIn("ticket_id", parsed)

    def test_custom_questions_default_is_valid_json(self):
        pattern = r'<textarea[^>]+id=["\']custom-questions["\'][^>]*>(.*?)</textarea>'
        match = re.search(pattern, self.html, re.DOTALL)
        self.assertIsNotNone(match, "custom-questions textarea must be present in index.html")
        val = match.group(1).strip()
        parsed = json.loads(val)
        self.assertIsInstance(parsed, dict)
        self.assertIn("requests_refund", parsed)
        self.assertIn("charge_type", parsed)
        self.assertIn("frustration_level", parsed)


class TestServerEndpoints(unittest.TestCase):
    """Test HTTP API endpoints in server.py using a test server instance."""

    server_thread = None
    httpd = None
    port = 8899

    @classmethod
    def setUpClass(cls):
        server._init_server_state(force_mock=True)

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

    def _post(self, path: str, payload: dict) -> tuple[int, dict]:
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

    def _get(self, path: str) -> tuple[int, dict | str | bytes]:
        url = f"http://127.0.0.1:{self.port}{path}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            if "application/json" in content_type:
                return status, json.loads(raw.decode("utf-8"))
            if "text/" in content_type or "svg" in content_type or "xml" in content_type:
                return status, raw.decode("utf-8")
            return status, raw

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
