---
title: Use-Case Map
tags:
  - jev
  - typesafe
  - guide
aliases:
  - Use Cases
  - Applications
---

# Use-Case Map

> [!abstract] Source
> https://docs.typesafe.ai/concepts/use-case-map.md — browse by industry and turn ideas into software workflows.

## Common Application Categories

### Routing & Classification

| Use Case | Approach |
|---|---|
| Ticket routing to department | [[Choice]] on ticket text |
| Intent detection | [[Choice]] on user message |
| Document type classification | [[Choice]] on document content |
| Language detection | [[Choice]] on text |
| Email topic routing | [[Choice]] on subject + body |

### Ranking & Reranking

| Use Case | Approach |
|---|---|
| RAG passage reranking | [[Score]] each passage for relevance |
| Support ticket priority | [[Pattern - Composite Scoring]] on severity + frustration + report quality |
| Resume shortlisting | Multiple [[Score]] dimensions, combined in code |
| Search result reranking | [[Score]] or [[Choice]] selecting the best candidate |

### Verification & Extraction

| Use Case | Approach |
|---|---|
| Citation verification | [[Choice]]: does quote context support claim? |
| Structured data extraction | Regex finds candidates; [[Choice]] selects correct span |
| Date extraction | [[Choice]] for parts; code resolves and validates |
| Duplicate detection | [[Noul]] per candidate: is this the same entity? |

### Content Moderation & Guardrails

| Use Case | Approach |
|---|---|
| LLM input/output screening | [[Noul]] per hazard type (jailbreak, PII, harmful content) |
| Spam detection | Multiple [[Noul]] signals combined in code |
| Policy violation check | [[Noul]] against specific policy rules |
| Severity scoring | [[Score]] on harm level |

### Interactive Experiences

| Use Case | Approach |
|---|---|
| Smart home assistant | [[Choice]] for action; [[Noul]] for validity |
| Conversational routing | [[Choice]] intent → handler |
| Agent tool selection | [[Choice]] over available tools/skills |
| Function calling | [[Choice]] selects function; [[Choice]]/[[Noul]] fills typed args |

### Data & ML

| Use Case | Approach |
|---|---|
| Feature discovery for ML | [[Score]]/[[Noul]] outputs as labeled features |
| Knowledge graph entity alignment | [[Score]] with levels: merge / leave / review |
| Hierarchical classification | Sequential [[Choice]] requests narrowing options |
| Self-consistency checking | Multiple calls → compare label agreement |

## Architecture Patterns to Match Use Cases

| If you need to... | Use pattern |
|---|---|
| Route to handlers based on intent | [[Pattern - Intent Routing]] |
| Ask many questions cheaply | [[Pattern - Speculative Fan-Out]] |
| Gate actions on certainty | [[Pattern - Confidence-Gated Routing]] |
| Score multi-dimensional quality | [[Pattern - Composite Scoring]] |

## Starting Points

1. Identify what the app needs to **select, change, show, or hand off**
2. Work backward to the **judgments** needed
3. Keep **rules, calculations, lookups** in code
4. Add Jev only where **semantic understanding** is needed
5. Consult the [[Cookbooks Index]] for worked examples

## See Also

- [[Cookbooks Index]] — detailed implementations for specific use cases
- [[How to Build with Jev]] — design workflow
- [Live use-case map](https://docs.typesafe.ai/concepts/use-case-map.md)
