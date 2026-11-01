"""Verify that roadmap, issue, ongoing and done documents agree by work ID.

@doc: docs/VerificationTools.md#6-작업-관리-검사기
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from tools.doclib import REPO_ROOT, Problem, iter_prose_lines, strip_inline_code, use_utf8_output

ROADMAP_DOC = "docs/Roadmap.md"
ISSUE_DOC = "docs/Issue.md"
ONGOING_DOC = "docs/Ongoing.md"
DONE_DOC = "docs/Done.md"

_ID = r"M\d+-T\d+|[IH]\d+"
_ID_RE = re.compile(rf"(?:{_ID})")
# ASCII-only boundaries so that IDs followed by Korean particles ("M0-T6으로") still match.
_ID_REF_RE = re.compile(rf"(?<![0-9A-Za-z-])({_ID})(?![0-9A-Za-z-])")
_MILESTONE_RE = re.compile(r"^## M(\d+) \S")
_TASK_RE = re.compile(r"^- \[([ ~x])\] (M(\d+)-T(\d+)) \S")
_ISSUE_RE = re.compile(r"^- \[([ ~x])\] (([IH])(\d+)) \S")
_LINK_FIELD_RE = re.compile(r"^\s+- 연결 작업: (\S+)")
_RECORD_RE = re.compile(rf"^## ({_ID}) \S")
_FIELD_RE = re.compile(r"^- ([^:]+): (.*)$")
_SECTION_RE = re.compile(r"^### (.+?)\s*$")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_STATUS_LABELS = {" ": "[ ]", "~": "[~]", "x": "[x]"}


@dataclass(frozen=True)
class WorkItem:
    """A roadmap task or an issue with its status.

    @doc: docs/VerificationTools.md#6-작업-관리-검사기
    """

    id: str
    status: str
    path: Path
    line: int
    link: str | None = None


@dataclass
class Record:
    """An entry of the ongoing or done document.

    @doc: docs/VerificationTools.md#6-작업-관리-검사기
    """

    id: str
    path: Path
    line: int
    fields: dict[str, str] = field(default_factory=dict)
    sections: set[str] = field(default_factory=set)


def _read_lines(path: Path) -> list[tuple[int, str]]:
    return list(iter_prose_lines(path.read_text(encoding="utf-8")))


def _expect_next(numbers: dict[str, int], key: str, actual: int, first: int) -> int | None:
    """Record the number for a sequence and return the expected one if it is out of order."""
    expected = numbers.get(key, first - 1) + 1
    numbers[key] = actual
    return expected if actual != expected else None


def parse_roadmap(path: Path) -> tuple[list[WorkItem], list[Problem]]:
    """Read roadmap tasks and report format and numbering problems.

    @doc: docs/VerificationTools.md#6-작업-관리-검사기
    """
    items, problems = [], []
    numbers: dict[str, int] = {}
    milestone = None
    for number, line in _read_lines(path):
        if line.startswith("## "):
            match = _MILESTONE_RE.match(line)
            if not match:
                problems.append(Problem(path, number, "마일스톤 제목 형식 오류: '## M<n> <이름>'이어야 함"))
                continue
            milestone = int(match.group(1))
            expected = _expect_next(numbers, "M", milestone, first=0)
            if expected is not None:
                problems.append(Problem(path, number, f"마일스톤 번호 차례 오류: M{expected}이어야 함"))
        elif line.startswith("- ["):
            match = _TASK_RE.match(line)
            if not match:
                problems.append(Problem(path, number, "태스크 줄 형식 오류: '- [ ] M<n>-T<m> <설명>'이어야 함"))
                continue
            status, task_id = match.group(1), match.group(2)
            task_milestone, task_number = int(match.group(3)), int(match.group(4))
            items.append(WorkItem(task_id, status, path, number))
            if task_milestone != milestone:
                problems.append(Problem(path, number, f"{task_id}가 M{task_milestone} 마일스톤 아래에 있지 않음"))
                continue
            expected = _expect_next(numbers, f"M{milestone}", task_number, first=1)
            if expected is not None:
                problems.append(
                    Problem(path, number, f"태스크 번호 차례 오류: M{milestone}-T{expected}이어야 함")
                )
    return items, problems


def parse_issues(path: Path) -> tuple[list[WorkItem], list[Problem]]:
    """Read issues with their linked work and report format and numbering problems.

    @doc: docs/VerificationTools.md#6-작업-관리-검사기
    """
    items, problems = [], []
    numbers: dict[str, int] = {}
    for number, line in _read_lines(path):
        if line.startswith("- ["):
            match = _ISSUE_RE.match(line)
            if not match:
                problems.append(Problem(path, number, "이슈 줄 형식 오류: '- [ ] I<n> <제목>' 또는 H<n>이어야 함"))
                continue
            prefix, issue_number = match.group(3), int(match.group(4))
            items.append(WorkItem(match.group(2), match.group(1), path, number))
            expected = _expect_next(numbers, prefix, issue_number, first=1)
            if expected is not None:
                problems.append(Problem(path, number, f"이슈 번호 차례 오류: {prefix}{expected}이어야 함"))
            continue
        match = _LINK_FIELD_RE.match(line)
        if match and items:
            target = match.group(1)
            if not _ID_RE.fullmatch(target):
                problems.append(Problem(path, number, f"연결 작업이 작업 ID가 아님: {target}"))
                continue
            last = items[-1]
            items[-1] = WorkItem(last.id, last.status, last.path, last.line, target)
    return items, problems


def parse_records(path: Path) -> tuple[list[Record], list[Problem]]:
    """Read ongoing or done records and report malformed or duplicate record headings.

    @doc: docs/VerificationTools.md#6-작업-관리-검사기
    """
    records: list[Record] = []
    problems = []
    seen: set[str] = set()
    current = None
    for number, line in _read_lines(path):
        if line.startswith("## "):
            match = _RECORD_RE.match(line)
            current = None
            if not match:
                problems.append(Problem(path, number, "기록 제목 형식 오류: '## <작업 ID> <제목>'이어야 함"))
                continue
            if match.group(1) in seen:
                problems.append(Problem(path, number, f"중복 기록: {match.group(1)}"))
                continue
            seen.add(match.group(1))
            current = Record(match.group(1), path, number)
            records.append(current)
        elif current is not None:
            section = _SECTION_RE.match(line)
            if section:
                current.sections.add(section.group(1))
                continue
            field_match = _FIELD_RE.match(line)
            if field_match and not current.sections:
                current.fields[field_match.group(1).strip()] = field_match.group(2).strip()
    return records, problems


def check_states(items: list[WorkItem], ongoing: list[Record], done: list[Record]) -> list[Problem]:
    """Report status marks that disagree with ongoing and done records.

    @doc: docs/VerificationTools.md#6-작업-관리-검사기
    """
    problems = []
    by_id: dict[str, WorkItem] = {}
    for item in items:
        if item.id in by_id:
            problems.append(Problem(item.path, item.line, f"중복 작업 ID: {item.id}"))
        else:
            by_id[item.id] = item
    ongoing_ids = {record.id for record in ongoing}
    done_ids = {record.id for record in done}
    for item in by_id.values():
        has_ongoing, has_done = item.id in ongoing_ids, item.id in done_ids
        if item.link is not None:
            problems.extend(_check_linked(item, by_id, has_ongoing or has_done))
            continue
        label = _STATUS_LABELS[item.status]
        if has_ongoing != (item.status == "~"):
            state = "있음" if has_ongoing else "없음"
            problems.append(Problem(item.path, item.line, f"{item.id}: 상태 {label}인데 진행 중 기록 {state}"))
        if has_done != (item.status == "x"):
            state = "있음" if has_done else "없음"
            problems.append(Problem(item.path, item.line, f"{item.id}: 상태 {label}인데 완료 기록 {state}"))
    for record in ongoing + done:
        if record.id not in by_id:
            problems.append(Problem(record.path, record.line, f"로드맵·이슈에 없는 작업의 기록: {record.id}"))
    return problems


def _check_linked(item: WorkItem, by_id: dict[str, WorkItem], has_record: bool) -> list[Problem]:
    target = by_id.get(item.link)
    if target is None:
        return [Problem(item.path, item.line, f"{item.id}: 연결 작업 {item.link}가 없음")]
    problems = []
    if target.link is not None:
        problems.append(Problem(item.path, item.line, f"{item.id}: 연결 작업 {item.link}가 다시 다른 작업에 연결됨"))
    if target.status != item.status:
        problems.append(
            Problem(
                item.path,
                item.line,
                f"{item.id}: 상태 {_STATUS_LABELS[item.status]}가 연결 작업 {item.link}의 "
                f"{_STATUS_LABELS[target.status]}와 다름",
            )
        )
    if has_record:
        problems.append(Problem(item.path, item.line, f"{item.id}: 연결 작업이 있는 이슈는 자체 기록을 두지 않음"))
    return problems


def check_records(ongoing_path: Path, ongoing: list[Record], done: list[Record]) -> list[Problem]:
    """Report missing fields and sections, bad dates, done order and the ongoing placeholder rule.

    @doc: docs/VerificationTools.md#6-작업-관리-검사기
    """
    problems = []
    for record in ongoing:
        problems.extend(_check_record(record, ("시작일",), ()))
    previous: date | None = None
    for record in done:
        problems.extend(_check_record(record, ("시작일", "완료일"), ("결과", "검증")))
        finished = _parse_date(record.fields.get("완료일", ""))
        if finished is None:
            continue
        if previous is not None and finished > previous:
            problems.append(Problem(record.path, record.line, f"{record.id}: 완료 기록은 완료일이 늦은 것부터 놓아야 함"))
        previous = finished
    placeholders = [number for number, line in _read_lines(ongoing_path) if line.strip() == "없음"]
    if not ongoing and not placeholders:
        problems.append(Problem(ongoing_path, 1, "진행 중 기록이 없으면 '없음'을 적어야 함"))
    for number in placeholders if ongoing else []:
        problems.append(Problem(ongoing_path, number, "진행 중 기록이 있는데 '없음'이 남아 있음"))
    return problems


def _check_record(record: Record, fields: tuple[str, ...], sections: tuple[str, ...]) -> list[Problem]:
    problems = []
    for name in fields:
        value = record.fields.get(name)
        if value is None:
            problems.append(Problem(record.path, record.line, f"{record.id}: '{name}' 필드 없음"))
        elif _parse_date(value) is None:
            problems.append(Problem(record.path, record.line, f"{record.id}: '{name}' 날짜 형식 오류: {value}"))
    for name in sections:
        if name not in record.sections:
            problems.append(Problem(record.path, record.line, f"{record.id}: '{name}' 절 없음"))
    return problems


def _parse_date(value: str) -> date | None:
    if not _DATE_RE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def check_references(paths: list[Path], known: set[str]) -> list[Problem]:
    """Report work IDs mentioned in prose that are not defined in the roadmap or issues.

    @doc: docs/VerificationTools.md#6-작업-관리-검사기
    """
    problems = []
    for path in paths:
        for number, line in _read_lines(path):
            for match in _ID_REF_RE.finditer(strip_inline_code(line)):
                if match.group(1) not in known:
                    problems.append(Problem(path, number, f"알 수 없는 작업 ID 참조: {match.group(1)}"))
    return problems


def main(argv: list[str] | None = None) -> int:
    """Run every task document check and print problems; return the exit code.

    @doc: docs/VerificationTools.md#6-작업-관리-검사기
    """
    use_utf8_output()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    root = parser.parse_args(argv).root.resolve()
    paths = [root / doc for doc in (ROADMAP_DOC, ISSUE_DOC, ONGOING_DOC, DONE_DOC)]
    missing = [Problem(path, 1, "작업 관리 문서 없음") for path in paths if not path.is_file()]
    if missing:
        problems = missing
    else:
        roadmap_path, issue_path, ongoing_path, done_path = paths
        tasks, problems = parse_roadmap(roadmap_path)
        issues, issue_problems = parse_issues(issue_path)
        ongoing, ongoing_problems = parse_records(ongoing_path)
        done, done_problems = parse_records(done_path)
        items = tasks + issues
        problems += (
            issue_problems
            + ongoing_problems
            + done_problems
            + check_states(items, ongoing, done)
            + check_records(ongoing_path, ongoing, done)
            + check_references(paths, {item.id for item in items})
        )
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_tasks: 문제 {len(problems)}건")
        return 1
    print(f"check_tasks: 통과 (작업 {len(items)}개, 진행 중 {len(ongoing)}개, 완료 {len(done)}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
