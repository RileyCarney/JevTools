---
title: Jev Design
tags: [jev, typesafe, guide, design]
aliases: [Build Guide, Question Design, TypeSafe Design Workflow, Composing Answers]
---

# Jev Design — Build Workflow, Question Rules, Answer Composition

## Core Philosophy

Code owns control flow. Jev fills **narrow semantic judgment slots** where ordinary code needs language understanding. Never agent loops — this is AI-powered software, not an agent.

**Summary:**
- Keep deterministic rules, calculations, exact lookups in code
- Break broad judgments into narrow typed questions
- Give each question only the context it needs
- Ask independent questions together (parallel)
- Combine answers with weights/thresholds in code
- Use confidence to act, flag, or escalate

---

## Design Workflow

### 1 — Use Code When You Can
Keep deterministic work in code. Avoid AI where a rule suffices:
```python
if (today - invoice.due_date).days > 30:
    route_to_collections(invoice)   # no AI needed
```

### 2 — Decompose State
Include only relevant context. Use JSON objects with descriptive field names. Reference fields in questions via backtick paths. See [[Jev Core#State]].

### 3 — Decompose Questions (Most Important)

> [!important] Ask the most explicit, narrow, specific, atomic questions possible. One question = one property.

❌ **Broad (bad)** — hides multiple signals:
```python
{"is_spam": Noul(instructions="Is `message` spam?")}
```

✓ **Decomposed (good)** — each signal inspectable and tunable:
```python
{
    "requests_credentials":   Noul(instructions="Does `message.body` ask for a password?"),
    "offers_unexpected_reward": Noul(instructions="Does `message.body` claim an unexpected reward?"),
    "creates_time_pressure":  Noul(instructions="Does `message` pressure the recipient to act quickly?"),
    "sender_identity_mismatch": Noul(instructions="Does `message.sender.display_name` conflict with the domain in `message.sender.email`?"),
    "link_domain_mismatch":   Noul(instructions="Does `message.links[0].url` conflict with `message.sender.display_name`?"),
}
```

### 4 — Use Structure in Questions
`instructions` and `criteria` can be objects/arrays when:
- Question needs inline code-sourced data
- Options need contrastive what/not-for/examples definitions

```python
# Code-sourced context as structured instructions
Noul(instructions={
    "candidate_record": {"name": "Jane Doe", "last_employer": "Stripe"},
    "question": "Is the resume for the same person as `candidate_record`?"
})
```

### 5 — Ask Many Questions Per Request
Questions run in parallel. Adding more barely changes latency. Ask everything you might need + speculative questions. See [[Jev Patterns#Speculative Fan-Out]].

### 6 — Combine in Code
Compose answers with weighted sums, thresholds, rules. Keep policy in code — not in the questions.

### 7 — Route on Uncertainty
Gate actions on confidence. Escalate to human or reasoning model when uncertain. See [[Jev Core#Confidence]].

### 8 — When to Make a Second Request
**Only** when the second questions require an earlier answer to:
- Fetch more data (e.g. top-3 candidates → fetch full text → judge again)
- Construct new state (e.g. merged text blocks that didn't exist before)
- Determine the next options (e.g. hierarchical classification)

Otherwise: ask everything in one request, ignore unused answers.

---

## Question Design Rules

| # | Rule | Anti-pattern |
|---|---|---|
| 1 | **One narrow judgment per question** | "Is this spam?" hides 5+ signals |
| 2 | **Write full meaning in `instructions`** — ID never sent to model | `Noul(instructions="Does this apply?")` — vague |
| 3 | **Give enough state** — source text, relationships, policies, facts | Missing context → wrong judgment |
| 4 | **Define criteria precisely** — concrete situations, not vague labels | Levels: "low/medium/high" → vague scores |
| 5 | **Include a no-match option** in Choice criteria | `"other": "None of the above"` |
| 6 | **Ask for fast judgments** — 1-second knowledgeable human decision | "Analyze and determine best action" = slow reasoning → decompose |
| 7 | **Use structure** when strings blur together | Long string template with embedded DB value |
| 8 | **Select don't generate** — regex finds candidates, Jev picks | Never ask Jev to generate extracted value |
| 9 | **Keep policy in code** — thresholds, weights, routing rules | Baked-in threshold → can't change without rerunning |
| 10 | **Check candidate coverage** — model can't pick what's missing | Missing option in Choice criteria |

**Score level rule:** Each level must describe a concrete situation and stand on its own.
```python
# Bad:
criteria=["low", "medium", "high"]
# Good:
criteria=[
    "Production working normally — no user impact.",
    "Feature degraded — some users affected.",
    "Production down — all users affected or data loss.",
]
```

---

## Composing Answers in Code

### Answer Access Patterns

| Primitive | Field | Type |
|---|---|---|
| Noul | `response.answers["q"].noul` | float 0–1 |
| Choice | `response.answers["q"].choice` | string (key) |
| Choice | `response.answers["q"].probabilities` | dict[str, float] |
| Choice/Score | `response.answers["q"].confidence` | float 0–1 |
| Score | `response.answers["q"].score` | float |
| Score | `response.answers["q"].probabilities` | list[float] |

Python shorthand: `response.nouls["q"].noul` · `response.choices["q"].choice` · `response.scores["q"].score`

### Composition Patterns

**Weighted sum:**
```python
quality = (
    0.4 * answers["answers_request"].noul
    + 0.4 * answers["citations_are_supported"].noul
    + 0.2 * (1 - answers["contradicts_context"].noul)
)
```

**Hard rule + weighted score:**
```python
if answers["policy_violation"].noul > 0.9:
    block()
else:
    score = 0.6 * answers["relevance"].score + 0.4 * answers["quality"].score
    act_on(score)
```

**Ignore speculative answers not needed:**
```python
if answers["is_bug"].noul > 0.7:
    severity = answers["bug_severity"].score   # only relevant for bugs
```

**Raw probabilities as ML features:**
```python
features = {
    "billing_p":   answers["billing"].noul,
    "urgency_p2":  answers["urgency"].probabilities[2],  # highest level prob
    "frustration": answers["frustration"].score / 2,     # normalized
}
# → feed into CatBoost, XGBoost, sklearn, etc.
```

### Rules for Code
- Never re-parse prose — Jev returns typed values
- Never use the question ID as a proxy for meaning — read the answer fields
- Confidence ≠ correctness guarantee
- Policy (thresholds, weights, routing) lives in code, not in questions

## See Also
- [[Jev MOC]] · [[Jev Core]] · [[Jev Patterns]] · [[Jev SDK & API]]
- Docs: https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md
