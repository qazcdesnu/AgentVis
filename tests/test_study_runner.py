"""Tests for the transcript runner of the experiment material tools.

@doc: docs/design/Study.md#6-테스트
"""

import json
import subprocess
from pathlib import Path

from agentvis.study.runner import RunSpec, claude_command, run_variant
from tests.support import RepoTestCase


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class ClaudeCommandTest(RepoTestCase):
    """@doc: docs/design/Study.md#6-테스트"""

    def test_command_is_isolated_from_user_settings(self) -> None:
        spec = RunSpec(repo="r", commit="c", instruction="fix it", name="v")
        command = claude_command(spec, "sid")
        self.assertEqual(command[:3], ["claude", "-p", "fix it"])
        self.assertIn("--setting-sources", command)
        self.assertEqual(command[command.index("--setting-sources") + 1], "project,local")
        self.assertIn("--strict-mcp-config", command)
        self.assertEqual(command[command.index("--session-id") + 1], "sid")
        self.assertIn("Bash", command)
        self.assertNotIn("--model", command)
        spec = RunSpec(repo="r", commit="c", instruction="x", name="v", model="m", max_budget_usd=0.5)
        command = claude_command(spec, "sid")
        self.assertEqual(command[command.index("--model") + 1], "m")
        self.assertEqual(command[command.index("--max-budget-usd") + 1], "0.5")


class RunVariantTest(RepoTestCase):
    """@doc: docs/design/Study.md#6-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.origin = self.root / "origin"
        self.origin.mkdir()
        _git(self.origin, "init", "-q")
        _git(self.origin, "config", "user.email", "t@example.com")
        _git(self.origin, "config", "user.name", "t")
        (self.origin / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        _git(self.origin, "add", "-A")
        _git(self.origin, "commit", "-q", "-m", "start")
        self.commit = _git(self.origin, "rev-parse", "HEAD")
        self.projects = self.root / "projects"
        self.out = self.root / "out"
        self.cwds: list[Path] = []

    def fake_claude(self, write: bool = True):
        def invoke(command: list[str], cwd: Path, timeout: float) -> subprocess.CompletedProcess:
            session = command[command.index("--session-id") + 1]
            self.cwds.append(cwd)
            (cwd / "calc.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
            (cwd / "__pycache__").mkdir(exist_ok=True)
            (cwd / "__pycache__" / "calc.cpython-312.pyc").write_bytes(b"\x00binary")
            if write:
                folder = self.projects / "-tmp-work"
                folder.mkdir(parents=True, exist_ok=True)
                (folder / f"{session}.jsonl").write_text('{"type": "user"}\n', encoding="utf-8")
                (folder / session / "subagents").mkdir(parents=True)
                (folder / session / "subagents" / "agent-a.jsonl").write_text("{}\n", encoding="utf-8")
            result = {"is_error": False, "num_turns": 3, "total_cost_usd": 0.01, "duration_ms": 900}
            return subprocess.CompletedProcess(command, 0, json.dumps(result), "")
        return invoke

    def run_spec(self, name: str = "calc-e2", write: bool = True, runs: int = 2) -> list[dict]:
        spec = RunSpec(repo=str(self.origin), commit=self.commit, instruction="fix add", name=name)
        return run_variant(spec, runs, self.out, self.projects, self.root / "work", self.fake_claude(write), version="9.9.9")

    def test_transcripts_move_into_the_scenario_folder(self) -> None:
        records = self.run_spec()
        self.assertEqual([record["run"] for record in records], [1, 2])
        for record in records:
            session = record["session_id"]
            self.assertEqual(record["transcript"], f"calc-e2/{session}.jsonl")
            self.assertTrue((self.out / "calc-e2" / f"{session}.jsonl").exists())
            self.assertTrue((self.out / "calc-e2" / session / "subagents" / "agent-a.jsonl").exists())
            diff = (self.out / "calc-e2" / f"{session}.diff").read_text(encoding="utf-8")
            self.assertIn("+    return a + b", diff)
            self.assertNotIn("__pycache__", diff)
            self.assertEqual((record["claude_version"], record["num_turns"], record["exit_code"]), ("9.9.9", 3, 0))
        # Every run of a task works in the same neutral folder, so the path does not name the variant.
        self.assertEqual(self.cwds, [self.root / "work" / "origin"] * 2)
        # Nothing is left where `agentvis serve` would read it later.
        self.assertEqual(list(self.projects.glob("*/*.jsonl")), [])
        lines = (self.out / "runs.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual([json.loads(line)["session_id"] for line in lines], [record["session_id"] for record in records])

    def test_a_run_without_a_transcript_is_recorded_as_missing(self) -> None:
        records = self.run_spec(write=False, runs=1)
        self.assertIsNone(records[0]["transcript"])

    def test_variant_names_cannot_leave_the_folder(self) -> None:
        for name in ("../x", "a/b", ""):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.run_spec(name=name, runs=1)
