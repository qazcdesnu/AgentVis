"""Tests for the publishable copy of experiment material.

@doc: docs/design/Study.md#6-테스트
"""

import io
import json
from contextlib import redirect_stderr, redirect_stdout

from agentvis.cli import main
from agentvis.study.scrub import personal_findings, scrub_folder
from tests.support import RepoTestCase

_T = {"sessionId": "s1", "timestamp": "2026-11-13T01:00:00.000Z"}
_LINES = [
    {"type": "session-owner", "accountUuid": "acc-1", "organizationUuid": "org-1", "sessionId": "s1"},
    {"type": "api-request-blob", "systemPrompt": "email alice@corp.io home /Users/alice", **_T},
    {"type": "attachment", "uuid": "t1", "attachment": {"type": "prompt_snapshot", "text": "alice@corp.io"}, **_T},
    {"type": "user", "uuid": "u1", "promptId": "p1", "entrypoint": "sdk-cli", "cwd": "/Users/alice/work/repo", "userEmail": "alice@corp.io",
     "message": {"role": "user", "content": "고쳐 주세요"}, **_T},
    {"type": "assistant", "uuid": "a1", "message": {"content": [{"type": "text", "text": "Co-Authored-By: Claude <noreply@anthropic.com>"}]}, **_T},
]


class ScrubTest(RepoTestCase):
    """@doc: docs/design/Study.md#6-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.source = self.root / "scenario"
        self.write("scenario/t1/s1.jsonl", "".join(json.dumps(line, ensure_ascii=False) + "\n" for line in _LINES))
        self.write("scenario/t1/s1.diff", "--- a//Users/alice/work/repo/x.py\n")
        self.write("scenario/runs.jsonl", json.dumps({"repo": "/Users/alice/repo", "session_id": "s1"}) + "\n")
        self.write("scenario/key.json", json.dumps({"version": 1, "trials": [{"note": "/Users/alice 에서 만듦"}]}))
        self.out = self.root / "public"

    def test_only_read_lines_survive_without_account_fields(self) -> None:
        findings = scrub_folder(self.source, self.out, [("/Users/alice", "/home/study")])
        self.assertEqual(findings, [])
        records = [json.loads(line) for line in (self.out / "t1" / "s1.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([record["type"] for record in records], ["user", "assistant"])
        self.assertNotIn("userEmail", records[0])
        self.assertEqual(records[0]["cwd"], "/home/study/work/repo")
        self.assertIn("/home/study/repo", (self.out / "runs.jsonl").read_text(encoding="utf-8"))
        self.assertIn("/home/study/work", (self.out / "t1" / "s1.diff").read_text(encoding="utf-8"))
        self.assertIn("/home/study", (self.out / "key.json").read_text(encoding="utf-8"))
        # The source folder is left as it was.
        self.assertIn("session-owner", (self.source / "t1" / "s1.jsonl").read_text(encoding="utf-8"))

    def test_leftovers_are_reported(self) -> None:
        findings = scrub_folder(self.source, self.out, [])
        self.assertTrue(any("홈 경로: /Users/alice" in finding and finding.startswith("t1/s1.jsonl:1") for finding in findings), findings)
        self.write("x/a.txt", "bob@corp.io /home/runner/x noreply@anthropic.com me@example.com C:\\\\Users\\\\carol\\\\x")
        self.assertEqual(sorted(finding.split(": ", 1)[1] for finding in personal_findings(self.root / "x")),
                         ["이메일: bob@corp.io", "홈 경로: C:\\\\Users\\\\carol"])

    def test_command(self) -> None:
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            self.assertEqual(main(["study", "scrub", str(self.source), "--out", str(self.out), "--replace", "/Users/alice=/home/study"]), 0)
            self.assertEqual(main(["study", "scrub", str(self.source), "--out", str(self.out)]), 1)
        self.assertIn("개인 정보로 보이는 글 없음", output.getvalue())
        self.assertIn("결과 폴더가 이미 있음", errors.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["study", "scrub", str(self.source), "--out", str(self.root / "public2")]), 1)
