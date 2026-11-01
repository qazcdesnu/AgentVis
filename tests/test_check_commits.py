"""Tests for the commit message checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import io
import subprocess
import unittest
from contextlib import redirect_stdout
from unittest import mock

from tests.support import RepoTestCase
from tools import check_commits
from tools.check_commits import check_branch, check_message, commit_messages, main, parse_subject

_STATUSES = {"M1-T1": "x", "M1-T2": "~", "M1-T3": " ", "I4": "x"}
_ROADMAP = "# 로드맵\n\n## M0 기반\n\n- [x] M0-T1 시작\n- [~] M0-T2 진행\n- [ ] M0-T3 예정\n"
_ISSUE = "# 이슈\n\n- [x] I1 지시\n"


class CheckMessageTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_valid_messages_pass(self) -> None:
        message = "M1-T1, I4: 저장소 구현\n\n본문.\n\nCo-Authored-By: A <a@b.c>\n# git 주석\n"
        self.assertEqual(check_message(message, _STATUSES, True), [])
        self.assertEqual(parse_subject("M1-T2: 요약"), (["M1-T2"], "요약"))

    def test_reports_format_problems(self) -> None:
        self.assertEqual(check_message("# 주석만\n", _STATUSES, False), ["빈 커밋 메시지"])
        self.assertIn("제목 형식 오류", check_message("M0, I1-I5: 범위", _STATUSES, False)[0])
        self.assertIn("제목 형식 오류", check_message("M1-T1:요약", _STATUSES, False)[0])
        problems = check_message("M1-T1: " + "가" * 80 + ".\n본문", _STATUSES, False)
        self.assertEqual(len(problems), 3)
        self.assertIn("72자를 넘음", problems[0])
        self.assertIn("비어 있어야 함", problems[1])
        self.assertIn("마침표", problems[2])

    def test_reports_unknown_repeated_and_unstarted_ids(self) -> None:
        problems = check_message("M1-T1, M1-T1, M9-T9, M1-T3: 요약", _STATUSES, True)
        self.assertIn("제목에 같은 작업 ID가 반복됨: M1-T1", problems)
        self.assertIn("로드맵·이슈에 없는 작업 ID: M9-T9", problems)
        self.assertIn("시작하지 않은 작업([ ])의 ID: M1-T3", problems)
        self.assertNotIn("시작하지 않은 작업([ ])의 ID: M1-T3", check_message("M1-T3: 요약", _STATUSES, False))


class CheckBranchTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_branch_names(self) -> None:
        self.assertEqual(check_branch("m1-t2-store", _STATUSES), [])
        self.assertEqual(check_branch("i4-pr-rules2", _STATUSES), [])
        for name in ("main", "feature/x", "M1-T2-store", "m1-t2", "m1-t2-Store", "m1-t2_store"):
            with self.subTest(name=name):
                self.assertIn("형식 오류", check_branch(name, _STATUSES)[0])
        self.assertEqual(check_branch("m9-t9-x", _STATUSES), ["로드맵·이슈에 없는 작업 ID의 브랜치: M9-T9"])


class CommitHistoryTest(RepoTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("docs/Roadmap.md", _ROADMAP)
        self.write("docs/Issue.md", _ISSUE)
        self.git("init", "-q", "-b", "main")
        self.base = self.commit("규칙 이전 커밋")

    def git(self, *args: str) -> str:
        command = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args]
        return subprocess.run(command, cwd=self.root, capture_output=True, encoding="utf-8", check=True).stdout.strip()

    def commit(self, message: str) -> str:
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "--short", "HEAD")

    def run_checker(self, *args: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root), *args])
        return code, output.getvalue()

    def test_history_after_baseline_skips_merges(self) -> None:
        good = self.commit("M0-T1: 첫 작업")
        self.git("checkout", "-q", "-b", "side")
        self.commit("M0-T2: 곁가지 작업")
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "Merge branch side", "side")
        hashes = [short_hash for short_hash, _ in commit_messages(self.root, f"{self.base}..HEAD")]
        self.assertIn(good, hashes)
        self.assertEqual(len(hashes), 2)
        with mock.patch.object(check_commits, "BASELINE_COMMIT", self.base):
            code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_history_reports_bad_commit(self) -> None:
        bad = self.commit("작업 ID 없는 커밋")
        with mock.patch.object(check_commits, "BASELINE_COMMIT", self.base):
            code, output = self.run_checker()
        self.assertEqual(code, 1)
        self.assertIn(f"commit {bad}:1: 제목 형식 오류", output)

    def test_missing_baseline_is_reported(self) -> None:
        with mock.patch.object(check_commits, "BASELINE_COMMIT", "0000000"):
            code, output = self.run_checker()
        self.assertEqual(code, 1)
        self.assertIn("git log 실패", output)

    def test_pr_subject_and_branch(self) -> None:
        self.assertEqual(self.run_checker("--subject", "M0-T2: 진행 중 작업 (#3)", "--branch", "m0-t2-work")[0], 0)
        code, output = self.run_checker("--subject", "M0-T3: 예정 작업", "--branch", "feature")
        self.assertEqual(code, 1)
        self.assertIn("PR:1: PR 제목: 시작하지 않은 작업([ ])의 ID: M0-T3", output)
        self.assertIn("브랜치 이름 형식 오류", output)

    def test_message_file_requires_started_work(self) -> None:
        message = self.write("MSG", "M0-T3: 예정 작업\n")
        code, output = self.run_checker("--message-file", str(message))
        self.assertEqual(code, 1)
        self.assertIn("시작하지 않은 작업([ ])의 ID: M0-T3", output)
        self.write("MSG", "M0-T2, I1: 진행 중 작업\n")
        self.assertEqual(self.run_checker("--message-file", str(message))[0], 0)


if __name__ == "__main__":
    unittest.main()
