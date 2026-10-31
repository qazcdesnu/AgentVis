"""Tests for building the flow graph of a turn.

@doc: docs/design/FlowGraph.md#8-테스트
"""

import unittest

from agentvis.analysis.graph import FlowGraph, build_turn_graph
from tests.test_analysis import _Session

_NOTE = "<task-notification>\n<task-id>{task}</task-id>\n<tool-use-id>{tool}</tool-use-id>\n<status>{status}</status>\n</task-notification>"


def _say(s: _Session, uuid: str, parent: str, message_id: str, block: dict, **extra: object) -> None:
    s.record(type="assistant", uuid=uuid, parentUuid=parent, message={"id": message_id, "content": [block]}, **extra)


def _tool(name: str, tool_id: str, **data: object) -> dict:
    return {"type": "tool_use", "id": tool_id, "name": name, "input": data}


def _notify(s: _Session, uuid: str, parent: str, task: str, tool: str, status: str = "completed") -> None:
    s.record(type="attachment", uuid=uuid, parentUuid=parent,
             attachment={"type": "queued_command", "commandMode": "task-notification", "prompt": _NOTE.format(task=task, tool=tool, status=status)})


def _graph(s: _Session, index: int = 1) -> FlowGraph:
    graph = build_turn_graph(s.build(), index)
    assert graph is not None
    return graph


def _edges(graph: FlowGraph, kind: str = "next") -> set[tuple[str, str]]:
    return {(edge.source, edge.target) for edge in graph.edges if edge.kind == kind}


def _node(graph: FlowGraph, kind: str, index: int = 0):
    return [node for node in graph.nodes if node.kind == kind][index]


class ParallelTest(unittest.TestCase):
    """@doc: docs/design/FlowGraph.md#8-테스트"""

    def test_parallel_calls_fan_out_from_the_model_node_and_join_at_the_next_response(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "읽어")
        _say(s, "a1", "u1", "m1", {"type": "thinking", "thinking": "둘 다 읽자"})
        _say(s, "a2", "a1", "m1", _tool("Read", "t1", file_path="a.py"))
        _say(s, "a3", "a2", "m1", _tool("Read", "t2", file_path="b.py"))
        s.hook("PreToolUse", prompt_id="p1", tool_use_id="t1", tool_name="Read", tool_input={"file_path": "a.py"})
        s.hook("PreToolUse", prompt_id="p1", tool_use_id="t2", tool_name="Read", tool_input={"file_path": "b.py"})
        s.hook("PostToolUse", prompt_id="p1", tool_use_id="t2", tool_name="Read", tool_response="b")
        s.hook("PostToolUse", prompt_id="p1", tool_use_id="t1", tool_name="Read", tool_response="a")
        s.result("r1", "a2", "p1", "t1", "a")
        s.result("r2", "a3", "p1", "t2", "b")
        _say(s, "a4", "r2", "m2", {"type": "text", "text": "다 읽었다"})
        graph = _graph(s)
        model, tool1, tool2, answer = (_node(graph, "model"), _node(graph, "tool_call"), _node(graph, "tool_call", 1), _node(graph, "model", 1))
        self.assertEqual((model.label, tool1.label, answer.label), ("생각", "Read a.py", "다 읽었다"))
        self.assertEqual(_edges(graph), {("prompt", model.id), (model.id, tool1.id), (model.id, tool2.id), (tool1.id, answer.id), (tool2.id, answer.id)})
        # Execution spans come from the hooks, so the two reads overlap.
        self.assertLess(tool2.started_at, tool1.ended_at)
        self.assertFalse(tool1.approximate)
        self.assertEqual([lane.id for lane in graph.lanes], ["main"])

    def test_response_without_thinking_or_text_has_no_model_node(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "실행")
        _say(s, "a1", "u1", "m1", _tool("Bash", "t1", command="ls"))
        _say(s, "a2", "a1", "m1", _tool("Bash", "t2", command="pwd"))
        graph = _graph(s)
        self.assertEqual([node.kind for node in graph.nodes], ["prompt", "tool_call", "tool_call"])
        self.assertEqual(_edges(graph), {("prompt", graph.nodes[1].id), ("prompt", graph.nodes[2].id)})
        # Without hooks the span starts at the record time, which is only an approximation.
        self.assertTrue(graph.nodes[1].approximate)

    def test_user_message_joins_the_frontier(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "고쳐")
        _say(s, "a1", "u1", "m1", _tool("Edit", "t1", file_path="a.py"))
        s.result("r1", "a1", "p1", "t1", "ok")
        s.record(type="attachment", uuid="q1", parentUuid="r1",
                 attachment={"type": "queued_command", "commandMode": "prompt", "origin": {"kind": "human"}, "prompt": "uv로 해"})
        _say(s, "a2", "q1", "m2", {"type": "text", "text": "알겠다"})
        graph = _graph(s)
        tool, message, answer = graph.nodes[1], graph.nodes[2], graph.nodes[3]
        self.assertEqual((message.kind, message.label), ("user_message", "uv로 해"))
        self.assertEqual(_edges(graph), {("prompt", tool.id), (tool.id, message.id), (message.id, answer.id)})

    def test_missing_turn_has_no_graph(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "작업")
        self.assertIsNone(build_turn_graph(s.build(), 2))


class LaneTest(unittest.TestCase):
    """@doc: docs/design/FlowGraph.md#8-테스트"""

    def _subagent(self, s: _Session, agent: str, prompt_id: str, tool_id: str, block: dict | None = None) -> None:
        s.record(type="user", uuid=f"{agent}-u", parentUuid=None, promptId=prompt_id, isSidechain=True, agentId=agent, message={"content": "일"})
        s.record(type="assistant", uuid=f"{agent}-a", parentUuid=f"{agent}-u", promptId=prompt_id, isSidechain=True, agentId=agent,
                 message={"id": f"{agent}-m", "content": [block or _tool("Read", tool_id, file_path="x.py")]})

    def test_foreground_subagent_lane_spawns_and_returns(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "리뷰해")
        _say(s, "a1", "u1", "m1", _tool("Agent", "toolu_ag", description="문서 리뷰"))
        self._subagent(s, "ag1", "p1", "toolu_r")
        s.hook("PreToolUse", prompt_id="p1", agent_id="ag1", tool_use_id="toolu_r", tool_name="Read", tool_input={"file_path": "x.py"})
        s.hook("PostToolUse", prompt_id="p1", agent_id="ag1", tool_use_id="toolu_r", tool_name="Read", tool_response="x")
        s.result("r1", "a1", "p1", "toolu_ag", "보고", tool_use_result={"agentId": "ag1", "status": "completed"})
        graph = _graph(s)
        lane = graph.lanes[1]
        spawner = _node(graph, "tool_call")
        self.assertEqual((lane.id, lane.kind, lane.label, lane.parent, lane.spawned_by, lane.status), ("toolu_ag", "subagent", "문서 리뷰", "main", spawner.id, "success"))
        read = [node for node in graph.nodes if node.lane == "toolu_ag"][0]
        self.assertEqual((read.label, read.status, read.approximate), ("Read x.py", "success", False))
        self.assertEqual(_edges(graph, "spawn"), {(lane.spawned_by, read.id)})
        self.assertEqual(_edges(graph, "return"), {(read.id, lane.spawned_by)})

    def test_nested_subagent_lane_has_the_subagent_as_parent(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "리뷰해")
        _say(s, "a1", "u1", "m1", _tool("Agent", "toolu_ag", description="바깥"))
        self._subagent(s, "ag1", "p1", "toolu_in", _tool("Agent", "toolu_in", description="안쪽"))
        s.record(type="user", uuid="ag1-r", parentUuid="ag1-a", promptId="p1", isSidechain=True, agentId="ag1", toolUseResult={"agentId": "ag2"},
                 message={"content": [{"type": "tool_result", "tool_use_id": "toolu_in", "content": "끝"}]})
        self._subagent(s, "ag2", "p1", "toolu_r")
        s.result("r1", "a1", "p1", "toolu_ag", "보고", tool_use_result={"agentId": "ag1"})
        graph = _graph(s)
        self.assertEqual([(lane.id, lane.parent) for lane in graph.lanes], [("main", None), ("toolu_ag", "main"), ("toolu_in", "toolu_ag")])

    def test_background_shell_lane_ends_at_its_notification(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "테스트 돌려")
        _say(s, "a1", "u1", "m1", _tool("Bash", "toolu_bg", command="uv run pytest", description="테스트", run_in_background=True))
        s.result("r1", "a1", "p1", "toolu_bg", "Command running in background with ID: b1", tool_use_result={"backgroundTaskId": "b1"})
        _say(s, "a2", "r1", "m2", {"type": "text", "text": "기다린다"})
        _notify(s, "n1", "a2", "b1", "toolu_bg", "failed")
        graph = _graph(s)
        lane = graph.lanes[1]
        task = _node(graph, "background_task")
        notification = _node(graph, "notification")
        self.assertEqual((lane.kind, lane.label, lane.status, lane.ended_at), ("background_shell", "Bash 테스트", "error", notification.started_at))
        self.assertEqual((task.id, task.lane, task.ended_at), ("bg:toolu_bg", "toolu_bg", notification.started_at))
        self.assertEqual(_edges(graph, "spawn"), {(lane.spawned_by, task.id)})
        self.assertEqual(_edges(graph, "return"), {(task.id, notification.id)})

    def test_background_without_notification_stays_open_until_the_session_ends(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "서버 띄워")
        _say(s, "a1", "u1", "m1", _tool("Bash", "toolu_bg", command="uv run agentvis serve", run_in_background=True))
        s.result("r1", "a1", "p1", "toolu_bg", "running", tool_use_result={"backgroundTaskId": "b1"})
        s.hook("Stop", prompt_id="p1")
        graph = _graph(s)
        self.assertEqual((graph.lanes[1].status, graph.lanes[1].ended_at, _edges(graph, "return")), ("running", None, set()))
        s.hook("SessionEnd")
        self.assertEqual(_graph(s).lanes[1].status, "unfinished")

    def test_background_agent_lane(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "조사해")
        _say(s, "a1", "u1", "m1", _tool("Agent", "toolu_ag", description="조사", run_in_background=True))
        s.result("r1", "a1", "p1", "toolu_ag", "launched", tool_use_result={"isAsync": True, "status": "async_launched", "agentId": "ag1"})
        self._subagent(s, "ag1", "p1", "toolu_r")
        _notify(s, "n1", "r1", "ag1", "toolu_ag")
        graph = _graph(s)
        lane = graph.lanes[1]
        read = [node for node in graph.nodes if node.lane == lane.id][0]
        notification = _node(graph, "notification")
        self.assertEqual((lane.kind, lane.status, lane.ended_at), ("background_agent", "success", notification.started_at))
        self.assertEqual(_edges(graph, "return"), {(read.id, notification.id)})

    def test_main_lane_extends_past_stop_when_work_resumes(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "작업")
        _say(s, "a1", "u1", "m1", {"type": "text", "text": "끝"})
        s.hook("Stop", prompt_id="p1")
        _say(s, "a2", "a1", "m2", {"type": "text", "text": "알림을 받아 이어서"})
        graph = _graph(s)
        self.assertEqual(graph.ended_at, graph.nodes[-1].started_at)
        self.assertEqual(graph.lanes[0].ended_at, graph.ended_at)


if __name__ == "__main__":
    unittest.main()
