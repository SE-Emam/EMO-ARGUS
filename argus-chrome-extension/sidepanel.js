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
  setStatus(false, "يفحص الاتصال…");
  try {
    const res = await fetch(`${BRIDGE_BASE}/health`, { method: "GET" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    setStatus(true, `متصل — الجسر يعمل (${data.tool || "argus"} ${data.version || ""})`);
  } catch (e) {
    // Fail-safe: offline message, no fallback destination.
    setStatus(false, "ARGUS Core is offline — شغّل argus_bridge.py محليًا");
  }
}

async function verifySnippet() {
  const snippet = $("snippet").value.trim();
  const { argusToken = "" } = await chrome.storage.local.get("argusToken");
  if (!argusToken) {
    $("result").textContent = "الصق رمز الجسر أولًا (من طرفية argus_bridge.py).";
    return;
  }
  if (!snippet) {
    $("result").textContent = "الصق مقتطفًا أولًا.";
    return;
  }
  $("result").textContent = "يُتحقق محليًا…";
  try {
    const res = await fetch(`${BRIDGE_BASE}/verify-snippet`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Argus-Token": argusToken },
      body: JSON.stringify({ snippet: snippet.slice(0, 2000) }),
    });
    const data = await res.json().catch(() => ({}));
    $("result").textContent = res.ok
      ? JSON.stringify(data, null, 2)
      : `مرفوض: ${data.error || `HTTP ${res.status}`}`;
  } catch (e) {
    $("result").textContent = "ARGUS Core is offline — شغّل argus_bridge.py محليًا";
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
    box.innerHTML = '<div class="hint">لا سياق بعد — حدّد نصًا ثم كليك يمين ← إرسال إلى ARGUS.</div>';
    return;
  }
  for (const e of entries.slice(0, 20)) {
    const div = document.createElement("div");
    div.className = "entry";
    const title = e.ok ? "تم الإرسال للنواة المحلية" : "تعذّر الإرسال";
    const body = e.ok
      ? JSON.stringify(e.response || {}, null, 2).slice(0, 800)
      : (e.error || "offline");
    // textContent only — never innerHTML with page content (XSS guard).
    div.textContent = `${title}\n${body}`;
    box.appendChild(div);
  }
}
