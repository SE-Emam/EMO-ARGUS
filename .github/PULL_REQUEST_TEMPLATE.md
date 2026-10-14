## What (user-visible value in 1-2 lines)

<!-- e.g. adds `argus preview --json` so agents can parse channel previews -->

## Hygiene (repo stays visitor-clean)

- [ ] `python scripts/check_hygiene.py` is green
- [ ] No new files in repo root outside the whitelist (`README.md`, `LICENSE`, `pyproject.toml`, `requirements.txt`, `src/emo_argus/`, `assets/images/ARGUS-banner.jpeg`, `docs/`, `scripts/`, `tests/`, `output/.gitkeep`)
- [ ] No internal codes in user-facing text (`S1/B6`, `Phase N`, `sovereign-grade`, `python argus_search.py`, `argus-search`)
- [ ] Canonical install intact: `pip install emo-argus` → `argus ...` commands
- [ ] `docs/CHANGELOG.md` updated if user behavior changed

## Quality

- [ ] `ruff check` clean
- [ ] `pytest -q` green (10/10 or more)
- [ ] `mcp_smoke_test.py` 3/3 (if MCP surface touched)

Full rules: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)
