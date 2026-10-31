"""Build the execution flow graph of one turn from a session view.

@doc: docs/design/FlowGraph.md
"""

from dataclasses import dataclass, field
from datetime import datetime

from agentvis.analysis.session import SessionView, Step, ToolCall, Turn

_LABEL_CHARS = 80
_BACKGROUND_STATUS = {"completed": "success", "failed": "error", "killed": "interrupted"}
_MODEL_KINDS = ("thinking", "text")


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


class _GraphBuilder:
    def __init__(self, graph: FlowGraph, turn: Turn, session_ended: bool) -> None:
        self.graph = graph
        self.turn = turn
        self.session_ended = session_ended

    def node(self, node: Node) -> Node:
        self.graph.nodes.append(node)
        return node

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
            heads, tails = self.stage(lane, stage)
            if not heads:
                continue
            for head in heads:
                self.link(frontier, head)
            if not entry:
                entry = heads
            frontier = tails
        return entry, frontier

    def stage(self, lane: Lane, stage: list[Step]) -> tuple[list[str], list[str]]:
        model_steps = [step for step in stage if step.kind in _MODEL_KINDS]
        tool_steps = [step for step in stage if step.kind == "tool_call" and step.tool_call is not None]
        if not model_steps and not tool_steps:
            point = self.point(lane, stage[0])
            return ([point.id], [point.id]) if point else ([], [])
        tools = [self.tool(lane, step) for step in tool_steps]
        if not model_steps:
            return tools, tools
        text = next((step.text for step in model_steps if step.kind == "text"), None)
        label = _first_line(text) if text is not None else "생각"
        model = self.node(Node(str(model_steps[0].id), lane.id, "model", model_steps[0].at, model_steps[0].at, label,
                               step_ids=[step.id for step in model_steps]))
        for tool in tools:
            self.link([model.id], tool)
        return [model.id], tools or [model.id]

    def point(self, lane: Lane, step: Step) -> Node | None:
        if step.kind == "subagent":
            self.child_unlinked(lane, step)
            return None
        label = {"compact": "문맥 압축", "hook_failure": "hook 전달 실패"}.get(step.kind) or _first_line(step.text)
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
