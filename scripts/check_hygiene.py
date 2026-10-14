"""ARGUS repo hygiene gate — keeps the visitor view clean.

Fails (exit 1) on:
  1. Root whitelist violation (junk / temp / instruction files in root).
  2. AI-slop / internal codes in user-facing files.
  2b. Language veto (non-Latin script outside allowlisted i18n data).
  3. Canonical install/command drift.
  4. Extension veto (browser/editor stay loopback-only institutional assistants).

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
    "assets",
    "src",
    "argus-chrome-extension",
    "argus-vscode-extension",
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
    r"python\s+src/emo_argus/search\.py",
    r"python\s+-m\s+emo_argus",
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
USER_FACING_SKIP_DIRS = {
    ".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv", "venv", "dist", "build",
    "node_modules", "out", ".vscode"}
# Extension + bridge files scanned too (visitor-facing institutional scope).
USER_FACING_SUFFIXES = {"py", "md", "toml", "txt", "yml", "js", "json", "html", "ts"}
# Sovereign features must NEVER appear in the browser extension or bridge.
SOVEREIGN_PATTERNS = [
    r"dark[_ ]?web",
    r"\bTor\b",
    r"\bonion\b",
    r"SQLi",
    r"XSS\s+payload",
    r"reverse[_ ]shell",
    r"privilege escalation",
    r"metasploit",
    r"\bnmap\b",
    r"\bburp\b",
]
# These files document the banned list itself — skip them in the slop scan.
SLOP_ALLOWLIST_FILES = {
    "docs/CONTRIBUTING.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "scripts/check_hygiene.py",
}
# Per-pattern exceptions: deliberate UI, not slop.
# - [Y] in SKILL.md lives ONLY inside verbatim consent-question templates
#   (the `Y`/`N` option labels the user actually sees and types).
SLOP_FILE_OVERRIDES: dict[str, set[str]] = {
    r"\[Y\]": {"docs/SKILL.md"},
}

# 2b) Language veto: visitor UI stays English-only (Latin script).
# Only allowlisted functional i18n data may carry non-Latin script:
#   - src/emo_argus/search.py (mode triggers + split regex — 14 langs)
#   - docs/SKILL.md (language table + trigger lists)
#   - tests/test_core.py (i18n behaviour assertions)
# Everything else must not contain Arabic or CJK characters.
LANGUAGE_VETO_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]"
)
LANGUAGE_VETO_ALLOW = {
    "src/emo_argus/search.py",
    "docs/SKILL.md",
    "tests/test_core.py",
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
        if path.suffix.lstrip(".") not in USER_FACING_SUFFIXES:
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


def check_extension_veto() -> None:
    """Architectural veto: browser + editor sides stay institutional-only, loopback-only."""
    ext = ROOT / "argus-chrome-extension"
    vs = ROOT / "argus-vscode-extension"
    bridge = ROOT / "src" / "emo_argus" / "bridge.py"
    ok = True
    if not ext.is_dir():
        fail("extension scaffold missing: argus-chrome-extension/")
        return
    for name in ("manifest.json", "background.js", "sidepanel.html", "sidepanel.js"):
        if not (ext / name).is_file():
            fail(f"extension scaffold missing file: argus-chrome-extension/{name}")
            ok = False
    if not vs.is_dir():
        fail("vscode scaffold missing: argus-vscode-extension/")
        return
    for name in ("package.json", "tsconfig.json", "src/extension.ts",
                 "src/bridgeClient.ts", "src/sidebarProvider.ts"):
        if not (vs / name).is_file():
            fail(f"vscode scaffold missing file: argus-vscode-extension/{name}")
            ok = False
    if not bridge.is_file():
        fail("bridge missing: src/emo_argus/bridge.py")
        ok = False
        return
    # 1) Sovereign terms must never appear in extension, vscode, or bridge.
    # Skip generated/vendor dirs (node_modules, out) — they are never shipped.
    compiled = [(p, re.compile(p, re.IGNORECASE)) for p in SOVEREIGN_PATTERNS]
    skip_parts = {"node_modules", "out", ".vscode"}
    scan_roots = [bridge, *(ext.rglob("*") if ext.is_dir() else []),
                  *(vs.rglob("*") if vs.is_dir() else [])]
    for path in scan_roots:
        if not path.is_file():
            continue
        if any(part in skip_parts for part in path.parts):
            continue
        if path.suffix.lstrip(".") not in USER_FACING_SUFFIXES:
            continue
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for raw, rx in compiled:
            if rx.search(text):
                fail(f"architectural veto: sovereign term `{raw}` in {rel}")
                ok = False
    # 2) Loopback-only: bridge binds 127.0.0.1, manifest allows only it.
    try:
        btext = bridge.read_text(encoding="utf-8")
    except OSError:
        btext = ""
    if 'HOST = "127.0.0.1"' not in btext or "0.0.0.0" in btext:
        fail("bridge must bind 127.0.0.1 only (never 0.0.0.0)")
        ok = False
    try:
        import json as _json
        manifest = _json.loads((ext / "manifest.json").read_text(encoding="utf-8"))
    except (ValueError, OSError):
        manifest = {}
    hosts = manifest.get("host_permissions", [])
    if hosts != ["http://127.0.0.1:8765/*"]:
        fail(f"manifest host_permissions must be exactly loopback bridge, got {hosts}")
        ok = False
    if manifest.get("manifest_version") != 3:
        fail("manifest must be Manifest V3")
        ok = False
    # 3) VS Code thin-client veto: loopback default + SecretStorage token.
    if not ok:
        # still run vscode checks to surface all failures at once
        pass
    try:
        import json as _vjson
        pkg = _vjson.loads((vs / "package.json").read_text(encoding="utf-8"))
    except (ValueError, OSError):
        pkg = {}
    try:
        vs_default = (pkg.get("contributes", {}).get("configuration", {})
                      .get("properties", {}).get("argus.bridgeUrl", {}).get("default", ""))
    except AttributeError:
        vs_default = ""
    if vs_default != "http://127.0.0.1:8765":
        fail(f"vscode bridgeUrl default must be loopback, got {vs_default!r}")
        ok = False
    try:
        bctext = (vs / "src" / "bridgeClient.ts").read_text(encoding="utf-8")
        extext = (vs / "src" / "extension.ts").read_text(encoding="utf-8")
        vstext = bctext + "\n" + extext
    except OSError:
        vstext = ""
        bctext = ""
        extext = ""
    if "DEFAULT_BRIDGE_URL = 'http://127.0.0.1:8765'" not in bctext:
        fail("vscode bridgeClient must pin DEFAULT_BRIDGE_URL to 127.0.0.1:8765")
        ok = False
    if "SecretStorage" not in extext and "secrets.store" not in extext:
        fail("vscode token must live in SecretStorage (secrets.store)")
        ok = False
    if "workspaceState" in extext and "bridgeToken" in extext:
        fail("vscode token must never live in workspaceState")
        ok = False
    if "X-Argus-Token" not in vstext:
        fail("vscode must send X-Argus-Token header")
        ok = False
    if "isLoopbackUrl" not in vstext:
        fail("vscode must gate non-loopback URLs via isLoopbackUrl")
        ok = False
    if "ARGUS Bridge is offline" not in vstext:
        fail("vscode must fail-safe with offline message")
        ok = False
    if ok:
        print("[PASS] extension-veto: institutional-only, loopback-only, MV3 strict")


def check_language_veto() -> None:
    """Visitor UI stays English-only: no Arabic/CJK outside allowlisted i18n data."""
    ok = True
    skip_dirs = USER_FACING_SKIP_DIRS | {".git", "output", "TEx_config"}
    for path in ROOT.rglob("*"):
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            continue
        if any(part in skip_dirs or part in FORBIDDEN_ANYWHERE for part in rel.parts):
            continue
        if not path.is_file():
            continue
        if str(rel) in LANGUAGE_VETO_ALLOW:
            continue
        if path.suffix.lower() not in (
            ".py", ".md", ".toml", ".txt", ".yml", ".yaml",
            ".js", ".json", ".html", ".ts",
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        m = LANGUAGE_VETO_RE.search(text)
        if m:
            line = text[: m.start()].count("\n") + 1
            fail(f"language veto: {rel}:{line} carries non-Latin script "
                 f"(visitor UI is English-only; allowlisted: {sorted(LANGUAGE_VETO_ALLOW)})")
            ok = False
    if ok:
        print("[PASS] language-veto: visitor UI English-only (i18n data allowlisted)")


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
    check_language_veto()
    check_extension_veto()
    check_canonicals()
    if failures:
        print(f"\nResult: {len(failures)} hygiene failure(s) — fix before PR")
        return 1
    print("\nResult: HYGIENE PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
