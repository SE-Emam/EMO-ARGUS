"""POST /api/report -> {markdown, share_id} (skeleton only, saved to Supabase)."""
from http.server import BaseHTTPRequestHandler

from _core import read_json, save_demo, send_json, validate
from emo_argus import search as core


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            query, mode = validate(read_json(self))
        except ValueError as e:
            send_json(self, 400, {"error": str(e)})
            return
        plan = {
            "mode": mode,
            "waves": core.MODES[mode]["waves"],
            "subquestions": core.generate_subquestions(query, mode),
        }
        report_md = core.build_report(
            query=query, mode=mode, langs="all-14",
            waves=core.MODES[mode]["waves"],
            consents={"scraping": False, "forums": False},
        )
        share_id = save_demo(query, mode, plan, report_md)
        send_json(self, 200, {"markdown": report_md, "share_id": share_id})
