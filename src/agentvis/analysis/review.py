"""The instruction review model of one turn: instruction sentences, their targets and the signals that point at them.

Every signal is an estimate made by fixed rules; nothing here decides that an instruction was wrong.

@doc: docs/design/ReviewView.md#4-분석기-지시-대조-모델
"""

import re
from dataclasses import dataclass, field

from agentvis.analysis.session import SessionView

_SENTENCE_END = re.compile(r"[.?!](?=\s|$)")
_BACKTICK = re.compile(r"`([^`\n]+)`")
_PATH = re.compile(r"/|\.[A-Za-z0-9]{1,5}$")
_TEST = re.compile(r"^(?:test_\w|Test\w)|::")
_COMMAND = re.compile(r"^[A-Za-z0-9_.-]+\s")
_CALL = re.compile(r"^([A-Za-z_][\w.]*)\(")


@dataclass
class Target:
    """N2: something the instruction names in backticks.

    @doc: docs/design/ReviewView.md#42-규칙
    """

    text: str
    kind: str
    start: int
    end: int


@dataclass
class Sentence:
    """N1: one numbered sentence of the instruction, with its place in the original text.

    @doc: docs/design/ReviewView.md#41-모델
    """

    index: int
    text: str
    start: int
    end: int
    targets: list[Target] = field(default_factory=list)


@dataclass
class Signal:
    """N3 to N8: one rule-found event that bears on how the instruction was read.

    @doc: docs/design/ReviewView.md#41-모델
    """

    kind: str
    step_id: int
    at: str | None
    summary: str
    sentence: int | None = None
    detail: dict = field(default_factory=dict)


@dataclass
class Review:
    """The instruction review of one turn.

    @doc: docs/design/ReviewView.md#41-모델
    """

    turn: int
    sentences: list[Sentence]
    signals: list[Signal] = field(default_factory=list)
    quiet_steps: list[int] = field(default_factory=list)


def _spans(text: str) -> list[tuple[int, int]]:
    """Sentence spans: fenced code blocks whole, otherwise lines cut after sentence ends outside backticks."""
    spans: list[tuple[int, int]] = []
    position, fence_start = 0, None
    for line in text.splitlines(keepends=True):
        start, end = position, position + len(line.rstrip("\r\n"))
        position += len(line)
        if line.strip().startswith("```"):
            if fence_start is None:
                fence_start = start
            else:
                spans.append((fence_start, end))
                fence_start = None
            continue
        if fence_start is not None:
            continue
        cut = start
        for match in _SENTENCE_END.finditer(text, start, end):
            if text.count("`", start, match.start()) % 2 == 0:
                spans.append((cut, match.end()))
                cut = match.end()
        spans.append((cut, end))
    if fence_start is not None:
        spans.append((fence_start, len(text)))
    trimmed = []
    for start, end in spans:
        piece = text[start:end]
        if piece.strip():
            lead = len(piece) - len(piece.lstrip())
            trimmed.append((start + lead, start + len(piece.rstrip())))
    return trimmed


def _target(raw: str) -> tuple[str, str]:
    if _TEST.search(raw):
        return raw, "test"
    if _COMMAND.match(raw):
        return raw, "command"
    call = _CALL.match(raw)
    if call:
        return call.group(1), "symbol"
    if _PATH.search(raw) and " " not in raw:
        return raw, "path"
    return raw, "symbol"


def split_instruction(text: str) -> list[Sentence]:
    """N1 and N2: the instruction cut into numbered sentences, each with its backticked targets.

    @doc: docs/design/ReviewView.md#42-규칙
    """
    sentences = []
    for number, (start, end) in enumerate(_spans(text), 1):
        sentence = Sentence(number, text[start:end], start, end)
        for match in _BACKTICK.finditer(text, start, end):
            name, kind = _target(match.group(1))
            sentence.targets.append(Target(name, kind, match.start(1), match.end(1)))
        sentences.append(sentence)
    return sentences


def review_turn(view: SessionView, index: int) -> Review | None:
    """The instruction review of the turn with the given index, or None if there is no such turn.

    @doc: docs/design/ReviewView.md#4-분석기-지시-대조-모델
    """
    turn = next((turn for turn in view.turns if turn.index == index), None)
    if turn is None:
        return None
    return Review(turn=index, sentences=split_instruction(turn.prompt))
