// Session overview strip as a turn sequence (E1) and jump badges (E3) drawn with D3 (global `d3`).
// Spec: docs/design/WebUI.md section 7, docs/design/VisualEncoding.md sections 3.1 and 3.3.
// Session text is untrusted: only ever use textContent or .text().

const SYMBOL_ROW = 14;
const CELL_HEIGHT = 28;
const CELL_GAP = 2;
const MIN_TIMED_WIDTH = 6;
const MIN_LABEL_WIDTH = 28;
const FAILURE = new Set(["error", "interrupted"]);
const BADGES = [
  { key: "failure", label: "실패한 턴", match: (turn) => turn.failed },
  { key: "user", label: "작업 중 사용자 메시지가 있는 턴", match: (turn) => turn.userMessages > 0 },
  { key: "compact", label: "압축이 있는 턴", match: (turn) => turn.compacts > 0 },
];

let keyHandler = null;

function formatDuration(ms) {
  const seconds = Math.round(ms / 1000);
  if (seconds < 60) return `${seconds}초`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return seconds % 60 ? `${minutes}분 ${seconds % 60}초` : `${minutes}분`;
  return `${Math.floor(minutes / 60)}시간 ${minutes % 60}분`;
}

// One summary per turn (WebUI.md section 7.1).
export function summarizeTurns(view) {
  return view.turns.map((turn) => {
    const steps = turn.steps;
    const end = turn.ended_at || (steps.length ? steps[steps.length - 1].at : turn.started_at);
    const firstFailure = steps.find((step) => step.kind === "tool_call" && step.tool_call && FAILURE.has(step.tool_call.status));
    return {
      index: turn.index,
      prompt: String(turn.prompt || "").trim().split("\n")[0],
      state: turn.state,
      tools: turn.tool_call_count,
      failures: turn.failure_count,
      failed: turn.failure_count > 0 || turn.state === "failed",
      firstFailure: firstFailure ? firstFailure.id : null,
      userMessages: steps.filter((step) => step.kind === "user_message").length,
      compacts: steps.filter((step) => step.kind === "compact").length,
      duration: Math.max(0, new Date(end).getTime() - new Date(turn.started_at).getTime()),
    };
  });
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function turnText(turn) {
  if (!turn) return "";
  const parts = [`#${turn.index}`, turn.prompt.length > 60 ? `${turn.prompt.slice(0, 60)}…` : turn.prompt, `도구 ${turn.tools}`];
  if (turn.failures) parts.push(`실패 ${turn.failures}`);
  parts.push(formatDuration(turn.duration));
  if (turn.userMessages) parts.push(`작업 중 사용자 메시지 ${turn.userMessages}`);
  if (turn.state === "running") parts.push("실행 중");
  return parts.join(" · ");
}

// Left edge and width of every cell: equal widths, or widths proportional to duration with a minimum.
function cellBoxes(turns, width, mode) {
  const usable = width - CELL_GAP * (turns.length - 1);
  let widths;
  if (mode === "time") {
    const total = turns.reduce((sum, turn) => sum + turn.duration, 0) || 1;
    const raw = turns.map((turn) => (turn.duration / total) * usable);
    const short = raw.filter((value) => value < MIN_TIMED_WIDTH).length;
    const longTotal = raw.filter((value) => value >= MIN_TIMED_WIDTH).reduce((sum, value) => sum + value, 0) || 1;
    const rest = Math.max(0, usable - short * MIN_TIMED_WIDTH);
    widths = raw.map((value) => (value < MIN_TIMED_WIDTH ? MIN_TIMED_WIDTH : (value / longTotal) * rest));
  } else {
    widths = turns.map(() => usable / turns.length);
  }
  let x = 0;
  return widths.map((w) => {
    const box = { x, w: Math.max(1, w) };
    x += w + CELL_GAP;
    return box;
  });
}

function drawStrip(box, turns, options, info) {
  const width = box.clientWidth;
  if (!width) return;
  const height = SYMBOL_ROW + CELL_HEIGHT;
  const cells = cellBoxes(turns, width, options.width);
  const selected = turns.find((turn) => turn.index === options.selected) || null;
  const svg = d3.create("svg").attr("class", "ov-svg").attr("width", width).attr("height", height);
  turns.forEach((turn, i) => {
    const { x, w } = cells[i];
    const group = svg.append("g").attr("class", "ov-turn-cell").attr("data-turn", turn.index);
    const classes = ["ov-cell", turn.failed ? "failed" : "routine"];
    if (turn.state === "running") classes.push("running");
    if (turn === selected) classes.push("selected");
    group.append("rect").attr("class", classes.join(" ")).attr("x", x).attr("y", SYMBOL_ROW).attr("width", w).attr("height", CELL_HEIGHT).attr("rx", 3);
    if (w >= MIN_LABEL_WIDTH) {
      const label = turn.failed ? `#${turn.index} ✕${turn.failures || ""}` : `#${turn.index}`;
      const fits = Math.max(1, Math.floor((w - 6) / 6.5));
      group.append("text").attr("class", turn.failed ? "ov-cell-label failed" : "ov-cell-label").attr("x", x + 4)
        .attr("y", SYMBOL_ROW + CELL_HEIGHT / 2).attr("dy", "0.35em").text(label.slice(0, fits));
    }
    if (turn.userMessages) {
      svg.append("text").attr("class", "ov-symbol ov-symbol-user").attr("x", x + w / 2).attr("y", SYMBOL_ROW - 3).attr("text-anchor", "middle").text("◆");
    }
    if (turn.compacts) {
      svg.append("line").attr("class", "ov-compact").attr("x1", x - CELL_GAP / 2).attr("x2", x - CELL_GAP / 2).attr("y1", 0).attr("y2", height);
      svg.append("text").attr("class", "ov-compact-label").attr("x", x + 2).attr("y", 10).text("압축");
    }
    group.on("click", () => options.onSelect(turn, false));
    group.on("mouseenter", () => { info.textContent = turnText(turn); });
  });
  svg.on("mouseleave", () => { info.textContent = turnText(selected); });
  box.replaceChildren(svg.node());
}

function renderBadges(turns, options) {
  const bar = el("div", "ov-badges");
  const current = turns.find((turn) => turn.index === options.selected);
  const jumps = {};
  for (const badge of BADGES) {
    const shown = turns.filter(badge.match);
    const next = () => (current ? shown.find((turn) => turn.index > current.index) : shown[0]);
    const previous = () => (current ? shown.filter((turn) => turn.index < current.index).pop() : shown[shown.length - 1]);
    jumps[badge.key] = { next, previous };
    const group = el("span", `ov-badge ov-badge-${badge.key}`);
    group.append(el("span", "ov-badge-label", `${badge.label} ${shown.length}`));
    for (const [symbol, pick, title] of [["◀", previous, "이전"], ["▶", next, "다음"]]) {
      const button = el("button", null, symbol);
      button.type = "button";
      button.title = `${title} ${badge.label}`;
      button.disabled = shown.length === 0;
      button.addEventListener("click", () => {
        const target = pick();
        if (target) options.onSelect(target, badge.key === "failure");
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
    if (target) onSelect(target, true);
  };
  document.addEventListener("keydown", keyHandler);
}

// Draws badges, strip and footer into `container`. `options`: selected (turn index), width ("equal" | "time"),
// onSelect(turn, toFailure) where toFailure asks to also select the turn's first failed step, onWidth(width).
export function renderOverview(container, turns, options) {
  container.replaceChildren();
  if (!turns.length) {
    container.append(el("p", "empty", "턴이 없습니다."));
    return;
  }
  const { bar, jumps } = renderBadges(turns, options);
  const box = el("div", "ov-strip");
  const footer = el("div", "ov-footer");
  const toggle = el("div", "view-toggle");
  toggle.append(el("span", "meta", "턴 너비:"));
  for (const [value, label, title] of [["equal", "같게", "모든 턴을 같은 너비로 그립니다"], ["time", "걸린 시간에 비례", "턴 너비를 그 턴에 걸린 시간에 비례시킵니다"]]) {
    const button = el("button", value === options.width ? "active" : null, label);
    button.type = "button";
    button.title = title;
    button.addEventListener("click", () => options.onWidth(value));
    toggle.append(button);
  }
  const info = el("span", "ov-info", turnText(turns.find((turn) => turn.index === options.selected)));
  footer.append(toggle, info);
  container.append(bar, box, footer);
  bindKeys(jumps, options.onSelect);
  drawStrip(box, turns, options, info);
  let width = box.clientWidth;
  const observer = new ResizeObserver(() => {
    if (!box.isConnected) {
      observer.disconnect();
    } else if (box.clientWidth !== width) {
      width = box.clientWidth;
      drawStrip(box, turns, options, info);
    }
  });
  observer.observe(box);
}
