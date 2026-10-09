"""ARGUS core tests (stdlib + pytest only)."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argus_search as core


def test_infer_mode_all_triggers_and_default():
    assert core.infer_mode("ARGUS: quick who is CEO") == "quick"
    assert core.infer_mode("قارن Notion ضد Obsidian") == "compare"
    assert core.infer_mode("deep quantum startups") == "deep"
    assert core.infer_mode("platform AI agents on Twitter") == "platform"
    assert core.infer_mode("timebox EU AI Act 2024-2026") == "timeboxed"
    assert core.infer_mode("region AI market in Africa") == "regional"
    assert core.infer_mode("narrow pricing of Stripe") == "narrow"
    # ambiguous -> Deep default
    assert core.infer_mode("something totally vague here") == "deep"


def test_split_compare_items_separators():
    assert core.split_compare_items("Notion vs Obsidian") == ["Notion", "Obsidian"]
    assert core.split_compare_items("أ vs ب") == ["أ", "ب"]
    assert core.split_compare_items("X مقابل Y") == ["X", "Y"]
    assert core.split_compare_items("X ضد Y") == ["X", "Y"]
    assert core.split_compare_items("cats or dogs") == ["cats", "dogs"]


def test_slugify_arabic_symbols_uuid_fallback():
    assert core.slugify("ARGUS: deep بحث عميق") == "deep-بحث-عميق"
    assert core.slugify("Hello World!") == "hello-world"
    fallback = core.slugify("!!! ??? ...")
    assert fallback.startswith("argus-report-") and len(fallback) > len("argus-report-")
    # two fallbacks must differ (no silent collisions)
    assert core.slugify("!!!") != core.slugify("???")


def test_detect_gates_four_keywords():
    gates = core.detect_gates("scrape the site + reddit threads + dark web + login bypass")
    assert gates == {"scraping": True, "forums": True, "dark": True, "restricted": True}
    clean = core.detect_gates("compare Notion vs Obsidian")
    assert clean == {"scraping": False, "forums": False, "dark": False, "restricted": False}


def test_parse_limit_clamps():
    assert core.parse_limit(-5) == 1
    assert core.parse_limit(0) == 1
    assert core.parse_limit(20) == 20
    assert core.parse_limit(100000) == core.MAX_PREVIEW_LIMIT
    assert core.parse_limit("bad") == 20


def test_resolve_waves_dry():
    base = core.resolve_waves("compare", {"dark": False, "restricted": False})
    assert base == ["Wave 1", "Wave 2", "Wave 4"]
    gated = core.resolve_waves("deep", {"dark": True, "restricted": True})
    assert gated[-2:] == ["Wave 6", "Wave 7"]


def test_channel_validation_rejects_injection():
    for bad in ["../../etc", "evil.com/x", "ab", "a" * 65, "chan;rm", "chan name"]:
        with pytest.raises((ValueError, RuntimeError)):
            core.fetch_telegram_preview(bad, limit=1)


def test_safe_output_path_rejects_escape(tmp_path):
    ok = core._safe_output_path(tmp_path, "argus-report-test.md")
    assert ok.parent == tmp_path.resolve()
    with pytest.raises(ValueError):
        core._safe_output_path(tmp_path, "../escape.md")
    with pytest.raises(ValueError):
        core._safe_output_path(tmp_path, "/etc/passwd")


def test_verify_rejects_report_without_urls_or_consent():
    body = "\n".join([f"## {i}. {s}\ncontent here" for i, s in enumerate(core.FULL_SECTIONS, 1)])
    verdict, findings = core.verify_report_text(body, check_links=False,
                                                require_consent_log=True)
    assert verdict == "FAIL"
    checks = {f["check"] for f in findings if f["level"] == "FAIL"}
    assert "urls" in checks
    assert "consent-log" in checks


def test_report_filename_unique_and_atomic(tmp_path):
    f1 = core.report_filename("same query")
    f2 = core.report_filename("same query")
    assert f1 != f2  # no same-day overwrite collisions
    assert re.fullmatch(r"argus-report-.+-\d{8}-\d{6}-[0-9a-f]{6}\.md", f1)
    target = tmp_path / f1
    core.atomic_write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"
    assert list(tmp_path.glob("*.tmp-*")) == []  # no tmp leftovers
