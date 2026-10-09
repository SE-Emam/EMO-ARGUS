# ARGUS — Architecture Decisions

> Why ARGUS is built this way. Read before changing any of these.

## ADR-1: stdlib-only core — why zero dependencies?

- **Decision:** the `argus` CLI uses the Python standard library only, and `dependencies = []` in `pyproject.toml`. The only dependency (`mcp`) is optional for the agent server.
- **Why:**
  1. Smaller attack surface — every external dependency is a supply-chain risk.
  2. Instant install — works in isolated, offline environments.
  3. Fully auditable — readable line by line, no black boxes.
- **Cost:** some utilities written by hand (regex instead of BeautifulSoup) — acceptable, see ADR-3.

## ADR-2: ThreadPoolExecutor instead of asyncio — why simple concurrency?

- **Decision:** link checks run on a synchronous `ThreadPoolExecutor(max_workers=8)`, with a short delay between requests and a 50-URL cap.
- **Why:**
  1. Simplicity — the CLI is synchronous by nature.
  2. Enough performance — 50 links finish in seconds in parallel.
  3. Avoids asyncio complexity in a CLI (loop management, harder tests).
- **Rejected:** `asyncio + aiohttp` — external dependency plus unjustified complexity at this scale.

## ADR-3: regex instead of BeautifulSoup for Telegram extraction — why?

- **Decision:** extract message text with one regex plus HTML unescape/escape before merging into output.
- **Why:**
  1. Avoids a heavy external dependency for a single-field extraction.
  2. The task is a public preview, not complex DOM analysis — regex is enough with guards: strict channel check, no redirects, host pinned to `t.me`, output escaped.
- **Known limit:** any Telegram markup change breaks extraction. Mitigation: clear failure message plus smoke test; preview never breaks the core.

## ADR-4: silence means deny — why default N?

- **Decision:** every gate (scraping, forums, dark, restricted) defaults to `False`; non-interactive input maps to `False` automatically; MCP consents stay `False` unless passed explicitly after outside approval.
- **Why:** least-privilege — no sensitive collection without a consent trace in the `Consent log:` section that `verify` checks.

## ADR-5: Secure Bridge Pattern for the browser companion — why loopback-only?

- **Decision:** the Chrome companion (`argus-chrome-extension/`, Manifest V3) never talks to the network except `http://127.0.0.1:8765/*`. A tiny stdlib bridge (`argus_bridge.py`, entry point `argus-bridge`) binds `127.0.0.1` only, checks a per-boot token (`X-Argus-Token` with constant-time compare), and exposes exactly three routes: `GET /health` (no auth), `POST /analyze` (plan from captured context), `POST /verify-snippet` (offline audit, no live fetch).
- **Why:**
  1. Browser is treated as an untrusted host — collection tiers with consent gates stay in the CLI/MCP, never in the extension.
  2. Extension role is context gathering + quick audit only: selected text (capped at 2000 chars), page URL/title, offline structure/citation/URL-shape checks.
  3. Fail-safe offline: when the bridge is down the panel shows `ARGUS Core is offline` and sends data nowhere else; captured context lives in session storage only (cleared with the session), the token alone persists locally.
- **Cost:** user runs one local command and pastes one token into the panel — acceptable, see `docs/EXTENSION.md`.
- **Enforced by:** `check_extension_veto` in `scripts/check_hygiene.py` (scaffold presence, Manifest V3, exact loopback permission, `127.0.0.1` bind, restricted-tier terms never in extension/bridge).

## ADR-6: VS Code companion as thin client — why no new collection logic?

- **Decision:** the VS Code companion (`argus-vscode-extension/`) is a thin client over the same loopback bridge (`127.0.0.1:8765`): `GET /health`, `POST /analyze`, `POST /verify-snippet` only. It adds zero collection tiers, zero scraping, zero network destinations. Token lives in `vscode.SecretStorage` only (never settings/workspace); non-loopback `argus.bridgeUrl` values are refused with a warning + one-click reset; every transport failure fails safe as offline.
- **Why:**
  1. Editor is treated as an untrusted host, same as the browser — consent-gated tiers stay in the CLI/MCP.
  2. Editor role is context auditing + skeleton only: selected text (capped at 2000 chars), offline verdict, 12-section report template mirroring core `build_report` locally.
  3. Fail-safe offline: when the bridge is down every command shows `ARGUS Bridge is offline. Please start the local server.` and sends data nowhere else; sidebar log is in-memory only (max 20, cleared with the session).
- **Enforced by:** `check_extension_veto` in `scripts/check_hygiene.py` (vscode scaffold presence, loopback `bridgeUrl` default + `DEFAULT_BRIDGE_URL` pin, `SecretStorage` token, `X-Argus-Token` header, `isLoopbackUrl` gate, offline message).
