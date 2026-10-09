/* ARGUS Field Companion — background service worker (Manifest V3).
 *
 * ARCHITECTURAL VETO (binding):
 * - Browser is a hostile environment. This extension NEVER contains
 *   restricted-collection tiers, intrusion tooling, or deep forensic
 *   collection. Institutional assistant ONLY.
 * - Role ONLY: capture page context (selection + URL + title) and forward
 *   it to the local ARGUS core via the secure bridge on 127.0.0.1.
 * - No external network. Fail-safe: if the bridge is offline, show
 *   "ARGUS Core is offline" and send data nowhere else.
 */

const BRIDGE_BASE = "http://127.0.0.1:8765";
const MENU_ID = "argus-send-to-core";

// Install: context-menu entry + side-panel behaviour.
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: MENU_ID,
    title: "إرسال إلى ARGUS للتحليل",
    contexts: ["selection"],
  });
  if (chrome.sidePanel && chrome.sidePanel.setPanelBehavior) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
  }
});

// Toolbar click opens the companion panel.
chrome.action.onClicked.addListener((tab) => {
  if (tab && tab.windowId !== undefined && chrome.sidePanel) {
    chrome.sidePanel.open({ windowId: tab.windowId }).catch(() => {});
  }
});

async function getToken() {
  const { argusToken } = await chrome.storage.local.get("argusToken");
  return (argusToken || "").trim();
}

// Context-menu click: gather context, forward to the local bridge only.
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== MENU_ID) return;
  const payload = {
    selected_text: (info.selectionText || "").slice(0, 2000),
    page_url: (tab && tab.url ? tab.url : info.pageUrl || "").slice(0, 2000),
    page_title: (tab && tab.title ? tab.title : "").slice(0, 500),
  };
  const token = await getToken();
  if (!token) {
    await rememberResult({ ok: false, error: "Missing token — paste the bridge token in the side panel." });
    return;
  }
  try {
    const res = await fetch(`${BRIDGE_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Argus-Token": token },
      body: JSON.stringify(payload),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      await rememberResult({ ok: false, error: data.error || `Bridge refused (HTTP ${res.status})` });
      return;
    }
    await rememberResult({ ok: true, at: Date.now(), request: payload, response: data });
  } catch (e) {
    // Fail-safe: offline bridge => report offline, never reroute elsewhere.
    await rememberResult({ ok: false, error: "ARGUS Core is offline — start argus_bridge.py, data sent nowhere." });
  }
});

// Ephemeral only: session storage (cleared with the session), never local persistence.
async function rememberResult(entry) {
  try {
    const { argusLog = [] } = await chrome.storage.session.get("argusLog");
    argusLog.unshift(entry);
    await chrome.storage.session.set({ argusLog: argusLog.slice(0, 20) });
  } catch (e) {
    // Stateless fallback: drop the entry rather than persist it unsafely.
  }
}
