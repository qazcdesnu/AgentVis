"""Tests for the answer key checker of the experiment material tools.

@doc: docs/design/Study.md#6-테스트
"""

import io
import json
from contextlib import redirect_stdout

from agentvis.cli import main
from agentvis.study.key import check_key, key_summary
from tests.support import RepoTestCase

_INSTRUCTION = "`total`이 틀립니다. `invoice.py`의 `round` 처리를 고쳐 주세요."


class KeyTest(RepoTestCase):
    """@doc: docs/design/Study.md#6-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.folder = self.root / "scenario"
        lines = [
            {"type": "user", "uuid": "u1", "message": {"role": "user", "content": _INSTRUCTION}},
            {"type": "assistant", "uuid": "a1", "message": {"content": [{"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {}}]}},
        ]
        for session in ("s1", "s2"):
            self.write(f"scenario/toy-e2/{session}.jsonl", "".join(json.dumps(line) + "\n" for line in lines))
        self.trials = [
            {"id": "t1", "use": "trial", "variant": "toy-e2", "session_id": "s1", "error_type": "E2",
             "original_text": "`discount.py`", "perturbed_text": "`invoice.py`의 `round` 처리",
             "response": "worked_around", "first_notice": "toolu_1"},
            {"id": "t2", "use": "trial", "variant": "toy-e2", "session_id": "s2", "error_type": "none",
             "original_text": None, "perturbed_text": None, "response": "followed", "first_notice": None},
        ]

    def save(self, trials: object) -> None:
        self.write("scenario/key.json", json.dumps({"version": 1, "trials": trials}, ensure_ascii=False))

    def test_a_sound_key_has_no_problems_and_a_balance_table(self) -> None:
        self.save(self.trials)
        self.assertEqual(check_key(self.folder), [])
        summary = key_summary(self.folder)
        self.assertIn("[trial] 시행 2개", summary)
        self.assertRegex(summary, r"E2\s+0\s+0\s+1\s+0")
        self.assertRegex(summary, r"none\s+1\s+0\s+0\s+0")

    def test_each_rule_is_reported(self) -> None:
        cases = {
            "기록 파일 없음": {"session_id": "missing"},
            "'response'는": {"response": "maybe"},
            "'perturbed_text'가 기록의 지시에 없음": {"perturbed_text": "다른 문장"},
            "'first_notice'가 기록의": {"first_notice": "toolu_9"},
        }
        for expected, change in cases.items():
            with self.subTest(expected=expected):
                self.save([{**self.trials[0], **change}])
                self.assertTrue(any(expected in problem for problem in check_key(self.folder)), check_key(self.folder))
        self.save([{**self.trials[1], "perturbed_text": "x"}])
        self.assertTrue(any("통제 시행" in problem for problem in check_key(self.folder)))
        self.save([{**self.trials[1], "first_notice": "toolu_1"}])
        self.assertTrue(any("'followed'" in problem for problem in check_key(self.folder)))
        self.save([self.trials[0], self.trials[0]])
        self.assertTrue(any("'id'가 겹침" in problem for problem in check_key(self.folder)))

    def test_broken_files_are_one_problem(self) -> None:
        self.write("scenario/key.json", "not json")
        self.assertEqual(len(check_key(self.folder)), 1)
        self.write("scenario/key.json", '{"trials": {}}')
        self.assertEqual(check_key(self.folder), ["key.json의 'trials'가 목록이 아님"])

    def test_command_exit_codes(self) -> None:
        self.save(self.trials)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["study", "check-key", str(self.folder)]), 0)
        self.save([{**self.trials[0], "response": "maybe"}])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["study", "check-key", str(self.folder)]), 1)
