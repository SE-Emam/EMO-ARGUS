"""ARGUS local bridge — Secure Bridge Pattern (institutional assistant only).

Loopback ONLY: GET /health, POST /analyze, POST /verify-snippet.
Stdlib only. Institutional scope: plan + offline snippet audit.
Restricted tiers stay in CLI/MCP with consent gates — never in browser.
"""
from __future__ import annotations

import argparse
import datetime
import hmac
import json
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

import argus_search as core

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_TEXT = 2000
MAX_BODY = 32 * 1024
VERSION = core.VERSION
TOKEN = ""


def _is_http_url(value: str) -> bool:
    try:
        parts = urlparse(value)
        return parts.scheme in ("http", "https") and bool(parts.netloc)
    except (ValueError, TypeError, AttributeError):
        return False


def analyze_context(selected_text: str, page_url: str, page_title: str) -> dict:
    """Plan from captured context. No I/O, no fetch, JSON-safe dict."""
    text = (selected_text or "")[:MAX_TEXT]
    url = (page_url or "")[:MAX_TEXT]
    title = (page_title or "")[:500]
    if url and not _is_http_url(url):
        url = ""
    query = text.strip() or title.strip() or "quick page context"
    mode = core.infer_mode(query)
    plan = core.generate_subquestions(query, mode)
    message = None
    if text.strip() == "test":
        message = "Token verified, received: test"
    return {
        "tool": "argus",
        "version": VERSION,
        "message": message,
        "mode": mode,
        "mode_name": core.MODES[mode]["name"],
        "waves": core.MODES[mode]["waves"],
        "subquestions": plan,
        "received_chars": len(text),
        "page_url_ok": bool(url),
    }


def verify_snippet_offline(snippet: str) -> dict:
    """Fast offline audit: structure/URL/citation checks, no live fetch."""
    text = (snippet or "")[:MAX_TEXT]
    verdict, findings = core.verify_report_text(
        text, check_links=False, require_consent_log=False
    )
    urls = sorted({core._clean_url(u) for u in core.URL_RE.findall(text)})
    return {
        "tool": "argus",
        "version": VERSION,
        "verdict": verdict,
        "url_count": len(urls),
        "urls": urls[:10],
        "findings": findings,
        "note": "offline snippet audit — live checks stay in `argus verify`",
    }
class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "ARGUSBridge/0.1"

    def log_message(self, fmt: str, *args) -> None:
        pass

    def _send_json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Argus-Token")
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        given = self.headers.get("X-Argus-Token") or ""
        return bool(TOKEN) and hmac.compare_digest(given, TOKEN)

    def _read_json(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except (ValueError, TypeError):
            return None
        if length <= 0 or length > MAX_BODY:
            return None
        try:
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else None
        except (ValueError, UnicodeDecodeError, OSError):
            return None

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Argus-Token")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        if urlparse(self.path).path == "/health":
            self._send_json(200, {
                "status": "ok",
                "tool": "argus",
                "version": VERSION,
                "scope": "institutional-assistant (plan + offline verify only)",
                "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })
            return
        self._send_json(404, {"error": "unknown endpoint (see /health)"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path not in ("/analyze", "/verify-snippet"):
            self._send_json(404, {"error": "unknown endpoint (see /health)"})
            return
        if not self._authorized():
            self._send_json(401, {"error": "unauthorized — bad or missing token"})
            return
        data = self._read_json()
        if data is None:
            self._send_json(400, {"error": "invalid JSON body (object, max 32KB)"})
            return
        if path == "/analyze":
            if not isinstance(data.get("selected_text", ""), str):
                self._send_json(400, {"error": "selected_text must be a string"})
                return
            page_url = data.get("page_url", "")
            page_title = data.get("page_title", "")
            result = analyze_context(
                data.get("selected_text", ""),
                page_url if isinstance(page_url, str) else "",
                page_title if isinstance(page_title, str) else "",
            )
            self._send_json(200, result)
            return
        snippet = data.get("snippet", "")
        if not isinstance(snippet, str) or not snippet.strip():
            self._send_json(400, {"error": "snippet must be a non-empty string"})
            return
        self._send_json(200, verify_snippet_offline(snippet))


def build_server(port: int, token: str) -> HTTPServer:
    global TOKEN
    TOKEN = token
    return HTTPServer((HOST, port), BridgeHandler)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="argus-bridge", description="ARGUS local bridge (127.0.0.1 only)")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--token", default="", help="pre-shared token (default: random per boot)")
    args = p.parse_args(argv)
    token = args.token.strip() or secrets.token_urlsafe(32)
    server = build_server(args.port, token)
    print(f"ARGUS bridge on http://{HOST}:{args.port} (loopback only)")
    print(f"Bridge token (paste into the extension side panel): {token}")
    print("Scope: institutional-assistant — plan + offline verify only.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
