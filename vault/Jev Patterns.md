---
title: Jev Patterns
tags: [jev, typesafe, pattern, use-case]
aliases: [Speculative Fan-Out, Confidence Routing, Composite Scoring, Intent Routing, Use Cases, TypeSafe Patterns]
---

# Jev Patterns — Architectural Patterns & Use-Cases

## Speculative Fan-Out

> [!info] Send all questions your code might need in one request. Let code decide which answers to use.

Questions evaluate **in parallel**. Adding more barely changes latency. Batching 13 questions into one call = **12.2× cheaper, 10× faster** vs 13 separate calls.

```python
response = client.system_one(
    state=ticket,
    questions={
        "department":   Choice(instructions="Which team handles this?", criteria={...}),
        "is_urgent":    Noul(instructions="Does this convey urgency?"),
        # Speculative — only consumed if it's a bug
        "bug_severity": Score(instructions="How severe is the bug?", criteria=[...]),
        # Speculative — only consumed if it's a billing issue
        "charge_type":  Choice(instructions="What kind of charge issue?", criteria={...}),
    },
)

if response.answers["department"].choice == "technical":
    severity = response.answers["bug_severity"].score   # use it; ignore charge_type
elif response.answers["department"].choice == "billing":
    charge = response.answers["charge_type"].choice     # use it; ignore bug_severity
```

**State speculative premises explicitly:**
```python
# Don't: "Is this a production outage?" (ambiguous what "this" is)
# Do:
Noul(instructions="If `ticket.message` describes a software bug, does it indicate production is currently down?")
```

**When a second request IS warranted** (exception, not rule):
- Need earlier answer to **fetch new evidence** (retrieve top-3 docs → judge again)
- Need earlier answer to **construct new state** (merged text blocks)
- Earlier answer determines the **next question's options** (hierarchical classification)

---

## Confidence-Gated Routing

> [!info] Confidence tells you *whether* to act. The answer tells you *what* to do.

```python
action     = response.answers["action"]
confidence = action.confidence

if confidence < 0.5:
    route_to_human()                    # genuinely unsure → don't guess

elif action.choice == "check_balance":
    show_balance()                      # low stakes: any conf ≥ 0.5 fine

elif action.choice == "approve_transfer":
    if confidence > 0.9:
        confirm_then_execute()          # high stakes + high conf
    else:
        ask_user_to_confirm()           # high stakes + moderate conf
```

**Three-tier structure:**
```
conf ≥ HIGH    → act automatically
LOW ≤ conf < HIGH → confirm / flag / review
conf < LOW     → human escalation / do not act
```

Each action type gets its own threshold based on consequence of being wrong.

> [!warning] Calibrate thresholds on your own data. Several acceptable alternatives spread probability — low confidence ≠ wrong answer.

---

## Composite Scoring

> [!info] Split a complex judgment into atomic Score questions. Combine with weights in code. Change weights — not questions — when priorities shift.

```python
response = client.system_one(
    state=ticket,
    questions={
        "bug_severity":   Score(instructions="How severe is this bug?",
                                criteria=["No user impact", "Some users affected", "All users / data loss"]),
        "frustration":    Score(instructions="How frustrated does the customer appear?",
                                criteria=["Calm", "Concerned but civil", "Very angry"]),
        "report_quality": Score(instructions="How actionable is this bug report?",
                                criteria=["Vague", "Some detail", "Clear steps and context"]),
    },
)

a = response.answers
priority = (
    0.5 * a["bug_severity"].score   / 2   # normalize 0–1
    + 0.3 * a["frustration"].score  / 2
    + 0.2 * a["report_quality"].score / 2
)

if priority > 0.8:   page_on_call(ticket)
elif priority > 0.5: schedule_sprint(ticket)
else:                backlog(ticket)
```

**Key benefits:**
- Questions run in parallel — no latency penalty for more
- Weights live in code — change without rerunning inference
- Individual scores preserved for display/debugging
- Raw probabilities usable as ML features in downstream CatBoost/XGBoost

**Storing both composite and dimensions:**
```python
result = {
    "priority": priority,
    "bug_severity": a["bug_severity"].score,
    "frustration":  a["frustration"].score,
    "report_quality": a["report_quality"].score,
}
```

---

## Intent Routing

> [!info] Use Choice to classify user intent, then route to the optimal handler — deterministic code, specialist LLM, or human.

```python
response = client.system_one(
    state=user_message,
    questions={
        "intent": Choice(
            instructions="What does the user want to do?",
            criteria={
                "check_status":   "User wants status of order or account.",
                "make_change":    "User wants to update, cancel, or modify something.",
                "get_help":       "User wants explanation or guidance.",
                "report_problem": "User reports a bug or unexpected behavior.",
                "other":          "None of the above.",
            },
        ),
    },
)

intent     = response.answers["intent"].choice
confidence = response.answers["intent"].confidence

if confidence < 0.5:
    route_to_human(user_message)
else:
    match intent:
        case "check_status":    show_status(user)
        case "make_change":     open_change_flow(user)
        case "get_help":        run_llm_answer(user_message)
        case "report_problem":  create_bug_report(user_message)
        case _:                 route_to_human(user_message)
```

**Combine with Speculative Fan-Out** — ask branch-specific questions in the same call:
```python
questions={
    "intent":      Choice(instructions="What does the user want?", criteria={...}),
    "change_type": Choice(instructions="What kind of change?", criteria={...}),   # speculative
    "problem_area": Choice(instructions="Which area is affected?", criteria={...}), # speculative
}
# consume only the relevant speculative answer in code
```

**Function calling variant** — select function + fill typed args:
```python
questions={
    "function":       Choice(instructions="Which function handles this?",
                             criteria={"get_price": ..., "place_order": ..., "cancel": ...}),
    "symbol":         Choice(instructions="Which trading symbol?",
                             criteria={"AAPL": ..., "TSLA": ..., "other": ...}),
    "is_limit_order": Noul(instructions="Does the request specify a limit price?"),
}
```

---

## Use-Case Map

### Routing & Classification
| Use Case | Primitive |
|---|---|
| Ticket → department | Choice on ticket text |
| Intent detection | Choice on user message |
| Document type | Choice on content |
| Language detection | Choice on text |

### Ranking & Reranking
| Use Case | Primitive |
|---|---|
| RAG passage reranking | Score each passage for relevance |
| Support ticket priority | Composite Scoring (severity + frustration + quality) |
| Resume shortlisting | Multiple Score dimensions |
| Search reranking | Score or Choice selecting best candidate |

### Verification & Extraction
| Use Case | Primitive |
|---|---|
| Citation verification | Choice: does quote context support claim? |
| Structured data extraction | Regex → candidates → Choice selects correct span |
| Date extraction | Choice for parts; code resolves |
| Duplicate detection | Noul per candidate |

### Moderation & Guardrails
| Use Case | Primitive |
|---|---|
| LLM input/output screening | Noul per hazard type |
| Spam detection | Multiple Noul signals, weighted in code |
| Policy violation | Noul against specific rules |
| Harm severity | Score on harm level |

### Data & ML
| Use Case | Primitive |
|---|---|
| ML feature discovery | Score/Noul outputs as labeled features |
| Entity alignment | Score with merge/leave/review levels |
| Hierarchical classification | Sequential Choice requests, narrowing options |
| Self-consistency check | Multiple calls → compare label agreement |

### Pattern → Use-Case Matching
| Need | Pattern |
|---|---|
| Route based on intent | Intent Routing |
| Ask many questions cheaply | Speculative Fan-Out |
| Gate actions on certainty | Confidence-Gated Routing |
| Multi-dimension quality score | Composite Scoring |

## See Also
- [[Jev MOC]] · [[Jev Core]] · [[Jev Design]] · [[Jev SDK & API]]
- Docs: https://docs.typesafe.ai/patterns.md · /concepts/use-case-map.md
