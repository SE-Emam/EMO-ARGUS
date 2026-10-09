"""ARGUS repo hygiene gate — keeps the visitor view clean.

Fails (exit 1) on:
  1. Root whitelist violation (junk / temp / instruction files in root).
  2. AI-slop / internal codes in user-facing files.
  3. Canonical install/command drift.

Usage: python scripts/check_hygiene.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 1) Only these may live in the repo root (files + dirs).
ALLOWED_ROOT = {
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "requirements.txt",
    "argus_search.py",
    "argus_mcp.py",
    "ARGUS-banner.jpeg",
    "docs",
    "scripts",
    "tests",
    "output",
    ".github",
    ".gitignore",
    ".gitattributes",
}

# Hard junk — must never be committed, even if gitignored.
FORBIDDEN_ANYWHERE = {
    "SHA256SUMS",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
}

# 2) Slop / internal codes banned from user-facing text.
SLOP_PATTERNS = [
    r"python\s+argus_search\.py",
    r"argus-search",
    r"sovereign-grade",
    r"sovereign deployment gate",
    r"\(S\d\)",
    r"\(B\d\)",
    r"Phase\s+[0-9]",
    r"\[Y\]",
    r"God-function",
    r"/DRY\)",
    r"\(B\d+/DRY\)",
]

USER_FACING_GLOBS = ["*.py", "*.md", "*.toml", "*.txt", "*.yml"]
USER_FACING_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv", "venv", "dist", "build"}
# These files document the banned list itself — skip them in the slop scan.
SLOP_ALLOWLIST_FILES = {
    "docs/CONTRIBUTING.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "scripts/check_hygiene.py",
}
# Per-pattern exceptions: deliberate UI, not slop.
# - [Y] in SKILL.md lives ONLY inside verbatim consent-question templates
#   (the `Y`/`N` option labels the user actually sees and types).
# - `python argus_search.py` in CI tests the source file pre-install
#   (no installed `argus` entry point exists yet at that step).
SLOP_FILE_OVERRIDES: dict[str, set[str]] = {
    r"\[Y\]": {"docs/SKILL.md"},
    r"python\s+argus_search\.py": {".github/workflows/ci.yml"},
}

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"[FAIL] {msg}")


def check_root_whitelist() -> None:
    ok = True
    for entry in ROOT.iterdir():
        if entry.name in FORBIDDEN_ANYWHERE:
            fail(f"root junk forbidden: {entry.name} (remove it, never commit)")
            ok = False
        elif entry.name not in ALLOWED_ROOT and not entry.name.startswith("."):
            # Allow hidden tooling (.github is allowed; other dotfiles flagged softly)
            if entry.name not in {".github", ".gitignore", ".gitattributes"}:
                fail(f"root whitelist violation: {entry.name} → move to docs/ or scripts/")
                ok = False
    # Forbidden dirs anywhere (top-level check is enough for the gate)
    for junk in ("dist", "build", "__pycache__", ".pytest_cache", ".ruff_cache"):
        if (ROOT / junk).exists():
            fail(f"build artifact present: {junk}/ (delete before commit)")
            ok = False
    for egg in ROOT.glob("*.egg-info"):
        fail(f"build artifact present: {egg.name}/ (delete before commit)")
        ok = False
    if ok:
        print("[PASS] root-whitelist: repo root is visitor-clean")


def check_slop() -> None:
    compiled = [(p, re.compile(p)) for p in SLOP_PATTERNS]
    hits = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(skip in path.parts for skip in USER_FACING_SKIP_DIRS):
            continue
        if path.suffix.lstrip(".") not in {"py", "md", "toml", "txt", "yml"}:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in SLOP_ALLOWLIST_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for raw, rx in compiled:
            if rel in SLOP_FILE_OVERRIDES.get(raw, set()):
                continue
            if rx.search(text):
                fail(f"slop pattern `{raw}` in {rel}")
                hits += 1
    if hits == 0:
        print("[PASS] slop-scan: no internal codes / AI slop in user-facing files")


def check_canonicals() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    ok = True
    if "pip install emo-argus" not in readme:
        fail("README must contain canonical `pip install emo-argus`")
        ok = False
    if "argus modes" not in readme:
        fail("README must show `argus modes` as first command")
        ok = False
    if 'name = "emo-argus"' not in pyproject:
        fail('pyproject name must stay "emo-argus" (argus is taken on PyPI)')
        ok = False
    if "dependencies = []" not in pyproject:
        fail("core must stay zero-dependency (dependencies = []) or add an ADR")
        ok = False
    if ok:
        print("[PASS] canonicals: install line + dist name + zero-dep core intact")


def main() -> int:
    print("== ARGUS hygiene gate ==")
    check_root_whitelist()
    check_slop()
    check_canonicals()
    if failures:
        print(f"\nResult: {len(failures)} hygiene failure(s) — fix before PR")
        return 1
    print("\nResult: HYGIENE PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
