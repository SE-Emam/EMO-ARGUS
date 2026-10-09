---
name: ARGUS
description: ARGUS - Research orchestrator that routes any AI agent through existing research tools (yt-dlp, Firecrawl, Crawl4AI, Patchright, Agent-Reach, Skyvern, etc.) using a 5-wave methodology. Offers 7 research modes (Quick, Compare, Deep, Platform, Time-boxed, Regional, Narrow) with configurable filters. NOT a scraper - a router that tells agents WHICH tools to use WHEN, and HOW to verify. Topic-agnostic. Works with any agent or framework.
---

# ARGUS - Research Orchestrator

## What is ARGUS?

ARGUS is **not a search engine, not a scraper, not a wrapper**. It is a **research orchestration skill** that:

1. **Asks the user what kind of research they want** (mode selection)
2. **Collects the user's constraints** (language, time range, region, sources)
3. **Routes the agent to the right tools** (yt-dlp for YouTube, Firecrawl for LLM-ready content, Patchright for anti-bot, Skyvern for browser automation, etc.)
4. **Enforces a 5-wave methodology** with cross-verification
5. **Delivers a structured report** as a Markdown file

> **Philosophy**: Don't reinvent the wheel. Compose existing tools into a coherent research workflow.

## When to Use

Load this skill when the user requests:
- Any research task with depth ("ابحث بعمق", "do a thorough analysis")
- Comparisons ("compare X vs Y")
- Platform-specific research ("research X on Twitter", "find videos on YouTube about Y")
- Time-bounded research ("what happened with X in 2025")
- Multi-source verification ("is this claim true?")

**Trigger phrases (Arabic)**: ابحث، بحث، قارن، حلل، افحص، ARGUS، research، سكرابنج، اسكراب، منتديات، تليجرام، تيليجرام
**Trigger phrases (English)**: search, research, analyze, compare, deep dive, ARGUS, scrape, crawl, forums, telegram

## Quick Start

```
ARGUS: <query>
ARGUS: compare <X> vs <Y>
ARGUS: platform <query> on <platform>
ARGUS: timebox <query> in <time range>
ARGUS: region <query> in <region>
```

Or just talk naturally: "I want a deep research on Y competing with Y European startup landscape" - the agent will infer the mode.

---

## Multilingual Support (14 Languages)

ARGUS is built to search across **14 languages** by default - covering the majority of the world's most-used languages and the regions where AI/web content is growing fastest.

### The 14 Supported Languages

| # | Language | ISO | Native Name | Script | Key Regions | Population (Speakers) |
|---|----------|-----|-------------|--------|-------------|------------------------|
| 1 | **English** | en | English | Latin | US, UK, AU, IN, NG | 1.5B |
| 2 | **Arabic** | ar | العربية | Arabic | Egypt, KSA, UAE, MA | 400M+ |
| 3 | **Mandarin Chinese** | zh | 中文 | Han/CJK | China, Taiwan, SG | 1.1B |
| 4 | **Spanish** | es | Español | Latin | Mexico, Spain, AR, CO | 560M |
| 5 | **Portuguese** | pt | Português | Latin | Brazil, Portugal, AO | 260M |
| 6 | **French** | fr | Français | Latin | France, CA, SN, CI, MA | 310M |
| 7 | **German** | de | Deutsch | Latin | Germany, AT, CH | 130M |
| 8 | **Russian** | ru | Русский | Cyrillic | Russia, KZ, BY | 260M |
| 9 | **Turkish** | tr | Türkçe | Latin | Turkey, AZ | 90M |
| 10 | **Hindi** | hi | हिन्दी | Devanagari | India | 600M |
| 11 | **Indonesian** | id | Bahasa Indonesia | Latin | Indonesia, MY | 270M |
| 12 | **Korean** | ko | 한국어 | Hangul | South Korea, NK | 80M |
| 13 | **Japanese** | ja | 日本語 | Japanese | Japan | 125M |
| 14 | **Greek** | el | Ελληνικά | Greek | Greece, CY | 13M |

**Total speakers covered**: ~5.7 billion people (more than 70% of the world's population).

### Regional Search Engines per Language

Each language has its own dominant regional search engines - using them surfaces content invisible to English-only Google searches.

| Language | Primary Engine | Secondary Engines | Local Sources to Index |
|----------|---------------|-------------------|------------------------|
| **en** | Google.com | Bing, DuckDuckGo | Reddit, X, YouTube, GitHub |
| **ar** | Yandex AR | Google.com.sa, Google.com.eg, Bing AR | Al Jazeera, Akhbar el Yom, Masrawy, Youm7 |
| **zh** | Baidu (百度) | Bing CN, Sogou (搜狗), 360 Search | Weibo, Zhihu (知乎), Bilibili, WeChat |
| **es** | Google.es | Bing ES, Yahoo Hispano | El País, La Nación, Milenio, ABC.es |
| **pt** | Google.com.br | Google.pt, Bing BR, UOL Busca | Folha, Estadão, G1, R7 |
| **fr** | Google.fr | Qwant (FR), Bing FR, Yahoo FR | Le Monde, Le Figaro, France 24, RFI |
| **de** | Google.de | Bing DE, T-Online, GMX | Spiegel, Die Zeit, FAZ, Heise |
| **ru** | Yandex.ru | Mail.ru, Rambler, Bing RU | RIA Novosti, Lenta.ru, Habr, VK |
| **tr** | Yandex TR | Google.com.tr, Bing TR | Hürriyet, Sabah, NTV, Ekşi Sözlük |
| **hi** | Google.co.in | Bing India, Yahoo India | NDTV, Aaj Tak, Amar Ujala, ABP |
| **id** | Google.co.id | Bing ID, Yahoo ID | Detik, Kompas, Tempo, Tribun |
| **ko** | Naver (네이버) | Daum (다음), Google.co.kr | Nate, Naver Blog, Daum Cafe |
| **ja** | Yahoo Japan JP | Goo.ne.jp, Bing JP, Google.co.jp | Nikkei, Asahi, ITmedia, Qiita |
| **el** | Google.gr | Bing GR, Yahoo GR | Kathimerini, Ta Nea, Newsbeast |

### Language Presets

ARGUS offers pre-defined language sets for common research scenarios:

| Preset | Languages Included | Use Case |
|--------|-------------------|----------|
| **All 14** | All supported languages | Default for Deep mode; maximum coverage |
| **European** | en, es, pt, fr, de, ru, el | EU + European research |
| **Asian** | zh, ja, ko, hi, id, tr | APAC + South Asia research |
| **MENA** | ar, tr, fr, en | Middle East + North Africa |
| **Latin** | es, pt | Latin America + Iberia |
| **BRICS** | en, zh, ru, hi, pt | BRICS countries research |
| **G7** | en, fr, de, ja, es | G7 economic research (es as proxy for it) |
| **Custom** | User picks any subset | Niche research |

### Locale Variations to Handle

Some languages have major regional variants that should be treated as separate search targets:

| Language | Major Variants | Search Strategy |
|----------|----------------|-----------------|
| **Portuguese** | PT-BR (Brazil) vs PT-PT (Portugal) | Search both Google.com.br and Google.pt |
| **Chinese** | ZH-CN (Simplified) vs ZH-TW (Traditional) | Search Baidu (CN) + Yahoo TW |
| **Arabic** | Egyptian, Gulf (KSA/UAE), Maghrebi (MA), Levantine (LB/SY) | Use MSA + regional dialects in queries |
| **Spanish** | ES-MX (Mexico), ES-AR (Argentina), ES-ES (Spain) | Use Latin American Spanish sources + Spain |
| **French** | FR-FR (France), FR-CA (Canada), FR-AF (Africa) | All three have distinct media ecosystems |
| **Hindi** | Devanagari vs Roman (Hinglish) | Search both, especially on social media |

### Cross-Language Search Methodology

When conducting multi-language research, follow this protocol:

1. **Translate the query** into the target language using the agent's translation capability
2. **Use native-script queries** when possible (e.g., 中文 not "Chinese AI")
3. **Use both Devanagari and Roman** for Hindi (Hinglish is widely used)
4. **Add regional qualifiers** to disambiguate (e.g., "AI市場 中國" vs "AI市場 台灣")
5. **For RTL languages** (Arabic, Hebrew), make sure web_fetch handles directionality
6. **Transliterate proper nouns** when needed (e.g., "Tesla" -> تسلا، 特斯拉، 테슬라)
7. **Validate translations** with native sources when possible

### Coverage Tiers

ARGUS offers three language coverage tiers:

| Tier | Languages | Default For | Use Case |
|------|-----------|-------------|----------|
| **Minimum** | 3 non-English | Quick mode | Speed-focused |
| **Standard** | 5-7 non-English | Compare, Time-boxed, Platform, Narrow | Balanced research |
| **Maximum** | All 14 (13 non-English) | Deep, Regional | Comprehensive multi-perspective research |

### Updated Quality Standards (Language)

- **Deep mode default**: search in **all 14 languages** (not just 3)
- **Regional mode**: search in **all 14 + region-specific** (e.g., LatAm = ES + PT + EN)
- **Cross-language verification**: claims from one language should be cross-referenced in another when possible
- **No translation-only citations**: when citing a foreign-language source, cite the original URL, not a translation
- **RTL/LTR handling**: ensure all multi-language output renders correctly (the report should follow LTR but quote foreign text in its native direction)

---

## Methodology (7 Steps)

### Step 0: Mode Selection

ARGUS has **7 research modes**. The agent should either infer the mode from the query or ask the user.

| # | Mode | When to use | Sub-questions | Tools |
|---|------|-------------|---------------|-------|
| 1 | **Quick** | Simple factual lookup | 1 | web_search |
| 2 | **Compare** | X vs Y comparison | 5-10 per item | web_search + extraction |
| 3 | **Deep** (DEFAULT) | Comprehensive research | 15-30 | All waves + all 14 languages |
| 4 | **Platform** | One platform focus | 5-10 | Platform-specific tools |
| 5 | **Time-boxed** | Time range filter | 15-30 | All waves + time filter |
| 6 | **Regional** | Geography focus | 15-30 | All waves + region filter + region-specific languages |
| 7 | **Narrow** | Single subtopic, deep | 3-5 | All waves, narrow scope |

**Default Mode**: Deep (full 5-wave methodology + all 14 languages).

### Step 1: Filter Configuration

The agent should ask for OR infer these filters:

| Filter | Options | Default |
|--------|---------|---------|
| **Language** | all 14 + custom subsets + presets | All 14 (in Deep mode) |
| **Time range** | last 7 days, last 30 days, last 90 days, 2024-2026, custom | No limit |
| **Region** | Global, Africa, LatAm, EU, MENA, APAC, North America | Global |
| **Sources** | academic, news, social, code, video, image, all | all |
| **Output format** | markdown report, JSON, table, brief | markdown report |
| **Depth** | surface, standard, exhaustive | standard |
| **Dark web** | yes/no (opt-in only, see consent workflow) | no |
| **Restricted sources** | yes/no (opt-in only, see consent workflow) | no |
| **Web scraping** | yes/no (opt-in only, see Consent A) | no - search+fetch only |
| **Forums & Telegram** | yes/no + scope (opt-in only, see Consent B) | no |

### Step 2: Tool Selection

Based on the mode and filters, route to these tools:

#### Tier 1 - Always available
- `web_search` - surface web consensus (Google, Bing, DuckDuckGo, Yandex, Baidu, Naver)
- `web_fetch` - extract content from URLs
- `write`/`edit` - produce the final report

#### Tier 2 - Recommended setup
- **Agent-Reach** (92.6k stars) - installs and routes 15 platform CLIs (Twitter, Reddit, YouTube, GitHub, Bilibili, 小红书, etc.)
- **yt-dlp** (196k stars) - YouTube + 1800+ sites for video/audio/subtitles
- **gallery-dl** - Instagram, Twitter, Reddit images
- **Exa** - neural search API
- **Jina Reader** - URL -> clean markdown
- **Forums/Telegram (opt-in only, see Consent B)** - Primary: **TEx / TelegramExplorer** (`pip install TelegramExplorer`, Apache-2.0, ~375 stars) - law-enforcement-grade collection (group info + full message scraper + media + HTML report + export + regex finder + ElasticSearch 8 + Tesseract OCR). Analytics add-on: **Telerecon** (1.3k stars, MIT) for network map + NER + threat assessment. Legacy/reference: **Telepathy** (1.3k stars, MIT - unmaintained since 2024, use pip release only). Forensic backbone (disk evidence): **IPED** (Brazilian Federal Police, 3k stars) + **chat4n6** (deleted-message recovery). Discovery helpers: HN Algolia API, StackExchange API, Telegram `t.me/s/` public preview

#### Tier 3 - Restricted sources (opt-in only)
- **Firecrawl** (125-164k stars) - LLM-ready scraping with anti-bot - requires Scraping Consent (A), and Wave 7 consent if anti-bot bypass involved
- **Crawl4AI** (66-77k stars) - RAG-optimized crawler, self-hosted - requires Scraping Consent (A)
- **Patchright** (4.6k stars) - undetectable Playwright
- **Skyvern** (AI browser automation with vision)
- **Browser Use** (LLM-browser bridge)
- **Steel Browser** (open-source browser sandbox)
- **FlareSolverr** (Cloudflare bypass proxy)
- **Byparr** (92% success anti-bot proxy)
- **Patchright + SeleniumBase UC Mode** (stealth automation)

#### Tier 4 - Dark web context (opt-in only)
- **OSINT firm reports** (Recorded Future, Flashpoint, KELA, Intel 471, Group-IB)
- **Academic papers** on dark web analysis (IEEE, ACM, USENIX)
- **Surface-web news** about dark web activity
- **Law enforcement** press releases (FBI, Europol, Interpol, DOJ)
- **NO .onion access ever**

### Step 3: Plan Generation

Generate sub-questions from the **per-mode template bank** below (mirrored in `argus plan` - same questions the CLI prints). Adapt names, numbers, and scope to the topic; do not fall back to generic 5W repetition.

| Mode | Sub-questions | Template focus |
|------|---------------|----------------|
| Quick | 1 | Single verified answer: one authoritative source + URL + date |
| Compare | 10-20 (5-10 per item) | Split `X vs Y` into items; per-item definition -> feature table -> pricing -> UX -> integrations -> limits -> security -> pro-X / pro-Y opinions (marked OPINION) -> switching cost -> verdict matrix, every cell cited |
| Deep | 15-30 | Scope -> timeline -> actors -> mechanism -> scale numbers -> academic consensus -> regional/non-English picture -> technical landscape -> business models -> risks -> contested claims (both sides) -> last-12-months -> practitioner threads -> gaps -> source audit (3+ languages, 3+ types) |
| Platform | 5-10 | Content formats -> top voices -> dominant narrative -> pushback -> 30-day trend -> native discovery (hashtags/boards) -> notable threads (top+controversial+recent) -> what is missing vs other sources |
| Time-boxed | 15-30 | Timeline spine (dated) -> actors per event -> before/after numbers -> policy milestones -> media shift -> academic coverage -> regional variance -> contested interpretations -> predictions vs reality -> unresolved threads -> per-phase citations -> stale-risk check |
| Regional | 15-30 | Region definition -> in-region scale -> local-language narrative (native-script) -> local leaders -> local regulation -> adoption barriers -> global-vs-local divergence -> case studies -> native data sources -> local criticism -> outlook -> contested local claims |
| Narrow | 3-5 | Precise scope -> verified facts (3+ sources) -> mechanism step-by-step -> edge cases -> open questions |

Show the plan to the user before execution. User can:
- Approve as-is
- Add constraints
- Change mode
- Skip waves
- Add specific URLs/sources they want included
- Override language defaults (e.g., "only ES + PT for LatAm research")

### Step 4: Wave Execution

Execute waves based on the selected mode. Skip waves that don't apply to the mode.

#### Wave 1 - Surface Consensus
- Tools: `web_search` (Google, Bing, DuckDuckGo)
- Goal: mainstream narrative, key actors
- Always executed

#### Wave 2 - Academic Depth
- Tools: Google Scholar, arXiv, PubMed, ResearchGate, JSTOR
- Source: official reports (World Bank, OECD, GSMA, IDC, Gartner)
- Always executed in Deep mode

#### Wave 3 - Regional + Non-English (14 Languages)
- **Coverage**: All 14 supported languages by default
- **Tools per language**:
  - **en**: Google.com, Bing, DuckDuckGo
  - **ar**: Yandex AR, Google.com.sa, Google.com.eg
  - **zh**: Baidu (百度), Bing CN, Sogou (搜狗)
  - **es**: Google.es, Bing ES
  - **pt**: Google.com.br, Google.pt
  - **fr**: Google.fr, Qwant (FR)
  - **de**: Google.de, Bing DE
  - **ru**: Yandex.ru, Mail.ru
  - **tr**: Yandex TR, Google.com.tr
  - **hi**: Google.co.in, Bing India
  - **id**: Google.co.id
  - **ko**: Naver, Daum
  - **ja**: Yahoo Japan JP, Goo.ne.jp
  - **el**: Google.gr
- **Sources**: regional news, blogs, forums in local languages
- **Cross-language verification**: cross-check claims between language editions
- **Always executed in Deep mode and Regional mode**

#### Wave 4 - Technical + Primary Sources
- Tools: GitHub, GitLab, StackOverflow, Firecrawl, Crawl4AI
- Sources: official docs, engineering blogs, HackerNews
- Executed when sources filter includes "code" or Deep mode

#### Wave 5 - Discussion + Edge Cases
- Tools: yt-dlp (YouTube), gallery-dl (Instagram), Agent-Reach (Reddit, Twitter, etc.)
- Sources: Reddit (subreddit depth), Medium, Substack, recent news
- Multi-language: search Reddit in other languages (r/de, r/fr, r/es, r/japan, r/korea, r/brasil, r/arabs)
- Executed when sources filter includes "social" or Deep mode
- **Forums & Telegram deep-dive is NOT part of default Wave 5** - it requires separate opt-in (see Consent B). Without consent, use only surface-level public threads via web_search.

#### Wave 6 - Dark Web Context ([WARNING] OPT-IN ONLY)
- See "Dark Web Consent Workflow" below
- Tools: surface web OSINT sources (NO direct .onion)
- NEVER executed by default

#### Wave 7 - Restricted Sources ([WARNING] OPT-IN ONLY)
- See "Restricted Sources Consent Workflow" below
- Tools: Patchright, FlareSolverr, Skyvern, Browser Use, Steel
- For: corporate sites with login, anti-bot-protected pages, captcha-protected resources
- NEVER executed by default

### Step 5: Cross-Verification

For every important claim, identify at least 3 independent sources. Classify each claim:

- **VERIFIED** - 3+ independent sources agree (can be across languages)
- **CONTESTED** - credible sources disagree (document both sides)
- **UNVERIFIED** - single source or sources lack independence
- **OPINION** - clearly attributed to a specific actor
- **OUTDATED** - source dates suggest information is no longer current

**Multi-language verification**: A claim in English should be cross-referenced in at least one other language when possible (e.g., a claim about Chinese AI market should be verified with both English and Chinese sources).

### Step 6: Synthesis

Produce a structured Markdown report using this template:

```markdown
# ARGUS: [Topic]
**Date** | **Mode**: [Quick/Compare/Deep/Platform/Time-boxed/Regional/Narrow] | **Languages**: [list of 14 with used subset] | **Waves executed**: [...]

## 1. Executive Summary
## 2. Background and Definitions
## 3. Key Actors / Items Compared
## 4. Verified Findings
## 5. Contested Claims and Disagreements
## 6. Geographic and Regional Specifics
## 7. Technical Landscape
## 8. Market and Opportunity Signals
## 9. Community Signals - Forums & Telegram (only if user opted in, else omit with note "skipped - no consent")
## 10. Gaps and Open Questions
## 11. Key Sources (with URLs) - group by language
## 12. Methodology Notes (include consent log: scraping Y/N, forums/Telegram Y/N + scope, Wave 6 Y/N, Wave 7 Y/N)
```

**Language section in Key Sources**:
```markdown
### English sources
- [URL 1]
- [URL 2]

### Arabic sources (العربية)
- [URL 1]
- [URL 2]

### Chinese sources (中文)
- [URL 1]
```

### Step 7: Delivery

- Write to `/workspace/output/argus-report-<topic-slug>-<YYYY-MM-DD>.md`
- Deliver via `<deliver-assets>` block
- Length: 800-5000 words depending on mode

---

## Visual Search Capability (Optional)

For visual content (products, UI/UX, geography, charts), use:
- **Image Web Search**: `web_search` with `search_type="images"`
- **Reverse Image Search**: user-provided image URL
- **Multimodal Extraction**: OCR, charts, diagrams via `mcode-tools`

Triggers: ابحث بالصور، بحث بصري، image search، reverse image search
Auto-activation: when topic involves visual elements

**Visual search works in all 14 languages** - image search engines support cross-language queries.

---

## Evidence & Media Pipeline (Opt-in - requires Consent B + legal basis)

Purpose: help judiciary / law enforcement reach the maximum admissible evidence - not by collecting more, but by collecting in a court-defensible chain: **collect -> preserve (hash) -> process -> analyze -> verify -> report**.

> No Evidence Pipeline step runs without explicit Forums/Telegram consent (B). For non-public devices or seized disks, a separate legal authorization (warrant/case file) is required - never remote extraction.

### Capabilities vs limits (verified from the tool repos themselves)

| Type | What TEx / Telerecon CAN do | Gap - covered by external processing layer |
|------|-----------------------------|--------------------------------------------|
| **Video** | Download + export media with size/type filters (TEx); archive chat media (Telepathy) | Speech inside video is NOT transcribed by TEx. External layer: speech-to-text (`faster-whisper` / Whisper, open-source) + frame OCR + reverse video-keyframe search |
| **Images** | Download + export (TEx); OCR on images via Tesseract (TEx); EXIF-GPS map (Telerecon); `exiftool` metadata (author, timestamps, timezone - per Telepathy docs) | Similarity / reverse-image matching is NOT built in. External layer: reverse image search (`web_search` images) + perceptual hash dedup; Arabic text in Telerecon PDF reports renders incorrectly - use TEx HTML + JSON/CSV export for Arabic evidence |
| **Documents** (PDF/DOCX/XLSX) | Download + export (TEx); regex Message Finder over messages; `exiftool` metadata (creation/edit times, often author/timezone) | Full-text inside attachments is NOT indexed by default. External layer: index via the native **ElasticSearch 8 integration (TEx)** - requires a running Elastic instance |
| **Tools/apps (incl. unethical ones)** | **Intelligence only**: document mentions, distribution links, package names, hashes, distribution channels in public channels as violation evidence | **Red lines (even with consent)**: no downloading/possessing malware, no running it, no redistributing it, no bypassing protections to obtain it, no instructions facilitating its use. Intelligence about the tool is allowed; the tool itself is never handled |

### The 7 stages

1. **Legal basis first** - record authorization type (user consent / case number / warrant) in the consent log. Without it: public content only.
2. **Collect (TEx)** - full scraper from first message + media + file export. Keep the original export + HTML report untouched.
3. **Preserve (chain of custody)** - hash every original file/report (SHA-256), record: URL/channel, access date-time, API account used, tool version. Originals are read-only; ALL derived outputs (OCR, transcripts, NER) are stored separately and labeled derivative.
4. **Process (external layer)** - images -> Tesseract OCR; video/audio -> speech-to-text transcript; documents -> ElasticSearch index; all media -> `exiftool` metadata extraction.
5. **Analyze (Telerecon)** - forward-graph (where a claim/file spread, Gephi edgelist), NER (persons/orgs/locations), timeline / pattern-of-life, capability-intent indicators. Every item stays UNVERIFIED at this stage.
6. **Verify** - each evidentiary claim needs 2+ independent non-social sources before leaving UNVERIFIED (standard cross-verification).
7. **Report** - TEx HTML report + `Community Signals` section + Methodology Notes containing the full consent log, channel list with access dates, file hashes, and a clear original-vs-derivative separation.

### Red lines (repeat: forbidden even with consent)

- No private groups/DMs without per-group approval; no member phone-number / user-ID harvesting; no de-anonymizing; no spam.
- No malware possession, execution, or redistribution; no credential theft; no DDoS; no paywall bypass for republication.
- Forum/Telegram opinion is never presented as verified fact.

---

## Consent Workflows (Mandatory)

> **Golden rule:** no scraping, no forums, no Telegram, no dark web, no restricted sources - without asking the user first and getting an explicit `[Y]`. Silence or ambiguity = SKIP always.

### A. General Web Scraping Consent (Mandatory before ANY scraping)

Applies whenever the user asks to scrape one or more websites (`scrape`, `سكرابنج`, `استخرج`, `crawl`, `extract site`):

#### 2-Level Warning (must be shown verbatim)

**Layer 1**: [WARNING] Web scraping may violate the target site's Terms of Service, rate limits, or copyright. The agent will use polite crawling only (rate-limited, respects robots.txt when possible).
**Layer 2**: [FORBIDDEN] What this skill will NOT do even with consent: no DDoS/load attacks, no credential stuffing, no mass-scale abuse, no bypassing paywalls for redistribution, no storing leaked credentials.

#### Consent Question
```text
Scraping requested for: <list URLs/domains>
[Y] Yes, scrape the listed sites politely (rate-limited, public content only)
[N] No, use search snippets + web_fetch of already-public pages only
```

#### Default = SKIP aggressive scraping
If user is silent or ambiguous -> fall back to `web_search` + `web_fetch` only (no Firecrawl / Crawl4AI / Patchright / bulk crawling). Log the decision in Methodology Notes.

#### What's Allowed vs Forbidden

| [OK] Allowed (with consent) | [NO] Forbidden (even with consent) |
|-----------|-------------|
| Public pages via web_fetch / Jina Reader | DDoS / load attacks |
| Single/low-volume extraction via Firecrawl / Crawl4AI | Credential stuffing / stolen sessions |
| Respecting rate limits + robots.txt when possible | Mass redistribution / piracy |
| User-owned sites (user confirms ownership) | Bypassing paywalls to republish |

### B. Forums & Telegram Advanced Search ([WARNING] OPT-IN ONLY)

For deep community-signal research inside forums and Telegram - high value, high sensitivity.

#### Scope

**Forums covered:**
- Reddit (subreddits + comments depth via Agent-Reach / rdt-cli), HackerNews, StackOverflow / StackExchange, Quora, Discourse forums, phpBB/vBulletin communities, regional forums (Ekşi Sözlük, Habr, Naver Cafe, Daum Cafe, Zhihu, Tieba)
- Search strategy: site-specific queries + native-language queries + thread-depth reading (top posts + controversial + recent)

**Telegram covered:**
- Primary tool: **TEx** - full group/channel message scraper since first message, media download with filters, HTML forensic report + message/file export, regex Message Finder, ElasticSearch 8 integration, Tesseract OCR on images, live listener + Discord alerts
- Analytics add-on: **Telerecon** - cross-channel user tracking, forward-graph mapping (Gephi edgelist), selectors/intel extraction with citations, NER (spaCy), EXIF-GPS map, pattern-of-life report, ideological/capability-intent indicators
- Public channels / public groups only via Telegram search + public web mirrors (t.me/s/ preview)
- Advanced: user-provided `TELEGRAM_API_ID/HASH` or export files the user supplies - never ask for passwords / 2FA codes; recommend burner/sock-puppet account + TraceLabs OSINT VM per Telerecon docs
- Search strategy: keyword search across public channels, forward-graph (where a claim spread), date-bounded search, cross-language channel variants

#### 3-Layer Warning (must be shown verbatim)

**Layer 1**: [WARNING] Forums and Telegram contain personal opinions, unverified claims, and personal data. Content may be biased, outdated, or posted by non-experts.
**Layer 2**: [FORBIDDEN] What this skill will NOT do: no joining private/invite-only groups on the user's behalf without explicit per-group approval, no scraping members' phone numbers / user IDs / personal data, no stalking or identifying private individuals, no storing or republishing leaked credentials, no spam or mass messaging.
**Layer 3**: [LEGAL] Some forums and Telegram groups prohibit automated scraping in their Terms. Bulk extraction may lead to bans or legal exposure in your jurisdiction. Only public content will be used; private/encrypted chats are out of scope - always.

#### Consent Question
```text
[Y] Yes, search public forums + public Telegram channels about: <topic>
[N] No, skip forums/Telegram (surface + academic + news only)
Optional: specify forums (e.g. Reddit only) or Telegram channels (e.g. t.me/xxx only)
```

#### Default = SKIP
If user is silent or ambiguous -> skip forums/Telegram advanced search entirely.

#### Execution rules (after consent)
1. Public only - no private groups, no DMs, no invite-links unless user supplies them and confirms membership rights.
2. Minimize PII - quote usernames only when necessary for attribution; never collect phone numbers.
3. Evidence handling (TEx): keep original export + HTML report untouched, record hash + access date + API account used; any OCR/NER output is derivative, not original evidence.
4. Classify every forums/Telegram claim as UNVERIFIED by default until cross-verified with 2+ independent non-social sources.
5. Separate section in the final report: `Community Signals (Forums/Telegram)` with per-item verdict VERIFIED / CONTESTED / UNVERIFIED / OPINION.
6. Log every channel/forum accessed with URL + access date in Methodology Notes (audit trail).

#### What's Allowed vs Forbidden

| [OK] Allowed (with consent) | [NO] Forbidden (even with consent) |
|-----------|-------------|
| Public subreddit threads, HN, SO, Quora | Private subreddits / private Discords / private Telegram groups without per-group approval |
| Public Telegram channels (t.me/s/ preview or user-supplied API) | Scraping member phone numbers / user IDs in bulk |
| Quoting public posts with URL attribution | De-anonymizing / doxxing authors |
| Sentiment + narrative mapping | Presenting forum opinion as verified fact |

### C. Dark Web Consent Request Workflow (Mandatory for Wave 6)

#### Warning (Question must be asked)

**Level 1**: [WARNING] The Dark Web contains illegal content in most cases.

#### Consent Question
```text
[Y] Yes, search within the Dark Web context (using open-source surface-web sources only)
[N] No, skip Wave 6
```

#### Default Option = SKIP
In case of no response or ambiguity -> Wave 6 is skipped.

---

### D. Restricted Sources Consent Workflow (Mandatory for Wave 7)

For corporate sites, anti-bot-protected pages, login-required resources:

#### 3-Layer Warning

**Layer 1**: [WARNING] Some sources require bypassing anti-bot measures or using login credentials.
**Layer 2**: [FORBIDDEN] What this skill will NOT do: no DDoS, no credential theft, no mass-scaling abuse, no rate-limit violation beyond reasonable use.
**Layer 3**: [LEGAL] Bypassing anti-bot measures may violate the target site's Terms of Service and laws in your jurisdiction.

#### Consent Question
```text
[Y] Yes, use restricted sources (Firecrawl + Crawl4AI + Patchright + Skyvern + etc.)
[N] No, use only public sources
```

#### Default = SKIP
If user is silent or ambiguous -> skip Wave 7.

#### What's Allowed vs Forbidden

| [OK] Allowed | [NO] Forbidden |
|-----------|-------------|
| Public Twitter posts via yt-dlp | Stalking/identifying private individuals |
| Public Instagram posts via gallery-dl | Storing leaked credentials |
| YouTube public videos | DDoS/load attacks |
| GitHub public repos | Credential stuffing |
| Reddit public threads | Terms of Service mass violations |
| Login-required sites the user owns | Rate-limit abuse beyond reasonable |
| Anti-bot bypass for legitimate research | Scraping for redistribution/commercial without permission |

---

## Quality Standards

- **No claim without a source URL** that was actually retrieved
- **No single-source claims** presented as fact
- **No silent disagreement** - contest every contested claim
- **No skipped waves** without explicit user opt-out (Quick mode = 1 wave only)
- **No language bias** - search in **all 14 languages** by default in Deep mode
- **Cross-language verification** - major claims cross-referenced in another language
- **No opinion as fact** - distinguish clearly
- **No scraping without explicit scraping consent (A)** - default is search+fetch only
- **No forums/Telegram deep search without explicit consent (B)** - forums/Telegram claims default to UNVERIFIED
- **No dark web content** without explicit user consent
- **No restricted source access** without explicit user consent
- **No DDoS, no credential stuffing, no mass abuse** - even with consent

## Anti-Patterns (Do Not Do)

- Do not run all 7 waves for Quick mode
- Do not rely on a single source for important claims
- Do not produce conclusions without showing sources
- Do not default to English-only - search all 14 languages in Deep mode
- Do not collapse contested claims into a single narrative
- Do not invent URLs or sources
- Do not scrape any site without showing the scraping warning and getting [Y]
- Do not search forums/Telegram in depth without showing the forums/Telegram warning and getting [Y]
- Do not execute Wave 6 or 7 without consent
- Do not bypass Terms of Service for mass abuse
- Do not use restricted sources for stalking/harassment
- Do not present forum/Telegram opinion as verified fact

## Honest Limitations

- Paywalled academic papers - use abstracts, preprints, citing papers
- Login-required databases (unless user opts into Wave 7)
- Private/encrypted channels (Telegram DMs, private groups without approval - always out of scope)
- Forums/Telegram private content - public channels/threads only, even with consent
- .onion sites (no Tor routing available)
- Restricted content from non-vulnerable sites
- Date sensitivity - sources older than 6 months for fast-moving topics
- Tool availability depends on what's installed in the agent's environment
- Some regional search engines (Naver, Baidu, Yandex) may have anti-bot measures that limit results
- Translation quality varies; native-script queries are always preferred

## How to Invoke

```
ARGUS: <query>
```

Or more specifically:
```
ARGUS: compare Notion vs Obsidian
ARGUS: platform AI agents on Twitter
ARGUS: timebox what happened with X in 2025
ARGUS: region AI market in Africa
ARGUS: narrow pricing model of Y company
ARGUS: deep quantum computing startups in Europe
ARGUS: quick who is the CEO of X
```

The agent will:
1. Detect or ask the mode
2. Apply default language coverage (all 14 in Deep) or ask for subset
3. Apply other default filters or ask
4. Generate plan (per-mode templates)
5. Get user approval
6. Execute waves across all 14 languages
7. Cross-verify including cross-language
8. Run `argus verify <report>` and fix every FAIL before delivery
9. Deliver structured report with sources grouped by language

### Step 8: Verification Gate (mandatory before delivery)

Run the offline audit on the finished report - do NOT deliver a report that FAILs:

```bash
argus verify ./output/argus-report-<slug>-<date>.md
argus verify ./output/argus-report-<slug>-<date>.md --offline  # structure/citations only
```

The gate checks, in order: 12-section structure -> no empty sections -> no TODO
leftovers -> URLs present, no placeholders, no dead links -> no uncited factual
bullets -> verdict labels in use -> per-language source grouping (or non-Latin
script evidence) -> consent log present. Verdicts: `PASS` (deliver),
`WARN` (deliver with noted caveats), `FAIL` (fix and re-run - never deliver).
Same gate exposed to agents as the MCP tool `verify_report`.