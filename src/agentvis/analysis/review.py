"""The instruction review model of one turn: instruction sentences, their targets and the signals that point at them.

Every signal is an estimate made by fixed rules; nothing here decides that an instruction was wrong.

@doc: docs/design/ReviewView.md#4-분석기-지시-대조-모델
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from agentvis.analysis.identify import is_test_path, relative_path, written_paths
from agentvis.analysis.session import SessionView, Step, Turn

_SENTENCE_END = re.compile(r"[.?!](?=\s|$)")
_BACKTICK = re.compile(r"`([^`\n]+)`")
_PATH = re.compile(r"/|\.[A-Za-z0-9]{1,5}$")
_TEST = re.compile(r"^(?:test_\w|Test\w)|::")
_COMMAND = re.compile(r"^[A-Za-z0-9_.-]+\s")
_CALL = re.compile(r"^([A-Za-z_][\w.]*)\(")
# N3: wording that sets the agent's reading against the instruction (ReviewView.md section 4.2).
_CONTRAST = re.compile(
    r"이슈에서는|지시(?:와는|와|에서는|대로라면)? ?달리|지시와 다르|실제로는|원인이 아니|문제가 아니|아닌 것 같|하지만|그러나|오히려"
    r"|\bhowever\b|\bactually\b|\binstead\b|turns out|rather than|contrary to|(?:is ?n[o']t|not) the (?:root )?(?:cause|problem|issue|culprit)"
    r"|does ?n[o']t seem|but the (?:issue|instruction|request)|the (?:issue|instruction) (?:says|claims|suggests)",
    re.IGNORECASE,
)
_NEGATION = re.compile(r"아니|않|\bnot\b|n't\b", re.IGNORECASE)
_CAUSE = re.compile(r"원인|문제|이유|버그|\bcause\b|\bproblem\b|\bissue\b|\bculprit\b|\bbug\b", re.IGNORECASE)
_AGENT_SENTENCE = re.compile(r"(?<=[.!?。？])\s+")
_QUESTION = re.compile(r"[?？]\s*$")
_FILE_TOKEN = re.compile(r"^[\w./-]+\.[A-Za-z0-9]{1,6}$")
_READ_COMMAND = re.compile(r"^(?:cat|head|tail|less|more|nl|wc|sed\s+-n)\b")
_SEGMENT = re.compile(r"\s*(?:&&|\|\||;|\||\n)\s*")
# Files outside an instruction's targets that are not worth a signal: tests are expected reading, configs and docs are context.
_CONTEXT_SUFFIXES = {".md", ".txt", ".rst", ".toml", ".cfg", ".ini", ".json", ".yaml", ".yml", ".lock"}
_FILE_TOOLS = {"Read": "read", "Edit": "edit", "MultiEdit": "edit", "Write": "edit", "NotebookEdit": "edit"}
_SUMMARY_CHARS = 160
_ERROR_NAME = re.compile(r"\b\w*(?:Error|Exception)\b")
_REPRO_RESULT = {"fail": "재현됨", "pass": "재현 안 됨", "unknown": "결과 모름", None: "결과 모름"}


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


def _walk(steps: list[Step] | None) -> Iterator[Step]:
    for step in steps or []:
        yield step
        yield from _walk(step.substeps)
        if step.tool_call is not None:
            yield from _walk(step.tool_call.subagent)


def _agent_sentences(text: str) -> list[str]:
    sentences, in_code = [], False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped or stripped.startswith("|"):
            continue
        sentences += [piece.strip() for piece in _AGENT_SENTENCE.split(stripped) if piece.strip()]
    return sentences


def _short(text: str) -> str:
    text = text.replace("**", "")
    return text if len(text) <= _SUMMARY_CHARS else text[:_SUMMARY_CHARS] + "…"


def _sentence_naming(sentences: list[Sentence], text: str) -> int | None:
    for sentence in sentences:
        if any(target.text in text for target in sentence.targets if target.kind != "command"):
            return sentence.index
    return None


def _at(step: Step) -> str | None:
    return step.at.isoformat() if step.at else None


def _interpretations(steps: list[Step], sentences: list[Sentence]) -> list[Signal]:
    """N3: response sentences that set the agent's reading against the instruction."""
    names = [target.text for sentence in sentences for target in sentence.targets if target.kind != "command"]
    signals = []
    for step in steps:
        if step.kind != "text" or not step.text:
            continue
        for text in _agent_sentences(step.text):
            if _QUESTION.search(text):
                continue
            names_target = any(name in text for name in names)
            if _CONTRAST.search(text) or (names_target and _NEGATION.search(text) and _CAUSE.search(text)):
                signals.append(Signal("interpret", step.id, _at(step), _short(text), _sentence_naming(sentences, text), {"text": text}))
    return signals


def _questions(turn: Turn, steps: list[Step], sentences: list[Sentence]) -> list[Signal]:
    """N4: the question tool (confirmed) and questions in the turn's final response (estimated)."""
    signals = []
    for step in steps:
        call = step.tool_call
        if call is not None and call.tool_name == "AskUserQuestion":
            signals.append(Signal("ask", step.id, _at(step), "질문 도구로 사용자에게 물음", None, {"confirmed": True}))
    texts = [step for step in turn.steps if step.kind == "text" and step.text]
    if turn.state != "running" and texts:
        final = texts[-1]
        asked = [text for text in _agent_sentences(final.text or "") if _QUESTION.search(text)]
        if asked:
            joined = " ".join(asked)
            signals.append(Signal("ask", final.id, _at(final), _short(joined), _sentence_naming(sentences, joined), {"confirmed": False, "text": joined}))
    return signals


def _touched_files(step: Step) -> list[tuple[str, str, bool]]:
    """(path, "read" | "edit", estimated) for the files one tool call reads or changes."""
    call = step.tool_call
    if call is None or not isinstance(call.input, dict):
        return []
    action = _FILE_TOOLS.get(call.tool_name or "")
    if action and isinstance(call.input.get("file_path"), str):
        return [(call.input["file_path"], action, False)]
    command = call.input.get("command")
    if call.tool_name != "Bash" or not isinstance(command, str):
        return []
    touched = [(path, "edit", True) for path in written_paths(command)]
    for segment in _SEGMENT.split(command):
        if _READ_COMMAND.match(segment):
            touched += [(word, "read", True) for word in segment.split()[1:] if _FILE_TOKEN.match(word) and "*" not in word]
    return touched


def _inside(path: str, sentences: list[Sentence]) -> bool:
    stem = PurePosixPath(path).stem
    for sentence in sentences:
        for target in sentence.targets:
            if target.kind == "path" and (path == target.text or path.endswith("/" + target.text) or target.text.endswith("/" + path)):
                return True
            if target.kind == "symbol":
                module = target.text.split(".")
                if stem in (module[0], module[-1]) or (len(module) > 1 and "/".join(module[:-1]) + ".py" in path):
                    return True
    return False


def _outside(steps: list[Step], sentences: list[Sentence], root: str | None) -> list[Signal]:
    """N5: source files read or changed that none of the instruction's targets names."""
    located = [sentence for sentence in sentences if any(target.kind in ("path", "symbol") for target in sentence.targets)]
    if not located:
        return []
    anchor = next((s.index for s in located if any(t.kind == "path" for t in s.targets)), located[0].index)
    candidates, seen = [], set()
    for step in steps:
        for path, action, estimated in _touched_files(step):
            relative = relative_path(path, root)
            if (relative, action) in seen or is_test_path(relative) or PurePosixPath(relative).suffix in _CONTEXT_SUFFIXES:
                continue
            seen.add((relative, action))
            if not _inside(relative, sentences):
                candidates.append((step, relative, action, estimated))
    # Reading around is ordinary exploration; a read counts once the agent also changes that file.
    edited = {relative for _, relative, action, _ in candidates if action == "edit"}
    return [
        Signal("outside", step.id, _at(step), f"{relative} {'읽음' if action == 'read' else '고침'}", anchor,
               {"path": relative, "action": action, "estimated_path": estimated})
        for step, relative, action, estimated in candidates if relative in edited
    ]


def _source_edits(step: Step, root: str | None) -> list[str]:
    """Project-relative source files (not tests, docs or configs) that one tool call changes."""
    edits = []
    for path, action, _ in _touched_files(step):
        relative = relative_path(path, root)
        if action == "edit" and not is_test_path(relative) and PurePosixPath(relative).suffix not in _CONTEXT_SUFFIXES:
            edits.append(relative)
    return edits


def _run(step: Step) -> dict | None:
    return step.tool_call.test_run if step.tool_call is not None else None


def _output(step: Step) -> str:
    call = step.tool_call
    return f"{call.result or ''}\n{call.error or ''}" if call is not None else ""


def _symptom_sentence(sentences: list[Sentence]) -> int | None:
    # Issues describe the symptom first.
    return sentences[0].index if sentences else None


def _reproductions(steps: list[Step], sentences: list[Sentence], prompt: str, root: str | None) -> list[Signal]:
    """N6: test runs before the first source edit, with whether they reproduced the reported symptom."""
    errors = set(_ERROR_NAME.findall(prompt))
    signals = []
    for step in steps:
        if _source_edits(step, root):
            break
        run = _run(step)
        if run is None:
            continue
        outcome = _REPRO_RESULT[run.get("result")]
        if run.get("result") == "fail" and errors and not any(error in _output(step) for error in errors):
            outcome = "다른 오류"
        summary = f"{outcome}: {run.get('summary') or '요약 없음'}"
        signals.append(Signal("repro", step.id, _at(step), summary, _symptom_sentence(sentences),
                              {"outcome": outcome, "result": run.get("result"), "expected_errors": sorted(errors)}))
    return signals


def _sentence_of_file(path: str, sentences: list[Sentence]) -> int | None:
    for sentence in sentences:
        if _inside(path, [sentence]):
            return sentence.index
    return None


def _remaining_failures(steps: list[Step], sentences: list[Sentence], root: str | None) -> list[Signal]:
    """N7: a failing test run right after the agent changed a file the instruction pointed at."""
    signals, pending = [], []
    for step in steps:
        pending += [path for path in _source_edits(step, root) if _inside(path, sentences) and path not in pending]
        run = _run(step)
        if run is None or not pending:
            continue
        if run.get("result") == "fail":
            files = ", ".join(pending)
            signals.append(Signal("remaining_failure", step.id, _at(step), f"{files} 고친 뒤 실패: {run.get('summary') or ''}".strip(),
                                  _sentence_of_file(pending[0], sentences), {"files": list(pending), "failed": run.get("failed", [])}))
        pending = []
    return signals


def _conflicts(steps: list[Step], sentences: list[Sentence], root: str | None) -> list[Signal]:
    """N8: between two runs of the same command with an edit between, one test starts passing as another starts failing."""
    signals, last, edited = [], {}, False
    for step in steps:
        edited = edited or bool(_source_edits(step, root))
        run = _run(step)
        if run is None or run.get("result") not in ("pass", "fail"):
            continue
        command = " ".join(str(step.tool_call.input.get("command", "")).split())
        before = last.get(command)
        failed = set(run.get("failed", [])) if run.get("result") == "fail" else set()
        if before is not None and edited:
            fixed, broken = sorted(before - failed), sorted(failed - before)
            if fixed and broken:
                names = [name.split("::")[-1].split(".")[-1] for name in fixed + broken]
                sentence = next((s.index for s in sentences if any(t.kind == "test" and t.text.split("::")[-1] in names for t in s.targets)), None)
                summary = f"통과로 바뀜: {', '.join(fixed)} · 실패로 바뀜: {', '.join(broken)}"
                signals.append(Signal("conflict", step.id, _at(step), _short(summary), sentence, {"fixed": fixed, "broken": broken}))
        last[command], edited = failed, False
    return signals


# Steps that can sit quietly: routine work, never a person's message, a notice or the final report.
_QUIET_KINDS = {"tool_call", "thinking", "text"}


def _quiet_steps(turn: Turn, steps: list[Step], signals: list[Signal]) -> list[int]:
    """N9: steps with no failure and no signal, which the screen folds or dims."""
    loud = {signal.step_id for signal in signals}
    texts = [step for step in turn.steps if step.kind == "text"]
    if texts:
        loud.add(texts[-1].id)
    quiet = []
    for step in steps:
        call = step.tool_call
        failed = call is not None and (call.status in ("error", "interrupted") or (call.test_run or {}).get("result") == "fail")
        if step.kind in _QUIET_KINDS and step.id not in loud and not failed:
            quiet.append(step.id)
    return quiet


def review_turn(view: SessionView, index: int) -> Review | None:
    """The instruction review of the turn with the given index, or None if there is no such turn.

    @doc: docs/design/ReviewView.md#4-분석기-지시-대조-모델
    """
    turn = next((turn for turn in view.turns if turn.index == index), None)
    if turn is None:
        return None
    sentences = split_instruction(turn.prompt)
    steps = list(_walk(turn.steps))
    signals = (_interpretations(steps, sentences) + _questions(turn, steps, sentences) + _outside(steps, sentences, view.project)
               + _reproductions(steps, sentences, turn.prompt, view.project) + _remaining_failures(steps, sentences, view.project)
               + _conflicts(steps, sentences, view.project))
    signals.sort(key=lambda signal: (signal.at or "", signal.step_id))
    return Review(turn=index, sentences=sentences, signals=signals, quiet_steps=_quiet_steps(turn, steps, signals))
