// Screen usage log, active only when the server runs in experiment mode.
// Spec: docs/design/WebUI.md section 9. Text from the page goes to this server only.

const FLUSH_MS = 2000;
const SCROLL_MS = 2000;
const TEXT_CHARS = 60;
const TARGETS = "button, a, summary, select, input, li, [role=button], .g-node, .ov-turn, .ov-list-row";

const queue = [];
let sending = false;

function record(type, detail = {}) {
  queue.push({ at: new Date().toISOString(), type, detail });
}

function describe(element) {
  const target = element.closest ? element.closest(TARGETS) || element : element;
  const text = (target.textContent || "").replace(/\s+/g, " ").trim().slice(0, TEXT_CHARS);
  const classes = typeof target.className === "string" ? target.className.split(/\s+/).filter(Boolean).slice(0, 2) : [];
  return { tag: (target.tagName || "").toLowerCase(), id: target.id || null, classes, text };
}

async function flush(leaving = false) {
  if (sending || !queue.length) return;
  sending = true;
  const batch = queue.splice(0, 200);
  try {
    const response = await fetch("/api/interactions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ events: batch }),
      keepalive: leaving,
    });
    if (!response.ok && response.status >= 500) queue.unshift(...batch);
  } catch {
    queue.unshift(...batch);
  } finally {
    sending = false;
  }
}

export async function startInteractionLog() {
  let info;
  try {
    const response = await fetch("/api/experiment");
    info = await response.json();
  } catch {
    return;
  }
  if (!info.participant) return;
  const badge = document.getElementById("experiment");
  badge.textContent = `실험 모드 · ${info.participant}`;
  badge.hidden = false;
  record("open", { hash: location.hash, path: location.pathname, width: window.innerWidth, height: window.innerHeight });
  // Where the reader is and how often they search: the baseline's main ways to look around (WebUI.md section 9.4).
  let lastScroll = 0;
  window.addEventListener("scroll", () => {
    const now = Date.now();
    if (now - lastScroll < SCROLL_MS) return;
    lastScroll = now;
    const height = document.documentElement.scrollHeight || 1;
    record("scroll", { y: Math.round(window.scrollY), ratio: Math.round((window.scrollY / height) * 1000) / 1000 });
  }, { passive: true });
  window.addEventListener("hashchange", () => record("hash", { hash: location.hash }));
  document.addEventListener("click", (event) => record("click", describe(event.target)), true);
  document.addEventListener("change", (event) => record("change", { ...describe(event.target), value: String(event.target.value ?? "").slice(0, TEXT_CHARS) }), true);
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "f") record("find");
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    if (event.target.closest && event.target.closest("input, textarea, select")) return;
    record("key", { key: event.key });
  }, true);
  document.addEventListener("visibilitychange", () => {
    record("visibility", { state: document.visibilityState });
    if (document.visibilityState === "hidden") flush(true);
  });
  setInterval(() => flush(), FLUSH_MS);
  // Trial boundaries go out at once, so a task's time comes straight from the log (WebUI.md section 9.1).
  const trial = document.getElementById("trial");
  let number = 1;
  let running = false;
  trial.hidden = false;
  trial.addEventListener("click", () => {
    record(running ? "trial_end" : "trial_start", { trial: number });
    if (running) number += 1;
    running = !running;
    trial.textContent = `시행 ${number} ${running ? "끝" : "시작"}`;
    trial.classList.toggle("running", running);
    flush();
  });
}
