"""Tests for reading transcript files into the event store.

@doc: docs/design/Transcript.md#6-테스트
"""

import json
import shutil
import threading
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

from agentvis import transcript
from agentvis.store import EventStore
from agentvis.server import create_app
from agentvis.transcript import (
    ReadResult,
    TranscriptReader,
    paths_to_read,
    read_new_records,
    read_subagent_meta,
    record_to_raw,
    subagent_transcript_path,
)
from tests.support import RepoTestCase

_BASE = {"sessionId": "s1", "cwd": "/Users/me/app", "timestamp": "2026-10-31T01:00:00.000Z"}


def _line(**fields: object) -> bytes:
    return json.dumps({**_BASE, **fields}, ensure_ascii=False).encode() + b"\n"


# Shapes observed in real transcripts (docs/DataSource.md, section 3 and 4).
_PROMPT = _line(type="user", uuid="u1", parentUuid=None, promptId="p1", message={"role": "user", "content": "테스트 고쳐"})
_THINKING = _line(type="assistant", uuid="a1", parentUuid="u1", message={"content": [{"type": "thinking", "thinking": "…"}]})
_TOOL_USE = _line(type="assistant", uuid="a2", parentUuid="a1", message={"content": [{"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {}}]})
_TOOL_RESULT = _line(
    type="user", uuid="u2", parentUuid="a2", promptId="p1",
    message={"content": [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "Exit code 1", "is_error": True}]},
    toolUseResult="Error: Exit code 1",
)
_SYSTEM = _line(type="system", subtype="turn_duration", uuid="y1", parentUuid="u2", durationMs=1200)
_QUEUED = json.dumps(
    {"type": "queue-operation", "operation": "enqueue", "content": "uv로 해", "sessionId": "s1", "timestamp": "2026-10-31T01:00:05.000Z"},
    ensure_ascii=False,
).encode() + b"\n"
_QUEUED_COMMAND = _line(
    type="attachment", uuid="t1", parentUuid="a2",
    attachment={"type": "queued_command", "prompt": "uv로 해", "commandMode": "prompt", "origin": {"kind": "human"}},
)
_HOOK_ERROR = _line(
    type="attachment", uuid="t2", parentUuid="a2",
    attachment={"type": "hook_non_blocking_error", "hookEvent": "PreToolUse", "toolUseID": "toolu_1", "stderr": "connect ECONNREFUSED 127.0.0.1:8765"},
)
_IGNORED = [
    _line(type="api-request-blob", hash="h"),
    b"not json\n",
    json.dumps({"type": "user", "sessionId": "s1"}).encode() + b"\n",
    _line(type="attachment", uuid="t3", attachment={"type": "deferred_tools_record"}),
    _line(type="attachment", uuid="t4", attachment="not an object"),
]


class RecordToRawTest(RepoTestCase):
    """@doc: docs/design/Transcript.md#6-테스트"""

    def test_maps_observed_record_shapes(self) -> None:
        prompt = record_to_raw(_PROMPT.strip())
        self.assertEqual((prompt.source, prompt.kind, prompt.session_id, prompt.prompt_id), ("transcript", "user", "s1", "p1"))
        self.assertEqual((prompt.cwd, prompt.dedup_key, prompt.payload), ("/Users/me/app", "uuid:u1", _PROMPT.strip().decode()))
        self.assertEqual(prompt.occurred_at.isoformat(), "2026-10-31T01:00:00+00:00")
        self.assertIsNone(record_to_raw(_THINKING.strip()).prompt_id)
        self.assertEqual(record_to_raw(_TOOL_USE.strip()).tool_use_id, "toolu_1")
        self.assertEqual(record_to_raw(_TOOL_RESULT.strip()).tool_use_id, "toolu_1")
        self.assertEqual(record_to_raw(_SYSTEM.strip()).kind, "system")
        queued = record_to_raw(_QUEUED.strip())
        self.assertEqual((queued.kind, queued.cwd), ("queue-operation", None))
        self.assertTrue(queued.dedup_key.startswith("sha256:"))

    def test_maps_selected_attachments(self) -> None:
        queued = record_to_raw(_QUEUED_COMMAND.strip())
        self.assertEqual((queued.kind, queued.dedup_key, queued.tool_use_id), ("attachment", "uuid:t1", None))
        self.assertEqual(record_to_raw(_HOOK_ERROR.strip()).tool_use_id, "toolu_1")

    def test_skips_other_types_and_unreadable_lines(self) -> None:
        for line in _IGNORED + [b"\xff\xfe", _line(type="user", uuid="u9", timestamp="2026-10-31T01:00:00")]:
            with self.subTest(line=line):
                self.assertIsNone(record_to_raw(line.strip()))


class ReadNewRecordsTest(RepoTestCase):
    """@doc: docs/design/Transcript.md#6-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.projects = self.root / "projects"
        self.path = self.projects / "-Users-me-app" / "s1.jsonl"
        self.path.parent.mkdir(parents=True)
        self.store = EventStore(self.root / "agentvis.db")
        self.addCleanup(self.store.close)

    def append(self, *lines: bytes) -> None:
        with self.path.open("ab") as file:
            file.write(b"".join(lines))

    def read(self) -> ReadResult:
        return read_new_records(self.store, self.path, self.projects)

    def test_reads_only_new_complete_lines(self) -> None:
        self.append(_PROMPT, _THINKING, *_IGNORED)
        first = self.read()
        self.assertEqual((first.stored, first.skipped), (2, 5))
        self.append(_TOOL_USE, _TOOL_RESULT[:-20])
        self.assertEqual(self.read().stored, 1)
        self.append(_TOOL_RESULT[-20:], _SYSTEM, _QUEUED)
        last = self.read()
        self.assertEqual(last.stored, 3)
        self.assertEqual(last.offset, self.path.stat().st_size)
        kinds = [event.kind for event in self.store.events()]
        self.assertEqual(kinds, ["user", "assistant", "assistant", "user", "system", "queue-operation"])
        self.assertEqual(self.read(), ReadResult(0, 0, last.offset))

    def test_replaced_or_truncated_file_is_read_again_without_duplicates(self) -> None:
        self.append(_PROMPT, _THINKING)
        self.read()
        copy = self.root / "copy.jsonl"
        shutil.copyfile(self.path, copy)
        self.path.unlink()
        shutil.copyfile(copy, self.path)
        self.append(_TOOL_USE)
        self.assertEqual(self.read().stored, 1)
        self.path.write_bytes(_PROMPT)
        self.assertEqual(self.read(), ReadResult(0, 0, len(_PROMPT)))
        self.assertEqual(len(self.store.events()), 3)

    def test_batches_advance_the_cursor(self) -> None:
        self.append(_PROMPT, _THINKING, _TOOL_USE, _TOOL_RESULT, _SYSTEM)
        with mock.patch.object(transcript, "BATCH_LINES", 2), mock.patch.object(
            self.store, "append_batch", wraps=self.store.append_batch
        ) as append_batch:
            self.assertEqual(self.read().stored, 5)
        self.assertEqual(append_batch.call_count, 3)
        self.assertEqual(self.store.cursor(str(self.path.resolve())).offset, self.path.stat().st_size)

    def test_paths_outside_the_projects_dir_are_refused_and_missing_files_are_empty(self) -> None:
        outside = self.root / "secret.jsonl"
        outside.write_bytes(_PROMPT)
        with self.assertRaises(ValueError):
            read_new_records(self.store, outside, self.projects)
        with self.assertRaises(ValueError):
            read_new_records(self.store, self.projects / ".." / "secret.jsonl", self.projects)
        self.assertEqual(read_new_records(self.store, self.projects / "x" / "absent.jsonl", self.projects), ReadResult(0, 0, 0))
        self.assertEqual(self.store.events(), [])


class SubagentTest(RepoTestCase):
    """@doc: docs/design/Transcript.md#6-테스트"""

    def test_subagent_path_and_meta(self) -> None:
        projects = self.root / "projects"
        session = projects / "-Users-me-app" / "s1.jsonl"
        self.assertEqual(
            subagent_transcript_path(session, "aa50d957"),
            projects / "-Users-me-app" / "s1" / "subagents" / "agent-aa50d957.jsonl",
        )
        meta = session.with_suffix("") / "subagents" / "agent-aa50d957.meta.json"
        meta.parent.mkdir(parents=True)
        meta.write_text('{"agentType": "general-purpose", "toolUseId": "toolu_1", "finished": false}')
        with EventStore(self.root / "agentvis.db") as store:
            self.assertTrue(read_subagent_meta(store, meta, projects))
            self.assertFalse(read_subagent_meta(store, meta, projects))
            meta.write_text('{"agentType": "general-purpose", "toolUseId": "toolu_1", "finished": true}')
            self.assertTrue(read_subagent_meta(store, meta, projects))
            events = store.events()
            self.assertEqual([(event.kind, event.session_id) for event in events], [("subagent-meta", "s1")] * 2)
            self.assertFalse(read_subagent_meta(store, meta.with_name("absent.meta.json"), projects))


class PathsToReadTest(RepoTestCase):
    """@doc: docs/design/Transcript.md#6-테스트"""

    def test_selects_session_subagent_and_agent_paths(self) -> None:
        session = "/p/-Users-me-app/s1.jsonl"
        self.assertEqual(paths_to_read({"transcript_path": session}), [Path(session)])
        self.assertEqual(
            paths_to_read({"transcript_path": session, "agent_id": "a1", "agent_transcript_path": "/p/-Users-me-app/s1/subagents/agent-a1.jsonl"}),
            [Path(session), Path("/p/-Users-me-app/s1/subagents/agent-a1.jsonl"), Path("/p/-Users-me-app/s1/subagents/agent-a1.meta.json")],
        )
        self.assertEqual(paths_to_read({"transcript_path": 3, "agent_id": "a1"}), [])


class TranscriptReaderTest(RepoTestCase):
    """@doc: docs/design/Transcript.md#6-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.projects = self.root / "projects"
        self.store = EventStore(self.root / "agentvis.db")
        self.addCleanup(self.store.close)
        self.reader = TranscriptReader(self.store, self.projects)
        self.addCleanup(self.reader.stop)

    def test_coalesces_waiting_requests_and_survives_failures(self) -> None:
        calls: list[Path] = []
        release = threading.Event()

        def fake_read(path: Path) -> None:
            calls.append(path)
            if path.name == "slow.jsonl":
                release.wait(5)
            if path.name == "bad.jsonl":
                raise ValueError("boom")

        with mock.patch.object(self.reader, "_read", fake_read), self.assertLogs("agentvis.transcript", "ERROR"):
            for name in ("a.jsonl", "a.jsonl", "bad.jsonl", "b.jsonl"):
                self.reader.request(Path(name))
            self.reader.start()
            self.assertTrue(self.reader.wait_until_idle(5))
            self.reader.request(Path("slow.jsonl"))
            while Path("slow.jsonl") not in calls:
                threading.Event().wait(0.01)
            self.reader.request(Path("slow.jsonl"))
            release.set()
            self.assertTrue(self.reader.wait_until_idle(5))
        self.assertEqual([path.name for path in calls], ["a.jsonl", "bad.jsonl", "b.jsonl", "slow.jsonl", "slow.jsonl"])

    def test_hook_event_brings_in_transcript_content(self) -> None:
        session = self.projects / "-Users-me-app" / "s1.jsonl"
        session.parent.mkdir(parents=True)
        session.write_bytes(_PROMPT + _THINKING + _QUEUED)
        self.reader.start()
        client = TestClient(create_app(self.store, self.reader), base_url="http://127.0.0.1:8765")
        hook = {"session_id": "s1", "hook_event_name": "Stop", "transcript_path": str(session), "cwd": "/Users/me/app"}
        response = client.post("/hooks", content=json.dumps(hook).encode(), headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.reader.wait_until_idle(5))
        stored = [(event.source, event.kind) for event in self.store.events()]
        self.assertEqual(
            stored,
            [("hook", "Stop"), ("transcript", "user"), ("transcript", "assistant"), ("transcript", "queue-operation")],
        )

