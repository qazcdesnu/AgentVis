"""Verify that a pull request contains every earlier open pull request.

@doc: docs/VerificationTools.md#9-pr-순서-검사기
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from tools.doclib import REPO_ROOT, Problem, use_utf8_output


def _is_ancestor(root: Path, commit: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=root, capture_output=True
    )
    # Exit code 1 means "not an ancestor"; 128 means the commit is unknown. Both count as missing.
    return result.returncode == 0


def missing_earlier_prs(root: Path, open_prs: list[dict], number: int) -> list[dict]:
    """Return open pull requests numbered before `number` whose head commit HEAD does not contain.

    @doc: docs/VerificationTools.md#9-pr-순서-검사기
    """
    earlier = sorted((pr for pr in open_prs if pr["number"] < number), key=lambda pr: pr["number"])
    return [pr for pr in earlier if not _is_ancestor(root, pr["headRefOid"])]


def main(argv: list[str] | None = None) -> int:
    """Report earlier open pull requests missing from HEAD; return the exit code.

    @doc: docs/VerificationTools.md#9-pr-순서-검사기
    """
    use_utf8_output()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--open-prs", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    open_prs = json.loads(args.open_prs.read_text(encoding="utf-8"))
    problems = [
        Problem(Path(f"PR #{args.pr}"), 1, f"PR #{pr['number']} ({pr['headRefName']})를 포함하지 않음")
        for pr in missing_earlier_prs(root, open_prs, args.pr)
    ]
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_pr_order: 문제 {len(problems)}건")
        return 1
    earlier = sum(pr["number"] < args.pr for pr in open_prs)
    print(f"check_pr_order: 통과 (앞선 열린 PR {earlier}개 포함)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
