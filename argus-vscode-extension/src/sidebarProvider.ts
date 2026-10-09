/**
 * ARGUS sidebar — status dot, log list, token hint.
 * Stateless view: no page text persisted, log kept in memory only.
 */
import * as vscode from 'vscode';

export class ArgusSidebarProvider implements vscode.WebviewViewProvider {
  private view?: vscode.WebviewView;
  private online = false;
  private status = 'Not checked — run ARGUS: Check Bridge Connection.';
  private log: string[] = [];

  constructor(private readonly root: vscode.Uri) {}

  resolveWebviewView(view: vscode.WebviewView): void {
    this.view = view;
    view.webview.options = { enableScripts: true, localResourceRoots: [this.root] };
    this.render();
  }

  setStatus(online: boolean, text: string): void {
    this.online = online;
    this.status = text;
    this.render();
  }

  pushLog(line: string): void {
    const stamp = new Date().toISOString().slice(11, 19);
    this.log.unshift(`[${stamp}] ${line}`);
    this.log = this.log.slice(0, 20);
    this.render();
  }

  private render(): void {
    if (!this.view) {
      return;
    }
    const dot = this.online ? '#2da44e' : '#cf222e';
    const items = this.log.length
      ? this.log.map((l) => `<li>${escapeHtml(l)}</li>`).join('')
      : '<li class="hint">No operations yet — select text, right-click, Verify with ARGUS.</li>';
    this.view.webview.html = [
      '<!DOCTYPE html><html><head><meta charset="utf-8">',
      '<style>body{font-family:var(--vscode-font-family);font-size:12px;padding:10px;}',
      '.row{display:flex;align-items:center;gap:8px;margin-bottom:8px;}',
      '.hint{color:var(--vscode-descriptionForeground);}ul{padding-left:16px;}li{margin-bottom:4px;word-break:break-word;}</style>',
      '</head><body>',
      `<div class="row"><span style="width:10px;height:10px;border-radius:50%;background:${dot};display:inline-block"></span><strong>ARGUS Bridge</strong></div>`,
      `<div class="hint">${escapeHtml(this.status)}</div>`,
      '<h4>Recent</h4><ul>' + items + '</ul>',
      '<div class="hint">Token lives in SecretStorage only. Bridge: 127.0.0.1:8765.</div>',
      '</body></html>',
    ].join('');
  }
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
