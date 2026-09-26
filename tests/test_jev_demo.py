#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_jev_demo.py - Comprehensive unit test suite for jev_demo.py and server helpers.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any
import unittest

# Ensure parent directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

import jev_demo


class TestJevDemoExtraction(unittest.TestCase):
    """Test safe extraction helpers for Noul, Score, and Choice primitives."""

    def test_extract_noul_dict(self):
        self.assertAlmostEqual(jev_demo.extract_noul({"noul": 0.85}), 0.85)
        self.assertAlmostEqual(jev_demo.extract_noul({"value": 0.42}), 0.42)
        self.assertAlmostEqual(jev_demo.extract_noul({"probability": 0.99}), 0.99)

    def test_extract_noul_scalar_and_clamping(self):
        self.assertAlmostEqual(jev_demo.extract_noul(0.7), 0.7)
        self.assertAlmostEqual(jev_demo.extract_noul("0.65"), 0.65)
        self.assertEqual(jev_demo.extract_noul(1.5), 1.0)
        self.assertEqual(jev_demo.extract_noul(-0.5), 0.0)
        self.assertEqual(jev_demo.extract_noul("invalid"), 0.0)

    def test_extract_score_dict(self):
        raw, norm, probs, conf = jev_demo.extract_score(
            {"score": 2.0, "probabilities": [0.1, 0.2, 0.7], "confidence": 0.9},
            max_score=2.0
        )
        self.assertEqual(raw, 2.0)
        self.assertEqual(norm, 1.0)
        self.assertEqual(len(probs), 3)
        self.assertEqual(conf, 0.9)

    def test_extract_choice_dict(self):
        choice, conf, probs = jev_demo.extract_choice(
            {"choice": "delighted", "confidence": 0.95, "probabilities": {"delighted": 0.95, "calm": 0.05}}
        )
        self.assertEqual(choice, "delighted")
        self.assertEqual(conf, 0.95)
        self.assertIn("delighted", probs)


class TestJevDemoProviderConfig(unittest.TestCase):
    """Test API key resolution and provider configuration."""

    def test_mask_key(self):
        self.assertEqual(jev_demo.mask_key(""), "[NOT SET]")
        self.assertEqual(jev_demo.mask_key("mock-key-for-testing"), "[MOCK MODE - NO KEY USED]")
        self.assertEqual(jev_demo.mask_key("sk-or-v1-abcdef0123456789xyz"), "sk-...")
        self.assertEqual(jev_demo.mask_key("sk-test1234"), "sk-...")
        self.assertEqual(jev_demo.mask_key("ts-abcdef0123456789"), "ts-...")

    def test_provider_heuristics(self):
        prov1, ep1, mdl1 = jev_demo.get_provider_config("sk-or-v1-testkey")
        self.assertEqual(prov1, "openrouter")
        self.assertIn("openrouter.ai", ep1)
        self.assertIn("jev", mdl1.lower())

        prov2, ep2, mdl2 = jev_demo.get_provider_config("ts-testkey")
        self.assertEqual(prov2, "typesafe")
        self.assertIn("typesafe.ai", ep2)
        self.assertIn("jev", mdl2.lower())

    def test_endpoint_validation_allowlist(self):
        # Valid approved endpoints
        self.assertEqual(
            jev_demo.validate_endpoint("https://openrouter.ai/api/v1/custom", "openrouter"),
            "https://openrouter.ai/api/v1/custom"
        )
        self.assertEqual(
            jev_demo.validate_endpoint("https://api.typesafe.ai/v1/test", "typesafe"),
            "https://api.typesafe.ai/v1/test"
        )

        # Disallowed host should fallback to default with warning
        with self.assertWarns(UserWarning):
            ep = jev_demo.validate_endpoint("https://evil-attacker.com/steal-keys", "openrouter")
            self.assertEqual(ep, jev_demo.OPENROUTER_API_URL)

        # Invalid scheme should fallback to default with warning
        with self.assertWarns(UserWarning):
            ep = jev_demo.validate_endpoint("ftp://openrouter.ai/resource", "openrouter")
            self.assertEqual(ep, jev_demo.OPENROUTER_API_URL)

        # get_provider_config with malicious endpoint
        with self.assertWarns(UserWarning):
            _, ep, _ = jev_demo.get_provider_config(
                "sk-test",
                provider="openrouter",
                endpoint="https://attacker.com/v1"
            )
            self.assertEqual(ep, jev_demo.OPENROUTER_API_URL)


class TestJevDemoReviewPipeline(unittest.TestCase):
    """Test customer review speculative fan-out in mock mode."""

    def test_review_enthusiast(self):
        rev = jev_demo.REVIEW_CASES[0][0]
        prod = jev_demo.REVIEW_CASES[0][1]
        res = jev_demo.analyze_review("mock", rev, prod, mock=True)
        self.assertGreater(res.overall_sentiment, 0.8)
        self.assertGreater(res.would_recommend, 0.9)
        self.assertLess(res.mentions_defect, 0.1)
        self.assertIn("[POSITIVE]", res.action)
        self.assertIsInstance(res.to_dict(), dict)

    def test_review_defect_escalation(self):
        rev = jev_demo.REVIEW_CASES[1][0]
        prod = jev_demo.REVIEW_CASES[1][1]
        res = jev_demo.analyze_review("mock", rev, prod, mock=True)
        self.assertGreater(res.mentions_defect, 0.75)
        self.assertIn("[ESCALATE]", res.action)

    def test_review_ambiguous_routing(self):
        rev = jev_demo.REVIEW_CASES[3][0] # "ok"
        prod = jev_demo.REVIEW_CASES[3][1]
        res = jev_demo.analyze_review("mock", rev, prod, mock=True)
        self.assertLess(res.emotion_confidence, 0.5)
        self.assertIn("[FLAG]", res.action)


class TestJevDemoTopicPipeline(unittest.TestCase):
    """Test topic classification in mock mode."""

    def test_topic_technology(self):
        para = jev_demo.TOPIC_CASES[0] # Transformer LLMs
        res = jev_demo.classify_topic("mock", para, mock=True)
        self.assertEqual(res.primary_topic, "technology")
        self.assertGreater(res.topic_confidence, 0.8)
        self.assertIn("[TECHNICAL: TECHNOLOGY]", res.routing_suggestion)
        self.assertIsInstance(res.to_dict(), dict)

    def test_topic_editorial_health(self):
        para = jev_demo.TOPIC_CASES[1] # Screen time opinion
        res = jev_demo.classify_topic("mock", para, mock=True)
        self.assertEqual(res.primary_topic, "health")
        self.assertGreater(res.is_opinion, 0.8)
        self.assertIn("[EDITORIAL: HEALTH]", res.routing_suggestion)


class TestJevDemoCustomPlayground(unittest.TestCase):
    """Test arbitrary custom questions evaluation."""

    def test_custom_decision(self):
        state = {"user": "Alice", "query": "Cancel my order"}
        questions: dict[str, Any] = {
            "wants_cancel": {"type": "noul", "instructions": "Does query request order cancellation?"},
            "category": {"type": "choice", "criteria": {"cancel": "Cancel", "help": "Help"}},
        }
        res = jev_demo.evaluate_custom_decision("mock", state, questions, mock=True)
        self.assertIn("answers", res)
        self.assertIn("wants_cancel", res["answers"])
        self.assertIn("metadata", res)
        self.assertEqual(res["metadata"]["question_count"], 2)


class TestJevDemoCLI(unittest.TestCase):
    """Test CLI execution and JSON formatting."""

    def test_cli_mock_json(self):
        cmd = [sys.executable, os.path.join(PARENT_DIR, "jev_demo.py"), "--mock", "--demo", "reviews", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertIn("reviews", data)
        self.assertEqual(len(data["reviews"]), len(jev_demo.REVIEW_CASES))

    def test_cli_custom_review(self):
        cmd = [sys.executable, os.path.join(PARENT_DIR, "jev_demo.py"), "--mock", "--review", "Best earbuds ever!", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertIn("overall_sentiment", data)
        self.assertIn("composite_score", data)

    def test_cli_custom_topic(self):
        cmd = [sys.executable, os.path.join(PARENT_DIR, "jev_demo.py"), "--mock", "--topic", "The president signed new legislation.", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertIn("primary_topic", data)


class TestJevDemoTTFT(unittest.TestCase):
    """Test Time To First Token (TTFT) and inference latency generation."""

    def test_tested_constants(self):
        self.assertEqual(jev_demo.OPENROUTER_TESTED_LATENCY_MS, 287.0)
        self.assertEqual(jev_demo.OPENROUTER_TESTED_TTFT_MS, 286.9)

    def test_review_analysis_generates_ttft(self):
        rev = jev_demo.REVIEW_CASES[0][0]
        prod = jev_demo.REVIEW_CASES[0][1]
        res = jev_demo.analyze_review("mock", rev, prod, mock=True)
        self.assertGreater(res.ttft_ms, 0)
        self.assertGreater(res.elapsed_ms, 0)
        d = res.to_dict()
        self.assertIn("ttft_ms", d)
        self.assertIn("elapsed_ms", d)

    def test_topic_classification_generates_ttft(self):
        para = jev_demo.TOPIC_CASES[0]
        res = jev_demo.classify_topic("mock", para, mock=True)
        self.assertGreater(res.ttft_ms, 0)
        self.assertGreater(res.elapsed_ms, 0)
        d = res.to_dict()
        self.assertIn("ttft_ms", d)
        self.assertIn("elapsed_ms", d)

    def test_custom_decision_generates_ttft(self):
        state = {"test": 123}
        questions: dict[str, Any] = {"is_valid": {"type": "noul", "instructions": "Is this valid?"}}
        res = jev_demo.evaluate_custom_decision("mock", state, questions, mock=True)
        self.assertIn("metadata", res)
        self.assertIn("ttft_ms", res["metadata"])
        self.assertIn("elapsed_ms", res["metadata"])
        self.assertGreater(res["metadata"]["ttft_ms"], 0)

    def test_openrouter_api_ttft_benchmark(self):
        """Interacts with OpenRouter API and verifies TTFT and latency measurements."""
        stats = jev_demo.measure_openrouter_ttft(runs=1)
        self.assertIn("avg_ttft_ms", stats)
        self.assertIn("avg_latency_ms", stats)
        self.assertIn("results", stats)
        self.assertGreater(stats["avg_ttft_ms"], 0)
        self.assertGreater(stats["avg_latency_ms"], 0)
        self.assertEqual(len(stats["results"]), 1)

    def test_cli_benchmark_flag(self):
        cmd = [sys.executable, os.path.join(PARENT_DIR, "jev_demo.py"), "--benchmark", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertIn("avg_ttft_ms", data)
        self.assertIn("avg_latency_ms", data)
        self.assertGreater(data["avg_ttft_ms"], 0)


class TestJevDemoHistoryCLI(unittest.TestCase):
    """Test CLI commands for personal device database history inspection and clearing."""

    def test_cli_clear_history(self):
        cmd = [sys.executable, os.path.join(PARENT_DIR, "jev_demo.py"), "--clear-history"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        self.assertIn("[OK] Cleared", result.stdout)

    def test_cli_history_json(self):
        # Clear first
        subprocess.run([sys.executable, os.path.join(PARENT_DIR, "jev_demo.py"), "--clear-history"], check=True)

        # Run a review
        cmd_run = [sys.executable, os.path.join(PARENT_DIR, "jev_demo.py"), "--mock", "--review", "Amazing product", "--json"]
        subprocess.run(cmd_run, check=True)

        # Check history via CLI
        cmd_hist = [sys.executable, os.path.join(PARENT_DIR, "jev_demo.py"), "--history", "--json"]
        result = subprocess.run(cmd_hist, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertIn("stats", data)
        self.assertIn("history", data)
        self.assertGreaterEqual(data["stats"]["total_requests"], 1)
        self.assertEqual(data["history"][0]["action_type"], "review_analysis")

    def test_cli_history_text_display(self):
        cmd_hist = [sys.executable, os.path.join(PARENT_DIR, "jev_demo.py"), "--history"]
        result = subprocess.run(cmd_hist, capture_output=True, text=True, check=True)
        self.assertIn("LOCAL REQUEST/RESPONSE HISTORY & STATS", result.stdout)
        self.assertIn("Database Path", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
