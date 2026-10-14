# ARGUS Field Companions — Browser + Editor (Localhost Only)

> Institutional assistant: capture context and quick-verify snippets via your local ARGUS core. No external network, no collection tiers outside the CLI.

## Companions

- **Chrome** (`argus-chrome-extension/`): right-click selected text, side panel with Verify Snippet box.
- **VS Code** (`argus-vscode-extension/`): sidebar view, right-click selected text in the editor, offline audit plus 12-section report template.

Both talk to the same local bridge on `127.0.0.1` only. If the bridge is down, both show an offline message and send data nowhere else.

---

## Security Model

### Loopback-only

Both extensions enforce loopback destinations at the code level:

- The VS Code extension validates `argus.bridgeUrl` with `isLoopbackUrl()` before every request. Only `http://127.0.0.1`, `http://localhost`, and `http://[::1]` are accepted. Any other value (including `https://`) is refused with a warning and a one-click reset to the default.
- The Chrome extension's `manifest.json` restricts `host_permissions` to `http://127.0.0.1:*` only. The background script never issues requests to any other origin.

### Fail-safe offline

Every transport failure (connection refused, timeout, DNS error) surfaces as the same offline message: `ARGUS Bridge is offline. Please start the local server.` Neither extension retries against an alternate host or falls back to an external service.

### No external network

- Zero outbound requests except to the configured loopback bridge URL.
- No telemetry, no analytics, no update checks from the extension code itself.
- Page text lives in session storage only (Chrome) or in-memory log only (VS Code); it is never persisted to disk or sent anywhere other than the local bridge.
- The bridge token is the only persistent credential: stored in `chrome.storage.local` (Chrome) or `vscode.SecretStorage` (VS Code).

---

## Chrome Extension (`argus-chrome-extension/`)

### Features

- Right-click selected text on any page -> **Send to ARGUS** -> research plan appears in the side panel.
- Side panel shows bridge status, a **Verify Snippet** box (offline audit, no live fetch), and ephemeral captured context.
- Configurable bridge port via the options/settings area (defaults to `8765`).

### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Bridge port | `8765` | Port number for the local ARGUS bridge. Combined with `http://127.0.0.1` to form the full URL. |
| Bridge token | *(empty)* | Paste the token printed by `argus-bridge` at startup. Stored in `chrome.storage.local`. |

### CSP Policy

The manifest enforces a strict Content Security Policy:

```
"default-src 'self'; connect-src http://127.0.0.1:*; style-src 'self' 'unsafe-inline'; script-src 'self'"
```

This blocks inline scripts, external stylesheets, and any network request that is not directed at the loopback bridge.

### How to load unpacked

1. Open `chrome://extensions`.
2. Enable **Developer mode** (toggle in the top-right corner).
3. Click **Load unpacked**.
4. Select the `argus-chrome-extension/` directory.
5. Open the ARGUS side panel from the toolbar icon or right-click menu.
6. Paste the bridge token from `argus-bridge` into the token field.

### Development setup

```bash
# Start the bridge (prints a random token per boot)
argus-bridge

# Load the extension in Chrome (see above)
# Edit files in argus-chrome-extension/ and reload the extension
# from chrome://extensions after each change
```

No build step is required; the Chrome extension ships plain JS/HTML/CSS.

---

## VS Code Extension (`argus-vscode-extension/`)

### Features

- Sidebar view **ARGUS Companion**: bridge status indicator, recent-operations log (in-memory, max 20 entries), token hint.
- Status bar item shows bridge connectivity (online/offline) at a glance.
- Commands available from the Command Palette and editor context menu (on selection).

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `argus.bridgeUrl` | `http://127.0.0.1:8765` | Local ARGUS bridge URL. Must be loopback. Non-loopback values are blocked with a warning and one-click reset. |

### Token storage

The bridge token is stored exclusively in `vscode.SecretStorage`. It is never written to `settings.json`, workspace state, or any file on disk. Use the commands below to manage it:

- **ARGUS: Set Bridge Token** -- prompts for the token and stores it securely.
- **ARGUS: Clear Bridge Token** -- removes the stored token.

### Commands

| Command | Description |
|---------|-------------|
| `ARGUS: Check Bridge Connection` | `GET /health`, no auth. Updates status bar. |
| `ARGUS: Verify Selection (offline audit)` | `POST /verify-snippet`, capped at 2000 chars. |
| `ARGUS: Plan From Selection` | `POST /analyze`, capped at 2000 chars. |
| `ARGUS: Insert Report Template` | Inserts 12-section offline skeleton locally (no bridge call). |
| `ARGUS: Set Bridge Token` | Store token in SecretStorage. |
| `ARGUS: Clear Bridge Token` | Remove stored token. |

### Development setup

```bash
cd argus-vscode-extension
npm install
npm run compile    # or npm run watch for incremental builds
npm test           # runs unit tests for pure functions (node --test)
```

Press `F5` in VS Code to launch the Extension Development Host. Open the ARGUS activity-bar view and run **ARGUS: Set Bridge Token** with the token from `argus-bridge`.

### Building a VSIX

```bash
npm install -g @vscode/vsce
vsce package       # produces argus-vscode-companion-0.1.0.vsix
```

Install the resulting `.vsix` via `code --install-extension argus-vscode-companion-0.1.0.vsix` or through the Extensions panel -> **Install from VSIX...**.

---

## What it does

- Right-click any selected text -> **Send to ARGUS** -> local core returns a research plan (mode + sub-questions).
- Side panel / sidebar shows bridge status, a **Verify Snippet** box (offline audit, no live fetch), and ephemeral captured context (cleared with the session).
- If the bridge is down, the panel shows **ARGUS Core is offline** and sends data nowhere else.

## What it never does

- No scraping, no forums deep search, no login-bypass, no restricted collection tiers -- those stay in `argus` CLI / `argus-mcp` behind explicit consent.
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

3. Load the extension (Chrome or VS Code) and paste the `<TOKEN>`.

## Endpoints (bridge, `127.0.0.1` only)

- `GET /health` -- liveness, no auth.
- `POST /analyze` -- auth via `X-Argus-Token`; body `{selected_text, page_url, page_title}` (capped at 2000 chars); returns mode + sub-questions.
- `POST /verify-snippet` -- auth; body `{snippet}`; returns offline audit (structure, URL shape, citations).

## Files

### Chrome extension

- `argus-chrome-extension/manifest.json` -- Manifest V3, `permissions: contextMenus, sidePanel, storage`, `host_permissions: 127.0.0.1 only`, strict CSP.
- `argus-chrome-extension/background.js` -- context menu + loopback `fetch` + offline fail-safe.
- `argus-chrome-extension/sidepanel.html` + `sidepanel.js` -- status, token box, verify box, ephemeral log (`textContent` only, never raw HTML).

### VS Code extension

- `src/bridgeClient.ts` -- loopback-only `fetch` wrapper (`checkHealth` / `analyzeSelection` / `verifySnippet`), `isLoopbackUrl` + `normalizeBridgeUrl` guards, 2000-char cap, 401/offline mapping.
- `src/bridgeClient.test.ts` -- pure unit tests for `isLoopbackUrl` and `normalizeBridgeUrl` (no vscode dependency).
- `src/extension.ts` -- 6 commands, `SecretStorage` token, non-loopback refusal, `buildReportTemplate` 12-section skeleton mirroring core `build_report`.
- `src/sidebarProvider.ts` -- stateless webview (status + log, `escapeHtml`, no persistence).
- `package.json` -- `argus.bridgeUrl` default `http://127.0.0.1:8765`, views + menus, `main: ./out/extension.js`.

### Bridge (Python)

- `src/emo_argus/bridge.py` -- stdlib `http.server`, constant-time token check, 32KB body cap, binds `127.0.0.1` only.

Architecture: `docs/DECISIONS.md` (ADR-5). Contributing: `docs/CONTRIBUTING.md`.