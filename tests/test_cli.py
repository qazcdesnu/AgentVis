"""Tests for the agentvis command line entry point.

@doc: docs/design/Cli.md#4-테스트
"""

import io
import json
import os
import tomllib
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from fastapi import FastAPI

from agentvis import __version__
from agentvis.cli import DEFAULT_PORT, main
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
        with mock.patch("agentvis.cli.uvicorn.run", self.fake_run):
            code, output = self.run_main("serve")
        self.assertEqual(code, 0)
        self.assertEqual(self.calls, [(FastAPI, "127.0.0.1", DEFAULT_PORT, True)])
        self.assertIn(f"AgentVis 서버: http://127.0.0.1:{DEFAULT_PORT}", output)
        self.assertIn(f"데이터베이스: {self.root / 'agentvis.db'}", output)
        self.assertEqual(self.closed, 1)

    def test_serve_port_option(self) -> None:
        with mock.patch("agentvis.cli.uvicorn.run", self.fake_run):
            self.run_main("serve", "--port", "9100")
        self.assertEqual(self.calls[0][2], 9100)

    def test_out_of_range_port_is_rejected(self) -> None:
        for port in ("0", "65536", "abc"):
            with self.subTest(port=port), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit_info:
                main(["serve", "--port", port])
            self.assertEqual(exit_info.exception.code, 2)

    def test_store_is_closed_when_server_fails(self) -> None:
        with mock.patch("agentvis.cli.uvicorn.run", side_effect=SystemExit(3)):
            with self.assertRaises(SystemExit):
                self.run_main("serve")
        self.assertEqual(self.closed, 1)


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
        self.assertIn("추가한 hook: 15개 (http://127.0.0.1:8765/hooks?client=agentvis)", output)
        self.assertEqual(len(list(self.backups.iterdir())), 1)
        code, output, _ = self.run_main("hooks", "uninstall", "--settings", str(self.settings))
        self.assertEqual(code, 0)
        self.assertIn("제거한 hook: 15개", output)
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
