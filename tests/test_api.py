"""Tests for the session query API.

@doc: docs/design/Analysis.md#9-테스트
"""

import os
from dataclasses import replace
from unittest import mock

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

    def test_turn_graph_and_missing_turn(self) -> None:
        graph = self.client.get("/api/sessions/s-new/turns/1/graph").json()
        self.assertEqual((graph["session_id"], graph["turn_index"], [lane["id"] for lane in graph["lanes"]]), ("s-new", 1, ["main"]))
        self.assertEqual([(node["kind"], node["status"]) for node in graph["nodes"]], [("prompt", None), ("tool_call", "error")])
        self.assertEqual(graph["edges"], [{"source": "prompt", "target": graph["nodes"][1]["id"], "kind": "next"}])
        self.assertEqual(self.client.get("/api/sessions/s-new/turns/2/graph").status_code, 404)
        self.assertEqual(self.client.get("/api/sessions/nope/turns/1/graph").status_code, 404)

    def test_project_list_groups_sessions(self) -> None:
        real = self.root / "home" / "work" / "real-app"
        real.mkdir(parents=True)
        built = _Session()
        built.clock = 200
        built.record(type="user", uuid="w1", promptId="x1", origin={"kind": "human"}, cwd=str(real), message={"content": "실재하는 폴더"})
        self.store.append_batch([replace(event, session_id="s-real", id=None) for event in built.events])
        self.store.append(replace(built.events[0], session_id="s-nocwd", cwd=None, dedup_key="uuid:nocwd",
                                  payload='{"type": "system", "subtype": "turn_duration"}', id=None))
        with mock.patch.dict(os.environ, {"HOME": str(self.root / "home")}):
            projects = self.client.get("/api/projects").json()["projects"]
        self.assertEqual([item["name"] for item in projects], ["real-app", "app", "other"])
        self.assertEqual((projects[0]["parent"], projects[0]["exists"], projects[0]["session_count"]), ("~/work", True, 1))
        self.assertEqual((projects[1]["path"], projects[1]["parent"], projects[1]["exists"], projects[1]["session_count"]),
                         ("/Users/me/app", "/Users/me", False, 2))
        self.assertTrue(projects[1]["last_activity"].endswith("+00:00"))


class WebScreenTest(RepoTestCase):
    """@doc: docs/design/WebUI.md#6-테스트"""

    def test_serves_screen_files_without_hiding_the_api(self) -> None:
        with EventStore(self.root / "agentvis.db") as store:
            client = TestClient(create_app(store), base_url="http://127.0.0.1:8765")
            index = client.get("/")
            self.assertEqual(index.status_code, 200)
            self.assertIn('<script type="module" src="app.js">', index.text)
            self.assertIn("javascript", client.get("/app.js").headers["content-type"])
            self.assertIn("text/css", client.get("/style.css").headers["content-type"])
            self.assertIn('<script src="vendor/d3-7.9.0.min.js">', index.text)
            self.assertIn("javascript", client.get("/graph.js").headers["content-type"])
            self.assertIn("d3js.org v7.9.0", client.get("/vendor/d3-7.9.0.min.js").text[:80])
            self.assertEqual(client.get("/api/projects").json(), {"projects": []})
            self.assertEqual(client.get("/health").json(), {"status": "ok"})
            self.assertEqual(client.get("/nope.js").status_code, 404)

