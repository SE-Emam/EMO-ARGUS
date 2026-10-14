# ARGUS Chrome Extension

Localhost-only companion for the ARGUS research integrity core. Capture selected text from any page and send it to your local ARGUS bridge for analysis or offline snippet verification. No external network, no telemetry.

## Install (load unpacked)

1. Open `chrome://extensions`.
2. Enable **Developer mode** (top-right toggle).
3. Click **Load unpacked**.
4. Select this directory (`argus-chrome-extension/`).
5. The ARGUS icon appears in the toolbar; click it or right-click selected text to open the side panel.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Bridge port | `8765` | Port for the local ARGUS bridge (default `8765`). Custom ports require updating `host_permissions` in `manifest.json` to match. |
| Bridge token | *(empty)* | Token printed by `argus-bridge` at startup. Paste it into the side panel token field. Stored in `chrome.storage.local`. |

## Usage

- **Send to ARGUS**: select text on any page, right-click, choose **Send to ARGUS**. A research plan (mode + sub-questions) appears in the side panel.
- **Verify Snippet**: paste a paragraph or URL into the Verify Snippet box in the side panel. Returns an offline verdict (`PASS` / `WARN` / `FAIL`), URL count, and findings. No live fetch is performed.
- **Bridge status**: the side panel shows whether the local bridge is reachable. If offline, all operations display `ARGUS Core is offline` and send data nowhere.

## Security

- **Loopback only**: `host_permissions` in `manifest.json` restricts all network requests to `http://127.0.0.1:8765/*`. The background script never contacts any other origin.
- **Strict CSP**: `"script-src 'self'; object-src 'self'; base-uri 'self'; connect-src http://127.0.0.1:8765; img-src 'self' data:; style-src 'self'; font-src 'self'"`. No inline styles or scripts, no external resources. All CSS is loaded from `sidepanel.css`.
- **Fail-safe offline**: connection errors surface as an offline message. No fallback to external services.
- **No persistent page data**: captured text lives in session storage only and is cleared when the browser session ends. Only the bridge token persists.
- **No telemetry**: zero analytics, tracking, or update checks from the extension code.

## Prerequisites

```bash
pip install emo-argus
argus-bridge   # prints a random token per boot
```

## Development

No build step required. Edit the JS/HTML/CSS files directly and reload the extension from `chrome://extensions` after each change.