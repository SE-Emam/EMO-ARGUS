# ARGUS — The 7 Research Modes

Pick the depth you need — from a 100-word answer to a 5,000-word multilingual report.

| # | Mode | Trigger | Use when | Sub-questions | Waves | Tools | Output |
|---|------|---------|----------|---------------|-------|-------|--------|
| 1 | **Quick** | `quick` | Simple question, fast answer | 1 | Wave 1 only | `web_search` only | 100-300 words |
| 2 | **Compare** | `compare` | Compare 2+ items | 10-20 (5-10 per item) | Wave 1, 2, 4 | `web_search` + extraction | Comparison table + 1000-2000 words |
| 3 | **Deep (DEFAULT)** | `deep` | Comprehensive research | 15-30 | Waves 1-5 (core) | All tools + all 14 languages | 2000-5000 words |
| 4 | **Platform** | `platform` | Single-platform research | 5-10 platform-specific | Wave 5 + platform tools | Agent-Reach, twitter-cli, rdt-cli, yt-dlp, gallery-dl, TEx (with consent) | 1500-3000 words |
| 5 | **Time-boxed** | `timebox` | Fixed time window | 15-30 (WHEN-focused) | All waves + time filter | All tools + date filter | 1500-3500 words |
| 6 | **Regional** | `region` | Specific geography | 15-30 (WHERE-heavy) | All waves + heavy Wave 3 | Regional engines (Yandex, Baidu, Naver) | 2000-4000 words |
| 7 | **Narrow** | `narrow` | Tight but deep question | 3-5 (one or two axes) | All waves on selected axes | Axis-dependent | 800-1500 words |

## Invocation examples

```
ARGUS: quick who is the CEO of OpenAI
ARGUS: compare Notion vs Obsidian vs Anytype
ARGUS: deep African fintech landscape 2026
ARGUS: platform AI agents on Twitter last 30 days
ARGUS: timebox EU AI Act developments 2024-2026
ARGUS: region AI market in Latin America
ARGUS: narrow pricing strategy of Stripe
```

## Rules

- Default is Deep when ambiguous.
- Quick uses Wave 1 only; no other waves allowed for it.
- Waves 6 (Dark) and 7 (Restricted) are outside every mode by default - opt-in only.
- Forums and Telegram deep dive are outside the default Wave 5 - separate Consent B required.

