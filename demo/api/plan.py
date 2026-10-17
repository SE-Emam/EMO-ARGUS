"""POST /api/plan -> {mode, mode_name, waves, subquestions, gates}"""
from http.server import BaseHTTPRequestHandler

from _core import ALLOWED_MODES, read_json, send_json, validate
from emo_argus import search as core


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            query, mode = validate(read_json(self))
        except ValueError as e:
            send_json(self, 400, {"error": str(e)})
            return
        gates = core.detect_gates(query)
        send_json(self, 200, {
            "mode": mode,
            "mode_name": core.MODES[mode]["name"],
            "waves": core.MODES[mode]["waves"],
            "words": core.MODES[mode]["words"],
            "subquestions": core.generate_subquestions(query, mode),
            "gates": [g for g, v in gates.items() if v],
        })

    def do_GET(self):
        send_json(self, 200, {"modes": list(ALLOWED_MODES)})
