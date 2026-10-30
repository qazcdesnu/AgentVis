"""Tests for the session query API.

@doc: docs/design/Analysis.md#9-테스트
"""

from dataclasses import replace

from fastapi.testclient import TestClient

from agentvis.server import create_app
from agentvis.store import EventStore
from tests.support import RepoTestCase
from tests.test_analysis import _Session


class SessionApiTest(RepoTestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.store = EventStore(self.root / "agentvis.db")
        self.addCleanup(self.store.close)
        older = _Session()
        older.prompt("u1", "p1", "첫 프로젝트 작업")
        newer = _Session()
        newer.clock = 100
        # Record uuids are dedup keys, so each session needs its own.
        newer.prompt("n1", "q1", "다른 작업")
        newer.assistant("n2", "n1", {"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {}})
        newer.result("n3", "n2", "q1", "toolu_1", "Exit code 1", is_error=True)
        other = _Session()
        other.clock = 50
        other.record(type="user", uuid="v1", promptId="r1", origin={"kind": "human"}, cwd="/Users/me/other", message={"content": "다른 프로젝트"})
        for session_id, built in (("s-old", older), ("s-new", newer), ("s-other", other)):
            self.store.append_batch([replace(event, session_id=session_id, id=None) for event in built.events])
        self.client = TestClient(create_app(self.store), base_url="http://127.0.0.1:8765")

    def test_lists_sessions_of_a_project_latest_first(self) -> None:
        response = self.client.get("/api/sessions", params={"project": "/Users/me/app"})
        self.assertEqual(response.status_code, 200)
        sessions = response.json()["sessions"]
        self.assertEqual([item["session_id"] for item in sessions], ["s-new", "s-old"])
        self.assertNotIn("turns", sessions[0])
        self.assertNotIn("preamble", sessions[0])
        self.assertEqual((sessions[0]["title"], sessions[0]["failure_count"]), ("다른 작업", 1))
        self.assertTrue(sessions[0]["last_activity"].endswith("+00:00"))
        everything = self.client.get("/api/sessions").json()["sessions"]
        self.assertEqual([item["session_id"] for item in everything], ["s-new", "s-other", "s-old"])

    def test_session_detail_and_missing_session(self) -> None:
        detail = self.client.get("/api/sessions/s-new").json()
        self.assertEqual(detail["turns"][0]["prompt"], "다른 작업")
        call = detail["turns"][0]["steps"][0]["tool_call"]
        self.assertEqual((call["tool_name"], call["status"]), ("Bash", "error"))
        self.assertEqual(self.client.get("/api/sessions/nope").status_code, 404)
        self.assertEqual(self.client.get("/api/sessions", headers={"Host": "attacker.example"}).status_code, 400)
