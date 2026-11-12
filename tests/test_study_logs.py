"""Tests for summarizing the experiment server's screen usage logs.

@doc: docs/design/Study.md#6-테스트
"""

import csv
import io
import json
from contextlib import redirect_stdout

from agentvis.cli import main
from agentvis.study.logs import element_kind, summarize_logs
from tests.support import RepoTestCase


def _entry(kind: str, at: str = "2026-11-13T01:00:00.000Z", **detail: object) -> dict:
    return {"type": kind, "at": at, "detail": detail}


_LOG = [
    {"type": "server_start", "participant": "P01", "version": "2.1.0", "condition": "agentvis"},
    _entry("click", tag="li", classes=["rv-signal"]),
    _entry("trial_start", "2026-11-13T01:00:00.000Z", trial=1),
    _entry("click", tag="button", id="trial", classes=["trial"]),
    _entry("click", tag="li", classes=["rv-signal"]),
    _entry("click", tag="li", classes=["rv-signal"]),
    _entry("click", tag="g", classes=["g-node", "kind-tool_call"]),
    _entry("hash", hash="#step=3"),
    _entry("key", key="j"),
    _entry("find"),
    _entry("scroll", y=10, ratio=0.1),
    _entry("trial_end", "2026-11-13T01:01:30.500Z", trial=1),
    _entry("click", tag="li", classes=["rv-signal"]),
    {"type": "server_start", "participant": "P01", "version": "2.1.0", "condition": "agentvis"},
    _entry("trial_start", trial=1),
]


class LogSummaryTest(RepoTestCase):
    """@doc: docs/design/Study.md#6-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.log = self.write("home/experiments/P01-setA/interactions.jsonl", "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in _LOG))

    def test_trials_are_timed_and_counted(self) -> None:
        rows = summarize_logs([self.root / "home"])
        self.assertEqual([(row["run"], row["trial"], row["seconds"]) for row in rows], [(1, 1, 90.5), (2, 1, None)])
        first = rows[0]
        self.assertEqual((first["participant"], first["block"], first["condition"]), ("P01", "P01-setA", "agentvis"))
        self.assertEqual((first["clicks"], first["keys"], first["finds"], first["scrolls"], first["views"]), (3, 1, 1, 1, 1))
        self.assertEqual(first["elements"], "신호 목록 2; 그래프 노드 1")

    def test_element_kinds(self) -> None:
        self.assertEqual(element_kind({"tag": "span", "classes": ["rv-sentence"]}), "지시 문장")
        self.assertEqual(element_kind({"tag": "g", "classes": []}), "그래프 노드")
        self.assertEqual(element_kind({"tag": "a", "classes": []}), "기록 링크")
        self.assertEqual(element_kind({"tag": "div", "classes": ["x"]}), "<div>")

    def test_command(self) -> None:
        out = self.root / "trials.csv"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["study", "log-summary", str(self.log), "--csv", str(out)]), 0)
        with out.open(encoding="utf-8") as file:
            self.assertEqual([row["seconds"] for row in csv.DictReader(file)], ["90.5", ""])
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["study", "log-summary", str(self.root / "home")]), 0)
        self.assertTrue(output.getvalue().startswith("participant\tblock"))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["study", "log-summary", str(self.root / "empty")]), 1)
