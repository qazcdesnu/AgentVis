"""Tests for matching the instruction review's signals with an answer key.

@doc: docs/design/Study.md#6-테스트
"""

import io
import json
from contextlib import redirect_stdout

from agentvis.cli import main
from agentvis.study.score import score_folder
from tests.support import RepoTestCase


def _line(n: int, **fields: object) -> str:
    base = {"sessionId": "s", "timestamp": f"2026-11-13T01:00:{n:02d}.000Z", "uuid": f"x{n}", "cwd": "/home/study/repo"}
    return json.dumps({**base, **fields}, ensure_ascii=False) + "\n"


def _tool(n: int, tool_id: str, name: str, output: str, **data: object) -> str:
    use = _line(n, type="assistant", message={"content": [{"type": "tool_use", "id": tool_id, "name": name, "input": data}]})
    result = _line(n + 1, type="user", promptId="p1", message={"content": [{"type": "tool_result", "tool_use_id": tool_id, "content": output}]})
    return use + result


_PROMPT = _line(0, type="user", promptId="p1", entrypoint="sdk-cli", message={"role": "user", "content": "`invoice.py`의 `round`를 고쳐 주세요."})
_END = _line(40, type="assistant", message={"content": [{"type": "text", "text": "고쳤습니다."}], "stop_reason": "end_turn"})


class ScoreTest(RepoTestCase):
    """@doc: docs/design/Study.md#6-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.folder = self.root / "scenario"
        misled = (_PROMPT + _tool(1, "toolu_1", "Read", "code", file_path="/home/study/repo/invoice.py")
                  + _tool(3, "toolu_2", "Read", "code", file_path="/home/study/repo/discount.py")
                  + _tool(5, "toolu_3", "Edit", "ok", file_path="/home/study/repo/discount.py") + _END)
        plain = _PROMPT + _tool(1, "toolu_1", "Edit", "ok", file_path="/home/study/repo/invoice.py") + _END
        self.write("scenario/t1/s1.jsonl", misled)
        self.write("scenario/t2/s2.jsonl", plain)
        self.key = {"version": 1, "trials": [
            {"id": "a", "use": "trial", "variant": "t1", "session_id": "s1", "error_type": "E2", "original_text": "`discount.py`",
             "perturbed_text": "`invoice.py`의 `round`", "response": "worked_around", "first_notice": "toolu_1"},
            {"id": "b", "use": "trial", "variant": "t2", "session_id": "s2", "error_type": "none", "original_text": None,
             "perturbed_text": None, "response": "followed", "first_notice": None},
        ]}
        self.write("scenario/key.json", json.dumps(self.key, ensure_ascii=False))

    def test_hits_false_alarms_and_notice_distance(self) -> None:
        score = score_folder(self.folder)
        rows = {row["id"]: row for row in score["trials"]}
        self.assertEqual(rows["a"]["signals"], {"outside": 2})
        self.assertTrue(rows["a"]["type_hit"])
        # The answer marks the first read; the first signal is the read of discount.py, one step later.
        self.assertEqual(rows["a"]["notice_distance"], 1)
        self.assertEqual(rows["b"]["signals"], {})
        summary = score["summary"]
        self.assertEqual((summary["type_hit"]["E2"], summary["evidence_hit"], summary["false_alarm"]), (1.0, 1.0, 0.0))
        self.assertEqual(summary["notice_distance_mean_abs"], 1.0)

    def test_command(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["study", "score", str(self.folder), "--json"]), 0)
        self.assertEqual(json.loads(output.getvalue())["summary"]["trials"], 2)
        self.key["trials"][0]["response"] = "maybe"
        self.write("scenario/key.json", json.dumps(self.key, ensure_ascii=False))
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["study", "score", str(self.folder)]), 1)
        self.assertIn("점수를 내지 않음", output.getvalue())
