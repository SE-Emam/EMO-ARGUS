# ARGUS - User Guide

> From query to report in 5 steps. Full spec is in `SKILL.md` - this guide is for daily use.

## 1. Install (one minute)

One line — you get the `argus` command:

```bash
pip install emo-argus
argus modes
```

> `pip install argus` is taken on PyPI since 2015 by another project,
> so our package is `emo-argus` — after install you just type `argus`.

Install later, only when needed:

| Task | Install |
|------|---------|
| Full Telegram collection | pip install pydantic, TelegramExplorer, plus your TELEGRAM_API_ID and TELEGRAM_API_HASH |
| Non-Latin image OCR | brew install tesseract-lang |
| Media metadata | brew install exiftool |
| Video/audio transcript | pip install faster-whisper |

## 2. Basic use (5 steps)

### Step 1 - Write your request

Free form (agent infers the mode):

```text
ARGUS: <research topic>
```

Directed form (faster and more precise):

```text
ARGUS: quick who is the CEO of X
ARGUS: compare Notion vs Obsidian
ARGUS: deep African fintech landscape 2026
ARGUS: platform AI agents on Twitter last 30 days
ARGUS: timebox EU AI Act developments 2024-2026
ARGUS: region AI market in Latin America
ARGUS: narrow pricing strategy of Stripe
```

Note: Arabic trigger words are also supported, see SKILL.md trigger lists.

### Step 2 - Answer 4 questions

1. Mode (or leave auto-inference)
2. Filters (languages, region, time - default is all 14 languages in Deep)
3. Plan approval (sub-question list before execution)
4. Opt-in consents only when needed (see section 4)

### Step 3 - Run via CLI (optional)

```bash
python argus_search.py plan "ARGUS: compare Notion vs Obsidian"
python argus_search.py report "ARGUS: deep AI in Africa" --output ./output
python argus_search.py report "ARGUS: quick X" --no-consent --output ./output
python argus_search.py modes
```

### Step 4 - Verify before delivery (mandatory)

```bash
python argus_search.py verify ./output/argus-report-<slug>-<date>.md
python argus_search.py verify ./output/argus-report-<slug>-<date>.md --offline
```

The gate checks: 12-section structure, no empty sections, no TODO leftovers, live URLs with no placeholders, no uncited factual claims, verdict labels in use, language coverage, consent log. PASS means deliver, WARN means deliver with noted caveats, FAIL means fix and re-run. Never deliver a failing report.

### Step 5 - Receive the report

Markdown file in ./output with fixed sections: summary, background, verified findings, contested claims, sources grouped by language, methodology notes plus consent log.

## 3. The seven modes in short

| Mode | When | Output |
|------|------|--------|
| Quick | Simple question | 100-300 words |
| Compare | Compare items | Table plus 1000-2000 words |
| Deep (default) | Comprehensive research | 2000-5000 words, all 14 languages |
| Platform | One platform | 1500-3000 words |
| Time-boxed | Time window | 1500-3500 words |
| Regional | Geography | 2000-4000 words |
| Narrow | Tight deep question | 800-1500 words |

Detail: MODES.md. Filters: FILTERS.md. Tools: TOOLS.md.

## 4. Consents (golden rule)

> No scraping, no forums or Telegram, no dark web, no restricted sources - without asking you first and getting an explicit [Y]. Silence means SKIP, always.

| Your request includes | What you see | Default |
|-----------------------|--------------|---------|
| Site scraping | 2-layer warning plus Y/N question naming the domains | search plus fetch only |
| Forums and Telegram | 3-layer warning | skip entirely |
| Dark web | Warning (mostly illicit content) | skip |
| Login or anti-bot sites | 3-layer warning (bypass may violate ToS and law) | public sources only |

## 5. Telegram and evidence scenario (for legal use)

Quick public preview with no account (public only, UNVERIFIED by default):

```bash
python argus_search.py preview telegram --limit 5
python argus_search.py preview <channel> --limit 20 --output preview.md
```

Full documented collection (needs your TELEGRAM_API_ID and HASH plus Consent B plus legal basis):

```text
Collect (TEx: full scraper plus media plus export plus HTML report)
  -> Preserve (SHA-256 per file plus access date plus account, originals read-only)
    -> Process (OCR, transcript, Elastic, exiftool, separate derivatives)
      -> Analyze (Telerecon: spread map plus NER plus timeline)
        -> Verify (2 independent sources before leaving UNVERIFIED)
          -> Report (HTML plus Community Signals plus consent log)
```

Red lines (even with consent): no private groups or DMs without per-group approval, no phone-number harvesting, no malware possession or execution or redistribution, no forum opinion presented as fact.

Full detail: Evidence and Media Pipeline section in SKILL.md.

## 6. Troubleshooting

| Problem | Fix |
|---------|-----|
| pydantic-core build fails (TEx) | Install pydantic first, then TEx with --no-deps |
| No tex command | Run via python -m TEx only |
| OCR misses non-Latin text | Install tesseract-lang data |
| exiftool not found | brew install exiftool |
| TEx asks for API credentials | Expected for full collection, use preview for public preview |
| Weak result | Try a deeper mode, or widen languages or region |

## 7. FAQ

**Is ARGUS a search engine?** No, it is a protocol that routes any agent to existing tools in the right order.

**Does it work without internet?** The CLI (plan, report, preview) runs locally. Full execution needs the host agent tools.

**How many languages?** 14 by default in Deep, see language table in SKILL.md.

**Where are reports?** In ./output, auto-created, excluded from git.
