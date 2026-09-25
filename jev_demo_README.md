<p align="center">
  <a href="https://github.com/RileyCarney/JevTools">
    <img src="https://repository-images.githubusercontent.com/1379027574/d9770636-5e32-4332-a030-72d119b8227f" alt="JevTools Banner" width="850">
  </a>
</p>

# Jev Demo: Semantic Decisions via OpenRouter

An example application demonstrating how to build fast, typed, deterministic judgment workflows with **Jev (TypeSafe System One)** accessed through the **OpenRouter Alpha Decisions API**.

Unlike generative Large Language Models that output unconstrained conversational text requiring complex prompt engineering and regex parsing, **Jev evaluates application state against typed questions and returns calibrated probability distributions and structured answers** with 287 ms tested inference latency (TTFT: 287 ms via OpenRouter API). Your code owns control flow and policy logic; Jev fills atomic semantic judgment slots.

---

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
  - [1. Web Cockpit UI (Localhost Dashboard)](#1-web-cockpit-ui-localhost-dashboard)
  - [2. Setting Your OpenRouter API Key](#2-setting-your-openrouter-api-key)
  - [3. Running the Demo via CLI](#3-running-the-demo-via-cli)
  - [4. Custom Text Analysis (--review, --topic)](#4-custom-text-analysis---review---topic)
  - [5. Offline Mock Testing](#5-offline-mock-testing)
  - [6. Personal Device Data Storage & History Tracking](#6-personal-device-data-storage--history-tracking)
- [Security & Key Hygiene (CLI Audit)](#security--key-hygiene-cli-audit)
- [OpenRouter API Architecture](#openrouter-api-architecture)
  - [Endpoint & Model](#endpoint--model)
  - [HTTP Headers](#http-headers)
  - [The 3 Core Primitives](#the-3-core-primitives)
- [Demo Walkthroughs](#demo-walkthroughs)
  - [Demo 1: Customer Review Analysis](#demo-1-customer-review-analysis)
  - [Demo 2: Topic Classification](#demo-2-topic-classification)
- [CLI Reference](#cli-reference)
- [Troubleshooting & FAQ](#troubleshooting--faq)

---

## Prerequisites

- **Python 3.8+**
- **Requests library**:
  ```bash
  pip install requests
  ```
  *(No vendor SDK required; calls are made directly via HTTP to OpenRouter).*
- An **OpenRouter API Key** (`sk-or-v1-...`). You can generate one at [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys).

---

## Quick Start

### 1. Web Cockpit UI (Localhost Dashboard)

Launch the interactive cyber/dark Web Cockpit following the [Website Project Tracking Template]:

```powershell
# Double-click start_ui.bat or run:
py server.py
```

Opens `http://localhost:8089` automatically with an interactive particle canvas, Review Studio, Topic Studio, Custom Playground, and live probability meters.

### 2. Setting Your OpenRouter API Key

We strongly recommend setting the key via environment variable to keep credentials out of process tables and terminal history:

#### Windows (PowerShell):
```powershell
$env:OPENROUTER_API_KEY = "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
py jev_demo.py
```

#### Windows (CMD):
```cmd
set OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
py jev_demo.py
```

#### Linux / macOS / Bash:
```bash
export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
python3 jev_demo.py
```

### 3. Running the Demo via CLI

If the environment variable is not set and you run the script without arguments, `jev_demo.py` will prompt you interactively:

```text
[?] No OPENROUTER_API_KEY or TYPESAFE_API_KEY environment variable detected.
Enter your OpenRouter or TypeSafe API key: [input is hidden]
```

To run a specific demo scenario:
```powershell
# Run only Customer Review Analysis (Demo 1)
py jev_demo.py --demo reviews

# Run only Topic Classification (Demo 2)
py jev_demo.py --demo topics

# Run both demos (default)
py jev_demo.py --demo all

# Output machine-readable JSON
py jev_demo.py --demo reviews --json --mock
```

### 4. Custom Text Analysis (--review, --topic)

Evaluate your own custom reviews or articles directly from the command line:

```powershell
# Analyze a custom product review
py jev_demo.py --review "The battery completely failed on day 2. Horrible support." --mock

# Classify a custom paragraph into a topic domain
py jev_demo.py --topic "Federal regulators raised interest rates by 25 basis points." --json --mock
```

### 5. Offline Mock Testing

You can test the entire application, CLI options, composite scoring formulas, and confidence routing logic without making any network requests or consuming OpenRouter credits using `--mock`:

```powershell
py jev_demo.py --mock
```

### 6. Personal Device Data Storage & History Tracking

Every evaluation sent through the CLI or Web Cockpit is automatically recorded in a local SQLite database (`jevtools.db`):
- **Stored Data:** Timestamp, client identifier (`cli`, `web_ui`), action type (`analyze_review`, `classify_topic`, `custom_decision`, `openrouter_ttft`), execution mode (`live` vs `mock`), full request payload (state text, questions, criteria), full response payload (answers, probabilities, composite score, routing action), status (`ok` or `error`), TTFT, and elapsed inference latency.
- **Privacy & Gitignore:** The database file `jevtools.db` is strictly listed in `.gitignore`. Your prompts, user data, customer reviews, and evaluation results stay exclusively on your personal device and are never committed to Git.
- **Inspect History:**
  ```powershell
  # Display formatted history table and summary metrics (no API key required)
  py jev_demo.py --history

  # Output full database records as structured JSON
  py jev_demo.py --history --json
  ```
- **Clear Database:**
  ```powershell
  # Wipe all logged interactions and reclaim disk space via SQLite VACUUM
  py jev_demo.py --clear-history
  ```

---

## Security & Key Hygiene (CLI Audit)

In CLI applications, passing secrets as command-line flags (e.g. `py jev_demo.py --api-key sk-or-...`) is considered a security vulnerability for several reasons:

1. **Process List Exposure:** Command arguments are visible in plain text to any local user or background monitoring tool via `Get-Process` on Windows, `/proc` on Linux, or `ps aux`.
2. **Terminal History:** Shell history files (e.g., `ConsoleHost_history.txt`, `.bash_history`) record the full command string, persisting API keys on disk.
3. **Log Scraping:** CI/CD runners and automated task runners often log full command lines in public build outputs.

### How `jev_demo.py` Protects Your Key:
- **Priority 1: Environment Variable (`OPENROUTER_API_KEY`)**  
  Keys remain securely in memory and never appear on the command line.
- **Priority 2: Interactive `getpass` Prompt**  
  Reads your key via OS-level masked stdin without echoing characters to the terminal or writing them to command history.
- **Key Display Masking**  
  Console output masks all characters after the prefix (`sk-...`), confirming the key was loaded without leaking the secret token.
- **Fallback Warning**  
  If `--api-key` is supplied explicitly, the script emits a prominent security warning explaining the risks.

---

## OpenRouter API Architecture

### Endpoint & Model
Jev is served through OpenRouter's structured decisions endpoint:
- **Endpoint:** `POST https://openrouter.ai/api/alpha/decisions`
- **Model:** `~typesafe/jev-latest` (or `typesafe/jev-1.13`)

### HTTP Headers
```http
POST /api/alpha/decisions HTTP/1.1
Host: openrouter.ai
Authorization: Bearer <OPENROUTER_API_KEY>
Content-Type: application/json
HTTP-Referer: https://github.com/RileyCarney/JevTools
X-OpenRouter-Title: JevTools Demo
```

### The 3 Core Primitives

| Primitive | Output Type | Description | Best For |
| :--- | :--- | :--- | :--- |
| **`noul`** | `float` ($0.0 \dots 1.0$) | Calibrated binary probability $P(\text{true})$. Uncertainty is self-contained. | Yes/No conditions: defect present, refund requested, urgent flag. |
| **`choice`** | `dict` (`choice`, `confidence`, `probabilities`) | Categorization into a discrete set of mutually exclusive options. | Multi-way routing: department triage, topic categorization. |
| **`score`** | `dict` (`score`, `confidence`, `probabilities`) | Placement on an ordered descriptive rubric ($0 \dots N-1$). Can return fractional values between tiers. | Graded spectrums: customer frustration, sentiment, technical depth. |

---

## Demo Walkthroughs

### Demo 1: Customer Review Analysis

Demonstrates the **Speculative Fan-Out Pattern**: 6 distinct evaluation questions are sent in a single parallel request for each review.

#### Questions Asked in Parallel:
1. `overall_sentiment` (`score`, 4 levels: 0=strongly negative to 3=strongly positive)
2. `quality_of_feedback` (`score`, 3 levels: 0=vague to 2=detailed)
3. `mentions_defect` (`noul`: probability product has a physical defect or malfunction)
4. `mentions_shipping` (`noul`: probability shipping or packaging is discussed)
5. `would_recommend` (`noul`: probability customer recommends the product)
6. `emotion_tone` (`choice`: calm, frustrated, delighted, other)

#### Decision Policy & Action Routing in Code:
```python
# Composite score formula:
composite = (
    0.40 * sentiment_norm
    + 0.25 * recommend_p
    + 0.20 * quality_norm
    + 0.15 * (1.0 - defect_p)
)

# Deterministic routing logic:
if emotion_conf < 0.5:
    action = "[FLAG] Ambiguous tone - route to human reviewer"
elif defect_p > 0.75:
    action = "[ESCALATE] High-probability product defect mentioned"
elif emotion == "frustrated" and composite < 0.35:
    action = "[CONTACT] Frustrated customer with poor experience - outreach recommended"
elif composite >= 0.70:
    action = "[POSITIVE] Feature as testimonial or send thank-you"
elif composite >= 0.40:
    action = "[REVIEW] Moderate feedback - log for product team"
else:
    action = "[POOR] Low-score review - log and consider follow-up"
```

---

### Demo 2: Topic Classification

Demonstrates **Multi-Dimensional Semantic Extraction & Routing**: classifying paragraphs across 5 distinct topics and evaluating writing characteristics simultaneously.

#### Questions Asked in Parallel:
1. `primary_topic` (`choice`, 9 options: technology, science, business, politics, health, environment, culture, education, other)
2. `is_opinion` (`noul`: probability the passage expresses subjective opinion/editorial viewpoint)
3. `technical_depth` (`score`, 3 levels: general audience, informed reader, specialist)
4. `has_actionable` (`noul`: probability text includes a directive or call-to-action)

#### Routing Policy in Code:
- **Low confidence ($< 50\%$)**: Flagged as multi-topic or ambiguous for human tagger.
- **High Opinion ($> 80\%$) in Politics/Health/Culture**: Routed to the **Editorial Desk**.
- **High Technical Depth ($> 65\%$) in Tech/Science**: Routed to **Subject-Matter Specialists**.
- **Actionable ($> 75\%$)**: Routed to the **Engagement & Campaign Team**.
- **Standard**: Routed directly to the corresponding category feed.

---

## CLI Reference

```text
usage: jev_demo.py [-h] [--api-key KEY] [--provider {openrouter,typesafe}]
                   [--model MODEL] [--endpoint ENDPOINT]
                   [--demo {reviews,topics,all}] [--review REVIEW]
                   [--product PRODUCT] [--topic TOPIC] [--mock] [--json]
                   [--history] [--clear-history]

Jev demo: customer review analysis + topic classification via OpenRouter / TypeSafe

options:
  -h, --help            Show this help message and exit
  --api-key KEY         API key (sk-or-v1-... or ts-...). Falls back to
                        OPENROUTER_API_KEY or TYPESAFE_API_KEY env var, then
                        an interactive secure prompt.
  --provider {openrouter,typesafe}
                        Explicitly select provider. Auto-detected from key prefix if omitted.
  --model MODEL         Override model name (~typesafe/jev-latest, jev-latest).
  --endpoint ENDPOINT   Override decision API endpoint URL.
  --demo {reviews,topics,all}
                        Which benchmark demo to run: 'reviews', 'topics', or 'all' (default: all).
  --review REVIEW       Custom customer review text to evaluate immediately.
  --product PRODUCT     Product name for custom review evaluation (default: Wireless Earbuds Pro).
  --topic TOPIC         Custom paragraph text to classify immediately.
  --mock                Run in offline mock mode to test formatting and policy
                        logic without making API calls.
  --json                Output structured JSON results instead of human-readable text.
  --history             View personal device request/response history table and storage metrics.
  --clear-history       Clear all stored interaction records from the local database.
```

---

## Troubleshooting & FAQ

### 1. `HTTP 401: User not found` or `Unauthorized`
- Verify that your key starts with `sk-or-v1-`.
- Ensure the key was created under an active OpenRouter account at [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys).
- If setting via PowerShell, ensure you did not include extra trailing spaces:
  ```powershell
  $env:OPENROUTER_API_KEY = "sk-or-v1-..."
  ```

### 2. `HTTP 402: Payment Required` / Insufficient Credits
- OpenRouter requires credits for model inference. Check your balance at [openrouter.ai/credits](https://openrouter.ai/credits).

### 3. Windows `UnicodeEncodeError: 'charmap'`
- The script includes built-in UTF-8 stream reconfiguring (`sys.stdout.reconfigure(encoding='utf-8', errors='replace')`) and terminal-friendly ASCII markers (`[OK]`, `[!]`, `[FLAG]`) so it works out-of-the-box on Windows PowerShell 5.1, PowerShell 7, Command Prompt, and Windows Terminal.

---

## License
MIT