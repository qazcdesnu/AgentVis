"""Tests for the agentvis command line entry point.

@doc: docs/design/Cli.md#4-테스트
"""

import io
import json
import os
import signal
import tomllib
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import uvicorn
from fastapi import FastAPI

from agentvis import __version__
from agentvis.cli import DEFAULT_PORT, SHUTDOWN_GRACE_SECONDS, _run_server, main
from agentvis.server import create_app
from agentvis.store import EventStore
from tests.support import RepoTestCase
from tools.doclib import REPO_ROOT


class CliTest(unittest.TestCase):
    """@doc: docs/design/Cli.md#4-테스트"""

    def test_version_option_prints_package_version(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as exit_info:
            main(["--version"])
        self.assertEqual(exit_info.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), f"agentvis {__version__}")
        pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(__version__, pyproject["project"]["version"])
        # Releases use semantic versions (PullRequestRule.md section 6).
        self.assertRegex(pyproject["project"]["version"], r"^\d+\.\d+\.\d+$")

    def test_no_arguments_prints_help(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main([])
        self.assertEqual(code, 0)
        self.assertIn("usage: agentvis", output.getvalue())


class ServeTest(RepoTestCase):
    """@doc: docs/design/Cli.md#4-테스트"""

    def setUp(self) -> None:
        super().setUp()
        patcher = mock.patch.dict(os.environ, {"AGENTVIS_HOME": str(self.root)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.calls: list[tuple] = []
        self.closed = 0
        original_close = EventStore.close

        def counting_close(store: EventStore) -> None:
            self.closed += 1
            original_close(store)

        close_patcher = mock.patch.object(EventStore, "close", counting_close)
        close_patcher.start()
        self.addCleanup(close_patcher.stop)

    def fake_run(self, app: FastAPI, host: str, port: int) -> None:
        self.calls.append((type(app), host, port, (self.root / "agentvis.db").exists()))

    def run_main(self, *args: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(list(args))
        return code, output.getvalue()

    def test_serve_runs_uvicorn_on_loopback_with_default_store(self) -> None:
        with mock.patch("agentvis.cli._run_server", self.fake_run):
            code, output = self.run_main("serve")
        self.assertEqual(code, 0)
        self.assertEqual(self.calls, [(FastAPI, "127.0.0.1", DEFAULT_PORT, True)])
        self.assertIn("놓친 세션 기록:", output)
        self.assertIn(f"AgentVis 서버: http://127.0.0.1:{DEFAULT_PORT}", output)
        self.assertIn(f"데이터베이스: {self.root / 'agentvis.db'}", output)
        self.assertEqual(self.closed, 1)

    def test_server_marks_the_app_stopping_and_bounds_the_wait_for_open_streams(self) -> None:
        with EventStore(self.root / "agentvis.db") as store:
            app = create_app(store)
            captured = {}
            with mock.patch.object(uvicorn.Server, "run", lambda server: captured.setdefault("server", server)):
                _run_server(app, "127.0.0.1", 9100)
            server = captured["server"]
            # An open live-update stream must not keep Ctrl+C from stopping the server (M4-T2).
            self.assertEqual(server.config.timeout_graceful_shutdown, SHUTDOWN_GRACE_SECONDS)
            self.assertFalse(app.state.stopping)
            server.handle_exit(signal.SIGINT, None)
            self.assertTrue(app.state.stopping)

    def test_serve_port_option(self) -> None:
        with mock.patch("agentvis.cli._run_server", self.fake_run):
            self.run_main("serve", "--port", "9100")
        self.assertEqual(self.calls[0][2], 9100)

    def test_out_of_range_port_is_rejected(self) -> None:
        for port in ("0", "65536", "abc"):
            with self.subTest(port=port), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit_info:
                main(["serve", "--port", port])
            self.assertEqual(exit_info.exception.code, 2)

    def test_store_is_closed_when_server_fails(self) -> None:
        with mock.patch("agentvis.cli._run_server", side_effect=SystemExit(3)):
            with self.assertRaises(SystemExit):
                self.run_main("serve")
        self.assertEqual(self.closed, 1)


class ExperimentTest(RepoTestCase):
    """@doc: docs/design/Cli.md#4-테스트"""

    def setUp(self) -> None:
        super().setUp()
        patcher = mock.patch.dict(os.environ, {"AGENTVIS_HOME": str(self.root / "home")})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.scenario = self.root / "scenario"
        record = {"type": "user", "uuid": "u1", "sessionId": "s1", "promptId": "p1", "cwd": "/work/app",
                  "timestamp": "2026-10-31T01:00:00.000Z", "message": {"role": "user", "content": "테스트 고쳐"}}
        session = self.write("scenario/-work-app/s1.jsonl", json.dumps(record, ensure_ascii=False) + "\n")
        # An old file still belongs to the scenario.
        os.utime(session, (946684800, 946684800))
        self.database = self.root / "home" / "experiments" / "P01" / "agentvis.db"
        self.stored: list[int] = []

    def fake_run(self, app: FastAPI, host: str, port: int) -> None:
        with EventStore(self.database) as store:
            self.stored.append(len(store.events()))

    def run_main(self, *args: str) -> tuple[int, str, str]:
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors), mock.patch("agentvis.cli._run_server", self.fake_run):
            code = main(list(args))
        return code, output.getvalue(), errors.getvalue()

    def test_reads_every_scenario_transcript_into_the_participant_store(self) -> None:
        code, output, _ = self.run_main("experiment", "P01", "--transcripts", str(self.scenario))
        self.assertEqual(code, 0)
        self.assertEqual(self.stored, [1])
        self.assertIn("AgentVis 실험 모드: 참가자 P01", output)
        self.assertIn("시나리오 세션 기록: 1개 파일", output)
        self.assertIn(f"데이터 디렉터리: {self.database.parent}", output)
        self.assertIn(f"AgentVis 버전: {__version__}", output)
        self.assertFalse((self.root / "home" / "agentvis.db").exists())

    def test_participant_numbers_cannot_leave_the_directory(self) -> None:
        for participant in ("../P01", "a/b", "P 01", "x" * 33, ""):
            with self.subTest(participant=participant), self.assertRaises(SystemExit) as exit_info:
                self.run_main("experiment", participant, "--transcripts", str(self.scenario))
            self.assertEqual(exit_info.exception.code, 2)

    def test_missing_or_empty_folders_are_errors(self) -> None:
        (self.root / "empty").mkdir()
        for folder in (self.root / "absent", self.root / "empty"):
            with self.subTest(folder=folder):
                code, _, errors = self.run_main("experiment", "P01", "--transcripts", str(folder))
                self.assertEqual(code, 1)
                self.assertIn("오류:", errors)
        self.assertFalse(self.database.exists())


class HooksCommandTest(RepoTestCase):
    """@doc: docs/design/Cli.md#4-테스트"""

    def setUp(self) -> None:
        super().setUp()
        patcher = mock.patch.dict(os.environ, {"AGENTVIS_HOME": str(self.root / "home")})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.original = '{\n  "model": "opus",\n  "hooks": {\n    "Stop": [{"hooks": [{"type": "command", "command": "x"}]}]\n  }\n}\n'
        self.settings = self.write("claude/settings.json", self.original)
        self.backups = self.root / "home" / "backups"

    def run_main(self, *args: str) -> tuple[int, str, str]:
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = main(list(args))
        return code, output.getvalue(), errors.getvalue()

    def test_install_then_uninstall_restores_settings(self) -> None:
        code, output, _ = self.run_main("hooks", "install", "--settings", str(self.settings))
        self.assertEqual(code, 0)
        self.assertIn("추가한 hook: 14개 (http://127.0.0.1:8765/hooks?client=agentvis)", output)
        self.assertEqual(len(list(self.backups.iterdir())), 1)
        code, output, _ = self.run_main("hooks", "uninstall", "--settings", str(self.settings))
        self.assertEqual(code, 0)
        self.assertIn("제거한 hook: 14개", output)
        self.assertEqual(json.loads(self.settings.read_text(encoding="utf-8")), json.loads(self.original))
        self.assertEqual(len(list(self.backups.iterdir())), 2)

    def test_repeating_install_changes_nothing(self) -> None:
        self.run_main("hooks", "install", "--settings", str(self.settings))
        before = self.settings.read_text(encoding="utf-8")
        code, output, _ = self.run_main("hooks", "install", "--settings", str(self.settings))
        self.assertEqual(code, 0)
        self.assertIn("변경 없음", output)
        self.assertEqual(self.settings.read_text(encoding="utf-8"), before)
        self.assertEqual(len(list(self.backups.iterdir())), 1)
        code, output, _ = self.run_main("hooks", "uninstall", "--settings", str(self.settings))
        code, output, _ = self.run_main("hooks", "uninstall", "--settings", str(self.settings))
        self.assertIn("제거할 AgentVis hook 없음", output)

    def test_invalid_settings_exit_1_and_file_unchanged(self) -> None:
        self.settings.write_text('{"hooks": []}', encoding="utf-8")
        code, _, errors = self.run_main("hooks", "install", "--settings", str(self.settings))
        self.assertEqual(code, 1)
        self.assertIn("오류:", errors)
        self.assertEqual(self.settings.read_text(encoding="utf-8"), '{"hooks": []}')
        self.assertFalse(self.backups.exists())


if __name__ == "__main__":
    unittest.main()
