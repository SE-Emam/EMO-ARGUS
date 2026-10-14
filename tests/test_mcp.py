"""Unit tests for ARGUS MCP server tools.

Tests call the underlying core functions directly rather than going through
the MCP protocol, so they exercise the same logic without requiring a
running MCP server.  The mcp package itself is optional; tests are skipped
when it is not installed.
"""
from __future__ import annotations

import shutil
import sys
import uuid
from pathlib import Path

import pytest

# Skip entire module when the mcp extra is not installed.
pytest.importorskip("mcp")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from emo_argus import search as core  # noqa: E402
from emo_argus.mcp import (  # noqa: E402
    generate_report,
    list_modes,
    plan_research,
    telegram_preview,
    verify_report,
)


# ------------------------------------------------------------------ #
# list_modes
# ------------------------------------------------------------------ #
def test_list_modes_returns_all_seven():
    result = list_modes()
    assert isinstance(result, str)
    lines = [ln for ln in result.strip().splitlines() if ln.strip()]
    assert len(lines) == 7, f"Expected 7 modes, got {len(lines)}"
    # Every known mode name should appear in the output.
    for key in core.MODES:
        assert core.MODES[key]["name"] in result


# ------------------------------------------------------------------ #
# plan_research
# ------------------------------------------------------------------ #
def test_plan_research_valid_query_returns_subquestions():
    result = plan_research("ARGUS: compare Notion vs Obsidian", mode="compare")
    assert "Sub-questions:" in result
    assert "Mode: Compare" in result
    # At least one numbered sub-question present.
    assert "1." in result


def test_plan_research_invalid_mode_returns_error():
    result = plan_research("some query", mode="nonexistent_mode")
    assert result.startswith("ERROR:")
    assert "nonexistent_mode" in result


# ------------------------------------------------------------------ #
# generate_report
# ------------------------------------------------------------------ #
def test_generate_report_writes_file():
    # _safe_path rejects paths outside CWD, so use a project-local dir.
    outdir = Path.cwd() / f".test_output_{uuid.uuid4().hex[:8]}"
    try:
        result = generate_report(
            query="ARGUS: quick test report",
            mode="quick",
            output_dir=str(outdir),
        )
        assert "Report skeleton written:" in result
        files = list(outdir.rglob("*"))
        assert len(files) >= 1, "generate_report should create at least one file"
    finally:
        shutil.rmtree(outdir, ignore_errors=True)


# ------------------------------------------------------------------ #
# telegram_preview
# ------------------------------------------------------------------ #
def test_telegram_preview_invalid_channel_returns_error():
    # Channel names must match ^[A-Za-z0-9_]{5,64}$; "!bad!" is invalid.
    result = telegram_preview(channel="!bad!")
    # The function returns the ValueError message text (no traceback).
    assert "invalid" in result.lower() or "error" in result.lower() or "channel" in result.lower()


# ------------------------------------------------------------------ #
# verify_report
# ------------------------------------------------------------------ #
def test_verify_report_nonexistent_file_returns_error():
    # _safe_path rejects paths outside CWD, so reference a nonexistent
    # file inside the project root.
    fake = str(Path.cwd() / f".nonexistent_{uuid.uuid4().hex[:8]}.md")
    result = verify_report(file=fake)
    assert "ERROR" in result
    assert "not found" in result.lower() or "nonexistent" in result
