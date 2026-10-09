#!/usr/bin/env python3
"""ARGUS CLI - orchestrator helper (stdlib only, no dependencies).

Implements the routing logic from SKILL.md locally:
  mode inference -> filter defaults -> plan generation ->
  consent gates -> report skeleton / public Telegram preview.

Usage:
  python argus_search.py plan "ARGUS: compare Notion vs Obsidian"
  python argus_search.py report "ARGUS: deep AI in Africa" --output ./output
  python argus_search.py preview durov --limit 5
  python argus_search.py modes
  python argus_search.py --help
"""
from __future__ import annotations

import argparse
import datetime
import html as htmlmod
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

VERSION = "1.1.0"

# --- Shared security / reliability constants (Phase 1) ---
CHANNEL_RE = re.compile(r"^[A-Za-z0-9_]{5,64}$")
MAX_PREVIEW_LIMIT = 50
MAX_VERIFY_URLS = 50
VERIFY_DELAY_SEC = 0.3

MODES: dict[str, dict] = {
    "quick": {
        "name": "Quick", "triggers": ["quick", "سريع"],
        "subq": 1, "waves": ["Wave 1"], "tools": ["web_search"],
        "words": "100-300",
    },
    "compare": {
        "name": "Compare", "triggers": ["compare", "قارن", "مقارنة"],
        "subq": "10-20", "waves": ["Wave 1", "Wave 2", "Wave 4"],
        "tools": ["web_search", "extraction"], "words": "1000-2000",
    },
    "deep": {
        "name": "Deep", "triggers": ["deep", "عميق"],
        "subq": "15-30", "waves": ["Wave 1", "Wave 2", "Wave 3", "Wave 4", "Wave 5"],
        "tools": ["all"], "words": "2000-5000",
    },
    "platform": {
        "name": "Platform", "triggers": ["platform", "منصة", "منصّة"],
        "subq": "5-10", "waves": ["Wave 5"],
        "tools": ["Agent-Reach", "yt-dlp", "gallery-dl", "TEx (consent B)"],
        "words": "1500-3000",
    },
    "timeboxed": {
        "name": "Time-boxed", "triggers": ["timebox", "time-box", "وقت", "زمن"],
        "subq": "15-30", "waves": ["Wave 1", "Wave 2", "Wave 3", "Wave 4", "Wave 5"],
        "tools": ["all + time filter"], "words": "1500-3500",
    },
    "regional": {
        "name": "Regional", "triggers": ["region", "منطقة"],
        "subq": "15-30", "waves": ["Wave 1", "Wave 2", "Wave 3 (heavy)", "Wave 4", "Wave 5"],
        "tools": ["regional engines (Yandex, Baidu, Naver)"], "words": "2000-4000",
    },
    "narrow": {
        "name": "Narrow", "triggers": ["narrow", "ضيق", "محدد"],
        "subq": "3-5", "waves": ["Wave 1-5 (scoped)"],
        "tools": ["axis-dependent"], "words": "800-1500",
    },
}

def split_compare_items(topic: str) -> list[str]:
    """Split 'X vs Y' style topics into compared items."""
    parts = re.split(r"\s+vs\.?\s+|\s+مقابل\s+|\s+ضد\s+|\s+or\s+", topic, flags=re.IGNORECASE)
    return [p.strip(" ,\"'") for p in parts if p.strip(" ,\"'")]


# Per-mode question templates. {t} = topic, {a}/{b} = compared items.
# Mirrors SKILL.md Step 3 "Template focus" column.
MODE_TEMPLATES: dict[str, list[str]] = {
    "quick": [
        "What is the single verified answer to '{t}'? (one authoritative source + URL + date)",
    ],
    "compare": [
        "Define {a}: what is it, who owns it, what is the pricing model? (cite official source)",
        "Define {b}: what is it, who owns it, what is the pricing model? (cite official source)",
        "Feature-by-feature: where do {a} and {b} differ on '{t}'? (table, cite docs)",
        "Pricing and total cost: {a} vs {b} for a typical individual user? (cite pricing pages)",
        "UX and learning curve: which is easier to adopt, per real user reports? (cite communities)",
        "Integrations and ecosystem: {a} vs {b}? (cite docs or directories)",
        "Performance and scale limits reported for each? (cite benchmarks or issue trackers)",
        "Security and privacy posture of {a} vs {b}? (cite policies or audits)",
        "Who recommends {a} over {b}, and why? (cite threads; mark OPINION)",
        "Who recommends {b} over {a}, and why? (cite threads; mark OPINION)",
        "Switching cost {a} <-> {b}: migration paths and lock-in? (cite migration guides)",
        "Verdict matrix: which wins per criterion on '{t}', every cell cited?",
    ],
    "deep": [
        "Define '{t}': scope, key terms, and what is explicitly OUT of scope?",
        "Timeline: how did '{t}' evolve? (5+ dated milestones, cite each)",
        "Key actors: who builds, funds, regulates, opposes? (names + roles + URLs)",
        "How does it work in practice? (mechanism, with a primary source)",
        "Scale in numbers: market size, users, growth - 3+ independent figures?",
        "Academic consensus: what do papers and scholars agree on? (cite Scholar/arXiv)",
        "Regional picture: how does '{t}' differ across regions and languages? (use non-English sources)",
        "Technical landscape: leading tools, standards, docs? (cite repos and docs)",
        "Business models and pricing in this space? (cite vendors)",
        "Risks, harms, criticisms: who warns, with what evidence?",
        "Contested claims: where do credible sources disagree? (cite both sides)",
        "Last 12 months: what changed recently? (dated news, newest first)",
        "What do practitioners discuss (surface threads) that official docs omit?",
        "Gaps: what cannot be verified today, and what would verify it?",
        "Source audit: are 3+ languages and 3+ source types represented?",
    ],
    "platform": [
        "What content about '{t}' exists on this platform, and in which formats?",
        "Who are the top voices or accounts on '{t}' here? (handles + follower signals)",
        "Dominant narratives: what does this platform mostly claim about '{t}'?",
        "Pushback: which posts challenge the dominant narrative? (cite URLs)",
        "Last-30-days trend: what is new about '{t}' here?",
        "Native discovery: which hashtags, subreddits, or boards index '{t}' best?",
        "Notable threads or posts worth citing, with URLs (top + controversial + recent)?",
        "What is missing here compared with other platforms and sources?",
    ],
    "timeboxed": [
        "Timeline spine: key events on '{t}' inside the window? (dated, each cited)",
        "Actors: who drove each event? (names + roles)",
        "Before/after numbers: what measurably changed in the window?",
        "Policy and regulatory milestones in the window? (cite official texts)",
        "Media narrative: how did coverage shift across the window?",
        "Academic and policy-paper coverage of this period? (cite)",
        "Regional variance: did the story differ by region or language?",
        "Contested interpretations of what happened? (cite both sides)",
        "What was predicted at the time vs what actually happened?",
        "Unresolved threads at the end of the window?",
        "Sources per phase: is each phase independently cited?",
        "Stale risk: which claims may already be OUTDATED?",
    ],
    "regional": [
        "Define the region for '{t}': which countries, why these, what is excluded?",
        "Market scale in-region: size, growth, local figures? (cite local sources)",
        "Local-language narrative: how do native sources frame '{t}'? (native-script queries)",
        "Local leaders: top companies or actors headquartered in-region?",
        "Regulation: which local laws or policies shape '{t}'? (cite official texts)",
        "Adoption barriers specific to this region?",
        "Global vs local: where does the region diverge from the global story?",
        "Case studies from inside the region? (cite)",
        "Local data sources: which outlets or datasets cover '{t}' natively?",
        "Risks and criticisms voiced locally - not imported narratives?",
        "Outlook: what is forecast for the region specifically?",
        "Contested local claims: who disagrees, with what evidence?",
    ],
    "narrow": [
        "Precise scope: what exactly is '{t}', and what is out of scope?",
        "Verified facts: what is established by 3+ independent sources?",
        "Mechanism: how does it work step by step? (cite a primary source)",
        "Edge cases and exceptions that break the simple story?",
        "Open questions: what remains unknown or contested?",
    ],
}

GATED_KEYWORDS = {
    "scraping": ["scrape", "crawl", "سكرابنج", "اسكراب", "استخرج"],
    "forums": ["forum", "reddit", "منتديات", "telegram", "تليجرام", "تيليجرام"],
    "dark": ["dark web", "دارك"],
    "restricted": ["login", "anti-bot", "captcha", "patchright", "skyvern"],
}


def infer_mode(query: str) -> str:
    q = query.lower()
    for key, spec in MODES.items():
        if key == "deep":
            continue
        if any(tr in q for tr in spec["triggers"]):
            return key
    return "deep"


def detect_gates(query: str) -> dict[str, bool]:
    q = query.lower()
    return {
        gate: any(kw in q for kw in kws)
        for gate, kws in GATED_KEYWORDS.items()
    }


def generate_subquestions(query: str, mode: str, n: int = 8) -> list[str]:
    """Per-mode sub-question plan. Compare splits 'X vs Y' into items."""
    raw = re.sub(r"(?i)^argus\s*:\s*(quick|compare|deep|platform|timebox\w*|region\w*|narrow|سريع|قارن|مقارنة|عميق|منص[ةه]|وقت|زمن|منطقة|ضيق|محدد)?\s*", "", query).strip() or query
    topic = raw
    items = split_compare_items(raw)
    a = items[0] if items else topic
    b = items[1] if len(items) > 1 else "the alternative"
    label = " vs ".join(items[:3]) if mode == "compare" and len(items) > 1 else topic
    templates = MODE_TEMPLATES.get(mode, MODE_TEMPLATES["deep"])
    out = [tpl.format(t=label, a=a, b=b) for tpl in templates]
    if mode == "quick":
        return out[:1]
    if isinstance(n, int) and 0 < n < len(out):
        return out[:n]
    return out


def ask_consent(prompt: str, default_no: bool = True) -> bool:
    """Interactive [Y/N] gate. Silence/ambiguity = SKIP (False)."""
    if not sys.stdin.isatty():
        return False
    try:
        ans = input(f"{prompt} [Y/N] (default N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return ans in ("y", "yes")


def slugify(text: str) -> str:
    """Filesystem-safe slug, keeps Arabic letters.

    Falls back to argus-report-<uuid8> (never silent 'research')
    to avoid report filename collisions (B8).
    """
    s = re.sub(r"(?i)^argus\s*:\s*", "", text)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE).strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = s[:60].strip("-")
    if not s:
        s = f"argus-report-{uuid.uuid4().hex[:8]}"
    return s


def parse_limit(v: int, default: int = 20) -> int:
    """Clamp a preview limit into safe range [1, MAX_PREVIEW_LIMIT]. (B3/DRY)"""
    try:
        n = int(v)
    except (TypeError, ValueError):
        return default
    return max(1, min(n, MAX_PREVIEW_LIMIT))


def resolve_waves(mode: str, consents: dict[str, bool]) -> list[str]:
    """Single source of truth for wave resolution (DRY for CLI + MCP)."""
    waves = list(MODES[mode]["waves"])
    if consents.get("dark"):
        waves.append("Wave 6")
    if consents.get("restricted"):
        waves.append("Wave 7")
    return waves


def format_verdict(label: str) -> str:
    """Normalise a cross-verification label for consistent reporting."""
    return (label or "").strip().upper()


def report_filename(query: str, now: datetime.datetime | None = None) -> str:
    """Collision-proof name: argus-report-{slug}-{YYYYMMDD}-{HHMMSS}-{rand6}.md (B6)."""
    ts = now or datetime.datetime.now()
    stamp = ts.strftime("%Y%m%d-%H%M%S")
    rand = uuid.uuid4().hex[:6]
    return f"argus-report-{slugify(query)}-{stamp}-{rand}.md"


def atomic_write_text(path: Path, text: str) -> None:
    """Atomic write: tmp file + os.replace, never leaves half-files. (B6)"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp-{uuid.uuid4().hex[:6]}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _safe_output_path(base_dir: str | Path, filename: str) -> Path:
    """Resolve filename inside base_dir; refuse path escape (../ or absolute)."""
    base = Path(base_dir).resolve()
    candidate = (base / filename).resolve()
    if not candidate.is_relative_to(base):
        raise ValueError(f"Refused path escape: {filename!r}")
    return candidate


def build_report(query: str, mode: str, langs: str, waves: list[str],
                 consents: dict[str, bool]) -> str:
    date = datetime.date.today().isoformat()
    m = MODES[mode]
    consent_log = ", ".join(
        f"{k}={'Y' if v else 'N'}" for k, v in consents.items()
    )
    return f"""# ARGUS: {query}
**Date**: {date} | **Mode**: {m['name']} | **Languages**: {langs} | **Waves**: {', '.join(waves)}

## 1. Executive Summary
(TODO: 3-5 sentences, every claim cited)

## 2. Background and Definitions
## 3. Key Actors / Items Compared
## 4. Verified Findings
## 5. Contested Claims and Disagreements
## 6. Geographic and Regional Specifics
## 7. Technical Landscape
## 8. Market and Opportunity Signals
## 9. Community Signals - Forums & Telegram
{'_Skipped - no consent._' if not consents.get('forums') else '(TODO: per-item verdict VERIFIED / CONTESTED / UNVERIFIED / OPINION)'}
## 10. Gaps and Open Questions
## 11. Key Sources (with URLs) - group by language
## 12. Methodology Notes
Consent log: {consent_log}. Tool: argus_search.py v1.1.0.
"""


def fetch_telegram_preview(channel: str, limit: int = 20) -> list[str]:
    """Public preview via t.me/s/ - no credentials needed.

    Security (S1): strict channel validation + host pinning.
    Only [A-Za-z0-9_]{5,64} accepted; final URL host must be t.me.
    Raises ValueError on invalid format (caller surfaces as ERROR).
    """
    channel = (channel or "").strip().lstrip("@")
    if not CHANNEL_RE.fullmatch(channel):
        raise ValueError(
            "ERROR: Invalid channel format. "
            "Use 5-64 chars of [A-Za-z0-9_], e.g. 'durov'."
        )
    limit = parse_limit(limit)
    url = f"https://t.me/s/{channel}"

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None  # S1: disable automatic redirects

    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with opener.open(req, timeout=25) as r:
            final_host = urllib.request.urlparse(r.geturl()).hostname or ""
            if final_host.lower() != "t.me":
                raise ValueError(
                    f"ERROR: refused redirect outside t.me ({final_host!r})"
                )
            page = r.read().decode("utf-8", errors="replace")
    except ValueError:
        raise
    except (urllib.error.URLError, urllib.error.HTTPError,
            TimeoutError, OSError) as e:
        raise RuntimeError(f"fetch failed for t.me/s/{channel}: {e}") from e
    raw = re.findall(r"tgme_widget_message_text[^>]*>(.*?)</div>", page, re.S)
    out = []
    for m in raw[:limit]:
        text = re.sub(r"<br\s*/?>", "\n", m)
        text = re.sub(r"<[^>]+>", "", text)
        text = htmlmod.unescape(text).strip()
        if text:
            # S2: escape before embedding in Markdown output files
            out.append(htmlmod.escape(text))
    return out


def cmd_plan(args: argparse.Namespace) -> int:
    mode = args.mode or infer_mode(args.query)
    gates = detect_gates(args.query)
    print(f"Mode: {MODES[mode]['name']}  |  Waves: {', '.join(MODES[mode]['waves'])}")
    print(f"Tools: {', '.join(MODES[mode]['tools'])}  |  Output: {MODES[mode]['words']} words")
    flagged = [g for g, v in gates.items() if v]
    if flagged:
        print(f"Consent required before execution: {', '.join(flagged)} (default = SKIP)")
    print("\nSub-questions (approve / edit / change mode before execution):")
    for i, q in enumerate(generate_subquestions(args.query, mode), 1):
        print(f"  {i}. {q}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    mode = args.mode or infer_mode(args.query)
    consents = {"scraping": False, "forums": False, "dark": False, "restricted": False}
    gates = detect_gates(args.query)
    if not args.no_consent and sys.stdin.isatty():
        if gates["scraping"]:
            consents["scraping"] = ask_consent("Scraping requested - scrape politely (rate-limited, public only)?")
        if gates["forums"]:
            consents["forums"] = ask_consent("Search PUBLIC forums + PUBLIC Telegram channels?")
        if gates["dark"]:
            consents["dark"] = ask_consent("Search dark-web context (surface-web OSINT only)?")
        if gates["restricted"]:
            consents["restricted"] = ask_consent("Use restricted sources (anti-bot/login)?")
    waves = resolve_waves(mode, consents)
    body = build_report(args.query, mode, args.langs, waves, consents)
    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)
    fname = report_filename(args.query)
    path = _safe_output_path(outdir, fname)
    atomic_write_text(path, body)
    print(f"Report skeleton written: {path}")
    print(f"Consent log: {consents}")
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    limit = parse_limit(getattr(args, "limit", 20))
    try:
        msgs = fetch_telegram_preview(args.channel, limit)
    except ValueError as e:
        # S1: invalid channel format - user error, no network attempted
        print(f"{e}", file=sys.stderr)
        return 2
    except (urllib.error.URLError, urllib.error.HTTPError,
            TimeoutError, OSError, RuntimeError) as e:
        # Network / fetch failure - report plainly (no traceback leak)
        print(f"ERROR fetching preview: {e}", file=sys.stderr)
        return 1
    print(f"Public preview: t.me/s/{args.channel} - {len(msgs)} messages (UNVERIFIED by default)")
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# Telegram preview: {htmlmod.escape(str(args.channel))}\n",
                 "_Source: public t.me/s/ preview. Claims = UNVERIFIED._\n"]
        lines += [f"\n---\n\n{m}\n" for m in msgs]
        atomic_write_text(out, "\n".join(lines))
        print(f"Saved: {out}")
    else:
        for m in msgs:
            print(f"\n---\n{m[:500]}")
    return 0


def cmd_modes(_: argparse.Namespace) -> int:
    for key, m in MODES.items():
        print(f"{m['name']:12s} triggers={m['triggers']} waves={m['waves']} out={m['words']}")
    return 0


# ---------------------------------------------------------------------------
# verify - offline report audit (structure, links, citations, languages)
# ---------------------------------------------------------------------------

FULL_SECTIONS = [
    "Executive Summary", "Background", "Key Actors", "Verified Findings",
    "Contested Claims", "Geographic", "Technical Landscape", "Market",
    "Community Signals", "Gaps", "Key Sources", "Methodology Notes",
]

URL_RE = re.compile(r"https?://[^\s)>\]\"']+")
PLACEHOLDER_HOSTS = ("example.com", "example.org", "example.net", "localhost",
                     "127.", "0.0.0.0", "your-url", "url-1", "todo")
NON_LATIN_RES = [
    ("Arabic", r"[\u0600-\u06FF]"),
    ("CJK", r"[\u4E00-\u9FFF\u3040-\u30FF]"),
    ("Cyrillic", r"[\u0400-\u04FF]"),
    ("Devanagari", r"[\u0900-\u097F]"),
    ("Hangul", r"[\uAC00-\uD7AF]"),
    ("Greek", r"[\u0370-\u03FF]"),
]
VERDICTS = ("VERIFIED", "CONTESTED", "UNVERIFIED", "OPINION", "OUTDATED")


def _clean_url(u: str) -> str:
    return u.rstrip(".,;:!?'\"*)]")


def _check_url_live(url: str, timeout: int = 8) -> str:
    """Return 'ok' | 'dead' | 'unknown' (network blocked/timeout)."""
    host = re.sub(r"^https?://", "", url).split("/")[0].lower()
    if any(p in host or p in url.lower() for p in PLACEHOLDER_HOSTS):
        return "placeholder"
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method,
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                code = r.status
            if code in (404, 410):
                return "dead"
            if code < 500:
                return "ok"
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return "dead"
            if e.code < 500:
                return "ok"  # exists but blocked (403/429) - not dead
            continue  # 5xx on HEAD -> still try GET
        except (urllib.error.URLError, TimeoutError,
                OSError):  # timeout/DNS/TLS -> try next method
            continue
    return "unknown"


def _finding(level: str, check: str, message: str) -> dict:
    return {"level": level, "check": check, "message": message}


def check_structure(text: str) -> list[dict]:
    """Sections present + non-empty + no TODO leftovers."""
    out: list[dict] = []
    lines = text.splitlines()
    missing = [s for s in FULL_SECTIONS
               if not re.search(rf"^##\s+\d+\.\s+.*{re.escape(s)}",
                                text, re.MULTILINE | re.IGNORECASE)]
    if missing:
        out.append(_finding("FAIL", "structure",
                            f"missing sections: {', '.join(missing)}"))
    else:
        out.append(_finding("PASS", "structure",
                            f"all {len(FULL_SECTIONS)} sections present"))
    heads = [(i, ln) for i, ln in enumerate(lines)
             if re.match(r"^##\s+\d+\.", ln)]
    empty: list[str] = []
    for idx, (li, _) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
        body = [ln for ln in lines[li + 1:end] if ln.strip()]
        if not body:
            empty.append(heads[idx][1].strip())
    if empty:
        out.append(_finding("FAIL", "empty-sections",
                            f"empty sections: {', '.join(empty)}"))
    else:
        out.append(_finding("PASS", "empty-sections",
                            "every section has content"))
    todos = [ln.strip()[:80] for ln in lines if "TODO" in ln]
    if todos:
        out.append(_finding("FAIL", "todo-leftovers",
                            f"{len(todos)} TODO marker(s), e.g. {todos[0]}"))
    else:
        out.append(_finding("PASS", "todo-leftovers", "no TODO markers"))
    return out


def check_urls(text: str) -> tuple[list[dict], list[str]]:
    """URL presence + placeholder detection. Returns (findings, live)."""
    out: list[dict] = []
    urls = sorted({_clean_url(u) for u in URL_RE.findall(text)})
    if not urls:
        out.append(_finding("FAIL", "urls",
                            "zero URLs - no claim can be verified"))
        return out, []
    out.append(_finding("PASS", "urls", f"{len(urls)} unique URL(s)"))
    placeholders = [u for u in urls
                    if any(p in u.lower() for p in PLACEHOLDER_HOSTS)]
    if placeholders:
        out.append(_finding("FAIL", "placeholder-urls",
                            f"placeholder URLs: {placeholders[:3]}"))
    live = [u for u in urls if u not in placeholders]
    return out, live



def check_citations(text: str) -> list[dict]:
    """Uncited factual bullets + verdict-label coverage."""
    out: list[dict] = []
    lines = text.splitlines()
    suspect: list[str] = []
    in_findings = False
    for ln in lines:
        if re.match(r"^##\s+\d+\.", ln):
            in_findings = bool(re.search(
                r"Verified|Contested|Findings|Actors|Technical|Market",
                ln, re.IGNORECASE))
            continue
        s = ln.strip()
        if (in_findings and re.match(r"^[-*]\s+\S", s) and len(s) > 60
                and "http" not in s
                and not any(v in s for v in VERDICTS)):
            suspect.append(s[:90])
    if suspect:
        out.append(_finding(
            "WARN", "uncited-claims",
            f"{len(suspect)} bullet(s) look factual but carry no URL/verdict, "
            f"e.g. {suspect[0]}"))
    else:
        out.append(_finding("PASS", "uncited-claims",
                            "no obviously uncited factual bullets"))
    used = [v for v in VERDICTS if format_verdict(v) in text]
    if len(used) < 2:
        out.append(_finding(
            "WARN", "verdicts",
            f"only {used or 'none'} verdict label(s) used - "
            "expected cross-verification marks (e.g. VERIFIED/UNVERIFIED)"))
    else:
        out.append(_finding("PASS", "verdicts",
                            f"verdict labels in use: {', '.join(used)}"))
    return out


def check_languages(text: str) -> list[dict]:
    """Per-language grouping + non-Latin script detection."""
    lang_heads = re.findall(r"^###\s+(.+sources.*)$", text,
                            re.MULTILINE | re.IGNORECASE)
    scripts = [name for name, pat in NON_LATIN_RES if re.search(pat, text)]
    if not lang_heads and not scripts:
        return [_finding("WARN", "languages",
                         "no per-language source grouping and no non-Latin "
                         "script detected - single-language research?")]
    return [_finding(
        "PASS", "languages",
        f"{len(lang_heads)} language group(s); "
        f"non-Latin scripts: {scripts or 'none'}")]


def check_consent(text: str,
                  require_consent_log: bool = True) -> list[dict]:
    """Consent-log audit line (full-version reports only)."""
    if not require_consent_log:
        return []
    if "Consent log:" in text:
        return [_finding("PASS", "consent-log",
                         "consent log present in Methodology Notes")]
    return [_finding("FAIL", "consent-log",
                     "missing 'Consent log:' audit line")]


def _check_live_links(live: list[str],
                      max_workers: int = 8) -> list[dict]:
    """Throttled + capped liveness probe (S4: sleep + MAX_VERIFY_URLS)."""
    out: list[dict] = []
    capped = live[:MAX_VERIFY_URLS]
    skipped = len(live) - len(capped)
    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {}
        for i, url in enumerate(capped):
            if i:
                time.sleep(VERIFY_DELAY_SEC)
            futs[url] = ex.submit(_check_url_live, url)
        for url, fut in futs.items():
            try:
                results[url] = fut.result()
            except (urllib.error.URLError, urllib.error.HTTPError,
                    TimeoutError, OSError, RuntimeError):
                results[url] = "unknown"
    dead = [u for u, s in results.items() if s == "dead"]
    unknown = [u for u, s in results.items() if s == "unknown"]
    if dead:
        out.append(_finding("FAIL", "dead-links",
                            f"{len(dead)} dead link(s): {dead[:3]}"))
    else:
        out.append(_finding("PASS", "dead-links",
                            f"0 dead of {len(capped)} checked"))
    if unknown:
        out.append(_finding(
            "WARN", "unreachable-links",
            f"{len(unknown)} unreachable (blocked/offline?), "
            f"e.g. {unknown[0][:60]}"))
    if skipped:
        out.append(_finding(
            "WARN", "link-cap",
            f"{skipped} URL(s) skipped by cap "
            f"(MAX_VERIFY_URLS={MAX_VERIFY_URLS})"))
    return out



def verify_report_text(text: str, check_links: bool = True,
                       require_consent_log: bool = True,
                       max_workers: int = 8) -> tuple[str, list[dict]]:
    """Audit a report. Returns (verdict, findings). Verdict: PASS/WARN/FAIL.

    Orchestrator (Phase 2): delegates to check_structure / check_urls /
    check_citations / check_languages / check_consent + throttled liveness.
    """
    findings: list[dict] = []
    findings += check_structure(text)
    url_findings, live_urls = check_urls(text)
    findings += url_findings
    if check_links and live_urls:
        findings += _check_live_links(live_urls, max_workers=max_workers)
    elif not check_links and live_urls:
        findings.append(_finding("WARN", "dead-links",
                                 "link liveness skipped (--offline)"))
    findings += check_citations(text)
    findings += check_languages(text)
    findings += check_consent(text, require_consent_log)
    fails = sum(1 for f in findings if f["level"] == "FAIL")
    verdict = "FAIL" if fails else ("WARN" if any(
        f["level"] == "WARN" for f in findings) else "PASS")
    return verdict, findings


def cmd_verify(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.is_file():
        print(f"ERROR: not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    verdict, findings = verify_report_text(
        text, check_links=not args.offline, require_consent_log=True)
    fails = sum(1 for f in findings if f["level"] == "FAIL")
    warns = sum(1 for f in findings if f["level"] == "WARN")
    for f in findings:
        print(f"[{f['level']:4s}] {f['check']:16s} {f['message']}")
    print(f"\nVerdict: {verdict} ({fails} FAIL, {warns} WARN)")
    return 0 if verdict == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="argus-search", description="ARGUS orchestrator CLI")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("plan", help="infer mode + show sub-question plan")
    pp.add_argument("query")
    pp.add_argument("--mode", choices=list(MODES))
    pp.set_defaults(func=cmd_plan)

    rp = sub.add_parser("report", help="generate report skeleton with consent gates")
    rp.add_argument("query")
    rp.add_argument("--mode", choices=list(MODES))
    rp.add_argument("--langs", default="all-14")
    rp.add_argument("--output", default="./output")
    rp.add_argument("--no-consent", action="store_true", help="skip interactive prompts (all = N)")
    rp.set_defaults(func=cmd_report)

    vp = sub.add_parser("preview", help="public Telegram channel preview (no credentials)")
    vp.add_argument("channel")
    vp.add_argument("--limit", type=int, default=20)
    vp.add_argument("--output")
    vp.set_defaults(func=cmd_preview)

    mp = sub.add_parser("modes", help="list the 7 modes")
    mp.set_defaults(func=cmd_modes)

    vp2 = sub.add_parser("verify", help="audit a finished report (links, citations, languages)")
    vp2.add_argument("file", help="path to the Markdown report")
    vp2.add_argument("--offline", action="store_true",
                     help="skip live link checks (structure/citations only)")
    vp2.set_defaults(func=cmd_verify)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
