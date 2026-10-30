"""The ``agentvis`` command line entry point.

@doc: docs/design/Cli.md#1-패키지-골격
@doc: docs/design/Cli.md#21-serve
"""

import argparse
import sys

import uvicorn

from agentvis import __version__
from agentvis.server import create_app
from agentvis.store import EventStore, default_db_path

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
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run the requested command; return the exit code.

    @doc: docs/design/Cli.md#1-패키지-골격
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
