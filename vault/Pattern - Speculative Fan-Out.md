---
title: Pattern - Speculative Fan-Out
tags:
  - jev
  - typesafe
  - pattern
aliases:
  - Speculative Fan-Out
  - Fan-Out Pattern
---

# Pattern: Speculative Fan-Out

> [!info] One-liner
> Ask **all questions your code might need** in one request — including ones whose answers only matter for some inputs. Let code decide which answers to use.

## Why

Questions in a single request evaluate in **parallel**. Adding more questions barely changes response time and costs only a small number of extra tokens. Asking a question you might not need is close to free.

Benchmark: batching 13 questions into one call is **12.2× cheaper and 10.0× faster** than 13 separate calls, with no change in answers.

## How It Works

```python
response = client.system_one(
    state=ticket,
    questions={
        # Always-needed
        "department":   Choice(instructions="Which team handles this?", criteria={...}),
        "is_urgent":    Noul(instructions="Does the message convey urgency?"),
        # Speculative — only used if it's a bug report
        "bug_severity": Score(instructions="How severe is this bug?", criteria=[...]),
        # Speculative — only used if it's a billing issue
        "charge_type":  Choice(instructions="What kind of charge issue is this?", criteria={...}),
    },
)

# Code decides what's relevant
if response.answers["department"].choice == "technical":
    severity = response.answers["bug_severity"].score   # use it
    # charge_type answer is ignored
elif response.answers["department"].choice == "billing":
    charge = response.answers["charge_type"].choice     # use it
    # bug_severity answer is ignored
```

## State Each Speculative Premise Explicitly

When asking speculative questions, include the relevant premise in the question:

```python
# Don't: assume the model knows what "the bug" refers to
Noul(instructions="Is this a production outage?")

# Do: be explicit about what you're evaluating
Noul(instructions="If `ticket.message` describes a software bug, does it indicate production is currently down?")
```

## When to Break It Up (Make a Second Request)

A second request is warranted **only when**:
- An earlier answer is needed to **fetch new evidence** (e.g. retrieve top 3 documents, then judge them)
- An earlier answer is needed to **construct the state** (e.g. reassemble text blocks from merge decisions)
- An earlier answer determines the **next question options** (e.g. hierarchical classification)

Otherwise: ask everything in one request.

## Cost of Extra Questions

Extra questions still use tokens — measure actual budgets, cost, and end-to-end latency for your use case. The savings come from eliminating serial round trips, not from questions being free.

## See Also

- [[Primitives Overview]] — multi-question requests
- [[Pattern - Composite Scoring]] — using multiple Scores together
- [[How to Build with Jev]] — Step 6: ask a lot of questions
