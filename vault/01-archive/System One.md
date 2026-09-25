---
title: System One
tags:
  - jev
  - typesafe
  - concept
aliases:
  - System One model
---

# System One

> [!info] One-liner
> System One models make **fast, structured decisions** for software. Jev is TypeSafe's flagship System One model.

## What It Is

- Accepts text input (strings, JSON objects, arrays — no images/audio yet)
- Returns **typed answers + probability distributions**, not generated text
- Trained for **calibrated decisions** — probabilities reflect genuine uncertainty
- ~100 ms per request; fast enough for real-time paths

## How It Differs from an LLM

| | LLM | System One (Jev) |
|---|---|---|
| Output | Free-form text | Typed choice / score / probability |
| Control | Prompt → text → parse | Code owns workflow; model fills judgment slots |
| Uncertainty | Often overconfident | Calibrated probabilities (RLCD training) |
| Speed | Hundreds of ms–seconds | ~100 ms |
| Use case | Generate, reason, explain | Classify, rank, verify, route |

## The Name

Named after Daniel Kahneman's *System 1* thinking — fast and intuitive, vs. System 2 (slow, deliberate). Emphasis on **fast, focused judgments**.

## Three Primitives

| Primitive | Question shape | Example output |
|---|---|---|
| [[Choice]] | Which of these options? | `"billing"` |
| [[Score]] | Which level on this scale? | `1.4` |
| [[Noul]] | Is this true? (probability) | `0.95` |

## Call It

- `POST /v1/systemone` — [[HTTP API]]
- Python: `client.system_one(state=..., questions={...})` — [[Python SDK]]
- JS/TS: `client.systemOne({state, questions})` — [[JavaScript SDK]]
- `model` field: use `jev-latest` (SDK default); see [Models](https://docs.typesafe.ai/models.md)

## Key Properties

- **Structured** — outputs conform to your schema; never recovers a value from prose
- **Parallel** — all questions in a request evaluate independently and simultaneously
- **Comparable** — outputs are sortable; drive thresholds and comparisons
- **Self-consistent** — stable answers across repeated evaluations

## See Also

- [[State]] — how to prepare input
- [[Primitives Overview]] — how to design questions
- [[Confidence]] — how uncertainty is surfaced
- [[How to Build with Jev]] — workflow design guide
