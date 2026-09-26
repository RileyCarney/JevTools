---
title: Jev MOC
tags:
  - jev
  - typesafe
  - moc
aliases:
  - TypeSafe MOC
  - System One MOC
---

# Jev / TypeSafe — Map of Contents

> [!abstract] What Is This?
> **Jev** is TypeSafe's flagship **System One** model. It turns natural language + application state into typed decisions (not generated text) — probabilities and structured answers your code consumes directly.
> Live docs: https://docs.typesafe.ai/llms.txt

## Core Concepts

- [[System One]] — what System One models are and how they differ from LLMs
- [[State]] — the input you send (string / JSON object / array)
- [[Primitives Overview]] — the three question types and how to pick one

## The Three Primitives

- [[Choice]] — pick one option from a fixed set
- [[Score]] — rate along ordered descriptive levels
- [[Noul]] — probability a yes/no statement is true

## Using Answers

- [[Confidence]] — how certainty is reported and thresholded
- [[Composing Answers in Code]] — combining outputs, weighted scores, ML features

## Building Workflows

- [[How to Build with Jev]] — the design workflow (code first, AI where needed)
- [[Question Design Rules]] — rules for writing effective questions

## Architectural Patterns

- [[Pattern - Speculative Fan-Out]] — many questions per call
- [[Pattern - Confidence-Gated Routing]] — confidence as a second decision axis
- [[Pattern - Composite Scoring]] — combine dimension scores with weights
- [[Pattern - Intent Routing]] — classify intent and route to handlers

## SDK & API

- [[Python SDK]] — sync + async client, install, quickstart
- [[JavaScript SDK]] — TypeScript/Node client, install, quickstart
- [[HTTP API]] — raw POST /v1/systemone reference

## Use-Cases & Cookbooks

- [[Use-Case Map]] — domains and ideas
- [[Cookbooks Index]] — all available cookbooks and what they demonstrate
