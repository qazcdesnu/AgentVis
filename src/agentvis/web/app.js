// AgentVis first screen: projects → sessions → turns and steps.
// Spec: docs/design/WebUI.md. All session text is untrusted: only ever use textContent.

const STATUS = {
  success: ["✓", "성공"],
  error: ["✕", "오류"],
  interrupted: ["⏸", "중단"],
  running: ["●", "실행 중"],
  unfinished: ["?", "끝나지 않음"],
};
const STEP_LABEL = {
  thinking: "생각",
  text: "응답",
  user_message: "사용자 메시지",
  notification: "알림",
  hook_failure: "hook 전달 실패",
  compact: "문맥 압축",
  subagent: "서브에이전트",
};
const NOTIFICATION_SOURCE = {
  "task-notification": "작업 알림",
  peer: "하위 에이전트 보고",
  user_shell: "사용자 셸",
  prompt: "전달된 메시지",
  meta: "시스템",
};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function readHash() {
  const params = new URLSearchParams(location.hash.slice(1));
  return { project: params.get("project"), session: params.get("session") };
}

function writeHash(project, session) {
  const params = new URLSearchParams();
  if (project) params.set("project", project);
  if (session) params.set("session", session);
  location.hash = params.toString();
}

async function getJSON(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}

function formatTime(iso) {
  if (!iso) return "";
  const date = new Date(iso);
  const pad = (value) => String(value).padStart(2, "0");
  return `${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function firstLine(text, limit = 120) {
  const line = String(text || "").trim().split("\n")[0];
  return line.length > limit ? `${line.slice(0, limit)}…` : line;
}

function toolSummary(call) {
  const input = call.input && typeof call.input === "object" ? call.input : {};
  const value = input.command ?? input.file_path ?? input.description ?? input.pattern ?? input.url;
  return firstLine(value !== undefined ? value : JSON.stringify(call.input ?? ""), 100);
}

function showError(container, error) {
  container.replaceChildren(el("p", "error", `불러오지 못했습니다: ${error.message}`));
}

async function loadProjects(selected) {
  const list = document.getElementById("projects");
  try {
    const { projects } = await getJSON("/api/projects");
    list.replaceChildren();
    if (!projects.length) list.append(el("li", "empty", "아직 수집된 프로젝트가 없습니다."));
    for (const project of projects) {
      const item = el("li", "item" + (project.path === selected ? " selected" : "") + (project.exists ? "" : " missing"));
      item.append(el("div", "name", project.name), el("div", "meta", project.parent));
      item.append(el("div", "meta", `세션 ${project.session_count} · ${formatTime(project.last_activity)}`));
      item.title = project.path;
      item.addEventListener("click", () => writeHash(project.path, null));
      list.append(item);
    }
  } catch (error) {
    showError(list, error);
  }
}

async function loadSessions(project, selected) {
  const list = document.getElementById("sessions");
  if (!project) {
    list.replaceChildren(el("li", "empty", "프로젝트를 고르세요."));
    return;
  }
  try {
    const { sessions } = await getJSON(`/api/sessions?project=${encodeURIComponent(project)}`);
    list.replaceChildren();
    for (const session of sessions) {
      const item = el("li", "item" + (session.session_id === selected ? " selected" : ""));
      item.append(el("div", "name", session.title || session.session_id));
      const meta = el("div", "meta", `${formatTime(session.last_activity)} · 턴 ${session.turn_count} · 도구 ${session.tool_call_count}`);
      if (session.failure_count) meta.append(" · ", el("span", "fail-count", `실패 ${session.failure_count}`));
      item.append(meta);
      item.addEventListener("click", () => writeHash(project, session.session_id));
      list.append(item);
    }
  } catch (error) {
    showError(list, error);
  }
}

function renderSteps(steps) {
  const list = el("ol", "steps");
  for (const step of steps) list.append(renderStep(step));
  return list;
}

function expandable(className, summaryText, bodyText, open = false) {
  const details = el("details", className);
  details.open = open;
  details.append(el("summary", null, summaryText));
  if (bodyText) details.append(el("pre", "body", bodyText));
  return details;
}

function renderStep(step) {
  const item = el("li", `step step-${step.kind}`);
  const label = STEP_LABEL[step.kind];
  if (step.kind === "tool_call" && step.tool_call) {
    item.append(renderToolCall(step.tool_call));
  } else if (step.kind === "thinking") {
    item.append(expandable("thinking", `${label}: ${firstLine(step.text, 100)}`, step.text));
  } else if (step.kind === "text") {
    const text = String(step.text || "");
    item.append(text.length > 300 ? expandable("text", firstLine(text, 200), text) : el("div", "text", text));
  } else if (step.kind === "user_message") {
    item.append(el("span", "badge", label), el("span", "message", step.text));
  } else if (step.kind === "notification") {
    const source = NOTIFICATION_SOURCE[step.detail?.source] || step.detail?.source || "";
    item.append(expandable("notification", `${label}(${source}): ${firstLine(step.text, 100)}`, step.text));
  } else if (step.kind === "hook_failure") {
    item.append(el("span", null, `${label}: ${step.detail?.hook_event || ""} — 이 구간의 hook 수집이 빠졌습니다 (${step.detail?.message || ""})`));
  } else if (step.kind === "compact") {
    item.append(el("span", null, `${label}${step.detail?.trigger ? ` (${step.detail.trigger})` : ""}`));
  } else if (step.kind === "subagent") {
    item.append(el("div", "label", `${label} ${step.detail?.agent_id || ""} (연결되지 않음)`), renderSteps(step.substeps || []));
  } else {
    item.append(el("span", null, step.kind));
  }
  return item;
}

function renderToolCall(call) {
  const [symbol, statusText] = STATUS[call.status] || ["·", call.status];
  const details = el("details", `tool status-${call.status}`);
  const summary = el("summary");
  summary.append(el("span", "symbol", symbol), el("span", "tool-name", call.tool_name || "도구"), el("span", "tool-input", toolSummary(call)));
  if (call.permission_requested) summary.append(el("span", "tag", "권한 요청"));
  if (call.subagent) summary.append(el("span", "tag", `서브에이전트 ${call.subagent.length}단계`));
  details.append(summary);
  const facts = [`상태: ${statusText}`];
  if (call.duration_ms !== null && call.duration_ms !== undefined) facts.push(`실행 시간: ${call.duration_ms}ms`);
  details.append(el("div", "facts", facts.join(" · ")));
  details.append(el("div", "label", "입력"), el("pre", "body", JSON.stringify(call.input, null, 2)));
  if (call.error) details.append(el("div", "label", "오류"), el("pre", "body error-text", call.error));
  else if (call.result) details.append(el("div", "label", "결과"), el("pre", "body", call.result));
  if (call.subagent) details.append(el("div", "label", "서브에이전트 단계"), renderSteps(call.subagent));
  return details;
}

function renderTurn(turn, open) {
  const details = el("details", `turn state-${turn.state}`);
  details.open = open;
  const summary = el("summary");
  summary.append(el("span", "turn-index", `#${turn.index}`), el("span", "turn-prompt", firstLine(turn.prompt, 140)));
  const meta = el("span", "turn-meta", `${formatTime(turn.started_at)} · ${turn.state} · 도구 ${turn.tool_call_count}`);
  if (turn.failure_count) meta.append(" · ", el("span", "fail-count", `실패 ${turn.failure_count}`));
  summary.append(meta);
  details.append(summary);
  if (turn.prompt && turn.prompt.includes("\n")) details.append(el("pre", "prompt-full", turn.prompt));
  details.append(renderSteps(turn.steps));
  return details;
}

async function loadSession(session) {
  const container = document.getElementById("detail");
  if (!session) {
    container.replaceChildren(el("p", "empty", "세션을 고르세요."));
    return;
  }
  try {
    const view = await getJSON(`/api/sessions/${encodeURIComponent(session)}`);
    const header = el("div", "session-header");
    header.append(el("div", "name", view.title || view.session_id));
    const meta = el("div", "meta", `${view.project || ""} · 턴 ${view.turn_count} · 도구 ${view.tool_call_count}`);
    if (view.failure_count) meta.append(" · ", el("span", "fail-count", `실패 ${view.failure_count}`));
    header.append(meta);
    const turns = el("div", "turns");
    if (view.preamble.length) turns.append(renderSteps(view.preamble));
    view.turns.forEach((turn, index) => {
      const open = turn.failure_count > 0 || turn.state !== "ended" || index === view.turns.length - 1;
      turns.append(renderTurn(turn, open));
    });
    container.replaceChildren(header, turns);
  } catch (error) {
    showError(container, error);
  }
}

async function render() {
  const { project, session } = readHash();
  await Promise.all([loadProjects(project), loadSessions(project, session), loadSession(session)]);
}

window.addEventListener("hashchange", render);
document.getElementById("refresh").addEventListener("click", render);
render();
