# ARGUS — User Guide

> From question to verified report in 5 steps. Start here, go deep only if you need to.

## 1. Install (30 seconds)

```bash
pip install emo-argus
argus modes
```

You now have the `argus` command. Zero dependencies, Python 3.9+.

> Why `emo-argus`? The name `argus` is taken on PyPI since 2015 by an unrelated package. Our distribution is `emo-argus` — it installs the `argus` + `argus-mcp` commands. After install you just type `argus`.

Only install extras when you need them:

| Task | Install |
|------|---------|
| AI-agent server | `pip install "emo-argus[mcp]"` then `argus-mcp` |
| Full Telegram collection | Your own `TELEGRAM_API_ID` + `TELEGRAM_API_HASH` |
| Video/audio transcripts | `pip install faster-whisper` |
| Image OCR / metadata | `brew install tesseract-lang exiftool` |

## 2. Use it (5 steps)

### Step 1 — Write your request

```text
ARGUS: <research topic>
ARGUS: quick who is the CEO of X
ARGUS: compare Notion vs Obsidian
ARGUS: deep African fintech landscape 2026
ARGUS: platform AI agents on Twitter last 30 days
ARGUS: timebox EU AI Act developments 2024-2026
ARGUS: region AI market in Latin America
ARGUS: narrow pricing strategy of Stripe
```

Arabic works too: `قارن`, `عميق`, `منطقة` and more.

### Step 2 — Confirm 4 things

1. Mode (or leave auto-detect — ambiguous defaults to Deep)
2. Filters (languages, region, time — Deep defaults to all 14 languages)
3. Plan approval (sub-question list before anything runs)
4. Consents — only when needed (see §4)

### Step 3 — CLI

```bash
argus plan "ARGUS: compare Notion vs Obsidian"
argus report "ARGUS: deep AI in Africa" --output ./output
argus report "ARGUS: quick X" --no-consent --output ./output
argus modes
```

### Step 4 — Verify before you trust (mandatory)

```bash
argus verify ./output/argus-report-*.md --offline
argus verify ./output/argus-report-*.md
```

What it checks: 12-section structure, no empty sections, no TODO leftovers, real URLs (no placeholders), cited claims, verdict labels (`VERIFIED` / `CONTESTED` / `UNVERIFIED`), language coverage, consent log.

`PASS` = deliver. `WARN` = deliver with caveats. `FAIL` = fix and re-run — never deliver a failing report.

### Step 5 — Read the report

Markdown in `./output`: summary, background, verified findings, contested claims, sources grouped by language, methodology + consent log.

## 3. The 7 modes

| Mode | When | You get |
|------|------|---------|
| Quick | One fact, fast | 100–300 words |
| Compare | X vs Y | Table + 1,000–2,000 words |
| Deep (default) | Proper research | 2,000–5,000 words, 14 languages |
| Platform | One platform | 1,500–3,000 words |
| Time-boxed | Time window | 1,500–3,500 words |
| Regional | One geography | 2,000–4,000 words |
| Narrow | One tight question | 800–1,500 words |

Detail: [`MODES.md`](MODES.md) · Filters: [`FILTERS.md`](FILTERS.md) · Tools: [`TOOLS.md`](TOOLS.md)

## 4. Safety (one rule)

> No scraping, no forums/Telegram deep search, no dark web, no login-bypass — without asking you first and getting an explicit `Y`. Silence = SKIP, always.

| Request includes | You see | Default |
|------------------|---------|---------|
| Site scraping | Warning naming the domains + Y/N | Search + fetch only |
| Forums / Telegram | Warning + scope question | Skip |
| Dark web | Warning | Skip |
| Login / anti-bot sites | Warning (may violate ToS/law) | Public sources only |

Run `argus-mcp` on stdio/localhost only — it writes files by design.

## 5. Telegram preview (no login)

```bash
argus preview durov --limit 5
argus preview <channel> --limit 20 --output preview.md
```

Public channels only, claims are `UNVERIFIED` by default. Full collection needs your own API credentials + explicit consent + legal basis — see [`SKILL.md`](SKILL.md) Evidence Pipeline.

Red lines (even with consent): no private groups/DMs without per-group approval, no phone harvesting, no malware handling, no forum opinion presented as fact.

## 6. Troubleshooting

| Problem | Fix |
|---------|-----|
| `argus: command not found` | Re-run `pip install emo-argus`, check PATH |
| Weak result | Try a deeper mode, widen languages/region |
| `preview` finds nothing | Channel name must be 5–64 chars `[A-Za-z0-9_]`, public only |
| OCR misses Arabic | `brew install tesseract-lang` |
| `exiftool not found` | `brew install exiftool` |

## 7. FAQ

**Is ARGUS a search engine?** No — it tells you (or your agent) which tools to use, in which order, and how to verify.

**Does it work offline?** `plan`, `report`, `verify --offline` run locally with zero dependencies. Live link checks and full research need network + agent tools.

**How many languages?** 14 in Deep by default — see language table in [`SKILL.md`](SKILL.md).

**Where are reports?** `./output/`, auto-created, excluded from git.

