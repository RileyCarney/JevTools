---
title: JavaScript SDK
tags:
  - jev
  - typesafe
  - sdk
aliases:
  - TypeSafe JavaScript
  - TypeSafe TypeScript
  - "@typesafe-ai/sdk"
---

# TypeSafe JavaScript/TypeScript SDK

> [!info] Package
> `@typesafe-ai/sdk` on npm. Source: https://github.com/typesafe-ai/typesafe-sdk-js  
> Requires Node.js 20+. Includes ESM, CommonJS, and TypeScript declarations.

## Install

```sh
npm install @typesafe-ai/sdk
```

## Auth

Set `TYPESAFE_API_KEY` in your environment (get key at https://console.typesafe.ai/).

## Quick Start

```ts
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();

const response = await client.systemOne({
  state: { document: "I was charged twice. Please fix this ASAP." },
  questions: {
    billing:  noul("Is this ticket about billing?"),
    tone:     choice("What is the customer's tone?", {
                billing: null, technical: null, other: null,
              }),
    urgency:  score("How urgent is this ticket?", [
                "can wait", "this week", "today"
              ]),
  },
});

console.log(response.answers.billing.noul);    // number 0–1
console.log(response.answers.tone.choice);     // "billing" | "technical" | "other"
console.log(response.answers.urgency.score);   // number
```

## Key Functions and Classes

| Export | Description |
|---|---|
| `TypeSafeClient` | Main client class |
| `choice(instructions, criteria)` | Build a Choice question |
| `noul(instructions, criteria?)` | Build a Noul question |
| `score(instructions, criteria)` | Build a Score question |

## Answer Types (TypeScript-inferred)

Answer types are inferred from the question types — no manual casting needed:

```ts
const result = await client.systemOne({
  state: "...",
  questions: {
    category: choice("Category?", { billing: null, tech: null }),
    urgent:   noul("Is this urgent?"),
  },
});

// TypeScript knows these types:
result.answers.category.choice        // "billing" | "tech"
result.answers.category.probabilities // Record<"billing" | "tech", number>
result.answers.category.confidence    // number
result.answers.urgent.noul            // number
```

## Configuration

```ts
const client = new TypeSafeClient({
  apiKey: "...",      // or TYPESAFE_API_KEY env var
  baseURL: "...",     // override endpoint
  timeout: 30_000,    // ms
  maxRetries: 2,
});
```

## Error Types

```ts
import {
  AuthenticationError,
  RateLimitError,
  APIConnectionError,
  APITimeoutError,
} from "@typesafe-ai/sdk";
```

## See Also

- [[Python SDK]] — Python equivalent
- [[HTTP API]] — raw HTTP reference
- [[Primitives Overview]] — how to design questions
- [Full JS SDK API reference](https://docs.typesafe.ai/sdk/javascript/api.md)
