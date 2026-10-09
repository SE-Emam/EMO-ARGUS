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
