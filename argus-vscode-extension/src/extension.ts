/** ARGUS thin client — loopback only, SecretStorage token, fail-safe offline. */
import * as vscode from 'vscode';
import { DEFAULT_BRIDGE_URL, OFFLINE_MESSAGE, analyzeSelection, checkHealth, isLoopbackUrl, normalizeBridgeUrl, verifySnippet } from './bridgeClient';
import { ArgusSidebarProvider } from './sidebarProvider';
const TOKEN_KEY = 'argus.bridgeToken';
const MAX_TEXT = 2000;
function bridgeUrl(): string {
  return normalizeBridgeUrl(vscode.workspace.getConfiguration('argus').get<string>('bridgeUrl', DEFAULT_BRIDGE_URL));
}
function allowLoopback(url: string): boolean {
  if (isLoopbackUrl(url)) { return true; }
  void vscode.window.showWarningMessage(`ARGUS refused non-loopback URL (${url}). Must stay 127.0.0.1.`, 'Reset to loopback').then((c) => {
    if (c === 'Reset to loopback') { void vscode.workspace.getConfiguration('argus').update('bridgeUrl', DEFAULT_BRIDGE_URL, true); }
  });
  return false;
}
async function token(s: vscode.SecretStorage): Promise<string> {
  return (await s.get(TOKEN_KEY))?.trim() ?? '';
}
export function buildReportTemplate(topic: string): string {
  const clean = (topic || 'Research question').trim().slice(0, 200);
  const date = new Date().toISOString().slice(0, 10);
  const secs = ['Executive Summary', 'Background and Definitions', 'Key Actors / Items Compared', 'Verified Findings', 'Contested Claims and Disagreements', 'Geographic and Regional Specifics', 'Technical Landscape', 'Market and Opportunity Signals', 'Community Signals - Forums & Telegram', 'Gaps and Open Questions', 'Key Sources (with URLs)', 'Methodology Notes'];
  const out = [`# ARGUS: ${clean}`, `**Date**: ${date} | **Mode**: deep | **Languages**: en+ar`, ''];
  secs.forEach((s, i) => { out.push(`## ${i + 1}. ${s}`, '(TODO: cited content)', ''); });
  out.push('Consent log: scraping=N, forums=N, dark=N, restricted=N. Tool: argus.');
  return out.join('\n');
}
export function activate(ctx: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel('ARGUS');
  const sidebar = new ArgusSidebarProvider(ctx.extensionUri);
  ctx.subscriptions.push(vscode.window.registerWebviewViewProvider('argus.sidebar', sidebar), output);
  const check = vscode.commands.registerCommand('argus.checkBridge', async () => {
    const base = bridgeUrl();
    if (!allowLoopback(base)) { sidebar.setStatus(false, 'Refused: non-loopback URL blocked.'); return; }
    const h = await checkHealth(base);
    if (h.ok) {
      const label = `Connected — bridge ok (${h.tool ?? 'argus'} ${h.version ?? ''})`.trim();
      sidebar.setStatus(true, label); sidebar.pushLog(`health: ${label}`);
      void vscode.window.showInformationMessage(label);
    } else {
      sidebar.setStatus(false, OFFLINE_MESSAGE); sidebar.pushLog('health: offline');
      void vscode.window.showWarningMessage(OFFLINE_MESSAGE);
    }
  });
  const verify = vscode.commands.registerCommand('argus.verifySelection', async () => {
    const base = bridgeUrl();
    if (!allowLoopback(base)) { return; }
    const ed = vscode.window.activeTextEditor;
    let text = ed ? ed.document.getText(ed.selection).trim() : '';
    if (!text) { text = (await vscode.window.showInputBox({ prompt: 'Paste snippet to verify (offline audit)' }))?.trim() ?? ''; }
    if (!text) { void vscode.window.showWarningMessage('Select or paste a snippet first.'); return; }
    const tok = await token(ctx.secrets);
    if (!tok) { void vscode.window.showWarningMessage('Missing bridge token — run ARGUS: Set Bridge Token.'); return; }
    try {
      const out = await verifySnippet(base, tok, text.slice(0, MAX_TEXT));
      const msg = `ARGUS verify: ${out.verdict ?? 'UNKNOWN'} — ${out.url_count ?? 0} URL(s).`;
      output.appendLine(msg); output.appendLine(JSON.stringify(out.raw, null, 2).slice(0, 2000));
      sidebar.pushLog(msg); output.show(true);
      void vscode.window.showInformationMessage(msg);
    } catch (e: any) {
      const msg = e?.message ?? OFFLINE_MESSAGE;
      sidebar.pushLog(`verify failed: ${msg}`); void vscode.window.showWarningMessage(msg);
    }
  });
  const analyze = vscode.commands.registerCommand('argus.analyzeSelection', async () => {
    const base = bridgeUrl();
    if (!allowLoopback(base)) { return; }
    const ed = vscode.window.activeTextEditor;
    const text = ed ? ed.document.getText(ed.selection).trim() : '';
    if (!text) { void vscode.window.showWarningMessage('Select text first.'); return; }
    const tok = await token(ctx.secrets);
    if (!tok) { void vscode.window.showWarningMessage('Missing bridge token.'); return; }
    try {
      const out = await analyzeSelection(base, tok, text.slice(0, MAX_TEXT));
      const head = `ARGUS plan: ${out.mode_name ?? out.mode ?? 'unknown'}`;
      output.appendLine(head);
      for (const q of out.subquestions ?? []) { output.appendLine(`- ${q}`); }
      sidebar.pushLog(head); output.show(true);
      void vscode.window.showInformationMessage(head);
    } catch (e: any) {
      const msg = e?.message ?? OFFLINE_MESSAGE;
      sidebar.pushLog(`analyze failed: ${msg}`); void vscode.window.showWarningMessage(msg);
    }
  });
  const insert = vscode.commands.registerCommand('argus.insertTemplate', async () => {
    const ed = vscode.window.activeTextEditor;
    if (!ed) { void vscode.window.showWarningMessage('Open a Markdown file first.'); return; }
    const topic = await vscode.window.showInputBox({ prompt: 'Report question', value: 'compare X vs Y' });
    if (topic === undefined) { return; }
    await ed.edit((b) => { b.insert(ed.selection.active, buildReportTemplate(topic ?? '') + '\n'); });
    sidebar.pushLog('template inserted (12 sections)');
    void vscode.window.showInformationMessage('ARGUS template inserted.');
  });
  const setT = vscode.commands.registerCommand('argus.setToken', async () => {
    const v = await vscode.window.showInputBox({ prompt: 'Paste bridge token', password: true, ignoreFocusOut: true });
    if (!v?.trim()) { return; }
    await ctx.secrets.store(TOKEN_KEY, v.trim());
    sidebar.pushLog('token saved to SecretStorage');
    void vscode.window.showInformationMessage('ARGUS token saved securely.');
  });
  const clearT = vscode.commands.registerCommand('argus.clearToken', async () => {
    await ctx.secrets.delete(TOKEN_KEY);
    sidebar.pushLog('token cleared');
    void vscode.window.showInformationMessage('ARGUS token cleared.');
  });
  ctx.subscriptions.push(check, verify, analyze, insert, setT, clearT);
}
export function deactivate(): void {}
