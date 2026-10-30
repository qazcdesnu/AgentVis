"""Tests for hook event conversion and the collector HTTP endpoints.

@doc: docs/design/Collector.md#3-테스트
"""

import json
import unittest
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from agentvis.collector import InvalidHookEvent, hook_event_to_raw
from agentvis.server import create_app
from agentvis.store import EventStore
from tests.support import RepoTestCase

# Shape observed from Claude Code 2.1.314 (docs/DataSource.md, section 2.3).
_FAILURE = json.dumps(
    {
        "session_id": "08b5b271-69fd-4501-8dc3-def2fa00d64a",
        "transcript_path": "/Users/me/.claude/projects/-Users-me-app/08b5b271.jsonl",
        "cwd": "/Users/me/app",
        "prompt_id": "c6131da1-ab93-48d1-8162-4f5af0114f0e",
        "permission_mode": "default",
        "hook_event_name": "PostToolUseFailure",
        "tool_name": "Bash",
        "tool_input": {"command": "ls /nonexistent_dir_xyz"},
        "tool_use_id": "toolu_01Y7eaRxHAzCUkDvKx3HE3PM",
        "error": "Exit code 1\nls: /nonexistent_dir_xyz: No such file or directory",
        "is_interrupt": False,
        "duration_ms": 54,
    },
    ensure_ascii=False,
)
_SESSION_END = '{"session_id": "s1", "hook_event_name": "SessionEnd", "reason": "other", "cwd": "/w"}'
_NOW = datetime(2026, 10, 31, 1, 0, tzinfo=UTC)


class HookEventToRawTest(unittest.TestCase):
    """@doc: docs/design/Collector.md#3-테스트"""

    def test_converts_observed_failure_event(self) -> None:
        event = hook_event_to_raw(_FAILURE.encode(), _NOW)
        self.assertEqual(event.source, "hook")
        self.assertEqual(event.kind, "PostToolUseFailure")
        self.assertEqual(event.session_id, "08b5b271-69fd-4501-8dc3-def2fa00d64a")
        self.assertEqual(event.prompt_id, "c6131da1-ab93-48d1-8162-4f5af0114f0e")
        self.assertEqual(event.tool_use_id, "toolu_01Y7eaRxHAzCUkDvKx3HE3PM")
        self.assertEqual(event.cwd, "/Users/me/app")
        self.assertEqual(event.occurred_at, _NOW)
        self.assertEqual(event.payload, _FAILURE)
        self.assertIsNone(event.dedup_key)

    def test_non_string_optional_fields_become_none(self) -> None:
        body = b'{"session_id": "s1", "hook_event_name": "FutureEvent", "prompt_id": 3, "tool_use_id": null, "cwd": []}'
        event = hook_event_to_raw(body, _NOW)
        self.assertEqual(event.kind, "FutureEvent")
        self.assertEqual((event.prompt_id, event.tool_use_id, event.cwd), (None, None, None))

    def test_rejects_invalid_bodies(self) -> None:
        for body in (b"not json", b"\xff\xfe", b"[1, 2]", b'{"session_id": "s1"}', b'{"hook_event_name": "Stop", "session_id": 1}'):
            with self.subTest(body=body), self.assertRaises(InvalidHookEvent):
                hook_event_to_raw(body, _NOW)


class CollectorAppTest(RepoTestCase):
    """@doc: docs/design/Collector.md#3-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.store = EventStore(self.root / "agentvis.db")
        self.addCleanup(self.store.close)
        # The same Host and Content-Type that Claude Code's http hook sends.
        self.client = TestClient(create_app(self.store), base_url="http://127.0.0.1:8765")
        self.client.headers["Content-Type"] = "application/json"

    def test_stores_hook_events_and_returns_empty_object(self) -> None:
        response = self.client.post("/hooks?client=agentvis", content=_FAILURE.encode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"{}")
        response = self.client.post("/hooks", content=_SESSION_END.encode())
        self.assertEqual(response.status_code, 200)
        stored = self.store.events()
        self.assertEqual([event.kind for event in stored], ["PostToolUseFailure", "SessionEnd"])
        self.assertEqual(stored[0].payload, _FAILURE)
        self.assertIsNone(stored[1].prompt_id)

    def test_invalid_body_gets_400_and_is_not_stored(self) -> None:
        for body in (b"not json", b"[]", b'{"session_id": "s1"}'):
            with self.subTest(body=body):
                response = self.client.post("/hooks", content=body)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json())
        self.assertEqual(self.store.events(), [])

    def test_rejects_requests_that_are_not_from_a_hook(self) -> None:
        cases = [
            ({"Host": "attacker.example:8765"}, 400),
            ({"Origin": "https://evil.example"}, 403),
            ({"Origin": "http://127.0.0.1:8765"}, 403),
            ({"Content-Type": "text/plain"}, 415),
        ]
        for headers, status in cases:
            with self.subTest(headers=headers):
                response = self.client.post("/hooks", content=_SESSION_END.encode(), headers=headers)
                self.assertEqual(response.status_code, status)
        bare = TestClient(create_app(self.store), base_url="http://127.0.0.1:8765")
        self.assertEqual(bare.post("/hooks", content=_SESSION_END.encode()).status_code, 415)
        self.assertEqual(self.store.events(), [])

    def test_accepts_localhost_and_json_with_charset(self) -> None:
        response = self.client.post(
            "/hooks",
            content=_SESSION_END.encode(),
            headers={"Host": "localhost:8765", "Content-Type": "application/json; charset=utf-8"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.store.events()), 1)

    def test_health(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
