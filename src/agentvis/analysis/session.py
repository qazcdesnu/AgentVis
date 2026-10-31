"""Build session, turn, step and tool call views from one session's raw events.

@doc: docs/design/Analysis.md
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime

from agentvis.store import RawEvent

# @doc: docs/design/Analysis.md#5-도구-호출
RESULT_PREVIEW_CHARS = 2000
_TITLE_CHARS = 80
_INTERRUPT_MARK = "[Request interrupted by user"
_SHELL_MARKS = ("<bash-input>", "<bash-stdout>", "<bash-stderr>")
_AGENT_TOOLS = ("Agent", "Task")
_NOTIFICATION_TAGS = {"task_id": "task-id", "tool_use_id": "tool-use-id", "status": "status"}


@dataclass
class ToolCall:
    """One tool call merged from its transcript records and hook events.

    @doc: docs/design/Analysis.md#5-도구-호출
    """

    tool_use_id: str
    tool_name: str | None
    input: object
    status: str = "running"
    result: str | None = None
    error: str | None = None
    duration_ms: int | None = None
    permission_requested: bool = False
    subagent: list["Step"] | None = None
    is_error: bool | None = None
    interrupted: bool = False
    agent_id: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    approximate: bool = False
    background: dict | None = None


@dataclass
class Step:
    """One time-ordered item inside a turn.

    @doc: docs/design/Analysis.md#4-단계
    """

    id: int
    kind: str
    at: datetime
    source: str
    text: str | None = None
    tool_call: ToolCall | None = None
    detail: dict = field(default_factory=dict)
    substeps: list["Step"] | None = None
    message_id: str | None = None


@dataclass
class Turn:
    """One instruction a person typed and the work done for it.

    @doc: docs/design/Analysis.md#3-턴
    """

    prompt_id: str
    prompt: str
    started_at: datetime
    index: int = 0
    ended_at: datetime | None = None
    state: str = "running"
    steps: list[Step] = field(default_factory=list)
    tool_call_count: int = 0
    failure_count: int = 0


@dataclass
class SessionView:
    """One session with its project, summary counts and turns.

    @doc: docs/design/Analysis.md#7-세션
    """

    session_id: str
    project: str | None
    project_from_hook: bool
    title: str
    started_at: datetime | None
    last_activity: datetime | None
    ended: bool
    turn_count: int
    tool_call_count: int
    failure_count: int
    turns: list[Turn]
    preamble: list[Step]


def _content_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
                elif block.get("type") == "image":
                    parts.append("[image]")
        return "\n".join(parts)
    return ""


def _preview(text: str | None) -> str | None:
    return None if text is None else text[:RESULT_PREVIEW_CHARS]


def _block(record: dict) -> dict:
    content = (record.get("message") or {}).get("content")
    return content[0] if isinstance(content, list) and content and isinstance(content[0], dict) else {}


def _background(kind: str, task_id: str | None = None) -> dict:
    return {"kind": kind, "task_id": task_id, "status": None, "ended_at": None, "notification_step_id": None}


def _notification_detail(text: str) -> dict:
    detail = {}
    for key, tag in _NOTIFICATION_TAGS.items():
        match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
        if match:
            detail[key] = match.group(1).strip()
    return detail


def _is_human_prompt(record: dict) -> bool:
    if record.get("type") != "user" or record.get("isMeta"):
        return False
    origin = record.get("origin")
    return isinstance(origin, dict) and origin.get("kind") == "human" and _block(record).get("type") != "tool_result"


class _Builder:
    """Accumulates turns and tool calls for one session or one subagent."""

    def __init__(self) -> None:
        self.turns: dict[str, Turn] = {}
        self.preamble: list[Step] = []
        self.tool_calls: dict[str, ToolCall] = {}
        self.uuid_turn: dict[str, str] = {}

    def turn_of(self, record: dict, at: datetime) -> str | None:
        prompt_id = record.get("promptId")
        if isinstance(prompt_id, str) and prompt_id in self.turns:
            return prompt_id
        # A new parent chain (e.g. after compaction) falls back to the turn running at that time.
        return self.uuid_turn.get(record.get("parentUuid")) or self.latest_turn(at)

    def latest_turn(self, at: datetime) -> str | None:
        earlier = [turn for turn in self.turns.values() if turn.started_at <= at]
        return max(earlier, key=lambda turn: turn.started_at).prompt_id if earlier else None

    def add_step(self, turn_id: str | None, step: Step) -> None:
        (self.turns[turn_id].steps if turn_id in self.turns else self.preamble).append(step)

    def add_record(self, event: RawEvent, record: dict) -> None:
        if _is_human_prompt(record) and isinstance(record.get("promptId"), str):
            prompt_id = record["promptId"]
            self.turns.setdefault(prompt_id, Turn(prompt_id, _content_text(record["message"].get("content")), event.occurred_at))
        turn_id = self.turn_of(record, event.occurred_at)
        if isinstance(record.get("uuid"), str) and turn_id is not None:
            self.uuid_turn[record["uuid"]] = turn_id
        step = self._record_step(event, record)
        if step is not None:
            self.add_step(turn_id, step)

    def _record_step(self, event: RawEvent, record: dict) -> Step | None:
        kind = record.get("type")
        if kind == "assistant":
            message_id = (record.get("message") or {}).get("id")
            step = self._assistant_step(event, _block(record))
            if step is not None and isinstance(message_id, str):
                step.message_id = message_id
            return step
        if kind == "user":
            return self._user_step(event, record)
        if kind == "attachment":
            return self._attachment_step(event, record.get("attachment") or {})
        if kind == "system" and record.get("subtype") == "compact_boundary":
            return Step(event.id, "compact", event.occurred_at, "transcript", detail={"trigger": (record.get("compactMetadata") or {}).get("trigger")})
        return None

    def _assistant_step(self, event: RawEvent, block: dict) -> Step | None:
        block_type = block.get("type")
        if block_type == "thinking":
            return Step(event.id, "thinking", event.occurred_at, "transcript", text=block.get("thinking"))
        if block_type == "text":
            return Step(event.id, "text", event.occurred_at, "transcript", text=block.get("text"))
        if block_type == "tool_use" and isinstance(block.get("id"), str):
            call = self.tool_calls.setdefault(block["id"], ToolCall(block["id"], block.get("name"), block.get("input")))
            call.tool_name, call.input = block.get("name"), block.get("input")
            call.started_at = call.started_at or event.occurred_at
            if isinstance(call.input, dict) and call.input.get("run_in_background") and call.background is None:
                call.background = _background("agent" if call.tool_name in _AGENT_TOOLS else "shell")
            return Step(event.id, "tool_call", event.occurred_at, "transcript", tool_call=call)
        return None

    def _user_step(self, event: RawEvent, record: dict) -> Step | None:
        block = _block(record)
        if block.get("type") == "tool_result":
            call = self.tool_calls.get(block.get("tool_use_id"))
            if call is not None:
                result = record.get("toolUseResult")
                call.result = _preview(_content_text(block.get("content")))
                call.is_error = bool(block.get("is_error"))
                call.interrupted = call.interrupted or (isinstance(result, dict) and bool(result.get("interrupted")))
                call.ended_at = event.occurred_at
                if isinstance(result, dict) and isinstance(result.get("agentId"), str):
                    call.agent_id = result["agentId"]
                    if result.get("isAsync"):
                        call.background = call.background or _background("agent")
                        call.background["task_id"] = result["agentId"]
                if isinstance(result, dict) and isinstance(result.get("backgroundTaskId"), str):
                    call.background = call.background or _background("shell")
                    call.background["task_id"] = result["backgroundTaskId"]
                if call.is_error and call.error is None:
                    call.error = call.result
            return None
        if _is_human_prompt(record):
            return None
        origin = record.get("origin") if isinstance(record.get("origin"), dict) else {}
        if record.get("isMeta") and not origin:
            # Harness-injected context such as <system-reminder>, not part of the work.
            return None
        text = _content_text((record.get("message") or {}).get("content"))
        source = "user_shell" if text.startswith(_SHELL_MARKS) else origin.get("kind") or "meta"
        return Step(event.id, "notification", event.occurred_at, "transcript", text=text, detail={"source": source})

    def _attachment_step(self, event: RawEvent, attachment: dict) -> Step | None:
        if attachment.get("type") == "queued_command":
            origin = attachment.get("origin") if isinstance(attachment.get("origin"), dict) else {}
            if origin.get("kind") == "human" and attachment.get("commandMode") == "prompt":
                return Step(event.id, "user_message", event.occurred_at, "transcript", text=attachment.get("prompt"))
            source = attachment.get("commandMode") or origin.get("kind")
            detail = {"source": source}
            if source == "task-notification":
                detail.update(_notification_detail(str(attachment.get("prompt") or "")))
            return Step(event.id, "notification", event.occurred_at, "transcript", text=attachment.get("prompt"), detail=detail)
        if attachment.get("type") == "hook_non_blocking_error":
            detail = {"hook_event": attachment.get("hookEvent"), "message": attachment.get("stderr")}
            return Step(event.id, "hook_failure", event.occurred_at, "transcript", detail=detail)
        return None


def _hook_turn(builder: _Builder, payload: dict, at: datetime) -> str | None:
    prompt_id = payload.get("prompt_id")
    if isinstance(prompt_id, str) and prompt_id in builder.turns:
        return prompt_id
    return builder.latest_turn(at)


def _apply_hooks(
    builder: _Builder, hooks: list[tuple[RawEvent, dict]], subagents: dict[str, _Builder], hooked: set[tuple[str, str]]
) -> tuple[bool, set[str], set[str]]:
    ended = False
    stopped: set[str] = set()
    failed: set[str] = set()
    for event, payload in hooks:
        kind = event.kind
        if kind == "UserPromptSubmit" and isinstance(payload.get("prompt_id"), str):
            builder.turns.setdefault(payload["prompt_id"], Turn(payload["prompt_id"], str(payload.get("prompt", "")), event.occurred_at))
            continue
        turn_id = _hook_turn(builder, payload, event.occurred_at)
        tool_use_id = payload.get("tool_use_id")
        if kind in ("PreToolUse", "PostToolUse", "PostToolUseFailure", "PermissionRequest"):
            agent_id = payload.get("agent_id")
            # Hooks fired inside a subagent belong to that subagent's tool calls, not the parent turn (H3).
            target = subagents.get(agent_id) if isinstance(agent_id, str) and agent_id else builder
            if target is None:
                continue
            steps = target.preamble if target is not builder else builder.turns[turn_id].steps if turn_id in builder.turns else builder.preamble
            _apply_tool_hook(target, steps, turn_id if target is builder else None, event, payload, hooked)
        elif kind == "Stop" and turn_id is not None:
            stopped.add(turn_id)
            builder.turns[turn_id].ended_at = event.occurred_at
        elif kind == "StopFailure" and turn_id is not None:
            failed.add(turn_id)
            builder.turns[turn_id].ended_at = event.occurred_at
        elif kind == "PostCompact" and not any(step.kind == "compact" for step in builder.turns.get(turn_id, Turn("", "", event.occurred_at)).steps):
            builder.add_step(turn_id, Step(event.id, "compact", event.occurred_at, "hook", detail={"trigger": payload.get("trigger")}))
        elif kind == "SessionEnd":
            ended = True
    return ended, stopped, failed


def _apply_tool_hook(
    target: _Builder, steps: list[Step], turn_id: str | None, event: RawEvent, payload: dict, hooked: set[tuple[str, str]]
) -> None:
    kind, tool_use_id = event.kind, payload.get("tool_use_id")
    if kind == "PreToolUse" and isinstance(tool_use_id, str):
        if tool_use_id not in target.tool_calls:
            call = ToolCall(tool_use_id, payload.get("tool_name"), payload.get("tool_input"))
            target.tool_calls[tool_use_id] = call
            target.add_step(turn_id, Step(event.id, "tool_call", event.occurred_at, "hook", tool_call=call))
        target.tool_calls[tool_use_id].started_at = event.occurred_at
        hooked.add((tool_use_id, "start"))
    elif kind in ("PostToolUse", "PostToolUseFailure") and tool_use_id in target.tool_calls:
        call = target.tool_calls[tool_use_id]
        call.ended_at = event.occurred_at
        hooked.add((tool_use_id, "end"))
        if isinstance(payload.get("duration_ms"), int):
            call.duration_ms = payload["duration_ms"]
        if kind == "PostToolUseFailure":
            call.interrupted = call.interrupted or bool(payload.get("is_interrupt"))
            call.error = call.error or payload.get("error")
            if call.is_error is None:
                call.is_error = True
        elif call.is_error is None:
            call.is_error = False
            response = payload.get("tool_response")
            call.result = _preview(response if isinstance(response, str) else json.dumps(response, ensure_ascii=False))
    elif kind == "PermissionRequest":
        for step in reversed(steps):
            call = step.tool_call
            if call and call.tool_name == payload.get("tool_name") and call.input == payload.get("tool_input") and call.is_error is None:
                call.permission_requested = True
                break


def _finish_turns(builder: _Builder, ended: bool, stopped: set[str], failed: set[str]) -> list[Turn]:
    turns = sorted(builder.turns.values(), key=lambda turn: turn.started_at)
    for index, turn in enumerate(turns, start=1):
        turn.index = index
        turn.steps.sort(key=lambda step: (step.at, step.id))
        if turn.prompt_id in failed:
            turn.state = "failed"
        elif turn.prompt_id in stopped or ended or index < len(turns):
            turn.state = "ended"
        if turn.ended_at is None and turn.state != "running" and turn.steps:
            turn.ended_at = turn.steps[-1].at
        calls = [step.tool_call for step in turn.steps if step.tool_call is not None]
        for call in calls:
            call.status = _status(call, turn.state)
        turn.tool_call_count = len(calls)
        turn.failure_count = sum(call.status in ("error", "interrupted") for call in calls)
    return turns


def _status(call: ToolCall, turn_state: str) -> str:
    if call.interrupted or (call.result and _INTERRUPT_MARK in call.result):
        return "interrupted"
    if call.is_error is True:
        return "error"
    if call.is_error is False:
        return "success"
    return "running" if turn_state == "running" else "unfinished"


def _subagent_builder(records: list[tuple[RawEvent, dict]]) -> _Builder:
    # A subagent has no turns of its own, so its steps collect in the builder's preamble.
    builder = _Builder()
    # The first record is the instruction the parent delegated; the spawning tool call already shows it.
    if records and records[0][1].get("type") == "user":
        records = records[1:]
    for event, record in records:
        step = builder._record_step(event, record)
        if step is not None:
            builder.preamble.append(step)
    return builder


def _all_steps(steps: list[Step]) -> list[Step]:
    found = []
    for step in steps:
        found.append(step)
        if step.substeps:
            found.extend(_all_steps(step.substeps))
        if step.tool_call is not None and step.tool_call.subagent:
            found.extend(_all_steps(step.tool_call.subagent))
    return found


def _link_background(calls: dict[str, ToolCall], steps: list[Step]) -> None:
    for step in steps:
        call = calls.get(step.detail.get("tool_use_id")) if step.kind == "notification" else None
        if call is None:
            continue
        call.background = call.background or _background("agent" if call.tool_name in _AGENT_TOOLS else "shell")
        if call.background["notification_step_id"] is None:
            call.background.update(status=step.detail.get("status"), ended_at=step.at, notification_step_id=step.id)


def build_session(events: list[RawEvent]) -> SessionView:
    """Compute the session view of one session's raw events.

    @doc: docs/design/Analysis.md#1-계산-방식
    """
    main: list[tuple[RawEvent, dict]] = []
    sidechains: dict[str, list[tuple[RawEvent, dict]]] = {}
    hooks: list[tuple[RawEvent, dict]] = []
    for event in events:
        try:
            payload = json.loads(event.payload)
        except ValueError:
            continue
        if not isinstance(payload, dict) or event.kind == "subagent-meta":
            continue
        if event.source == "hook":
            hooks.append((event, payload))
        elif payload.get("isSidechain") and isinstance(payload.get("agentId"), str):
            sidechains.setdefault(payload["agentId"], []).append((event, payload))
        else:
            main.append((event, payload))
    builder = _Builder()
    for event, record in main:
        builder.add_record(event, record)
    subagents = {agent_id: _subagent_builder(records) for agent_id, records in sidechains.items()}
    hooked: set[tuple[str, str]] = set()
    ended, stopped, failed = _apply_hooks(builder, sorted(hooks, key=lambda item: (item[0].occurred_at, item[0].id)), subagents, hooked)
    calls = dict(builder.tool_calls)
    for sub in subagents.values():
        calls.update(sub.tool_calls)
    by_agent = {call.agent_id: call for call in calls.values() if call.agent_id}
    for agent_id, sub in subagents.items():
        steps = sorted(sub.preamble, key=lambda step: (step.at, step.id))
        if agent_id in by_agent:
            by_agent[agent_id].subagent = steps
        elif steps:
            first_event, first = sidechains[agent_id][0]
            step = Step(first_event.id, "subagent", first_event.occurred_at, "transcript", detail={"agent_id": agent_id}, substeps=steps)
            builder.add_step(first.get("promptId") if first.get("promptId") in builder.turns else None, step)
    turns = _finish_turns(builder, ended, stopped, failed)
    for agent_id, sub in subagents.items():
        parent_turn = builder.turns.get(sidechains[agent_id][0][1].get("promptId"))
        for call in sub.tool_calls.values():
            call.status = _status(call, parent_turn.state if parent_turn else "ended")
    for call in calls.values():
        has_end = call.ended_at is not None
        call.approximate = (call.tool_use_id, "start") not in hooked or (has_end and (call.tool_use_id, "end") not in hooked)
    _link_background(calls, _all_steps([step for turn in turns for step in turn.steps] + builder.preamble))
    project = next((record.get("cwd") for _, record in main if isinstance(record.get("cwd"), str)), None)
    from_hook = project is None
    if from_hook:
        project = next((payload.get("cwd") for _, payload in hooks if isinstance(payload.get("cwd"), str)), None)
    times = [event.occurred_at for event in events]
    first_prompt = turns[0].prompt.strip().splitlines()[0] if turns and turns[0].prompt.strip() else ""
    return SessionView(
        session_id=events[0].session_id if events else "",
        project=project,
        project_from_hook=from_hook and project is not None,
        title=first_prompt[:_TITLE_CHARS],
        started_at=min(times) if times else None,
        last_activity=max(times) if times else None,
        ended=ended,
        turn_count=len(turns),
        tool_call_count=sum(turn.tool_call_count for turn in turns),
        failure_count=sum(turn.failure_count for turn in turns),
        turns=turns,
        preamble=sorted(builder.preamble, key=lambda step: (step.at, step.id)),
    )
