// Session overview strip (E1) and jump badges (E3) drawn with D3 (global `d3`).
// Spec: docs/design/WebUI.md section 7, docs/design/VisualEncoding.md sections 3.1 and 3.3.
// Session text is untrusted: only ever use textContent or .text().

const SYMBOL_ROW = 14;
const BAR_ROW = 24;
const TURN_ROW = 14;
const SHORT_BAR = 10;
const MAX_BAR = 6;
const TIME_BAR = 2;
const TIME_PADDING = 4;
const MIN_SYMBOL_GAP = 8;
const MIN_TURN_LABEL_GAP = 28;
const FAILURE = new Set(["error", "interrupted"]);
const EVENT_KINDS = new Set(["tool_call", "user_message", "compact"]);
const STATUS_TEXT = { success: "✓ 성공", error: "✕ 오류", interrupted: "⏸ 중단", running: "● 실행 중", unfinished: "? 끝나지 않음" };
const BADGES = [
  { key: "failure", label: "실패", match: (event) => event.kind === "tool_call" && FAILURE.has(event.status) },
  { key: "user", label: "사용자 메시지", match: (event) => event.kind === "user_message" },
  { key: "compact", label: "압축", match: (event) => event.kind === "compact" },
];

let keyHandler = null;

// Main-agent tool calls, user messages and compactions of every turn, in order (WebUI.md section 7.1).
export function collectEvents(view, describe) {
  const events = [];
  for (const turn of view.turns) {
    for (const step of turn.steps) {
      if (!EVENT_KINDS.has(step.kind) || (step.kind === "tool_call" && !step.tool_call)) continue;
      const call = step.tool_call;
      events.push({
        id: step.id,
        order: events.length,
        turn: turn.index,
        kind: step.kind,
        status: call ? call.status : null,
        at: new Date((call && call.started_at) || step.at).getTime(),
        stepAt: new Date(step.at).getTime(),
        label: describe(step),
      });
    }
  }
  return events;
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function eventText(event) {
  if (!event) return "";
  const status = event.status ? ` · ${STATUS_TEXT[event.status] || event.status}` : "";
  return `#${event.turn} · ${event.label}${status}`;
}

function buildX(events, axis, width) {
  if (axis === "time") {
    const [low, high] = d3.extent(events, (event) => event.at);
    const scale = d3.scaleLinear().domain(low === high ? [low - 1, high + 1] : [low, high]).range([TIME_PADDING, width - TIME_PADDING]);
    return { x: (event) => scale(event.at), half: TIME_BAR, barWidth: TIME_BAR };
  }
  const slot = width / events.length;
  return { x: (event) => (event.order + 0.5) * slot, half: slot / 2, barWidth: Math.max(1, Math.min(MAX_BAR, slot - 1)) };
}

function nearest(events, x, px) {
  let best = null;
  let distance = Infinity;
  for (const event of events) {
    const gap = Math.abs(x(event) - px);
    if (gap < distance) {
      best = event;
      distance = gap;
    }
  }
  return best;
}

function drawStrip(box, events, options, info) {
  const width = box.clientWidth;
  if (!width) return;
  const height = SYMBOL_ROW + BAR_ROW + TURN_ROW;
  const { x, half, barWidth } = buildX(events, options.axis, width);
  const selected = events.find((event) => event.id === options.selected) || null;
  const svg = d3.create("svg").attr("class", "ov-svg").attr("width", width).attr("height", height);

  if (options.range) {
    const [from, to] = options.range;
    svg.append("rect").attr("class", "ov-range").attr("x", x(from) - half).attr("y", 0)
      .attr("width", Math.max(2, x(to) - x(from) + half * 2)).attr("height", SYMBOL_ROW + BAR_ROW);
  }

  const bars = svg.append("g");
  for (const event of events.filter((item) => item.kind === "tool_call")) {
    const failed = FAILURE.has(event.status);
    bars.append("rect").attr("class", failed ? `ov-bar status-${event.status}` : "ov-bar routine")
      .attr("x", x(event) - barWidth / 2).attr("width", barWidth)
      .attr("y", failed ? SYMBOL_ROW : SYMBOL_ROW + BAR_ROW - SHORT_BAR).attr("height", failed ? BAR_ROW : SHORT_BAR);
  }

  for (const event of events.filter((item) => item.kind === "compact")) {
    svg.append("line").attr("class", "ov-compact").attr("x1", x(event)).attr("x2", x(event)).attr("y1", 0).attr("y2", SYMBOL_ROW + BAR_ROW);
    svg.append("text").attr("class", "ov-compact-label").attr("x", x(event) + 3).attr("y", 10).text("압축");
  }

  let lastSymbol = -Infinity;
  for (const event of events) {
    const symbol = event.kind === "user_message" ? "▲" : event.status === "error" ? "✕" : event.status === "interrupted" ? "⏸" : null;
    if (!symbol || x(event) - lastSymbol < MIN_SYMBOL_GAP) continue;
    lastSymbol = x(event);
    const kind = event.kind === "user_message" ? "user" : event.status;
    svg.append("text").attr("class", `ov-symbol ov-symbol-${kind}`).attr("x", x(event)).attr("y", SYMBOL_ROW - 3).attr("text-anchor", "middle").text(symbol);
  }

  let lastTurn = null;
  let lastLabel = -Infinity;
  for (const event of events) {
    if (event.turn === lastTurn) continue;
    lastTurn = event.turn;
    const left = x(event) - half;
    svg.append("line").attr("class", "ov-turn").attr("x1", left).attr("x2", left).attr("y1", SYMBOL_ROW + BAR_ROW).attr("y2", SYMBOL_ROW + BAR_ROW + 4);
    if (left - lastLabel < MIN_TURN_LABEL_GAP) continue;
    lastLabel = left;
    svg.append("text").attr("class", "ov-turn-label").attr("x", left + 2).attr("y", height - 2).text(`#${event.turn}`);
  }

  if (selected) {
    svg.append("line").attr("class", "ov-cursor").attr("x1", x(selected)).attr("x2", x(selected)).attr("y1", 0).attr("y2", SYMBOL_ROW + BAR_ROW);
  }

  // A press without dragging selects the nearest event; a drag selects a range (WebUI.md section 7.4).
  const brush = d3.brushX().extent([[0, 0], [width, SYMBOL_ROW + BAR_ROW]]).on("end", (event) => {
    if (!event.sourceEvent) return;
    if (!event.selection) {
      const [px] = d3.pointer(event.sourceEvent, svg.node());
      const found = nearest(events, x, px);
      if (found) options.onSelect(found);
      return;
    }
    const [x0, x1] = event.selection;
    const inside = events.filter((item) => x(item) >= x0 && x(item) <= x1);
    if (inside.length) options.onRange(inside[0], inside[inside.length - 1]);
    else svg.select(".ov-brush").call(brush.move, null);
  });
  svg.append("g").attr("class", "ov-brush").call(brush);
  svg.on("mousemove", (event) => {
    const [px] = d3.pointer(event, svg.node());
    info.textContent = eventText(nearest(events, x, px));
  });
  svg.on("mouseleave", () => {
    info.textContent = selected ? eventText(selected) : "";
  });
  box.replaceChildren(svg.node());
}

function renderBadges(events, options) {
  const bar = el("div", "ov-badges");
  const current = events.find((event) => event.id === options.selected);
  const inRange = (event) => !options.range || (event.order >= options.range[0].order && event.order <= options.range[1].order);
  const jumps = {};
  for (const badge of BADGES) {
    const all = events.filter(badge.match);
    const shown = all.filter(inRange);
    const next = () => (current ? shown.find((event) => event.order > current.order) : shown[0]);
    const previous = () => (current ? shown.filter((event) => event.order < current.order).pop() : shown[shown.length - 1]);
    jumps[badge.key] = { next, previous };
    const group = el("span", `ov-badge ov-badge-${badge.key}`);
    group.append(el("span", "ov-badge-label", `${badge.label} ${options.range ? `${shown.length}/${all.length}` : all.length}`));
    for (const [symbol, pick, title] of [["◀", previous, "이전"], ["▶", next, "다음"]]) {
      const button = el("button", null, symbol);
      button.type = "button";
      button.title = `${title} ${badge.label}`;
      button.disabled = shown.length === 0;
      button.addEventListener("click", () => {
        const target = pick();
        if (target) options.onSelect(target);
      });
      group.append(button);
    }
    bar.append(group);
  }
  return { bar, jumps };
}

function bindKeys(jumps, onSelect) {
  if (keyHandler) document.removeEventListener("keydown", keyHandler);
  keyHandler = (event) => {
    if (event.key !== "[" && event.key !== "]") return;
    if (event.target.closest && event.target.closest("input, select, textarea")) return;
    const target = event.key === "]" ? jumps.failure.next() : jumps.failure.previous();
    if (target) onSelect(target);
  };
  document.addEventListener("keydown", keyHandler);
}

// Draws badges, strip and footer into `container`. `options`: selected (step id), range ([fromEvent, toEvent] or null),
// axis ("order" | "time"), onSelect(event), onRange(fromEvent, toEvent), onClearRange(), onAxis(axis).
export function renderOverview(container, events, options) {
  container.replaceChildren();
  if (!events.length) {
    container.append(el("p", "empty", "도구 호출이 없습니다."));
    return;
  }
  const { bar, jumps } = renderBadges(events, options);
  const box = el("div", "ov-strip");
  const footer = el("div", "ov-footer");
  const toggle = el("div", "view-toggle");
  for (const [value, label] of [["order", "순서"], ["time", "실제 시간"]]) {
    const button = el("button", value === options.axis ? "active" : null, label);
    button.type = "button";
    button.addEventListener("click", () => options.onAxis(value));
    toggle.append(button);
  }
  footer.append(toggle);
  if (options.axis === "time") footer.append(el("span", "meta", "실제 시간 축: 가까운 사건은 겹쳐 보일 수 있습니다"));
  const info = el("span", "ov-info", eventText(events.find((event) => event.id === options.selected)));
  footer.append(info);
  if (options.range) {
    const clear = el("button", null, "범위 지우기");
    clear.type = "button";
    clear.addEventListener("click", options.onClearRange);
    footer.append(clear);
  }
  container.append(bar, box, footer);
  bindKeys(jumps, options.onSelect);
  drawStrip(box, events, options, info);
  let width = box.clientWidth;
  const observer = new ResizeObserver(() => {
    if (!box.isConnected) {
      observer.disconnect();
    } else if (box.clientWidth !== width) {
      width = box.clientWidth;
      drawStrip(box, events, options, info);
    }
  });
  observer.observe(box);
}
