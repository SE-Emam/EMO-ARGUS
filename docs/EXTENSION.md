# ARGUS Field Companions — Browser + Editor (Localhost Only)

> Institutional assistant: capture context and quick-verify snippets via your local ARGUS core. No external network, no collection tiers outside the CLI.

## Companions

- Chrome (`argus-chrome-extension/`): right-click selected text, side panel with Verify Snippet box.
- VS Code (`argus-vscode-extension/`): sidebar view, right-click selected text in the editor, offline audit plus 12-section report template.

Both talk to the same local bridge on `127.0.0.1` only. If the bridge is down, both show an offline message and send data nowhere else.

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
- `src/emo_argus/bridge.py` — stdlib `http.server`, constant-time token check, 32KB body cap, binds `127.0.0.1` only.

## VS Code companion (`argus-vscode-extension/`)

Thin client over the same bridge — no new collection logic.

- Sidebar view `ARGUS Companion`: bridge status dot, recent-operations log (in-memory, max 20), token hint.
- Commands (Command Palette + right-click on selection):
  - `ARGUS: Check Bridge Connection` — `GET /health`, no auth.
  - `ARGUS: Verify Selection (offline audit)` — `POST /verify-snippet`, capped at 2000 chars.
  - `ARGUS: Plan From Selection` — `POST /analyze`, capped at 2000 chars.
  - `ARGUS: Insert Report Template` — inserts the 12-section offline skeleton locally (no bridge call).
  - `ARGUS: Set/Clear Bridge Token` — token lives in `vscode.SecretStorage` only, never in settings or workspace state.
- Safety: `argus.bridgeUrl` defaults to `http://127.0.0.1:8765`; any non-loopback value is refused with a warning + one-click reset. When the bridge is down every call fails safe with `ARGUS Bridge is offline. Please start the local server.`

### VS Code setup (2 minutes)

1. Same bridge as Chrome (loopback only):

```bash
argus-bridge
# prints: Bridge token (paste into VS Code via ARGUS: Set Bridge Token): <TOKEN>
```

2. Open `argus-vscode-extension/` in VS Code → `npm install` → `npm run compile` → press `F5` (Extension Development Host) → open the ARGUS activity-bar view → run `ARGUS: Set Bridge Token` and paste `<TOKEN>`.

### VS Code files

- `src/bridgeClient.ts` — loopback-only `fetch` wrapper (`checkHealth` / `analyzeSelection` / `verifySnippet`), `isLoopbackUrl` + `normalizeBridgeUrl` guards, 2000-char cap, 401/offline mapping.
- `src/extension.ts` — 6 commands, `SecretStorage` token, non-loopback refusal, `buildReportTemplate` 12-section skeleton mirroring core `build_report`.
- `src/sidebarProvider.ts` — stateless webview (status + log, `escapeHtml`, no persistence).
- `package.json` — `argus.bridgeUrl` default `http://127.0.0.1:8765`, views + menus, `main: ./out/extension.js`.

Architecture: `docs/DECISIONS.md` (ADR-5). Contributing: `docs/CONTRIBUTING.md`.
