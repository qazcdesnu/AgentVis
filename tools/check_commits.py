"""Verify that commit messages follow the work-ID commit convention.

@doc: docs/VerificationTools.md#7-커밋-검사기
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

from tools.check_tasks import ISSUE_DOC, ROADMAP_DOC, parse_issues, parse_roadmap
from tools.doclib import REPO_ROOT, Problem

BASELINE_COMMIT = "2a80e26"
SUBJECT_MAX_LENGTH = 72

_ID = r"M\d+-T\d+|[IH]\d+"
_SUBJECT_RE = re.compile(rf"^((?:{_ID})(?:, (?:{_ID}))*): (\S.*)$")
# Field and record separators that cannot appear in commit messages.
_FIELD_SEP, _RECORD_SEP = "\x1f", "\x1e"


def work_statuses(root: Path) -> dict[str, str]:
    """Map every roadmap task and issue ID to its status mark.

    @doc: docs/VerificationTools.md#7-커밋-검사기
    """
    tasks, _ = parse_roadmap(root / ROADMAP_DOC)
    issues, _ = parse_issues(root / ISSUE_DOC)
    return {item.id: item.status for item in tasks + issues}


def parse_subject(subject: str) -> tuple[list[str], str] | None:
    """Split a subject line into its work IDs and summary, or return None if malformed.

    @doc: docs/VerificationTools.md#7-커밋-검사기
    """
    match = _SUBJECT_RE.match(subject)
    if not match:
        return None
    return match.group(1).split(", "), match.group(2)


def check_message(message: str, statuses: dict[str, str], require_started: bool) -> list[str]:
    """Return the convention violations of one commit message.

    @doc: docs/VerificationTools.md#7-커밋-검사기
    """
    lines = [line.rstrip() for line in message.splitlines() if not line.startswith("#")]
    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)
    if not lines:
        return ["빈 커밋 메시지"]
    subject = lines[0]
    problems = []
    if len(subject) > SUBJECT_MAX_LENGTH:
        problems.append(f"제목 줄이 {SUBJECT_MAX_LENGTH}자를 넘음 ({len(subject)}자)")
    if len(lines) > 1 and lines[1]:
        problems.append("제목 다음 줄은 비어 있어야 함")
    parsed = parse_subject(subject)
    if parsed is None:
        problems.append("제목 형식 오류: '<작업 ID>[, <작업 ID>…]: <요약>'이어야 함")
        return problems
    ids, summary = parsed
    if summary.endswith("."):
        problems.append("요약은 마침표로 끝내지 않음")
    for work_id in sorted(set(ids)):
        if ids.count(work_id) > 1:
            problems.append(f"제목에 같은 작업 ID가 반복됨: {work_id}")
    for work_id in dict.fromkeys(ids):
        status = statuses.get(work_id)
        if status is None:
            problems.append(f"로드맵·이슈에 없는 작업 ID: {work_id}")
        elif require_started and status == " ":
            problems.append(f"시작하지 않은 작업([ ])의 ID: {work_id}")
    return problems


def commit_messages(root: Path, revision_range: str) -> list[tuple[str, str]]:
    """Return (short hash, message) of the non-merge commits in a revision range.

    @doc: docs/VerificationTools.md#7-커밋-검사기
    """
    output = subprocess.run(
        ["git", "log", "--no-merges", f"--format=%h{_FIELD_SEP}%B{_RECORD_SEP}", revision_range],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    commits = []
    for record in output.split(_RECORD_SEP):
        if _FIELD_SEP in record:
            short_hash, message = record.split(_FIELD_SEP, 1)
            commits.append((short_hash.strip(), message))
    return commits


def main(argv: list[str] | None = None) -> int:
    """Check one message file or the history after the baseline; return the exit code.

    @doc: docs/VerificationTools.md#7-커밋-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--message-file", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    statuses = work_statuses(root)
    problems = []
    if args.message_file is not None:
        message = args.message_file.read_text(encoding="utf-8")
        problems = [Problem(args.message_file, 1, text) for text in check_message(message, statuses, True)]
        checked = 1
    else:
        try:
            commits = commit_messages(root, f"{BASELINE_COMMIT}..HEAD")
        except subprocess.CalledProcessError as error:
            commits = []
            problems.append(Problem(root, 1, f"git log 실패: {error.stderr.strip()}"))
        for short_hash, message in commits:
            problems += [
                Problem(Path(f"commit {short_hash}"), 1, text)
                for text in check_message(message, statuses, False)
            ]
        checked = len(commits)
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_commits: 문제 {len(problems)}건")
        return 1
    print(f"check_commits: 통과 (커밋 {checked}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
