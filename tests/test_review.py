"""Tests for the instruction review model of a turn.

@doc: docs/design/ReviewView.md#5-테스트
"""

import unittest
from dataclasses import replace

from fastapi.testclient import TestClient

from agentvis.analysis.graph import build_turn_graph
from agentvis.analysis.review import review_turn, split_instruction
from agentvis.server import create_app
from agentvis.store import EventStore
from tests.support import RepoTestCase
from tests.test_analysis import _Session

_PROMPT = (
    '`total([100.0], "save10")`가 90.0이 아니라 100.0을 돌려줍니다. '
    "`invoice.py`의 `total`에서 `round` 처리를 고쳐 주세요.\n"
    "테스트는 `python3 -m unittest discover -s tests -t .`로 돌립니다.\n\n"
    "```\nx = 1. y\n```\n"
    "`test_code_is_case_insensitive`와 `tests/a.py::test_b`가 실패합니다? 확인해 주세요!"
)


class SplitTest(unittest.TestCase):
    """@doc: docs/design/ReviewView.md#5-테스트"""

    def test_sentences_follow_sentence_ends_but_not_numbers_backticks_or_code(self) -> None:
        sentences = split_instruction(_PROMPT)
        self.assertEqual([sentence.index for sentence in sentences], [1, 2, 3, 4, 5, 6])
        self.assertTrue(sentences[0].text.endswith("돌려줍니다."))
        self.assertTrue(sentences[2].text.endswith("돌립니다."))
        self.assertEqual(sentences[3].text, "```\nx = 1. y\n```")
        self.assertTrue(sentences[4].text.endswith("실패합니다?"))
        for sentence in sentences:
            self.assertEqual(_PROMPT[sentence.start:sentence.end], sentence.text)

    def test_targets_are_classified_and_located(self) -> None:
        targets = [(target.text, target.kind) for sentence in split_instruction(_PROMPT) for target in sentence.targets]
        self.assertEqual(targets, [
            ("total", "symbol"), ("invoice.py", "path"), ("total", "symbol"), ("round", "symbol"),
            ("python3 -m unittest discover -s tests -t .", "command"),
            ("test_code_is_case_insensitive", "test"), ("tests/a.py::test_b", "test"),
        ])
        for sentence in split_instruction(_PROMPT):
            for target in sentence.targets:
                self.assertEqual(_PROMPT[target.start - 1], "`")
                self.assertEqual(_PROMPT[target.end], "`")

    def test_blank_instruction_has_no_sentences(self) -> None:
        self.assertEqual(split_instruction("\n\n  \n"), [])


class ReviewApiTest(RepoTestCase):
    """@doc: docs/design/ReviewView.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.store = EventStore(self.root / "agentvis.db")
        self.addCleanup(self.store.close)
        s = _Session()
        s.prompt("u1", "p1", _PROMPT)
        self.view = s.build()
        self.store.append_batch([replace(event, session_id="s1", id=None) for event in s.events])
        self.client = TestClient(create_app(self.store), base_url="http://127.0.0.1:8765")

    def test_review_of_a_turn(self) -> None:
        self.assertIsNone(review_turn(self.view, 2))
        review = self.client.get("/api/sessions/s1/turns/1/review").json()
        self.assertEqual(review["turn"], 1)
        self.assertEqual(len(review["sentences"]), 6)
        self.assertEqual(review["sentences"][1]["targets"][0], {"text": "invoice.py", "kind": "path", "start": _PROMPT.index("invoice.py"), "end": _PROMPT.index("invoice.py") + 10})
        self.assertEqual((review["signals"], review["quiet_steps"]), ([], []))
        self.assertEqual(self.client.get("/api/sessions/s1/turns/2/review").status_code, 404)
        self.assertEqual(self.client.get("/api/sessions/nope/turns/1/review").status_code, 404)


def _review(s: _Session):
    view = s.build()
    review = review_turn(view, 1)
    assert review is not None
    return review


class InterpretationSignalTest(unittest.TestCase):
    """@doc: docs/design/ReviewView.md#5-테스트"""

    def setUp(self) -> None:
        self.s = _Session()
        self.s.prompt("u1", "p1", "`invoice.py`의 `round` 처리가 원인입니다. 고쳐 주세요.")

    def say(self, uuid: str, parent: str, text: str, **extra: object) -> None:
        self.s.assistant(uuid, parent, {"type": "text", "text": text}, **extra)

    def tool(self, uuid: str, parent: str, tool_id: str, name: str, **data: object) -> None:
        self.s.assistant(uuid, parent, {"type": "tool_use", "id": tool_id, "name": name, "input": data})
        self.s.result(f"r-{uuid}", uuid, "p1", tool_id, "ok")

    def test_interpretations(self) -> None:
        self.say("a1", "u1", "The `round` call is not the cause. 계산은 `round`가 아니라 `total`에서 합니다.\n```\nhowever = 1\n```")
        self.say("a2", "a1", "`round`는 바꾸지 않았습니다. 정말 `round`가 문제가 아닐까요?")
        signals = [(s.kind, s.summary, s.sentence) for s in _review(self.s).signals]
        self.assertEqual(signals, [("interpret", "The `round` call is not the cause.", 1)])

    def test_questions(self) -> None:
        self.tool("a1", "u1", "toolu_1", "AskUserQuestion", questions=[])
        self.say("a2", "r-a1", "어느 쪽을 고칠까요? `round`인가요?")
        running = [(s.kind, s.detail["confirmed"]) for s in _review(self.s).signals]
        self.assertEqual(running, [("ask", True)])
        self.s.hook("Stop", prompt_id="p1")
        signals = [(s.kind, s.detail["confirmed"], s.sentence) for s in _review(self.s).signals]
        self.assertEqual(signals, [("ask", True, None), ("ask", False, 1)])

    def test_outside_files(self) -> None:
        self.tool("a1", "u1", "toolu_1", "Read", file_path="/Users/me/app/invoice.py")
        self.tool("a2", "r-a1", "toolu_2", "Bash", command="cat discount.py && cat README.md && head notes.py")
        self.tool("a3", "r-a2", "toolu_3", "Read", file_path="/Users/me/app/tests/test_invoice.py")
        self.tool("a4", "r-a3", "toolu_4", "Edit", file_path="/Users/me/app/discount.py", old_string="a", new_string="b")
        self.tool("a5", "r-a4", "toolu_5", "Bash", command="echo x > helpers.py")
        signals = [(s.kind, s.summary, s.sentence, s.detail["estimated_path"]) for s in _review(self.s).signals]
        self.assertEqual(signals, [
            ("outside", "discount.py 읽음", 1, True),
            ("outside", "discount.py 고침", 1, False),
            ("outside", "helpers.py 고침", 1, True),
        ])

    def test_graph_nodes_carry_signal_marks(self) -> None:
        self.tool("a1", "u1", "toolu_1", "Edit", file_path="/Users/me/app/discount.py", old_string="a", new_string="b")
        graph = build_turn_graph(self.s.build(), 1)
        marks = {node.label.split()[0]: node.marks for node in graph.nodes if node.marks}
        self.assertEqual(marks, {"Edit": ["signal_outside"]})
