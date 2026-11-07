// Flow graph of one turn drawn with D3 (global `d3` from vendor/d3-7.9.0.min.js).
// Spec: docs/design/FlowGraph.md section 6. Session text is untrusted: only ever use .text().

const LABEL_WIDTH = 180;
const ROW_HEIGHT = 26;
const LANE_PADDING = 6;
const PX_PER_SECOND = 40;
const MIN_GAP = 6;
const LONG_GAP_MS = 10000;
const BREAK_WIDTH = 48;
const WAVE_STEP = 6;
const WAVE_AMPLITUDE = 3;
const BAR_HEIGHT = 14;
const MIN_BAR = 6;
const POINT_RADIUS = 5;
const OVERLAP_MARGIN = 4;
const TOP_MARGIN = 22;
const RIGHT_MARGIN = 40;
const LEFT_MARGIN = 12;
const BREAK_LABEL_SPACING = 56;
const STATUS_SYMBOL = { success: "✓", error: "✕", interrupted: "⏸", running: "●", unfinished: "?" };
const LANE_KIND = { main: "주", subagent: "서브", background_agent: "백그라운드", background_shell: "백그라운드" };
const BAR_KINDS = new Set(["tool_call", "background_task"]);

function time(value) {
  return value ? new Date(value).getTime() : null;
}

function formatDuration(ms) {
  const seconds = Math.round(ms / 1000);
  if (seconds < 60) return `${seconds}초`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return seconds % 60 ? `${minutes}분 ${seconds % 60}초` : `${minutes}분`;
  return `${Math.floor(minutes / 60)}시간 ${minutes % 60}분`;
}

function formatClock(ms) {
  const date = new Date(ms);
  const pad = (value, size = 2) => String(value).padStart(size, "0");
  return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}.${pad(date.getMilliseconds(), 3)}`;
}

// Order-preserving time scale (FlowGraph.md section 6.1). "compress" keeps gaps up to LONG_GAP_MS proportional and
// cuts longer ones to BREAK_WIDTH with a wave mark; "real" keeps every gap proportional.
function buildScale(times, zoom, mode) {
  const sorted = [...new Set(times)].sort((a, b) => a - b);
  const domain = [sorted[0]];
  const range = [0];
  const breaks = [];
  for (let i = 1; i < sorted.length; i += 1) {
    const gap = sorted[i] - sorted[i - 1];
    const natural = (gap / 1000) * PX_PER_SECOND;
    const cut = mode !== "real" && gap > LONG_GAP_MS;
    const width = (mode === "real" ? natural : cut ? BREAK_WIDTH : Math.max(MIN_GAP, natural)) * zoom;
    domain.push(sorted[i]);
    range.push(range[range.length - 1] + width);
    if (cut) breaks.push({ x: range[range.length - 2] + width / 2, duration: gap });
  }
  if (domain.length === 1) {
    domain.push(domain[0] + 1);
    range.push(MIN_GAP * zoom);
  }
  return { scale: d3.scaleLinear().domain(domain).range(range).clamp(true), width: range[range.length - 1], breaks };
}

function orderLanes(lanes) {
  const children = d3.group(lanes.filter((lane) => lane.parent), (lane) => lane.parent);
  const ordered = [];
  const visit = (lane) => {
    ordered.push(lane);
    const kids = (children.get(lane.id) || []).slice().sort((a, b) => time(a.started_at) - time(b.started_at));
    kids.forEach(visit);
  };
  lanes.filter((lane) => !lane.parent).forEach(visit);
  // Lanes whose parent is missing still get drawn.
  lanes.filter((lane) => !ordered.includes(lane)).forEach(visit);
  return ordered;
}

function isBar(node) {
  return BAR_KINDS.has(node.kind) || (node.kind === "model" && time(node.ended_at) > time(node.started_at));
}

function layout(graph, zoom, mode) {
  const end = d3.max(graph.nodes.flatMap((node) => [time(node.started_at), time(node.ended_at)]).concat([time(graph.ended_at)]).filter(Boolean));
  const times = graph.nodes.flatMap((node) => [time(node.started_at), time(node.ended_at) ?? end, time(node.generation_started_at)]).filter((value) => value !== null);
  const { scale, width, breaks } = buildScale(times, zoom, mode);
  const lanes = orderLanes(graph.lanes);
  const placed = new Map();
  let y = TOP_MARGIN;
  const laneBoxes = [];
  for (const lane of lanes) {
    const rows = [];
    const nodes = graph.nodes.filter((node) => node.lane === lane.id);
    for (const node of nodes) {
      const bar = isBar(node);
      const start = scale(time(node.started_at));
      const finish = bar ? Math.max(scale(time(node.ended_at) ?? end), start + MIN_BAR) : start + POINT_RADIUS;
      const left = bar ? start : start - POINT_RADIUS;
      // A bar may touch the bar before it (writing runs straight into the tool run); points keep a margin.
      let row = rows.findIndex((last) => (last.bar && bar ? last.right <= left + 0.5 : last.right + OVERLAP_MARGIN <= left));
      if (row === -1) {
        row = rows.length;
        rows.push({ right: finish, bar });
      } else {
        rows[row] = { right: finish, bar };
      }
      const generation = time(node.generation_started_at);
      const xg = bar && generation !== null ? Math.min(finish, Math.max(start, scale(generation))) : null;
      placed.set(node.id, { node, isBar: bar, x0: start, x1: finish, xg, row, open: bar && !node.ended_at });
    }
    const height = Math.max(1, rows.length) * ROW_HEIGHT + LANE_PADDING * 2;
    laneBoxes.push({ lane, y, height });
    for (const item of placed.values()) {
      if (item.node.lane === lane.id && item.y === undefined) item.y = y + LANE_PADDING + item.row * ROW_HEIGHT + ROW_HEIGHT / 2;
    }
    y += height;
  }
  return { placed, laneBoxes, breaks, width, height: y };
}

function nodeTitle(node) {
  const start = time(node.started_at);
  const finish = time(node.ended_at);
  const generation = time(node.generation_started_at);
  const parts = [node.label || node.kind];
  if (node.status) parts.push(`상태: ${node.status}`);
  if (generation !== null) {
    if (generation > start) parts.push(`생각: ${formatDuration(generation - start)}`);
    parts.push(`작성: ${formatDuration(finish - generation)}${node.output_chars ? ` (${node.output_chars.toLocaleString()}자)` : ""}`);
  }
  parts.push(`시각: ${formatClock(start)}${finish && finish !== start ? ` ~ ${formatClock(finish)}` : ""}`);
  if (finish && finish !== start) parts.push(`실행 시간: ${formatDuration(finish - start)} (${finish - start}ms)`);
  if (node.approximate) parts.push(node.kind === "model" ? "시작 시각 근사(생각이 끝난 시각 − 걸린 시간)" : "시각 근사(hook 없음)");
  return parts.join("\n");
}

function drawBands(svg, laneBoxes, width) {
  const group = svg.append("g").attr("class", "g-lanes");
  laneBoxes.forEach(({ y, height }, index) => {
    group.append("rect").attr("class", index % 2 ? "g-band odd" : "g-band").attr("x", 0).attr("y", y).attr("width", width).attr("height", height);
  });
}

function drawLaneLabels(svg, laneBoxes) {
  laneBoxes.forEach(({ lane, y }) => {
    const label = svg.append("text").attr("class", `g-lane-label status-${lane.status}`).attr("x", 8).attr("y", y + LANE_PADDING + ROW_HEIGHT / 2).attr("dy", "0.35em");
    if (lane.kind !== "main") label.append("tspan").attr("class", "g-lane-kind").text(`${LANE_KIND[lane.kind] || lane.kind} `);
    label.append("tspan").text(`${STATUS_SYMBOL[lane.status] || ""} ${lane.label}`.trim().slice(0, 24));
    label.append("title").text(`${lane.label}\n상태: ${lane.status}`);
  });
}

function drawEdges(content, graph, placed) {
  const link = d3.linkHorizontal();
  const group = content.append("g").attr("class", "g-edges");
  for (const edge of graph.edges) {
    const source = placed.get(edge.source);
    const target = placed.get(edge.target);
    if (!source || !target) continue;
    // A subagent's result returns to the end of the call that spawned it.
    const targetX = edge.kind === "return" && target.isBar ? target.x1 : target.isBar ? target.x0 : target.x0 - POINT_RADIUS;
    const path = link({ source: [source.x1, source.y], target: [targetX, target.y] });
    group.append("path").attr("class", `g-edge ${edge.kind}`).attr("d", path).attr("marker-end", edge.kind === "return" ? "url(#g-arrow)" : null);
  }
}

// A bar crossing a cut gap gets a wave cut where the gap was shortened: it is longer than it looks.
function drawBarCuts(content, placed, breaks) {
  const group = content.append("g").attr("class", "g-bar-cuts");
  for (const item of placed.values()) {
    if (!item.isBar) continue;
    for (const gap of breaks) {
      if (gap.x <= item.x0 || gap.x >= item.x1) continue;
      const path = wavePath(gap.x, item.y - BAR_HEIGHT / 2 - 2, item.y + BAR_HEIGHT / 2 + 2);
      group.append("path").attr("class", "g-bar-cut-gap").attr("d", path);
      group.append("path").attr("class", "g-bar-cut").attr("d", path);
    }
  }
}

function drawNodes(content, placed, height, onSelect) {
  const group = content.append("g").attr("class", "g-nodes");
  for (const item of placed.values()) {
    const { node } = item;
    const element = group.append("g").attr("class", `g-node kind-${node.kind} status-${node.status || "none"}${node.approximate ? " approximate" : ""}${item.open ? " open" : ""}`).attr("data-id", node.id);
    if (node.kind === "user_message") {
      content.insert("line", ".g-edges").attr("class", "g-guide").attr("x1", item.x0).attr("x2", item.x0).attr("y1", TOP_MARGIN).attr("y2", height);
    }
    if (item.isBar && item.xg !== null) {
      // Model bar: thinking part, then the writing part hatched (FlowGraph.md section 6.3, I38).
      if (item.xg > item.x0) element.append("rect").attr("class", "g-thinking").attr("x", item.x0).attr("y", item.y - BAR_HEIGHT / 2).attr("width", item.xg - item.x0).attr("height", BAR_HEIGHT).attr("rx", 3);
      element.append("rect").attr("class", "g-writing").attr("x", item.xg).attr("y", item.y - BAR_HEIGHT / 2).attr("width", Math.max(MIN_BAR, item.x1 - item.xg)).attr("height", BAR_HEIGHT).attr("rx", 3);
      if (item.x1 - item.x0 > 40) {
        element.append("text").attr("class", "g-bar-label model").attr("x", item.x0 + 4).attr("y", item.y).attr("dy", "0.35em").text(node.label.slice(0, Math.floor((item.x1 - item.x0 - 8) / 7)));
      }
    } else if (item.isBar) {
      element.append("rect").attr("x", item.x0).attr("y", item.y - BAR_HEIGHT / 2).attr("width", item.x1 - item.x0).attr("height", BAR_HEIGHT).attr("rx", 3);
      const symbol = STATUS_SYMBOL[node.status] || "";
      const text = `${symbol} ${node.label}`;
      if (item.x1 - item.x0 > 40) {
        element.append("text").attr("class", "g-bar-label").attr("x", item.x0 + 4).attr("y", item.y).attr("dy", "0.35em").text(text.slice(0, Math.floor((item.x1 - item.x0 - 8) / 7)));
      }
    } else if (node.kind === "user_message") {
      element.append("path").attr("d", d3.symbol(d3.symbolDiamond, USER_MESSAGE_SIZE)()).attr("transform", `translate(${item.x0},${item.y})`);
    } else if (node.kind === "compact" || node.kind === "hook_failure") {
      element.append("rect").attr("x", item.x0 - 4).attr("y", item.y - 4).attr("width", 8).attr("height", 8);
    } else {
      element.append("circle").attr("cx", item.x0).attr("cy", item.y).attr("r", node.kind === "prompt" ? POINT_RADIUS + 2 : node.kind === "model" ? POINT_RADIUS - 1 : POINT_RADIUS);
    }
    element.append("title").text(nodeTitle(node));
    element.on("click", () => onSelect(node));
  }
}

// Diagonal hatch for the writing part of a model bar, shared by the graph and the legend swatch.
function addHatch(svg) {
  const pattern = svg.select("defs").empty() ? svg.append("defs") : svg.select("defs");
  pattern.append("pattern").attr("id", "g-hatch").attr("width", 5).attr("height", 5).attr("patternUnits", "userSpaceOnUse")
    .attr("patternTransform", "rotate(45)")
    .call((p) => {
      p.append("rect").attr("class", "g-hatch-bg").attr("width", 5).attr("height", 5);
      p.append("line").attr("class", "g-hatch-line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 5);
    });
}

const USER_MESSAGE_SIZE = 140;
const LEGEND_WIDTH = 26;
const LEGEND_HEIGHT = 24;
const LEGEND = [
  ["run", "도구 실행(색 = 상태: ✓ 성공 · ✕ 오류 · ⏸ 중단)"],
  ["thinking", "생각"],
  ["writing", "작성(응답·도구 입력 생성)"],
  ["approximate", "시각 근사(점선 테두리)"],
  ["wave", "≈ 줄인 대기"],
  ["user", "사용자 메시지(세로 점선이 모든 줄을 가로지름)"],
  ["prompt", "지시"],
  ["notification", "알림"],
];

// One-line legend above the graph (FlowGraph.md section 6.3, I38). Swatches reuse the graph's own sizes and classes,
// so a symbol looks the same in the legend and in the graph.
function renderLegend() {
  const legend = document.createElement("div");
  legend.className = "g-legend";
  const mid = LEGEND_HEIGHT / 2;
  for (const [kind, text] of LEGEND) {
    const item = document.createElement("span");
    item.className = "g-legend-item";
    const svg = d3.create("svg").attr("class", "g-svg").attr("width", LEGEND_WIDTH).attr("height", LEGEND_HEIGHT);
    if (kind === "writing") addHatch(svg);
    const bar = (classes, rectClass = null) => svg.append("g").attr("class", classes).append("rect").attr("class", rectClass)
      .attr("x", 1).attr("y", mid - BAR_HEIGHT / 2).attr("width", LEGEND_WIDTH - 2).attr("height", BAR_HEIGHT).attr("rx", 3);
    if (kind === "run") bar("g-node status-success");
    else if (kind === "thinking") bar("g-node kind-model", "g-thinking");
    else if (kind === "writing") bar("g-node kind-model", "g-writing");
    else if (kind === "approximate") bar("g-node kind-model approximate", "g-thinking");
    else if (kind === "wave") svg.append("path").attr("class", "g-break").attr("d", wavePath(LEGEND_WIDTH / 2, 0, LEGEND_HEIGHT));
    else if (kind === "user") {
      svg.append("line").attr("class", "g-guide").attr("x1", LEGEND_WIDTH / 2).attr("x2", LEGEND_WIDTH / 2).attr("y1", 0).attr("y2", LEGEND_HEIGHT);
      svg.append("g").attr("class", "g-node kind-user_message").append("path")
        .attr("d", d3.symbol(d3.symbolDiamond, USER_MESSAGE_SIZE)()).attr("transform", `translate(${LEGEND_WIDTH / 2},${mid})`);
    } else {
      svg.append("g").attr("class", `g-node kind-${kind}`).append("circle").attr("cx", LEGEND_WIDTH / 2).attr("cy", mid)
        .attr("r", kind === "prompt" ? POINT_RADIUS + 2 : POINT_RADIUS);
    }
    const label = document.createElement("span");
    label.textContent = text;
    item.append(svg.node(), label);
    legend.append(item);
  }
  return legend;
}

function wavePath(x, y0, y1) {
  let path = `M ${x} ${y0}`;
  for (let y = y0, side = 1; y < y1; y += WAVE_STEP, side = -side) {
    path += ` Q ${x + side * WAVE_AMPLITUDE} ${y + WAVE_STEP / 2} ${x} ${Math.min(y + WAVE_STEP, y1)}`;
  }
  return path;
}

function drawBreaks(content, breaks, height) {
  const group = content.append("g").attr("class", "g-breaks");
  let lastLabel = -Infinity;
  for (const gap of breaks) {
    const text = `≈ ${formatDuration(gap.duration)}`;
    group.append("path").attr("class", "g-break").attr("d", wavePath(gap.x, TOP_MARGIN - 4, height))
      .append("title").text(`생략한 구간: ${formatDuration(gap.duration)}`);
    // Labels too close to the previous one would overlap, so only the line remains.
    if (gap.x - lastLabel < BREAK_LABEL_SPACING) continue;
    lastLabel = gap.x;
    group.append("text").attr("class", "g-break-label").attr("x", gap.x).attr("y", 12).attr("text-anchor", "middle").text(text);
  }
}

// Draws the graph into `container` with zoom and time-axis controls; `onSelect(node)` runs when a node is clicked.
// options.initialId names a node to start selected (WebUI.md section 7.5); it is ignored when no node has that id.
// options.scale is "compress" or "real" (section 6.1) and options.onScale(scale) runs when the toggle is pressed.
export function renderGraph(container, graph, onSelect, options = {}) {
  const { initialId = null, scale: mode = "compress", onScale = () => {} } = options;
  let zoom = 1;
  let selected = null;
  const toolbar = document.createElement("div");
  toolbar.className = "g-toolbar";
  // Lane names stay fixed on the left while the timeline scrolls sideways.
  const canvas = document.createElement("div");
  canvas.className = "g-canvas";
  const labels = document.createElement("div");
  labels.className = "g-labels";
  const scroller = document.createElement("div");
  scroller.className = "g-scroller";
  canvas.append(labels, scroller);
  const hint = document.createElement("span");
  hint.className = "meta";
  hint.textContent = "Ctrl·⌘+휠로도 확대 · 가로 스크롤로 이동 · 노드를 누르면 상세";
  const zoomButtons = [
    ["축소", "가로 배율을 줄입니다", () => setZoom(zoom / 1.5)],
    ["확대", "가로 배율을 키웁니다", () => setZoom(zoom * 1.5)],
    ["전체 보기", "그래프 전체를 화면 폭에 맞춥니다", () => setZoom(fitZoom())],
  ];
  const buttons = zoomButtons.map(([label, title, action]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.title = title;
    button.addEventListener("click", action);
    return button;
  });
  const scaleToggle = document.createElement("div");
  scaleToggle.className = "view-toggle g-scale";
  const scaleLabel = document.createElement("span");
  scaleLabel.className = "meta";
  scaleLabel.textContent = "시간축:";
  scaleToggle.append(scaleLabel);
  for (const [value, label, title] of [["compress", "긴 대기 줄여 보기", "10초를 넘는 간격을 물결(≈)로 줄여 보여 줍니다"], ["real", "실제 시간 길이로 보기", "모든 가로 길이를 실제 걸린 시간에 비례시킵니다"]]) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.title = title;
    if (value === mode) button.className = "active";
    button.addEventListener("click", () => { if (value !== mode) onScale(value); });
    scaleToggle.append(button);
  }
  toolbar.append(scaleToggle, ...buttons, hint);
  container.replaceChildren(toolbar, renderLegend(), canvas);

  function fitZoom() {
    const natural = layout(graph, 1, mode).width;
    const available = scroller.clientWidth - LEFT_MARGIN - RIGHT_MARGIN;
    return natural > 0 && available > 0 ? Math.min(1, available / natural) : 1;
  }

  function setZoom(value) {
    const anchor = (scroller.scrollLeft + scroller.clientWidth / 2) / Math.max(1, scroller.scrollWidth);
    zoom = Math.min(40, Math.max(0.05, value));
    draw();
    scroller.scrollLeft = anchor * scroller.scrollWidth - scroller.clientWidth / 2;
  }

  function draw() {
    const { placed, laneBoxes, breaks, width, height } = layout(graph, zoom, mode);
    const totalWidth = LEFT_MARGIN + width + RIGHT_MARGIN;
    const labelSvg = d3.create("svg").attr("class", "g-svg").attr("width", LABEL_WIDTH).attr("height", height + 8);
    drawBands(labelSvg, laneBoxes, LABEL_WIDTH);
    drawLaneLabels(labelSvg, laneBoxes);
    const svg = d3.create("svg").attr("class", "g-svg").attr("width", totalWidth).attr("height", height + 8);
    svg.append("defs").append("marker").attr("id", "g-arrow").attr("viewBox", "0 0 10 10").attr("refX", 9).attr("refY", 5)
      .attr("markerWidth", 6).attr("markerHeight", 6).attr("orient", "auto-start-reverse")
      .append("path").attr("d", "M 0 0 L 10 5 L 0 10 z").attr("class", "g-arrow");
    addHatch(svg);
    drawBands(svg, laneBoxes, totalWidth);
    const content = svg.append("g").attr("transform", `translate(${LEFT_MARGIN},0)`);
    drawBreaks(content, breaks, height);
    drawEdges(content, graph, placed);
    drawNodes(content, placed, height, (node) => {
      selected = node.id;
      highlight();
      onSelect(node);
    });
    drawBarCuts(content, placed, breaks);
    labels.replaceChildren(labelSvg.node());
    scroller.replaceChildren(svg.node());
    highlight();
  }

  function highlight() {
    d3.select(canvas).selectAll(".g-node").classed("selected", function () {
      return this.getAttribute("data-id") === selected;
    });
  }

  scroller.addEventListener("wheel", (event) => {
    if (!event.ctrlKey && !event.metaKey) return;
    event.preventDefault();
    setZoom(zoom * (event.deltaY < 0 ? 1.15 : 1 / 1.15));
  }, { passive: false });

  draw();
  // Real-time proportion can be very wide, so it always starts fitted (section 6.1).
  if (scroller.clientWidth) setZoom(mode === "real" ? fitZoom() : Math.max(fitZoom(), 0.15));
  const initial = initialId === null ? null : graph.nodes.find((node) => node.id === String(initialId));
  if (initial) {
    selected = initial.id;
    highlight();
    onSelect(initial);
    const item = layout(graph, zoom, mode).placed.get(initial.id);
    if (item) scroller.scrollLeft = LEFT_MARGIN + item.x0 - scroller.clientWidth / 2;
  }
}
