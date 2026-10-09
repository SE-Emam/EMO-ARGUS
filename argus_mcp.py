"""ARGUS MCP server - verified research plans for AI agents.

Tools:
  list_modes        - the 7 research modes
  plan_research     - infer mode, flag consent gates, show sub-questions
  generate_report   - write report skeleton (all consents default False = SKIP)
  telegram_preview  - public t.me/s/ preview (UNVERIFIED by default)
  verify_report     - audit a finished report (links, citations, languages)

Safety: MCP is non-interactive, so every consent defaults to False.
Pass True only after explicit user approval obtained OUTSIDE this server.

Run on stdio/localhost ONLY. Never expose
this server to a network socket without authentication + TLS + allowlist,
because generate_report / verify_report perform filesystem I/O.
"""
from __future__ import annotations

from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # graceful message when extra not installed
    raise SystemExit("mcp package missing: pip install 'emo-argus[mcp]'")

import argus_search as core

mcp = FastMCP("argus")


def _safe_path(path: str | Path) -> Path:
    """Refuse path escape - resolved path must stay inside CWD.

    Used by generate_report (output_dir) and verify_report (file).
    Rejects '..' segments and absolute paths outside the project.
    """
    base = Path.cwd().resolve()
    candidate = Path(path).resolve()
    if not candidate.is_relative_to(base):
        raise ValueError(f"Refused path outside project: {path!r}")
    return candidate


@mcp.tool()
def list_modes() -> str:
    """List the 7 ARGUS research modes with waves and output size."""
    lines = []
    for m in core.MODES.values():
        lines.append(
            f"{m['name']}: triggers={m['triggers']}, "
            f"waves={m['waves']}, output={m['words']} words"
        )
    return "\n".join(lines)


@mcp.tool()
def plan_research(query: str, mode: str = "") -> str:
    """Infer mode, flag consent gates, and return the sub-question plan.

    Args:
        query: e.g. 'ARGUS: compare Notion vs Obsidian'
        mode: optional override (quick/compare/deep/platform/timeboxed/regional/narrow)
    """
    key = (mode or core.infer_mode(query)).lower()
    if key not in core.MODES:
        return f"ERROR: unknown mode '{mode}'. Valid: {sorted(core.MODES)}"
    m = core.MODES[key]
    gates = core.detect_gates(query)
    flagged = [g for g, v in gates.items() if v]
    out = [
        f"Mode: {m['name']} | Waves: {', '.join(m['waves'])} | Output: {m['words']} words",
        f"Tools: {', '.join(m['tools'])}",
    ]
    if flagged:
        out.append(f"Consent required (default SKIP): {', '.join(flagged)}")
    out.append("Sub-questions:")
    for i, q in enumerate(core.generate_subquestions(query, key), 1):
        out.append(f"  {i}. {q}")
    return "\n".join(out)


@mcp.tool()
def generate_report(
    query: str,
    mode: str = "",
    langs: str = "all-14",
    output_dir: str = "./output",
    scraping: bool = False,
    forums: bool = False,
    dark: bool = False,
    restricted: bool = False,
) -> str:
    """Write a report skeleton. ALL consents default False (SKIP).

    Set a consent True ONLY after explicit user approval obtained outside MCP.
    """
    key = (mode or core.infer_mode(query)).lower()
    if key not in core.MODES:
        return f"ERROR: unknown mode '{mode}'. Valid: {sorted(core.MODES)}"
    consents = {
        "scraping": scraping,
        "forums": forums,
        "dark": dark,
        "restricted": restricted,
    }
    waves = core.resolve_waves(key, consents)
    body = core.build_report(query, key, langs, waves, consents)
    try:
        outdir = _safe_path(output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        fname = core.report_filename(query)
        path = core._safe_output_path(outdir, fname)
        core.atomic_write_text(path, body)
    except ValueError as e:
        return f"ERROR: {e}"
    return f"Report skeleton written: {path}\nConsent log: {consents}"


@mcp.tool()
def telegram_preview(channel: str, limit: int = 20) -> str:
    """Public Telegram preview via t.me/s/ (no credentials). Claims = UNVERIFIED."""
    try:
        msgs = core.fetch_telegram_preview(channel, core.parse_limit(limit))
    except ValueError as e:
        # S1: invalid channel format - no network attempted
        return f"{e}"
    except (RuntimeError, OSError) as e:
        # Network / fetch failure surfaced as text (no traceback leak)
        return f"ERROR fetching preview: {e}"
    out = [
        f"Public preview: t.me/s/{channel} - {len(msgs)} messages (UNVERIFIED by default)"
    ]
    out += [f"\n---\n{m[:1000]}" for m in msgs]
    return "\n".join(out)


@mcp.tool()
def verify_report(file: str, offline: bool = False) -> str:
    """Audit a finished Markdown report (structure, dead links, uncited claims, languages).

    Args:
        file: path to the report file (must resolve inside CWD - S3)
        offline: skip live link checks when True
    """
    try:
        path = _safe_path(file)
    except ValueError as e:
        return f"ERROR: {e}"
    if not path.is_file():
        return f"ERROR: not found: {file}"
    text = path.read_text(encoding="utf-8")
    verdict, findings = core.verify_report_text(
        text, check_links=not offline, require_consent_log=True)
    lines = [f"[{f['level']:4s}] {f['check']:16s} {f['message']}" for f in findings]
    fails = sum(1 for f in findings if f["level"] == "FAIL")
    warns = sum(1 for f in findings if f["level"] == "WARN")
    lines.append(f"\nVerdict: {verdict} ({fails} FAIL, {warns} WARN)")
    return "\n".join(lines)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
