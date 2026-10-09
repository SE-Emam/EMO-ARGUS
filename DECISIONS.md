# ARGUS - Architecture Decisions

> Purpose: stop re-litigating settled choices. Read the rationale before changing any of these.

## ADR-1: stdlib-only core - why zero dependencies?

- **Decision:** `argus_search.py` uses the Python standard library only (argparse, datetime, html, re, urllib, pathlib, concurrent.futures), and `dependencies = []` in `pyproject.toml`. The only dependency (`mcp`) is optional for the agent server.
- **Why:**
  1. Smaller attack surface - every external dependency is a supply-chain risk (typosquatting, hijack).
  2. Instant install with no network - required for isolated air-gapped environments.
  3. Fully auditable - 733 lines readable line by line, no black boxes.
- **Cost:** some utilities written by hand (regex sanitization instead of BeautifulSoup) - acceptable, see ADR-3.

## ADR-2: ThreadPoolExecutor instead of asyncio - why simple concurrency?

- **Decision:** link liveness checks run on a synchronous `ThreadPoolExecutor(max_workers=8)`, with `time.sleep(0.3)` between submissions and a `MAX_VERIFY_URLS=50` cap.
- **Why:**
  1. Simplicity - the CLI is synchronous by nature; asyncio would force an event loop and full refactor for no gain.
  2. Enough performance - 50 links at about 1s each finishes in seconds in parallel; no async engine needed.
  3. Avoids asyncio complexity in a CLI (loop management, cancellation, harder tests).
- **Rejected:** `asyncio + aiohttp` - external dependency plus unjustified complexity at this scale.

## ADR-3: regex instead of BeautifulSoup for Telegram extraction - why?

- **Decision:** extract `tgme_widget_message_text` with one regex plus `html.unescape` plus `html.escape` before merging into output.
- **Why:**
  1. Avoids a heavy external dependency (`bs4 + lxml`) for a single-field extraction.
  2. The task is a public proof-of-concept preview, not complex DOM analysis - regex is enough with guards: strict channel check (`^[A-Za-z0-9_]{5,64}$`) plus disabled redirects plus host pinned to `t.me` plus `html.escape` against reflected XSS.
- **Documented limit:** structural fragility - any Telegram markup change breaks extraction. Mitigation: clear failure message plus smoke test plus optional fetch that never breaks the core.

## ADR-4: silent consent means deny - why default N?

- **Decision:** every gate (scraping, forums, dark, restricted) defaults to `False`; non-tty input maps to `False` automatically; MCP consents stay `False` unless passed explicitly after an external `[Y]`.
- **Why:** least-privilege principle for sovereign environments - no sensitive collection without a consent trace in the `Consent log:` section that `verify` checks.
