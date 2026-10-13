# JevTools: Project Submission & Review Details

This document contains structured answers to the submission and review questionnaire for **JevTools** ([https://github.com/RileyCarney/JevTools](https://github.com/RileyCarney/JevTools)).

---

## 1. Jev-specific value and suggested category

> **Prompt:**  
> *Who benefits, and what does this add beyond existing entries? For apps, name the feature Jev powers, what other models do, and link evidence such as implementation code or a reproducible demo. At least 40 characters.*

### Suggested Category
**Developer Tools & Frameworks / Semantic Routing, Scoring & Agent Architectures**

### Who Benefits?
Software engineers, autonomous agent developers, backend system architects, and ML platform teams building hybrid deterministic/probabilistic architectures benefit directly. It is designed for applications requiring high-throughput, sub-second semantic triage, confidence-calibrated routing, and structured scoring without paying the latency, token cost, and parsing brittleness of generative LLMs.

### What Does This Add Beyond Existing Entries?
Most AI ecosystem entries focus on generative chat wrappers, multi-turn conversational agents, or complex prompt-engineering scaffolds that rely on generative "System Two" LLMs. Those systems suffer from slow time-to-first-token (1–3s+), high token expenditure, uncalibrated confidence estimates, and frequent JSON parsing or schema hallucination errors.

JevTools introduces a production-ready toolkit, knowledge base, web dashboard, and reference implementation demonstrating **Control Inversion** with **Jev (TypeSafe System One)**:
1. **Control Inversion Architecture:** Host application code strictly controls workflow, state transitions, and business policies. Rather than delegating control flow to an LLM, the application invokes Jev as an ultra-fast (~300 ms) decision kernel that populates typed semantic judgment slots (`noul`, `choice`, `score`).
2. **Dual-Provider Gateway:** First-class support for both the **OpenRouter Alpha Decisions API** (`https://openrouter.ai/api/alpha/decisions`) and the **TypeSafe Direct Native API** (`https://api.typesafe.ai/v1/systemone`), featuring dynamic provider detection, cross-provider model sanitization, and fallback routing.
3. **Zero-Dependency Personal Device Telemetry & Storage:** An embedded SQLite engine ([`database.py`](file:///D:/Programming/jevtools/database.py)) running in WAL mode logs every prompt, typed question, calibrated probability distribution, and execution latency locally. It is strictly gitignored to guarantee complete privacy and zero data leakage.
4. **Interactive Cybernetic Web Dashboard:** A zero-dependency localhost dashboard ([`index.html`](file:///D:/Programming/jevtools/index.html) + [`server.py`](file:///D:/Programming/jevtools/server.py)) with real-time probability meters, speculative fan-out visualization, schema exploration, and an offline mock mode.
5. **Obsidian Knowledge Vault:** A comprehensive 40+ note vault ([`vault/`](file:///D:/Programming/jevtools/vault/)) documenting 18 architectural cookbooks (dual-threshold escalation, speculative evaluation, multi-model fallbacks, etc.).

### Features Jev Powers
* **Speculative Fan-Out Customer Review Analysis & Triage (Demo 1):** Jev runs a parallel 6-question speculative evaluation (`overall_sentiment`, `quality_of_feedback`, `mentions_defect`, `mentions_shipping`, `would_recommend`, `emotion_tone`). Application code computes a weighted composite score ($0.40 \cdot \text{sentiment} + 0.25 \cdot \text{recommend} + 0.20 \cdot \text{quality} + 0.15 \cdot (1 - \text{defect})$) and executes confidence-gated policy escalation (`[ESCALATE]`, `[CONTACT]`, `[POSITIVE]`, `[FLAG]`).
* **Multi-Dimensional Topic Classification & Content Routing (Demo 2):** Jev extracts primary topic classification (`choice` across 9 domains) alongside stylistic properties (`is_opinion` as binary `noul`, `technical_depth` as 3-tier `score`, `has_actionable` as `noul`) simultaneously, routing items to specialized editorial or technical desks.
* **Custom Decision Playground:** Evaluates arbitrary application state against user-defined question schemas in real-time.

### What Other Models Do
Generative LLMs (e.g., GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro) are "System Two" text generation engines. When assigned routing, categorization, or scoring tasks:
* They generate token-by-token conversational text or JSON strings, requiring 1,000–3,000+ ms of latency.
* They require fragile prompt engineering, JSON mode / tool-calling overhead, and post-generation regex parsing.
* They do not emit calibrated output-layer probability distributions for discrete options, making confidence thresholds arbitrary.
* They incur high token costs for both input scaffolds and output generation.

In contrast, **Jev** acts as "System One": it computes decisions in ~300 ms, directly outputs calibrated probability distributions over discrete answer spaces, uses zero token generation overhead, and produces strictly typed, deterministic responses.

### Evidence & Reproducible Demos
* **Implementation Code:**
  * GitHub Repository: [https://github.com/RileyCarney/JevTools](https://github.com/RileyCarney/JevTools)
  * Review Analysis & Policy Routing: [`jev_demo.py` (lines 180–265)](https://github.com/RileyCarney/JevTools/blob/main/jev_demo.py) / local [`jev_demo.py`](file:///D:/Programming/jevtools/jev_demo.py)
  * Dual-Gateway Decision Engine: [`jev_demo.py` (lines 60–175)](https://github.com/RileyCarney/JevTools/blob/main/jev_demo.py)
  * Local Telemetry SQLite Engine: [`database.py`](https://github.com/RileyCarney/JevTools/blob/main/database.py) / local [`database.py`](file:///D:/Programming/jevtools/database.py)
  * Web Dashboard & Server: [`index.html`](https://github.com/RileyCarney/JevTools/blob/main/index.html) and [`server.py`](https://github.com/RileyCarney/JevTools/blob/main/server.py)
* **Reproducible Demos:**
  * Offline CLI Mock Demo (no API key or internet required):
    ```powershell
    py jev_demo.py --mock
    py jev_demo.py --demo reviews --json --mock
    ```
  * Custom Review Evaluation:
    ```powershell
    py jev_demo.py --review "The battery completely failed on day 2. Horrible support." --mock
    ```
  * Web Dashboard One-Click Launch:
    ```powershell
    py server.py # or double-click start_ui.bat
    ```

---

## 2. Project guide details (optional)

> **Prompt:**  
> *When to use it, setup and expected output, real example or demo links, prerequisites, key variables, data recipients, costs, license, and limitations.*

### When to Use It
* When building software pipelines or agent architectures requiring ultra-fast (<400 ms), deterministic, structured semantic evaluations (sentiment scoring, content filtering, priority routing, intent triage, defect detection) without the latency and token costs of generative LLMs.
* When migrating away from slow, brittle prompt-and-parse loops to typed, deterministic decision slots.
* When prototyping, evaluating, or benchmarking Jev models locally with an interactive GUI, zero-credit mock engine, and on-device telemetry audit log.

### Setup and Expected Output
1. **Setup:**
   ```bash
   git clone https://github.com/RileyCarney/JevTools.git
   cd JevTools
   pip install -r requirements.txt
   ```
2. **Web Dashboard Execution:**
   ```powershell
   py server.py
   ```
   *Expected Output:* Local web server binds to `http://localhost:8089` (or next free port), launches the default browser, and renders the cybernetic dashboard with live probability meters, Review Studio, Topic Studio, and the SQLite history explorer.
3. **CLI Execution:**
   ```powershell
   py jev_demo.py --demo reviews --mock
   ```
   *Expected Output:* Formatted console output detailing 6 parallel questions, extracted types, normalized scores, composite calculations, policy escalation banner (`[ESCALATE] High-probability product defect mentioned`), and sub-second execution metrics (`elapsed_ms`), or clean structured JSON with `--json`.

### Real Example & Demo Links
* **Repository:** [https://github.com/RileyCarney/JevTools](https://github.com/RileyCarney/JevTools)
* **Documentation & Walkthrough:** [`README.md`](file:///D:/Programming/jevtools/README.md) and [`jev_demo_README.md`](file:///D:/Programming/jevtools/jev_demo_README.md)
* **Sample CLI Run:**
  ```powershell
  # Topic classification demo
  py jev_demo.py --topic "Federal regulators raised interest rates by 25 basis points." --mock
  ```

### Prerequisites
* Python 3.8 or higher.
* Python `requests` library (`pip install requests`).
* *(Optional for live calls)* An OpenRouter API Key (`sk-or-v1-...`) or TypeSafe API Key (`ts-...`). Offline mock mode requires zero keys and zero network connectivity.

### Key Variables
* **Environment Variables:**
  * `OPENROUTER_API_KEY`: OpenRouter bearer authentication token.
  * `TYPESAFE_API_KEY`: TypeSafe direct native API token.
  * `OPENROUTER_REFERER`: HTTP referer header for OpenRouter analytics (defaults to `https://github.com/RileyCarney/JevTools`).
  * `OPENROUTER_TITLE`: Custom application title displayed on OpenRouter (defaults to `JevTools Demo`).
  * `JEV_MODEL`: Optional model override.
  * `JEV_API_URL`: Optional custom endpoint URL.
* **CLI Flags:**
  * `--provider {openrouter, typesafe}`
  * `--model <model_name>`
  * `--endpoint <url>`
  * `--demo {reviews, topics, all}`
  * `--review "<text>"`, `--product "<name>"`, `--topic "<text>"`
  * `--mock` (offline testing)
  * `--benchmark` (latency testing)
  * `--history`, `--all`, `--limit <n>`, `--filter-action`, `--filter-status`, `--filter-search`, `--db-schema`, `--clear-history`
  * `--json` (machine-readable JSON output)

### Data Recipients
* **Personal Device Storage:** All request inputs, evaluation questions, model responses, probabilities, and latency numbers are stored exclusively in a local SQLite database (`jevtools.db`) on your machine. This file is strictly listed in `.gitignore` and never committed or transmitted.
* **Remote Gateways (Live mode only):**
  * When using OpenRouter: State and questions are sent via HTTPS to `https://openrouter.ai/api/alpha/decisions`.
  * When using TypeSafe Direct: Payloads are sent via HTTPS to `https://api.typesafe.ai/v1/systemone`.
* **Mock Mode:** 100% on-device; no external data recipients.

### Costs
* **Mock Mode & Local Testing:** $0.00 (completely free, zero credits consumed).
* **OpenRouter Decisions:** Billed according to OpenRouter's standard alpha decision pricing for `~typesafe/jev-latest` (sub-cent microtransactions; orders of magnitude cheaper than generative text models due to absence of token generation overhead).
* **TypeSafe Direct:** Billed against active TypeSafe subscription / credits.

### License
* **MIT License** ([`LICENSE`](file:///D:/Programming/jevtools/LICENSE))

### Limitations
* Jev is an atomic semantic decision model ("System One"), not a conversational or generative model ("System Two"). It does not write arbitrary text, generate code, or draft creative essays.
* Candidate answer spaces must be defined ahead of time in the question schema (e.g., discrete choices, numeric rubrics, or binary truth conditions).
* The OpenRouter Decisions endpoint is designated as Alpha (`/api/alpha/decisions`).

---

## 3. Your review

> **Prompt:**  
> *What did you read or run? Supported API or model versions, prerequisites, costs, and known limitations. At least 20 characters.*

### What Was Read and Run
* **Code & Architecture Review:** Thoroughly reviewed the complete JevTools codebase and architectural documentation:
  * [`README.md`](file:///D:/Programming/jevtools/README.md) and [`jev_demo_README.md`](file:///D:/Programming/jevtools/jev_demo_README.md)
  * Core CLI & Decision Engine: [`jev_demo.py`](file:///D:/Programming/jevtools/jev_demo.py)
  * Local Storage Engine: [`database.py`](file:///D:/Programming/jevtools/database.py)
  * HTTP Web Server & REST API: [`server.py`](file:///D:/Programming/jevtools/server.py)
  * Web Dashboard: [`index.html`](file:///D:/Programming/jevtools/index.html)
  * Security audits: [`SECURITY.md`](file:///D:/Programming/jevtools/SECURITY.md) and [`SECURITY_REMEDIATION_PLAN.md`](file:///D:/Programming/jevtools/SECURITY_REMEDIATION_PLAN.md)
  * Obsidian Knowledge Vault: [`vault/`](file:///D:/Programming/jevtools/vault/) (including core concepts, patterns, SDKs, and cookbooks)
* **Execution & Verification:**
  * Executed the comprehensive automated test suite (`tests/test_database.py`, `tests/test_jev_demo.py`, `tests/test_server.py`).
  * Ran offline mock evaluations across review and topic classification benchmarks (`py jev_demo.py --mock`, `py jev_demo.py --demo reviews --json`).
  * Verified localhost REST API endpoints (`/api/status`, `/api/analyze-review`, `/api/classify-topic`, `/api/custom-decision`, `/api/config`, `/api/history`, `/api/history/stats`) with SQLite WAL persistence.
  * Tested live model routing against TypeSafe's API (`https://api.typesafe.ai/v1/systemone`) and OpenRouter's API (`https://openrouter.ai/api/alpha/decisions`), verifying model sanitization (`sanitize_model_for_provider`), error handling, and latency profiling (sub-380 ms actual round-trip latency).

### Supported API and Model Versions
* **OpenRouter Alpha Decisions Gateway:**
  * Endpoint: `POST https://openrouter.ai/api/alpha/decisions`
  * Models:
    * `~typesafe/jev-latest` (Recommended, auto-redirect to latest Jev)
    * `typesafe/jev-latest`
    * `typesafe/jev-1.13`
    * `typesafe/jev-router` (Adaptive routing)
    * `openrouter/auto`
* **TypeSafe Direct Native Gateway:**
  * Endpoint: `POST https://api.typesafe.ai/v1/systemone`
  * Models:
    * `jev-latest` (Recommended)
    * `jev-1.13` (Production Stable)
    * `jev-1.13.0` (Pinned Release)
    * `jev-preview` (Preview Track)

### Prerequisites
* Python 3.8+ and `requests >= 2.28.0`.
* Optional API key (`OPENROUTER_API_KEY` or `TYPESAFE_API_KEY`) for live inference.
* Works seamlessly across Windows, macOS, and Linux without external database daemons.

### Costs
* Free and open-source under MIT. Zero cost for local usage, unit testing, schema exploration, and mock mode (`--mock`).
* Live decisions incur sub-cent micro-costs on OpenRouter or TypeSafe.

### Known Limitations
* Decision-oriented only: Jev returns typed primitives (`choice`, `score`, `noul`) with probability distributions; it does not synthesize free-form text or long-form reasoning traces.
* Request schemas must provide explicit question structures and candidate answer spaces.
* OpenRouter Decisions endpoint is currently in Alpha.

---

## 4. Affiliation and AI assistance

> **Prompt:**  
> *Your relationship to the project and any AI assistance used for this submission. “None” is fine.*

* **Relationship to the Project:** Creator, maintainer, and lead developer of JevTools ([RileyCarney/JevTools](https://github.com/RileyCarney/JevTools)).
* **AI Assistance:** Formulated, structured, and compiled with the assistance of Antigravity (Google DeepMind agentic AI coding assistant).
