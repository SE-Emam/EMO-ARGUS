# ARGUS — Stop getting shallow AI answers

![ARGUS banner](ARGUS-banner.jpeg)

[![PyPI version](https://img.shields.io/pypi/v/emo-argus)](https://pypi.org/project/emo-argus/)
[![Python](https://img.shields.io/pypi/pyversions/emo-argus)](https://pypi.org/project/emo-argus/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/SE-Emam/EMO-ARGUS/actions/workflows/ci.yml/badge.svg)](https://github.com/SE-Emam/EMO-ARGUS/actions)

> AI assistants guess. **ARGUS verifies.** One command turns a vague question into a sourced, multilingual research report — with dead links and uncited claims caught before delivery.

If you use ChatGPT, Claude, or any agent for research and you're tired of invented URLs, English-only results, and no sources — ARGUS is the 60-second fix.

## Install (30 seconds)

```bash
pip install emo-argus
argus modes
```

That's it. You now have the `argus` command. Zero dependencies, works on Python 3.9+.

> Why `emo-argus` and not `argus`? The name `argus` is taken on PyPI since 2015 by an unrelated camera-calibration package. Our distribution is `emo-argus`, but it installs the exact same `argus` + `argus-mcp` commands. After install you just type `argus`.

For AI agents (Claude Code, Cursor, Copilot):

```bash
pip install "emo-argus[mcp]"
argus-mcp
```

## 60-second demo

```bash
# 1. See the plan before anything runs
argus plan "ARGUS: compare Notion vs Obsidian"

# 2. Generate a report skeleton
argus report "ARGUS: deep AI startups in Africa" --output ./output

# 3. Preview any public Telegram channel (no login needed)
argus preview durov --limit 5

# 4. Audit any report before you trust it (mandatory gate)
argus verify ./output/argus-report-*.md --offline
```

Real output: a Markdown report with executive summary, verified findings, contested claims, sources grouped by language, and a consent log.

## Why ARGUS matters

| Without ARGUS | With ARGUS |
|---|---|
| Single-language, Google-only answers | **14 languages** by default in Deep mode (Arabic, Chinese, Spanish, Russian, Hindi…) |
| Invented links you discover too late | **`verify` gate** checks structure, live links, citations, and language coverage |
| "Deep research" = one long paragraph | **7 modes** from 100-word quick answers to 5,000-word deep reports |
| Scraping / forums happen silently | **Explicit consent gates** — silence always means SKIP |
| Agent does random tool calls | **Fixed 5-wave method** — broad → regional → technical → discussion → verify |

**Zero-dependency core:** the CLI is pure Python stdlib. No supply-chain risk, auditable line by line, runs even in air-gapped environments.

## The 7 modes

| Mode | Use it when | You get |
|---|---|---|
| `quick` | One fact, fast | 100–300 words, 1 question |
| `compare` | X vs Y | Table + 1,000–2,000 words |
| `deep` (default) | "Research this properly" | 2,000–5,000 words, all 14 languages |
| `platform` | One platform (YouTube, X, Reddit…) | 1,500–3,000 words |
| `timebox` | "What happened in 2024–2026?" | Timeline + 1,500–3,500 words |
| `region` | One geography | 2,000–4,000 words + regional engines |
| `narrow` | One tight question, deep | 800–1,500 words |

Example:

```text
ARGUS: quick who is the CEO of OpenAI
ARGUS: compare Notion vs Obsidian
ARGUS: deep African fintech landscape 2026
ARGUS: platform AI agents on Twitter last 30 days
```

Full detail: [`docs/MODES.md`](docs/MODES.md) · Filters: [`docs/FILTERS.md`](docs/FILTERS.md) · Tools: [`docs/TOOLS.md`](docs/TOOLS.md)

## Safety in one line

> No scraping, no forums/Telegram deep search, no dark web, no login-bypass — without asking you first and getting an explicit `Y`. Silence = SKIP, always.

Run the MCP server on stdio/localhost only. It touches the filesystem by design.

## Docs

| I want to… | Open |
|---|---|
| Daily use, 5-step flow, FAQ | [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) |
| Modes, filters, tool routing | [`docs/MODES.md`](docs/MODES.md), [`docs/FILTERS.md`](docs/FILTERS.md), [`docs/TOOLS.md`](docs/TOOLS.md) |
| Agent skill spec (advanced) | [`docs/SKILL.md`](docs/SKILL.md) |
| Architecture decisions | [`docs/DECISIONS.md`](docs/DECISIONS.md) |
| What changed | [`docs/CHANGELOG.md`](docs/CHANGELOG.md) |

## License

MIT — see [LICENSE](LICENSE).


