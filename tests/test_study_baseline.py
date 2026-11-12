"""Tests for the baseline text view of the experiment material tools.

@doc: docs/design/Study.md#6-테스트
"""

import io
import json
from contextlib import redirect_stdout

from agentvis.cli import main
from agentvis.study.baseline import FOLD_LINES, render_transcript
from tests.support import RepoTestCase

_T = "2026-11-13T01:00:00.000Z"
_RECORDS = [
    {"type": "user", "timestamp": _T, "message": {"role": "user", "content": "`invoice.py`를 고쳐 주세요 <script>alert(1)</script>"}},
    {"type": "assistant", "timestamp": _T, "message": {"content": [{"type": "thinking", "thinking": ""}]}},
    {"type": "assistant", "timestamp": _T, "message": {"content": [{"type": "text", "text": "먼저 봅니다."}]}},
    {"type": "assistant", "timestamp": _T, "message": {"content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "cat invoice.py"}}]}},
    {"type": "user", "timestamp": _T, "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": "def total(): ..."}]}},
    {"type": "assistant", "timestamp": _T, "message": {"content": [{"type": "tool_use", "id": "t2", "name": "Edit",
        "input": {"file_path": "discount.py", "old_string": "get(code", "new_string": "get(code.upper()"}}]}},
    {"type": "user", "timestamp": _T, "message": {"content": [{"type": "tool_result", "tool_use_id": "t2", "content": "Exit code 1", "is_error": True}]}},
    {"type": "system", "subtype": "turn_duration", "timestamp": _T},
    {"type": "user", "timestamp": _T, "message": {"content": [{"type": "tool_result", "tool_use_id": "t3",
        "content": "\n".join(f"line {n}" for n in range(FOLD_LINES + 5))}]}},
]


class BaselineTest(RepoTestCase):
    """@doc: docs/design/Study.md#6-테스트"""

    def test_items_appear_in_order_with_their_shapes(self) -> None:
        page = render_transcript(_RECORDS, "실행 기록 x")
        heads = ["&gt; 사용자", "생각", "● 응답", "● Bash", "⎿ 결과", "● Edit", "⎿ 오류"]
        positions = [page.index(head) for head in heads]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("$ cat invoice.py", page)
        self.assertIn("--- 바꾸기 전\nget(code\n+++ 바꾼 뒤\nget(code.upper()", page)
        self.assertIn("(내용 없음)", page)
        self.assertNotIn("turn_duration", page)
        self.assertIn(f"<summary>{FOLD_LINES + 5}줄 펼치기</summary>", page)

    def test_record_text_is_escaped(self) -> None:
        page = render_transcript(_RECORDS, "t")
        self.assertNotIn("<script>alert", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)

    def test_command_writes_one_page_per_session_without_the_variant_name(self) -> None:
        self.write("scenario/cal-e2/s-123.jsonl", "".join(json.dumps(record) + "\n" for record in _RECORDS))
        out = self.root / "baseline"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["study", "baseline", str(self.root / "scenario"), "--out", str(out)]), 0)
        self.assertEqual([path.name for path in out.iterdir()], ["s-123.html"])
        self.assertNotIn("cal-e2", (out / "s-123.html").read_text(encoding="utf-8"))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["study", "baseline", str(self.root / "empty"), "--out", str(out)]), 1)
