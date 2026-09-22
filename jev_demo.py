# -*- coding: utf-8 -*-
"""
jev_demo.py - Example application using TypeSafe Jev via OpenRouter and TypeSafe API.

Demonstrates two primary use-cases plus a custom evaluation playground:
  1. Customer Review Analysis - score sentiment/quality/actionability, flag escalation
  2. Topic Classification     - classify a paragraph into one of several topic areas
  3. Custom Decision Pipeline - speculative fan-out across user-defined state & questions

Usage:
    py jev_demo.py                          # prompts securely for key
    $env:OPENROUTER_API_KEY="sk-or-..."     # recommended non-interactive form
    py jev_demo.py
    py jev_demo.py --mock                   # test run offline without API calls
    py jev_demo.py --demo reviews           # run review demo only
    py jev_demo.py --demo topics            # run topic demo only
    py jev_demo.py --review "Great ear tips, battery died on day 3." --mock
    py jev_demo.py --topic "The central bank lowered the policy rate." --json --mock

Dependencies:
    pip install requests

Security note on --api-key:
    Passing secrets as CLI arguments exposes them in the OS process table (e.g.
    `ps aux`, Task Manager, shell history). Prefer the OPENROUTER_API_KEY
    environment variable or the interactive prompt (no argument -> getpass).
"""

from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Optional
import argparse
import getpass
import json
import os
import re
import sys
import textwrap
import time

# Configure UTF-8 encoding on Windows to prevent charmap encoding errors
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

try:
    import requests
except ImportError:
    sys.exit("requests is not installed.\nRun:  pip install requests\n")


# ---------------------------------------------------------------------------
# Provider & Endpoint Defaults
# ---------------------------------------------------------------------------

OPENROUTER_API_URL = "https://openrouter.ai/api/alpha/decisions"
OPENROUTER_DEFAULT_MODEL = "~typesafe/jev-latest"

TYPESAFE_API_URL = "https://api.typesafe.ai/v1/systemone"
TYPESAFE_DEFAULT_MODEL = "jev-latest"

# Optional metadata shown on OpenRouter dashboards/rankings
_HTTP_REFERER = os.environ.get("OPENROUTER_REFERER", "https://github.com/RileyCarney/JevTools")
_OPENROUTER_TITLE = os.environ.get("OPENROUTER_TITLE", "JevTools Demo")


def _find_env_file() -> None:
    """Scan current directory and parent directories for a .env file if not already set."""
    search_dirs = [os.getcwd(), os.path.dirname(os.path.abspath(__file__)), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
    for d in search_dirs:
        env_path = os.path.join(d, ".env")
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k not in os.environ:
                                os.environ[k] = v
                break
            except Exception:
                pass


_find_env_file()


def get_provider_config(
    api_key: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> tuple[str, str, str]:
    """
    Determine (provider_name, endpoint_url, model_name) based on explicit options,
    environment variables, and API key prefix heuristics.
    """
    prov = (provider or "").strip().lower()
    key = (api_key or "").strip()

    # Heuristic determination
    if not prov:
        if key.startswith("ts-") or os.environ.get("TYPESAFE_API_KEY"):
            prov = "typesafe"
        else:
            prov = "openrouter"

    if prov == "typesafe":
        ep = endpoint or os.environ.get("JEV_API_URL", TYPESAFE_API_URL)
        mdl = model or os.environ.get("JEV_MODEL", TYPESAFE_DEFAULT_MODEL)
    else:
        prov = "openrouter"
        ep = endpoint or os.environ.get("JEV_API_URL", OPENROUTER_API_URL)
        mdl = model or os.environ.get("JEV_MODEL", OPENROUTER_DEFAULT_MODEL)

    return prov, ep, mdl


def _build_headers(api_key: str, provider: str = "openrouter") -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if provider == "openrouter":
        if _HTTP_REFERER:
            headers["HTTP-Referer"] = _HTTP_REFERER
        if _OPENROUTER_TITLE:
            headers["X-OpenRouter-Title"] = _OPENROUTER_TITLE
    return headers


# ---------------------------------------------------------------------------
# Safe Extraction Helpers
# ---------------------------------------------------------------------------

def extract_noul(ans: Any) -> float:
    """Extract a calibrated float 0.0-1.0 from a Noul answer."""
    if isinstance(ans, dict):
        val = ans.get("noul", ans.get("value", ans.get("probability", 0.0)))
    else:
        val = ans
    try:
        return max(0.0, min(1.0, float(val)))
    except (TypeError, ValueError):
        return 0.0


def extract_score(ans: Any, max_score: float = 1.0) -> tuple[float, float, list[float], float]:
    """
    Extract (raw_score, normalized_0_to_1, probabilities, confidence) from a Score answer.
    """
    if isinstance(ans, dict):
        raw = float(ans.get("score", ans.get("value", 0.0)))
        raw_probs = ans.get("probabilities", [])
        probs = [float(p) for p in raw_probs] if isinstance(raw_probs, list) else []
        conf = float(ans.get("confidence", 0.0))
    else:
        try:
            raw = float(ans)
        except (TypeError, ValueError):
            raw = 0.0
        probs = []
        conf = 1.0

    norm = max(0.0, min(1.0, raw / max_score if max_score > 0 else raw))
    return raw, norm, probs, conf


def extract_choice(ans: Any) -> tuple[str, float, dict[str, float]]:
    """
    Extract (choice, confidence, probabilities_dict) from a Choice answer.
    """
    if isinstance(ans, dict):
        choice = str(ans.get("choice", ans.get("value", "other")))
        raw_probs = ans.get("probabilities", {})
        probs = {str(k): float(v) for k, v in raw_probs.items()} if isinstance(raw_probs, dict) else {}
        conf = float(ans.get("confidence", probs.get(choice, 0.5) if isinstance(probs, dict) else 0.5))
        return choice, conf, probs
    return str(ans), 0.5, {}


# ---------------------------------------------------------------------------
# Intelligent Mock Generator (Offline & Zero-Credit Testing)
# ---------------------------------------------------------------------------

def _mock_jev_response(state: Any, questions: dict) -> dict:
    """
    Generate realistic mock Jev answers for offline testing.
    Uses exact calibrated ground-truth for benchmark cases, and intelligent
    keyword heuristics for arbitrary user inputs.
    """
    answers: dict[str, Any] = {}

    # 1. Customer Review Context
    if isinstance(state, dict) and "review" in state:
        rev = str(state["review"]).strip().lower()
        if "absolutely love" in rev or "transformed" in rev:
            answers["overall_sentiment"] = {"score": 3.0, "confidence": 0.98, "probabilities": [0.0, 0.0, 0.05, 0.95]}
            answers["quality_of_feedback"] = {"score": 2.0, "confidence": 0.92, "probabilities": [0.02, 0.08, 0.90]}
            answers["mentions_defect"] = {"noul": 0.01}
            answers["mentions_shipping"] = {"noul": 0.95 if "shipping" in rev else 0.05}
            answers["would_recommend"] = {"noul": 0.98}
            answers["emotion_tone"] = {
                "choice": "delighted",
                "confidence": 0.97,
                "probabilities": {"delighted": 0.97, "calm": 0.02, "frustrated": 0.00, "other": 0.01},
            }
        elif "battery died" in rev or "disappointed" in rev:
            answers["overall_sentiment"] = {"score": 0.2, "confidence": 0.95, "probabilities": [0.90, 0.08, 0.02, 0.0]}
            answers["quality_of_feedback"] = {"score": 1.8, "confidence": 0.88, "probabilities": [0.05, 0.15, 0.80]}
            answers["mentions_defect"] = {"noul": 0.96}
            answers["mentions_shipping"] = {"noul": 0.02}
            answers["would_recommend"] = {"noul": 0.02}
            answers["emotion_tone"] = {
                "choice": "frustrated",
                "confidence": 0.95,
                "probabilities": {"frustrated": 0.95, "calm": 0.03, "delighted": 0.00, "other": 0.02},
            }
        elif rev in ("ok", "fine", "meh"):
            answers["overall_sentiment"] = {"score": 1.5, "confidence": 0.45, "probabilities": [0.1, 0.4, 0.4, 0.1]}
            answers["quality_of_feedback"] = {"score": 0.0, "confidence": 0.99, "probabilities": [0.98, 0.02, 0.0]}
            answers["mentions_defect"] = {"noul": 0.05}
            answers["mentions_shipping"] = {"noul": 0.05}
            answers["would_recommend"] = {"noul": 0.50}
            answers["emotion_tone"] = {
                "choice": "other",
                "confidence": 0.40,
                "probabilities": {"calm": 0.35, "other": 0.40, "frustrated": 0.15, "delighted": 0.10},
            }
        elif "decent product" in rev or "ear tips" in rev:
            answers["overall_sentiment"] = {"score": 1.8, "confidence": 0.85, "probabilities": [0.05, 0.25, 0.65, 0.05]}
            answers["quality_of_feedback"] = {"score": 1.3, "confidence": 0.80, "probabilities": [0.1, 0.7, 0.2]}
            answers["mentions_defect"] = {"noul": 0.12}
            answers["mentions_shipping"] = {"noul": 0.92}
            answers["would_recommend"] = {"noul": 0.35}
            answers["emotion_tone"] = {
                "choice": "calm",
                "confidence": 0.88,
                "probabilities": {"calm": 0.88, "frustrated": 0.06, "delighted": 0.04, "other": 0.02},
            }
        else:
            # Dynamic semantic mock for arbitrary reviews
            pos_words = ["great", "love", "awesome", "excellent", "good", "amazing", "perfect", "fantastic", "pleased", "recommend"]
            neg_words = ["bad", "terrible", "horrible", "worst", "broken", "poor", "defect", "hate", "unhappy", "waste", "disappointed", "died"]
            defect_words = ["broken", "defect", "defective", "stopped", "died", "cracked", "damage", "malfunction", "fault", "failed"]
            shipping_words = ["ship", "shipping", "delivery", "delivered", "package", "arrived", "box", "transit", "courier"]
            frust_words = ["angry", "irritated", "furious", "annoyed", "frustrated", "scam", "refund", "useless", "sucks"]

            pos_hits = sum(1 for w in pos_words if w in rev)
            neg_hits = sum(1 for w in neg_words if w in rev)
            has_defect = any(w in rev or w in rev for w in defect_words)
            has_shipping = any(w in rev for w in shipping_words)
            has_frust = any(w in rev for w in frust_words)

            if pos_hits > neg_hits and not has_defect:
                score_val = min(3.0, 2.0 + 0.3 * pos_hits)
                emotion = "delighted" if pos_hits >= 2 else "calm"
                rec_p = 0.88
                defect_p = 0.04
            elif has_defect or neg_hits > pos_hits or has_frust:
                score_val = max(0.1, 0.8 - 0.2 * neg_hits)
                emotion = "frustrated"
                rec_p = 0.08
                defect_p = 0.92 if has_defect else 0.45
            else:
                score_val = 1.6
                emotion = "calm"
                rec_p = 0.50
                defect_p = 0.15

            word_count = len(rev.split())
            quality_score = 2.0 if word_count > 25 else (1.0 if word_count > 8 else 0.1)

            answers["overall_sentiment"] = {
                "score": round(score_val, 2),
                "confidence": 0.89,
                "probabilities": [0.1, 0.2, 0.4, 0.3],
            }
            answers["quality_of_feedback"] = {
                "score": round(quality_score, 2),
                "confidence": 0.86,
                "probabilities": [0.1, 0.4, 0.5],
            }
            answers["mentions_defect"] = {"noul": round(defect_p, 2)}
            answers["mentions_shipping"] = {"noul": 0.94 if has_shipping else 0.06}
            answers["would_recommend"] = {"noul": round(rec_p, 2)}
            answers["emotion_tone"] = {
                "choice": emotion,
                "confidence": 0.91,
                "probabilities": {emotion: 0.91, "calm": 0.05, "other": 0.04},
            }

    # 2. Topic Classification Context
    elif isinstance(state, dict) and "paragraph" in state:
        para = str(state["paragraph"]).strip().lower()
        if "transformer" in para or "attention heads" in para:
            answers["primary_topic"] = {
                "choice": "technology",
                "confidence": 0.98,
                "probabilities": {"technology": 0.98, "science": 0.02, "business": 0.0, "education": 0.0},
            }
            answers["is_opinion"] = {"noul": 0.08}
            answers["technical_depth"] = {"score": 2.0, "confidence": 0.95, "probabilities": [0.0, 0.05, 0.95]}
            answers["has_actionable"] = {"noul": 0.05}
        elif "screen time" in para:
            answers["primary_topic"] = {
                "choice": "health",
                "confidence": 0.82,
                "probabilities": {"health": 0.82, "politics": 0.12, "education": 0.04, "culture": 0.02},
            }
            answers["is_opinion"] = {"noul": 0.92}
            answers["technical_depth"] = {"score": 0.7, "confidence": 0.85, "probabilities": [0.4, 0.5, 0.1]}
            answers["has_actionable"] = {"noul": 0.88}
        elif "federal reserve" in para or "interest rates" in para:
            answers["primary_topic"] = {
                "choice": "business",
                "confidence": 0.96,
                "probabilities": {"business": 0.96, "politics": 0.03, "other": 0.01},
            }
            answers["is_opinion"] = {"noul": 0.12}
            answers["technical_depth"] = {"score": 1.2, "confidence": 0.88, "probabilities": [0.1, 0.7, 0.2]}
            answers["has_actionable"] = {"noul": 0.04}
        elif "risotto" in para or "recipe" in para or "butter" in para:
            answers["primary_topic"] = {
                "choice": "culture",
                "confidence": 0.94,
                "probabilities": {"culture": 0.94, "health": 0.04, "other": 0.02},
            }
            answers["is_opinion"] = {"noul": 0.10}
            answers["technical_depth"] = {"score": 0.5, "confidence": 0.80, "probabilities": [0.6, 0.35, 0.05]}
            answers["has_actionable"] = {"noul": 0.92}
        elif "atlantic meridional" in para or "amoc" in para or "climate" in para:
            answers["primary_topic"] = {
                "choice": "science",
                "confidence": 0.95,
                "probabilities": {"science": 0.95, "environment": 0.04, "other": 0.01},
            }
            answers["is_opinion"] = {"noul": 0.15}
            answers["technical_depth"] = {"score": 1.7, "confidence": 0.90, "probabilities": [0.05, 0.25, 0.70]}
            answers["has_actionable"] = {"noul": 0.08}
        else:
            # Dynamic topic keywords classifier
            categories = {
                "technology": ["software", "hardware", "ai", "model", "algorithm", "computer", "code", "python", "chip", "cyber", "internet", "gpu"],
                "science": ["physics", "biology", "molecule", "astronomy", "cell", "genome", "quantum", "chemistry", "research", "experiment"],
                "business": ["market", "stock", "revenue", "economy", "bank", "investor", "sales", "ceo", "company", "profit", "trade"],
                "politics": ["senate", "congress", "president", "vote", "election", "law", "government", "policy", "treaty", "court"],
                "health": ["doctor", "disease", "fitness", "nutrition", "diet", "mental", "hospital", "patient", "medical", "exercise"],
                "environment": ["climate", "ocean", "forest", "emissions", "carbon", "wildlife", "energy", "solar", "species", "planet"],
                "culture": ["movie", "music", "art", "sport", "game", "book", "food", "fashion", "film", "culinary"],
                "education": ["student", "school", "university", "teach", "learn", "degree", "academic", "course", "curriculum"],
            }
            scores = {cat: 0.05 for cat in categories}
            for cat, words in categories.items():
                for w in words:
                    if w in para:
                        scores[cat] += 0.35

            total = sum(scores.values()) or 1.0
            probs = {cat: round(v / total, 3) for cat, v in scores.items()}
            sorted_cats = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            top_choice, top_prob = sorted_cats[0]

            is_opinion_val = 0.78 if any(w in para for w in ["should", "must", "believe", "opinion", "terrible", "ought"]) else 0.14
            actionable_val = 0.85 if any(w in para for w in ["call", "visit", "click", "buy", "remember to", "ensure", "check out"]) else 0.09
            depth_val = 1.6 if any(len(w) > 9 for w in para.split()) else 0.8

            answers["primary_topic"] = {
                "choice": top_choice,
                "confidence": round(top_prob, 2),
                "probabilities": probs,
            }
            answers["is_opinion"] = {"noul": is_opinion_val}
            answers["technical_depth"] = {"score": depth_val, "confidence": 0.85, "probabilities": [0.2, 0.5, 0.3]}
            answers["has_actionable"] = {"noul": actionable_val}

    # 3. Handle Any Remaining or Custom User-Defined Questions
    for q_id, q_spec in questions.items():
        if q_id in answers:
            continue
        q_type = str(q_spec.get("type", "noul")).lower()
        if q_type == "noul":
            answers[q_id] = {"noul": 0.72}
        elif q_type == "choice":
            crit = q_spec.get("criteria", {})
            if isinstance(crit, dict) and crit:
                keys = list(crit.keys())
                picked = keys[0]
                n = len(keys)
                dist = {k: round(1.0 / n, 2) for k in keys}
                dist[picked] = round(1.0 - sum(v for k, v in dist.items() if k != picked), 2)
            else:
                picked = "option_a"
                dist = {"option_a": 0.85, "option_b": 0.15}
            answers[q_id] = {
                "choice": picked,
                "confidence": 0.85,
                "probabilities": dist,
            }
        elif q_type == "score":
            crit = q_spec.get("criteria", [])
            n_levels = len(crit) if isinstance(crit, list) and crit else 3
            answers[q_id] = {
                "score": round((n_levels - 1) * 0.65, 2),
                "confidence": 0.88,
                "probabilities": [round(1.0 / n_levels, 2)] * n_levels,
            }
        else:
            answers[q_id] = {"noul": 0.5}

    return answers


# ---------------------------------------------------------------------------
# API Transport
# ---------------------------------------------------------------------------

def _call_jev(
    api_key: str,
    state: Any,
    questions: dict,
    mock: bool = False,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> dict:
    """
    POST to the Jev decisions endpoint (OpenRouter or TypeSafe) and return the
    parsed answers dictionary.
    """
    if mock:
        return _mock_jev_response(state, questions)

    prov, url, mdl = get_provider_config(api_key, provider=provider, model=model, endpoint=endpoint)
    payload = {
        "model": mdl,
        "state": state,
        "questions": questions,
    }

    try:
        resp = requests.post(
            url=url,
            headers=_build_headers(api_key, provider=prov),
            json=payload,
            timeout=60,
        )
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network error connecting to {prov.title()} ({url}): {exc}") from exc

    if not resp.ok:
        try:
            err_data = resp.json()
            err_msg = (
                err_data.get("error", {}).get("message")
                or err_data.get("message")
                or str(err_data)
            )
        except Exception:
            err_msg = resp.text.strip() or f"HTTP {resp.status_code}"
        raise RuntimeError(f"{prov.title()} API error (HTTP {resp.status_code}): {err_msg}")

    data = resp.json()
    answers = data.get("answers")
    if answers is None and "data" in data and isinstance(data["data"], dict):
        answers = data["data"].get("answers")
    if answers is None and "result" in data and isinstance(data["result"], dict):
        answers = data["result"].get("answers")

    if answers is None or not isinstance(answers, dict):
        raise RuntimeError(f"Response missing 'answers' dictionary from {url}: {data}")

    return answers


# ============================================================================
# Shared Helpers & Formatter
# ============================================================================

DIVIDER = "=" * 64


def section(title: str) -> None:
    print(f"\n{DIVIDER}\n  {title}\n{DIVIDER}")


def confidence_label(conf: float) -> str:
    """Map confidence to a human-readable operational tier."""
    if conf >= 0.8:
        return "HIGH   [OK] act automatically"
    if conf >= 0.5:
        return "MEDIUM [!]  confirm / flag"
    return "LOW    [X]  route to human"


def mask_key(key: str) -> str:
    """Mask an API key for safe console display."""
    clean = (key or "").strip()
    if not clean:
        return "[NOT SET]"
    if clean.startswith("mock-") or clean == "mock-key-for-testing":
        return "[MOCK MODE - NO KEY USED]"
    if clean.startswith("sk-"):
        return "sk-..."
    if clean.startswith("ts-"):
        return "ts-..."
    if len(clean) <= 12:
        return "*" * len(clean)
    return f"{clean[:10]}...{clean[-4:]}"


# ============================================================================
# USE-CASE 1: Customer Review Analysis
# ============================================================================

@dataclass
class ReviewResult:
    review: str
    product: str
    overall_sentiment: float              # 0-1 normalized (Score, 4 levels -> /3)
    sentiment_raw_score: float            # 0-3 raw score
    sentiment_probabilities: list[float]  # distribution across 4 levels
    quality_of_feedback: float            # 0-1 normalized (Score, 3 levels -> /2)
    quality_raw_score: float              # 0-2 raw score
    quality_probabilities: list[float]    # distribution across 3 levels
    mentions_defect: float                # Noul probability
    mentions_shipping: float              # Noul probability
    would_recommend: float                # Noul probability
    emotion_tone: str                     # Choice
    emotion_confidence: float             # Choice confidence
    emotion_probabilities: dict[str, float] # Choice probabilities
    composite_score: float                # weighted composite
    action: str                           # determined by policy in code
    raw_answers: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_review(
    api_key: str,
    review_text: str,
    product_name: str,
    mock: bool = False,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> ReviewResult:
    """
    Analyze a single customer review using parallel Jev questions.
    All 6 questions are sent in ONE request (speculative fan-out).
    """
    state = {
        "review": review_text,
        "product": product_name,
    }

    questions = {
        # Score: overall sentiment (4 levels, 0-3 -> normalized to 0-1)
        "overall_sentiment": {
            "type": "score",
            "instructions": "What is the overall sentiment expressed in `review` about `product`?",
            "criteria": [
                "Strongly negative - the customer is dissatisfied or angry with the product.",
                "Somewhat negative - the customer has more complaints than praise.",
                "Somewhat positive - the customer is mostly satisfied with minor issues.",
                "Strongly positive - the customer is enthusiastic and pleased with the product.",
            ],
        },
        # Score: quality/actionability of the feedback (3 levels, 0-2 -> normalized to 0-1)
        "quality_of_feedback": {
            "type": "score",
            "instructions": "How detailed and actionable is the feedback in `review`?",
            "criteria": [
                "Vague - no specific details, examples, or constructive information.",
                "Moderate - some specific details but lacks concrete examples or suggestions.",
                "Detailed - specific examples, clear descriptions, and/or actionable suggestions.",
            ],
        },
        # Noul: does the review mention a product defect/fault?
        "mentions_defect": {
            "type": "noul",
            "instructions": "Does `review` mention a defect, malfunction, or quality problem with `product`?",
            "criteria": {
                "true":  "The reviewer explicitly describes something broken, faulty, defective, or of poor quality.",
                "false": "The review does not mention any product defect or quality issue.",
            },
        },
        # Noul: does the review mention shipping/delivery?
        "mentions_shipping": {
            "type": "noul",
            "instructions": "Does `review` mention shipping speed, delivery condition, or packaging for `product`?",
        },
        # Noul: would the reviewer recommend the product?
        "would_recommend": {
            "type": "noul",
            "instructions": "Based on `review`, would this customer recommend `product` to others?",
            "criteria": {
                "true":  "The reviewer explicitly recommends it or expresses strong satisfaction.",
                "false": "The reviewer explicitly discourages purchasing or expresses strong dissatisfaction.",
            },
        },
        # Choice: emotional tone (for routing/escalation decisions)
        "emotion_tone": {
            "type": "choice",
            "instructions": "What is the primary emotional tone of `review`?",
            "criteria": {
                "calm":       "Matter-of-fact, neutral language. No strong positive or negative emotion.",
                "frustrated": "Irritated, annoyed, or disappointed. Expresses dissatisfaction or complaints.",
                "delighted":  "Enthusiastic, excited, or very pleased. Strong positive emotion.",
                "other":      "Mixed emotions, sarcasm, or tone that doesn't clearly fit the above.",
            },
        },
    }

    a = _call_jev(api_key, state, questions, mock=mock, provider=provider, model=model, endpoint=endpoint)

    # ---- Policy in code (not in questions) ----
    sent_raw, sentiment_norm, sent_probs, sent_conf = extract_score(a.get("overall_sentiment"), max_score=3.0)
    qual_raw, quality_norm, qual_probs, qual_conf = extract_score(a.get("quality_of_feedback"), max_score=2.0)

    recommend_p = extract_noul(a.get("would_recommend"))
    defect_p = extract_noul(a.get("mentions_defect"))
    shipping_p = extract_noul(a.get("mentions_shipping"))

    emotion, emotion_conf, emotion_probs = extract_choice(a.get("emotion_tone"))

    # Composite review score: weighted combination
    composite = (
        0.40 * sentiment_norm
        + 0.25 * recommend_p
        + 0.20 * quality_norm
        + 0.15 * (1.0 - defect_p)   # defect = bad signal -> invert
    )
    composite = round(max(0.0, min(1.0, composite)), 4)

    # Action routing
    if emotion_conf < 0.5:
        action = "[FLAG] Ambiguous tone - route to human reviewer"
    elif defect_p > 0.75:
        action = "[ESCALATE] High-probability product defect mentioned"
    elif emotion == "frustrated" and composite < 0.35:
        action = "[CONTACT] Frustrated customer with poor experience - outreach recommended"
    elif composite >= 0.70:
        action = "[POSITIVE] Feature as testimonial or send thank-you"
    elif composite >= 0.40:
        action = "[REVIEW] Moderate feedback - log for product team"
    else:
        action = "[POOR] Low-score review - log and consider follow-up"

    return ReviewResult(
        review=review_text,
        product=product_name,
        overall_sentiment=sentiment_norm,
        sentiment_raw_score=sent_raw,
        sentiment_probabilities=sent_probs,
        quality_of_feedback=quality_norm,
        quality_raw_score=qual_raw,
        quality_probabilities=qual_probs,
        mentions_defect=defect_p,
        mentions_shipping=shipping_p,
        would_recommend=recommend_p,
        emotion_tone=emotion,
        emotion_confidence=emotion_conf,
        emotion_probabilities=emotion_probs,
        composite_score=composite,
        action=action,
        raw_answers=a,
    )


def print_review_result(result: ReviewResult, idx: int) -> None:
    print(f"\n  Review #{idx}")
    print(f"  Text: {textwrap.shorten(result.review, width=70, placeholder='...')}")
    print(f"\n  Scores:")
    print(f"    Overall sentiment   : {result.overall_sentiment:.2f}  (0=very negative, 1=very positive)")
    print(f"    Feedback quality    : {result.quality_of_feedback:.2f}  (0=vague, 1=detailed/actionable)")
    print(f"    Composite score     : {result.composite_score:.2f}")
    print(f"\n  Signals (Noul probabilities):")
    print(f"    Would recommend     : {result.would_recommend:.2%}")
    print(f"    Mentions defect     : {result.mentions_defect:.2%}")
    print(f"    Mentions shipping   : {result.mentions_shipping:.2%}")
    print(f"\n  Emotion tone        : {result.emotion_tone}  (confidence: {result.emotion_confidence:.2f} - {confidence_label(result.emotion_confidence)})")
    print(f"\n  Action              : {result.action}")


# ============================================================================
# USE-CASE 2: Topic Classification
# ============================================================================

@dataclass
class TopicResult:
    paragraph: str
    primary_topic: str
    topic_confidence: float
    topic_probabilities: dict[str, float]
    is_opinion: float                           # Noul: probability it's opinion vs fact
    technical_depth: float                      # Score 0-1 normalized
    technical_depth_raw: float                  # Score 0-2 raw
    technical_depth_probabilities: list[float]  # Score probabilities
    has_actionable: float                       # Noul
    routing_suggestion: str
    raw_answers: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def classify_topic(
    api_key: str,
    paragraph: str,
    mock: bool = False,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> TopicResult:
    """
    Classify the topic area and properties of a paragraph.
    All 4 questions are sent in ONE request (parallel evaluation).
    """
    state = {"paragraph": paragraph}

    questions = {
        # Choice: primary topic (8 domains + fallback)
        "primary_topic": {
            "type": "choice",
            "instructions": "What is the primary subject area of `paragraph`?",
            "criteria": {
                "technology":  "Software, hardware, AI/ML, programming, cybersecurity, or tech products.",
                "science":     "Natural sciences: physics, chemistry, biology, medicine, or research findings.",
                "business":    "Economics, finance, markets, entrepreneurship, corporate strategy, or management.",
                "politics":    "Government, policy, elections, legislation, international relations, or political figures.",
                "health":      "Personal health, fitness, nutrition, mental health, or wellness practices.",
                "environment": "Climate, ecology, conservation, sustainability, or environmental policy.",
                "culture":     "Arts, entertainment, sports, social trends, history, or lifestyle.",
                "education":   "Learning, academic research, schools, pedagogy, or skills development.",
                "other":       "The paragraph does not clearly belong to any of the above categories.",
            },
        },
        # Noul: is this opinion/editorial rather than factual/neutral?
        "is_opinion": {
            "type": "noul",
            "instructions": (
                "Is `paragraph` primarily expressing an opinion, editorial view, or subjective "
                "perspective rather than stating objective facts?"
            ),
            "criteria": {
                "true":  "The paragraph uses evaluative language, expresses a viewpoint, or argues a position.",
                "false": "The paragraph reports facts, describes events, or explains concepts without a clear personal stance.",
            },
        },
        # Score: technical depth (3 levels -> normalized 0-1)
        "technical_depth": {
            "type": "score",
            "instructions": "What level of technical expertise does `paragraph` assume in the reader?",
            "criteria": [
                "General audience - uses plain language, no jargon, accessible to anyone.",
                "Informed reader - some domain terminology, assumes basic familiarity with the subject.",
                "Specialist - dense technical language, assumes expert-level background knowledge.",
            ],
        },
        # Noul: does the paragraph contain a call-to-action or recommendation?
        "has_actionable": {
            "type": "noul",
            "instructions": (
                "Does `paragraph` contain a call-to-action, recommendation, or directive "
                "telling the reader to do something?"
            ),
        },
    }

    a = _call_jev(api_key, state, questions, mock=mock, provider=provider, model=model, endpoint=endpoint)

    topic, topic_conf, topic_probs = extract_choice(a.get("primary_topic"))
    is_opinion = extract_noul(a.get("is_opinion"))
    depth_raw, depth_norm, depth_probs, depth_conf = extract_score(a.get("technical_depth"), max_score=2.0)
    actionable = extract_noul(a.get("has_actionable"))

    # ---- Routing policy in code ----
    if topic_conf < 0.5:
        routing = (
            f"[MULTI-TOPIC] Low confidence ({topic_conf:.0%}) - paragraph may span "
            f"several subject areas. Consider splitting or tagging with top-2 topics."
        )
    elif is_opinion > 0.8 and topic in ("politics", "culture", "business", "health"):
        routing = f"[EDITORIAL: {topic.upper()}] High-opinion content - route to editorial desk for review."
    elif depth_norm > 0.65 and topic in ("technology", "science"):
        routing = f"[TECHNICAL: {topic.upper()}] Specialist-level content - route to subject-matter expert."
    elif actionable > 0.75:
        routing = f"[ACTIONABLE: {topic.upper()}] Contains call-to-action - route to campaign/engagement team."
    else:
        routing = f"[STANDARD: {topic.upper()}] Route to {topic} content section."

    return TopicResult(
        paragraph=paragraph,
        primary_topic=topic,
        topic_confidence=topic_conf,
        topic_probabilities=topic_probs,
        is_opinion=is_opinion,
        technical_depth=depth_norm,
        technical_depth_raw=depth_raw,
        technical_depth_probabilities=depth_probs,
        has_actionable=actionable,
        routing_suggestion=routing,
        raw_answers=a,
    )


def print_topic_result(result: TopicResult, idx: int) -> None:
    print(f"\n  Paragraph #{idx}")
    print(f"  Text: {textwrap.shorten(result.paragraph, width=70, placeholder='...')}")
    print(f"\n  Primary topic       : {result.primary_topic.upper()}  "
          f"(confidence: {result.topic_confidence:.2f} - {confidence_label(result.topic_confidence)})")
    print(f"\n  Topic probabilities:")
    sorted_probs = sorted(result.topic_probabilities.items(), key=lambda x: x[1], reverse=True)
    for topic, prob in sorted_probs[:4]:
        bar = "#" * int(prob * 30)
        print(f"    {topic:<14} {prob:.2%}  {bar}")
    print(f"\n  Signals (Noul probabilities):")
    print(f"    Is opinion/editorial: {result.is_opinion:.2%}")
    print(f"    Has call-to-action  : {result.has_actionable:.2%}")
    print(f"    Technical depth     : {result.technical_depth:.2f}  (0=general, 1=specialist)")
    print(f"\n  Routing             : {result.routing_suggestion}")


# ============================================================================
# USE-CASE 3: Custom Decision Evaluation
# ============================================================================

def evaluate_custom_decision(
    api_key: str,
    state: Any,
    questions: dict,
    mock: bool = False,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> dict[str, Any]:
    """
    Evaluate arbitrary user-defined state and questions dictionary via Jev.
    Returns full raw answers dictionary alongside execution metadata.
    """
    start_time = time.perf_counter()
    prov, ep, mdl = get_provider_config(api_key, provider=provider, model=model, endpoint=endpoint)
    answers = _call_jev(
        api_key=api_key,
        state=state,
        questions=questions,
        mock=mock,
        provider=prov,
        model=mdl,
        endpoint=ep,
    )
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return {
        "answers": answers,
        "metadata": {
            "provider": prov,
            "endpoint": ep if not mock else "[OFFLINE MOCK]",
            "model": mdl,
            "mock": mock,
            "elapsed_ms": round(elapsed_ms, 2),
            "question_count": len(questions),
        },
    }


# ============================================================================
# Benchmark Cases
# ============================================================================

REVIEW_CASES = [
    (
        "Absolutely love this product! Works exactly as described and shipping "
        "was super fast. Already recommended it to three friends. Will definitely "
        "buy again from this seller.",
        "Wireless Earbuds Pro",
    ),
    (
        "The battery died after two weeks of normal use. Contacted support but "
        "they were unhelpful. The charging cable also stopped working. Very "
        "disappointed - expected better quality for this price point. Do not buy.",
        "Wireless Earbuds Pro",
    ),
    (
        "Decent product overall. Sound quality is good but the ear tips are a "
        "bit uncomfortable after an hour. Arrived on time and packaging was nice. "
        "Probably wouldn't buy again but not terrible.",
        "Wireless Earbuds Pro",
    ),
    (
        "ok",
        "Wireless Earbuds Pro",
    ),
    (
        "These headphones have completely transformed my daily commute! The noise "
        "cancellation is incredible - I can barely hear the subway. The touch "
        "controls are intuitive and battery life is exactly as advertised at 28 "
        "hours. Build quality feels premium. Best purchase I've made this year "
        "without a doubt. If you're on the fence, just buy them!",
        "Wireless Earbuds Pro",
    ),
]

TOPIC_CASES = [
    (
        "Transformer-based large language models have demonstrated emergent "
        "capabilities at scale, including few-shot reasoning and chain-of-thought "
        "prompting. Recent interpretability work suggests that attention heads "
        "specialize in syntactic roles such as subject-verb agreement and "
        "coreference resolution, pointing toward mechanistic explanations of "
        "in-context learning."
    ),
    (
        "Every parent should limit their child's screen time to no more than two "
        "hours per day. Excessive social media use has been linked to anxiety, "
        "poor sleep, and reduced attention spans in adolescents. It's time for "
        "governments to regulate algorithm-driven content before an entire "
        "generation is harmed."
    ),
    (
        "The Federal Reserve raised interest rates by 25 basis points at its "
        "September meeting, citing continued resilience in the labor market and "
        "core inflation remaining above the 2% target. Markets responded with "
        "a brief sell-off in equities before recovering most losses by close."
    ),
    (
        "To prepare the perfect risotto, toast the arborio rice in butter for "
        "two minutes before adding white wine. Add warm stock one ladle at a "
        "time, stirring constantly, and finish with cold butter and parmesan "
        "off the heat. Serve immediately - risotto waits for no one."
    ),
    (
        "Climate scientists at NOAA report that the Atlantic Meridional "
        "Overturning Circulation (AMOC) has weakened significantly compared "
        "to pre-industrial levels. A substantial weakening or collapse could "
        "dramatically alter precipitation patterns across Europe and North "
        "America and accelerate sea level rise along the eastern US coastline."
    ),
]


# ============================================================================
# CLI & Key Management
# ============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Jev demo: customer review analysis + topic classification via OpenRouter / TypeSafe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              py jev_demo.py                            # Secure interactive prompt
              $env:OPENROUTER_API_KEY="sk-or-v1-..."    # PowerShell env var (recommended)
              py jev_demo.py
              py jev_demo.py --mock                     # Test run offline without API calls
              py jev_demo.py --demo reviews             # Run review analysis demo only
              py jev_demo.py --demo topics              # Run topic classification demo only
              py jev_demo.py --review "Great sound!" --product "Earbuds" --mock
              py jev_demo.py --topic "Interest rates rose by 25 bps" --json --mock
        """),
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=None,
        metavar="KEY",
        help=(
            "API key (sk-or-v1-... or ts-...). Falls back to OPENROUTER_API_KEY or "
            "TYPESAFE_API_KEY env var, then an interactive secure prompt. "
            "[!] Passing secrets via CLI arguments exposes them in the OS process "
            "table (ps, Task Manager, shell history). Prefer env var or prompt."
        ),
    )
    parser.add_argument(
        "--provider",
        choices=["openrouter", "typesafe"],
        default=None,
        help="Explicitly select provider: 'openrouter' or 'typesafe'. Auto-detected from key if omitted.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override model name (e.g. ~typesafe/jev-latest, typesafe/jev-1.13, jev-latest).",
    )
    parser.add_argument(
        "--endpoint",
        default=None,
        help="Override decision API endpoint URL.",
    )
    parser.add_argument(
        "--demo",
        choices=["reviews", "topics", "all"],
        default="all",
        help="Which benchmark demo to run: 'reviews', 'topics', or 'all' (default: all).",
    )
    parser.add_argument(
        "--review",
        default=None,
        help="Custom customer review text to evaluate immediately.",
    )
    parser.add_argument(
        "--product",
        default="Wireless Earbuds Pro",
        help="Product name for custom review evaluation (default: Wireless Earbuds Pro).",
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Custom paragraph text to classify immediately.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in offline mock mode to test formatting and policy logic without making API calls.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON results instead of human-readable text.",
    )
    return parser.parse_args()


def resolve_api_key(cli_key: Optional[str], mock: bool = False) -> str:
    """
    Return the API key using the safest available source:
      1. OPENROUTER_API_KEY, TYPESAFE_API_KEY, or OPENROUTER_KEY env var
      2. Interactive getpass prompt (never echoed to terminal or history)
      3. --api-key CLI argument (accepted, but warns loudly about process table exposure)
    """
    if mock:
        return "mock-key-for-testing"

    # 1. Environment variables - preferred for non-interactive / automated use
    for env_var in ("OPENROUTER_API_KEY", "TYPESAFE_API_KEY", "OPENROUTER_KEY", "JEV_API_KEY"):
        val = os.environ.get(env_var, "").strip()
        if val:
            return val

    # 2. Interactive secure prompt - preferred when running in a terminal
    if sys.stdin.isatty():
        try:
            print("\n[?] No OPENROUTER_API_KEY or TYPESAFE_API_KEY environment variable detected.")
            prompted = getpass.getpass("Enter your OpenRouter or TypeSafe API key: ").strip()
            if prompted:
                return prompted
        except (KeyboardInterrupt, EOFError):
            print()

    # 3. CLI argument - least secure; accepted with loud warning
    if cli_key:
        print(
            "\n[WARNING] --api-key passed on the command line. The key is visible in\n"
            "          the OS process table (e.g. Task Manager, ps aux) and may be saved\n"
            "          in shell history. Please set the OPENROUTER_API_KEY environment\n"
            "          variable or use the interactive prompt instead.\n",
            file=sys.stderr,
        )
        return cli_key

    sys.exit(
        "\nError: No API key provided.\n"
        "To run with your OpenRouter key, choose one of these options:\n"
        "  1. Set the environment variable in PowerShell (recommended):\n"
        "     $env:OPENROUTER_API_KEY = \"sk-or-v1-...\"\n"
        "     py jev_demo.py\n\n"
        "  2. Run without arguments and type your key into the hidden prompt:\n"
        "     py jev_demo.py\n\n"
        "  3. Test offline without an API key using mock mode:\n"
        "     py jev_demo.py --mock\n\n"
        "Get an OpenRouter API key at: https://openrouter.ai/settings/keys\n"
        "Or TypeSafe API key at: https://console.typesafe.ai/"
    )


def main() -> None:
    args = parse_args()
    api_key = resolve_api_key(args.api_key, mock=args.mock)
    prov, endpoint, model = get_provider_config(
        api_key=api_key,
        provider=args.provider,
        model=args.model,
        endpoint=args.endpoint,
    )

    # If --json is requested, collect structured dicts
    json_output: dict[str, Any] = {
        "metadata": {
            "provider": prov,
            "endpoint": endpoint if not args.mock else "[OFFLINE MOCK]",
            "model": model,
            "mock": args.mock,
        },
        "reviews": [],
        "topics": [],
    }

    # Custom single review mode
    if args.review:
        res = analyze_review(
            api_key=api_key,
            review_text=args.review,
            product_name=args.product,
            mock=args.mock,
            provider=prov,
            model=model,
            endpoint=endpoint,
        )
        if args.json:
            print(json.dumps(res.to_dict(), indent=2))
            return
        section("CUSTOM CUSTOMER REVIEW ANALYSIS")
        print_review_result(res, 1)
        return

    # Custom single topic mode
    if args.topic:
        res = classify_topic(
            api_key=api_key,
            paragraph=args.topic,
            mock=args.mock,
            provider=prov,
            model=model,
            endpoint=endpoint,
        )
        if args.json:
            print(json.dumps(res.to_dict(), indent=2))
            return
        section("CUSTOM TOPIC CLASSIFICATION")
        print_topic_result(res, 1)
        return

    # Benchmark demo header
    if not args.json:
        print("\n" + "=" * 64)
        print("      Jev (TypeSafe System One) via OpenRouter - Demo App      ")
        print("=" * 64)
        print(f"  Provider : {prov.title()}")
        print(f"  Endpoint : {endpoint if not args.mock else '[OFFLINE MOCK]'}")
        print(f"  Model    : {model}")
        print(f"  API key  : {mask_key(api_key)}")

    # ----------------------------------------------------------------
    # Demo 1: Customer Review Analysis
    # ----------------------------------------------------------------
    if args.demo in ("reviews", "all"):
        if not args.json:
            section("DEMO 1 - Customer Review Analysis")
            print(
                "  Product: Wireless Earbuds Pro\n"
                "  Each review: 6 questions asked in ONE parallel Jev call.\n"
                "  Primitives used: Score (sentiment, quality), Noul (defect,\n"
                "  shipping, recommend), Choice (emotion tone).\n"
                "  Policy: composite score + confidence-gated action routing."
            )

        for i, (review_text, product_name) in enumerate(REVIEW_CASES, start=1):
            try:
                result = analyze_review(
                    api_key=api_key,
                    review_text=review_text,
                    product_name=product_name,
                    mock=args.mock,
                    provider=prov,
                    model=model,
                    endpoint=endpoint,
                )
                if args.json:
                    json_output["reviews"].append(result.to_dict())
                else:
                    print_review_result(result, i)
            except Exception as exc:
                if args.json:
                    json_output["reviews"].append({"error": str(exc), "review": review_text})
                else:
                    print(f"\n  Review #{i} - ERROR: {exc}")

    # ----------------------------------------------------------------
    # Demo 2: Topic Classification
    # ----------------------------------------------------------------
    if args.demo in ("topics", "all"):
        if not args.json:
            section("DEMO 2 - Topic Classification")
            print(
                "  Each paragraph: 4 questions asked in ONE parallel Jev call.\n"
                "  Primitives used: Choice (primary topic), Noul (opinion,\n"
                "  actionable), Score (technical depth).\n"
                "  Policy: confidence-gated routing + editorial/technical flags."
            )

        for i, paragraph in enumerate(TOPIC_CASES, start=1):
            try:
                result = classify_topic(
                    api_key=api_key,
                    paragraph=paragraph,
                    mock=args.mock,
                    provider=prov,
                    model=model,
                    endpoint=endpoint,
                )
                if args.json:
                    json_output["topics"].append(result.to_dict())
                else:
                    print_topic_result(result, i)
            except Exception as exc:
                if args.json:
                    json_output["topics"].append({"error": str(exc), "paragraph": paragraph})
                else:
                    print(f"\n  Paragraph #{i} - ERROR: {exc}")

    if args.json:
        print(json.dumps(json_output, indent=2))
    else:
        print(f"\n{DIVIDER}")
        print("  Done.")


if __name__ == "__main__":
    main()
