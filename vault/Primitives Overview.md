---
title: Primitives Overview
tags:
  - jev
  - typesafe
  - concept
aliases:
  - Questions
  - TypeSafe Primitives
---

# Primitives (Questions)

> [!info] One-liner
> TypeSafe primitives are typed question-answer pairs. A **question** defines one judgment; its **answer** is the typed value your code consumes.

## The Three Types

| Type | What it answers | Returns |
|---|---|---|
| [[Choice]] | Which of these options? | `choice`, `probabilities`, `confidence` |
| [[Score]] | Which level on this scale? | `score`, `legend`, `probabilities`, `confidence` |
| [[Noul]] | Is this statement true? | `noul` (0–1 float, no separate confidence) |

## Choosing a Type

```
One of a fixed, unordered set?     → Choice
  (routing a ticket, classifying a doc type)

Position on a spectrum?            → Score
  (bug severity, frustration, skill level)

Clean yes/no with probability?     → Noul
  (contains PII, requests refund, mentions Python)
```

> [!warning] Noul vs Score confusion
> A Noul of 0.5 = equally likely yes or no — NOT a medium intensity.
> Use a **Score** with defined levels when you want to measure degree.
> Use a **Noul** only when the question is genuinely binary.

## Anatomy of a Question

Every question has:

| Field | Required | Description |
|---|---|---|
| ID (dict key) | ✓ | Code label only — never sent to model. Put full meaning in `instructions`. |
| `type` | ✓ | `"choice"`, `"score"`, or `"noul"` |
| `instructions` | ✓ | The actual question / judgment to make. String, object, or array. |
| `criteria` | Choice/Score ✓ | Options (Choice) or ordered levels (Score). Optional clarifier for Noul. |

## Reference State Fields in Instructions

Use backtick dot-and-index paths:
```
"Does `ticket.messages[0].text` request a refund?"
"Does `refund_policy` support the request in `ticket.messages[0].text`?"
```

## Asking Multiple Questions

- Send all questions sharing the same state **in one request**
- Questions evaluate **in parallel** — adding more barely changes latency
- Mix types freely in the same request
- Ask speculative questions you might not need → [[Pattern - Speculative Fan-Out]]

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"message": "My flight was cancelled. Can I get a refund?",
               "refund_policy": "Cancelled flights are eligible for a full refund."},
        questions={
            "refund_requested": Noul(
                instructions="Does `message` request a refund?"
            ),
            "request_type": Choice(
                instructions="What is the main request in `message`?",
                criteria={
                    "refund":      "The customer wants money returned.",
                    "rebooking":   "The customer wants a replacement flight.",
                    "information": "The customer is asking for information only.",
                },
            ),
            "frustration": Score(
                instructions="How frustrated does the customer appear in `message`?",
                criteria=["Calm and neutral.", "Concerned but civil.", "Very angry or strong language."],
            ),
        },
    )

print(response.answers["refund_requested"].noul)
print(response.answers["request_type"].choice)
print(response.answers["frustration"].score)
```

## When to Make a Second Request

Make a **second request** only when the second question requires an earlier answer to:
- Fetch more data for the state
- Construct new state that didn't exist yet
- Determine what the next options are

Otherwise ask everything in one request and ignore unused answers in code.

## Advanced: Structured Instructions/Criteria

`instructions` and `criteria` can be objects/arrays instead of strings when:
- The question needs inline context or examples
- Part of the question comes from your database (put that data in a separate field)
- Several options need contrastive what/not-for/examples definitions

See [[Question Design Rules]] for the full guide.

## See Also

- [[Choice]], [[Score]], [[Noul]] — individual primitive pages
- [[Confidence]] — how to use returned confidence values
- [[Composing Answers in Code]] — combining multiple answers
- [[Pattern - Speculative Fan-Out]] — batching questions efficiently
