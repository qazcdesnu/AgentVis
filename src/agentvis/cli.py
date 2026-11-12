"""The ``agentvis`` command line entry point.

@doc: docs/design/Cli.md#1-패키지-골격
@doc: docs/design/Cli.md#21-serve
@doc: docs/design/Cli.md#22-experiment
@doc: docs/design/Cli.md#34-hooks-명령
@doc: docs/design/Cli.md#23-study
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

from agentvis import __version__
from agentvis.hook_settings import (
    SettingsError,
    backup_settings,
    default_settings_path,
    hook_url,
    install_hooks,
    load_settings,
    save_settings,
    uninstall_hooks,
)
from agentvis.interaction import InteractionLog
from agentvis.server import create_app
from agentvis.study.key import check_key, key_summary
from agentvis.study.runner import STUDY_TIMEOUT_SECONDS, RunSpec, run_variant
from agentvis.store import EventStore, data_dir, default_db_path, experiment_dir
from agentvis.transcript import TranscriptReader, default_projects_dir, find_unread_transcripts

# @doc: docs/design/Cli.md#21-serve
DEFAULT_PORT = 8765
_HOST = "127.0.0.1"
# Open live-update streams would otherwise keep the server from stopping on Ctrl+C.
# @doc: docs/design/Cli.md#2-명령
SHUTDOWN_GRACE_SECONDS = 3
# Participant numbers become directory names, so they may not hold separators or dots.
# @doc: docs/design/Cli.md#22-experiment
PARTICIPANT_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,32}")
# @doc: docs/design/Cli.md#22-experiment
EXPERIMENT_READ_SECONDS = 300


def _port(value: str) -> int:
    port = int(value)
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError(f"포트는 1~65535 사이여야 함: {value}")
    return port


class _StoppingServer(uvicorn.Server):
    """A uvicorn server that marks the app as stopping before it waits for connections to close.

    @doc: docs/design/Cli.md#2-명령
    """

    def handle_exit(self, sig: int, frame: object) -> None:
        self.config.app.state.stopping = True
        super().handle_exit(sig, frame)


def _run_server(app: FastAPI, host: str, port: int) -> None:
    """Run the app until it is stopped; live-update streams end on their own when it stops.

    @doc: docs/design/Cli.md#2-명령
    """
    config = uvicorn.Config(app, host=host, port=port, timeout_graceful_shutdown=SHUTDOWN_GRACE_SECONDS)
    _StoppingServer(config).run()


def _serve(args: argparse.Namespace) -> int:
    path = default_db_path()
    with EventStore(path) as store:
        reader = TranscriptReader(store, default_projects_dir())
        reader.start()
        try:
            # Sessions that ran while the server was down send no more hooks, so look for them now (M2-T4).
            missed = find_unread_transcripts(store, default_projects_dir())
            for missed_path in missed:
                reader.request(missed_path)
            print(f"AgentVis 서버: http://{_HOST}:{args.port}")
            print(f"놓친 세션 기록: {len(missed)}개 파일")
            print(f"데이터베이스: {path}", flush=True)
            _run_server(create_app(store, reader), _HOST, args.port)
        finally:
            reader.stop()
    return 0


def _participant(value: str) -> str:
    if not PARTICIPANT_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError(f"참가자 번호는 영문자·숫자·_·- 1~32자여야 함: {value!r}")
    return value


def _experiment(args: argparse.Namespace) -> int:
    """Serve only the scenario transcripts in args.transcripts, storing into the participant's directory.

    @doc: docs/design/Cli.md#22-experiment
    """
    transcripts = args.transcripts.expanduser()
    if not transcripts.is_dir():
        print(f"오류: 시나리오 세션 기록 폴더가 없음: {transcripts}", file=sys.stderr)
        return 1
    if not any(transcripts.glob("*/*.jsonl")):
        print(f"오류: 폴더에 세션 기록(<프로젝트 폴더>/<세션>.jsonl)이 없음: {transcripts}", file=sys.stderr)
        return 1
    directory = experiment_dir(args.participant)
    with EventStore(directory / "agentvis.db") as store:
        reader = TranscriptReader(store, transcripts)
        reader.start()
        try:
            files = find_unread_transcripts(store, transcripts, everything=True)
            for path in files:
                reader.request(path)
            if not reader.wait_until_idle(EXPERIMENT_READ_SECONDS):
                print("경고: 시나리오 세션 기록을 다 읽기 전에 서버를 시작함", file=sys.stderr)
            print(f"AgentVis 실험 모드: 참가자 {args.participant}")
            print(f"AgentVis 서버: http://{_HOST}:{args.port}")
            print(f"시나리오 세션 기록: {len(files)}개 파일")
            log = InteractionLog(directory / "interactions.jsonl", args.participant)
            print(f"데이터 디렉터리: {directory}")
            print(f"화면 사용 기록: {log.path}")
            print(f"AgentVis 버전: {__version__}", flush=True)
            _run_server(create_app(store, reader, collect_hooks=False, interaction_log=log), _HOST, args.port)
        finally:
            reader.stop()
    return 0


def _study_run(args: argparse.Namespace) -> int:
    """Run Claude Code on one instruction variant and collect the transcripts.

    @doc: docs/design/Study.md#2-실행-기록-생성-m9-t2
    """
    try:
        instruction = args.instruction.read_text(encoding="utf-8")
    except OSError as error:
        print(f"오류: 지시 파일을 읽을 수 없음: {error}", file=sys.stderr)
        return 1
    spec = RunSpec(
        repo=args.repo, commit=args.commit, instruction=instruction, name=args.name, model=args.model,
        max_budget_usd=args.max_budget_usd, timeout=args.timeout, claude=args.claude,
    )
    try:
        records = run_variant(spec, args.runs, args.out, default_projects_dir(), args.workdir)
    except (ValueError, subprocess.CalledProcessError) as error:
        print(f"오류: {error}", file=sys.stderr)
        return 1
    for record in records:
        print(f"{record['name']} #{record['run']}: {record['transcript'] or '기록 없음'} "
              f"(종료 코드 {record['exit_code']}, 비용 {record['total_cost_usd']})")
    failed = sum(1 for record in records if record["transcript"] is None)
    print(f"실행 {len(records)}회, 기록 없음 {failed}회, 실행 정보: {args.out / 'runs.jsonl'}")
    return 1 if failed else 0


def _study_check_key(args: argparse.Namespace) -> int:
    """Check a scenario folder's answer key and print its balance table.

    @doc: docs/design/Study.md#3-정답표-m9-t3
    """
    problems = check_key(args.folder)
    for problem in problems:
        print(problem)
    if problems:
        print(f"정답표 문제 {len(problems)}건")
        return 1
    print(key_summary(args.folder))
    return 0


def _apply_settings_change(path: Path, change: str, port: int | None) -> int:
    try:
        settings = load_settings(path)
        if change == "install":
            updated, count = install_hooks(settings, port)
        else:
            updated, count = uninstall_hooks(settings)
    except SettingsError as error:
        print(f"오류: {error}", file=sys.stderr)
        return 1
    print(f"설정 파일: {path}")
    if updated == settings:
        print("변경 없음" if change == "install" else "제거할 AgentVis hook 없음")
        return 0
    backup = backup_settings(path, data_dir() / "backups")
    save_settings(path, updated)
    print(f"백업: {backup if backup else '없음(새 파일)'}")
    if change == "install":
        print(f"추가한 hook: {count}개 ({hook_url(port)})")
    else:
        print(f"제거한 hook: {count}개")
    return 0


def _hooks_install(args: argparse.Namespace) -> int:
    return _apply_settings_change(args.settings or default_settings_path(), "install", args.port)


def _hooks_uninstall(args: argparse.Namespace) -> int:
    return _apply_settings_change(args.settings or default_settings_path(), "uninstall", None)


def _print_help(parser: argparse.ArgumentParser) -> int:
    parser.print_help()
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentvis",
        description="Claude Code 에이전트의 작업 과정을 수집하고 시각화한다.",
    )
    parser.add_argument("--version", action="version", version=f"agentvis {__version__}")
    commands = parser.add_subparsers(dest="command")
    serve = commands.add_parser("serve", help=f"로컬 서버를 {_HOST}에서 실행한다.")
    serve.add_argument("--port", type=_port, default=DEFAULT_PORT, help=f"포트 (기본 {DEFAULT_PORT})")
    serve.set_defaults(handler=_serve)

    experiment = commands.add_parser("experiment", help="실험 모드: 시나리오 세션 기록만 읽어 참가자별로 저장하고 서버를 실행한다.")
    experiment.add_argument("participant", type=_participant, help="참가자 번호 (영문자·숫자·_·- 1~32자)")
    experiment.add_argument("--transcripts", type=Path, required=True, help="시나리오 세션 기록 폴더 (<프로젝트 폴더>/<세션>.jsonl)")
    experiment.add_argument("--port", type=_port, default=DEFAULT_PORT, help=f"포트 (기본 {DEFAULT_PORT})")
    experiment.set_defaults(handler=_experiment)

    study = commands.add_parser("study", help="연구 설계 2의 실험 자료를 만든다.")
    study.set_defaults(handler=lambda _: _print_help(study))
    study_commands = study.add_subparsers(dest="study_command")
    run = study_commands.add_parser("run", help="지시 변형으로 Claude Code를 실행해 실행 기록을 모은다.")
    run.add_argument("--repo", required=True, help="원본 과제 저장소 (경로 또는 URL)")
    run.add_argument("--commit", required=True, help="작업을 시작할 커밋")
    run.add_argument("--instruction", type=Path, required=True, help="지시 파일 (UTF-8 텍스트)")
    run.add_argument("--name", required=True, help="변형 이름 (영문자·숫자·_·-)")
    run.add_argument("--out", type=Path, required=True, help="결과 폴더 (실험 모드의 --transcripts)")
    run.add_argument("--runs", type=int, default=1, help="실행 회수 (기본 1)")
    run.add_argument("--model", default=None, help="모델 (실험 내내 고정)")
    run.add_argument("--max-budget-usd", type=float, default=None, help="회차마다 최대 비용")
    run.add_argument("--timeout", type=float, default=STUDY_TIMEOUT_SECONDS, help=f"회차마다 최대 시간(초, 기본 {STUDY_TIMEOUT_SECONDS})")
    run.add_argument("--workdir", type=Path, default=None, help="작업 사본을 둘 폴더 (기본: 임시 폴더/agentvis-study)")
    run.add_argument("--claude", default="claude", help="Claude Code 실행 파일 (기본 claude)")
    run.set_defaults(handler=_study_run)
    check = study_commands.add_parser("check-key", help="시나리오 폴더의 정답표(key.json)를 검사한다.")
    check.add_argument("folder", type=Path, help="시나리오 폴더")
    check.set_defaults(handler=_study_check_key)

    hooks = commands.add_parser("hooks", help="Claude Code 설정에 AgentVis hook을 설치하거나 제거한다.")
    hooks.set_defaults(handler=lambda _: _print_help(hooks))
    hook_commands = hooks.add_subparsers(dest="hooks_command")
    settings_help = "Claude Code 설정 파일 (기본 ~/.claude/settings.json)"
    install = hook_commands.add_parser("install", help="AgentVis hook을 설치한다.")
    install.add_argument("--port", type=_port, default=DEFAULT_PORT, help=f"수집 서버 포트 (기본 {DEFAULT_PORT})")
    install.add_argument("--settings", type=Path, default=None, help=settings_help)
    install.set_defaults(handler=_hooks_install)
    uninstall = hook_commands.add_parser("uninstall", help="AgentVis hook만 제거한다.")
    uninstall.add_argument("--settings", type=Path, default=None, help=settings_help)
    uninstall.set_defaults(handler=_hooks_uninstall)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run the requested command; return the exit code.

    @doc: docs/design/Cli.md#1-패키지-골격
    """
    # Windows prints through its legacy code page when output is piped, which cannot encode Korean.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        return _print_help(parser)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
