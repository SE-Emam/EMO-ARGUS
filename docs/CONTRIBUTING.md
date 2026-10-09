# Contributing to ARGUS — Keep the Repo Visitor-Clean

> Golden rule: **a visitor sees value in 10 seconds.** Anything for maintainers, agents, or internal tasks belongs in `docs/` or `scripts/`, never in the root.

## 1) Where Do Files Go?

| Type | Correct place | Forbidden |
|---|---|---|
| Visitor-facing (install, value, demo) | `README.md` only | Instruction files in root |
| Agent spec / advanced detail | `docs/` | Any new `*.md` in root |
| Verification / smoke scripts | `scripts/` | Temp files in root |
| Tests | `tests/` | — |
| Generated reports | `output/` (ignored, only `.gitkeep` stays) | Committing generated `*.md` reports |
| Architecture / decisions | `docs/DECISIONS.md` (add a new ADR) | Scattered decision comments in code |

Allowed root only:

```
README.md  LICENSE  pyproject.toml  requirements.txt
argus_search.py  argus_mcp.py  argus_bridge.py  ARGUS-banner.jpeg
argus-chrome-extension/  argus-vscode-extension/  docs/  scripts/  tests/  output/.gitkeep  .github/  .gitignore
```

Any file outside this list (`SHA256SUMS`, `dist/`, `*.egg-info/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`) is rejected in CI.

> Extension veto (binding): `argus-chrome-extension/` and `argus-vscode-extension/` are institutional assistants only — `host_permissions` / `bridgeUrl` loopback-only (`127.0.0.1:8765`), strict Manifest V3 for Chrome, VS Code token in `SecretStorage` only, no restricted collection tiers outside the CLI. Enforced by `check_extension_veto` in `scripts/check_hygiene.py`.

## 2) Visitor Language (No AI Slop, English-Only UI)

Banned in any user-facing file (`README.md`, `docs/*.md` except allowlisted i18n data, `argus_*.py --help`, `pyproject.toml`, both extensions):

- `python argus_search.py` → use `argus ...`
- `argus-search` → correct is `emo-argus` for the distribution and `argus` for the command
- `sovereign-grade` / `sovereign deployment gate`
- Internal codes: `(S1)` `(B6)` `Phase 1/2` `DRY` `God-function`
- `[Y]` → use explicit `Y` or `yes`

Language policy:

- Visitor UI is **English only**. No Arabic or CJK script in `README.md`, `docs/CONTRIBUTING.md`, `docs/EXTENSION.md`, `docs/CHANGELOG.md`, `docs/DECISIONS.md`, `docs/USER_GUIDE.md`, both extensions, or the bridge.
- Only allowlisted functional i18n data may contain non-Latin script: `argus_search.py` mode triggers + split regex, and `docs/SKILL.md` language table + trigger lists (14-language coverage is the product). Everything else must stay ASCII/Latin.
- Enforced by `check_language_veto` in `scripts/check_hygiene.py`.

Before any PR, run:

```bash
python scripts/check_hygiene.py
```

## 3) Canonical Commands

- Only legal install: `pip install emo-argus`
- Commands after install: `argus plan|report|preview|modes|verify` + `argus-mcp` + `argus-bridge`
- `pyproject.toml`: marketing `description`, `keywords` present, `project.urls` (Homepage/Docs/Repo/Changelog) intact
- Core stays dependency-free: `dependencies = []` — any new dependency needs an ADR

## 4) Protected Workflow (Never Push to main Directly)

```bash
git checkout develop
# ... edit ...
python scripts/check_hygiene.py
python -m ruff check .
python -m pytest tests/ -q
python scripts/mcp_smoke_test.py
git commit -m "feat(scope): what + why"
git push origin develop
gh pr create --base main --head develop
# wait for green CI -> squash merge -> sync develop
```

## 5) PR Checklist (Also in the Template)

- [ ] `python scripts/check_hygiene.py` is green
- [ ] `ruff` + `pytest 10/10` + `smoke 3/3`
- [ ] No new files in root outside the whitelist
- [ ] No internal terms in user-facing text
- [ ] `README.md` still: 30-second install + value + 60-second demo
- [ ] `docs/CHANGELOG.md` updated if user behavior changed

## 6) Task and Fix Files Stay Local (Never in the Repo)

- Internal task lists, fix notes, session logs, delivery zips, `SHA256SUMS`, `dist/`, `*.egg-info/` stay on your machine only. Never `git add` them.
- The hygiene gate fails on `SHA256SUMS`, `dist/`, `build/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.venv/` anywhere in the tree.
- If you need to share a task file, paste it in the PR description or chat — do not commit it.

