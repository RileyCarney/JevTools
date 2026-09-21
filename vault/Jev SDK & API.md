---
title: Jev SDK & API
tags: [jev, typesafe, sdk, api, cookbook]
aliases: [Python SDK, JavaScript SDK, TypeScript SDK, HTTP API, TypeSafe API, Cookbooks]
---

# Jev SDK & API — Python, JavaScript, HTTP, Cookbooks

## Python SDK

**Package:** `typesafe-sdk` · **Source:** https://github.com/typesafe-ai/typesafe-sdk-python

```sh
pip install typesafe-sdk   # or: uv add typesafe-sdk
```

Set `TYPESAFE_API_KEY` env var (get key at https://console.typesafe.ai/).

**Sync:**
```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "billing": Noul(instructions="Is this about billing?"),
            "tone":    Choice(instructions="Customer's tone?",
                              criteria={"calm": None, "frustrated": None, "angry": None}),
            "urgency": Score(instructions="How urgent?",
                             criteria=["can wait", "this week", "today"]),
        },
    )

# Typed shorthand accessors
response.nouls["billing"].noul        # float 0–1
response.choices["tone"].choice       # "calm" | "frustrated" | "angry"
response.scores["urgency"].score      # float

# Generic accessor (all primitives)
response.answers["billing"].noul
response.answers["tone"].choice
response.answers["urgency"].score
```

**Async:**
```python
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score

async with AsyncTypeSafeClient() as client:
    response = await client.system_one(state=..., questions={...})
```

**Key classes:**

| Class/Object | Description |
|---|---|
| `TypeSafeClient` | Sync client |
| `AsyncTypeSafeClient` | Async client |
| `Noul(instructions, criteria=None)` | Build Noul question |
| `Choice(instructions, criteria)` | Build Choice question |
| `Score(instructions, criteria)` | Build Score question |

**Response fields:**
```python
response.answers   # dict[str, NoulAnswer | ChoiceAnswer | ScoreAnswer]
response.nouls     # dict[str, NoulAnswer]
response.choices   # dict[str, ChoiceAnswer]
response.scores    # dict[str, ScoreAnswer]
response.model     # str
response.usage     # token usage
```

**Configuration:**
```python
TypeSafeClient(api_key="...", base_url="...", timeout=30.0, max_retries=2)
# Override model per call:
client.system_one(state=..., questions={...}, model="jev-1.13")
```

**Exceptions:** `AuthenticationError` · `RateLimitError` · `APIConnectionError` · `APITimeoutError`

Full reference: https://docs.typesafe.ai/sdk/python.md

---

## JavaScript / TypeScript SDK

**Package:** `@typesafe-ai/sdk` · Node.js 20+ · ESM + CommonJS + TypeScript declarations
**Source:** https://github.com/typesafe-ai/typesafe-sdk-js

```sh
npm install @typesafe-ai/sdk
```

Set `TYPESAFE_API_KEY` env var.

```ts
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const response = await client.systemOne({
    state: { document: "I was charged twice. Please fix this ASAP." },
    questions: {
        billing:  noul("Is this about billing?"),
        tone:     choice("Customer's tone?", { calm: null, frustrated: null, angry: null }),
        urgency:  score("How urgent?", ["can wait", "this week", "today"]),
    },
});

// Answer types are inferred from question types — no casting needed
response.answers.billing.noul            // number
response.answers.tone.choice             // "calm" | "frustrated" | "angry"
response.answers.tone.probabilities      // Record<"calm"|"frustrated"|"angry", number>
response.answers.tone.confidence         // number
response.answers.urgency.score           // number
```

**Key exports:** `TypeSafeClient` · `choice(instructions, criteria)` · `noul(instructions, criteria?)` · `score(instructions, criteria)`

**Configuration:**
```ts
new TypeSafeClient({ apiKey: "...", baseURL: "...", timeout: 30_000, maxRetries: 2 })
```

**Exceptions:** `AuthenticationError` · `RateLimitError` · `APIConnectionError` · `APITimeoutError`

Full reference: https://docs.typesafe.ai/sdk/javascript/api.md

---

## HTTP API

**Endpoint:** `POST https://api.typesafe.ai/v1/systemone`  
**Auth:** `Authorization: Bearer YOUR_TYPESAFE_API_KEY`  
**Full reference:** https://docs.typesafe.ai/api.md

> [!caution] Keep API keys server-side. Never expose in browser/client-side code.

**Request schema:**
```json
{
  "model": "jev-latest",
  "state": "<string | object | array>",
  "questions": {
    "<question_id>": {
      "type": "noul | choice | score",
      "instructions": "<string | object | array>",
      "criteria": "<object for choice | array for score | object for noul (optional)>"
    }
  }
}
```

**Example request:**
```json
{
  "model": "jev-latest",
  "state": {"message": "Flight cancelled. Can I get a refund?",
             "refund_policy": "Cancelled flights eligible for full refund."},
  "questions": {
    "refund_requested": {"type": "noul", "instructions": "Does `message` request a refund?"},
    "request_type": {
      "type": "choice",
      "instructions": "Main request in `message`?",
      "criteria": {"refund": "Wants money returned.", "rebooking": "Wants replacement flight.", "information": "Asking for info only."}
    },
    "frustration": {
      "type": "score",
      "instructions": "How frustrated does the customer appear?",
      "criteria": ["Calm and neutral.", "Concerned but civil.", "Very angry."]
    }
  }
}
```

**Example response:**
```json
{
  "model": "jev-latest",
  "answers": {
    "refund_requested": {"type": "noul", "noul": 0.95},
    "request_type": {"type": "choice", "choice": "refund",
                     "probabilities": {"refund": 0.88, "rebooking": 0.09, "information": 0.03},
                     "confidence": 0.82},
    "frustration": {"type": "score", "score": 0.8,
                    "legend": ["Calm.", "Concerned.", "Very angry."],
                    "probabilities": [0.25, 0.60, 0.15], "confidence": 0.45}
  },
  "usage": {"input_tokens": 150, "output_tokens": 30}
}
```

**Models:** `jev-latest` (default) · See https://docs.typesafe.ai/models.md for versioned aliases and pricing.

---

## Cookbooks Index

Read the closest relevant cookbook before writing a new integration — it often shows a better decomposition.

| Cookbook | Demonstrates | Key Technique |
|---|---|---|
| [Parallel Questions](https://docs.typesafe.ai/cookbooks/parallel_questions.md) | 13 questions in 1 call: 12.2× cheaper, 10× faster | Speculative Fan-Out |
| [Function Calling](https://docs.typesafe.ai/cookbooks/function_calling.md) | Natural-language trading → typed function calls | Choice for name + args |
| [Value Extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md) | Regex candidates → Choice selects → code normalizes | Select-don't-generate |
| [Structure Recovery](https://docs.typesafe.ai/cookbooks/autoformat.md) | Reconstruct Markdown from plain text (2 requests) | Multi-step, state built from prior answers |
| [Reranking](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md) | BM25 shortlist → Jev reranks → top-1 5% → 18% | Score per candidate |
| [Semantic Search](https://docs.typesafe.ai/cookbooks/semantic_find.md) | Score 218 line IDs against query in 1 request | Choice + Noul |
| [Citation Check](https://docs.typesafe.ai/cookbooks/citation_check.md) | Verify quotes against source; flag uncertain | Choice + Confidence |
| [LLM Guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails.md) | Screen LLM I/O for hazards; threshold to block/review | Noul + Score per hazard |
| [Classifying RAG Passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages.md) | Score each passage; filter contradictions/injections | Score per passage |
| [SDE Cascade](https://docs.typesafe.ai/cookbooks/sde_cascade.md) | Mini → verify → reasoning fallback; high quality, low cost | Multi-stage cascade |
| [Date Extraction](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook.md) | Extract dates; resolve and validate in code | Choice for parts |
| [Self-Consistency: Nouls](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook.md) | Route uncertain probabilities to human review | Noul + confidence thresholds |
| [Self-Consistency: Choices](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md) | Compare label agreement with automatic action rate | Choice + agreement scoring |
| [Hierarchical Classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md) | Classify deep hierarchies via parallel beam search | Sequential Choice requests |
| [Skill Suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion.md) | Rank 182 skills → fetch top 3 → judge again | Two-request pattern |
| [Entity Alignment](https://docs.typesafe.ai/cookbooks/entity_alignment.md) | 450 beer catalog pairs: merge/leave/review | Score with decision-action levels |
| [AutoResearch Features](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery.md) | Propose questions → convert text → train CatBoost | Score/Noul as ML features |
| [Classification via Confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md) | 75 industry groups; confidence fallback to broader category | Choice + Confidence hierarchy |

> [!tip] Start with Parallel Questions if new to Jev — it demonstrates the core batching economics.

## See Also
- [[Jev MOC]] · [[Jev Core]] · [[Jev Design]] · [[Jev Patterns]]
- Full docs: https://docs.typesafe.ai
