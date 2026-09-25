# Security Policy & Architecture Guide

JevTools is an open-source reference implementation, local-first web cockpit, and knowledge toolkit for **Jev (TypeSafe System One)** and the **OpenRouter Alpha Decisions API**.

This document outlines the project's security architecture, supported versions, responsible vulnerability disclosure process, threat model, and a comprehensive chronological history of all security enhancements and safeguards implemented in the codebase—including exact code snippets, published dates, and branch links.

---

## 1. Supported Versions & Branch Lifecycle

JevTools follows Semantic Versioning (`MAJOR.MINOR.PATCH`). Active security maintenance is provided for current production releases on the primary branch.

| Version | Status | Published Date | Branch Link | Security Support |
| :--- | :--- | :--- | :--- | :--- |
| **0.1.0** | **Current Release** | 2026-09-25 | [`main`](https://github.com/RileyCarney/JevTools/tree/main) | :white_check_mark: Actively Supported |
| **0.1.0-dev** | Development Preview | 2026-09-22 | [`RileyCarney-Templates`](https://github.com/RileyCarney/JevTools/tree/RileyCarney-Templates) | :warning: Pre-release patches only |
| **0.0.1-alpha** | Knowledge Vault Base | 2026-09-20 | [`list`](https://github.com/RileyCarney/JevTools/tree/list) | :x: End of Life / Historical |

### Version Policy
- **Patch Releases (`0.1.x`)**: Issued immediately for critical or high-severity vulnerabilities (CVSS $\ge 7.0$).
- **Minor Releases (`0.x.0`)**: Scheduled for new capabilities, dependency updates, and architectural security improvements.
- **Branch Tracking**: All production security updates are committed and tagged on the [`main`](https://github.com/RileyCarney/JevTools/tree/main) branch. Pull requests merged from feature branches such as [`RileyCarney-Templates`](https://github.com/RileyCarney/JevTools/tree/RileyCarney-Templates) undergo security audit before landing in `main`.

---

## 2. Reporting a Vulnerability

The JevTools maintainers take the security of this project and its users' personal data seriously. If you discover a vulnerability, please report it privately rather than creating a public GitHub issue.

### How to Report Privately

1. **GitHub Security Advisory (Recommended)**:  
   Navigate to the repository's [Security Advisories tab](https://github.com/RileyCarney/JevTools/security/advisories/new) and submit a private draft advisory.
2. **Direct Maintainer Contact**:  
   If the advisory interface is unavailable, email the maintainer directly:
   - **Contact**: Riley Carney
   - **Email**: `3312970+RileyCarney@users.noreply.github.com`
   - **Subject Line**: `[SECURITY VULNERABILITY] JevTools - <Component / Short Description>`

### Information to Include in Your Report
To accelerate triage and remediation, please include:
- A descriptive summary of the vulnerability and its potential impact.
- Affected component(s) (`jev_demo.py`, `database.py`, `server.py`, `index.html`, etc.).
- Step-by-step instructions or a Minimal Reproducible Example / Proof of Concept (PoC).
- Any observed boundary violations (e.g., secret disclosure, unauthorized file access, SQL injection).
- Proposed fix, mitigation, or remediation suggestions if available.

### Response & Remediation Timelines

```
[Day 0] Discovery & Report Received
   │
   ├─► Within 24-48 Hours : Acknowledgment of receipt and initial review
   │
   ├─► Within 72 Hours    : Triage complete, CVSS v3.1 severity assigned, PoC confirmed
   │
   ├─► Within 7-14 Days   : Patch engineered, unit tests written, release candidate verified
   │
   └─► Release Day        : Security advisory published, release tagged, CVE requested (if applicable)
```

- **Initial Acknowledgment**: Within **24 to 48 hours** of report receipt.
- **Triage & Assessment**: Within **72 hours**, confirming reproducibility and severity.
- **Remediation & Patching**: Typically released within **7 to 14 business days**.
- **Coordinated Disclosure**: We request an embargo period of **30 days** following patch availability to allow users time to update their local installations before full public technical disclosure.

### Safe Harbor Policy
Activities conducted in accordance with this policy are considered authorized. The maintainers will not initiate legal action against individuals who conduct good-faith security research, adhere to responsible disclosure timelines, and do not attempt to access, alter, or destroy user data or degrade system availability.

---

## 3. Threat Model & Security Architecture

JevTools is designed around five core security pillars:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             JEVTOOLS THREAT MODEL                           │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 1. Zero-Trust Credential Security    │ 2. Personal Device Data Sovereignty   │
│    - Multi-tier safe key resolution  │    - 100% on-device SQLite storage   │
│    - Terminal echo suppression       │    - Strict .gitignore git insulation │
│    - Global display key masking      │    - Forensic zeroing via VACUUM     │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 3. Control Inversion & Prompt Defense│ 4. Local Web Server Isolation        │
│    - Deterministic code-level routing│    - Localhost loopback binding only │
│    - Typed outputs (choice/score)    │    - Protected file path blocking    │
│    - No free-form command execution  │    - No-cache & explicit CORS headers│
├──────────────────────────────────────┴──────────────────────────────────────┤
│ 5. Minimal Attack Surface & Supply Chain Defense                            │
│    - Zero external runtime dependencies (Python standard library only)      │
│    - Automated weekly Dependabot manifests auditing                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pillar 1: Zero-Trust Credential & Secret Management
- **Safe Resolution Priority**: Keys are loaded in strict order of safety:
  1. Environment variables (`OPENROUTER_API_KEY`, `TYPESAFE_API_KEY`, `OPENROUTER_KEY`, `JEV_API_KEY`).
  2. Secure interactive prompt using `getpass.getpass()`—suppresses terminal echoing and prevents persistence in shell histories (`.bash_history`, `.zsh_history`, PSReadLine).
  3. CLI argument `--api-key` (produces a high-visibility warning regarding OS process table inspection risk).
- **Secret Masking Everywhere**: `mask_key()` prevents keys from leaking into stdout, console logs, error dumps, database records, and HTTP responses. Keys are rendered as `sk-...` or `ts-...`.
- **Zero-Credit Mock Mode**: Full offline execution (`--mock`) enables automated testing, CI pipelines, and UI inspection without transmitting keys over any network.

### Pillar 2: Personal Device Data Sovereignty & SQLite Storage
- **On-Device Storage**: User queries, evaluations, reviews, classification texts, and model outputs are stored exclusively in `jevtools.db` on the personal device.
- **Git Insulation**: The SQLite database (`jevtools.db`), write-ahead log files (`*.db-journal`), sqlite wildcards (`*.sqlite`, `*.sqlite3`), and secrets files (`.env`, `secrets.json`, `*.pem`) are strictly gitignored to prevent accidental commits to public repositories.
- **SQL Injection Elimination**: All database interactions in `database.py` use parameterized queries (`?` placeholders). No string concatenation or format string injection is permitted.
- **Data Erasure & Compaction**: The `DELETE /api/history` and `clear_history()` routines purge rows and issue an immediate SQLite `VACUUM` to release physical storage and overwrite deleted data from disk pages.

### Pillar 3: Control Inversion & Prompt Injection Resistance
Traditional LLM architectures allow untrusted inputs to dictate workflow and control flow. Jev operates via **Control Inversion**:
- Jev is a System One semantic scorer and router, returning strictly typed judgments (`choice`, `score`, `noul`) with calibrated probability distributions.
- **Application Logic in Code**: Thresholds, fallback branches, actions, and escalation policies reside purely in deterministic Python code. A malicious prompt cannot instruct Jev to bypass routing rules or execute arbitrary commands.

### Pillar 4: Local Web Server & Frontend Isolation
- **Localhost Binding**: `server.py` binds exclusively to `127.0.0.1`, preventing exposure to external networks or LAN interfaces.
- **Path Traversal & File Disclosure Defense**: Static file serving explicitly filters and blocks requests targeting dotfiles (`/.git`, `/.env`), database files (`*.db`, `*.sqlite`), credentials (`*.pem`, `*.key`), and Python source files (`*.py`), returning HTTP `403 Forbidden`.
- **Cache Invalidation**: HTTP responses enforce `Cache-Control: no-cache, no-store, must-revalidate` to prevent proxy or browser disk caching of sensitive state.
- **XSS Prevention**: `index.html` renders dynamic content, API responses, and database logs exclusively via DOM `textContent` APIs rather than `innerHTML` interpolation.

### Pillar 5: Supply Chain & Dependency Hardening
- **Zero Runtime Dependencies**: The core JevTools library (`database.py`, `server.py`, `jev_demo.py`) has zero third-party dependencies at runtime. It runs entirely on the standard Python 3.10+ library.
- **Development Dependency Isolation**: Optional test and lint dependencies (`pytest`, `ruff`) are isolated in `pyproject.toml` and monitored weekly via `.github/dependabot.yml`.

---

## 4. In-Scope vs. Out-of-Scope Vulnerabilities

| Classification | Examples (In-Scope) | Examples (Out-of-Scope) |
| :--- | :--- | :--- |
| **Authentication & Secrets** | Key leakage in logs, unmasked keys in APIs, credential retention in files | User intentionally sharing their personal API key |
| **Data Storage & Injection** | SQL injection in `database.py`, path traversal in `server.py`, file disclosure | Direct physical tampering with `jevtools.db` on unlocked machine |
| **Web Server & UI** | Cross-Site Scripting (XSS) in cockpit, CORS escalation, SSRF | Localhost denial of service by overloading local port |
| **Supply Chain** | Vulnerable pinned development dependencies, malicious build scripts | Upstream service outages (OpenRouter / TypeSafe downtime) |
| **Model Judgment** | Prompt injection altering deterministic control flow | Probabilistic variance inherent to LLM classification |

---

## 5. Chronological History of Security Changes & Code Implementations

The following timeline details all security-relevant architectural changes, bug fixes, hardening measures, and commits applied to the codebase from repository inception to the current version.

### Summary Table of Security Milestones

| Published Date & Time | Commit Hash | Branch | Component | Security Focus |
| :--- | :--- | :--- | :--- | :--- |
| **2026-09-20 20:26:47 -07:00** | [`35c9496`](https://github.com/RileyCarney/JevTools/commit/35c9496720cc6c2f27546c5f75211922f2d6e0ee) | [`main`](https://github.com/RileyCarney/JevTools/tree/main) | `.gitignore` | Initial repository file exclusion policy |
| **2026-09-20 22:09:55 -07:00** | [`36ebc76`](https://github.com/RileyCarney/JevTools/commit/36ebc76c37a924b9e61a21684e47a8dca38b1fa8) | [`main`](https://github.com/RileyCarney/JevTools/tree/main) | `SECURITY.md` | Initial security policy creation |
| **2026-09-22 00:49:05 -07:00** | [`d0f8224`](https://github.com/RileyCarney/JevTools/commit/d0f82248f63774ff2c52515988b6c9f5b5d3eb41) | [`RileyCarney-Templates`](https://github.com/RileyCarney/JevTools/tree/RileyCarney-Templates) | `jev_demo.py`, `server.py`, `.gitignore` | Secret masking, safe key resolution, no-cache headers |
| **2026-09-23 23:16:43 -07:00** | [`e95b547`](https://github.com/RileyCarney/JevTools/commit/e95b5471124221650510f7217ce2f0ba1b465d59) | [`main`](https://github.com/RileyCarney/JevTools/tree/main) | `.gitignore` | Workspace config insulation |
| **2026-09-25 00:32:14 -07:00** | [`8221329`](https://github.com/RileyCarney/JevTools/commit/8221329530ef3fa5fbbf70d9c0f6f390f3b354a8) | [`main`](https://github.com/RileyCarney/JevTools/tree/main) | `.github/dependabot.yml` | Automated weekly dependency vulnerability scanning |
| **2026-09-25 01:10:04 -07:00** | [`f3e817a`](https://github.com/RileyCarney/JevTools/commit/f3e817a7e9b0396ebe715bcbc1ee65f31a083fb4) | [`main`](https://github.com/RileyCarney/JevTools/tree/main) | `database.py`, `server.py`, `index.html` | Parameterized SQL, WAL mode, database gitignore, XSS protection |
| **2026-09-25 01:13:50 -07:00** | [`a88e0fc`](https://github.com/RileyCarney/JevTools/commit/a88e0fcdd5403049e5ea4cf2e4a21b1b91c6beb6) | [`main`](https://github.com/RileyCarney/JevTools/tree/main) | `pyproject.toml`, `requirements.txt` | Zero external runtime dependency footprint |
| **2026-09-25 (Current)** | Local Hardening | [`main`](https://github.com/RileyCarney/JevTools/tree/main) | `server.py`, `tests/test_server.py` | Local static file disclosure protection (403 Forbidden) |

---

### Detailed Code Evolution & Security Implementations

#### 1. Repository Insulation & Credential Leak Prevention
- **Published Date**: 2026-09-20 20:26:47 -07:00
- **Commit**: [`35c9496720cc6c2f27546c5f75211922f2d6e0ee`](https://github.com/RileyCarney/JevTools/commit/35c9496720cc6c2f27546c5f75211922f2d6e0ee)
- **Branch**: [`main`](https://github.com/RileyCarney/JevTools/tree/main)
- **Problem**: Accidental staging of environment variables, certificates, or credentials.
- **Code Change (`.gitignore`)**:
```gitignore
# Environment & Secrets
.env
.env.*
!.env.example
*.pem
secrets.json
```

---

#### 2. Safe Secret Resolution Hierarchy & Process Table Defense
- **Published Date**: 2026-09-22 00:49:05 -07:00
- **Commit**: [`d0f82248f63774ff2c52515988b6c9f5b5d3eb41`](https://github.com/RileyCarney/JevTools/commit/d0f82248f63774ff2c52515988b6c9f5b5d3eb41)
- **Branch**: [`RileyCarney-Templates`](https://github.com/RileyCarney/JevTools/tree/RileyCarney-Templates)
- **Problem**: Passing API tokens as command-line arguments exposes them in OS process listings (`ps aux`, Task Manager) and shell history files.
- **Code Implementation ([`jev_demo.py`](https://github.com/RileyCarney/JevTools/blob/main/jev_demo.py#L1457-L1508))**:
```python
def resolve_api_key(cli_key: Optional[str], mock: bool = False, allow_fallback: bool = False) -> str:
    """
    Return the API key using the safest available source:
      1. OPENROUTER_API_KEY, TYPESAFE_API_KEY, or OPENROUTER_KEY env var
      2. Interactive getpass prompt (never echoed to terminal or history)
      3. --api-key CLI argument (accepted, but warns loudly about process table exposure)
    """
    if mock:
        return "mock-key-for-testing"

    # 1. Environment variables - preferred for automated use
    for env_var in ("OPENROUTER_API_KEY", "TYPESAFE_API_KEY", "OPENROUTER_KEY", "JEV_API_KEY"):
        val = os.environ.get(env_var, "").strip()
        if val:
            return val

    # 2. Interactive secure prompt - preferred in terminal (no echo)
    if sys.stdin.isatty() and not allow_fallback:
        try:
            print("\n[?] No OPENROUTER_API_KEY or TYPESAFE_API_KEY environment variable detected.")
            prompted = getpass.getpass("Enter your OpenRouter or TypeSafe API key: ").strip()
            if prompted:
                return prompted
        except (KeyboardInterrupt, EOFError):
            sys.exit("\nAborted.")

    # 3. CLI argument - accepted with loud security warning
    if cli_key and cli_key.strip():
        print(
            "\n[!] SECURITY WARNING: Passing secrets via CLI arguments exposes them in the OS "
            "process table (ps aux, Task Manager) and shell history. Prefer setting the "
            "OPENROUTER_API_KEY environment variable or using the interactive prompt.",
            file=sys.stderr,
        )
        return cli_key
```

---

#### 3. Complete API Key Display Masking
- **Published Date**: 2026-09-22 00:49:05 -07:00
- **Commit**: [`d0f82248f63774ff2c52515988b6c9f5b5d3eb41`](https://github.com/RileyCarney/JevTools/commit/d0f82248f63774ff2c52515988b6c9f5b5d3eb41)
- **Branch**: [`RileyCarney-Templates`](https://github.com/RileyCarney/JevTools/tree/RileyCarney-Templates)
- **Problem**: API keys inadvertently logged to terminal outputs, error messages, or transmitted in plain text to web dashboards.
- **Code Implementation ([`jev_demo.py`](https://github.com/RileyCarney/JevTools/blob/main/jev_demo.py#L781-L795))**:
```python
def mask_key(key: str) -> str:
    """Mask an API key for safe console display and API responses."""
    clean = (key or "").strip()
    if not clean:
        return "[NOT SET]"
    if clean.startswith("mock-") or clean == "mock-key-for-testing":
        return "[MOCK MODE - NO KEY USED]"
    if clean.startswith("sk-"):
        return "sk-..."
    if clean.startswith("ts-"):
        return "ts-..."
    if len(clean) <= 12:
        return "*" * len(clean)
    return f"{clean[:10]}...{clean[-4:]}"
```

---

#### 4. Automated Supply Chain Monitoring via Dependabot
- **Published Date**: 2026-09-25 00:32:14 -07:00
- **Commit**: [`8221329530ef3fa5fbbf70d9c0f6f390f3b354a8`](https://github.com/RileyCarney/JevTools/commit/8221329530ef3fa5fbbf70d9c0f6f390f3b354a8)
- **Branch**: [`main`](https://github.com/RileyCarney/JevTools/tree/main)
- **Problem**: Unmonitored dependencies can harbor known CVEs or supply chain compromises.
- **Code Implementation ([`.github/dependabot.yml`](https://github.com/RileyCarney/JevTools/blob/main/.github/dependabot.yml#L1-L13))**:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

---

#### 5. SQL Injection Prevention & Parameterized Queries
- **Published Date**: 2026-09-25 01:10:04 -07:00
- **Commit**: [`f3e817a7e9b0396ebe715bcbc1ee65f31a083fb4`](https://github.com/RileyCarney/JevTools/commit/f3e817a7e9b0396ebe715bcbc1ee65f31a083fb4)
- **Branch**: [`main`](https://github.com/RileyCarney/JevTools/tree/main)
- **Problem**: User-provided strings (review text, topic paragraphs, action types) could lead to SQL injection if formatted directly into database queries.
- **Code Implementation ([`database.py`](https://github.com/RileyCarney/JevTools/blob/main/database.py#L137-L163))**:
```python
# Thread-safe insertion using parameterized placeholders
cursor.execute("""
    INSERT INTO request_logs (
        timestamp, action_type, provider, model, endpoint,
        status, ttft_ms, elapsed_ms, is_mock,
        request_payload, response_payload, error_message, client_info
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
""", (
    timestamp, action_type, provider or "openrouter",
    model or "", endpoint or "", status,
    float(ttft_ms or 0.0), float(elapsed_ms or 0.0),
    1 if is_mock else 0,
    req_json, resp_json, err_str, client_info or "unknown",
))

# Filtered search using parameterized query building
query = "SELECT * FROM request_logs WHERE 1=1"
params = []
if action_type:
    query += " AND action_type = ?"
    params.append(action_type)
if search:
    query += " AND (request_payload LIKE ? OR response_payload LIKE ? OR error_message LIKE ?)"
    wildcard = f"%{search}%"
    params.extend([wildcard, wildcard, wildcard])
query += " ORDER BY id DESC LIMIT ? OFFSET ?"
params.extend([max(1, limit), max(0, offset)])
cursor.execute(query, params)
```

---

#### 6. Personal Device Data Isolation & Git Exclusion
- **Published Date**: 2026-09-25 01:10:04 -07:00
- **Commit**: [`f3e817a7e9b0396ebe715bcbc1ee65f31a083fb4`](https://github.com/RileyCarney/JevTools/commit/f3e817a7e9b0396ebe715bcbc1ee65f31a083fb4)
- **Branch**: [`main`](https://github.com/RileyCarney/JevTools/tree/main)
- **Problem**: Committing local SQLite databases leaks internal prompts, confidential reviews, and user queries to remote git repos.
- **Code Change ([`.gitignore`](https://github.com/RileyCarney/JevTools/blob/main/.gitignore#L36-L44))**:
```gitignore
# Local SQLite Database & Personal User Data Store
*.db
*.db-journal
*.sqlite
*.sqlite3
data/
jevtools.db
```

---

#### 7. Forensic Data Erasure & Storage Compaction via `VACUUM`
- **Published Date**: 2026-09-25 01:10:04 -07:00
- **Commit**: [`f3e817a7e9b0396ebe715bcbc1ee65f31a083fb4`](https://github.com/RileyCarney/JevTools/commit/f3e817a7e9b0396ebe715bcbc1ee65f31a083fb4)
- **Branch**: [`main`](https://github.com/RileyCarney/JevTools/tree/main)
- **Problem**: Simply executing `DELETE FROM table;` leaves deleted payload fragments on unallocated SQLite disk pages.
- **Code Implementation ([`database.py`](https://github.com/RileyCarney/JevTools/blob/main/database.py#L241-L264))**:
```python
def clear_history(db_path: Optional[str] = None) -> int:
    """Clear all request/response history and reclaim disk space via VACUUM."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM request_logs;")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM request_logs;")

    # VACUUM runs in autocommit to wipe residual data pages and shrink the database
    path = db_path or get_default_db_path()
    if os.path.exists(path):
        vac_conn = sqlite3.connect(path, isolation_level=None, timeout=15.0)
        try:
            vac_conn.execute("VACUUM;")
        finally:
            vac_conn.close()

    return count
```

---

#### 8. DOM XSS Elimination in Web Cockpit
- **Published Date**: 2026-09-25 01:10:04 -07:00
- **Commit**: [`f3e817a7e9b0396ebe715bcbc1ee65f31a083fb4`](https://github.com/RileyCarney/JevTools/commit/f3e817a7e9b0396ebe715bcbc1ee65f31a083fb4)
- **Branch**: [`main`](https://github.com/RileyCarney/JevTools/tree/main)
- **Problem**: Dynamic rendering of user review text, topic strings, error messages, and raw JSON payloads using `innerHTML` creates Cross-Site Scripting sinks.
- **Code Implementation ([`index.html`](https://github.com/RileyCarney/JevTools/blob/main/index.html#L3648-L3677))**:
```javascript
function displayPayloadModal(item) {
    // Safe text injection prevents HTML and script execution
    document.getElementById('pm-id').textContent = `#${item.id}`;
    document.getElementById('pm-time').textContent = item.timestamp ? new Date(item.timestamp).toLocaleString() : '--';
    document.getElementById('pm-action').textContent = item.action_type;
    document.getElementById('pm-provider').textContent = item.provider || 'openrouter';
    document.getElementById('pm-model').textContent = item.model || 'default';

    if (item.error_message) {
        document.getElementById('pm-error-banner').style.display = 'block';
        document.getElementById('pm-error-msg').textContent = item.error_message;
    }

    // Preformatted code blocks populated safely with stringified JSON
    document.getElementById('pm-req-code').textContent = JSON.stringify(item.request_payload, null, 2);
    document.getElementById('pm-resp-code').textContent = JSON.stringify(item.response_payload, null, 2);
}
```

---

#### 9. Zero Runtime External Dependencies
- **Published Date**: 2026-09-25 01:13:50 -07:00
- **Commit**: [`a88e0fcdd5403049e5ea4cf2e4a21b1b91c6beb6`](https://github.com/RileyCarney/JevTools/commit/a88e0fcdd5403049e5ea4cf2e4a21b1b91c6beb6)
- **Branch**: [`main`](https://github.com/RileyCarney/JevTools/tree/main)
- **Problem**: Transitive dependencies introduce vulnerability risks, package hijacking vectors, and typosquatting threats.
- **Code Configuration ([`pyproject.toml`](https://github.com/RileyCarney/JevTools/blob/main/pyproject.toml#L23-L29))**:
```toml
[project]
name = "jevtools"
version = "0.1.0"
requires-python = ">=3.10"
license = {text = "GPL-3.0-or-later"}
dependencies = []  # Zero external runtime dependencies

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.3.0",
]
```

---

#### 10. Local Static File Disclosure Protection
- **Published Date**: 2026-09-25 (Hardening)
- **Branch**: [`main`](https://github.com/RileyCarney/JevTools/tree/main)
- **Problem**: Python's `SimpleHTTPRequestHandler` serves arbitrary files in the working directory if unconstrained, risking exposure of `.git`, `jevtools.db`, `.env`, or Python source files.
- **Code Implementation ([`server.py`](https://github.com/RileyCarney/JevTools/blob/main/server.py#L192-L203))**:
```python
# Block access to hidden files, databases, credentials, and source files
clean_path = urllib.parse.unquote(path).strip()
lower_path = clean_path.lower()
if (
    lower_path.startswith("/.")
    or "/." in lower_path
    or any(lower_path.endswith(ext) for ext in (".db", ".db-journal", ".sqlite", ".sqlite3", ".env", ".pem", ".key", ".py"))
):
    self._send_json_error("Forbidden: access to protected file or directory is restricted", status=403)
    return
```

---

## 6. Repository Branch & Version Links

All security-related history is tied directly to the repository branch structure:

- **[`main` Branch](https://github.com/RileyCarney/JevTools/tree/main)**:  
  The production release branch containing the fully hardened zero-dependency engine, database audit logger, web cockpit, and test suite.  
  - Current Head: [`a88e0fc`](https://github.com/RileyCarney/JevTools/commit/a88e0fcdd5403049e5ea4cf2e4a21b1b91c6beb6)
- **[`RileyCarney-Templates` Branch](https://github.com/RileyCarney/JevTools/tree/RileyCarney-Templates)**:  
  The initial demo development branch where the CLI decision engine, secret resolution hierarchy, and mock mode were first introduced.  
  - Branch Head: [`d0f8224`](https://github.com/RileyCarney/JevTools/commit/d0f82248f63774ff2c52515988b6c9f5b5d3eb41)
- **[`list` Branch](https://github.com/RileyCarney/JevTools/tree/list)**:  
  Exploratory branch containing skill documents and architecture blueprints.  
  - Branch Head: [`ba6bced`](https://github.com/RileyCarney/JevTools/commit/ba6bced346a1fc2348f58c86ab3f86c6fb47ffdb)

---

## 7. Security Best Practices for Operators

1. **Protect Environment Secrets**: Store your `OPENROUTER_API_KEY` in your private user profile or shell configuration (`$env:OPENROUTER_API_KEY` or `export OPENROUTER_API_KEY`). Avoid setting API keys in shared scripts or commit history.
2. **Localhost Isolation**: Do not bind `server.py` to `0.0.0.0` or expose the dashboard port to untrusted public networks without adding an authenticating reverse proxy (e.g., Caddy or Nginx with TLS and HTTP Basic Auth).
3. **Database Permissions**: Ensure the file permissions on `jevtools.db` restrict read/write access exclusively to the operating system user executing the service.
4. **Regular Dependency Audits**: Maintainers and contributors should routinely run `pip audit` and monitor automated Dependabot alerts for development tooling.
