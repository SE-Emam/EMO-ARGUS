# Changelog - ARGUS

All notable changes documented here. Format follows Keep a Changelog, versioning follows SemVer.

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
