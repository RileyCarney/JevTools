---
title: How to Build with Jev
tags:
  - jev
  - typesafe
  - guide
aliases:
  - Build Guide
  - TypeSafe Design Workflow
---

# How to Build with Jev

> [!abstract] Core Philosophy
> Code owns the control flow. Jev handles **narrow, structured judgments** where code needs semantic understanding over unstructured data.

## Design Principle

Start from desired behavior, work backward to needed judgments:

1. **What will the app show, select, change, or hand off?**
2. **What judgments does code need to make that?**
3. **Keep known rules, calculations, exact lookups in code.** Add Jev only for semantic understanding.

## The Design Workflow (7 Steps)

### 1. Use Code When You Can
Keep deterministic work in code — reliable and cheap. Avoid agent `while` loops when a software workflow can express the same behavior.

```python
days_overdue = (today - invoice.due_date).days
if days_overdue > 30:
    route_to_collections(invoice)  # deterministic — no AI needed
```

### 2. Decompose the Input State
Include only context relevant to the current questions. See [[State]].
- Use JSON objects with descriptive field names
- Point questions at specific fields with backtick paths
- Don't pass in everything; avoid distractions and context rot

### 3. Use Structure in the State
Nest JSON for clarity. Reference fields in questions:

```
"Does `support.tickets[0].message` and `commerce.orders[0].charges` indicate a duplicate charge?"
```

### 4. Decompose the Questions

> [!important] Most Important Concept
> Ask the **most explicit, narrow, specific, atomic** questions you can. Break broad judgments into separate questions — each evaluating one property.

❌ Bad — one broad question hides multiple judgments:
```python
{"is_spam": Noul(instructions="Is `message` spam?")}
```

✓ Good — decomposed into inspectable signals:
```python
{
    "requests_credentials": Noul(instructions="Does `message.body` ask for a password?"),
    "offers_unexpected_reward": Noul(instructions="Does `message.body` claim an unexpected reward?"),
    "creates_time_pressure": Noul(instructions="Does `message` pressure the recipient to act quickly?"),
    "sender_identity_mismatch": Noul(instructions="Does the sender display_name conflict with the email domain?"),
    "link_domain_mismatch": Noul(instructions="Does the link url conflict with the sender organization?"),
}
```

### 5. Use Structure in the Questions
`instructions` and `criteria` can be objects/arrays when:
- Question needs inline context or code-sourced data
- Multiple options need contrastive what/not-for/examples definitions

```python
Noul(instructions={
    "potential_duplicate": {"name": "John Smith", "last_employer": "Google"},
    "question": "Is the resume for the same person as `potential_duplicate`?"
})
```

### 6. Ask a Lot of Questions
Ask many narrow independent questions per request. They run in parallel — adding more barely changes latency. See [[Pattern - Speculative Fan-Out]].

### 7. Combine Outputs in Code
Deterministically combine answers — weighted sums, thresholds, rules:

```python
quality = (
    0.4 * answers["answers_request"].noul
    + 0.4 * answers["citations_are_supported"].noul
    + 0.2 * (1 - answers["contradicts_context"].noul)
)
```

Or use answers as features in a downstream classical ML model.

### 8. Route on Uncertainty
Make code behave differently for confident vs unconfident answers. Escalate uncertain cases to a human or reasoning model. See [[Confidence]].

## Three Software Architectures

| Architecture | Description |
|---|---|
| Traditional | Complex decision trees from simple reliable primitives |
| LLM Agents | Model picks next step — hard to control, loops can go off-rails |
| **AI-Powered Software** ← Use This | Code owns control flow; Jev appears only for semantic judgments, each constrained and atomic |

## When to Make a Second Request

Make a second request **only when** the second set of questions requires an earlier answer to:
- Fetch more data (e.g. look up the top 3 skill candidates, then read their full text)
- Construct new state that didn't exist before (e.g. assembled text blocks)
- Determine the next question's options (e.g. hierarchical classification)

Otherwise: ask everything in one request and ignore unused answers.

## Testing

- Test representative cases and resulting application behavior
- For failures, inspect: exact state → questions → answers → composition → outcome
- Separate: missing evidence / model errors / code errors / service failures
- Cookbook thresholds and demo results are **examples to evaluate**, not universal rules

## See Also

- [[State]] — structuring input
- [[Question Design Rules]] — detailed question writing guide
- [[Primitives Overview]] — choosing question types
- [[Composing Answers in Code]] — combining answer signals
- [[Confidence]] — routing on uncertainty
