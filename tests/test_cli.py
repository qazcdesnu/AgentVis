"""Tests for the agentvis command line entry point.

@doc: docs/design/Cli.md#4-테스트
"""

import io
import tomllib
import unittest
from contextlib import redirect_stdout

from agentvis import __version__
from agentvis.cli import main
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


if __name__ == "__main__":
    unittest.main()
