"""The ``agentvis`` command line entry point.

@doc: docs/design/Cli.md#1-패키지-골격
@doc: docs/design/Cli.md#21-serve
@doc: docs/design/Cli.md#34-hooks-명령
"""

import argparse
import sys
from pathlib import Path

import uvicorn

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
from agentvis.store import EventStore, data_dir, default_db_path

# @doc: docs/design/Cli.md#21-serve
DEFAULT_PORT = 8765
_HOST = "127.0.0.1"


def _port(value: str) -> int:
    port = int(value)
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError(f"포트는 1~65535 사이여야 함: {value}")
    return port


def _serve(args: argparse.Namespace) -> int:
    path = default_db_path()
    with EventStore(path) as store:
        print(f"AgentVis 서버: http://{_HOST}:{args.port}")
        print(f"데이터베이스: {path}", flush=True)
        uvicorn.run(create_app(store), host=_HOST, port=args.port)
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
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        return _print_help(parser)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
