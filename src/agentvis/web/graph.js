// Flow graph of one turn drawn with D3 (global `d3` from vendor/d3-7.9.0.min.js).
// Spec: docs/design/FlowGraph.md section 6. Session text is untrusted: only ever use .text().

const LABEL_WIDTH = 180;
const ROW_HEIGHT = 26;
const LANE_PADDING = 6;
const PX_PER_SECOND = 40;
const MIN_GAP = 6;
const MAX_GAP = 120;
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
  const minutes = Math.round(seconds / 60);
  return minutes < 60 ? `${minutes}분` : `${Math.floor(minutes / 60)}시간 ${minutes % 60}분`;
}

function formatClock(ms) {
  const date = new Date(ms);
  const pad = (value, size = 2) => String(value).padStart(size, "0");
  return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}.${pad(date.getMilliseconds(), 3)}`;
}

// Order-preserving compressed time scale: each gap between neighbouring times is clamped.
function buildScale(times, zoom) {
  const sorted = [...new Set(times)].sort((a, b) => a - b);
  const domain = [sorted[0]];
  const range = [0];
  const breaks = [];
  for (let i = 1; i < sorted.length; i += 1) {
    const gap = sorted[i] - sorted[i - 1];
    const natural = (gap / 1000) * PX_PER_SECOND;
    const width = Math.min(MAX_GAP, Math.max(MIN_GAP, natural)) * zoom;
    domain.push(sorted[i]);
    range.push(range[range.length - 1] + width);
    if (natural > MAX_GAP) breaks.push({ x: range[range.length - 2] + width / 2, duration: gap });
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

function layout(graph, zoom) {
  const end = d3.max(graph.nodes.flatMap((node) => [time(node.started_at), time(node.ended_at)]).concat([time(graph.ended_at)]).filter(Boolean));
  const times = graph.nodes.flatMap((node) => [time(node.started_at), time(node.ended_at) ?? end]);
  const { scale, width, breaks } = buildScale(times, zoom);
  const lanes = orderLanes(graph.lanes);
  const placed = new Map();
  let y = TOP_MARGIN;
  const laneBoxes = [];
  for (const lane of lanes) {
    const rows = [];
    const nodes = graph.nodes.filter((node) => node.lane === lane.id);
    for (const node of nodes) {
      const isBar = BAR_KINDS.has(node.kind);
      const start = scale(time(node.started_at));
      const finish = isBar ? Math.max(scale(time(node.ended_at) ?? end), start + MIN_BAR) : start + POINT_RADIUS;
      const left = isBar ? start : start - POINT_RADIUS;
      let row = rows.findIndex((right) => right + OVERLAP_MARGIN <= left);
      if (row === -1) {
        row = rows.length;
        rows.push(finish);
      } else {
        rows[row] = finish;
      }
      placed.set(node.id, { node, isBar, x0: start, x1: finish, row, open: isBar && !node.ended_at });
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
  const parts = [node.label || node.kind];
  if (node.status) parts.push(`상태: ${node.status}`);
  parts.push(`시각: ${formatClock(start)}${finish && finish !== start ? ` ~ ${formatClock(finish)}` : ""}`);
  if (finish && finish !== start) parts.push(`실행 시간: ${formatDuration(finish - start)} (${finish - start}ms)`);
  if (node.approximate) parts.push("시각 근사(hook 없음)");
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

function drawNodes(content, placed, height, onSelect) {
  const group = content.append("g").attr("class", "g-nodes");
  for (const item of placed.values()) {
    const { node } = item;
    const element = group.append("g").attr("class", `g-node kind-${node.kind} status-${node.status || "none"}${node.approximate ? " approximate" : ""}${item.open ? " open" : ""}`).attr("data-id", node.id);
    if (node.kind === "user_message") {
      content.insert("line", ".g-edges").attr("class", "g-guide").attr("x1", item.x0).attr("x2", item.x0).attr("y1", TOP_MARGIN).attr("y2", height);
    }
    if (item.isBar) {
      element.append("rect").attr("x", item.x0).attr("y", item.y - BAR_HEIGHT / 2).attr("width", item.x1 - item.x0).attr("height", BAR_HEIGHT).attr("rx", 3);
      const symbol = STATUS_SYMBOL[node.status] || "";
      const text = `${symbol} ${node.label}`;
      if (item.x1 - item.x0 > 40) {
        element.append("text").attr("class", "g-bar-label").attr("x", item.x0 + 4).attr("y", item.y).attr("dy", "0.35em").text(text.slice(0, Math.floor((item.x1 - item.x0 - 8) / 7)));
      }
    } else if (node.kind === "user_message") {
      element.append("path").attr("d", d3.symbol(d3.symbolDiamond, 140)()).attr("transform", `translate(${item.x0},${item.y})`);
    } else if (node.kind === "compact" || node.kind === "hook_failure") {
      element.append("rect").attr("x", item.x0 - 4).attr("y", item.y - 4).attr("width", 8).attr("height", 8);
    } else {
      element.append("circle").attr("cx", item.x0).attr("cy", item.y).attr("r", node.kind === "prompt" ? POINT_RADIUS + 2 : node.kind === "model" ? POINT_RADIUS - 1 : POINT_RADIUS);
    }
    element.append("title").text(nodeTitle(node));
    element.on("click", () => onSelect(node));
  }
}

function drawBreaks(content, breaks, height) {
  const group = content.append("g").attr("class", "g-breaks");
  let lastLabel = -Infinity;
  for (const gap of breaks) {
    const text = `⋯ ${formatDuration(gap.duration)}`;
    group.append("line").attr("class", "g-break").attr("x1", gap.x).attr("x2", gap.x).attr("y1", TOP_MARGIN - 4).attr("y2", height)
      .append("title").text(text);
    // Labels too close to the previous one would overlap, so only the line remains.
    if (gap.x - lastLabel < BREAK_LABEL_SPACING) continue;
    lastLabel = gap.x;
    group.append("text").attr("class", "g-break-label").attr("x", gap.x).attr("y", 12).attr("text-anchor", "middle").text(text);
  }
}

// Draws the graph into `container` with zoom controls; `onSelect(node)` runs when a node is clicked.
export function renderGraph(container, graph, onSelect) {
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
  hint.textContent = "확대: Ctrl·⌘+휠 또는 단추 · 이동: 가로 스크롤 · 노드를 누르면 상세";
  const buttons = [["−", () => setZoom(zoom / 1.5)], ["+", () => setZoom(zoom * 1.5)], ["맞춤", () => setZoom(fitZoom())]].map(([label, action]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", action);
    return button;
  });
  toolbar.append(...buttons, hint);
  container.replaceChildren(toolbar, canvas);

  function fitZoom() {
    const natural = layout(graph, 1).width;
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
    const { placed, laneBoxes, breaks, width, height } = layout(graph, zoom);
    const totalWidth = LEFT_MARGIN + width + RIGHT_MARGIN;
    const labelSvg = d3.create("svg").attr("class", "g-svg").attr("width", LABEL_WIDTH).attr("height", height + 8);
    drawBands(labelSvg, laneBoxes, LABEL_WIDTH);
    drawLaneLabels(labelSvg, laneBoxes);
    const svg = d3.create("svg").attr("class", "g-svg").attr("width", totalWidth).attr("height", height + 8);
    svg.append("defs").append("marker").attr("id", "g-arrow").attr("viewBox", "0 0 10 10").attr("refX", 9).attr("refY", 5)
      .attr("markerWidth", 6).attr("markerHeight", 6).attr("orient", "auto-start-reverse")
      .append("path").attr("d", "M 0 0 L 10 5 L 0 10 z").attr("class", "g-arrow");
    drawBands(svg, laneBoxes, totalWidth);
    const content = svg.append("g").attr("transform", `translate(${LEFT_MARGIN},0)`);
    drawBreaks(content, breaks, height);
    drawEdges(content, graph, placed);
    drawNodes(content, placed, height, (node) => {
      selected = node.id;
      highlight();
      onSelect(node);
    });
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
  if (scroller.clientWidth) setZoom(Math.max(fitZoom(), 0.15));
}
