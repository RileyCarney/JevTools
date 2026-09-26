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
from typing import Any
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
        req_payload: dict[str, Any] = {
            "review": "Excellent build quality!",
            "product": "Earbuds Pro",
            "questions": {"sentiment": {"type": "score"}}
        }
        resp_payload: dict[str, Any] = {
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
        assert row_id is not None
        self.assertGreater(row_id, 0)

        record = database.get_request(row_id, db_path=self.test_db_path)
        self.assertIsNotNone(record)
        assert record is not None
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
        assert row_id is not None

        record = database.get_request(row_id, db_path=self.test_db_path)
        self.assertIsNotNone(record)
        assert record is not None
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

    def test_get_history_limits_and_search_truncation(self) -> None:
        """Verify that get_history caps limit to MAX_QUERY_LIMIT and truncates search to MAX_SEARCH_LENGTH."""
        # Log a record with a known long string
        database.log_interaction(
            action_type="review_analysis",
            request_payload={"content": "A" * 250},
            db_path=self.test_db_path,
        )

        # Search with >200 chars should be truncated to 200 chars without error
        long_search = "A" * 250
        res = database.get_history(search=long_search, db_path=self.test_db_path)
        self.assertEqual(len(res), 1)

        # Excessive limit should be safely capped to MAX_QUERY_LIMIT (500)
        res_capped = database.get_history(limit=99999, db_path=self.test_db_path)
        self.assertLessEqual(len(res_capped), database.MAX_QUERY_LIMIT)

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

    def test_extended_filtering_and_counting(self) -> None:
        """Verify filtering by provider, model, is_mock, latency, and count_history."""
        database.log_interaction(
            action_type="review_analysis",
            request_payload={"item": "headphones"},
            provider="openrouter",
            model="meta-llama/llama-3.1-8b-instruct",
            is_mock=True,
            elapsed_ms=150.0,
            status="success",
            client_info="web_ui",
            db_path=self.test_db_path,
        )
        database.log_interaction(
            action_type="topic_classification",
            request_payload={"text": "artificial intelligence"},
            provider="typesafe",
            model="~typesafe/jev-latest",
            is_mock=False,
            elapsed_ms=450.0,
            status="success",
            client_info="cli",
            db_path=self.test_db_path,
        )
        database.log_interaction(
            action_type="custom_decision",
            request_payload={"state": "billing_issue"},
            provider="openrouter",
            model="meta-llama/llama-3.1-8b-instruct",
            is_mock=False,
            elapsed_ms=800.0,
            status="error",
            error_message="Gateway timeout",
            client_info="web_ui",
            db_path=self.test_db_path,
        )

        # Count total
        self.assertEqual(database.count_history(db_path=self.test_db_path), 3)

        # Filter by provider
        openrouter_items = database.get_history(provider="openrouter", db_path=self.test_db_path)
        self.assertEqual(len(openrouter_items), 2)
        self.assertEqual(database.count_history(provider="openrouter", db_path=self.test_db_path), 2)

        typesafe_items = database.get_history(provider="typesafe", db_path=self.test_db_path)
        self.assertEqual(len(typesafe_items), 1)

        # Filter by is_mock
        mock_items = database.get_history(is_mock=True, db_path=self.test_db_path)
        self.assertEqual(len(mock_items), 1)
        self.assertEqual(mock_items[0]["action_type"], "review_analysis")

        live_items = database.get_history(is_mock=False, db_path=self.test_db_path)
        self.assertEqual(len(live_items), 2)

        # Filter by latency range
        fast_items = database.get_history(max_latency=300.0, db_path=self.test_db_path)
        self.assertEqual(len(fast_items), 1)
        self.assertEqual(fast_items[0]["elapsed_ms"], 150.0)

        slow_items = database.get_history(min_latency=500.0, db_path=self.test_db_path)
        self.assertEqual(len(slow_items), 1)
        self.assertEqual(slow_items[0]["elapsed_ms"], 800.0)

        # Filter by client_info
        cli_items = database.get_history(client_info="cli", db_path=self.test_db_path)
        self.assertEqual(len(cli_items), 1)
        self.assertEqual(cli_items[0]["provider"], "typesafe")

    def test_custom_sorting_and_unlimited_query(self) -> None:
        """Verify sorting by various columns and allow_unlimited parameter."""
        for i in range(1, 15):
            database.log_interaction(
                action_type="benchmark_ttft",
                request_payload={"run": i},
                elapsed_ms=float(i * 50),
                ttft_ms=float(i * 20),
                db_path=self.test_db_path,
            )

        # Sort by elapsed_ms ascending
        asc_items = database.get_history(sort_by="elapsed_ms", sort_order="ASC", db_path=self.test_db_path)
        self.assertEqual(asc_items[0]["elapsed_ms"], 50.0)
        self.assertEqual(asc_items[-1]["elapsed_ms"], 700.0)

        # Sort by elapsed_ms descending
        desc_items = database.get_history(sort_by="elapsed_ms", sort_order="DESC", db_path=self.test_db_path)
        self.assertEqual(desc_items[0]["elapsed_ms"], 700.0)
        self.assertEqual(desc_items[-1]["elapsed_ms"], 50.0)

        # Unlimited query
        all_items = database.get_history(allow_unlimited=True, db_path=self.test_db_path)
        self.assertEqual(len(all_items), 14)

    def test_get_filter_options(self) -> None:
        """Verify filter options summary returns dynamic metadata and counts."""
        database.log_interaction(
            action_type="review_analysis",
            request_payload={},
            provider="openrouter",
            model="model-a",
            status="success",
            is_mock=True,
            client_info="web_ui",
            db_path=self.test_db_path,
        )
        database.log_interaction(
            action_type="topic_classification",
            request_payload={},
            provider="typesafe",
            model="model-b",
            status="error",
            is_mock=False,
            client_info="python_sdk",
            db_path=self.test_db_path,
        )

        options = database.get_filter_options(db_path=self.test_db_path)
        self.assertEqual(options["total_count"], 2)

        action_names = [a["name"] for a in options["action_types"]]
        self.assertIn("review_analysis", action_names)
        self.assertIn("topic_classification", action_names)

        provider_names = [p["name"] for p in options["providers"]]
        self.assertIn("openrouter", provider_names)
        self.assertIn("typesafe", provider_names)

        model_names = [m["name"] for m in options["models"]]
        self.assertIn("model-a", model_names)
        self.assertIn("model-b", model_names)

        client_names = [c["name"] for c in options["client_infos"]]
        self.assertIn("web_ui", client_names)
        self.assertIn("python_sdk", client_names)

    def test_get_schema_info(self) -> None:
        """Verify SQLite schema inspector returns columns, indexes, and table stats."""
        schema = database.get_schema_info(db_path=self.test_db_path)
        self.assertEqual(schema["table_name"], "request_logs")
        self.assertGreater(len(schema["columns"]), 10)

        col_names = [c["name"] for c in schema["columns"]]
        self.assertIn("id", col_names)
        self.assertIn("timestamp", col_names)
        self.assertIn("action_type", col_names)
        self.assertIn("provider", col_names)
        self.assertIn("model", col_names)
        self.assertIn("endpoint", col_names)
        self.assertIn("status", col_names)
        self.assertIn("ttft_ms", col_names)
        self.assertIn("elapsed_ms", col_names)
        self.assertIn("is_mock", col_names)
        self.assertIn("request_payload", col_names)
        self.assertIn("response_payload", col_names)
        self.assertIn("error_message", col_names)
        self.assertIn("client_info", col_names)

        self.assertIn("journal_mode", schema)
        self.assertIn("indexes", schema)
        index_names = [idx["name"] for idx in schema["indexes"]]
        self.assertIn("idx_request_logs_timestamp", index_names)

    def test_structural_column_filtering(self) -> None:
        """Verify filtering across every structural column and arbitrary column_filters."""
        id1 = database.log_interaction(
            action_type="review_analysis",
            request_payload={"p": 1},
            provider="openrouter",
            model="or-model",
            endpoint="https://openrouter.ai/api/v1/decisions",
            status="success",
            ttft_ms=150.0,
            elapsed_ms=200.0,
            is_mock=False,
            client_info="cli_tool",
            db_path=self.test_db_path,
        )
        id2 = database.log_interaction(
            action_type="topic_classification",
            request_payload={"p": 2},
            provider="typesafe",
            model="ts-model",
            endpoint="https://api.typesafe.ai/v1/systemone",
            status="error",
            ttft_ms=300.0,
            elapsed_ms=450.0,
            is_mock=True,
            error_message="Gateway timeout on upstream node",
            client_info="web_ui",
            db_path=self.test_db_path,
        )

        # 1. Filter by endpoint
        ts_items = database.get_history(endpoint="typesafe.ai", db_path=self.test_db_path)
        self.assertEqual(len(ts_items), 1)
        self.assertEqual(ts_items[0]["id"], id2)

        # 2. Filter by TTFT range
        fast_ttft = database.get_history(max_ttft=200.0, db_path=self.test_db_path)
        self.assertEqual(len(fast_ttft), 1)
        self.assertEqual(fast_ttft[0]["id"], id1)

        slow_ttft = database.get_history(min_ttft=250.0, db_path=self.test_db_path)
        self.assertEqual(len(slow_ttft), 1)
        self.assertEqual(slow_ttft[0]["id"], id2)

        # 3. Filter by ID and ID bounds
        exact_id = database.get_history(id=id1, db_path=self.test_db_path)
        self.assertEqual(len(exact_id), 1)
        self.assertEqual(exact_id[0]["id"], id1)

        id_range = database.get_history(min_id=id2, max_id=id2, db_path=self.test_db_path)
        self.assertEqual(len(id_range), 1)
        self.assertEqual(id_range[0]["id"], id2)

        # 4. Filter by error status and error search
        err_items = database.get_history(has_error=True, db_path=self.test_db_path)
        self.assertEqual(len(err_items), 1)
        self.assertEqual(err_items[0]["id"], id2)

        ok_items = database.get_history(has_error=False, db_path=self.test_db_path)
        self.assertEqual(len(ok_items), 1)
        self.assertEqual(ok_items[0]["id"], id1)

        err_search = database.get_history(error_contains="timeout", db_path=self.test_db_path)
        self.assertEqual(len(err_search), 1)
        self.assertEqual(err_search[0]["id"], id2)

        # 5. Generic structural column_filters (gte operator)
        cf_gte = database.get_history(
            column_filters=[{"column": "elapsed_ms", "operator": "gte", "value": 300}],
            db_path=self.test_db_path,
        )
        self.assertEqual(len(cf_gte), 1)
        self.assertEqual(cf_gte[0]["id"], id2)

        # 6. Generic structural column_filters (eq operator on provider)
        cf_eq = database.get_history(
            column_filters=[{"column": "provider", "operator": "eq", "value": "openrouter"}],
            db_path=self.test_db_path,
        )
        self.assertEqual(len(cf_eq), 1)
        self.assertEqual(cf_eq[0]["id"], id1)

        # 7. Count matches exactly
        self.assertEqual(database.count_history(endpoint="typesafe.ai", db_path=self.test_db_path), 1)
        self.assertEqual(database.count_history(has_error=True, db_path=self.test_db_path), 1)

    def test_enhanced_schema_profiling(self) -> None:
        """Verify get_schema_info returns all_tables, structure map, and column profile metrics."""
        database.log_interaction(
            action_type="review_analysis",
            request_payload={"test": True},
            status="success",
            endpoint="https://openrouter.ai",
            db_path=self.test_db_path,
        )
        database.log_interaction(
            action_type="topic_classification",
            request_payload={"test": True},
            status="error",
            error_message="HTTP 500",
            endpoint="https://api.typesafe.ai",
            db_path=self.test_db_path,
        )

        schema = database.get_schema_info(db_path=self.test_db_path)
        self.assertIn("all_tables", schema)
        self.assertIn("request_logs", schema["all_tables"])
        self.assertIn("structure", schema)
        self.assertEqual(schema["total_records"], 2)

        col_struct = schema["structure"]
        self.assertIn("error_message", col_struct)
        self.assertEqual(col_struct["error_message"]["non_null_count"], 1)
        self.assertEqual(col_struct["error_message"]["null_count"], 1)

        self.assertIn("endpoint", col_struct)
        self.assertEqual(col_struct["endpoint"]["non_null_count"], 2)
        self.assertEqual(col_struct["endpoint"]["distinct_count"], 2)


if __name__ == "__main__":
    unittest.main()
