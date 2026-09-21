---
title: Cookbooks Index
tags:
  - jev
  - typesafe
  - cookbooks
aliases:
  - Cookbook List
  - TypeSafe Examples
---

# Cookbooks Index

> [!info] Source
> All cookbooks live at https://docs.typesafe.ai (append `.md` to any page path to get raw markdown).  
> Read the closest relevant cookbook before writing a new integration — it often shows a better decomposition than a generic approach.

## All Cookbooks

| Cookbook | What It Demonstrates | Key Technique |
|---|---|---|
| [Parallel Questions](https://docs.typesafe.ai/cookbooks/parallel_questions.md) | 13 questions in one call — 12.2× cheaper, 10× faster vs separate calls | [[Pattern - Speculative Fan-Out]] |
| [Function Calling](https://docs.typesafe.ai/cookbooks/function_calling.md) | Map natural-language trading requests to typed function calls | [[Choice]] for name + args |
| [Value Extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md) | Regex finds candidates; Jev selects correct span; code normalizes | Select-don't-generate |
| [Structure Recovery](https://docs.typesafe.ai/cookbooks/autoformat.md) | Reconstruct Markdown from plain text in 2 requests (merge lines → classify blocks) | Multi-step with state built from prior answers |
| [Reranking](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md) | BM25 shortlist → Jev reranks → top-1 accuracy 5% → 18% | [[Score]] per candidate |
| [Semantic Search](https://docs.typesafe.ai/cookbooks/semantic_find.md) | Score 218 line IDs against a query in one request | [[Choice]] for relevance + [[Noul]] for presence |
| [Citation Check](https://docs.typesafe.ai/cookbooks/citation_check.md) | Verify quotes against source; confidence flags for human review | [[Choice]] + [[Confidence]] |
| [LLM Guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails.md) | Screen LLM inputs/outputs for hazards; threshold to block/review/route | [[Noul]] + [[Score]] per hazard |
| [Classifying RAG Passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages.md) | Score each retrieved passage; filter contradictions or injections | [[Score]] per passage |
| [SDE Cascade](https://docs.typesafe.ai/cookbooks/sde_cascade.md) | Structured data extraction: mini model → verify → reasoning fallback | Multi-stage cascade |
| [Date Extraction](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook.md) | Extract absolute/relative dates; resolve and validate in code | [[Choice]] for parts + code logic |
| [Self-Consistency: Nouls](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook.md) | Route uncertain probabilities to human review | [[Noul]] + confidence thresholds |
| [Self-Consistency: Choices](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md) | Compare label agreement with share of automatic actions | [[Choice]] + agreement scoring |
| [Hierarchical Classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md) | Classify into deep hierarchies using parallel beam search over [[Choice]] probabilities | Sequential requests, narrowing options |
| [Skill Suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion.md) | Rank 182 skills, then read top 3 full texts and judge again | Two-request pattern with evidence fetching |
| [Entity Alignment](https://docs.typesafe.ai/cookbooks/entity_alignment.md) | Decide if 450 candidate pairs describe the same product (merge/leave/review) | [[Score]] with decision-action levels |
| [AutoResearch Feature Discovery](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery.md) | Propose questions, convert text to numeric features, train CatBoost | [[Score]]/[[Noul]] as ML features |
| [Classification Using Confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence.md) | Classify into 75 industry groups; use confidence to fallback to broader category | [[Choice]] + [[Confidence]] for hierarchy |

## How to Navigate

1. Know what you want to build → find the matching row above
2. Fetch the `.md` URL for current, full code
3. Check the "Key Technique" column to understand what primitives/patterns are central

> [!tip] Start with Parallel Questions
> If new to Jev, read [Parallel Questions](https://docs.typesafe.ai/cookbooks/parallel_questions.md) first. It demonstrates the core batching principle that makes Jev economical.

## See Also

- [[Use-Case Map]] — which use case maps to which approach
- [[Pattern - Speculative Fan-Out]] — the batching principle
- [[Primitives Overview]] — understanding the primitives used in cookbooks
