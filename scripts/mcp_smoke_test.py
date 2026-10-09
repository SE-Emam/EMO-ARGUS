#!/usr/bin/env python3
"""MCP smoke test protocol (sovereign deployment gate).

Runs WITHOUT the mcp package: imports core logic directly and exercises
the same code paths the MCP tools use (resolve_waves / report_filename /
_safe_output_path / atomic_write_text / fetch_telegram_preview validation).

Expected:
  1. Safe path   (./output/...)        -> PASS (accepted, file written)
  2. Traversal    (../../../tmp/evil)  -> PASS (refused with ERROR)
  3. Bad channel  (../../etc)          -> PASS (refused with ERROR)
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argus_search as core

results: list[str] = []


def record(name: str, ok: bool, detail: str) -> None:
    status = "PASS" if ok else "FAIL"
    results.append(f"[{status}] {name}: {detail}")
    print(results[-1])


def test_safe_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        fname = core.report_filename("smoke safe query")
        try:
            path = core._safe_output_path(base, fname)
            core.atomic_write_text(path, "# smoke\nConsent log: all=N\n")
            ok = path.is_file() and not list(base.glob("*.tmp-*"))
            record("safe-path", ok, f"written {path.name}, no tmp leftovers")
        except ValueError as e:
            record("safe-path", False, f"unexpected refusal: {e}")


def test_traversal_rejection() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for evil in ["../../../tmp/evil.md", "/etc/passwd", "../escape.md"]:
            try:
                core._safe_output_path(base, evil)
                record("traversal-rejection", False, f"ACCEPTED evil path {evil!r}")
                return
            except ValueError:
                continue
        record("traversal-rejection", True,
               "ERROR refused all evil paths (outside project)")


def test_channel_validation() -> None:
    bad_channels = ["../../etc", "evil.com/x", "ab", "a" * 65, "chan;rm"]
    refused = 0
    for ch in bad_channels:
        try:
            core.fetch_telegram_preview(ch, limit=1)
        except (ValueError, RuntimeError):
            refused += 1
    record("channel-validation", refused == len(bad_channels),
           f"ERROR Invalid channel format for {refused}/{len(bad_channels)} bad inputs")


def main() -> int:
    print("== ARGUS MCP smoke test ==")
    test_safe_path()
    test_traversal_rejection()
    test_channel_validation()
    fails = sum(1 for r in results if r.startswith("[FAIL]"))
    print(f"\nSummary: {len(results) - fails}/{len(results)} PASS")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
