"""POST /api/search -> live web search via Exa.

Self-contained (no sibling imports). The Exa API key lives only in the
server environment (EXA_API_KEY) and never reaches the browser.
"""
import json
import os
import time
import urllib.request
from http.server import BaseHTTPRequestHandler

MAX_QUERY = 500
DEPTHS = {
    "quick": {"numResults": 5, "maxChars": 800},
    "deep": {"numResults": 8, "maxChars": 1500},
}


def _send(h, code, obj):
    body = json.dumps(obj).encode()
    h.send_response(code)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(body)))
    h.end_headers()
    h.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return _send(self, 400, {"error": "invalid JSON"})
        query = str(data.get("query", ""))[:MAX_QUERY].strip()
        depth = str(data.get("depth", "quick"))
        if not query:
            return _send(self, 400, {"error": "empty query"})
        if depth not in DEPTHS:
            return _send(self, 400, {"error": "bad depth"})
        key = os.environ.get("EXA_API_KEY", "").strip()
        if not key:
            return _send(self, 503, {"error": "live search is not configured yet"})
        cfg = DEPTHS[depth]
        payload = json.dumps({
            "query": query,
            "numResults": cfg["numResults"],
            "contents": {
                "text": {"maxCharacters": cfg["maxChars"]},
                "highlights": True,
            },
        }).encode()
        req = urllib.request.Request(
            "https://api.exa.ai/search",
            data=payload,
            headers={"Content-Type": "application/json", "x-api-key": key},
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                d = json.loads(r.read().decode())
        except Exception:
            return _send(self, 502, {"error": "search provider unreachable"})
        out = []
        for res in d.get("results", [])[: cfg["numResults"]]:
            out.append({
                "title": str(res.get("title", ""))[:200],
                "url": str(res.get("url", ""))[:500],
                "text": str(res.get("text", ""))[: cfg["maxChars"]],
                "highlights": [str(h)[:300] for h in res.get("highlights", [])[:3]],
            })
        _send(self, 200, {
            "results": out,
            "took_ms": int((time.time() - t0) * 1000),
        })

    def log_message(self, *a):
        pass
