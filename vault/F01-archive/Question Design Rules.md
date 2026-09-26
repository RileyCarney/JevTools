---
title: Question Design Rules
tags:
  - jev
  - typesafe
  - guide
aliases:
  - Question Writing Guide
  - Prompt Design for Jev
---

# Question Design Rules

> [!abstract] Purpose
> Concrete rules for writing effective TypeSafe questions. Poor question design is the primary cause of poor results.

## Rule 1 — One Narrow Judgment Per Question

Ask one narrow, coherent judgment per question. Split independently useful dimensions **without** destroying the relationship being judged.

✓ "Does `message.body` ask for a password?"  
✗ "Is `message` spam?" ← hides 5+ independent signals

## Rule 2 — Write Complete Meaning in Instructions

Question IDs are for code and are **never sent to the model**. Never rely on the ID to convey the question — write the complete judgment in `instructions`.

```python
# Wrong: ID implies meaning, instructions are vague
{"is_refund": Noul(instructions="Does this apply?")}

# Right: Instructions are self-contained
{"is_refund": Noul(instructions="Does `ticket.messages[0].text` request a refund?")}
```

## Rule 3 — Give Enough State

Each question needs enough relevant state to answer:
- Source text, identities, relationships, policies, current facts
- Prefer named JSON fields when context has several parts
- Reference specific fields with backtick paths (`ticket.messages[0].text`)

## Rule 4 — Define Criteria Precisely

- **Choice options**: include an `other`/`none_of_the_above` when the list might be incomplete
- **Score levels**: describe **concrete situations** — levels must stand on their own; vague levels produce vague scores
- **Noul criteria**: optional but useful when "yes" and "no" need clarification

```python
# Vague Score levels (bad)
criteria=["low", "medium", "high"]

# Concrete Score levels (good)
criteria=[
    "Production is working normally — no user impact.",
    "A feature is degraded — some users affected.",
    "Production is down — all users affected or data loss occurring.",
]
```

## Rule 5 — Include a No-Match Outcome

When nothing may fit, include a no-match option:
```python
criteria={
    "billing": "Payment or subscription issues",
    "technical": "Bugs or integration problems",
    "sales": "Pricing or account questions",
    "other": "None of the above — escalate to general support",  # ← always include
}
```

## Rule 6 — Ask for Fast Judgments, Not Slow Reasoning

A good question = what a knowledgeable person decides in a second given the right context.

✓ "Does this message convey urgency?"  
✗ "Analyze this message and determine the best course of action" ← slow reasoning; break into multiple questions instead

## Rule 7 — Use Structure When Strings Blur Together

Use object/array `instructions` or `criteria` when:
- Question needs inline context from your code
- Several questions have similar instructions (add supplementary data to distinguish)
- Options need contrastive what/not-for/examples to avoid confusion

```python
# Code-sourced context in structured instructions
Noul(instructions={
    "candidate_record": {"name": "Jane Doe", "last_employer": "Stripe"},
    "question": "Is the resume for the same person as `candidate_record`?"
})
```

## Rule 8 — Use Source Spans; Don't Generate

When you need a specific value extracted:
1. Find candidates in code (regex, lookup)
2. Ask Jev to select/verify the correct one
3. Code normalizes the verbatim selected value

Never ask Jev to **generate** the extracted value — it might hallucinate.

## Rule 9 — Keep Policy in Code

Raw judgments should be reusable. Encode policy (thresholds, weights, routing rules) in code, not in the question:

```python
# Judgment (in Jev)
Score(instructions="How severe is this bug?", criteria=[...])

# Policy (in code)
if answers["bug_severity"].score > 1.5 and answers["production_impact"].noul > 0.8:
    page_on_call_engineer()
```

This way, changing a threshold doesn't require rerunning inference.

## Rule 10 — Check Candidate Coverage for Selection

When using Choice to select from a list of candidates, verify the model **can choose an omitted value**. The model cannot pick what isn't in `criteria`.

## Common Anti-Patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| "Is X good?" | What is "good"? | Define scoring levels or specific conditions |
| ID replaces instructions | Model never sees the ID | Write full question in `instructions` |
| One broad classification | Hides multiple signals | Decompose into atomic questions |
| Asking to generate a value | May hallucinate | Ask to select from candidates |
| Policy baked into question | Can't change without rerunning | Move policy to code |

## See Also

- [[Primitives Overview]] — choosing between Choice / Score / Noul
- [[How to Build with Jev]] — full design workflow
- [[State]] — structuring the context you provide
