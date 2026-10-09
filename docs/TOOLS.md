# ARGUS — Tool Routing

The right tool for the right task. Restricted tools stay gated behind explicit consent.

## Routing Matrix

| Tool | Stars / License | Wave | Mode | Trigger | Gate |
|------|-----------------|------|------|---------|------|
| `web_search` | - | 1, 2, 3, 5 | all | always | open |
| `web_fetch` | - | all | all | always | open |
| `Agent-Reach` | 92.6k | 5 | Platform, Deep | social signals | open (public) |
| `yt-dlp` | 196k | 5 | Platform (YouTube), Deep | videos | open (public) |
| `gallery-dl` | - | 5 | Platform (Instagram), Deep | images | open (public) |
| `Exa` | - | 1, 5 | Deep | broad discovery | open |
| `Jina Reader` | - | 1 | Deep | URL extraction | open |
| **TEx / TelegramExplorer** | ~375 / Apache-2.0 | 5B (opt-in) | Deep, Platform | Telegram collection | **Consent B** |
| **Telerecon** | 1.3k / MIT | 5B (opt-in) | Deep, Platform | TG analytics | **Consent B** |
| Telepathy (reference) | 1.3k / MIT | - | - | reference only | unmaintained since 2024 - pip release only |
| `Firecrawl` | ~179k | 4, 7 | Deep, Compare, Restricted | anti-bot sites | **Consent A** (+ Wave 7 on bypass) |
| `Crawl4AI` | 58k+ | 4, 7 | Deep, Compare, Restricted | RAG pipeline | **Consent A** |
| `Patchright` | 4.6k | 7 | Restricted | stealth | **Wave 7** |
| `SeleniumBase UC` | 13k | 7 | Restricted | stealth | **Wave 7** |
| `FlareSolverr` / `Byparr` | - | 7 | Restricted | Cloudflare bypass | **Wave 7** |
| `Skyvern` / `Browser Use` / `Steel` | - | 7 | Restricted | browser automation | **Wave 7** |
| `Wayback Machine` | - | 1 | all | historical | open |
| Dark web OSINT sources | - | 6 | Dark web | surface-web OSINT | **Wave 6** |
| **IPED + chat4n6** | 3k / open | disk forensics | Legal evidence | seized disks | **judicial warrant only - not live collection** |

## Why TEx is primary (verified 2026-10-07)

`guibacellar/TEx` - built for researchers, investigators, and law enforcement:
full collection + media + HTML report + export + regex finder + ElasticSearch 8 + Tesseract OCR.
Verified: v0.3.0 runs on Python 3.13 (`pydantic>=2.9` first, then `--no-deps`); run via `python -m TEx`.

Verification notes:
- No console script - run via `python -m TEx`.
- OCR is English-only by default - non-Latin evidence needs extra `tesseract-lang` data.
- `exiftool` is installed separately (`brew install exiftool`).
- Full collection needs user-supplied `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`.

## Media processing layer (Evidence Pipeline - opt-in)

| Processing | Tool | Output |
|------------|------|--------|
| Video/audio transcript | `faster-whisper` (open-source) | derivative - not original evidence |
| Image OCR | `Tesseract` (+ lang data as needed) | derivative |
| Metadata | `exiftool` | derivative |
| Reverse search + dedup | `web_search` images + perceptual hash | derivative |
| Document index | ElasticSearch 8 (TEx built-in) | needs a running instance |

> Originals (export + HTML + hash) stay read-only and separate from derivatives.

