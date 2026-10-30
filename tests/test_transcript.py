"""Tests for reading transcript files into the event store.

@doc: docs/design/Transcript.md#6-테스트
"""

import json
import shutil
from unittest import mock

from agentvis import transcript
from agentvis.store import EventStore
from agentvis.transcript import (
    ReadResult,
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
_IGNORED = [_line(type="api-request-blob", hash="h"), b"not json\n", json.dumps({"type": "user", "sessionId": "s1"}).encode() + b"\n"]


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
        self.assertEqual((first.stored, first.skipped), (2, 3))
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
