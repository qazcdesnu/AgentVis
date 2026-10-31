"""Tests for building session views from raw events.

@doc: docs/design/Analysis.md#9-테스트
"""

import json
import unittest
from dataclasses import replace
from datetime import UTC, datetime, timedelta

from agentvis.analysis.session import SessionView, build_session
from agentvis.collector import hook_event_to_raw
from agentvis.store import RawEvent
from agentvis.transcript import record_to_raw

_START = datetime(2026, 10, 31, 1, 0, tzinfo=UTC)


class _Session:
    """Builds a list of raw events through the real conversion paths."""

    def __init__(self) -> None:
        self.events: list[RawEvent] = []
        self.clock = 0

    def _at(self) -> datetime:
        self.clock += 1
        return _START + timedelta(seconds=self.clock)

    def record(self, **fields: object) -> None:
        at = self._at()
        line = json.dumps({"sessionId": "s1", "cwd": "/Users/me/app", "timestamp": at.isoformat(), **fields}, ensure_ascii=False)
        event = record_to_raw(line.encode())
        assert event is not None, fields
        self.events.append(replace(event, id=len(self.events) + 1))

    def hook(self, name: str, **fields: object) -> None:
        body = json.dumps({"session_id": "s1", "hook_event_name": name, "cwd": "/Users/me/app/sub", **fields}, ensure_ascii=False)
        self.events.append(replace(hook_event_to_raw(body.encode(), self._at()), id=len(self.events) + 1))

    def prompt(self, uuid: str, prompt_id: str, text: str, parent: str | None = None) -> None:
        self.record(type="user", uuid=uuid, parentUuid=parent, promptId=prompt_id, origin={"kind": "human"},
                    promptSource="typed", message={"role": "user", "content": text})

    def assistant(self, uuid: str, parent: str, block: dict, **extra: object) -> None:
        self.record(type="assistant", uuid=uuid, parentUuid=parent, message={"content": [block]}, **extra)

    def result(self, uuid: str, parent: str, prompt_id: str, tool_use_id: str, content: str, is_error: bool = False, tool_use_result: object = None) -> None:
        self.record(type="user", uuid=uuid, parentUuid=parent, promptId=prompt_id, toolUseResult=tool_use_result,
                    message={"content": [{"type": "tool_result", "tool_use_id": tool_use_id, "content": content, "is_error": is_error}]})

    def build(self) -> SessionView:
        return build_session(self.events)


def _steps(view: SessionView, index: int) -> list[str]:
    return [step.kind for step in view.turns[index].steps]


class TurnTest(unittest.TestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def test_only_human_prompts_start_turns_and_records_follow_parents(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "테스트 고쳐")
        s.assistant("a1", "u1", {"type": "thinking", "thinking": "…"})
        s.assistant("a2", "a1", {"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "pytest"}})
        s.result("u2", "a2", "p1", "toolu_1", "ok")
        s.record(type="user", uuid="m1", parentUuid="u2", isMeta=True, origin={"kind": "peer"}, message={"content": "하위 에이전트 보고"})
        s.record(type="system", uuid="c1", parentUuid=None, subtype="compact_boundary", compactMetadata={"trigger": "auto"})
        s.assistant("a3", "c1", {"type": "text", "text": "끝"})
        s.prompt("u3", "p2", "다음 일", parent="a3")
        view = s.build()
        self.assertEqual([turn.prompt for turn in view.turns], ["테스트 고쳐", "다음 일"])
        self.assertEqual(_steps(view, 0), ["thinking", "tool_call", "notification", "compact", "text"])
        self.assertEqual((view.turns[0].state, view.turns[1].state), ("ended", "running"))
        self.assertEqual(view.title, "테스트 고쳐")

    def test_hook_only_turn_and_stop_failure(self) -> None:
        s = _Session()
        s.hook("UserPromptSubmit", prompt_id="p1", prompt="hook으로만 온 지시")
        s.hook("StopFailure", prompt_id="p1", error="model_not_found")
        s.hook("SessionEnd", reason="other")
        view = s.build()
        self.assertEqual((view.turns[0].prompt, view.turns[0].state, view.ended), ("hook으로만 온 지시", "failed", True))
        self.assertEqual((view.project, view.project_from_hook), ("/Users/me/app/sub", True))


class ToolCallTest(unittest.TestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def test_merges_sources_and_classifies_status(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "작업")
        s.hook("PreToolUse", prompt_id="p1", tool_use_id="toolu_e", tool_name="Bash", tool_input={"command": "ls x"})
        s.assistant("a1", "u1", {"type": "tool_use", "id": "toolu_e", "name": "Bash", "input": {"command": "ls x"}})
        s.result("u2", "a1", "p1", "toolu_e", "Exit code 1", is_error=True)
        s.hook("PostToolUseFailure", prompt_id="p1", tool_use_id="toolu_e", error="Exit code 1", is_interrupt=False, duration_ms=54)
        s.assistant("a2", "u2", {"type": "tool_use", "id": "toolu_i", "name": "Bash", "input": {}})
        s.result("u3", "a2", "p1", "toolu_i", "[Request interrupted by user for tool use]", is_error=True)
        s.assistant("a3", "u3", {"type": "tool_use", "id": "toolu_w", "name": "Write", "input": {"file_path": "x"}})
        s.hook("PreToolUse", prompt_id="p1", tool_use_id="toolu_w", tool_name="Write", tool_input={"file_path": "x"})
        s.hook("PermissionRequest", prompt_id="p1", tool_name="Write", tool_input={"file_path": "x"})
        s.hook("PreToolUse", prompt_id="p1", tool_use_id="toolu_r", tool_name="Bash", tool_input={"command": "sleep 60"})
        running = s.build()
        calls = {step.tool_call.tool_use_id: step.tool_call for step in running.turns[0].steps if step.tool_call}
        self.assertEqual(
            {key: call.status for key, call in calls.items()},
            {"toolu_e": "error", "toolu_i": "interrupted", "toolu_w": "running", "toolu_r": "running"},
        )
        self.assertEqual((calls["toolu_e"].duration_ms, calls["toolu_e"].error), (54, "Exit code 1"))
        self.assertTrue(calls["toolu_w"].permission_requested)
        self.assertEqual(running.turns[0].steps[-1].source, "hook")
        self.assertEqual((running.tool_call_count, running.failure_count), (4, 2))
        s.hook("Stop", prompt_id="p1")
        ended = {step.tool_call.tool_use_id: step.tool_call.status for step in s.build().turns[0].steps if step.tool_call}
        self.assertEqual((ended["toolu_w"], ended["toolu_r"]), ("unfinished", "unfinished"))

    def test_hook_success_without_transcript_result(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "작업")
        s.hook("PreToolUse", prompt_id="p1", tool_use_id="toolu_1", tool_name="Bash", tool_input={})
        s.hook("PostToolUse", prompt_id="p1", tool_use_id="toolu_1", tool_response={"stdout": "ok"}, duration_ms=6)
        call = s.build().turns[0].steps[0].tool_call
        self.assertEqual((call.status, call.duration_ms, call.result), ("success", 6, '{"stdout": "ok"}'))


class MessageTest(unittest.TestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def test_queued_messages_and_hook_failures(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "작업")
        s.assistant("a1", "u1", {"type": "text", "text": "진행"})
        s.record(type="attachment", uuid="t1", parentUuid="a1",
                 attachment={"type": "queued_command", "prompt": "uv로 해", "commandMode": "prompt", "origin": {"kind": "human"}})
        s.record(type="attachment", uuid="t2", parentUuid="t1",
                 attachment={"type": "queued_command", "prompt": "<task-notification>…", "commandMode": "task-notification"})
        s.record(type="attachment", uuid="t3", parentUuid="t2",
                 attachment={"type": "hook_non_blocking_error", "hookEvent": "PreToolUse", "toolUseID": "toolu_1", "stderr": "connect ECONNREFUSED"})
        s.record(type="queue-operation", operation="enqueue", content="uv로 해")
        s.record(type="user", uuid="b1", parentUuid="t3", message={"content": "<bash-input>gh auth login</bash-input>"})
        view = s.build()
        steps = view.turns[0].steps
        self.assertEqual([step.kind for step in steps], ["text", "user_message", "notification", "hook_failure", "notification"])
        self.assertEqual(steps[4].detail, {"source": "user_shell"})
        self.assertEqual((steps[1].text, steps[2].detail, steps[3].detail["hook_event"]), ("uv로 해", {"source": "task-notification"}, "PreToolUse"))


class SubagentAndProjectTest(unittest.TestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def test_subagent_links_by_agent_id_and_unlinked_ones_get_a_step(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "리뷰해")
        s.assistant("a1", "u1", {"type": "tool_use", "id": "toolu_ag", "name": "Agent", "input": {"description": "리뷰"}})
        for agent in ("ag1", "ag2"):
            s.record(type="user", uuid=f"{agent}-u", parentUuid=None, promptId="p1", isSidechain=True, agentId=agent, message={"content": "일"})
            s.record(type="user", uuid=f"{agent}-m", parentUuid=f"{agent}-u", promptId="p1", isSidechain=True, agentId=agent,
                     isMeta=True, message={"content": "<system-reminder>…</system-reminder>"})
            s.record(type="assistant", uuid=f"{agent}-a", parentUuid=f"{agent}-u", isSidechain=True, agentId=agent,
                     message={"content": [{"type": "tool_use", "id": f"toolu_{agent}", "name": "Read", "input": {}}]}, )
        s.result("u2", "a1", "p1", "toolu_ag", "보고", tool_use_result={"agentId": "ag1", "status": "completed"})
        view = s.build()
        steps = view.turns[0].steps
        agent_call = steps[0].tool_call
        self.assertEqual((agent_call.agent_id, [step.kind for step in agent_call.subagent]), ("ag1", ["tool_call"]))
        # A subagent call without a result follows the parent turn, which is still running.
        self.assertEqual(agent_call.subagent[0].tool_call.status, "running")
        self.assertEqual((steps[-1].kind, steps[-1].detail, len(steps[-1].substeps)), ("subagent", {"agent_id": "ag2"}, 1))
        self.assertEqual(view.tool_call_count, 1)

    def test_project_is_first_transcript_cwd_not_hook_subfolder(self) -> None:
        s = _Session()
        s.hook("PreToolUse", prompt_id="p1", tool_use_id="toolu_1", tool_name="Bash", tool_input={})
        s.prompt("u1", "p1", "작업")
        view = s.build()
        self.assertEqual((view.project, view.project_from_hook), ("/Users/me/app", False))
        self.assertEqual(build_session([]).turns, [])


class GraphFieldTest(unittest.TestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def test_message_id_spans_and_background_link(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "테스트 돌려")
        s.assistant("a1", "u1", {"type": "tool_use", "id": "toolu_bg", "name": "Bash", "input": {"command": "pytest", "run_in_background": True}})
        s.result("r1", "a1", "p1", "toolu_bg", "running", tool_use_result={"backgroundTaskId": "b1"})
        s.hook("PreToolUse", prompt_id="p1", tool_use_id="toolu_bg", tool_name="Bash", tool_input={})
        s.record(type="attachment", uuid="n1", parentUuid="r1", attachment={"type": "queued_command", "commandMode": "task-notification",
                 "prompt": "<task-notification>\n<task-id>b1</task-id>\n<tool-use-id>toolu_bg</tool-use-id>\n<status>completed</status>\n</task-notification>"})
        steps = s.build().turns[0].steps
        call, note = steps[0].tool_call, steps[1]
        self.assertEqual(note.detail, {"source": "task-notification", "task_id": "b1", "tool_use_id": "toolu_bg", "status": "completed"})
        self.assertEqual(call.background, {"kind": "shell", "task_id": "b1", "status": "completed", "ended_at": note.at, "notification_step_id": note.id})
        # The start came from the hook but the end only from the transcript result.
        self.assertEqual((call.started_at, call.approximate), (s.events[3].occurred_at, True))
        self.assertIsNone(steps[0].message_id)

    def test_subagent_hooks_join_the_subagent_not_the_parent_turn(self) -> None:
        s = _Session()
        s.prompt("u1", "p1", "리뷰해")
        s.assistant("a1", "u1", {"type": "tool_use", "id": "toolu_ag", "name": "Agent", "input": {}}, )
        s.record(type="user", uuid="g-u", parentUuid=None, promptId="p1", isSidechain=True, agentId="ag1", message={"content": "일"})
        s.record(type="assistant", uuid="g-a", parentUuid="g-u", isSidechain=True, agentId="ag1",
                 message={"id": "msg_g", "content": [{"type": "tool_use", "id": "toolu_r", "name": "Read", "input": {}}]})
        s.hook("PreToolUse", prompt_id="p1", agent_id="ag1", tool_use_id="toolu_r", tool_name="Read", tool_input={})
        s.hook("PostToolUse", prompt_id="p1", agent_id="ag1", tool_use_id="toolu_r", tool_name="Read", duration_ms=12, tool_response="x")
        s.hook("PreToolUse", prompt_id="p1", agent_id="ag-unknown", tool_use_id="toolu_x", tool_name="Read", tool_input={})
        s.result("r1", "a1", "p1", "toolu_ag", "보고", tool_use_result={"agentId": "ag1"})
        view = s.build()
        steps = view.turns[0].steps
        self.assertEqual([step.kind for step in steps], ["tool_call"])
        inner = steps[0].tool_call.subagent[0]
        self.assertEqual((inner.message_id, inner.tool_call.status, inner.tool_call.duration_ms, inner.tool_call.approximate), ("msg_g", "success", 12, False))
        self.assertEqual(view.tool_call_count, 1)

