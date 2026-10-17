"""GET /api/config -> public Supabase URL + anon key (safe: RLS protects data)."""
import os
from http.server import BaseHTTPRequestHandler

from _core import send_json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        send_json(self, 200, {
            "supabase_url": os.environ.get("SUPABASE_URL", ""),
            "anon_key": os.environ.get("SUPABASE_ANON_KEY", ""),
        })
