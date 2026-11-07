// AgentVis screen: projects → sessions → overview strip, then turns as a flow graph or a list.
// Spec: docs/design/WebUI.md, docs/design/FlowGraph.md. All session text is untrusted: only ever use textContent.

import { renderGraph } from "./graph.js";
import { renderOverview, summarizeTurns } from "./overview.js";

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
  user_message: "작업 중 사용자 메시지",
  notification: "알림",
  hook_failure: "실시간 신호 누락",
  compact: "대화 요약(문맥 압축)",
  subagent: "서브에이전트",
};
// What the transcript recovers when a hook was not delivered (WebUI.md section 3, I40): [explanation, recovered].
const LOST_HOOK = {
  PreToolUse: ["도구 실행 시각을 세션 기록 시각으로 추정함", true],
  PostToolUse: ["도구 실행 시각을 세션 기록 시각으로 추정함", true],
  PostToolUseFailure: ["실패 여부와 오류 문구를 세션 기록으로 보완함", true],
  Stop: ["턴 끝을 세션 기록의 턴 소요 시간 기록으로 보완함", true],
  UserPromptSubmit: ["턴 시작 지시를 세션 기록으로 보완함", true],
  PermissionRequest: ["이 도구의 권한 요청 여부는 확인할 수 없음", false],
  SubagentStart: ["서브에이전트의 정확한 시작·끝 시각은 확인할 수 없음", false],
  SubagentStop: ["서브에이전트의 정확한 시작·끝 시각은 확인할 수 없음", false],
  StopFailure: ["턴 실패의 오류 코드는 확인할 수 없음", false],
};

function lostHookText(detail) {
  const hook = detail?.hook_event || "hook";
  const [explanation, recovered] = LOST_HOOK[hook] || ["이 신호의 내용은 확인할 수 없음", false];
  const cause = String(detail?.message || "").includes("ECONNREFUSED") ? "AgentVis 서버가 꺼져 있었음" : "전달 실패";
  return { text: `실시간 신호 누락(${hook}) · ${explanation} · 원인: ${cause}`, recovered };
}

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
  return {
    project: params.get("project"),
    session: params.get("session"),
    view: params.get("view") === "list" ? "list" : "graph",
    turn: Number(params.get("turn")) || null,
    step: params.get("step") || null,
    width: params.get("width") === "time" ? "time" : "equal",
    scale: params.get("scale") === "real" ? "real" : "compress",
    live: params.get("live") !== "off",
  };
}

// Changes some hash fields and keeps the rest; null removes a field (WebUI.md section 7.4).
function updateHash(changes) {
  const params = new URLSearchParams(location.hash.slice(1));
  for (const [key, value] of Object.entries(changes)) {
    if (value === null || value === undefined) params.delete(key);
    else params.set(key, String(value));
  }
  location.hash = params.toString();
}

// Starts a fresh hash for a newly chosen project or session.
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
  item.dataset.stepId = String(step.id);
  const label = STEP_LABEL[step.kind];
  if (step.kind === "tool_call" && step.tool_call) {
    item.append(renderToolCall(step.tool_call));
  } else if (step.kind === "thinking") {
    const facts = [];
    if (step.detail?.duration_ms !== undefined) facts.push(`${(step.detail.duration_ms / 1000).toFixed(1)}초`);
    if (step.detail?.tokens !== undefined) facts.push(`${step.detail.tokens}토큰`);
    const head = [label, ...facts].join(" · ");
    if (String(step.text || "").trim()) item.append(expandable("thinking", `${head}: ${firstLine(step.text, 100)}`, step.text));
    else item.append(el("span", "thinking", `${head} (내용이 기록에 남지 않음)`));
  } else if (step.kind === "text") {
    const text = String(step.text || "");
    item.append(text.length > 300 ? expandable("text", firstLine(text, 200), text) : el("div", "text", text));
  } else if (step.kind === "user_message") {
    item.append(el("span", "badge", label), el("span", "message", step.text));
  } else if (step.kind === "notification") {
    const source = NOTIFICATION_SOURCE[step.detail?.source] || step.detail?.source || "";
    item.append(expandable("notification", `${label}(${source}): ${firstLine(step.text, 100)}`, step.text));
  } else if (step.kind === "hook_failure") {
    const { text, recovered } = lostHookText(step.detail);
    item.classList.add(recovered ? "recovered" : "lost");
    item.append(expandable("hook-failure", text, step.detail?.message || ""));
  } else if (step.kind === "compact") {
    item.append(el("span", null, `${label}${step.detail?.trigger ? ` (${step.detail.trigger})` : ""}`));
  } else if (step.kind === "subagent") {
    item.append(el("div", "label", `${label} ${step.detail?.agent_id || ""} (연결되지 않음)`), renderSteps(step.substeps || []));
  } else {
    item.append(el("span", null, step.kind));
  }
  return item;
}

// JSON raw/formatted view (WebUI.md section 3, I43). The chosen view of each block survives live redraws.
const RESULT_PREVIEW_CHARS = 2000;
const jsonViews = new Map();

function parseJSON(text) {
  try {
    return { ok: true, value: JSON.parse(text) };
  } catch {
    return { ok: false };
  }
}

// String values that are JSON themselves are opened up in the formatted input view.
function expandJSONStrings(value) {
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed[0] === "{" || trimmed[0] === "[") {
      const parsed = parseJSON(trimmed);
      if (parsed.ok) return expandJSONStrings(parsed.value);
    }
    return value;
  }
  if (Array.isArray(value)) return value.map(expandJSONStrings);
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, expandJSONStrings(item)]));
  return value;
}

// A labelled text block; `views` is null (plain text) or {raw, formatted, initial}.
function textBlock(label, key, text, className, views, note = null) {
  const block = el("div", "text-block");
  const head = el("div", "block-head");
  head.append(el("div", "label", label));
  const body = el("pre", className, text);
  if (views) {
    const toggle = el("div", "view-toggle json-toggle");
    const show = (mode) => {
      body.textContent = mode === "formatted" ? views.formatted : views.raw;
      for (const button of toggle.children) button.classList.toggle("active", button.dataset.mode === mode);
      jsonViews.set(key, mode);
    };
    for (const [mode, name, title] of [["raw", "원문", "기록에 남은 그대로 봅니다"], ["formatted", "JSON 정리", "JSON을 들여쓰기 2칸으로 정리해 봅니다"]]) {
      const button = el("button", null, name);
      button.type = "button";
      button.title = title;
      button.dataset.mode = mode;
      button.addEventListener("click", () => show(mode));
      toggle.append(button);
    }
    head.append(toggle);
    show(jsonViews.get(key) || views.initial);
  } else if (note) {
    head.append(el("span", "meta", note));
  }
  block.append(head, body);
  return block;
}

function outputBlock(label, key, text, className) {
  const trimmed = text.trim();
  const parsed = trimmed[0] === "{" || trimmed[0] === "[" ? parseJSON(trimmed) : { ok: false };
  if (parsed.ok) return textBlock(label, key, text, className, { raw: text, formatted: JSON.stringify(parsed.value, null, 2), initial: "raw" });
  const cut = text.length >= RESULT_PREVIEW_CHARS && (trimmed[0] === "{" || trimmed[0] === "[");
  return textBlock(label, key, text, className, null, cut ? `앞 ${RESULT_PREVIEW_CHARS.toLocaleString()}자만 보관되어 잘린 JSON이라 정리할 수 없음` : null);
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
  const id = call.tool_use_id;
  const formattedInput = JSON.stringify(expandJSONStrings(call.input), null, 2);
  details.append(textBlock("입력", `${id}:input`, formattedInput, "body", { raw: JSON.stringify(call.input), formatted: formattedInput, initial: "formatted" }));
  if (call.error) details.append(outputBlock("오류", `${id}:error`, call.error, "body error-text"));
  else if (call.result) details.append(outputBlock("결과", `${id}:result`, call.result, "body"));
  if (call.subagent) details.append(el("div", "label", "서브에이전트 단계"), renderSteps(call.subagent));
  return details;
}


function indexSteps(steps, index = new Map()) {
  for (const step of steps || []) {
    index.set(step.id, step);
    indexSteps(step.substeps, index);
    indexSteps(step.tool_call?.subagent, index);
  }
  return index;
}

// Only how the chosen turn's flow is drawn; the chosen turn and step stay (WebUI.md section 2).
function viewToggle(state) {
  const toggle = el("div", "view-toggle");
  for (const [value, label] of [["graph", "흐름 그래프"], ["list", "목록"]]) {
    const button = el("button", value === state.view ? "active" : null, label);
    button.type = "button";
    button.addEventListener("click", () => updateHash({ view: value }));
    toggle.append(button);
  }
  return toggle;
}


function focusStep(container, stepId, scroll = true) {
  const item = stepId ? container.querySelector(`.steps [data-step-id="${stepId}"]`) : null;
  if (!item) return;
  item.classList.add("focused");
  for (let node = item; node && node !== container; node = node.parentElement) {
    if (node.tagName === "DETAILS") node.open = true;
  }
  const own = item.querySelector(":scope > details");
  if (own) own.open = true;
  if (scroll) item.scrollIntoView({ block: "center" });
}

function renderNodeDetail(container, node, turn, steps) {
  container.replaceChildren();
  if (node.kind === "prompt") {
    container.append(el("div", "label", "턴 시작 지시"), el("pre", "prompt-full", turn.prompt));
    return;
  }
  if (node.kind === "model" && node.generation_started_at) {
    const start = new Date(node.started_at).getTime();
    const generation = new Date(node.generation_started_at).getTime();
    const seconds = (ms) => (ms >= 60000 ? `${Math.floor(ms / 60000)}분 ${Math.round((ms % 60000) / 1000)}초` : `${(ms / 1000).toFixed(1)}초`);
    const facts = [];
    if (generation > start) facts.push(`생각 ${seconds(generation - start)}`);
    facts.push(`작성 ${seconds(new Date(node.ended_at).getTime() - generation)}`);
    if (node.output_chars) facts.push(`응답·도구 입력 ${node.output_chars.toLocaleString()}자 작성`);
    if (node.approximate) facts.push("시각 근사");
    container.append(el("div", "facts", facts.join(" · ")));
  }
  const found = node.step_ids.map((id) => steps.get(id)).filter(Boolean);
  if (!found.length) {
    container.append(el("p", "empty", "이 노드의 단계를 찾지 못했습니다. 새로고침해 보세요."));
    return;
  }
  container.append(renderSteps(found));
  container.querySelectorAll("details").forEach((details) => { details.open = true; });
}


// The turn shown in both views: the hash's turn, else the last one (WebUI.md section 2).
function chosenTurn(state, view) {
  const last = view.turns[view.turns.length - 1];
  return state.live ? last : view.turns.find((turn) => turn.index === state.turn) || last;
}

// The newest main-agent step of a turn, followed while live follow is on (WebUI.md section 8.2, I42).
function latestMainStep(turn) {
  return turn.steps.length ? String(turn.steps[turn.steps.length - 1].id) : null;
}

function latestMainNode(graph) {
  const main = graph.nodes.filter((node) => node.lane === "main");
  return main.reduce((latest, node) => (!latest || new Date(node.started_at) >= new Date(latest.started_at) ? node : latest), null);
}

// Box 3: which turn to look at. It is the same in both views.
function renderTurnPicker(view, turn) {
  const picker = el("div", "turn-picker");
  const select = el("select", "turn-select");
  for (const item of view.turns) {
    const option = el("option", null, `#${item.index} ${firstLine(item.prompt, 80)}${item.failure_count ? ` · 실패 ${item.failure_count}` : ""}`);
    option.value = String(item.index);
    option.selected = item === turn;
    select.append(option);
  }
  select.addEventListener("change", () => pickTurn(view, Number(select.value), null));
  const meta = el("div", "meta", `${formatTime(turn.started_at)} · ${turn.state} · 도구 ${turn.tool_call_count}`);
  if (turn.failure_count) meta.append(" · ", el("span", "fail-count", `실패 ${turn.failure_count}`));
  picker.append(select, meta);
  if (turn.prompt && turn.prompt.includes("\n")) picker.append(expandable("prompt", "턴 시작 지시 전문", turn.prompt));
  picker.append(followControl());
  return picker;
}

// Without a turn in the hash the last turn is shown, so a new turn is followed automatically (WebUI.md section 8.2).
// Picking anything other than the latest turn as a whole turns live follow off, so the next update
// does not take the choice away (WebUI.md section 8.2).
function pickTurn(view, index, step) {
  const last = view.turns[view.turns.length - 1];
  if (readHash().live && last && index === last.index && step === null) return;
  updateHash({ live: "off", turn: index, step });
}

function followControl() {
  return readHash().live ? el("div", "meta follow", "● 최신 턴과 최신 노드를 따라가는 중") : el("span");
}

// Box 4, list view: the chosen turn's steps (WebUI.md section 7.5).
function renderTurnSteps(view, turn) {
  const wrapper = el("div", "turn-steps");
  if (turn === view.turns[0] && view.preamble.length) wrapper.append(el("div", "label", "첫 턴 앞의 단계"), renderSteps(view.preamble));
  wrapper.append(turn.steps.length ? renderSteps(turn.steps) : el("p", "empty", "보여 줄 단계가 없습니다."));
  return wrapper;
}

// Box 4, graph view: the chosen turn's flow graph and node detail.
async function renderTurnGraph(state, view, turn) {
  const wrapper = el("div", "graph-view");
  const graphBox = el("div", "graph-box");
  const detail = el("div", "node-detail");
  detail.append(el("p", "empty", "노드를 누르면 여기에 상세가 나옵니다."));
  wrapper.append(graphBox, detail);
  try {
    if (!cache.graphs.has(turn.index)) {
      cache.graphs.set(turn.index, await getJSON(`/api/sessions/${encodeURIComponent(view.session_id)}/turns/${turn.index}/graph`));
    }
    const graph = cache.graphs.get(turn.index);
    const steps = indexSteps(turn.steps);
    const latest = state.live ? latestMainNode(graph) : null;
    shownStep = latest ? latest.id : state.step;
    // The graph needs its container laid out to fit the width, so draw after it is attached.
    const viewKey = `${view.session_id}:${turn.index}:${state.scale}`;
    const onNode = (node, byUser) => {
      renderNodeDetail(detail, node, turn, steps);
      // A clicked node goes to the hash so a live redraw keeps its detail open (WebUI.md section 8.2).
      if (byUser && (readHash().live || String(readHash().step) !== node.id)) updateHash({ live: "off", turn: turn.index, step: node.id });
    };
    requestAnimationFrame(() => renderGraph(graphBox, graph, onNode, {
      initialId: latest ? latest.id : state.step,
      follow: Boolean(latest),
      scale: state.scale,
      onScale: (scale) => updateHash({ scale: scale === "real" ? "real" : null }),
      view: graphViews.get(viewKey) || null,
      onView: (saved) => graphViews.set(viewKey, saved),
    }));
  } catch (error) {
    showError(graphBox, error);
  }
  return wrapper;
}

async function loadSession(state) {
  const container = document.getElementById("detail");
  if (!state.session) {
    container.replaceChildren(el("p", "empty", "세션을 고르세요."));
    return;
  }
  try {
    if (!cache.view) {
      cache.view = await getJSON(`/api/sessions/${encodeURIComponent(state.session)}`);
      cache.turns = summarizeTurns(cache.view);
    }
    const { view, turns } = cache;
    const header = el("div", "session-header");
    header.append(el("div", "name", view.title || view.session_id));
    const meta = el("div", "meta", `${view.project || ""} · 턴 ${view.turn_count} · 도구 ${view.tool_call_count}`);
    if (view.failure_count) meta.append(" · ", el("span", "fail-count", `실패 ${view.failure_count}`));
    header.append(meta);
    const overview = el("div", "overview");
    const boxes = [box("세션 정보", header, "session"), box("세션 전체 흐름", overview, "session")];
    const turn = view.turns.length ? chosenTurn(state, view) : null;
    shownTurn = turn ? turn.index : null;
    shownStep = state.live && turn ? latestMainStep(turn) : state.step;
    if (turn) {
      const flow = state.view === "list" ? renderTurnSteps(view, turn) : await renderTurnGraph(state, view, turn);
      boxes.push(box("턴 선택", renderTurnPicker(view, turn), "turn first"), box(`턴 #${turn.index} 작업 흐름`, flow, "turn", viewToggle(state)));
    } else {
      boxes.push(box("턴 선택", el("p", "empty", "턴이 없습니다."), "turn first"));
    }
    container.replaceChildren(...boxes);
    // The strip fits the detail width, so draw it after it is attached.
    renderOverview(overview, turns, {
      selected: turn ? turn.index : null,
      width: state.width,
      onSelect: (picked, toFailure) => pickTurn(view, picked.index, toFailure ? picked.firstFailure : null),
      onWidth: (width) => updateHash({ width: width === "time" ? "time" : null }),
    });
    // Only a newly chosen step scrolls the list; a live redraw leaves the scroll where it is.
    // Only a newly chosen step scrolls the list, except while following, which keeps the newest step in sight.
    const focusId = state.live && turn ? latestMainStep(turn) : state.step;
    const focusKey = `${view.session_id}:${focusId}`;
    if (turn && state.view === "list") focusStep(container, focusId, state.live || focusKey !== lastFocus);
    lastFocus = focusKey;
    updateLiveButton();
  } catch (error) {
    showError(container, error);
  }
}

// One titled box of the session detail; boxes of the same scope (session or turn) form a group (WebUI.md section 2).
// `controls` sit in the title row and act on this box only.
function box(title, content, scope, controls = null) {
  const section = el("section", `box box-${scope.split(" ").join(" box-")}`);
  const head = el("div", "box-head");
  head.append(el("h3", "box-title", title));
  if (controls) head.append(controls);
  section.append(head, content);
  return section;
}

// The last session detail and its turn graphs, reused while only the selection in the hash changes (WebUI.md section 7.4).
let cache = { view: null, turns: [], graphs: new Map() };
let shown = { project: undefined, session: undefined };
// Zoom and scroll of each drawn graph, by session, turn and time axis, kept across live redraws (WebUI.md section 8.2).
const graphViews = new Map();
let lastFocus = null;
// What is on screen now, so turning live follow off can pin it.
let shownTurn = null;
let shownStep = null;

async function render(force = false) {
  const state = readHash();
  const changed = force || state.project !== shown.project || state.session !== shown.session;
  shown = { project: state.project, session: state.session };
  const tasks = [];
  if (changed) {
    cache = { view: null, turns: [], graphs: new Map() };
    tasks.push(loadProjects(state.project), loadSessions(state.project, state.session));
  }
  tasks.push(loadSession(state));
  await Promise.all(tasks);
}

// Side pane collapse is a per-viewer preference, so it lives in localStorage, never in the hash (WebUI.md section 2).
const COLLAPSE_KEY = "agentvis.collapsed";

function readCollapsed() {
  try {
    return new Set(JSON.parse(localStorage.getItem(COLLAPSE_KEY) || "[]"));
  } catch {
    return new Set();
  }
}

function applyCollapsed(collapsed) {
  const panes = document.querySelector(".panes");
  for (const button of document.querySelectorAll("button.collapse")) {
    const id = button.dataset.pane;
    const closed = collapsed.has(id);
    panes.classList.toggle(`${id}-collapsed`, closed);
    document.getElementById(id).classList.toggle("collapsed", closed);
    button.setAttribute("aria-expanded", String(!closed));
    button.textContent = closed ? "▸" : "◂";
    const name = document.getElementById(id).querySelector("h2").textContent;
    button.title = `${name} 목록 ${closed ? "펴기" : "접기"}`;
  }
}

function setupCollapse() {
  const collapsed = readCollapsed();
  for (const button of document.querySelectorAll("button.collapse")) {
    button.addEventListener("click", () => {
      const id = button.dataset.pane;
      if (collapsed.has(id)) collapsed.delete(id);
      else collapsed.add(id);
      try {
        localStorage.setItem(COLLAPSE_KEY, JSON.stringify([...collapsed]));
      } catch {
        // Storage can be unavailable (private window); the toggle still works for this page.
      }
      applyCollapsed(collapsed);
    });
  }
  applyCollapsed(collapsed);
}

// Live updates: the server names the sessions that got new events (WebUI.md section 8).
const LIST_REFRESH_MS = 15000;
let refreshing = false;
let refreshAgain = false;
let lastListRefresh = 0;
let listTimer = null;

async function refreshSession() {
  if (refreshing) {
    refreshAgain = true;
    return;
  }
  refreshing = true;
  try {
    do {
      refreshAgain = false;
      cache = { view: null, turns: [], graphs: new Map() };
      await loadSession(readHash());
    } while (refreshAgain);
  } finally {
    refreshing = false;
  }
}

// Session and project lists are slow to compute, so they refresh at most every LIST_REFRESH_MS.
function refreshLists() {
  if (listTimer) return;
  const wait = Math.max(0, lastListRefresh + LIST_REFRESH_MS - Date.now());
  listTimer = setTimeout(async () => {
    listTimer = null;
    lastListRefresh = Date.now();
    const state = readHash();
    await Promise.all([loadProjects(state.project), loadSessions(state.project, state.session)]);
  }, wait);
}

let connected = false;

function setLive(value) {
  connected = value;
  updateLiveButton();
}

// The header button turns live follow on and off; it also shows a lost server connection (WebUI.md section 8.2).
function updateLiveButton() {
  const button = document.getElementById("live");
  const following = readHash().live;
  if (!connected) {
    button.textContent = "○ 연결 끊김";
    button.className = "live lost";
    button.title = "서버와의 연결을 다시 잇는 중입니다. 이어지면 화면을 다시 받습니다.";
  } else if (following) {
    button.textContent = "● 실시간 따라가기";
    button.className = "live on";
    button.title = "최신 턴과 주 에이전트의 최신 노드를 따라가는 중입니다. 누르면 지금 화면에 머뭅니다.";
  } else {
    button.textContent = "○ 따라가기 꺼짐";
    button.className = "live off";
    button.title = "보던 턴과 노드에 머무는 중입니다(내용은 계속 갱신됩니다). 누르면 최신 작업을 따라갑니다.";
  }
  button.setAttribute("aria-pressed", String(following));
}

function toggleLive() {
  if (readHash().live) updateHash({ live: "off", turn: shownTurn, step: shownStep });
  else updateHash({ live: null, turn: null, step: null });
}

function connectStream() {
  const source = new EventSource("/api/stream");
  let lost = false;
  source.addEventListener("open", () => {
    setLive(true);
    // Changes made while disconnected were not announced, so reload everything once.
    if (lost) render(true);
    lost = false;
  });
  source.addEventListener("error", () => {
    lost = true;
    setLive(false);
  });
  source.addEventListener("change", (event) => {
    let sessions = [];
    try {
      sessions = JSON.parse(event.data).sessions || [];
    } catch {
      return;
    }
    if (sessions.includes(readHash().session)) refreshSession();
    refreshLists();
  });
}

setupCollapse();
window.addEventListener("hashchange", () => render());
document.getElementById("refresh").addEventListener("click", () => render(true));
document.getElementById("live").addEventListener("click", toggleLive);
render();
connectStream();
