/* ARGUS Field Companion — side panel logic.
 * Stateless by design: captured context lives in chrome.storage.session
 * (ephemeral). Only the bridge token persists in storage.local, and it is
 * sent exclusively to http://127.0.0.1:8765. Fail-safe stays offline-only.
 */
const BRIDGE_BASE = "http://127.0.0.1:8765";
const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  loadToken();
  checkHealth();
  renderLog();
  $("token").addEventListener("change", saveToken);
  $("refreshBtn").addEventListener("click", checkHealth);
  $("verifyBtn").addEventListener("click", verifySnippet);
  chrome.storage.session.onChanged.addListener(renderLog);
});

async function loadToken() {
  const { argusToken = "" } = await chrome.storage.local.get("argusToken");
  $("token").value = argusToken;
}

async function saveToken() {
  await chrome.storage.local.set({ argusToken: $("token").value.trim() });
}

function setStatus(online, text) {
  $("dot").className = "dot " + (online ? "on" : "off");
  $("statusText").textContent = text;
}

async function checkHealth() {
  setStatus(false, "Checking…");
  try {
    const res = await fetch(`${BRIDGE_BASE}/health`, { method: "GET" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    setStatus(true, `Connected — bridge ok (${data.tool || "argus"} ${data.version || ""})`);
  } catch (e) {
    // Fail-safe: offline message, no fallback destination.
    setStatus(false, "ARGUS Core is offline — start argus-bridge locally");
  }
}

async function verifySnippet() {
  const snippet = $("snippet").value.trim();
  const { argusToken = "" } = await chrome.storage.local.get("argusToken");
  if (!argusToken) {
    $("result").textContent = "Paste the bridge token first (from the argus-bridge terminal).";
    return;
  }
  if (!snippet) {
    $("result").textContent = "Paste a snippet first.";
    return;
  }
  $("result").textContent = "Verifying locally…";
  try {
    const res = await fetch(`${BRIDGE_BASE}/verify-snippet`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Argus-Token": argusToken },
      body: JSON.stringify({ snippet: snippet.slice(0, 2000) }),
    });
    const data = await res.json().catch(() => ({}));
    $("result").textContent = res.ok
      ? JSON.stringify(data, null, 2)
      : `Refused: ${data.error || `HTTP ${res.status}`}`;
  } catch (e) {
    $("result").textContent = "ARGUS Core is offline — start argus-bridge locally";
  }
}

async function renderLog() {
  const box = $("log");
  let entries = [];
  try {
    ({ argusLog: entries = [] } = await chrome.storage.session.get("argusLog"));
  } catch (e) {
    entries = [];
  }
  box.innerHTML = "";
  if (!entries.length) {
    box.innerHTML = '<div class="hint">No context yet — select text, right-click, Send to ARGUS.</div>';
    return;
  }
  for (const e of entries.slice(0, 20)) {
    const div = document.createElement("div");
    div.className = "entry";
    const title = e.ok ? "Sent to local core" : "Send failed";
    const body = e.ok
      ? JSON.stringify(e.response || {}, null, 2).slice(0, 800)
      : (e.error || "offline");
    // textContent only — never innerHTML with page content (XSS guard).
    div.textContent = `${title}\n${body}`;
    box.appendChild(div);
  }
}
