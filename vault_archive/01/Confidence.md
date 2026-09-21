---
title: Confidence
tags:
  - jev
  - typesafe
  - concept
---

# Confidence

> [!info] One-liner
> **Confidence** (0–1) summarizes how peaked the probability distribution is across options/levels. High confidence = clear winner. Low confidence = spread out = uncertain.

## Which Primitives Have It

| Primitive | Has `confidence`? |
|---|---|
| [[Choice]] | ✓ |
| [[Score]] | ✓ |
| [[Noul]] | ✗ — the `noul` value itself carries uncertainty |

## How It's Computed

Confidence is derived from the `probabilities` distribution returned in the answer.  
For a Choice with N options: `confidence ≈ (N × largest_probability − 1) / (N − 1)`

- All probability on one option → `1.0`
- Evenly spread → `0.0`

You always have access to the raw `probabilities` if you want to compute your own measure.

## Three Ranges for Behavior

```
High (e.g. > 0.8)   → Act automatically
Medium (0.5–0.8)    → Proceed with caution / ask for confirmation
Low (< 0.5)         → Do not act / route to human / request clarification
```

> [!warning] Thresholds depend on your domain and stakes
> The numbers above are starting points. Calibrate against your own data.

## Risk-Scaled Thresholds

Different actions should be gated at different confidence levels:

```python
action     = response.answers["action"]
confidence = action.confidence

if confidence < 0.5:
    route_to_human(user_message)           # genuinely unsure

elif action.choice == "check_balance":
    show_balance(account_id)               # low stakes — any confidence above 0.5 fine

elif action.choice == "approve_transfer":
    if confidence > 0.9:
        confirm_then_execute(account_id)   # high stakes, high confidence
    else:
        ask_user_to_confirm(account_id)    # high stakes, moderate confidence
```

## What Confidence Does NOT Mean

- It does **not** guarantee the answer is correct
- It does **not** represent overall workflow correctness
- It does **not** grant "permission to act" — that's your policy
- Low confidence on a [[Choice]] often means no option is clearly better, not that all are equally bad
- Several acceptable alternatives can spread probability; low confidence need not invalidate a harmless preference choice

## Confidence vs Noul

- [[Noul]] returns a raw probability (0–1) — near 0.5 = uncertain, near 0 or 1 = certain
- [[Choice]]/[[Score]] return `confidence` derived from their distribution — same intuition

## See Also

- [[Pattern - Confidence-Gated Routing]] — full architecture for routing on confidence
- [[Composing Answers in Code]] — using confidence in application logic
- [Confidence docs](https://docs.typesafe.ai/confidence.md)
