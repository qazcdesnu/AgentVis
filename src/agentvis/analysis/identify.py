"""Rules that identify test runs, test file changes and completion reports (M8-T6).

Every result here is an estimate made by fixed rules; it never judges whether a change was right.

@doc: docs/design/Analysis.md#51-테스트-사건과-완료-보고
"""

import re

_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n\s*\2[ \t]*(?=\n|$)", re.DOTALL)
_COMMAND_SPLIT = re.compile(r"\s*(?:&&|\|\||;|\n)\s*")
_PIPE_SPLIT = re.compile(r"(?<!\|)\|(?!\|)")
_PREFIX = re.compile(r"^(?:\w+=\S*\s+)*(?:(?:uv|poetry|pdm|hatch|pipenv)\s+run\s+|npx\s+|bunx\s+)?")
_RUNNER = re.compile(
    r"(?:python3?\s+-m\s+(?:pytest|unittest)\b|pytest\b|py\.test\b|(?:npm|yarn|pnpm|bun)\s+(?:run\s+)?test\b"
    r"|go\s+test\b|cargo\s+test\b|jest\b|vitest\b|mocha\b|rspec\b|tox\b|nox\b|make\s+test\b|mvn\s+test\b"
    r"|(?:\./)?gradlew?\s+test\b|dotnet\s+test\b|ctest\b)"
)
_TEST_PATH = re.compile(
    r"(^|/)(tests?|__tests__|specs?)/|(^|/)test_[^/]*\.py$|_test\.(py|go)$|\.(test|spec)\.[cm]?[jt]sx?$|_spec\.rb$"
)
_REDIRECT = re.compile(r"(?<![<>&\d])>>?\s*(['\"]?)([^\s'\"<>|;&]+)\1")
_TEE = re.compile(r"\btee\s+(?:-a\s+)?(['\"]?)([^\s'\"<>|;&]+)\1")
_IN_PLACE = re.compile(r"^(?:sed\s+-i|perl\s+-pi)\b")
_PY_WRITE = re.compile(r"\.write_(?:text|bytes)\(|open\([^)\n]*['\"][wa]b?\+?['\"]")
_PY_PATH = re.compile(r"(?:Path|open)\(\s*(['\"])([^'\"\n]+)\1")
_PYTEST = re.compile(
    r"(?m)^[=\s]*((?:\d+ (?:failed|passed|skipped|errors?|xfailed|xpassed|deselected|warnings?)(?:, )?)+)(?: in [\d.]+s)?"
)
_UNITTEST = re.compile(r"(?m)^Ran (\d+) tests?.*?\n\s*\n?(OK(?: \([^)]*\))?|FAILED \([^)]*\))", re.DOTALL)
_UNITTEST_TAIL = re.compile(r"(?m)^(OK(?: \([^)]*\))?|FAILED \((?:failures|errors)=[^)]*\))[ \t]*$")
_GO = re.compile(r"(?m)^(?:(ok|FAIL)\s+\S+|--- (FAIL):)")
_CARGO = re.compile(r"test result: (ok|FAILED)\.([^\n]*)")
_JS = re.compile(r"(?m)^\s*Tests:?\s+(\d[^\n]*)$")
_DONE = re.compile(
    r"완료(?:했|됐|되었|하였|입니다|함)|통과(?:했|합니다|함|됐|되었|하였)|모두 통과"
    r"|고쳤|수정했|추가했|구현했|만들었|바꿨|반영했|해결했|작성했|마쳤|끝냈|올렸|커밋했|합쳤|옮겼|지웠|삭제했|넣었|등록했|정리했"
    r"|\b(?:done|completed?|fixed|implemented|added|passed|passes|passing|resolved|finished|merged|created|updated)\b|\btests?\s+pass\b",
    re.IGNORECASE,
)
_NOT_DONE = re.compile(r"못|않|실패|아직|남았|\bnot\b|n't\b|\bfail", re.IGNORECASE)
_LINE_MARK = re.compile(r"^\s*(?:#+\s*|>\s*|[-*+]\s+|\d+[.)]\s+)*")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_SENTENCE_CHARS = 300


def _without_heredocs(command: str) -> str:
    return _HEREDOC.sub("<<HEREDOC", command)


def test_command(command: str) -> dict | None:
    """Return {"clipped": bool} when the Bash command runs tests, else None.

    @doc: docs/design/Analysis.md#51-테스트-사건과-완료-보고
    """
    found, clipped = False, False
    for part in _COMMAND_SPLIT.split(_without_heredocs(command)):
        pipeline = [piece.strip() for piece in _PIPE_SPLIT.split(part)]
        head = pipeline[0]
        if _RUNNER.match(head[_PREFIX.match(head).end():]):
            found = True
            clipped = clipped or len(pipeline) > 1
    return {"clipped": clipped} if found else None


def test_outcome(text: str) -> tuple[str | None, str | None]:
    """Read ("pass" | "fail", summary) from a test run's whole output, or (None, None) without a summary.

    @doc: docs/design/Analysis.md#51-테스트-사건과-완료-보고
    """
    found: list[tuple[int, str, str]] = []
    for match in _PYTEST.finditer(text):
        summary = match.group(1).strip().rstrip(",")
        found.append((match.start(), "fail" if re.search(r"failed|error", summary) else "pass", summary))
    for match in _UNITTEST.finditer(text):
        found.append((match.start(), "fail" if match.group(2).startswith("FAILED") else "pass", f"Ran {match.group(1)} tests · {match.group(2)}"))
    if not any(item[2].startswith("Ran ") for item in found):
        # Output cut with `| tail -1` keeps only the unittest verdict line.
        for match in _UNITTEST_TAIL.finditer(text):
            found.append((match.start(), "fail" if match.group(1).startswith("FAILED") else "pass", match.group(1)))
    go = [(match.start(), match.group(0).strip()) for match in _GO.finditer(text)]
    if go:
        failed = [line for _, line in go if "FAIL" in line]
        found.append((go[-1][0], "fail" if failed else "pass", (failed or [line for _, line in go])[-1]))
    for match in _CARGO.finditer(text):
        found.append((match.start(), "fail" if match.group(1) == "FAILED" else "pass", f"test result: {match.group(1)}.{match.group(2)}".strip()))
    for match in _JS.finditer(text):
        found.append((match.start(), "fail" if "failed" in match.group(1) else "pass", match.group(1).strip()))
    if not found:
        return None, None
    failures = [item for item in found if item[1] == "fail"]
    _, result, summary = max(failures or found, key=lambda item: item[0])
    return result, summary


def is_test_path(path: str, root: str | None = None) -> bool:
    """Whether a file path, taken relative to the project root, is a test file.

    @doc: docs/design/Analysis.md#51-테스트-사건과-완료-보고
    """
    return bool(_TEST_PATH.search(relative_path(path, root)))


def relative_path(path: str, root: str | None = None) -> str:
    """The path with forward slashes, relative to root when it lies inside root.

    @doc: docs/design/Analysis.md#51-테스트-사건과-완료-보고
    """
    path = path.replace("\\", "/")
    if root:
        base = root.replace("\\", "/").rstrip("/") + "/"
        if path.startswith(base):
            return path[len(base):]
    return path


def written_paths(command: str) -> list[str]:
    """Paths a Bash command appears to write: redirections, tee, in-place edits and Python heredoc writes.

    @doc: docs/design/Analysis.md#51-테스트-사건과-완료-보고
    """
    paths: list[str] = []
    shell = _without_heredocs(command)
    for match in [*_REDIRECT.finditer(shell), *_TEE.finditer(shell)]:
        target = match.group(2)
        if not target.startswith(("/dev/", "&")):
            paths.append(target)
    for part in _COMMAND_SPLIT.split(shell):
        part = part.strip()
        words = part.split()
        if _IN_PLACE.match(part) and len(words) > 2:
            paths.append(words[-1].strip("'\""))
    for match in _HEREDOC.finditer(command):
        body = match.group(3)
        if _PY_WRITE.search(body):
            paths.extend(found.group(2) for found in _PY_PATH.finditer(body))
    return list(dict.fromkeys(paths))


def completion_sentences(text: str) -> list[str]:
    """Sentences of a response that report finished work, skipping code blocks, tables, negations and questions.

    @doc: docs/design/Analysis.md#51-테스트-사건과-완료-보고
    """
    sentences: list[str] = []
    in_code = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped or stripped.startswith("|"):
            continue
        clean = _LINE_MARK.sub("", stripped).replace("**", "")
        for sentence in _SENTENCE_END.split(clean):
            sentence = sentence.strip()
            if not sentence or sentence.endswith("?") or not _DONE.search(sentence) or _NOT_DONE.search(sentence):
                continue
            sentences.append(sentence if len(sentence) <= _SENTENCE_CHARS else sentence[:_SENTENCE_CHARS] + "…")
    return sentences
