"""POST /api/search -> live web search via Exa with research controls.

Self-contained (no sibling imports). The Exa API key lives only in the
server environment (EXA_API_KEY) and never reaches the browser.

Params (JSON):
  query     string, required, max 500 chars
  count     "10" | "25" | "50"            (default "25")
  category  "all" | "news" | "research" | "pdf" | "github" | "company" | "tweets"
  method    "auto" | "semantic" | "exact" (Exa auto / neural / keyword)
  lang      "auto" | "ar" | "en" | "both"
  region    "all" | "egypt" | "saudi" | "uae" | "qatar" | "morocco" | "usa" | "uk"
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

MAX_QUERY = 500
COUNTS = {"10": (10, 1200), "25": (25, 700), "50": (50, 400), "100": (100, 250)}
# Each category: exa_category and/or includeDomains for Exa, suffix appended
# to the query, or a dedicated handler (wikimedia needs no Exa key).
CATEGORIES = {
    "all":       {},
    "images":    {"handler": "wikimedia"},
    "video":     {"domains": ["youtube.com", "vimeo.com"]},
    "documents": {"exa_category": "pdf"},
    "data":      {"suffix": " dataset statistics data"},
    "apps":      {"domains": ["play.google.com", "apps.apple.com"]},
    "news":      {"exa_category": "news"},
    "research":  {"exa_category": "research paper"},
    "github":    {"exa_category": "github"},
    "company":   {"exa_category": "company"},
    "tweets":    {"exa_category": "tweet"},
}
METHODS = {"auto": "auto", "semantic": "neural", "exact": "keyword"}
LANGS = ("auto", "ar", "en", "both")
REGIONS = {
    "all": None,
    # Middle East
    "eg": "Egypt", "sa": "Saudi Arabia", "ae": "United Arab Emirates",
    "qa": "Qatar", "kw": "Kuwait", "bh": "Bahrain", "om": "Oman",
    "jo": "Jordan", "lb": "Lebanon", "iq": "Iraq", "tr": "Turkey",
    "ir": "Iran", "il": "Israel", "ye": "Yemen", "sy": "Syria",
    # Africa
    "ma": "Morocco", "dz": "Algeria", "tn": "Tunisia", "ly": "Libya",
    "sd": "Sudan", "ng": "Nigeria", "za": "South Africa", "ke": "Kenya",
    "et": "Ethiopia", "gh": "Ghana",
    # Europe
    "uk": "United Kingdom", "de": "Germany", "fr": "France",
    "es": "Spain", "it": "Italy", "nl": "Netherlands", "se": "Sweden",
    "no": "Norway", "pl": "Poland", "ua": "Ukraine", "ru": "Russia",
    "gr": "Greece", "pt": "Portugal", "ch": "Switzerland",
    "at": "Austria", "be": "Belgium", "dk": "Denmark", "fi": "Finland",
    "ie": "Ireland", "cz": "Czechia", "hu": "Hungary", "ro": "Romania",
    # Asia
    "cn": "China", "jp": "Japan", "kr": "South Korea", "in": "India",
    "pk": "Pakistan", "bd": "Bangladesh", "id": "Indonesia",
    "my": "Malaysia", "sg": "Singapore", "th": "Thailand",
    "vn": "Vietnam", "ph": "Philippines", "tw": "Taiwan",
    "hk": "Hong Kong",
    # Americas
    "us": "United States", "ca": "Canada", "mx": "Mexico",
    "br": "Brazil", "ag": "Argentina", "cl": "Chile",
    "co": "Colombia", "pe": "Peru",
    # Oceania
    "au": "Australia", "nz": "New Zealand",
}
AR_RE = re.compile(r"[\u0600-\u06FF]")


def _send(h, code, obj):
    body = json.dumps(obj).encode()
    h.send_response(code)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(body)))
    h.end_headers()
    h.wfile.write(body)


def _translate_ar_en(text):
    """Arabic -> English via the keyless Google endpoint. Raises on failure."""
    url = ("https://translate.googleapis.com/translate_a/single"
           "?client=gtx&sl=ar&tl=en&dt=t&q=" + urllib.parse.quote(text))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as r:
        d = json.loads(r.read().decode())
    out = "".join(seg[0] for seg in d[0] if seg and seg[0])
    if not out.strip():
        raise ValueError("empty translation")
    return out


def _exa_search(query, key, num, max_chars, exa_category, method, domains):
    payload = {
        "query": query,
        "numResults": num,
        "type": method,
        "contents": {
            "text": {"maxCharacters": max_chars},
            "highlights": True,
        },
    }
    if exa_category:
        payload["category"] = exa_category
    if domains:
        payload["includeDomains"] = domains
    req = urllib.request.Request(
        "https://api.exa.ai/search",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": key},
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode()).get("results", [])


def _wikimedia_search(query, num):
    """Image search via Wikimedia Commons (keyless, no Exa needed)."""
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
           "&generator=search&gsrnamespace=6&gsrlimit=" + str(min(num, 50)) +
           "&gsrsearch=" + urllib.parse.quote(query) +
           "&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=400")
    req = urllib.request.Request(url, headers={"User-Agent": "ARGUS-demo/1.0"})
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read().decode())
    out = []
    for p in (d.get("query", {}).get("pages") or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        thumb = ii.get("thumburl") or ii.get("url") or ""
        if not thumb:
            continue
        desc = ""
        em = ii.get("extmetadata") or {}
        if isinstance(em.get("ImageDescription"), dict):
            desc = re.sub(r"<[^>]+>", " ", em["ImageDescription"].get("value", ""))
            desc = re.sub(r"\s+", " ", desc).strip()[:300]
        out.append({
            "title": str(p.get("title", "")).replace("File:", "")[:150],
            "url": str(ii.get("descriptionurl", ""))[:500],
            "image": thumb[:500],
            "text": desc,
        })
    return out


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        t0 = time.time()
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return _send(self, 400, {"error": "invalid JSON"})
        query = str(data.get("query", ""))[:MAX_QUERY].strip()
        count = str(data.get("count", "25"))
        category = str(data.get("category", "all"))
        method = str(data.get("method", "auto"))
        lang = str(data.get("lang", "auto"))
        region = str(data.get("region", "all"))
        if not query:
            return _send(self, 400, {"error": "empty query"})
        if count not in COUNTS:
            return _send(self, 400, {"error": "bad count"})
        if category not in CATEGORIES or method not in METHODS:
            return _send(self, 400, {"error": "bad category/method"})
        if lang not in LANGS or region not in REGIONS:
            return _send(self, 400, {"error": "bad lang/region"})
        key = os.environ.get("EXA_API_KEY", "").strip()
        cat = CATEGORIES[category]
        num, max_chars = COUNTS[count]
        exa_method = METHODS[method]
        region_name = REGIONS[region]
        has_ar = bool(AR_RE.search(query))
        translated = None

        # Images go through Wikimedia Commons: keyless, no translation needed.
        if cat.get("handler") == "wikimedia":
            try:
                results = _wikimedia_search(query, num)
            except Exception:
                results = []
            out = [{
                "title": r["title"], "url": r["url"], "lang": "orig",
                "text": r["text"], "highlights": [], "image": r["image"],
            } for r in results]
            return _send(self, 200, {
                "results": out,
                "took_ms": int((time.time() - t0) * 1000),
                "translated_query": None,
            })

        if not key:
            return _send(self, 503, {"error": "live search is not configured yet"})

        # Build the list of (label, query) searches to run.
        queries = []
        if lang == "en" and has_ar:
            try:
                translated = _translate_ar_en(query)
                queries.append(("en", translated))
            except Exception:
                queries.append(("orig", query))
        elif lang == "both" and has_ar:
            queries.append(("ar", query))
            try:
                translated = _translate_ar_en(query)
                queries.append(("en", translated))
            except Exception:
                pass
        else:
            queries.append(("orig", query))
        aug = (cat.get("suffix", "") + (" in " + region_name if region_name else "")).strip()
        if aug:
            queries = [(lbl, (q + " " + aug)[:MAX_QUERY]) for lbl, q in queries]

        # Run sequentially with a time budget so the 10s function limit holds.
        seen, out = set(), []
        for lbl, q in queries:
            if time.time() - t0 > 7:
                break
            try:
                results = _exa_search(q, key, num, max_chars,
                                      cat.get("exa_category"), exa_method,
                                      cat.get("domains"))
            except Exception:
                continue
            for res in results:
                url = str(res.get("url", ""))
                if not url or url in seen:
                    continue
                seen.add(url)
                out.append({
                    "title": str(res.get("title", ""))[:200],
                    "url": url[:500],
                    "lang": lbl,
                    "text": str(res.get("text", ""))[:max_chars],
                    "highlights": [str(h)[:300] for h in res.get("highlights", [])[:3]],
                })
                if len(out) >= num * len(queries):
                    break
        _send(self, 200, {
            "results": out,
            "took_ms": int((time.time() - t0) * 1000),
            "translated_query": translated,
        })

    def log_message(self, *a):
        pass
