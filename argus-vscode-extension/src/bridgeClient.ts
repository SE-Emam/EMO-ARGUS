/**
 * ARGUS bridge client — thin HTTP wrapper, loopback only.
 *
 * ARCHITECTURAL VETO (binding):
 * - This module NEVER contains collection tiers, scraping, or network
 *   destinations other than the local ARGUS core on 127.0.0.1.
 * - Role ONLY: POST captured context to the secure bridge and return JSON.
 * - Fail-safe: any network failure surfaces as OFFLINE, never reroutes.
 */

export const DEFAULT_BRIDGE_URL = 'http://127.0.0.1:8765';
export const TOKEN_HEADER = 'X-Argus-Token';
export const MAX_TEXT = 2000;
export const OFFLINE_MESSAGE =
  'ARGUS Bridge is offline. Please start the local server.';

export interface HealthResult {
  ok: boolean;
  tool?: string;
  version?: string;
  raw?: unknown;
}

export interface AnalyzeResult {
  mode?: string;
  mode_name?: string;
  subquestions?: string[];
  message?: string | null;
  raw: unknown;
}

export interface VerifyResult {
  verdict?: string;
  url_count?: number;
  findings?: Array<{ level?: string; check?: string; message?: string }>;
  raw: unknown;
}

/** True only for loopback destinations (127.0.0.1, localhost, ::1). */
export function isLoopbackUrl(value: string): boolean {
  try {
    const u = new URL(value);
    if (u.protocol !== 'http:') {
      return false;
    }
    const host = (u.hostname || '').toLowerCase();
    return host === '127.0.0.1' || host === 'localhost' || host === '::1';
  } catch {
    return false;
  }
}

/** Normalize configured URL: trim + drop trailing slashes. */
export function normalizeBridgeUrl(value: string): string {
  return (value || '').trim().replace(/\/+$/, '') || DEFAULT_BRIDGE_URL;
}

async function fetchJson(
  url: string,
  init: RequestInit,
  timeoutMs = 15000
): Promise<{ status: number; data: any }> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...init, signal: ctrl.signal });
    const data = await res.json().catch(() => ({}));
    return { status: res.status, data };
  } catch (err: any) {
    // Fail-safe: every transport failure is OFFLINE, nowhere else.
    if (err && err.name === 'AbortError') {
      throw new Error(OFFLINE_MESSAGE + ' (timeout)');
    }
    throw new Error(OFFLINE_MESSAGE);
  } finally {
    clearTimeout(timer);
  }
}

function authHeaders(token: string): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    [TOKEN_HEADER]: token,
  };
}

function requireToken(token: string): void {
  if (!token || !token.trim()) {
    throw new Error('Missing bridge token — run ARGUS: Set Bridge Token first.');
  }
}

/** GET /health — no auth. Returns ok=false instead of throwing on offline. */
export async function checkHealth(baseUrl: string): Promise<HealthResult> {
  const base = normalizeBridgeUrl(baseUrl);
  try {
    const { status, data } = await fetchJson(
      `${base}/health`,
      { method: 'GET' },
      8000
    );
    if (status !== 200) {
      return { ok: false, raw: data };
    }
    return { ok: true, tool: data.tool, version: data.version, raw: data };
  } catch {
    return { ok: false };
  }
}

/** POST /analyze — plan from captured context (capped at 2000 chars). */
export async function analyzeSelection(
  baseUrl: string,
  token: string,
  selectedText: string,
  pageUrl = '',
  pageTitle = ''
): Promise<AnalyzeResult> {
  requireToken(token);
  const base = normalizeBridgeUrl(baseUrl);
  const { status, data } = await fetchJson(`${base}/analyze`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({
      selected_text: (selectedText || '').slice(0, MAX_TEXT),
      page_url: (pageUrl || '').slice(0, MAX_TEXT),
      page_title: (pageTitle || '').slice(0, 500),
    }),
  });
  if (status === 401) {
    throw new Error('Bridge refused: bad or missing token (HTTP 401).');
  }
  if (status !== 200) {
    throw new Error(data?.error || `Bridge refused (HTTP ${status}).`);
  }
  return {
    mode: data.mode,
    mode_name: data.mode_name,
    subquestions: Array.isArray(data.subquestions) ? data.subquestions : [],
    message: data.message ?? null,
    raw: data,
  };
}

/** POST /verify-snippet — offline audit, no live fetch. */
export async function verifySnippet(
  baseUrl: string,
  token: string,
  snippet: string
): Promise<VerifyResult> {
  requireToken(token);
  const text = (snippet || '').trim();
  if (!text) {
    throw new Error('Select or paste a snippet first.');
  }
  const base = normalizeBridgeUrl(baseUrl);
  const { status, data } = await fetchJson(`${base}/verify-snippet`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ snippet: text.slice(0, MAX_TEXT) }),
  });
  if (status === 401) {
    throw new Error('Bridge refused: bad or missing token (HTTP 401).');
  }
  if (status !== 200) {
    throw new Error(data?.error || `Bridge refused (HTTP ${status}).`);
  }
  return {
    verdict: data.verdict,
    url_count: data.url_count,
    findings: Array.isArray(data.findings) ? data.findings : [],
    raw: data,
  };
}
