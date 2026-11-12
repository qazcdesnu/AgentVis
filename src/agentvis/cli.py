"""The ``agentvis`` command line entry point.

@doc: docs/design/Cli.md#1-패키지-골격
@doc: docs/design/Cli.md#21-serve
@doc: docs/design/Cli.md#22-experiment
@doc: docs/design/Cli.md#34-hooks-명령
"""

import argparse
import re
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
from agentvis.server import create_app
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
            print(f"데이터 디렉터리: {directory}")
            print(f"AgentVis 버전: {__version__}", flush=True)
            _run_server(create_app(store, reader, collect_hooks=False), _HOST, args.port)
        finally:
            reader.stop()
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
