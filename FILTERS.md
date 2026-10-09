# ARGUS - Filters (10 Filters)

> Reference: `SKILL.md` Step 1. Standalone filter detail.

| Filter | Type | Default | Description |
|--------|------|---------|-------------|
| **Language** | multi-select (14 + subsets + presets) | All 14 (Deep mode) | Target languages - see language table in SKILL.md |
| **Time range** | date range | no limit | From-to (last 7/30/90 days, 2024-2026, custom) |
| **Region** | multi-select | global | Global, Africa, LatAm, EU, MENA, APAC, North America |
| **Sources** | multi-select | all | academic / news / social / code / video / image |
| **Output format** | enum | markdown | markdown / json / table / brief |
| **Depth** | enum | standard | surface / standard / exhaustive |
| **Dark web** | boolean | false | Wave 6 - opt-in + Consent C |
| **Restricted sources** | boolean | false | Wave 7 - opt-in + Consent D |
| **Web scraping** | boolean | false | Any scraping needs Consent A first; silence = search+fetch only |
| **Forums & Telegram** | boolean + scope | false | Advanced search - opt-in + Consent B; public only |

## Language Presets

| Preset | Languages | Use case |
|--------|-----------|----------|
| All 14 | all | Default for Deep |
| European | en, es, pt, fr, de, ru, el | EU research |
| Asian | zh, ja, ko, hi, id, tr | APAC + South Asia |
| MENA | ar, tr, fr, en | Middle East + North Africa |
| Latin | es, pt | Latin America + Iberia |
| BRICS | en, zh, ru, hi, pt | BRICS countries |
| G7 | en, fr, de, ja, es | G7 economic (es as proxy for it) |
| Custom | any subset | Niche research |

## Coverage Tiers

| Tier | Languages | Default for |
|------|-----------|-------------|
| Minimum | 3 non-English | Quick |
| Standard | 5-7 non-English | Compare, Time-boxed, Platform, Narrow |
| Maximum | All 14 | Deep, Regional |

