---
title: Pattern - Composite Scoring
tags:
  - jev
  - typesafe
  - pattern
aliases:
  - Composite Scoring
  - Multi-Dimension Scoring
---

# Pattern: Composite Scoring

> [!info] One-liner
> Break a complex judgment into **atomic [[Score]] questions** along independent dimensions. Combine with weights you control in code. Change weights — not questions — when priorities shift.

## Why Not One Big Score?

A single "how good is this?" score hides:
- Which dimension is failing?
- How do different dimensions trade off?
- How do you tune without rerunning the model?

Splitting into atomic dimensions makes each independently inspectable and adjustable.

## Structure

```python
response = client.system_one(
    state=ticket,
    questions={
        "bug_severity":    Score(
            instructions="How severe is this bug?",
            criteria=["No user impact", "Some users affected", "All users affected or data loss"]
        ),
        "customer_frustration": Score(
            instructions="How frustrated does the customer appear?",
            criteria=["Calm", "Concerned but civil", "Very angry"]
        ),
        "report_quality":  Score(
            instructions="How actionable is this bug report for an engineer?",
            criteria=["Vague, no reproduction steps", "Some detail", "Clear steps and context"]
        ),
    },
)

answers = response.answers

# Normalize each score to 0–1 range (levels: 0, 1, 2 → divide by 2)
priority = (
    0.5 * answers["bug_severity"].score         / 2
    + 0.3 * answers["customer_frustration"].score / 2
    + 0.2 * answers["report_quality"].score       / 2
)

if priority > 0.8:
    page_on_call(ticket)
elif priority > 0.5:
    schedule_next_sprint(ticket)
else:
    add_to_backlog(ticket)
```

## When to Use This Pattern

- Evaluating content quality along multiple dimensions
- Ranking items when priorities are tunable (change weights without rerunning)
- When the "combined score" shifts based on context (e.g. SLA tier changes weights)
- When you want to preserve individual dimension scores for display or debugging

## Key Properties

- **Questions run in parallel** — no latency penalty for asking more
- **Weights live in code** — change priorities without rerunning inference
- **Individual scores are preserved** — inspect any dimension for debugging or display
- **Labels are yours** — if you have labeled outcomes, use scores as features in a downstream ML model

## Preserving Individual Signals

```python
# Store both composite and individual for display
ticket_analysis = {
    "priority_score":     priority,
    "bug_severity":       answers["bug_severity"].score,
    "customer_frustration": answers["customer_frustration"].score,
    "report_quality":     answers["report_quality"].score,
}
```

## Training Downstream Models

If you have labeled outcomes (e.g. human-reviewed priority labels), use the raw Score probabilities as ML features rather than just the scalar score — they carry more information:

```python
features = {
    "severity_p0": answers["bug_severity"].probabilities[0],
    "severity_p1": answers["bug_severity"].probabilities[1],
    "severity_p2": answers["bug_severity"].probabilities[2],
    # ... same for other dimensions
}
```

## See Also

- [[Score]] — the Score primitive
- [[Composing Answers in Code]] — combining answers generally
- [[Pattern - Speculative Fan-Out]] — asking many Score questions in one call
