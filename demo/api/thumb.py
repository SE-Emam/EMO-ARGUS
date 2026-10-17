"""GET /api/thumb?url=... -> thumbnail proxy.

The browser never talks to third parties directly (anti-tracking): images
are fetched server-side and relayed. Only Wikimedia image hosts are allowed,
so this cannot be abused as an open proxy (no SSRF).
"""
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

ALLOWED = {"upload.wikimedia.org", "thumb.wikimedia.org"}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.urlparse(self.path).query
        url = urllib.parse.parse_qs(q).get("url", [""])[0]
        try:
            u = urllib.parse.urlparse(url)
            ok = u.scheme == "https" and (u.hostname or "") in ALLOWED
        except Exception:
            ok = False
        if not ok:
            self.send_response(400)
            self.end_headers()
            return
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "ARGUS-demo/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                ctype = r.headers.get("Content-Type", "")
                if not ctype.startswith("image/"):
                    raise ValueError("not an image")
                data = r.read(5 * 1024 * 1024)
        except Exception:
            self.send_response(502)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "public, max-age=86400")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass
