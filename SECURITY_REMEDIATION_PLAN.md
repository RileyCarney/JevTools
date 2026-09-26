# JevTools Security Remediation Plan

> **Generated**: 2026-09-25 | **Analyst**: Senior Security Advisor (Antigravity)  
> **Scope**: Full codebase audit — `server.py`, `database.py`, `jev_demo.py`, `index.html`, `.github/`  
> **Methodology**: Static analysis, code pattern review, threat model mapping

---

## Executive Summary

The JevTools codebase has a solid security foundation — parameterized SQL, key masking, gitignored secrets, and `.py` file blocking are all present and correctly implemented. However, **10 confirmed vulnerabilities** and **3 best-practice gaps** were identified. The most severe is a **server binding to all network interfaces** (`0.0.0.0`) instead of loopback only, which directly contradicts the project's own threat model and `SECURITY.md` documentation. The second most impactful is a cluster of **Cross-Site Scripting (XSS) vulnerabilities** in `index.html` where API response data from the server (which includes user-supplied content stored in the SQLite database) is injected into the DOM via `innerHTML` without HTML sanitization.

---

## Vulnerability Index

| # | ID | Severity | Component | Title |
|---|---|---|---|---|
| 1 | VUL-001 | 🔴 **HIGH** | `server.py:423` | Server binds to all interfaces (`""` = `0.0.0.0`) |
| 2 | VUL-002 | 🔴 **HIGH** | `index.html:2828,2933,3042,3138,3144,3577` | Stored XSS via `innerHTML` injection of server response data |
| 3 | VUL-003 | 🟠 **MEDIUM** | `server.py:100` | Overly permissive CORS (`Access-Control-Allow-Origin: *`) |
| 4 | VUL-004 | 🟠 **MEDIUM** | `server.py:122-125` | No maximum request body size limit (DoS vector) |
| 5 | VUL-005 | 🟠 **MEDIUM** | `server.py:377-378` | Unbounded benchmark `runs` parameter |
| 6 | VUL-006 | 🟠 **MEDIUM** | `jev_demo.py:126,130` | SSRF: user-controlled `JEV_API_URL` env var and `--endpoint` CLI arg |
| 7 | VUL-007 | 🟡 **LOW** | `server.py:99-104` | Missing hardening HTTP response headers (CSP, X-Frame-Options, X-Content-Type-Options) |
| 8 | VUL-008 | 🟡 **LOW** | `server.py:226-234` | Path traversal filter bypassable via edge cases |
| 9 | VUL-009 | 🟡 **LOW** | `jev_demo.py:564-570` | No explicit `verify=True` / `allow_redirects=False` on HTTP requests |
| 10 | VUL-010 | 🟡 **LOW** | `database.py:190-192` | Search parameter has no maximum length limit |
| 11 | GAP-001 | ℹ️ **INFO** | `server.py` | Default request logging exposes query strings to stdout |
| 12 | GAP-002 | ℹ️ **INFO** | `.github/dependabot.yml` | Dependabot only scans pip; GitHub Actions not monitored |
| 13 | GAP-003 | ℹ️ **INFO** | `server.py` | `allow_reuse_address` not explicitly set — port rebind race on restart |

---

## Detailed Findings & Remediation Steps

---

### VUL-001 — 🔴 HIGH: Server Binds to All Network Interfaces

**File**: `server.py`, line 423  
**CVSS v3.1**: 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)

**Description**  
The `TCPServer` is instantiated with an empty string `""` as the host, which Python resolves to `0.0.0.0` — binding to **all network interfaces** including LAN, Wi-Fi, and any VPN adapters. This directly contradicts the project's documented threat model in `SECURITY.md` (Pillar 4: "Localhost Binding: server.py binds exclusively to `127.0.0.1`").

**Current Vulnerable Code** (`server.py:423`):
```python
with socketserver.TCPServer(("", port), handler) as httpd:
```

**Impact**  
Any machine on the same network (LAN, café Wi-Fi, VPN) can access the JevTools dashboard. Combined with:
- `/api/config` which accepts and stores API keys in the server's runtime state
- `/api/custom-decision` which proxies arbitrary user state to the Jev API using the stored key

This constitutes a **remote API key theft** and **remote credit abuse** vector on shared networks.

**Fix**:
```python
# server.py line 423
with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
```

**Verification**: `netstat -an | findstr 8089` must show `127.0.0.1:8089`, NOT `0.0.0.0:8089`.

---

### VUL-002 — 🔴 HIGH: Stored XSS via `innerHTML` Injection

**File**: `index.html`  
**Affected Lines**: 2828–2836, 2933–2941, 3042–3056, 3138, 3144, 3577–3622  
**CVSS v3.1**: 7.4 (AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N)

**Description**  
Multiple locations in `index.html` interpolate data from API responses — which ultimately originates from user-controlled inputs stored in the SQLite database — directly into `innerHTML` template literals without HTML escaping. This is a **Stored XSS** vector.

**Attack Chain**:
1. User submits a review containing `<img src=x onerror="alert(1)">` via `/api/analyze-review`
2. The payload is stored in `jevtools.db` as `request_payload`
3. When the History table loads, `tbody.innerHTML` renders database fields directly as raw HTML
4. The injected script executes in the browser context of the dashboard

**Specific Vulnerable Patterns**:

```javascript
// Line 2828 — Tone distribution: emotion_probabilities keys from API
distContainer.innerHTML += `<span class="dist-label">${tone}</span>`;  // UNSAFE

// Line 2933 — Topic probability chart: topic names from API
chart.innerHTML += `<span class="dist-label">${topic}</span>`;  // UNSAFE

// Line 3042 — Hub module card
card.innerHTML = `<div class="project-title">${mod.title}</div>`;  // UNSAFE pattern

// Line 3138 — Modal features list
featUl.innerHTML = mod.features.map(f => `<li>${f}</li>`).join('');  // UNSAFE

// Line 3144 — Modal web service links (href injection possible)
webDiv.innerHTML = `<a href="${w.url}" ...>🌐 Launch ${w.name}</a>`;  // UNSAFE

// Lines 3577–3622 — History table (MOST DANGEROUS: DB data → innerHTML)
tbody.innerHTML = items.map(item => `
    <td>${item.provider}</td>   // UNSAFE: stored in DB from user input
    <td>${item.model}</td>      // UNSAFE
`).join('');
```

**Fix — Step 1**: Add this shared escaping utility near the top of the `<script>` block:

```javascript
/**
 * Escape a string for safe interpolation into HTML innerHTML.
 * MUST be applied to ALL server-sourced or user-sourced values before innerHTML use.
 */
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
```

**Fix — Step 2**: Apply `escapeHtml()` to every interpolated value from server/DB data:

```javascript
// Line 2830 — FIXED:
`<span class="dist-label">${escapeHtml(tone)}</span>`

// Line 2935 — FIXED:
`<span class="dist-label">${escapeHtml(topic)}</span>`

// Lines 3050–3052 — FIXED:
`<div class="project-title">${escapeHtml(mod.title)}</div>`
`<p class="project-desc">${escapeHtml(mod.desc)}</p>`

// Line 3138 — FIXED:
featUl.innerHTML = mod.features.map(f => `<li>${escapeHtml(f)}</li>`).join('');

// Line 3144 — FIXED (also validate URL scheme):
const safeUrl = (w.url || '').startsWith('https://') ? w.url : '#';
`<a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer" ...>
    🌐 Launch ${escapeHtml(w.name)}
</a>`

// Lines 3605–3614 — FIXED (history table — highest priority):
const providerModel = `${escapeHtml(item.provider || 'openrouter')} / ${escapeHtml(item.model || 'default')}`;
// Apply escapeHtml() to dateStr, actionLabel, ttftStr, latStr, and providerModel in table rows
```

**Fix — Step 3**: Add `rel="noopener noreferrer"` to all existing `target="_blank"` links (prevents tab-napping).

---

### VUL-003 — 🟠 MEDIUM: Overly Permissive CORS Header

**File**: `server.py`, lines 100–102  
**CVSS v3.1**: 5.3 (AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)

**Description**  
`Access-Control-Allow-Origin: *` is sent on every response. Any webpage opened in the browser can make cross-origin requests to the localhost API and read responses — meaning a malicious page the user visits can silently read `/api/status` (which exposes provider config), or POST to `/api/config` to overwrite runtime state.

**Current Code** (`server.py:100`):
```python
self.send_header("Access-Control-Allow-Origin", "*")
```

**Fix** — replace the wildcard with an explicit localhost origin allowlist:
```python
_ALLOWED_CORS_ORIGINS = {
    f"http://localhost:{DEFAULT_PORT}",
    f"http://127.0.0.1:{DEFAULT_PORT}",
    "null",  # file:// origin (opening HTML directly)
}

# In end_headers():
origin = self.headers.get("Origin", "")
cors_origin = origin if origin in _ALLOWED_CORS_ORIGINS else f"http://localhost:{DEFAULT_PORT}"
self.send_header("Access-Control-Allow-Origin", cors_origin)
self.send_header("Vary", "Origin")
```

---

### VUL-004 — 🟠 MEDIUM: No Maximum Request Body Size (DoS Vector)

**File**: `server.py`, lines 121–125  
**CVSS v3.1**: 5.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)

**Description**  
`_parse_json_body()` reads exactly `Content-Length` bytes with no upper bound. A request with `Content-Length: 104857600` causes a 100 MB memory allocation attempt, exhausting RAM and hanging the server thread.

**Current Code**:
```python
def _parse_json_body(self) -> dict[str, Any]:
    content_length = int(self.headers.get("Content-Length", 0))
    if content_length <= 0:
        return {}
    body = self.rfile.read(content_length).decode("utf-8")  # No limit!
```

**Fix**:
```python
MAX_REQUEST_BODY_BYTES = 1 * 1024 * 1024  # 1 MB — far exceeds any legitimate Jev payload

def _parse_json_body(self) -> dict[str, Any]:
    try:
        content_length = int(self.headers.get("Content-Length", 0))
    except (ValueError, TypeError):
        return {}
    if content_length <= 0:
        return {}
    if content_length > MAX_REQUEST_BODY_BYTES:
        raise ValueError(
            f"Request body too large: {content_length} bytes "
            f"(maximum: {MAX_REQUEST_BODY_BYTES} bytes)"
        )
    body = self.rfile.read(content_length).decode("utf-8")
    ...
```

---

### VUL-005 — 🟠 MEDIUM: Unbounded Benchmark `runs` Parameter

**File**: `server.py`, lines 377–378  
**CVSS v3.1**: 5.0 (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)

**Description**  
The `runs` parameter is accepted from user input with no upper bound. `POST /api/benchmark-ttft` with `{"runs": 10000}` issues 10,000 live HTTP requests to OpenRouter using the user's API key, consuming credits and hanging the server thread.

**Current Code** (`server.py:377-378`):
```python
raw_runs = body.get("runs")
runs = int(raw_runs) if isinstance(raw_runs, (int, str, float)) else 3
```

**Fix**:
```python
MAX_BENCHMARK_RUNS = 10  # Generous upper bound for any legitimate latency test

raw_runs = body.get("runs")
try:
    runs = max(1, min(MAX_BENCHMARK_RUNS, int(raw_runs))) if raw_runs is not None else 3
except (ValueError, TypeError):
    runs = 3
```

---

### VUL-006 — 🟠 MEDIUM: SSRF via User-Controlled Endpoint URL

**File**: `jev_demo.py`, lines 126, 130  
**CVSS v3.1**: 5.8 (AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N)

**Description**  
The `endpoint` parameter is user-controllable via the `JEV_API_URL` environment variable and the `--endpoint` CLI argument. A malicious or misconfigured value can redirect all Jev API calls — including those carrying the real API key in the `Authorization` header — to an attacker-controlled server.

**Current Code** (`jev_demo.py:126, 130`):
```python
ep = endpoint or os.environ.get("JEV_API_URL", TYPESAFE_API_URL)
ep = endpoint or os.environ.get("JEV_API_URL", OPENROUTER_API_URL)
```

**Fix** — Add endpoint validation with an allowlist in `get_provider_config`:
```python
import urllib.parse
import warnings

_ALLOWED_API_HOSTS: frozenset[str] = frozenset({
    "openrouter.ai",
    "api.typesafe.ai",
})

def _validate_endpoint(url: str, provider: str) -> str:
    """Validate that an API endpoint URL points only to an approved host."""
    default = TYPESAFE_API_URL if provider == "typesafe" else OPENROUTER_API_URL
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("https", "http"):
            raise ValueError(f"Scheme must be https or http, got: {parsed.scheme!r}")
        if parsed.hostname not in _ALLOWED_API_HOSTS:
            raise ValueError(
                f"Host {parsed.hostname!r} is not in the allowlist {_ALLOWED_API_HOSTS}"
            )
    except Exception as exc:
        warnings.warn(
            f"[SECURITY] Endpoint URL rejected ({exc}); using default: {default}",
            stacklevel=3,
        )
        return default
    return url
```

Call `ep = _validate_endpoint(ep, prov)` at the end of `get_provider_config()` before the `return` statement.

---

### VUL-007 — 🟡 LOW: Missing Hardening HTTP Response Headers

**File**: `server.py`, lines 99–104  
**CVSS v3.1**: 3.7 (AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N)

**Description**  
The server is missing the following standard security headers:
- `Content-Security-Policy` — limits what scripts/resources can execute, mitigating XSS impact
- `X-Content-Type-Options: nosniff` — prevents MIME-type confusion attacks
- `X-Frame-Options: DENY` — prevents clickjacking via iframe embedding
- `Referrer-Policy: no-referrer` — prevents internal URLs from leaking in referrer headers

**Fix** — extend `end_headers()` in `server.py`:
```python
def end_headers(self) -> None:
    # CORS (from VUL-003 fix)
    self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
    # Security hardening headers
    self.send_header("X-Content-Type-Options", "nosniff")
    self.send_header("X-Frame-Options", "DENY")
    self.send_header("Referrer-Policy", "no-referrer")
    self.send_header(
        "Content-Security-Policy",
        # unsafe-inline required while <script>/<style> are inline in index.html
        # Future: extract to separate files and use a strict CSP nonce
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https://repository-images.githubusercontent.com; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    super().end_headers()
```

> **Note**: The `unsafe-inline` directives are a temporary necessity. Once the inline `<script>` and `<style>` blocks in `index.html` are extracted to separate `.js` and `.css` files, a strict CSP with a per-request nonce can be applied, which would fully neutralize inline XSS.

---

### VUL-008 — 🟡 LOW: Path Traversal Filter Bypassable via Edge Cases

**File**: `server.py`, lines 226–234  
**CVSS v3.1**: 4.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)

**Description**  
The current path filtering uses string matching on the URL-decoded path. Edge case bypasses include:
1. **Missing extension coverage**: `pyproject.toml` and `pyright_output.json` are currently accessible
2. **Symlink attacks**: A symlink inside the served directory pointing outside could escape the filter
3. **Null-byte injection**: `/server.py%00.jpg` — null byte after the extension changes the suffix check

**Current Code** (`server.py:226-234`):
```python
clean_path = urllib.parse.unquote(path).strip()
lower_path = clean_path.lower()
if (
    lower_path.startswith("/.")
    or "/." in lower_path
    or any(lower_path.endswith(ext) for ext in (".db", ".db-journal", ".sqlite", ".sqlite3", ".env", ".pem", ".key", ".py"))
):
```

**Fix** — replace with `pathlib`-based containment check:
```python
import pathlib

_BLOCKED_EXTENSIONS: frozenset[str] = frozenset({
    ".db", ".db-journal", ".db-shm", ".db-wal",
    ".sqlite", ".sqlite3",
    ".env", ".pem", ".key", ".crt",
    ".py", ".pyi", ".pyc",
    ".toml", ".cfg", ".ini",
    ".bat", ".sh", ".ps1",
})
_ALLOWED_DIR: pathlib.Path = pathlib.Path(CURRENT_DIR).resolve()

def _is_safe_path(self, raw_path: str) -> bool:
    """Return True only if the path resolves inside CURRENT_DIR and is not a blocked type."""
    # Strip null bytes to prevent null-byte injection
    decoded = urllib.parse.unquote(raw_path).replace("\x00", "")
    lower = decoded.lower()
    # Block dotfiles and dotdirs
    if lower.startswith("/.") or "/." in lower:
        return False
    # Block sensitive extensions
    suffix = pathlib.PurePosixPath(lower).suffix
    if suffix in _BLOCKED_EXTENSIONS:
        return False
    # Resolve and verify the actual path stays inside the served directory
    try:
        resolved = (_ALLOWED_DIR / decoded.lstrip("/")).resolve()
        resolved.relative_to(_ALLOWED_DIR)  # raises ValueError if outside
    except (ValueError, OSError):
        return False
    return True
```

Replace the existing block check in `do_GET` with:
```python
if not self._is_safe_path(path):
    self._send_json_error("Forbidden: access to protected file or directory is restricted", status=403)
    return
```

> **Important**: Adding `.toml` and `.json` to the blocked list will also block `pyright_output.json`. Move any config/output JSON files out of the served directory, or whitelist them explicitly.

---

### VUL-009 — 🟡 LOW: No Explicit SSL Verification / Redirect Control

**File**: `jev_demo.py`, lines 564–570 and 719  
**CVSS v3.1**: 3.7 (AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)

**Description**  
`requests.post()` does not explicitly set `verify=True` or `allow_redirects=False`. While `requests` defaults to `verify=True`, explicit declaration protects against environment variables (`REQUESTS_CA_BUNDLE=""`) silently degrading certificate verification. Without `allow_redirects=False`, a server-side redirect could forward the `Authorization: Bearer <api_key>` header to a different host.

**Current Code** (`jev_demo.py:564-570`):
```python
with requests.post(
    url=url,
    headers=_build_headers(api_key, provider=prov),
    json=payload,
    stream=True,
    timeout=60,
) as resp:
```

**Fix** — add explicit security parameters:
```python
with requests.post(
    url=url,
    headers=_build_headers(api_key, provider=prov),
    json=payload,
    stream=True,
    timeout=60,
    verify=True,           # Explicitly enforce TLS certificate verification
    allow_redirects=False, # Prevent SSRF via redirect chains leaking the auth header
) as resp:
```

Apply the same to the fallback `requests.get()` call in `measure_openrouter_ttft()` at line 719.

---

### VUL-010 — 🟡 LOW: Unbounded Database Search Parameter

**File**: `database.py`, lines 189–192 and `server.py`, line 202  
**CVSS v3.1**: 3.1 (AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:L)

**Description**  
The `search` parameter is used in a `LIKE '%<term>%'` query with no length limit. A very long search string causes a resource-intensive full-text scan on all three payload columns. The existing parameterized query prevents SQL injection — this is purely a resource exhaustion concern.

**Fix — `server.py` (input layer)**:
```python
search_list = query_params.get("search")
raw_search = search_list[0] if search_list else None
search = raw_search[:200] if raw_search else None  # Cap at 200 characters
```

**Fix — `database.py` (defense in depth)**:
```python
_MAX_SEARCH_LENGTH = 200
_MAX_QUERY_LIMIT = 500

def get_history(limit: int = 50, offset: int = 0, ..., search: Optional[str] = None, ...) -> list[dict[str, Any]]:
    limit = min(max(1, limit), _MAX_QUERY_LIMIT)
    if search and len(search) > _MAX_SEARCH_LENGTH:
        search = search[:_MAX_SEARCH_LENGTH]
    ...
```

---

### GAP-001 — ℹ️ INFO: Default Request Logging Exposes Query Strings

**File**: `server.py`

`SimpleHTTPRequestHandler` logs every request to stdout including the full path and query string. If the server terminal is visible, query parameters such as `/api/history?search=<sensitive-text>` are exposed.

**Recommendation**: Override `log_message()`:
```python
def log_message(self, format: str, *args: object) -> None:
    """Suppress default HTTP access logging to prevent query string exposure in terminal."""
    pass  # Optionally replace with structured logging that strips query parameters
```

---

### GAP-002 — ℹ️ INFO: Dependabot Missing GitHub Actions Monitoring

**File**: `.github/dependabot.yml`

Dependabot currently monitors only `pip`. If GitHub Actions workflows are added in the future, action pinning vulnerabilities won't be caught automatically.

**Recommended addition**:
```yaml
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

---

### GAP-003 — ℹ️ INFO: `allow_reuse_address` Not Set

**File**: `server.py`

`socketserver.TCPServer` defaults to `allow_reuse_address = False`. On rapid restart, the OS keeps the port in `TIME_WAIT` for up to 60 seconds. The port-increment loop works around this but is not canonical.

**Fix**: Subclass `TCPServer` (this also consolidates the VUL-001 `127.0.0.1` fix):
```python
class _LocalhostTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

# Replace in main():
with _LocalhostTCPServer(("127.0.0.1", port), handler) as httpd:
```

---

## Prioritized Remediation Roadmap

### Phase 1 — Critical (Fix Immediately, Target: < 1 Day)

| Priority | ID | File | One-Line Action |
|---|---|---|---|
| 🔴 P1 | VUL-001 | `server.py:423` | Change `("", port)` → `("127.0.0.1", port)` |
| 🔴 P1 | VUL-002 | `index.html` | Add `escapeHtml()` utility; apply to all `innerHTML` interpolations |
| 🔴 P1 | VUL-002 | `index.html` | Add `rel="noopener noreferrer"` to all `target="_blank"` links |

### Phase 2 — High Priority (Fix Within 3 Days)

| Priority | ID | File | One-Line Action |
|---|---|---|---|
| 🟠 P2 | VUL-003 | `server.py:100` | Replace `*` CORS with explicit localhost origin allowlist |
| 🟠 P2 | VUL-004 | `server.py:122` | Add `MAX_REQUEST_BODY_BYTES = 1_048_576` guard in `_parse_json_body()` |
| 🟠 P2 | VUL-005 | `server.py:378` | Cap `runs` with `max(1, min(10, int(raw_runs)))` |
| 🟠 P2 | VUL-006 | `jev_demo.py:126,130` | Add `_validate_endpoint()` with `_ALLOWED_API_HOSTS` allowlist |

### Phase 3 — Hardening (Fix Within 1 Week)

| Priority | ID | File | One-Line Action |
|---|---|---|---|
| 🟡 P3 | VUL-007 | `server.py:99-104` | Add CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy headers |
| 🟡 P3 | VUL-008 | `server.py:226-234` | Replace string-matching filter with `pathlib.Path.resolve()` containment check |
| 🟡 P3 | VUL-009 | `jev_demo.py:564,719` | Add `verify=True, allow_redirects=False` to all `requests` calls |
| 🟡 P3 | VUL-010 | `database.py`, `server.py` | Add `_MAX_SEARCH_LENGTH = 200` and `_MAX_QUERY_LIMIT = 500` guards |

### Phase 4 — Best-Practice Gaps (Fix at Next Opportunity)

| Priority | ID | File | One-Line Action |
|---|---|---|---|
| ℹ️ P4 | GAP-001 | `server.py` | Override `log_message()` to suppress query string exposure |
| ℹ️ P4 | GAP-002 | `.github/dependabot.yml` | Add `github-actions` ecosystem to Dependabot config |
| ℹ️ P4 | GAP-003 | `server.py` | Subclass `TCPServer` with `allow_reuse_address = True` and `127.0.0.1` bind |

---

## Testing & Verification Checklist

Run after applying all fixes to confirm nothing is broken and remediations are effective:

```bash
# 1. Run the full existing test suite (must pass 100%)
python -m pytest tests/ -v

# 2. VUL-001: Confirm loopback-only binding
#    Run the server, then in another terminal:
netstat -an | findstr 8089
#    PASS: Shows only  127.0.0.1:8089
#    FAIL: Shows       0.0.0.0:8089

# 3. VUL-002: XSS test
#    Submit review text: <img src=x onerror="document.title='XSS'">
#    Open the History tab — title MUST remain "JevTools // System One Cockpit"

# 4. VUL-003: CORS test
curl -H "Origin: http://evil.example.com" http://localhost:8089/api/status -v 2>&1 | findstr "Access-Control"
#    PASS: Response contains "http://localhost:8089" (NOT evil.example.com or *)

# 5. VUL-004: Body size limit
python -c "
import urllib.request
req = urllib.request.Request(
    'http://localhost:8089/api/analyze-review',
    data=b'x' * 2_000_000,
    headers={'Content-Type': 'application/json', 'Content-Length': '2000000'},
    method='POST'
)
try:
    urllib.request.urlopen(req)
except Exception as e:
    print(f'PASS: Rejected with {e}')
"
#    PASS: Returns 400 immediately, server does NOT hang

# 6. VUL-005: Benchmark runs cap
python -c "
import urllib.request, json
req = urllib.request.Request(
    'http://localhost:8089/api/benchmark-ttft',
    data=json.dumps({'runs': 10000}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())
    print(f'Runs executed: {data[\"runs\"]} (PASS if <= 10)')
"

# 7. VUL-007: Security headers
curl -I http://localhost:8089/ | findstr /i "X-Content X-Frame Content-Security Referrer"
#    PASS: All four headers present

# 8. VUL-008: Path traversal tests
#    Each should return 403:
curl -o NUL -s -w "%{http_code}" "http://localhost:8089/pyproject.toml"
curl -o NUL -s -w "%{http_code}" "http://localhost:8089/server.py%00.jpg"
curl -o NUL -s -w "%{http_code}" "http://localhost:8089/pyright_output.json"
```

---

## Reference: Current Security Strengths (Preserve Through All Changes)

The following existing controls are correctly implemented and must not be removed or weakened:

| Control | Location | Description |
|---|---|---|
| Parameterized SQL | `database.py:138-158` | All queries use `?` placeholders — SQL injection eliminated |
| API key masking | `jev_demo.py:781-794` | `mask_key()` applied everywhere — no plaintext key leakage |
| `.py` file blocking | `server.py:231` | Python source files blocked with HTTP 403 |
| `.db` file blocking | `server.py:231` | Database files blocked with HTTP 403 |
| Dotfile blocking | `server.py:229-230` | `.git`, `.env` and dotfile paths blocked |
| Zero runtime deps | `pyproject.toml:23` | No third-party packages at runtime (standard library only) |
| DB gitignore | `.gitignore:38-43` | `jevtools.db` excluded from version control |
| Secrets gitignore | `.gitignore:31-35` | `.env`, `*.pem`, `secrets.json` excluded |
| WAL mode | `database.py:49` | Write-Ahead Logging for database integrity |
| Secure key resolution | `jev_demo.py:1457-1510` | Env var → `getpass` → CLI with explicit security warning |
| Mock mode | `jev_demo.py:1465-1466` | Zero-credit offline testing without API key |
| Weekly Dependabot | `.github/dependabot.yml` | Automated dev-dependency vulnerability scanning |

---

*End of Security Remediation Plan — Version 1.0 — 2026-09-25*  
*Next review recommended: After Phase 1 & 2 fixes are applied, re-audit `index.html` for any residual XSS in `innerHTML` usages*
