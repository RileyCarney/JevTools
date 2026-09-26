---
title: Choice
tags:
  - jev
  - typesafe
  - primitive
aliases:
  - Choice question
  - Choice primitive
---

# Choice

> [!info] One-liner
> **Choice** asks "which of these options?" and returns the selected option plus a probability distribution across all options.

## When to Use

- Answer is one of a **known, unordered set** of options
- Routing (ticket → department), classifying document type, detecting language
- You want to branch code on the winner

> [!tip] Add a fallback option
> Always add an `"other"` or `"none_of_the_above"` option when the list might not cover every input.

## What It Returns

| Field | Type | Description |
|---|---|---|
| `choice` | string | The selected option key |
| `probabilities` | dict | Probability for each option (sums to 1) |
| `confidence` | float 0–1 | How peaked the distribution is — see [[Confidence]] |

## Defining Options

Options are a `dict` mapping option key → description:

```python
from typesafe_sdk import Choice

Choice(
    instructions="Which team should handle this ticket?",
    criteria={
        "billing":   "Payment, subscription, or invoice issues.",
        "technical": "Bugs, API errors, or integration problems.",
        "sales":     "Pricing, upgrades, or new account questions.",
        "other":     "None of the above.",
    },
)
```

- Option **keys** are what the model returns in `choice`
- Option **values** (descriptions) clarify what belongs in that category
- Order within the dict does not imply ranking

## Structured Criteria (Advanced)

Use object descriptions for contrastive disambiguation:

```python
criteria={
    "disposable_card_limits": {
        "what":     "Quantity, transaction, or merchant restrictions",
        "not_for":  "Purpose, eligibility, or setup",
        "examples": ["How many disposable cards can I make per day?",
                     "Where can I use a disposable card?"],
    },
    "get_disposable_card": {
        "what":     "Purpose, eligibility, or setup",
        "not_for":  "Quantity, transaction, or merchant restrictions",
        "examples": ["How can I get a disposable virtual card?",
                     "What are disposable cards for?"],
    },
}
```

## Reading the Answer

```python
answer = response.answers["department"]
winner = answer.choice           # e.g. "billing"
prob   = answer.probabilities    # {"billing": 0.87, "technical": 0.09, "sales": 0.04}
conf   = answer.confidence       # e.g. 0.83
```

## Confidence Formula (3 options)

`confidence ≈ (3 × largest_probability − 1) / 2`

Higher when one option dominates; lower when probability spreads evenly.

## See Also

- [[Primitives Overview]] — choosing between Choice / Score / Noul
- [[Confidence]] — thresholding behavior on confidence
- [[Pattern - Intent Routing]] — routing architecture built on Choice
- [[Pattern - Confidence-Gated Routing]] — gating actions on confidence
