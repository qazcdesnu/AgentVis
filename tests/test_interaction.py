"""Tests for the screen usage log of experiment mode.

@doc: docs/design/WebUI.md#93-테스트
"""

import json

from fastapi.testclient import TestClient

from agentvis import __version__
from agentvis.interaction import MAX_BODY_BYTES, MAX_EVENTS, InteractionLog
from agentvis.server import create_app
from agentvis.store import EventStore
from tests.support import RepoTestCase

_ORIGIN = {"Origin": "http://127.0.0.1:8765", "Content-Type": "application/json"}


class InteractionLogTest(RepoTestCase):
    """@doc: docs/design/WebUI.md#93-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.store = EventStore(self.root / "agentvis.db")
        self.addCleanup(self.store.close)
        self.log = InteractionLog(self.root / "P01" / "interactions.jsonl", "P01")
        self.client = TestClient(create_app(self.store, interaction_log=self.log), base_url="http://127.0.0.1:8765")

    def lines(self) -> list[dict]:
        return [json.loads(line) for line in self.log.path.read_text(encoding="utf-8").splitlines()]

    def post(self, body: object, headers: dict = _ORIGIN):
        content = body if isinstance(body, bytes) else json.dumps(body).encode()
        return self.client.post("/api/interactions", content=content, headers=headers)

    def test_experiment_endpoint_tells_the_mode(self) -> None:
        self.assertEqual(self.client.get("/api/experiment").json(), {"participant": "P01", "version": __version__, "condition": "agentvis"})
        plain = TestClient(create_app(self.store), base_url="http://127.0.0.1:8765")
        self.assertEqual(plain.get("/api/experiment").json(), {"participant": None, "version": __version__, "condition": None})
        self.assertEqual(plain.post("/api/interactions", content=b'{"events": []}', headers=_ORIGIN).status_code, 404)

    def test_events_are_appended_one_line_each_after_the_start_line(self) -> None:
        events = [
            {"at": "2026-11-12T01:00:00.000Z", "type": "open", "detail": {"hash": "", "width": 1280}},
            {"at": "2026-11-12T01:00:01.000Z", "type": "hash", "detail": {"hash": "#session=s1"}},
        ]
        response = self.post({"events": events})
        self.assertEqual(response.json(), {"stored": 2})
        lines = self.lines()
        self.assertEqual(lines[0]["type"], "server_start")
        self.assertEqual(lines[0]["version"], __version__)
        self.assertEqual([(line["type"], line["participant"], line["at"]) for line in lines[1:]],
                         [("open", "P01", events[0]["at"]), ("hash", "P01", events[1]["at"])])
        self.assertEqual(lines[2]["detail"], {"hash": "#session=s1"})

    def test_requests_from_elsewhere_or_malformed_are_refused(self) -> None:
        good = {"events": [{"at": "t", "type": "click", "detail": {}}]}
        self.assertEqual(self.post(good, {"Content-Type": "application/json"}).status_code, 403)
        self.assertEqual(self.post(good, {**_ORIGIN, "Origin": "http://evil.example"}).status_code, 403)
        self.assertEqual(self.post(good, {**_ORIGIN, "Content-Type": "text/plain"}).status_code, 415)
        bad_bodies = [
            b"not json",
            {"events": "x"},
            {"events": [{"at": "t", "type": "click"}] * (MAX_EVENTS + 1)},
            {"events": [{"at": "t", "type": "Click!"}]},
            {"events": [{"at": 1, "type": "click"}]},
            {"events": [{"at": "t", "type": "click", "detail": {"text": "x" * 2001}}]},
            {"events": [{"at": "t", "type": "click", "detail": []}]},
            b'{"events": [], "pad": "' + b"x" * MAX_BODY_BYTES + b'"}',
        ]
        for body in bad_bodies:
            with self.subTest(body=str(body)[:40]):
                self.assertEqual(self.post(body).status_code, 400)
        self.assertEqual(len(self.lines()), 1)


class BaselineConditionTest(RepoTestCase):
    """@doc: docs/design/WebUI.md#93-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.store = EventStore(self.root / "agentvis.db")
        self.addCleanup(self.store.close)
        record = {"type": "user", "timestamp": "2026-11-13T01:00:00.000Z", "message": {"role": "user", "content": "<b>고쳐</b> 주세요"}}
        for session in ("s-b", "s-a"):
            self.write(f"block/cal-e2/{session}.jsonl", json.dumps(record, ensure_ascii=False) + "\n")
        log = InteractionLog(self.root / "P01" / "interactions.jsonl", "P01", "baseline")
        self.client = TestClient(create_app(self.store, interaction_log=log, baseline=self.root / "block"), base_url="http://127.0.0.1:8765")

    def test_index_names_records_only_by_order(self) -> None:
        page = self.client.get("/").text
        self.assertIn('<a href="/baseline/s-a">기록 1</a>', page)
        self.assertIn('<a href="/baseline/s-b">기록 2</a>', page)
        self.assertNotIn("cal-e2", page)
        self.assertIn('id="trial"', page)

    def test_record_pages_carry_the_header_and_escape_the_record(self) -> None:
        page = self.client.get("/baseline/s-b").text
        self.assertIn("실행 기록 2", page)
        self.assertIn('import { startInteractionLog } from "/interaction.js"', page)
        self.assertIn("&lt;b&gt;고쳐&lt;/b&gt;", page)
        self.assertEqual(self.client.get("/baseline/nope").status_code, 404)
        self.assertEqual(self.client.get("/baseline/..%2Fx").status_code, 404)
        self.assertEqual(self.client.get("/api/experiment").json()["condition"], "baseline")

    def test_plain_apps_have_no_baseline_pages(self) -> None:
        plain = TestClient(create_app(self.store), base_url="http://127.0.0.1:8765")
        self.assertEqual(plain.get("/baseline/s-a").status_code, 404)
        self.assertIn("<title>AgentVis</title>", plain.get("/").text)
