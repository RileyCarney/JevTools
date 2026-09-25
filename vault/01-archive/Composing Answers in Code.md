---
title: Composing Answers in Code
tags:
  - jev
  - typesafe
  - guide
aliases:
  - Answer Composition
  - Combining Answers
---

# Composing Answers in Code

> [!info] One-liner
> Jev returns typed, constrained answers. Your code combines them with deterministic logic to make application decisions.

## Core Idea

Each answer is independent and typed. Code acts as the composer:

```python
answers = response.answers

# Weighted composition
quality = (
    0.4 * answers["answers_request"].noul
    + 0.4 * answers["citations_are_supported"].noul
    + 0.2 * (1 - answers["contradicts_context"].noul)
)

# Threshold decision
if quality > 0.75:
    send_to_user(response_text)
else:
    flag_for_review(response_text)
```

## Answer Types Reference

| Primitive | Access Pattern | Type |
|---|---|---|
| [[Noul]] | `response.answers["q"].noul` | float 0–1 |
| [[Choice]] | `response.answers["q"].choice` | string (option key) |
| [[Choice]] | `response.answers["q"].probabilities` | dict[str, float] |
| [[Choice]] | `response.answers["q"].confidence` | float 0–1 |
| [[Score]] | `response.answers["q"].score` | float |
| [[Score]] | `response.answers["q"].probabilities` | list[float] |
| [[Score]] | `response.answers["q"].confidence` | float 0–1 |

Python SDK also provides typed shorthand:
```python
response.nouls["billing"].noul
response.choices["tone"].choice
response.scores["urgency"].score
```

## Patterns for Composition

### Weighted Sum
```python
spam_score = (
    0.3 * answers["requests_credentials"].noul
    + 0.3 * answers["offers_reward"].noul
    + 0.2 * answers["creates_urgency"].noul
    + 0.2 * answers["sender_mismatch"].noul
)
```

### Normalize Score to 0–1
```python
# If Score has 3 levels (0, 1, 2)
normalized = answers["frustration"].score / 2
```

### Hard Rule + Weighted Score
```python
# Any hard violation blocks regardless of score
has_violation = answers["policy_violation"].noul > 0.9

if has_violation:
    block()
else:
    overall = 0.6 * answers["relevance"].score + 0.4 * answers["quality"].score
    act_on(overall)
```

### Threshold on Confidence + Choice
```python
answer = response.answers["card_topic"]
if answer.confidence < 0.5:
    route_to_human()
else:
    handle_topic(answer.choice)
```

### Ignore Irrelevant Speculative Answers
```python
# Speculative questions — only use what's needed
if answers["is_bug_report"].noul > 0.7:
    severity = answers["bug_severity"].score   # only relevant if it's a bug report
```

## Using Probabilities as ML Features

Raw probabilities can feed into a downstream classical ML model:

```python
features = {
    "billing_prob":    answers["billing"].noul,
    "frustration":     answers["frustration"].score / 2,
    "urgency_high_p":  answers["urgency"].probabilities[2],  # probability of highest level
}
# Pass features to CatBoost, XGBoost, sklearn, etc.
```

## What Code Should NOT Do

- Don't re-parse generated prose — Jev returns typed values only
- Don't infer from the question ID — always use the answer fields
- Don't confuse confidence with correctness — it's a certainty signal, not a guarantee
- Don't bake policy into questions — keep thresholds and weights in code

## See Also

- [[Confidence]] — routing logic based on confidence
- [[Pattern - Composite Scoring]] — full composite scoring architecture
- [[Pattern - Speculative Fan-Out]] — asking speculative questions efficiently
- [[Pattern - Confidence-Gated Routing]] — confidence-based escalation
