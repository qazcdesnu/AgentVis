"""Tests for the task document consistency checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import io
import unittest
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from tools.check_tasks import main

_ROADMAP = """# 로드맵

## M0 기반

- [x] M0-T1 첫 작업
- [~] M0-T2 둘째 작업

## M1 다음

- [ ] M1-T1 할 일
"""
_ISSUE = """# 이슈

- [x] I1 사용자 지시
  - 연결 작업: M0-T1
- [ ] I2 미정 문제
- [~] H1 급한 결함
"""
_ONGOING = """# 진행 중

## M0-T2 둘째 작업

- 시작일: 2026-10-31
- 관련 이슈: I2

## H1 급한 결함

- 시작일: 2026-10-31
"""
_DONE = """# 완료

## M0-T1 첫 작업

- 시작일: 2026-10-30
- 완료일: 2026-10-30

### 결과
- 됨. I1을 함께 처리했다.

### 검증
- 통과
"""


class CheckTasksTest(RepoTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("docs/Roadmap.md", _ROADMAP)
        self.write("docs/Issue.md", _ISSUE)
        self.write("docs/Ongoing.md", _ONGOING)
        self.write("docs/Done.md", _DONE)

    def run_checker(self) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root)])
        return code, output.getvalue()

    def assert_reports(self, *messages: str) -> None:
        code, output = self.run_checker()
        self.assertEqual(code, 1, output)
        for message in messages:
            self.assertIn(message, output)

    def test_consistent_documents_pass(self) -> None:
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_reports_malformed_lines(self) -> None:
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [ ] M1-T1", "- [?] M1-T1").replace("## M1 다음", "## 다음"))
        self.assert_reports("태스크 줄 형식 오류", "마일스톤 제목 형식 오류")

    def test_reports_numbering_gaps_and_wrong_milestone(self) -> None:
        roadmap = _ROADMAP.replace("M0-T2 둘째", "M0-T3 둘째").replace("M1-T1 할 일", "M0-T9 할 일")
        self.write("docs/Roadmap.md", roadmap)
        self.write("docs/Ongoing.md", _ONGOING.replace("M0-T2", "M0-T3"))
        self.write("docs/Issue.md", _ISSUE.replace("I2 미정", "I3 미정"))
        self.assert_reports(
            "태스크 번호 차례 오류: M0-T2이어야 함", "M0-T9가 M0 마일스톤 아래에 있지 않음", "이슈 번호 차례 오류: I2이어야 함"
        )

    def test_reports_status_without_matching_record(self) -> None:
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [ ] M1-T1", "- [x] M1-T1"))
        self.write("docs/Issue.md", _ISSUE.replace("- [~] H1", "- [ ] H1"))
        self.assert_reports("M1-T1: 상태 [x]인데 완료 기록 없음", "H1: 상태 [ ]인데 진행 중 기록 있음")

    def test_reports_record_for_unknown_id(self) -> None:
        self.write("docs/Done.md", _DONE + "\n## M5-T1 유령\n\n- 시작일: 2026-10-29\n- 완료일: 2026-10-29\n\n### 결과\n### 검증\n")
        self.assert_reports("로드맵·이슈에 없는 작업의 기록: M5-T1")

    def test_reports_linked_issue_problems(self) -> None:
        self.write("docs/Issue.md", _ISSUE.replace("- [x] I1", "- [~] I1").replace("- [ ] I2 미정 문제", "- [ ] I2 미정 문제\n  - 연결 작업: M9-T1"))
        self.assert_reports("I1: 상태 [~]가 연결 작업 M0-T1의 [x]와 다름", "I2: 연결 작업 M9-T1가 없음")

    def test_reports_missing_fields_sections_and_order(self) -> None:
        older = "## M0-T9 x\n\n- 시작일: 2026-10-01\n- 완료일: 2026-10-01\n\n### 결과\n### 검증\n\n"
        done = _DONE.replace("## M0-T1", older + "## M0-T1").replace("### 검증\n- 통과\n", "")
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [~] M0-T2", "- [x] M0-T9 x\n- [~] M0-T2"))
        self.write("docs/Done.md", done)
        self.write("docs/Ongoing.md", _ONGOING.replace("- 시작일: 2026-10-31\n- 관련", "- 관련"))
        self.assert_reports("M0-T1: '검증' 절 없음", "M0-T1: 완료 기록은 완료일이 늦은 것부터", "M0-T2: '시작일' 필드 없음")

    def test_ongoing_placeholder_rule(self) -> None:
        self.write("docs/Ongoing.md", _ONGOING + "\n없음\n")
        self.assert_reports("진행 중 기록이 있는데 '없음'이 남아 있음")
        self.write("docs/Roadmap.md", _ROADMAP.replace("- [~] M0-T2", "- [ ] M0-T2"))
        self.write("docs/Issue.md", _ISSUE.replace("- [~] H1", "- [ ] H1"))
        self.write("docs/Ongoing.md", "# 진행 중\n")
        self.assert_reports("진행 중 기록이 없으면 '없음'을 적어야 함")

    def test_reports_unknown_references_even_with_korean_particles(self) -> None:
        self.write("docs/Done.md", _DONE.replace("I1을 함께", "M7-T2으로 옮긴 I9을 `M8-T1`과 함께"))
        code, output = self.run_checker()
        self.assertIn("알 수 없는 작업 ID 참조: M7-T2", output)
        self.assertIn("알 수 없는 작업 ID 참조: I9", output)
        self.assertNotIn("M8-T1", output)


if __name__ == "__main__":
    unittest.main()
