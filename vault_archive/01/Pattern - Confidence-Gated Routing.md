---
title: Pattern - Confidence-Gated Routing
tags:
  - jev
  - typesafe
  - pattern
aliases:
  - Confidence-Gated Routing
  - Confidence Routing
---

# Pattern: Confidence-Gated Routing

> [!info] One-liner
> Use **confidence as a second decision axis**. The answer tells you *what*; confidence tells you *whether to act*.

## Core Idea

Every [[Choice]] and [[Score]] answer returns a `confidence` value (0–1). Use it to decide:
- **High confidence** → act automatically
- **Medium confidence** → proceed with caution, confirm, or flag
- **Low confidence** → route to human / escalate / request clarification

The answer and confidence are independent axes — you can route differently depending on **both**.

## Example: Risk-Scaled Banking Action

```python
response = client.system_one(
    state=user_message,
    questions={
        "action": Choice(
            instructions="What is the user trying to do?",
            criteria={
                "check_balance":   "View account balance",
                "approve_transfer": "Approve the pending withdrawal request",
                "support":         "Get help with an issue",
            },
        ),
    },
)

action     = response.answers["action"]
confidence = action.confidence

if confidence < 0.5:
    route_to_human(user_message)       # model is genuinely unsure

elif action.choice == "check_balance":
    show_balance(account_id)           # low stakes: any confidence ≥ 0.5 is fine

elif action.choice == "approve_transfer":
    if confidence > 0.9:
        confirm_then_execute(account_id)   # high stakes + high confidence
    else:
        ask_user_to_confirm(account_id)    # high stakes + moderate confidence
```

## Threshold Design Principles

- **Floor** (e.g. 0.5): catches anything genuinely uncertain — route all of these to humans
- **Action-specific thresholds**: raise the bar proportionally to stakes
  - Read-only / recoverable → low threshold fine
  - Destructive / irreversible → require high threshold
- **Domain-dependent**: calibrate against your own data, not cookbook examples

## Three-Tier Structure

```
Confidence ≥ HIGH_THRESH   → Automatic action
Confidence between LOW–HIGH → Confirm / flag / review
Confidence < LOW_THRESH    → Human escalation
```

Each action type gets its own `HIGH_THRESH` based on consequences.

## What Confidence Is NOT

- Not an overall correctness guarantee
- Not permission to act
- Low confidence on a harmless preference choice need not block it
- Several acceptable alternatives can spread probability; that is not the same as the model being wrong

## See Also

- [[Confidence]] — how confidence is computed and what it means
- [[Pattern - Intent Routing]] — routing architecture built on Choice answers
- [[Pattern - Speculative Fan-Out]] — combining with fan-out for efficient requests
