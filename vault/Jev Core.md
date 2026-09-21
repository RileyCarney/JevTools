---
title: Jev Core
tags: [jev, typesafe, concept, primitive]
aliases: [System One, State, Choice, Score, Noul, Confidence, TypeSafe Primitives]
---

# Jev Core — System One, State, Primitives, Confidence

## System One Model

- **Jev** = TypeSafe's System One model. Input: text (string/JSON object/array). Output: typed decisions + probability distributions. No images/audio yet.
- ~100 ms/request. Calibrated probabilities via RLCD training (not overconfident).
- Endpoint: `POST /v1/systemone` — `model: "jev-latest"` (default)

**vs LLM:**

| | LLM | Jev (System One) |
|---|---|---|
| Output | Free-form text | Typed: choice / score / float |
| Control | Prompt → text → parse | Code owns flow; model fills judgment slots |
| Uncertainty | Overconfident | Calibrated probability distributions |
| Speed | 500 ms–s | ~100 ms |
| Use | Generate, reason, explain | Classify, rank, verify, route |

Key properties: **Structured** (schema-conformant), **Parallel** (questions evaluate simultaneously), **Comparable** (sortable outputs), **Self-consistent** (stable across repeated calls).

---

## State

**State** = the content Jev evaluates. Pass in `state` field alongside `questions`.

| Format | Use when | Example |
|---|---|---|
| `string` | Single text passage | `"Card charged twice."` |
| `object` | Named fields, related records ← **preferred** | `{"message": "...", "policy": "..."}` |
| `array` | Sequence of messages/records | `["Hi", "Charged twice"]` |

Rules:
- Include **only context relevant to current questions** — avoid context rot
- Supply current data from your own sources; don't rely on model weights
- All questions in one request see the **same state** and evaluate **independently**

**Reference nested fields** in instructions with backtick paths:
```
"Does `ticket.messages[0].text` request a refund?"
"Does `refund_policy` support `ticket.messages[0].text` given `order.charges`?"
```

---

## The Three Primitives

Every question has: **ID** (code-only key, never sent to model) · **type** · **instructions** · **criteria** (Choice/Score required; Noul optional).

### Choosing a Type

```
Answer is one of a fixed unordered set?    → Choice   (routing, classification)
Answer falls on a spectrum?                → Score    (severity, frustration, quality)
Clean yes/no where probability matters?    → Noul     (contains PII, requests refund)
```

> [!warning] Noul ≠ degree — Noul 0.5 = equal probability yes/no, NOT medium intensity. Use Score for degree.

---

### Choice

Picks one option from a defined set. Returns: `choice` (string key) · `probabilities` (dict) · `confidence` (0–1).

```python
from typesafe_sdk import Choice
Choice(
    instructions="Which team handles this ticket?",
    criteria={
        "billing":   "Payment, subscription, or invoice issues.",
        "technical": "Bugs, API errors, or integration problems.",
        "other":     "None of the above.",          # always include fallback
    },
)
# answer.choice → "billing"
# answer.probabilities → {"billing": 0.87, "technical": 0.09, "other": 0.04}
# answer.confidence → 0.83
```

**Structured criteria** (for contrastive disambiguation):
```python
criteria={
    "limits": {"what": "Quantity/transaction restrictions", "not_for": "Setup/eligibility",
               "examples": ["How many cards per day?"]},
    "setup":  {"what": "Purpose/eligibility/setup", "not_for": "Quantity/transaction restrictions",
               "examples": ["How do I get a card?"]},
}
```

---

### Score

Rates content along ordered descriptive levels. Returns: `score` (float, can fall between levels) · `legend` · `probabilities` (list) · `confidence` (0–1).

```python
from typesafe_sdk import Score
Score(
    instructions="How frustrated does the customer appear?",
    criteria=[
        "Calm — stating facts, no emotional language.",      # level 0
        "Concerned but civil — some frustration, polite.",   # level 1
        "Very angry — strong language, demanding action.",   # level 2
    ],
)
# answer.score → 1.4  (between level 1 and 2)
```

Levels must describe **concrete situations** and stand on their own. Vague levels ("low/medium/high") produce vague scores.

**Normalize to 0–1:** `normalized = answer.score / (num_levels - 1)`

---

### Noul

Returns the **probability** the answer is yes — a single float 0–1. No separate confidence field.

```python
from typesafe_sdk import Noul
Noul(instructions="Does the customer request a refund?")
# Optional criteria to clarify yes/no:
Noul(instructions="Is this a high-priority bug?",
     criteria={"yes": "Production down or data loss.", "no": "Degraded but not down."})
# answer.noul → 0.95  (strong yes)
# near 0.5 = uncertain; near 0 = strong no; near 1 = strong yes
```

**Use one Noul per independent label** (not Choice) when multiple conditions can apply simultaneously:
```python
questions={
    "has_pii":          Noul(instructions="Does `text` contain personally identifiable information?"),
    "requests_refund":  Noul(instructions="Does `text` request a refund?"),
    "is_urgent":        Noul(instructions="Does `text` express urgency?"),
}
```

---

## Confidence

Applies to **Choice** and **Score** only (Noul carries uncertainty in its own value).

- Derived from probability distribution shape: concentrated → high; spread → low
- Formula (3-option Choice): `confidence ≈ (3 × max_prob − 1) / 2`
- Range 0–1; raw `probabilities` always available if you want a custom measure

**Three behavioral tiers:**

| Range | Behavior |
|---|---|
| ≥ 0.8 (high) | Act automatically |
| 0.5–0.8 (medium) | Confirm / flag / gather more info |
| < 0.5 (low) | Route to human / escalate / do not act |

> [!warning] Calibrate thresholds on your own data. These numbers are starting points only.

**Risk-scaled thresholds** — raise the bar proportional to stakes:
```python
if confidence < 0.5:          route_to_human()
elif action == "check_balance": show_balance()          # low stakes → any conf ≥ 0.5
elif action == "approve_transfer":
    if confidence > 0.9:      confirm_then_execute()    # high stakes + high conf
    else:                     ask_user_to_confirm()     # high stakes + moderate conf
```

**Confidence does NOT mean:**
- Correctness guarantee
- Permission to act
- That all low-confidence answers are wrong (several acceptable alternatives spread probability)

## See Also
- [[Jev MOC]] · [[Jev Design]] · [[Jev Patterns]] · [[Jev SDK & API]]
- Docs: https://docs.typesafe.ai/concepts/system-one.md · /primitives.md · /confidence.md
