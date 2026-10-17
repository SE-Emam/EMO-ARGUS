"""Security regression tests — path traversal, YAML injection, bridge auth."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from emo_argus import bridge, search

# The mcp extra is optional: import emo_argus.mcp lazily (it raises
# SystemExit at import when the third-party `mcp` package is missing).
def _mcp_module():
    pytest.importorskip("mcp", reason="mcp extra not installed")
    from emo_argus import mcp as mcp_mod
    return mcp_mod


# --- path traversal guards -------------------------------------------------

@pytest.mark.parametrize("evil", [
    "../../../etc/passwd",
    "subdir/../../../../tmp/x",
    "/absolute/path/evil.md",
])
def test_safe_output_path_rejects_traversal(tmp_path, evil):
    with pytest.raises(ValueError):
        search._safe_output_path(tmp_path, evil)


def test_safe_output_path_accepts_normal(tmp_path):
    p = search._safe_output_path(tmp_path, "report.md")
    assert p.parent == tmp_path.resolve()


def test_mcp_safe_path_locked_to_cwd(tmp_path, monkeypatch):
    mcp = _mcp_module()
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        mcp._safe_path("../escape.md")
    ok = mcp._safe_path("notes.md")
    assert ok.parent == tmp_path.resolve()


# --- YAML frontmatter injection --------------------------------------------

def _frontmatter_lines(report: str) -> list[str]:
    return report.split("---")[1].strip().splitlines()


def _build_evil_report(query: str) -> str:
    return search.build_report(
        query=query, mode="quick", langs="en", waves=["w1"], consents={})


def test_report_title_cannot_inject_yaml_keys():
    evil = 'x"\nmalicious: true\ninjected: "y'
    lines = _frontmatter_lines(_build_evil_report(evil))
    keys = [ln.split(":", 1)[0].strip() for ln in lines
            if not ln.startswith((" ", "-"))]
    assert "malicious" not in keys
    assert "injected" not in keys


def test_report_title_is_single_line_no_quotes():
    lines = _frontmatter_lines(
        _build_evil_report('line1\nline2\rline3"quoted"'))
    title = next(ln for ln in lines if ln.startswith("title:"))
    assert title.count('"') == 2  # only the wrapping quotes survive
    assert "\n" not in title and "\r" not in title


# --- telegram parser robustness --------------------------------------------

def test_tgme_parser_handles_nested_markup():
    html = (
        '<div class="tgme_widget_message_text js-message_text">'
        "Hello <b>bold <i>nested</i></b> world<br>second line"
        '<div class="inner">inner div content</div> tail</div>'
    )
    p = search._TgmeMessageParser()
    p.feed(html)
    assert len(p.messages) == 1
    assert "nested" in p.messages[0]
    assert "inner div content" in p.messages[0]
    assert "second line" in p.messages[0]
    assert "\n" in p.messages[0]  # <br> became a newline


def test_tgme_parser_ignores_other_divs():
    p = search._TgmeMessageParser()
    p.feed('<div class="other">nope</div>'
           '<div class="tgme_widget_message_text">yes</div>')
    assert p.messages == ["yes"]


def test_tgme_parser_self_closing_br():
    p = search._TgmeMessageParser()
    p.feed('<div class="tgme_widget_message_text">a<br/>b</div>')
    assert p.messages == ["a\nb"]


# --- bridge auth surface ----------------------------------------------------

def test_bridge_token_env_precedence():
    # Mirror of main()'s precedence: --token > $ARGUS_BRIDGE_TOKEN > random.
    def pick(cli: str, env: str) -> str:
        return cli.strip() or env.strip() or "random"
    assert pick("", "env-secret") == "env-secret"
    assert pick("cli-token", "env-secret") == "cli-token"
    assert pick("  ", "  ") == "random"


def test_bridge_build_server_takes_token():
    server = bridge.build_server(0, "env-secret-token")
    try:
        assert bridge.TOKEN == "env-secret-token"
    finally:
        server.server_close()


def test_analyze_context_never_leaks_debug():
    out = bridge.analyze_context("test", "https://example.com/", "T")
    assert out["message"] is None
