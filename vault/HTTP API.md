---
title: HTTP API
tags:
  - jev
  - typesafe
  - api
aliases:
  - TypeSafe REST API
  - POST systemone
---

# HTTP API

> [!info] Endpoint
> `POST https://api.typesafe.ai/v1/systemone`  
> Full reference: https://docs.typesafe.ai/api.md

## Authentication

```http
Authorization: Bearer YOUR_TYPESAFE_API_KEY
Content-Type: application/json
```

## Request Schema

```json
{
  "model": "jev-latest",
  "state": "string | object | array",
  "questions": {
    "question_id": {
      "type": "noul | choice | score",
      "instructions": "string | object | array",
      "criteria": "object (choice) | array (score) | object (noul, optional)"
    }
  }
}
```

### Field Notes

| Field | Required | Description |
|---|---|---|
| `model` | No | Defaults to `jev-latest`. See [Models](https://docs.typesafe.ai/models.md) |
| `state` | Yes | The content to evaluate |
| `questions` | Yes | Map of question IDs to question objects |
| `questions.*.type` | Yes | `"noul"`, `"choice"`, or `"score"` |
| `questions.*.instructions` | Yes | The judgment to make |
| `questions.*.criteria` | Choice/Score | Options or levels |

## Example Request

```json
{
  "model": "jev-latest",
  "state": {
    "message": "My flight was cancelled. Can I get a refund?",
    "refund_policy": "Cancelled flights are eligible for a full refund."
  },
  "questions": {
    "refund_requested": {
      "type": "noul",
      "instructions": "Does `message` request a refund?"
    },
    "request_type": {
      "type": "choice",
      "instructions": "What is the main request in `message`?",
      "criteria": {
        "refund":      "The customer wants money returned.",
        "rebooking":   "The customer wants a replacement flight.",
        "information": "The customer is asking for information only."
      }
    },
    "frustration": {
      "type": "score",
      "instructions": "How frustrated does the customer appear in `message`?",
      "criteria": ["Calm and neutral.", "Concerned but civil.", "Very angry."]
    }
  }
}
```

## Example Response

```json
{
  "model": "jev-latest",
  "answers": {
    "refund_requested": {
      "type": "noul",
      "noul": 0.95
    },
    "request_type": {
      "type": "choice",
      "choice": "refund",
      "probabilities": {"refund": 0.88, "rebooking": 0.09, "information": 0.03},
      "confidence": 0.82
    },
    "frustration": {
      "type": "score",
      "score": 0.8,
      "legend": ["Calm and neutral.", "Concerned but civil.", "Very angry."],
      "probabilities": [0.25, 0.60, 0.15],
      "confidence": 0.45
    }
  },
  "usage": {
    "input_tokens": 150,
    "output_tokens": 30
  }
}
```

## Keep API Keys Server-Side

> [!caution]
> Never expose your API key in client-side browser code. Always make TypeSafe calls from your server or backend.

## See Also

- [[Python SDK]] — typed Python wrapper
- [[JavaScript SDK]] — typed TypeScript/Node wrapper
- [Full API reference](https://docs.typesafe.ai/api.md)
