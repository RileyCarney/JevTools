<p align="center">
  <a href="https://github.com/RileyCarney/JevTools">
    <img src="https://repository-images.githubusercontent.com/1379027574/d9770636-5e32-4332-a030-72d119b8227f" alt="JevTools Banner" width="850">
  </a>
</p>

# JevTools

A toolkit, knowledge base, web cockpit, and reference implementation for building AI applications with **Jev (TypeSafe System One)** via **OpenRouter Alpha Decisions** and **TypeSafe Direct API**.

---

## What is Jev?

**Jev** is a sub-second "System One" decision model built by TypeSafe AI. It acts as an automated semantic router, scorer, and verifier in software systems:

- **Fast:** ~100 ms average inference latency.
- **Typed:** Returns structured types (`choice`, `score`, `noul`) with calibrated probability distributions.
- **Control Inversion:** Code owns application workflow and control flow; Jev evaluates state and fills typed judgment slots without free-form text parsing.

---

## Repository Architecture

- **[`index.html`](./index.html):** Futuristic, cybernetic Web Cockpit styled to match the official GitHub banner preview. Features the 3D extruded `JEVTOOLS` wordmark with GitHub Octocat integration, a dynamic PCB circuit board matrix canvas with animated glowing electron pulses, real-time probability meters, dynamic routing banners, and an architecture hub.
- **[`assets/`](./assets/):** Brand visual assets, including the high-resolution GitHub repository preview banner (`jevtools_banner.png`, `jevtools_card.png`), app icon (`icon.png`), and vector SVG favicons and logos (`favicon.svg`, `jevtools_logo.svg`).
- **[`server.py`](./server.py):** Zero-dependency Python localhost web server (CORS-enabled, port auto-scanning, browser auto-launch, asset serving) exposing REST API endpoints:
  - `GET /api/status`: Engine status, provider, masked API key, benchmark counts.
  - `POST /api/analyze-review`: Runs 6-question speculative fan-out and composite scoring.
  - `POST /api/classify-topic`: Runs multi-dimensional classification and routing policy.
  - `POST /api/custom-decision`: Evaluates arbitrary user-defined state and question schemas.
  - `POST /api/config`: Dynamically updates session keys, execution mode, or provider.
- **[`start_ui.bat`](./start_ui.bat) / [`start_dashboard.bat`](./start_dashboard.bat):** One-click batch launchers for the web cockpit.
- **[`jev_demo.py`](./jev_demo.py):** Enhanced, production-ready CLI application and Python library:
  - **Demo 1 (Customer Review Analysis):** Speculative fan-out evaluating 6 questions in parallel, weighted composite scoring, and action escalation.
  - **Demo 2 (Topic Classification):** Multi-dimensional classification, property detection, and confidence-gated routing.
  - **CLI Flags:** Custom input evaluation (`--review`, `--topic`, `--product`), structured JSON output (`--json`), multi-provider auto-detection (`--provider {openrouter,typesafe}`), and offline mock testing (`--mock`).
- **[`jev_demo_README.md`](./jev_demo_README.md):** Detailed guide to Jev decisions, API architecture, CLI usage, and security.
- **[`vault/`](./vault/):** Obsidian-compatible knowledge vault documenting Jev architecture, core concepts, design rules, SDKs, and 18 cookbooks.
- **[`skills/`](./skills/):** Antigravity agent skills for Jev development and Obsidian markdown.

---

## Quick Start

### 1. Launching the Web Cockpit UI

Double-click **`start_ui.bat`** or run from your terminal:

```powershell
py server.py
```

The server binds automatically to `http://localhost:8089` (or next free port) and opens your browser.

> [!TIP]
> The cockpit comes with a full **Offline Mock Mode (Zero-Credit Testing)** toggle, allowing you to interactively test arbitrary reviews, custom topics, and raw Jev JSON payloads without consuming API credits or requiring an internet connection.

### 2. Running via CLI

#### Benchmark Demos:
```powershell
# Run offline mock mode (no API key needed)
py jev_demo.py --mock

# Output clean machine-readable JSON
py jev_demo.py --mock --demo reviews --json
```

#### Custom Text Analysis:
```powershell
# Evaluate a custom customer review
py jev_demo.py --review "The sound quality is incredible and battery lasts all week!" --mock

# Classify a custom topic paragraph
py jev_demo.py --topic "The central bank lowered interest rates following the latest CPI release." --json --mock
```

#### Running Live with Your API Key:
```powershell
# PowerShell (recommended to keep key out of process tables)
$env:OPENROUTER_API_KEY = "sk-or-v1-xxxxxxxxxxxxxxxx"
py jev_demo.py
```

---

## License
MIT
