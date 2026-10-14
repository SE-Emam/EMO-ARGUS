# ARGUS Analyst Companion (VS Code)

Localhost-only VS Code extension for the ARGUS research integrity core. Verify snippets, plan from selected code, and insert report templates -- all through your local ARGUS bridge on `127.0.0.1`. No external network, no telemetry.

## Install

### From VSIX

```bash
npm install -g @vscode/vsce
cd argus-vscode-extension
vsce package
code --install-extension argus-vscode-companion-0.1.0.vsix
```

Or use the Extensions panel: **Install from VSIX...** and select the `.vsix` file.

### From Marketplace

Search for **ARGUS Analyst Companion** in the VS Code Extensions panel and click Install.

### Development (Extension Development Host)

```bash
cd argus-vscode-extension
npm install
npm run compile   # or npm run watch
npm test          # unit tests for pure functions
```

Press `F5` to launch the Extension Development Host.

## Commands

| Command | Description |
|---------|-------------|
| `ARGUS: Check Bridge Connection` | Ping `GET /health` (no auth). Updates status bar indicator. |
| `ARGUS: Verify Selection (offline audit)` | Send selected text to `POST /verify-snippet`. Returns verdict, URL count, findings. Capped at 2000 chars. |
| `ARGUS: Plan From Selection` | Send selected text to `POST /analyze`. Returns mode + sub-questions. Capped at 2000 chars. |
| `ARGUS: Insert Report Template` | Insert a 12-section offline report skeleton at the cursor. No bridge call. |
| `ARGUS: Set Bridge Token` | Prompt for the bridge token and store it in SecretStorage. |
| `ARGUS: Clear Bridge Token` | Remove the stored bridge token. |

Commands are available from the Command Palette (`Ctrl+Shift+P`) and from the editor context menu when text is selected.

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `argus.bridgeUrl` | `http://127.0.0.1:8765` | Local ARGUS bridge URL. Must be loopback (`127.0.0.1`, `localhost`, or `::1`). Non-loopback values are refused with a warning and one-click reset. |

## Status Bar

A status bar item displays bridge connectivity:

- **ARGUS: Online** -- bridge responded to the last health check.
- **ARGUS: Offline** -- bridge is unreachable. All operations fail safe with an offline message.

The indicator updates automatically on each command and can be refreshed manually via `ARGUS: Check Bridge Connection`.

## Security

- **Loopback validation**: `isLoopbackUrl()` rejects any non-loopback `argus.bridgeUrl` before every request. Only `http://127.0.0.1`, `http://localhost`, and `http://[::1]` are accepted. HTTPS is rejected.
- **SecretStorage**: the bridge token is stored exclusively in `vscode.SecretStorage`. It is never written to `settings.json`, workspace state, or any file on disk.
- **Fail-safe offline**: every transport failure (connection refused, timeout, DNS error) surfaces as `ARGUS Bridge is offline. Please start the local server.` No fallback to external services.
- **No external network**: zero outbound requests except to the configured loopback bridge. No telemetry, analytics, or update checks.
- **In-memory only**: captured text lives in an in-memory log (max 20 entries) and is cleared when VS Code closes. Nothing is persisted except the bridge token.

## Prerequisites

```bash
pip install emo-argus
argus-bridge   # prints a random token per boot
```

Run `ARGUS: Set Bridge Token` in VS Code and paste the printed token.