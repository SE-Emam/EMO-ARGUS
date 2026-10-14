# Changelog - ARGUS

All notable changes documented here. Format follows Keep a Changelog, versioning follows SemVer.

## [1.2.1] - 2026-10-14 - Packaging hotfix

### FIX
- Ship `templates.json` inside the wheel/sdist via `[tool.setuptools.package-data]` — PyPI 1.2.0 crashed on every `plan`/`report` with `KeyError: 'deep'` because the file was missing from the distribution.
- `generate_subquestions` now degrades to generic fallback questions instead of raising `KeyError` when templates are unavailable.
- Chrome extension clamps the configured bridge port to 1-65535 in both `background.js` and `sidepanel.js` (storage is user-writable).
- License metadata uses the SPDX expression (`license = "Apache-2.0"`) per current packaging guidance.
- Report footer uses dynamic `VERSION` (no hardcoded version string).

### ADD
- Packaging regression tests: `templates.json` ships with all 7 modes; sub-question generation survives missing templates.
- CI now builds the wheel and asserts `templates.json` is inside it.

## [1.2.0] - 2026-10-14 - Hardening, extensions, Apache-2.0

### SECURITY
- Bridge CORS restricted to loopback origins only (DNS rebinding guard).
- Chrome manifest pinned to exact `http://127.0.0.1:8765/*` with strict CSP (no unsafe-inline).
- VSCode webview `enableScripts: false`, `validateBridgeUrl` with port-range check, SecretStorage token only.
- Fixed `urlparse` import bug in `fetch_telegram_preview` (`urllib.parse`).

### ADD
- MCP unit tests (`tests/test_mcp.py`, 6 tests); total suite 22 passed.
- `src/emo_argus/templates.json` external mode templates; structured logging via `ARGUS_LOG_FORMAT`/`ARGUS_LOG_LEVEL`.
- YAML frontmatter in generated reports; configurable timeouts via `ARGUS_PREVIEW_TIMEOUT`/`ARGUS_VERIFY_TIMEOUT`.
- Multi-stage Dockerfile at `docs/docker/Dockerfile`; pre-commit config; extension READMEs; Agent Skills README section (no-Docker native run).
- Chrome: configurable bridge port UI, retry with backoff. VSCode: status-bar item, `bridgeClient` unit tests.

### CHANGED
- License switched from MIT to Apache-2.0 (`LICENSE`, `pyproject.toml`, README badge, VSCode package).
- README rewritten for marketing clarity (English-only visitor UI); report footer uses dynamic `VERSION`.
- Dockerfile moved from root to `docs/docker/` to pass hygiene root whitelist.

## [Unreleased] - ARGUS-LITE foundation

### ADD
- Profile-based configuration via `src/emo_argus/profiles.py`: sovereign preset (7 modes, full gates, full verify) and institutional preset (quick, compare, regional; silent gates; structure plus links verify).
- CLI `--profile {sovereign,institutional}` flag (default sovereign) wired into plan, report, modes, and verify; plus `argus-lite` entry point defaulting to institutional.
- Institutional tests covering mode clamping and silent gates.
- README section for ARGUS Lite institutional use.

## [Unreleased] - Field companions scaffold (Secure Bridge Pattern)

### FIX
- Visitor UI is English-only again: rewrote `docs/CONTRIBUTING.md` fully in English, converted Chrome companion UI (`background.js` menu title, `sidepanel.html` layout/labels, `sidepanel.js` status/result/log strings) to English, removed stray Arabic line in `docs/USER_GUIDE.md`. Only allowlisted functional i18n data keeps non-Latin script (`src/emo_argus/search.py` triggers, `docs/SKILL.md` language table, `tests/test_core.py` assertions).
- Added `check_language_veto` gate in `scripts/check_hygiene.py` (fails on Arabic/CJK outside the allowlist) and documented it in `docs/CONTRIBUTING.md` §2.
- Task/fix/session artifacts stay local-only: `TASK-*.md`, `FIX-*.md`, `*.log`, `SHA256SUMS`, `*.zip`, `*.vsix` added to `.gitignore` plus `docs/CONTRIBUTING.md` §6. Verified no such files are tracked (`git ls-files` clean).

### ADD
- VS Code companion scaffold `argus-vscode-extension/` (thin client, zero collection logic): sidebar view, 6 commands (`Check Bridge`, `Verify Selection`, `Plan From Selection`, `Insert Report Template`, `Set/Clear Token`), loopback-only client (`src/bridgeClient.ts`), `SecretStorage` token, 12-section offline report template mirroring core `build_report`.
- Local bridge `src/emo_argus/bridge.py` (stdlib only, entry point `argus-bridge`): binds `127.0.0.1:8765` only, per-boot token via `X-Argus-Token`, routes `GET /health`, `POST /analyze` (plan from captured context), `POST /verify-snippet` (offline audit, no live fetch).
- Chrome companion scaffold `argus-chrome-extension/` (Manifest V3 strict): `manifest.json` (loopback host only, strict CSP), `background.js` (context menu + offline fail-safe), `sidepanel.html` + `sidepanel.js` (status, token box, Verify Snippet, ephemeral session log).
- Bridge unit tests `tests/test_bridge.py` (4 tests: verification message, truncation, URL guard, offline audit shape).
- Docs: `docs/EXTENSION.md` (setup + use + endpoints), ADR-5 in `docs/DECISIONS.md` (loopback-only bridge rationale).

### SECURITY
- Architectural veto enforced by new `check_extension_veto` gate in `scripts/check_hygiene.py`: Manifest V3 + exact loopback permission + `127.0.0.1` bind + restricted-tier terms never in extension/bridge. Browser role is context gathering + quick audit only.

## [1.1.0] - 2026-10-09 - Security and Stability Hardening

### SECURITY
- Strict Telegram channel validation (`^[A-Za-z0-9_]{5,64}$`) against path injection (SSRF), redirects disabled, host pinned to `t.me` only.
- Path confinement via `_safe_path` in MCP surfaces (`generate_report` / `verify_report`) and `_safe_output_path` in core against read/write outside the project.
- Telegram output sanitized via `html.escape` before merging into outputs (reflected XSS guard).

### FIX
- Live link check logic fixed (`HEAD` then `GET`): `HEAD` failure falls through with `continue` to try `GET`; `unknown` only after both fail. Removes false positives.
- CLI `limit` clamped with the same MCP logic (`[1, 50]`) via `parse_limit()`.
- Report name collisions fixed: `argus-report-{slug}-{YYYYMMDD}-{HHMMSS}-{rand6}.md` plus atomic write (`tmp + os.replace`).
- Empty `slugify` falls back to `argus-report-<uuid8>` instead of silent `research`.
- Parent directory auto-created in `cmd_preview --output` (`mkdir parents=True`).
- `n` parameter honored in `generate_subquestions`.

### REFACTOR
- Long `verify_report_text` (115 lines) split into 5 focused functions: `check_structure` / `check_urls` / `check_citations` / `check_languages` / `check_consent` plus `_check_live_links` coordinator.
- Shared DRY logic extracted: `resolve_waves()` / `parse_limit()` / `format_verdict()` used by CLI and MCP.
- `ThreadPoolExecutor` moved to top-level import; bare `except Exception` replaced with specific exceptions (`URLError, HTTPError, TimeoutError, OSError`).

### TEST
- 10 core unit tests added (`tests/test_core.py`) covering security and functional logic - `10 passed`.
- MCP smoke-test protocol added (`scripts/mcp_smoke_test.py`).

### DOCS
- `README` examples updated (`preview durov --limit 5`) plus local-only MCP deploy warning (`stdio/localhost ONLY`).
- `DECISIONS.md` added (architecture log: stdlib-only / ThreadPool / regex / default-N).
- `CI` added (`.github/workflows/ci.yml`: ruff + pytest + pip-audit + verify-offline).
- `.gitignore` clarified (`output/*.md` explicit) and `__pycache__` cleaned.

## [1.0.0] - 2026-10-07 - Initial orchestrator release
- 7 research modes plus 5-wave methodology plus 4 consent gates plus `verify` delivery gate plus MCP server.
