# ARGUS - Research Orchestrator

![ARGUS banner](ARGUS-banner.jpeg)

> Not a search engine, not a scraper, not a wrapper. A research orchestration skill and CLI that routes any AI agent through existing open-source tools using a 5-wave methodology with cross-verification.

**Philosophy:** do not reinvent the wheel. Compose existing tools (yt-dlp, Firecrawl, Crawl4AI, TEx, Telerecon) into one coherent research workflow.

## Quick start

```
ARGUS: <query>
ARGUS: compare Notion vs Obsidian
ARGUS: platform AI agents on Twitter
ARGUS: timebox EU AI Act 2024-2026
ARGUS: region AI market in Africa
ARGUS: narrow pricing model of Stripe
ARGUS: deep quantum computing startups in Europe
ARGUS: quick who is the CEO of X
```

Local CLI (standard library only, no install required):

```bash
python argus_search.py plan "ARGUS: compare Notion vs Obsidian"
python argus_search.py report "ARGUS: deep AI in Africa" --output ./output
python argus_search.py preview durov --limit 5
python argus_search.py verify ./output/argus-report-<slug>-<date>.md   # mandatory gate before delivery
python argus_search.py modes
```

Install as a package (one line — you get the `argus` command):

```bash
pip install emo-argus      # CLI: argus
argus modes                # verify install
pip install emo-argus[mcp] # MCP server: argus-mcp
```

> **Why not `pip install argus`?** The name `argus` is taken on PyPI
> since 2015 (v0.0.11, camera calibration utils) — so our distribution
> is `emo-argus`, but it installs the exact same `argus` + `argus-mcp`
> commands. After install you just type `argus`.

> **MCP deployment:** run the MCP server on stdio or localhost only.
> Never bind it to a network socket without authentication, TLS, and a path
> allowlist, because `generate_report` and `verify_report` perform filesystem I/O.

## Contents

| File | Role |
|------|------|
| `SKILL.md` | Orchestrator spec: modes, filters, routing, consent workflows, evidence pipeline |
| `MODES.md` | The 7 research modes in detail |
| `FILTERS.md` | The 10 filters and language presets |
| `TOOLS.md` | Routing matrix and tool notes |
| `USER_GUIDE.md` | Install, 5-step flow, consents, troubleshooting |
| `DECISIONS.md` | Architecture decision records |
| `CHANGELOG.md` | Release history |
| `argus_search.py` | CLI: plan bank, consent gates, report skeleton, Telegram preview, `verify` gate |
| `argus_mcp.py` | MCP server: `list_modes`, `plan_research`, `generate_report`, `telegram_preview`, `verify_report` |
| `pyproject.toml` | Packaging: `argus-search` CLI and `argus-mcp` server |

## Golden rule

> No scraping, no forums or Telegram deep search, no dark web, no restricted sources - without asking the user first and getting an explicit `[Y]`. Silence means SKIP, always.

## Status

- Phase 1 (build) done. Phase 2 (verify) done. Phase 3 (publish prep) done.
- Verified 2026-10-07: 7/7 modes, 7/7 routing entries, 4/4 consents, 5/5 verification checks.
- Full Telegram collection requires the user's own `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`.

