# 진행 중

이 문서는 지금 진행 중인 작업의 상세 내역을 적는다. 작업을 시작하면 항목을 추가하고, 끝나면 항목을 [완료](Done.md)로 옮기고 이 문서에서 지운다. 기록 형식과 흐름은 [작업 관리 규칙](TaskRule.md#4-작업-흐름)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## I31 과업별 정보 요구와 데이터 특성 분석

- 시작일: 2026-11-01
- 근거 문서: [Claude Code 실무 고충 조사](research/ClaudeCodePainPoints.md), [좋은 시각화 원칙 조사](research/VisualizationPrinciples.md), [데이터 소스](DataSource.md)

### 계획
- 6가지 과업마다 사용자가 원본 기록으로 판정하는 절차를 적고, 그 절차에 필요한 정보 항목을 뽑는다.
- 정보 항목을 공통 사전으로 모아 원천 필드, 데이터 유형, 원본·파생, 확정·추정, 규모를 분석한다.
- 과업 × 정보 항목 표로 공통 항목과 과업 전용 항목을 가른다.
- 결과를 `docs/design/TaskAbstraction.md`로 만들고, 인코딩(시각화 방식) 설계의 입력으로 둔다.
- 최신 `main`에서 만든 브랜치 `i31-task-data-abstraction`에서 진행한다.

### 진행 기록
- 2026-11-01: 사용자 지시로 I31을 등록했다. 이 세션 기록에서 도구 결과의 실제 필드를 확인했다. Bash는 `stdout`·`stderr`·`interrupted`, 종료 코드는 오류 텍스트의 "Exit code N", Edit·Write는 `structuredPatch`·`filePath`·`originalFile`, 응답은 `usage`(토큰)를 가진다.
- 2026-11-01: [과업과 데이터 추상화](design/TaskAbstraction.md) 초안을 썼다. 내용은 판정 절차 6개, 정보 항목 40개(D1~D40), 과업 × 정보 표, 데이터 특성에서 나온 설계 함의 6개다. 사용자 검토를 기다린다.

