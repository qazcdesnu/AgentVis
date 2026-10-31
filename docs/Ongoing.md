# 진행 중

이 문서는 지금 진행 중인 작업의 상세 내역을 적는다. 작업을 시작하면 항목을 추가하고, 끝나면 항목을 [완료](Done.md)로 옮기고 이 문서에서 지운다. 기록 형식과 흐름은 [작업 관리 규칙](TaskRule.md#4-작업-흐름)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M4-T6 작업 흐름 그래프 상세 설계와 라이브러리(D3) 도입 방침

- 시작일: 2026-10-31
- 근거 문서: [웹 UI 설계](design/WebUI.md), [분석기 설계](design/Analysis.md), [데이터 소스](DataSource.md)
- 관련 이슈: I24

### 계획
- 사용자 지시(I24)를 이슈로 등록하고 로드맵에 M4-T6~M4-T8을 더한다.
- 외부 CDN 미사용 결정을 다시 검토하고, 웹 UI 설계의 라이브러리 방침을 "라이브러리는 써도 되며 저장소에 넣어 쓴다"로 고친다.
- 실제 세션 기록으로 병렬 호출·백그라운드 작업·서브에이전트의 연결 방식을 실측해 데이터 소스에 적는다.
- 작업 흐름 그래프 설계 문서(`docs/design/FlowGraph.md`)를 쓰고, 분석기 설계에 그래프에 필요한 필드를 더한다.
- 라이브러리 방침 중 기계적으로 검사할 수 있는 부분(외부 주소 금지, 저장소에 넣은 파일의 해시)을 검사하는 웹 정적 파일 검사기를 만든다.
- PR로 올라갈 M4-T3 브랜치(`m4-t3-first-screen`) 위에 쌓은 브랜치 `m4-t6-flow-graph-design`에서 진행한다.

### 진행 기록
- 2026-10-31: 사용자가 cascading 목록 대신 `parent` 관계를 이용한 흐름 그래프를 요청했다(I24). 이 세션 기록(4,295개)을 실측한 결과, `parentUuid`는 병렬 도구 호출을 한 줄로 잇고 갈라짐 250곳이 대부분 hook 첨부·도구 결과 같은 곁가지라, 그대로는 실행 구조 그래프가 되지 않음을 확인했다. 사용자와 함께 외부 CDN 미사용 결정을 다시 검토했고, 사용자가 D3를 저장소에 넣어 쓰는 방안을 승인했다.
- 2026-10-31: 실제 이벤트 저장소의 hook 시각으로 한 응답의 병렬 도구 호출을 재 보니, `tool_use` 기록 시각은 생성 시각이고 실제 실행 구간은 `PreToolUse`·`PostToolUse`로만 알 수 있었다(`WebFetch` 4개는 겹쳐 실행, `Write`·`Bash`는 차례로). 백그라운드 작업 알림 10건 모두 띄운 호출의 `<tool-use-id>`를 담고 있었다. [데이터 소스](DataSource.md#35-병렬-실행과-백그라운드-작업의-연결)에 적었다.
- 2026-10-31: [작업 흐름 그래프 설계](design/FlowGraph.md)를 쓰고 [분석기 설계](design/Analysis.md)에 M4-T7 필드를 표시했다. [웹 UI 설계](design/WebUI.md#11-저장소에-넣은-라이브러리)의 라이브러리 방침을 고치고, 그 검사기 `tools/check_web.py`와 테스트를 만들어 검증 명령·CI에 더했다.
- 2026-10-31: I24는 그래프 화면이 생겨야 해결되므로 연결 작업을 M4-T8로 했다. M4-T3 완료 기록이 먼저 `main` 쪽 브랜치에 들어가야 완료 문서 맨 위가 충돌하지 않으므로, M4-T6 완료 처리는 M4-T3 완료 뒤에 한다.

### 결정 사항
- 그래프 단위는 턴 하나다. 줄(주 에이전트·서브에이전트·백그라운드)과 순서를 지키는 압축 시간축으로 그린다. 이유는 [작업 흐름 그래프 설계](design/FlowGraph.md#6-화면)에 있다.
- 외부 CDN 미사용 결정은 유지하고, 라이브러리는 저장소에 넣어 쓴다. D3 파일은 화면을 만드는 M4-T8에서 넣는다.

### 변경 파일
- `docs/Issue.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/DataSource.md`, `docs/Architecture.md`, `docs/index.md`
- `docs/design/FlowGraph.md`(새 문서), `docs/design/WebUI.md`, `docs/design/Analysis.md`
- `docs/VerificationTools.md`, `docs/CodeRule.md`, `CLAUDE.md`, `.github/workflows/verify.yml`
- `tools/check_web.py`, `tests/test_check_web.py`
