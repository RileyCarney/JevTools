---
title: State
tags:
  - jev
  - typesafe
  - concept
---

# State

> [!info] One-liner
> **State** is the content you send Jev to evaluate — everything the model needs to answer your questions.

## Formats

Pass `state` as:

| Format | When to use | Example |
|---|---|---|
| `string` | Single piece of text | `"My card was charged twice."` |
| `object` (JSON) | Named fields, related records (preferred) | `{"message": "...", "policy": "..."}` |
| `array` | Sequence of messages / records | `["Hi", "I was charged twice"]` |

> [!tip] Default to objects
> Use a JSON object for most requests. Named fields make relationships explicit and let questions reference specific parts with backtick paths.

## Structuring State

- Include **only the context relevant** to the current questions — avoid distractions and context rot
- Don't rely on model weight knowledge; supply current data from your own sources
- Group related information together even if it comes from multiple tables (ticket + order + policy in one object)

```json
{
  "ticket": {
    "subject": "Duplicate charge",
    "messages": [
      {"from": "customer", "text": "I was charged twice for order A-104. Please refund."},
      {"from": "support",  "text": "We are checking the charges."}
    ]
  },
  "order": {
    "id": "A-104",
    "charges": [
      {"amount_usd": 49, "status": "captured"},
      {"amount_usd": 49, "status": "captured"}
    ]
  },
  "refund_policy": "Duplicate charges are eligible for a refund."
}
```

## Referencing Fields in Questions

Point questions at specific fields with backtick dot-and-index paths:

```
"Does `ticket.messages[0].text` request a refund?"
"Does `refund_policy` support the request in `ticket.messages[0].text`, given `order.charges`?"
```

## Limitations

- Text only — no images, audio, or video (yet)
- Primary training language is English; other languages accepted but lower accuracy

## All Questions See the Same State

Every question in a single request sees identical state and is evaluated **independently** — one question's answer is not hidden context for another.

## See Also

- [[Primitives Overview]] — designing questions against state
- [[How to Build with Jev]] — workflow design, including state decomposition
- [[HTTP API]] — `state` field in the request schema
