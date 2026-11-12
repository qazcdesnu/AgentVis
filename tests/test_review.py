"""Tests for the instruction review model of a turn.

@doc: docs/design/ReviewView.md#5-테스트
"""

import unittest
from dataclasses import replace

from fastapi.testclient import TestClient

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
