"""Build the execution flow graph of one turn from a session view.

@doc: docs/design/FlowGraph.md
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from agentvis.analysis.session import SessionView, Step, ToolCall, Turn

_LABEL_CHARS = 80
_BACKGROUND_STATUS = {"completed": "success", "failed": "error", "killed": "interrupted"}
_MODEL_KINDS = ("thinking", "text")
# A tool-only response gets its own model node only when writing it took at least this long (FlowGraph.md 3.2).
GENERATION_NODE_MIN_MS = 5000


@dataclass
class Lane:
    """One actor that works in order: the main agent, a subagent or a background task.

    @doc: docs/design/FlowGraph.md#31-줄
    """

    id: str
    kind: str
    label: str
    parent: str | None
    spawned_by: str | None
    started_at: datetime | None
    ended_at: datetime | None
    status: str


@dataclass
class Node:
    """One point or bar in the graph.

    @doc: docs/design/FlowGraph.md#32-노드
    """

    id: str
    lane: str
    kind: str
    started_at: datetime
    ended_at: datetime | None
    label: str
    status: str | None = None
    approximate: bool = False
    step_ids: list[int] = field(default_factory=list)
    generation_started_at: datetime | None = None
    output_chars: int | None = None


@dataclass
class Edge:
    """A link between two nodes.

    @doc: docs/design/FlowGraph.md#33-간선
    """

    source: str
    target: str
    kind: str


@dataclass
class FlowGraph:
    """The lanes, nodes and edges of one turn.

    @doc: docs/design/FlowGraph.md#34-그래프
    """

    session_id: str
    turn_index: int
    started_at: datetime
    ended_at: datetime | None
    lanes: list[Lane] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)


def _first_line(text: object) -> str:
    lines = str(text or "").strip().splitlines()
    return lines[0][:_LABEL_CHARS] if lines else ""


def _tool_label(call: ToolCall) -> str:
    data = call.input if isinstance(call.input, dict) else {}
    summary = next((data[key] for key in ("description", "command", "file_path", "pattern", "url") if data.get(key)), "")
    return f"{call.tool_name or '도구'} {_first_line(summary)}".strip()


def _thinking_ms(steps: list[Step]) -> int | None:
    durations = [step.detail["duration_ms"] for step in steps if "duration_ms" in step.detail]
    return sum(durations) if durations else None


def _duration_text(ms: float) -> str:
    seconds = round(ms / 1000)
    if seconds < 60:
        return f"{seconds}초"
    minutes, rest = divmod(seconds, 60)
    return f"{minutes}분 {rest}초" if rest else f"{minutes}분"


def _model_label(thinking: int | None, generation_ms: float) -> str:
    parts = [f"생각 {thinking / 1000:.1f}초"] if thinking is not None else []
    if generation_ms >= GENERATION_NODE_MIN_MS:
        parts.append(f"작성 {_duration_text(generation_ms)}")
    return " · ".join(parts) or "생각"


def _output_chars(steps: list[Step]) -> int:
    texts = [step.text or "" for step in steps if step.kind == "text"]
    inputs = [json.dumps(step.tool_call.input, ensure_ascii=False) for step in steps if step.tool_call is not None]
    return sum(len(value) for value in texts + inputs)


class _GraphBuilder:
    def __init__(self, graph: FlowGraph, turn: Turn, session_ended: bool) -> None:
        self.graph = graph
        self.turn = turn
        self.session_ended = session_ended
        self.by_id: dict[str, Node] = {}

    def node(self, node: Node) -> Node:
        self.graph.nodes.append(node)
        self.by_id[node.id] = node
        return node

    def frontier_end(self, frontier: list[str]) -> datetime | None:
        ends = [node.ended_at or node.started_at for node in (self.by_id.get(item) for item in frontier) if node is not None]
        return max(ends) if ends else None

    def link(self, sources: list[str], target: str, kind: str = "next") -> None:
        for source in sources:
            self.graph.edges.append(Edge(source, target, kind))

    def stages(self, steps: list[Step]) -> list[list[Step]]:
        stages: list[list[Step]] = []
        for step in steps:
            groupable = step.message_id is not None and step.kind in (*_MODEL_KINDS, "tool_call")
            if groupable and stages and stages[-1][0].message_id == step.message_id:
                stages[-1].append(step)
            else:
                stages.append([step])
        return stages

    def lane(self, lane: Lane, steps: list[Step], frontier: list[str]) -> tuple[list[str], list[str]]:
        """Add a lane's nodes and next edges; return its entry nodes and final frontier."""
        entry: list[str] = []
        for stage in self.stages(steps):
            heads, tails = self.stage(lane, stage, self.frontier_end(frontier))
            if not heads:
                continue
            for head in heads:
                self.link(frontier, head)
            if not entry:
                entry = heads
            frontier = tails
        return entry, frontier

    def stage(self, lane: Lane, stage: list[Step], previous_end: datetime | None) -> tuple[list[str], list[str]]:
        model_steps = [step for step in stage if step.kind in _MODEL_KINDS]
        tool_steps = [step for step in stage if step.kind == "tool_call" and step.tool_call is not None]
        if not model_steps and not tool_steps:
            point = self.point(lane, stage[0])
            return ([point.id], [point.id]) if point else ([], [])
        tools = [self.tool(lane, step) for step in tool_steps]
        # Writing the response runs from the end of thinking (a thinking record is written when thinking ends), or
        # from the end of the previous nodes, to the response's last record (FlowGraph.md 3.2, I38).
        thought = bool(model_steps) and model_steps[0].kind == "thinking"
        generation_start = model_steps[0].at if thought else previous_end
        end = max(step.at for step in stage)
        generating = generation_start is not None and end > generation_start
        generation_ms = (end - generation_start).total_seconds() * 1000 if generating else 0.0
        if not model_steps and generation_ms < GENERATION_NODE_MIN_MS:
            return tools, tools
        thinking = _thinking_ms(model_steps)
        anchor = generation_start if generation_start is not None else model_steps[0].at
        start = anchor - timedelta(milliseconds=thinking) if thinking else anchor
        text = next((step.text for step in model_steps if step.kind == "text"), None)
        label = _first_line(text) if text is not None else _model_label(thinking, generation_ms)
        first = model_steps[0] if model_steps else tool_steps[0]
        node_id = str(first.id) if model_steps else f"gen:{first.id}"
        step_ids = [step.id for step in (model_steps or tool_steps)]
        model = self.node(Node(node_id, lane.id, "model", start, end if generating else anchor, label,
                               approximate=bool(thinking) or (generating and not thought), step_ids=step_ids,
                               generation_started_at=generation_start if generating else None, output_chars=_output_chars(stage)))
        for tool in tools:
            self.link([model.id], tool)
        return [model.id], tools or [model.id]

    def point(self, lane: Lane, step: Step) -> Node | None:
        if step.kind == "subagent":
            self.child_unlinked(lane, step)
            return None
        label = {"compact": "대화 요약(문맥 압축)", "hook_failure": "hook 전달 실패"}.get(step.kind) or _first_line(step.text)
        return self.node(Node(str(step.id), lane.id, step.kind, step.at, step.at, label, step_ids=[step.id]))

    def tool(self, lane: Lane, step: Step) -> str:
        call = step.tool_call
        assert call is not None
        start = call.started_at or step.at
        node = self.node(Node(str(step.id), lane.id, "tool_call", start, call.ended_at, _tool_label(call), call.status,
                              call.approximate, [step.id]))
        background = call.background
        if background is not None and background["kind"] == "shell":
            self.background_shell(lane, node, call)
        elif call.subagent is not None:
            self.child_agent(lane, node, call)
        return node.id

    def background_status(self, call: ToolCall) -> str:
        background = call.background or {}
        if background.get("notification_step_id") is not None:
            return _BACKGROUND_STATUS.get(background.get("status"), "unfinished")
        # Background tasks such as servers outlive their turn, so only the session's end settles them.
        return "unfinished" if self.session_ended else "running"

    def background_shell(self, parent: Lane, spawner: Node, call: ToolCall) -> None:
        background = call.background or {}
        status = self.background_status(call)
        lane = Lane(call.tool_use_id, "background_shell", _tool_label(call), parent.id, spawner.id,
                    spawner.started_at, background.get("ended_at"), status)
        self.graph.lanes.append(lane)
        task = self.node(Node(f"bg:{call.tool_use_id}", lane.id, "background_task", spawner.started_at,
                              background.get("ended_at"), lane.label, status, spawner.approximate, list(spawner.step_ids)))
        self.link([spawner.id], task.id, "spawn")
        if background.get("notification_step_id") is not None:
            self.link([task.id], str(background["notification_step_id"]), "return")

    def child_agent(self, parent: Lane, spawner: Node, call: ToolCall) -> None:
        background = call.background
        data = call.input if isinstance(call.input, dict) else {}
        label = _first_line(data.get("description") or data.get("subagent_type") or "서브에이전트")
        if background is not None:
            lane = Lane(call.tool_use_id, "background_agent", label, parent.id, spawner.id, spawner.started_at,
                        background.get("ended_at"), self.background_status(call))
        else:
            lane = Lane(call.tool_use_id, "subagent", label, parent.id, spawner.id, spawner.started_at, call.ended_at, call.status)
        self.graph.lanes.append(lane)
        entry, frontier = self.lane(lane, call.subagent or [], [])
        for head in entry:
            self.link([spawner.id], head, "spawn")
        if background is None:
            self.link(frontier, spawner.id, "return")
        elif background.get("notification_step_id") is not None:
            self.link(frontier, str(background["notification_step_id"]), "return")

    def child_unlinked(self, parent: Lane, step: Step) -> None:
        agent_id = step.detail.get("agent_id")
        substeps = step.substeps or []
        status = "running" if self.turn.state == "running" else "unfinished"
        lane = Lane(f"agent:{agent_id}", "subagent", f"서브에이전트 {agent_id}", parent.id, None,
                    step.at, substeps[-1].at if substeps else None, status)
        self.graph.lanes.append(lane)
        self.lane(lane, substeps, [])


def build_turn_graph(session: SessionView, index: int) -> FlowGraph | None:
    """Compute the flow graph of the turn with the given 1-based index.

    @doc: docs/design/FlowGraph.md#3-그래프-모델
    """
    turn = next((turn for turn in session.turns if turn.index == index), None)
    if turn is None:
        return None
    graph = FlowGraph(session.session_id, index, turn.started_at, turn.ended_at)
    builder = _GraphBuilder(graph, turn, session.ended)
    main = Lane("main", "main", "주 에이전트", None, None, turn.started_at, turn.ended_at, turn.state)
    graph.lanes.append(main)
    prompt = builder.node(Node("prompt", main.id, "prompt", turn.started_at, turn.started_at, _first_line(turn.prompt)))
    builder.lane(main, turn.steps, [prompt.id])
    ids = {node.id for node in graph.nodes}
    edges, seen = [], set()
    for edge in graph.edges:
        key = (edge.source, edge.target, edge.kind)
        if edge.source in ids and edge.target in ids and key not in seen:
            seen.add(key)
            edges.append(edge)
    graph.edges = edges
    graph.nodes.sort(key=lambda node: node.started_at)
    if turn.state != "running":
        # Work resumed after Stop by a background task notification stays in this turn.
        main_times = [time for node in graph.nodes if node.lane == main.id for time in (node.started_at, node.ended_at) if time]
        main.ended_at = max([*main_times, *([turn.ended_at] if turn.ended_at else [])])
    else:
        main.ended_at = None
    graph.ended_at = main.ended_at
    graph.lanes = [main] + sorted(graph.lanes[1:], key=lambda lane: lane.started_at or turn.started_at)
    return graph
