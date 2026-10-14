#!/usr/bin/env python3
"""ARGUS CLI - turn a vague question into a verified research plan.

Usage:
  argus plan "ARGUS: compare Notion vs Obsidian"
  argus report "ARGUS: deep AI in Africa" --output ./output
  argus preview durov --limit 5
  argus modes
  argus --help
"""
from __future__ import annotations

import argparse
import datetime
import html as htmlmod
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    from .profiles import allowed_modes as _allowed_modes
    from .profiles import get_profile as _get_profile
except ImportError:  # pragma: no cover - direct script fallback
    from emo_argus.profiles import allowed_modes as _allowed_modes
    from emo_argus.profiles import get_profile as _get_profile

VERSION = "1.1.0"

# --- Structured logging ---
_logger = logging.getLogger("argus")
if not _logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    if os.environ.get("ARGUS_LOG_FORMAT", "").lower() == "json":
        class _JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                payload = {
                    "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "msg": record.getMessage(),
                }
                if record.exc_info and record.exc_info[0] is not None:
                    payload["exception"] = self.formatException(record.exc_info)
                return json.dumps(payload, ensure_ascii=False)
        _handler.setFormatter(_JsonFormatter())
    else:
        _handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-7s %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        ))
    _logger.addHandler(_handler)
    _debug = os.environ.get("ARGUS_LOG_LEVEL", "").upper() == "DEBUG"
    _logger.setLevel(logging.DEBUG if _debug else logging.INFO)

# --- Shared security / reliability limits ---
CHANNEL_RE = re.compile(r"^[A-Za-z0-9_]{5,64}$")
MAX_PREVIEW_LIMIT = 50
MAX_VERIFY_URLS = 50
VERIFY_DELAY_SEC = 0.3


def _int_env(name: str, default: int) -> int:
    """Read an integer from an env var, falling back to default on any failure."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


PREVIEW_TIMEOUT = _int_env("ARGUS_PREVIEW_TIMEOUT", 25)
VERIFY_TIMEOUT = _int_env("ARGUS_VERIFY_TIMEOUT", 8)

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


# Per-mode question templates loaded from external JSON file.
# Falls back to empty dict if the file is missing or invalid.
_templates_path = Path(__file__).parent / "templates.json"
try:
    MODE_TEMPLATES: dict[str, list[str]] = json.loads(
        _templates_path.read_text(encoding="utf-8")
    )
except (FileNotFoundError, json.JSONDecodeError, OSError):
    MODE_TEMPLATES = {}

GATED_KEYWORDS = {
    "scraping": ["scrape", "crawl", "سكرابنج", "اسكراب", "استخرج"],
    "forums": ["forum", "reddit", "منتديات", "telegram", "تليجرام", "تيليجرام"],
    "dark": ["dark web", "دارك"],
    "restricted": ["login", "anti-bot", "captcha", "patchright", "skyvern"],
}


def infer_mode(query: str, profile: str | None = None) -> str:
    """Pick research mode from triggers; default depends on profile."""
    prof = _get_profile(profile)
    allowed = list(prof.get("allowed_modes", list(MODES)))
    default = str(prof.get("default_mode", "deep"))
    q = query.lower()
    for key in allowed:
        spec = MODES.get(key)
        if not spec:
            continue
        if any(tr in q for tr in spec["triggers"]):
            return key
    return default if default in allowed else (allowed[0] if allowed else "quick")


def clamp_mode(mode: str, profile: str | None = None) -> str:
    """Clamp an explicit mode into the profile allowlist."""
    prof = _get_profile(profile)
    allowed = list(prof.get("allowed_modes", list(MODES)))
    default = str(prof.get("default_mode", "deep"))
    if mode in allowed:
        return mode
    return default if default in allowed else (allowed[0] if allowed else "quick")


def detect_gates(query: str, profile: str | None = None) -> dict[str, bool]:
    prof = _get_profile(profile)
    if prof.get("name") == "institutional":
        return {gate: False for gate in GATED_KEYWORDS}
    q = query.lower()
    return {
        gate: any(kw in q for kw in kws)
        for gate, kws in GATED_KEYWORDS.items()
    }


def generate_subquestions(query: str, mode: str, n: int = 8) -> list[str]:
    """Per-mode sub-question plan. Compare splits 'X vs Y' into items."""
    raw = re.sub(
        r"(?i)^argus\s*:\s*(quick|compare|deep|platform|timebox\w*|"
        r"region\w*|narrow|سريع|قارن|مقارنة|عميق|منص[ةه]|وقت|زمن|منطقة|ضيق|محدد)?\s*",
        "",
        query,
    ).strip() or query
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
    to avoid report filename collisions.
    """
    s = re.sub(r"(?i)^argus\s*:\s*", "", text)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE).strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = s[:60].strip("-")
    if not s:
        s = f"argus-report-{uuid.uuid4().hex[:8]}"
    return s


def parse_limit(v: int, default: int = 20) -> int:
    """Clamp a preview limit into safe range [1, MAX_PREVIEW_LIMIT]."""
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
    """Collision-proof name: argus-report-{slug}-{YYYYMMDD}-{HHMMSS}-{rand6}.md."""
    ts = now or datetime.datetime.now(datetime.timezone.utc)
    stamp = ts.strftime("%Y%m%d-%H%M%S")
    rand = uuid.uuid4().hex[:6]
    return f"argus-report-{slugify(query)}-{stamp}-{rand}.md"


def atomic_write_text(path: Path, text: str) -> None:
    """Atomic write: tmp file + os.replace, never leaves half-files."""
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
    date = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    m = MODES[mode]
    consent_log = ", ".join(
        f"{k}={'Y' if v else 'N'}" for k, v in consents.items()
    )
    if consents.get("forums"):
        forums_note = "(TODO: per-item verdict VERIFIED / CONTESTED / UNVERIFIED)"
    else:
        forums_note = "_Skipped - no consent._"

    # YAML frontmatter
    waves_yaml = "\n".join(f"  - {w}" for w in waves)
    consents_yaml = "\n".join(
        f"  {k}: {'true' if v else 'false'}" for k, v in consents.items()
    )
    frontmatter = (
        "---\n"
        f"title: \"ARGUS: {query}\"\n"
        f"date: {date}\n"
        f"mode: {mode}\n"
        f"languages: {langs}\n"
        "waves:\n"
        f"{waves_yaml}\n"
        "consents:\n"
        f"{consents_yaml}\n"
        f"tool_version: \"{VERSION}\"\n"
        "---\n"
    )

    body = f"""# ARGUS: {query}
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
{forums_note}
## 10. Gaps and Open Questions
## 11. Key Sources (with URLs) - group by language
## 12. Methodology Notes
Consent log: {consent_log}. Tool: argus v1.1.0.
"""
    return frontmatter + body


def fetch_telegram_preview(channel: str, limit: int = 20) -> list[str]:
    """Public preview via t.me/s/ - no credentials needed.

    Strict channel validation + host pinning.
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
            return None  # disable automatic redirects

    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with opener.open(req, timeout=PREVIEW_TIMEOUT) as r:
            final_host = urllib.parse.urlparse(r.geturl()).hostname or ""
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
    raw = re.findall(r"tgme_widget_message_text[^>]*>(.*?)</div>", page, re.DOTALL)
    out = []
    for m in raw[:limit]:
        text = re.sub(r"<br\s*/?>", "\n", m)
        text = re.sub(r"<[^>]+>", "", text)
        text = htmlmod.unescape(text).strip()
        if text:
            # escape before embedding in Markdown output files
            out.append(htmlmod.escape(text))
    return out


def cmd_plan(args: argparse.Namespace) -> int:
    profile = getattr(args, "profile", "sovereign")
    raw = args.mode or infer_mode(args.query, profile)
    mode = clamp_mode(raw, profile)
    gates = detect_gates(args.query, profile)
    _logger.info("plan: mode=%s query=%r", mode, args.query)
    print(f"Mode: {MODES[mode]['name']}  |  Waves: {', '.join(MODES[mode]['waves'])}")
    print(f"Tools: {', '.join(MODES[mode]['tools'])}  |  Output: {MODES[mode]['words']} words")
    flagged = [g for g, v in gates.items() if v]
    if flagged:
        _logger.debug("plan: consent gates flagged: %s", flagged)
        print(f"Consent required before execution: {', '.join(flagged)} (default = SKIP)")
    subqs = generate_subquestions(args.query, mode)
    _logger.debug("plan: generated %d sub-questions for mode=%s", len(subqs), mode)
    print("\nSub-questions (approve / edit / change mode before execution):")
    for i, q in enumerate(subqs, 1):
        print(f"  {i}. {q}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    profile = getattr(args, "profile", "sovereign")
    raw = args.mode or infer_mode(args.query, profile)
    mode = clamp_mode(raw, profile)
    consents = {"scraping": False, "forums": False, "dark": False, "restricted": False}
    gates = detect_gates(args.query, profile)
    if not args.no_consent and sys.stdin.isatty():
        if gates["scraping"]:
            consents["scraping"] = ask_consent(
                "Scraping requested - scrape politely (public only)?"
            )
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
    _logger.info("report: written to %s mode=%s", path, mode)
    _logger.debug("report: consents=%s", consents)
    print(f"Report skeleton written: {path}")
    print(f"Consent log: {consents}")
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    limit = parse_limit(getattr(args, "limit", 20))
    try:
        msgs = fetch_telegram_preview(args.channel, limit)
    except ValueError as e:
        # invalid channel format - user error, no network attempted
        _logger.error("preview: invalid channel format: %s", e)
        print(f"{e}", file=sys.stderr)
        return 2
    except (urllib.error.URLError, urllib.error.HTTPError,
            TimeoutError, OSError, RuntimeError) as e:
        # Network / fetch failure - report plainly (no traceback leak)
        _logger.error("preview: fetch failed for %s: %s", args.channel, e)
        print(f"ERROR fetching preview: {e}", file=sys.stderr)
        return 1
    _logger.info("preview: fetched %d messages from t.me/s/%s", len(msgs), args.channel)
    print(f"Public preview: t.me/s/{args.channel} - {len(msgs)} messages (UNVERIFIED by default)")
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# Telegram preview: {htmlmod.escape(str(args.channel))}\n",
                 "_Source: public t.me/s/ preview. Claims = UNVERIFIED._\n"]
        lines += [f"\n---\n\n{m}\n" for m in msgs]
        atomic_write_text(out, "\n".join(lines))
        _logger.debug("preview: saved to %s", out)
        print(f"Saved: {out}")
    else:
        for m in msgs:
            print(f"\n---\n{m[:500]}")
    return 0


def cmd_modes(args: argparse.Namespace) -> int:
    profile = getattr(args, "profile", "sovereign")
    allowed = _allowed_modes(profile)
    for key in allowed:
        m = MODES[key]
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


def _check_url_live(url: str, timeout: int = VERIFY_TIMEOUT) -> str:
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
    """Throttled + capped liveness probe."""
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
                       profile: str | None = None,
                       max_workers: int = 8) -> tuple[str, list[dict]]:
    """Audit a report. Returns (verdict, findings). Verdict: PASS/WARN/FAIL.

    Delegates to check_structure / check_urls /
    check_citations / check_languages / check_consent + throttled liveness.
    Institutional profile keeps structure + links only (light audit).
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
    prof = _get_profile(profile)
    if prof.get("name") != "institutional":
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
        _logger.error("verify: file not found: %s", path)
        print(f"ERROR: not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    profile = getattr(args, "profile", "sovereign")
    require_log = bool(_get_profile(profile).get("require_consent_log", True))
    _logger.info("verify: auditing %s (offline=%s)", path, args.offline)
    verdict, findings = verify_report_text(
        text, check_links=not args.offline, profile=profile,
        require_consent_log=require_log)
    fails = sum(1 for f in findings if f["level"] == "FAIL")
    warns = sum(1 for f in findings if f["level"] == "WARN")
    _logger.debug("verify: %d findings (%d FAIL, %d WARN)", len(findings), fails, warns)
    for f in findings:
        print(f"[{f['level']:4s}] {f['check']:16s} {f['message']}")
    print(f"\nVerdict: {verdict} ({fails} FAIL, {warns} WARN)")
    return 0 if verdict == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="argus", description="ARGUS - verified research reports (CLI)"
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    p.add_argument("--profile", choices=["sovereign", "institutional"],
                   default="sovereign",
                   help="behaviour preset (default sovereign)")
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


def lite_main(argv: list[str] | None = None) -> int:
    """Institutional entry point: same CLI defaulting to institutional."""
    args = list(argv) if argv is not None else list(sys.argv[1:])
    if "--profile" not in args:
        args = ["--profile", "institutional", *args]
    return main(args)


if __name__ == "__main__":
    raise SystemExit(main())
