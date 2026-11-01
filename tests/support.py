"""Shared fixtures for tests that build a throwaway repository.

@doc: docs/VerificationTools.md#5-테스트
"""

import tempfile
import unittest
from pathlib import Path


class RepoTestCase(unittest.TestCase):
    """A test case with a fresh temporary repository root per test.

    @doc: docs/VerificationTools.md#5-테스트
    """

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path
