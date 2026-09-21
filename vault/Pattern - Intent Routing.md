---
title: Pattern - Intent Routing
tags:
  - jev
  - typesafe
  - pattern
aliases:
  - Intent Routing
  - Intent Classification Routing
---

# Pattern: Intent Routing

> [!info] One-liner
> Use a [[Choice]] question to classify incoming user intent, then route to the optimal handler — deterministic logic, a specialist LLM, or a human.

## Why

Incoming requests vary: some need code, some need AI, some need a human. Routing them correctly makes each downstream handler simpler and more reliable than a single general handler.

## Structure

```python
response = client.system_one(
    state=user_message,
    questions={
        "intent": Choice(
            instructions="What does the user want to do?",
            criteria={
                "check_status":    "User wants to know the current status of their order or account.",
                "make_change":     "User wants to update, cancel, or modify something.",
                "get_help":        "User wants explanation or guidance.",
                "report_problem":  "User is reporting a bug or unexpected behavior.",
                "other":           "None of the above — route to general support.",
            },
        ),
    },
)

intent     = response.answers["intent"].choice
confidence = response.answers["intent"].confidence

# Confidence gate first
if confidence < 0.5:
    route_to_human(user_message)
else:
    match intent:
        case "check_status":
            show_status(user)           # deterministic lookup
        case "make_change":
            open_change_flow(user)      # structured workflow
        case "get_help":
            run_llm_answer(user_message)  # specialist LLM
        case "report_problem":
            create_bug_report(user_message)
        case _:
            route_to_human(user_message)
```

## Combining with Speculative Questions

Ask branch-specific questions up front in the same request, then consume only the relevant answers:

```python
response = client.system_one(
    state=user_message,
    questions={
        "intent":         Choice(instructions="What does the user want?", criteria={...}),
        # Speculative — only used if intent is "make_change"
        "change_type":    Choice(instructions="What kind of change is being requested?", criteria={...}),
        # Speculative — only used if intent is "report_problem"
        "problem_area":   Choice(instructions="What area of the product is affected?", criteria={...}),
    },
)

if response.answers["intent"].choice == "make_change":
    change = response.answers["change_type"].choice  # use it
elif response.answers["intent"].choice == "report_problem":
    area = response.answers["problem_area"].choice   # use it
```

## Function Calling Variant

Use Choice to select a function name and Noul/Choice for its typed arguments:

```python
questions={
    "function":     Choice(instructions="Which function handles this request?", criteria={"get_price": ..., "place_order": ..., "cancel": ...}),
    "symbol":       Choice(instructions="Which trading symbol is mentioned?", criteria={"AAPL": ..., "TSLA": ..., "other": ...}),
    "is_limit_order": Noul(instructions="Does the request specify a limit price?"),
}
```

## See Also

- [[Choice]] — the Choice primitive
- [[Confidence]] — gating on confidence before routing
- [[Pattern - Confidence-Gated Routing]] — full confidence-based escalation
- [[Pattern - Speculative Fan-Out]] — combining intent routing with speculative branch questions
