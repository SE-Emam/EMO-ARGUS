"""POST /api/report -> {markdown, share_id}.

Generates the report skeleton (local compute only).
The browser stores it in localStorage; no server-side persistence.
Self-contained: no sibling imports (Vercel-safe).
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

from emo_argus import search as core

ALLOWED_MODES = ("quick", "compare", "deep", "platform",
                 "timeboxed", "regional", "narrow")
MAX_QUERY = 500


def _read_json(h: BaseHTTPRequestHandler) -> dict:
    length = int(h.headers.get("Content-Length") or 0)
    if length <= 0 or length > 4096:
        raise ValueError("bad request body")
    return json.loads(h.rfile.read(length).decode("utf-8"))


def _send(h: BaseHTTPRequestHandler, status: int, obj: dict) -> None:
    body = json.dumps(obj).encode("utf-8")
    h.send_response(status)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(body)))
    h.end_headers()
    h.wfile.write(body)


def _validate(payload: dict) -> tuple[str, str]:
    query = str(payload.get("query", "")).strip()
    mode = str(payload.get("mode", "quick")).strip().lower()
    if not query:
        raise ValueError("query is required")
    if len(query) > MAX_QUERY:
        raise ValueError(f"query too long (max {MAX_QUERY} chars)")
    if mode not in ALLOWED_MODES:
        raise ValueError(f"unknown mode: {mode}")
    return query, mode


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            query, mode = _validate(_read_json(self))
        except ValueError as e:
            _send(self, 400, {"error": str(e)})
            return
        report_md = core.build_report(
            query=query, mode=mode, langs="all-14",
            waves=core.MODES[mode]["waves"],
            consents={"scraping": False, "forums": False},
        )
        _send(self, 200, {"markdown": report_md})
