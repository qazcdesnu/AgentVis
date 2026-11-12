"""Run Claude Code on instruction variants and collect the transcripts into a scenario folder (M9-T2).

@doc: docs/design/Study.md#2-실행-기록-생성-m9-t2
"""

import json
import re
import shutil
import subprocess
import tempfile
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

# Variant names become folder names.
# @doc: docs/design/Study.md#1-자료의-모양
STUDY_NAME_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}")
# @doc: docs/design/Study.md#2-실행-기록-생성-m9-t2
STUDY_TIMEOUT_SECONDS = 1800
_ALLOWED_TOOLS = ("Bash", "Read", "Edit", "Write", "Glob", "Grep")
# Build artifacts the agent leaves behind say nothing about its change.
# @doc: docs/design/Study.md#2-실행-기록-생성-m9-t2
DIFF_EXCLUDES = (":(exclude)**/__pycache__/**", ":(exclude)*.pyc", ":(exclude)**/node_modules/**", ":(exclude)**/.pytest_cache/**")

Invoke = Callable[[list[str], Path, float], subprocess.CompletedProcess]


@dataclass(frozen=True)
class RunSpec:
    """One instruction variant of one task, and how to run Claude Code on it.

    @doc: docs/design/Study.md#2-실행-기록-생성-m9-t2
    """

    repo: str
    commit: str
    instruction: str
    name: str
    model: str | None = None
    max_budget_usd: float | None = None
    timeout: float = STUDY_TIMEOUT_SECONDS
    claude: str = "claude"


def claude_command(spec: RunSpec, session_id: str) -> list[str]:
    """The non-interactive Claude Code command for one run, isolated from the user's settings.

    @doc: docs/design/Study.md#2-실행-기록-생성-m9-t2
    """
    command = [
        spec.claude, "-p", spec.instruction,
        "--session-id", session_id,
        "--output-format", "json",
        "--setting-sources", "project,local",
        "--strict-mcp-config",
        "--permission-mode", "acceptEdits",
        "--allowedTools", *_ALLOWED_TOOLS,
    ]
    if spec.model:
        command += ["--model", spec.model]
    if spec.max_budget_usd is not None:
        command += ["--max-budget-usd", str(spec.max_budget_usd)]
    return command


def collect_transcript(projects_dir: Path, session_id: str, destination: Path) -> Path | None:
    """Move a session's transcript and its subagent folder out of the transcript root.

    @doc: docs/design/Study.md#2-실행-기록-생성-m9-t2
    """
    found = sorted(projects_dir.glob(f"*/{session_id}.jsonl"))
    if not found:
        return None
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / found[0].name
    shutil.move(str(found[0]), target)
    folder = found[0].with_suffix("")
    if folder.is_dir():
        shutil.move(str(folder), destination / folder.name)
    return target


def _invoke(command: list[str], cwd: Path, timeout: float) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=timeout)


def _git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=True)
    return result.stdout


def _claude_version(claude: str) -> str | None:
    try:
        return subprocess.run([claude, "--version"], capture_output=True, text=True, timeout=30).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _result_fields(stdout: str) -> dict:
    try:
        data = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {key: data.get(key) for key in ("is_error", "num_turns", "total_cost_usd", "duration_ms")}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def run_variant(
    spec: RunSpec,
    runs: int,
    out: Path,
    projects_dir: Path,
    workdir: Path | None = None,
    invoke: Invoke = _invoke,
    version: str | None = None,
) -> list[dict]:
    """Run one variant `runs` times and return the run records also appended to out/runs.jsonl.

    @doc: docs/design/Study.md#2-실행-기록-생성-m9-t2
    """
    if not STUDY_NAME_PATTERN.fullmatch(spec.name):
        raise ValueError(f"변형 이름은 영문자·숫자·_·- 1~64자여야 함: {spec.name!r}")
    workdir = workdir or Path(tempfile.gettempdir()) / "agentvis-study"
    version = version if version is not None else _claude_version(spec.claude)
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for run in range(1, runs + 1):
        work = workdir / f"{spec.name}-{run}"
        if work.exists():
            shutil.rmtree(work)
        work.parent.mkdir(parents=True, exist_ok=True)
        _git("clone", "--quiet", spec.repo, str(work))
        _git("checkout", "--quiet", spec.commit, cwd=work)
        session_id = str(uuid.uuid4())
        started = _now()
        timed_out, exit_code, fields = False, None, {}
        try:
            completed = invoke(claude_command(spec, session_id), work, spec.timeout)
            exit_code, fields = completed.returncode, _result_fields(completed.stdout)
        except subprocess.TimeoutExpired:
            timed_out = True
        transcript = collect_transcript(projects_dir, session_id, out / spec.name)
        _git("add", "-A", cwd=work)
        (out / spec.name).mkdir(parents=True, exist_ok=True)
        (out / spec.name / f"{session_id}.diff").write_text(_git("diff", "--cached", "--", ".", *DIFF_EXCLUDES, cwd=work), encoding="utf-8")
        record = {
            "name": spec.name, "run": run, "session_id": session_id, "repo": spec.repo, "commit": spec.commit,
            "model": spec.model, "claude_version": version, "started_at": started, "ended_at": _now(),
            "exit_code": exit_code, "timed_out": timed_out,
            "transcript": transcript.relative_to(out).as_posix() if transcript else None,
            **{key: fields.get(key) for key in ("is_error", "num_turns", "total_cost_usd", "duration_ms")},
        }
        with (out / "runs.jsonl").open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
        records.append(record)
    return records
