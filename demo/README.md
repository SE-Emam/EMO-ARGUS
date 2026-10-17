# ARGUS live demo — Vercel

Public demo of the [emo-argus](https://pypi.org/project/emo-argus/) core.
Exposes **only** `plan` and `report` (pure local computation). The network
features (`verify --live-links`, Telegram `preview`) are intentionally not
exposed — they would let strangers make the server fetch arbitrary URLs.

Generated reports are stored in the **visitor's browser** (`localStorage`,
capped at 20). Nothing is stored server-side — no database, no accounts,
no tracking.

## Structure

```
api/plan.py     POST /api/plan   -> plan JSON
api/report.py   POST /api/report -> report skeleton markdown
public/         static frontend (index.html demo + history, share.html viewer)
```

Each file in `api/` is self-contained (no sibling imports — Vercel-safe).

## Deploy

Import this folder on Vercel (or deploy the files via the API, see
`DEPLOY_RUNBOOK.md`). No env vars needed.

## Security notes

- Query capped at 500 chars, mode allowlist enforced server-side.
- Report markdown is rendered with `textContent`/escaping — no HTML injection.
- For production traffic, add Vercel Firewall / rate limiting on `/api/*`.
