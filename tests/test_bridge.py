"""Bridge unit tests — loopback-only institutional scope."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from emo_argus import bridge


def test_analyze_test_word_returns_verification_message():
    out = bridge.analyze_context("test", "https://example.com/a", "Example")
    assert out["message"] == "Token verified, received: test"
    valid_modes = ("quick", "compare", "deep", "platform", "timeboxed")
    valid_modes += ("regional", "narrow")
    assert out["mode"] in valid_modes
    assert isinstance(out["subquestions"], list) and out["subquestions"]


def test_analyze_truncates_long_selection():
    out = bridge.analyze_context("x" * 5000, "https://example.com/", "T")
    assert out["received_chars"] == bridge.MAX_TEXT


def test_analyze_rejects_malformed_page_url():
    out = bridge.analyze_context("some context", "not a url at all", "T")
    assert out["page_url_ok"] is False


def test_verify_snippet_offline_shape():
    out = bridge.verify_snippet_offline("Claim here https://example.com/source")
    assert out["verdict"] in ("PASS", "WARN", "FAIL")
    assert out["url_count"] >= 1
    assert isinstance(out["findings"], list)
