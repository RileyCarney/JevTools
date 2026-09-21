---
title: Noul
tags:
  - jev
  - typesafe
  - primitive
aliases:
  - Noul question
  - Noul primitive
---

# Noul

> [!info] One-liner
> **Noul** asks a yes/no question and returns the **probability** that the answer is yes — a single float from 0 to 1.

## When to Use

- Clean yes/no judgment where **the probability itself is the signal**
- Examples: "Does this message contain PII?", "Does the customer request a refund?", "Does the resume mention Python?"
- You want to `if` branch or threshold on the result
- Use **one Noul per label** when several labels may independently apply (vs. Choice which picks one)

> [!warning] Noul ≠ degree
> Noul 0.5 = model gives equal probability to yes and no — NOT medium intensity.
> For measuring degree, use [[Score]].

## What It Returns

| Field | Type | Description |
|---|---|---|
| `noul` | float 0–1 | Probability the answer is yes |

No separate `confidence` field. The noul value itself carries uncertainty — near 0.5 means uncertain, near 0 or 1 means confident.

## Definition

```python
from typesafe_sdk import Noul

Noul(instructions="Does the customer request a refund?")
```

Optional `criteria` to clarify what "yes" and "no" mean:

```python
Noul(
    instructions="Is this a high-priority bug?",
    criteria={
        "yes": "Production is down or data loss is occurring.",
        "no":  "Degraded performance or a feature is unavailable.",
    },
)
```

## Reading the Answer

```python
p = response.answers["refund_requested"].noul
# p near 1.0 → strong yes
# p near 0.0 → strong no
# p near 0.5 → uncertain

if p > 0.8:
    trigger_refund_flow()
elif p > 0.5:
    flag_for_human_review()
```

## Multiple Independent Labels

When several conditions may apply simultaneously, use one Noul per condition — not a Choice:

```python
questions={
    "requests_credentials": Noul(instructions="Does `message.body` ask for a password?"),
    "offers_reward":        Noul(instructions="Does `message.body` claim an unexpected reward?"),
    "creates_urgency":      Noul(instructions="Does `message` create time pressure?"),
    "sender_mismatch":      Noul(instructions="Does the sender display name conflict with the email domain?"),
}
```

Combine in code:
```python
spam_score = (
    0.3 * answers["requests_credentials"].noul
    + 0.3 * answers["offers_reward"].noul
    + 0.2 * answers["creates_urgency"].noul
    + 0.2 * answers["sender_mismatch"].noul
)
```

## See Also

- [[Primitives Overview]] — choosing between Choice / Score / Noul
- [[Score]] — use when measuring degree on a spectrum
- [[Composing Answers in Code]] — combining Noul values with weights
