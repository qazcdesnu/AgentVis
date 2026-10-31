"""Tests for the pull request order checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import io
import json
import subprocess
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from tools.check_pr_order import main, missing_earlier_prs


class CheckPrOrderTest(RepoTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def git(self, *args: str) -> str:
        command = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args]
        return subprocess.run(command, cwd=self.root, capture_output=True, encoding="utf-8", check=True).stdout.strip()

    def commit(self, name: str) -> str:
        self.write(f"{name}.txt", name)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", name)
        return self.git("rev-parse", "HEAD")

    def setUp(self) -> None:
        super().setUp()
        self.git("init", "-q", "-b", "main")
        self.commit("base")
        self.git("switch", "-q", "-c", "i1-first")
        self.first = self.commit("first")
        self.git("switch", "-q", "-c", "i2-stacked")
        self.second = self.commit("second")
        self.git("switch", "-q", "-c", "i3-from-main", "main")
        self.third = self.commit("third")
        self.prs = [
            {"number": 1, "headRefName": "i1-first", "headRefOid": self.first},
            {"number": 2, "headRefName": "i2-stacked", "headRefOid": self.second},
            {"number": 3, "headRefName": "i3-from-main", "headRefOid": self.third},
            {"number": 4, "headRefName": "i4-gone", "headRefOid": "0" * 40},
        ]

    def test_stacked_branch_contains_earlier_prs(self) -> None:
        self.git("switch", "-q", "i2-stacked")
        self.assertEqual(missing_earlier_prs(self.root, self.prs, 2), [])

    def test_branch_from_main_misses_earlier_prs_and_later_prs_are_ignored(self) -> None:
        self.git("switch", "-q", "i3-from-main")
        self.assertEqual([pr["number"] for pr in missing_earlier_prs(self.root, self.prs, 3)], [1, 2])
        self.assertEqual(missing_earlier_prs(self.root, self.prs, 1), [])

    def test_unknown_commit_counts_as_missing_and_main_reports(self) -> None:
        self.git("switch", "-q", "i2-stacked")
        listing = self.write("open-prs.json", json.dumps(self.prs))
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root), "--pr", "5", "--open-prs", str(listing)])
        self.assertEqual(code, 1)
        self.assertIn("PR #5:1: PR #3 (i3-from-main)를 포함하지 않음", output.getvalue())
        self.assertIn("PR #4 (i4-gone)를 포함하지 않음", output.getvalue())
        self.assertNotIn("PR #1 ", output.getvalue())
