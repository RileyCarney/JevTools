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

- **Fast:** 287 ms actual tested inference latency (TTFT: 287 ms via OpenRouter API).
- **Typed:** Returns structured types (`choice`, `score`, `noul`) with calibrated probability distributions.
- **Control Inversion:** Code owns application workflow and control flow; Jev evaluates state and fills typed judgment slots without free-form text parsing.

---

## Repository Architecture

- **[`index.html`](./index.html):** Futuristic, cybernetic Web Cockpit styled to match the official GitHub banner preview. Features the 3D extruded `JEVTOOLS` wordmark with GitHub Octocat integration, a dynamic PCB circuit board matrix canvas with animated glowing electron pulses, real-time probability meters, dynamic routing banners, an interactive Request History & Storage inspector, and an architecture hub.
- **[`assets/`](./assets/):** Brand visual assets, including the high-resolution GitHub repository preview banner (`jevtools_banner.png`, `jevtools_card.png`), app icon (`icon.png`), and vector SVG favicons and logos (`favicon.svg`, `jevtools_logo.svg`).
- **[`database.py`](./database.py):** Zero-dependency local SQLite database engine (`jevtools.db`, strictly gitignored) for personal device storage. Captures all outgoing requests, incoming responses, decision metrics, latency, and status without third-party dependencies.
- **[`server.py`](./server.py):** Zero-dependency Python localhost web server (CORS-enabled, port auto-scanning, browser auto-launch, asset serving) exposing REST API endpoints:
  - `GET /api/status`: Engine status, provider, masked API key, benchmark counts.
  - `POST /api/analyze-review`: Runs 6-question speculative fan-out and composite scoring.
  - `POST /api/classify-topic`: Runs multi-dimensional classification and routing policy.
  - `POST /api/custom-decision`: Evaluates arbitrary user-defined state and question schemas.
  - `POST /api/config`: Dynamically updates session keys, execution mode, or provider.
  - `GET /api/history`: Paginated query history with search, action filtering, and detail lookups.
  - `GET /api/history/stats`: Aggregate request counts, success rates, latency averages, and database size.
  - `POST /api/history/clear` & `DELETE /api/history`: Purges logs and compacts disk storage via `VACUUM`.
- **[`start_ui.bat`](./start_ui.bat) / [`start_dashboard.bat`](./start_dashboard.bat):** One-click batch launchers for the web cockpit.
- **[`jev_demo.py`](./jev_demo.py):** Enhanced, production-ready CLI application and Python library:
  - **Demo 1 (Customer Review Analysis):** Speculative fan-out evaluating 6 questions in parallel, weighted composite scoring, and action escalation.
  - **Demo 2 (Topic Classification):** Multi-dimensional classification, property detection, and confidence-gated routing.
  - **CLI Flags:** Custom input evaluation (`--review`, `--topic`, `--product`), structured JSON output (`--json`), multi-provider auto-detection (`--provider {openrouter,typesafe}`), offline mock testing (`--mock`), local history viewer (`--history`), and database cleanup (`--clear-history`).
- **[`jev_demo_README.md`](./jev_demo_README.md):** Detailed guide to Jev decisions, API architecture, CLI usage, personal device storage, and security.
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

## Personal Device Storage & Privacy

All outgoing requests (prompt inputs, application state, typed questions) and incoming responses (answers, composite scores, action decisions, TTFT, and inference latencies) are automatically tracked in a local SQLite database (`jevtools.db`).

- **100% On-Device & Gitignored:** The database file (`jevtools.db`), SQLite journals (`*.db-journal`), and database wildcards (`*.sqlite`, `*.sqlite3`) are strictly added to [`.gitignore`](./.gitignore). Your data, API payloads, and internal evaluations **never leave your local machine** and will never be committed to source control.
- **Zero Dependencies:** Powered by Python's standard `sqlite3` library with WAL (Write-Ahead Logging) mode and thread-safe connections.
- **Inspect via Web UI:** The Cockpit UI includes a dedicated **📜 Request History & Database Structure** tab featuring:
  - **Database Structure & Schema Explorer:** Interactive view of SQLite table schema, PRAGMA metadata, column definitions, data types, nullability, constraints, and indexes.
  - **Structural Column Filter Tool:** Filter across any structural column in the SQLite schema (`id`, `timestamp`, `action_type`, `provider`, `model`, `endpoint`, `status`, `ttft_ms`, `elapsed_ms`, `is_mock`, `request_payload`, `response_payload`, `error_message`, `client_info`) with operators (`=`, `!=`, `contains`, `starts_with`, `ends_with`, `>`, `>=`, `<`, `<=`, `is_null`, `is_not_null`).
  - **Unrestricted Database Viewing by Default:** The Web Cockpit and `GET /api/history` show every request in the database by default (`limit=all`), with selectable page sizes (10, 25, 50, 100, 250, All) and full pagination controls.
  - **Database Structure & Schema Explorer:** Interactive schema card viewer with column metrics (non-null counts, distinct counts, sample values) and click-to-filter support.
  - **Direct Browser Navigation Routes:** Navigate directly to `http://127.0.0.1:8080/database`, `/db`, `/history`, or `/explorer` to jump straight to the database explorer.
  - **Dynamic Quick-Filter Chips & Sorting:** Clickable status/action chips and sortable column headers (`Timestamp`, `Latency`, `Action`, `Status`, `ID`).
  - **Export:** Instant one-click export of filtered records to CSV or formatted JSON.
- **Inspect via CLI:**
  ```powershell
  # View request history table (default: recent 25)
  py jev_demo.py --history

  # View entire database without caps
  py jev_demo.py --history --all

  # Filter by action, status, mode, endpoint, or full-text query
  py jev_demo.py --history --filter-action review_analysis --filter-status success
  py jev_demo.py --history --filter-endpoint openrouter
  py jev_demo.py --history --filter-search "battery" --limit 50

  # Inspect SQLite database schema, columns, datatypes, and indexes
  py jev_demo.py --db-schema

  # Output full matching history records as JSON
  py jev_demo.py --history --all --json

  # Purge all local records and reclaim disk space
  py jev_demo.py --clear-history
  ```
- **No Key Required:** Viewing schema, filtering, or purging history runs directly on your local database without prompting for an API key.

---

## License
MIT
