# ARGUS Field Companion — Chrome Extension (Localhost Only)

> Institutional assistant: capture page context and quick-verify snippets via your local ARGUS core. No external network, no collection tiers in the browser.

## What it does

- Right-click any selected text → **Send to ARGUS** → local core returns a research plan (mode + sub-questions).
- Side panel shows bridge status, a **Verify Snippet** box (offline audit, no live fetch), and ephemeral captured context (cleared with the session).
- If the bridge is down, the panel shows **ARGUS Core is offline** and sends data nowhere else.

## What it never does

- No scraping, no forums deep search, no login-bypass, no restricted collection tiers — those stay in `argus` CLI / `argus-mcp` behind explicit consent.
- No external network: the only allowed host is `http://127.0.0.1:8765/*`.
- No persistent page text: context lives in session storage only; only the bridge token persists on your machine.

## Setup (2 minutes)

1. Install the package (zero-dependency core):

```bash
pip install emo-argus
argus modes
```

2. Start the local bridge (loopback only, random token per boot):

```bash
argus-bridge
# prints: Bridge token (paste into the extension side panel): <TOKEN>
```

3. Load the extension in Developer Mode:
   - Open `chrome://extensions` → enable **Developer mode** → **Load unpacked** → select `argus-chrome-extension/`.
   - Open the ARGUS side panel, paste the `<TOKEN>` from step 2.

## Use it

- Select text on any page → right-click → **Send to ARGUS** → plan appears in the panel log.
- Or paste a paragraph/URL into **Verify Snippet** → **Verify Snippet** → offline verdict (`PASS` / `WARN` / `FAIL`) + URL count + findings.
- Live link checks stay in the CLI: `argus verify ./output/argus-report-*.md`.

## Endpoints (bridge, `127.0.0.1` only)

- `GET /health` — liveness, no auth.
- `POST /analyze` — auth via `X-Argus-Token`; body `{selected_text, page_url, page_title}` (capped at 2000 chars); returns mode + sub-questions.
- `POST /verify-snippet` — auth; body `{snippet}`; returns offline audit (structure, URL shape, citations).

## Files

- `argus-chrome-extension/manifest.json` — Manifest V3, `permissions: contextMenus, sidePanel, storage`, `host_permissions: 127.0.0.1 only`, strict CSP.
- `argus-chrome-extension/background.js` — context menu + loopback `fetch` + offline fail-safe.
- `argus-chrome-extension/sidepanel.html` + `sidepanel.js` — status, token box, verify box, ephemeral log (`textContent` only, never raw HTML).
- `argus_bridge.py` — stdlib `http.server`, constant-time token check, 32KB body cap, binds `127.0.0.1` only.

Architecture: `docs/DECISIONS.md` (ADR-5). Contributing: `docs/CONTRIBUTING.md`.
