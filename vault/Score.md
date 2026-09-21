---
title: Score
tags:
  - jev
  - typesafe
  - primitive
aliases:
  - Score question
  - Score primitive
---

# Score

> [!info] One-liner
> **Score** asks "which level on this scale?" and returns a floating-point position along ordered, descriptive levels — plus a probability distribution across levels.

## When to Use

- Answer falls on a **spectrum** and you can describe each point
- Examples: bug severity, customer frustration, skill level, content quality
- You want to **rank** items: give the same Score question to multiple items and sort by `score`
- You want **graded thresholds** instead of a binary

> [!warning] Score ≠ Noul for degree
> Don't use Noul to measure degree. A Noul of 0.5 means equal probability of yes/no, not medium intensity. Define concrete levels with Score instead.

## What It Returns

| Field | Type | Description |
|---|---|---|
| `score` | float | Position along levels (can fall between two) |
| `legend` | list | Your levels repeated by number |
| `probabilities` | list | Probability assigned to each level |
| `confidence` | float 0–1 | How peaked the distribution is — see [[Confidence]] |

## Defining Levels

Levels are an **ordered list** from low to high. Each must describe a **concrete situation** and stand on its own.

```python
from typesafe_sdk import Score

Score(
    instructions="How frustrated does the customer appear?",
    criteria=[
        "Calm and neutral — stating facts without emotional language.",   # level 0
        "Concerned but civil — some frustration, polite tone.",           # level 1
        "Very angry or using strong language, demanding resolution.",     # level 2
    ],
)
```

Score returns a float like `1.4` — between "Concerned" and "Very angry".

## Structured Level Descriptions (Advanced)

Each level can be an object:

```python
criteria=[
    {"description": "Calm", "examples": ["I have a question about my bill."]},
    {"description": "Frustrated", "examples": ["This has been going on for a week."]},
    {"description": "Very angry", "examples": ["This is completely unacceptable!"]},
]
```

## Reading the Answer

```python
answer = response.answers["frustration"]
level  = answer.score           # e.g. 1.4
legend = answer.legend          # ["Calm...", "Concerned...", "Very angry..."]
probs  = answer.probabilities   # [0.05, 0.45, 0.50]
conf   = answer.confidence      # e.g. 0.55
```

## Composite Scoring Pattern

Split a complex judgment into multiple Score questions, then weight them in code:

```python
answers = response.answers
priority = (
    0.5 * answers["bug_severity"].score / 2      # normalize to 0–1
    + 0.3 * answers["customer_frustration"].score / 2
    + 0.2 * answers["report_quality"].score / 2
)
```

See [[Pattern - Composite Scoring]] for the full pattern.

## See Also

- [[Primitives Overview]] — choosing between Choice / Score / Noul
- [[Confidence]] — thresholding on the returned confidence
- [[Pattern - Composite Scoring]] — combining multiple Scores
- [[Composing Answers in Code]] — weighting and normalization
