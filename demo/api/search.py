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
COUNTS = {"10": (10, 1200), "25": (25, 700), "50": (50, 400)}
CATEGORIES = {
    "all": None, "news": "news", "research": "research paper",
    "pdf": "pdf", "github": "github", "company": "company",
    "tweets": "tweet",
}
METHODS = {"auto": "auto", "semantic": "neural", "exact": "keyword"}
LANGS = ("auto", "ar", "en", "both")
REGIONS = {
    "all": None, "egypt": "Egypt", "saudi": "Saudi Arabia",
    "uae": "United Arab Emirates", "qatar": "Qatar",
    "morocco": "Morocco", "usa": "United States", "uk": "United Kingdom",
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


def _exa_search(query, key, num, max_chars, category, method):
    payload = {
        "query": query,
        "numResults": num,
        "type": method,
        "contents": {
            "text": {"maxCharacters": max_chars},
            "highlights": True,
        },
    }
    if category:
        payload["category"] = category
    req = urllib.request.Request(
        "https://api.exa.ai/search",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": key},
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode()).get("results", [])


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
        if not key:
            return _send(self, 503, {"error": "live search is not configured yet"})

        num, max_chars = COUNTS[count]
        exa_cat = CATEGORIES[category]
        exa_method = METHODS[method]
        region_name = REGIONS[region]
        has_ar = bool(AR_RE.search(query))
        translated = None

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
        if region_name:
            queries = [(lbl, q + " in " + region_name) for lbl, q in queries]

        # Run sequentially with a time budget so the 10s function limit holds.
        seen, out = set(), []
        for lbl, q in queries:
            if time.time() - t0 > 7:
                break
            try:
                results = _exa_search(q, key, num, max_chars, exa_cat, exa_method)
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
