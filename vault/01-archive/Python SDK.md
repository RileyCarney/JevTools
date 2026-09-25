---
title: Python SDK
tags:
  - jev
  - typesafe
  - sdk
aliases:
  - TypeSafe Python
  - typesafe-sdk python
---

# TypeSafe Python SDK

> [!info] Package
> `typesafe-sdk` on PyPI. Source: https://github.com/typesafe-ai/typesafe-sdk-python

## Install

```sh
pip install typesafe-sdk
# or
uv add typesafe-sdk
```

## Auth

Set `TYPESAFE_API_KEY` in your environment (get key at https://console.typesafe.ai/).

## Sync Client

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "billing": Noul(instructions="Is this ticket about billing?"),
            "tone":    Choice(
                instructions="What is the customer's tone?",
                criteria={"calm": None, "frustrated": None, "angry": None},
            ),
            "urgency": Score(
                instructions="How urgent is this ticket?",
                criteria=["can wait", "this week", "today"],
            ),
        },
    )

# Typed accessors
print(response.nouls["billing"].noul)      # float 0–1
print(response.choices["tone"].choice)     # "calm" | "frustrated" | "angry"
print(response.scores["urgency"].score)    # float

# Generic accessor
print(response.answers["billing"].noul)
```

## Async Client

```python
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        response = await client.system_one(
            state={"document": "I was charged twice. Please fix this ASAP."},
            questions={
                "billing": Noul(instructions="Is this ticket about billing?"),
                "tone":    Choice(
                    instructions="What is the customer's tone?",
                    criteria={"calm": None, "frustrated": None, "angry": None},
                ),
                "urgency": Score(
                    instructions="How urgent is this ticket?",
                    criteria=["can wait", "this week", "today"],
                ),
            },
        )

    print(response.nouls["billing"].noul)
    print(response.choices["tone"].choice)
    print(response.scores["urgency"].score)
```

## Key SDK Classes

| Class | Description |
|---|---|
| `TypeSafeClient` | Synchronous client |
| `AsyncTypeSafeClient` | Asynchronous client |
| `Noul(instructions, criteria=None)` | Noul question builder |
| `Choice(instructions, criteria)` | Choice question builder |
| `Score(instructions, criteria)` | Score question builder |

## Response Fields

```python
response.answers          # dict[str, NoulAnswer | ChoiceAnswer | ScoreAnswer]
response.nouls            # dict[str, NoulAnswer]
response.choices          # dict[str, ChoiceAnswer]
response.scores           # dict[str, ScoreAnswer]
response.model            # str — model name used
response.usage            # token usage info
```

## Configuration

```python
TypeSafeClient(
    api_key="...",          # or use TYPESAFE_API_KEY env var
    base_url="...",         # override endpoint
    timeout=30.0,           # seconds
    max_retries=2,
)
```

Default model: `jev-latest`. Override per call:
```python
client.system_one(state=..., questions={...}, model="jev-1.13")
```

## Error Handling

```python
from typesafe_sdk.exceptions import (
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
)
```

## Retries

Configure via `RetryPolicy` — attempt count, retryable statuses, backoff.  
See [retries docs](https://docs.typesafe.ai/sdk/python/api/retries.md).

## See Also

- [[JavaScript SDK]] — Node.js/TypeScript equivalent
- [[HTTP API]] — raw HTTP reference
- [[Primitives Overview]] — how to design questions
- [Full Python SDK docs](https://docs.typesafe.ai/sdk/python.md)
