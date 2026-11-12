"""Tests for the rules that identify test runs, test file changes and completion reports.

@doc: docs/design/Analysis.md#9-테스트
"""

import unittest

from agentvis.analysis.identify import completion_sentences, failed_tests, is_test_path, test_command, test_outcome, written_paths


class TestCommandTest(unittest.TestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def test_runners_are_found_in_any_part_of_the_command(self) -> None:
        self.assertEqual(test_command("uv run python -m unittest discover -s tests -t ."), {"clipped": False})
        self.assertEqual(test_command("cd backend && uv run pytest -q 2>&1 | tail -15"), {"clipped": True})
        self.assertEqual(test_command("CI=1 npm run test"), {"clipped": False})
        self.assertEqual(test_command("go test ./... || echo done"), {"clipped": False})
        self.assertIsNone(test_command("git status && grep -rn pytest docs"))
        self.assertIsNone(test_command("pytesting --help"))

    def test_heredoc_bodies_are_not_commands(self) -> None:
        command = "python3 - <<'EOF'\nimport subprocess\npytest = 1\nEOF\ngit diff"
        self.assertIsNone(test_command(command))
        self.assertEqual(test_command("cat > a.txt <<EOF\nx\nEOF\npytest -q"), {"clipped": False})


class TestOutcomeTest(unittest.TestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def test_each_runner_summary(self) -> None:
        self.assertEqual(test_outcome("....\nFAILED tests/a.py::t - x\n2 failed, 68 passed in 0.65s"), ("fail", "2 failed, 68 passed"))
        self.assertEqual(test_outcome("===== 147 passed in 2.66s ====="), ("pass", "147 passed"))
        self.assertEqual(test_outcome("Ran 17 tests in 4.309s\n\nFAILED (failures=8)"), ("fail", "Ran 17 tests · FAILED (failures=8)"))
        self.assertEqual(test_outcome("Ran 145 tests in 1.4s\n\nOK"), ("pass", "Ran 145 tests · OK"))
        self.assertEqual(test_outcome("ok  \texample.com/a\t0.1s\n--- FAIL: TestB\nFAIL\texample.com/b"), ("fail", "FAIL\texample.com/b"))
        self.assertEqual(test_outcome("test result: ok. 3 passed; 0 failed; 0 ignored"), ("pass", "test result: ok. 3 passed; 0 failed; 0 ignored"))
        self.assertEqual(test_outcome("Tests:       1 failed, 5 passed, 6 total"), ("fail", "1 failed, 5 passed, 6 total"))
        self.assertEqual(test_outcome("check_docs: 통과\nOK"), ("pass", "OK"))
        self.assertEqual(test_outcome("FAILED (failures=1, errors=2)"), ("fail", "FAILED (failures=1, errors=2)"))
        self.assertEqual(test_outcome("no summary here"), (None, None))

    def test_any_failing_summary_wins(self) -> None:
        self.assertEqual(test_outcome("Ran 3 tests in 0s\n\nFAILED (errors=1)\n...\n5 passed in 1s")[0], "fail")


class FailedTestsTest(unittest.TestCase):
    """@doc: docs/design/ReviewView.md#5-테스트"""

    def test_names_from_each_runner(self) -> None:
        text = "FAILED tests/a.py::test_x - E\nFAILED tests/a.py::test_x - E\nFAIL: test_c (tests.t.T.test_c)\nERROR: test_b (tests.t.C)\n    --- FAIL: TestGo (0.00s)"
        self.assertEqual(failed_tests(text), ["tests/a.py::test_x", "tests.t.T.test_c", "tests.t.C.test_b", "TestGo"])
        self.assertEqual(failed_tests("Ran 3 tests\n\nOK"), [])


class TestPathTest(unittest.TestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def test_paths_are_judged_inside_the_project(self) -> None:
        self.assertTrue(is_test_path("/Users/me/app/tests/test_cart.py", "/Users/me/app"))
        self.assertTrue(is_test_path("src/cart.test.ts"))
        self.assertTrue(is_test_path("pkg/cart_test.go"))
        self.assertTrue(is_test_path("C:\\work\\app\\__tests__\\cart.js", "C:\\work\\app"))
        self.assertFalse(is_test_path("/home/u/test/app/src/cart.py", "/home/u/test/app"))
        self.assertFalse(is_test_path("src/contest.py"))

    def test_bash_write_targets(self) -> None:
        self.assertEqual(written_paths("cat > tests/test_a.py <<'EOF'\nx > tests/other.py\nEOF"), ["tests/test_a.py"])
        self.assertEqual(written_paths("pytest 2>&1 | tee out.log > /dev/null"), ["out.log"])
        self.assertEqual(written_paths("sed -i '' 's/a/b/' tests/test_b.py"), ["tests/test_b.py"])
        script = "uv run python - <<'EOF'\nfrom pathlib import Path\np = Path(\"tests/test_c.py\")\np.write_text(p.read_text())\nEOF"
        self.assertEqual(written_paths(script), ["tests/test_c.py"])
        self.assertEqual(written_paths("python3 - <<'EOF'\nprint(open('tests/test_d.py').read())\nEOF"), [])


class CompletionSentenceTest(unittest.TestCase):
    """@doc: docs/design/Analysis.md#9-테스트"""

    def test_reports_are_sentences_of_finished_work(self) -> None:
        text = "\n".join([
            "## 요약",
            "- **로그인 화면을 추가했습니다.** 다음은 무엇을 할까요?",
            "- 테스트 12개가 모두 통과합니다.",
            "완료 보고가 무엇인지 정리합니다.",
            "- 결제 테스트는 아직 고치지 못했습니다.",
            "| 파일 | 완료 |",
            "```",
            "done",
            "```",
            "All tests pass. I fixed the cart bug.",
        ])
        self.assertEqual(completion_sentences(text), ["로그인 화면을 추가했습니다.", "테스트 12개가 모두 통과합니다.", "All tests pass.", "I fixed the cart bug."])


if __name__ == "__main__":
    unittest.main()
