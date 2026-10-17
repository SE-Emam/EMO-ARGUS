# ARGUS live demo — Vercel + Supabase

Public demo of the [emo-argus](https://pypi.org/project/emo-argus/) core.
Exposes **only** `plan` and `report` (pure local computation). The network
features (`verify --live-links`, Telegram `preview`) are intentionally not
exposed — they would let strangers make the server fetch arbitrary URLs.

## Structure

```
api/_core.py    shared: validation, Supabase save (service_role, server-side only)
api/plan.py     POST /api/plan   -> plan JSON
api/report.py   POST /api/report -> report skeleton + share_id
api/config.py   GET  /api/config -> public Supabase URL + anon key (RLS-safe)
public/         static frontend (index.html demo, share.html shared reports)
supabase/schema.sql  demos table + RLS (public read, no public insert)
```

## Setup

1. **Supabase**: create a project → SQL editor → run `supabase/schema.sql`.
2. **Vercel**: import this folder (or the repo) → set env vars:
   - `SUPABASE_URL` — e.g. `https://xyz.supabase.co`
   - `SUPABASE_ANON_KEY` — public, used by share.html via `/api/config`
   - `SUPABASE_SERVICE_ROLE_KEY` — **server-side only**, used by `api/_core.py`
3. Deploy. The demo is at `/`, shared reports at `/share.html?id=<uuid>`.

## Security notes

- `service_role` key never touches the browser (only `_core.save_demo`).
- RLS: anon can `select`, cannot `insert` — writes go through the API.
- Query capped at 500 chars, mode allowlist enforced server-side.
- For production traffic, add Vercel Firewall / rate limiting on `/api/*`.
