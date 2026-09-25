# -*- coding: utf-8 -*-
"""
test_database.py - Comprehensive Unit Tests for JevTools Personal Device SQLite Storage.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

# Ensure root directory is on path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import database


class TestDatabaseModule(unittest.TestCase):
    """Test suite for the zero-dependency SQLite request/response tracking database."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="jevtools_db_test_")
        self.test_db_path = os.path.join(self.temp_dir, "test_jevtools.db")

    def tearDown(self) -> None:
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception:
                pass

    def test_init_db(self) -> None:
        """Verify that init_db initializes the SQLite file and schema correctly."""
        self.assertFalse(os.path.exists(self.test_db_path))
        database.init_db(self.test_db_path)
        self.assertTrue(os.path.exists(self.test_db_path))

        with database.get_connection(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='request_logs';")
            self.assertIsNotNone(cursor.fetchone())

            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_request_logs_%';")
            indexes = [r[0] for r in cursor.fetchall()]
            self.assertIn("idx_request_logs_timestamp", indexes)
            self.assertIn("idx_request_logs_action", indexes)
            self.assertIn("idx_request_logs_status", indexes)

    def test_log_interaction_success(self) -> None:
        """Verify logging of a successful interaction with full metadata."""
        req_payload = {
            "review": "Excellent build quality!",
            "product": "Earbuds Pro",
            "questions": {"sentiment": {"type": "score"}}
        }
        resp_payload = {
            "overall_sentiment": 0.95,
            "action": "[POSITIVE] Testimonial",
            "raw_answers": {"sentiment": {"score": 2.9}}
        }

        row_id = database.log_interaction(
            action_type="review_analysis",
            request_payload=req_payload,
            response_payload=resp_payload,
            provider="openrouter",
            model="~typesafe/jev-latest",
            endpoint="https://openrouter.ai/api/alpha/decisions",
            status="success",
            ttft_ms=286.9,
            elapsed_ms=287.0,
            is_mock=False,
            client_info="test_suite",
            db_path=self.test_db_path,
        )
        self.assertIsNotNone(row_id)
        self.assertGreater(row_id, 0)

        record = database.get_request(row_id, db_path=self.test_db_path)
        self.assertIsNotNone(record)
        self.assertEqual(record["id"], row_id)
        self.assertEqual(record["action_type"], "review_analysis")
        self.assertEqual(record["provider"], "openrouter")
        self.assertEqual(record["model"], "~typesafe/jev-latest")
        self.assertEqual(record["status"], "success")
        self.assertAlmostEqual(record["ttft_ms"], 286.9, places=1)
        self.assertAlmostEqual(record["elapsed_ms"], 287.0, places=1)
        self.assertFalse(record["is_mock"])
        self.assertEqual(record["client_info"], "test_suite")
        self.assertIsNone(record["error_message"])

        # Check deserialized JSON payloads
        self.assertEqual(record["request_payload"]["product"], "Earbuds Pro")
        self.assertEqual(record["response_payload"]["action"], "[POSITIVE] Testimonial")

    def test_log_interaction_error(self) -> None:
        """Verify logging of a failed interaction with error message."""
        row_id = database.log_interaction(
            action_type="custom_decision",
            request_payload={"state": "invalid", "questions": {}},
            response_payload=None,
            provider="typesafe",
            model="jev-latest",
            endpoint="https://api.typesafe.ai/v1/systemone",
            status="error",
            ttft_ms=0.0,
            elapsed_ms=115.4,
            is_mock=False,
            error_message="HTTP 401 Unauthorized: Invalid API Token",
            client_info="test_suite",
            db_path=self.test_db_path,
        )
        self.assertIsNotNone(row_id)

        record = database.get_request(row_id, db_path=self.test_db_path)
        self.assertIsNotNone(record)
        self.assertEqual(record["status"], "error")
        self.assertIn("HTTP 401 Unauthorized", record["error_message"])
        self.assertIsNone(record["response_payload"])

    def test_get_history_ordering_and_pagination(self) -> None:
        """Verify that get_history orders items newest-first and supports pagination."""
        for i in range(1, 11):
            database.log_interaction(
                action_type=f"action_{i}",
                request_payload={"index": i},
                response_payload={"result": i * 10},
                elapsed_ms=float(i * 10),
                db_path=self.test_db_path,
            )

        page_1 = database.get_history(limit=4, offset=0, db_path=self.test_db_path)
        self.assertEqual(len(page_1), 4)
        # Newest first
        self.assertEqual(page_1[0]["id"], 10)
        self.assertEqual(page_1[1]["id"], 9)
        self.assertEqual(page_1[2]["id"], 8)
        self.assertEqual(page_1[3]["id"], 7)

        page_2 = database.get_history(limit=4, offset=4, db_path=self.test_db_path)
        self.assertEqual(len(page_2), 4)
        self.assertEqual(page_2[0]["id"], 6)
        self.assertEqual(page_2[1]["id"], 5)
        self.assertEqual(page_2[2]["id"], 4)
        self.assertEqual(page_2[3]["id"], 3)

        page_3 = database.get_history(limit=4, offset=8, db_path=self.test_db_path)
        self.assertEqual(len(page_3), 2)
        self.assertEqual(page_3[0]["id"], 2)
        self.assertEqual(page_3[1]["id"], 1)

    def test_get_history_filtering(self) -> None:
        """Verify filtering by action_type, status, and search string."""
        database.log_interaction(
            action_type="review_analysis",
            request_payload={"text": "Super fast shipping and great sound"},
            status="success",
            db_path=self.test_db_path,
        )
        database.log_interaction(
            action_type="topic_classification",
            request_payload={"paragraph": "Quantum computing and semiconductors"},
            status="success",
            db_path=self.test_db_path,
        )
        database.log_interaction(
            action_type="review_analysis",
            request_payload={"text": "Defective product, completely broken"},
            status="error",
            error_message="Connection reset by peer",
            db_path=self.test_db_path,
        )

        # Filter by action_type
        reviews = database.get_history(action_type="review_analysis", db_path=self.test_db_path)
        self.assertEqual(len(reviews), 2)
        topics = database.get_history(action_type="topic_classification", db_path=self.test_db_path)
        self.assertEqual(len(topics), 1)

        # Filter by status
        errors = database.get_history(status="error", db_path=self.test_db_path)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["action_type"], "review_analysis")

        # Search term filter
        search_quantum = database.get_history(search="Quantum", db_path=self.test_db_path)
        self.assertEqual(len(search_quantum), 1)
        self.assertEqual(search_quantum[0]["action_type"], "topic_classification")

        search_broken = database.get_history(search="broken", db_path=self.test_db_path)
        self.assertEqual(len(search_broken), 1)

    def test_clear_history(self) -> None:
        """Verify that clear_history removes all logs and vacuums the database."""
        for i in range(5):
            database.log_interaction(
                action_type="review_analysis",
                request_payload={"item": i},
                db_path=self.test_db_path,
            )

        self.assertEqual(len(database.get_history(db_path=self.test_db_path)), 5)
        cleared_count = database.clear_history(db_path=self.test_db_path)
        self.assertEqual(cleared_count, 5)
        self.assertEqual(len(database.get_history(db_path=self.test_db_path)), 0)

    def test_get_stats(self) -> None:
        """Verify calculated stats across mock and live requests."""
        # Log 2 mock requests
        database.log_interaction(
            action_type="review_analysis",
            request_payload={},
            response_payload={},
            ttft_ms=286.9,
            elapsed_ms=287.0,
            is_mock=True,
            status="success",
            provider="openrouter",
            db_path=self.test_db_path,
        )
        database.log_interaction(
            action_type="topic_classification",
            request_payload={},
            response_payload={},
            ttft_ms=200.0,
            elapsed_ms=250.0,
            is_mock=True,
            status="success",
            provider="openrouter",
            db_path=self.test_db_path,
        )
        # Log 1 live error request
        database.log_interaction(
            action_type="custom_decision",
            request_payload={},
            status="error",
            error_message="Network Timeout",
            elapsed_ms=5000.0,
            is_mock=False,
            provider="typesafe",
            db_path=self.test_db_path,
        )

        stats = database.get_stats(db_path=self.test_db_path)
        self.assertEqual(stats["total_requests"], 3)
        self.assertEqual(stats["success_count"], 2)
        self.assertEqual(stats["error_count"], 1)
        self.assertEqual(stats["mock_count"], 2)
        self.assertEqual(stats["live_count"], 1)
        self.assertAlmostEqual(stats["avg_ttft_ms"], (286.9 + 200.0) / 2, places=1)
        self.assertIn("review_analysis", stats["action_breakdown"])
        self.assertIn("topic_classification", stats["action_breakdown"])
        self.assertIn("custom_decision", stats["action_breakdown"])
        self.assertIn("openrouter", stats["provider_breakdown"])
        self.assertIn("typesafe", stats["provider_breakdown"])
        self.assertGreater(stats["db_size_bytes"], 0)

    def test_gitignore_ignores_database_files(self) -> None:
        """Verify that .gitignore properly ignores local database files."""
        gitignore_path = os.path.join(ROOT_DIR, ".gitignore")
        self.assertTrue(os.path.exists(gitignore_path), ".gitignore must exist")

        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check required gitignore patterns
        self.assertIn("jevtools.db", content)
        self.assertIn("*.db", content)
        self.assertIn("*.sqlite", content)

        # Test using git check-ignore if git CLI is available
        try:
            res = subprocess.run(
                ["git", "check-ignore", "-v", "jevtools.db", "test.db", "data/test.sqlite3"],
                cwd=ROOT_DIR,
                capture_output=True,
                text=True,
            )
            if res.returncode == 0:
                self.assertIn("jevtools.db", res.stdout)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    unittest.main()
