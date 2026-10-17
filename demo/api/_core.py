"""Shared helpers for the ARGUS demo API (Vercel Python serverless).

Security model for the public demo:
- Only `plan` and `report` are exposed. Both are pure local computation
  (no network, no cost, no SSRF surface).
- `verify --live-links` and Telegram `preview` are intentionally NOT
  exposed: they would let strangers make the server fetch arbitrary URLs.
- Input is strictly validated: query length cap, mode allowlist.
"""
from __future__ import annotations

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

from emo_argus import search as core

ALLOWED_MODES = ("quick", "compare", "deep", "platform",
                 "timeboxed", "regional", "narrow")
MAX_QUERY = 500


def read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0 or length > 4096:
        raise ValueError("bad request body")
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def validate(payload: dict) -> tuple[str, str]:
    query = str(payload.get("query", "")).strip()
    mode = str(payload.get("mode", "quick")).strip().lower()
    if not query:
        raise ValueError("query is required")
    if len(query) > MAX_QUERY:
        raise ValueError(f"query too long (max {MAX_QUERY} chars)")
    if mode not in ALLOWED_MODES:
        raise ValueError(f"unknown mode: {mode}")
    return query, mode


def send_json(handler: BaseHTTPRequestHandler, status: int, obj: dict) -> None:
    body = json.dumps(obj).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def save_demo(query: str, mode: str, plan: dict, report_md: str) -> str | None:
    """Persist a demo run to Supabase (best-effort; never breaks the demo)."""
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        return None
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/demos",
            data=json.dumps({
                "query": query, "mode": mode,
                "plan": plan, "report_md": report_md,
            }).encode("utf-8"),
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            rows = json.loads(r.read().decode("utf-8"))
        return rows[0]["id"] if rows else None
    except Exception:
        return None
