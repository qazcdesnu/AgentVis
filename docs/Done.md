# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## M4-T6 작업 흐름 그래프 상세 설계와 라이브러리(D3) 도입 방침

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [웹 UI 설계](design/WebUI.md), [분석기 설계](design/Analysis.md), [데이터 소스](DataSource.md)
- 관련 이슈: I24

### 계획
- 사용자 지시(I24)를 이슈로 등록하고 로드맵에 M4-T6~M4-T8을 더한다.
- 외부 CDN 미사용 결정을 다시 검토하고, 웹 UI 설계의 라이브러리 방침을 "라이브러리는 써도 되며 저장소에 넣어 쓴다"로 고친다.
- 실제 세션 기록으로 병렬 호출·백그라운드 작업·서브에이전트의 연결 방식을 실측해 데이터 소스에 적는다.
- 작업 흐름 그래프 설계 문서(`docs/design/FlowGraph.md`)를 쓰고, 분석기 설계에 그래프에 필요한 필드를 더한다.
- 라이브러리 방침 중 기계적으로 검사할 수 있는 부분(외부 주소 금지, 저장소에 넣은 파일의 해시)을 검사하는 웹 정적 파일 검사기를 만든다.
- PR #9(`m4-t3-first-screen`) 위에 쌓은 브랜치 `m4-t6-flow-graph-design`에서 진행한다.

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

### 결과
- 작업 흐름 그래프의 모델(줄·노드·간선), 조회 API, 화면 배치와 상호작용이 [작업 흐름 그래프 설계](design/FlowGraph.md)에 정해져 M4-T7·M4-T8을 시작할 수 있다.
- 라이브러리는 저장소에 넣어 쓰는 방침과 절차가 [웹 UI 설계](design/WebUI.md#11-저장소에-넣은-라이브러리)에 있고, 웹 정적 파일 검사기가 외부 주소와 넣은 라이브러리의 해시를 검사한다(검증 명령과 CI에 포함).

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 112개 통과(웹 정적 파일 검사기 9개 포함).

## M4-T3 세션 목록과 턴별 작업 흐름 화면

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [웹 UI 설계](design/WebUI.md)

### 계획
- [웹 UI 설계](design/WebUI.md)의 파일을 실제 파일로 링크하고, 서버 앱에 정적 파일 연결을 더한다.
- `index.html`, `app.js`, `style.css`로 프로젝트·세션·세션 상세 화면을 만든다.
- 정적 파일 제공을 테스트하고, 미리보기 서버로 화면을 확인한다.
- PR #8(`m4-t1-ui-design`) 위에 쌓은 브랜치 `m4-t3-first-screen`에서 진행한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: 서버 앱에 `web/` 정적 파일 연결을 조회 API 경로 뒤에 더하고, 세 영역 화면(`index.html`, `app.js`, `style.css`)을 만들었다. 세션 기록의 모든 텍스트는 `textContent`로만 넣는다.
- 2026-10-31: 실제 이벤트 저장소의 사본에 지난 세션 기록을 모두 읽힌 미리보기 서버(포트 8766)를 띄워 사용자가 브라우저로 확인했다.
- 2026-10-31: 화면을 본 사용자가 병렬·백그라운드 작업 흐름을 그래프로 보자고 했다. 다음 PR에서 이슈와 태스크로 등록해 따로 진행하고, 이 목록 화면은 그래프의 상세 보기로 계속 쓴다.

### 결정 사항
- 시각화 라이브러리 없이 접고 펴는 세로 타임라인으로 만들었다([웹 UI 설계](design/WebUI.md#3-턴과-단계-표시)).

### 변경 파일
- `src/agentvis/server.py`, `src/agentvis/web/index.html`, `src/agentvis/web/app.js`, `src/agentvis/web/style.css`
- `tests/test_api.py`
- `docs/design/WebUI.md`, `docs/design/Collector.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- `agentvis serve`를 띄우고 `http://127.0.0.1:<포트>/`를 열면 프로젝트 → 세션 → 턴·단계·도구 호출을 볼 수 있다. 실패가 있거나 진행 중인 턴과 마지막 턴이 펼쳐져 있고, 작업 중 사람 메시지가 강조되며, 선택 상태가 URL 해시에 남는다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits` 통과. 단위 테스트 103개 통과(`GET /`·정적 파일 제공, 조회 API가 정적 파일 연결에 가려지지 않음).
- 브라우저 확인(사용자, 2026-10-31): 프로젝트 목록, 세션 목록, 세션 상세(턴 펼치기, 도구 호출 상세, 사용자 메시지 강조)가 잘 보인다.

## M4-T1 웹 UI 상세 설계와 시각화 라이브러리 선정

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md), [시스템 구조의 기술 선택](Architecture.md#6-기술-선택), [분석기 설계](design/Analysis.md)

### 계획
- `docs/design/WebUI.md`에 화면 구성, 단계 종류별 표시, 기술·라이브러리 선택, 보안 규칙, 파일 구성, 테스트를 정한다.
- 사용자 방침("보면서 나중에 추가하고 고치면 된다")에 따라 권장안으로 정하고, 첫 화면(M4-T3)을 본 뒤 고친다.
- PR #7(`m3-t5-project-api`) 위에 쌓은 브랜치 `m4-t1-ui-design`에서 진행한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: [웹 UI 설계](design/WebUI.md)를 작성했다. 프로젝트·세션·세션 상세의 세 영역, 턴 머리와 단계 종류별 표시, 도구 호출 상태 기호·색, 해시 상태, 보안 규칙(`textContent`만 사용, 외부 요청 없음), 파일 구성, 테스트를 정했다. 인덱스와 [시스템 구조](Architecture.md#6-기술-선택)에 연결했다.

### 결정 사항
- 첫 화면은 시각화 라이브러리 없이 CSS 세로 타임라인으로 만든다. 외부 CDN에 의존하지 않고 오프라인에서도 동작하게 하기 위해서다. 차트·그래프가 필요해지면 라이브러리를 정하고 저장소 안에 둔다.
- 작업 도중 사람이 보낸 메시지(`user_message`)를 가장 강하게 강조한다. 지시 오해(Q6)를 볼 때 가장 중요한 지점이기 때문이다.
- 프로젝트 목록 선택은 첫 화면(M4-T3)에 넣고, 경로 직접 입력은 M4-T5에서 더한다.
- 사용자 방침에 따라 권장안으로 정했으며, 첫 화면을 본 뒤 고친다.

### 변경 파일
- 신규: `docs/design/WebUI.md`
- 수정: `docs/index.md`, `docs/Architecture.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- M4-T3(첫 화면)을 [웹 UI 설계](design/WebUI.md)에 따라 구현할 수 있다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`: 통과

## M3-T5 프로젝트 판정(세션 기록의 첫 `cwd`)과 프로젝트 목록 API (`/api/projects`)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [분석기 설계의 프로젝트](design/Analysis.md#2-프로젝트), [조회 API](design/Analysis.md#8-조회-api)

### 계획
- [분석기 설계](design/Analysis.md#2-프로젝트)의 프로젝트 목록 계산과 응답 형태를 정하고 코드 포인터를 건다. 프로젝트 판정 자체는 M3-T2의 `build_session`에 이미 있다.
- `list_projects`와 `GET /api/projects`를 구현하고 테스트한다.
- PR #6(`i23-probe-isolation`) 위에 쌓은 브랜치 `m3-t5-project-api`에서 진행한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: [분석기 설계](design/Analysis.md#2-프로젝트)에 프로젝트 목록 계산(`list_sessions`의 세션을 프로젝트 경로로 묶음, 경로 없는 세션 제외)과 응답 형태(`{"projects": [...]}`)를 정하고 코드 포인터를 걸었다.
- 2026-10-31: `ProjectView`, `list_projects`, `GET /api/projects`를 구현했다. 테스트를 쓰기 전에, 마지막 활동이 없는 프로젝트의 정렬 기본값(`datetime.min`)이 시간대 없는 값이라 시간대 있는 시각과 비교하면 오류가 나는 버그를 발견해 고쳤다.
- 2026-10-31: 미리보기 사본으로 확인했다. 프로젝트 6개가 마지막 활동 순으로 나왔고, `AI윤리`처럼 세션 기록 디렉터리 이름에서는 사라지는 한글 폴더 이름도 정확히 나왔다. 폴더가 지워진 H2 실측 세션은 `exists`가 거짓이었다.

### 결정 사항
- 프로젝트 판정(세션 기록의 첫 `cwd`)은 M3-T2의 `build_session`이 이미 하므로, 이번 태스크는 묶기와 목록 API만 구현했다.
- 상위 경로는 홈 디렉터리 아래면 `~`로 줄인다.

### 변경 파일
- 수정: `src/agentvis/analysis/catalog.py`, `src/agentvis/server.py`, `tests/test_api.py`, `docs/design/Analysis.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- `GET /api/projects`로 Claude Code를 쓴 프로젝트 목록(이름, 상위 경로, 세션 수, 마지막 활동, 폴더 존재 여부)을 볼 수 있다. M4 화면의 첫 단계(프로젝트 선택)가 이 목록을 쓴다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 102개 통과

## I23 실측용 `claude -p` 세션이 실제 이벤트 저장소에 섞임

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [데이터 소스의 실측 방법](DataSource.md#24-실측-방법)

### 계획
- 실측 세션이 실제 수집에 섞이지 않는 실행 방법을 정하고 문서에 적는다.

### 진행 기록
- 2026-10-31: M3-T4 미리보기에서 `scratchpad/h2/proj` 세션을 발견했다. H2 실측에서 `--settings`로 임시 설정을 더했지만 사용자 설정의 실제 hook도 함께 동작한 것이다. 실제 이벤트 저장소에서 `/private/tmp/` 작업 경로의 세션은 이것 하나(이벤트 5개)였다. M1-T6 실측은 실제 hook 설치(M1-T7) 전이라 영향이 없었다.
- 2026-10-31: `claude --help`에서 `--setting-sources <sources>`(user, project, local 중 불러올 것)를 확인하고, 실측은 `--setting-sources project,local --settings <임시 설정>`으로 하도록 [데이터 소스](DataSource.md#24-실측-방법)에 적었다. 절 번호가 밀려 2.5·2.6절을 가리키는 링크를 고쳤다.

### 결정 사항
- 섞여 들어간 이벤트 5개는 지우지 않는다. 원시 이벤트는 변경하지 않는다는 원칙이 있고, 실제로 일어난 세션이며 다른 프로젝트로 분리되어 분석에 영향이 없다.

### 변경 파일
- 수정: `docs/DataSource.md`(절 추가와 번호 변경), 그 절을 가리키던 문서들, `docs/Issue.md`, `docs/Done.md`

### 결과
- 이후 실측 세션은 실제 이벤트 저장소에 섞이지 않는다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`: 통과

## M3-T4 조회 API (`/api/sessions`, `/api/sessions/{id}`)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [분석기 설계의 조회 API](design/Analysis.md#8-조회-api)

### 계획
- [분석기 설계](design/Analysis.md#8-조회-api)에 응답 형태, 세션 목록 계산 방법, 필요한 이벤트 저장소 조회를 정하고 코드 포인터를 건다.
- 세션 목록·상세 조회 함수와 두 경로를 구현하고 테스트한다.
- PR #4(`m3-t2-analysis-model`) 위에 쌓은 브랜치 `m3-t4-session-api`에서 진행한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: [분석기 설계의 조회 API](design/Analysis.md#8-조회-api)에 응답 형태(`{"sessions": [...]}`, `project` 생략 시 전체), 세션 목록 계산(세션마다 `build_session`), 조회 함수(`catalog` 모듈)를 정하고, [이벤트 저장소 설계](design/Store.md#8-조회-보조)에 `session_ids`를 더했다.
- 2026-10-31: 포인터 검사기가 역방향 포인터 누락 2건을 잡았다. 분석기 설계가 이벤트 저장소 코드를 직접 가리킨 것은 이벤트 저장소 설계를 가리키도록, 서버 코드가 분석기 설계를 근거로 삼는데 분석기 설계가 서버를 가리키지 않은 것은 서버 앱을 링크하도록 고쳤다.
- 2026-10-31: API 테스트 2건이 실패했는데, 세 세션의 테스트 기록에 같은 `uuid`를 써서 중복 제거로 뒤 세션 기록이 저장되지 않은 테스트 자료 문제였다. 세션마다 다른 `uuid`를 쓰게 고쳤다.

### 결정 사항
- 세션 목록은 세션마다 분석기를 계산해 요약만 내보낸다. 지금 규모(세션 수 개, 이벤트 수천 개)에서는 충분하고, 느려지면 세션 단위 캐시를 설계한다.
- FastAPI의 자동 API 문서 화면(`/docs`)을 그대로 둬, 화면(M4)이 생기기 전에도 브라우저에서 조회 API를 시험할 수 있게 한다.

### 변경 파일
- 신규: `src/agentvis/analysis/catalog.py`, `tests/test_api.py`
- 수정: `src/agentvis/server.py`, `src/agentvis/store.py`, `tests/test_store.py`, `docs/design/Analysis.md`, `docs/design/Store.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- `GET /api/sessions[?project=…]`와 `GET /api/sessions/{id}`로 세션 목록과 턴·단계·도구 호출 상세를 JSON으로 볼 수 있다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 101개 통과

## M3-T2 세션·턴·단계·도구 호출 구성

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [분석기 설계](design/Analysis.md)
- 관련 이슈: I18

### 계획
- 서브에이전트 연결 근거를 실측하고 [분석기 설계](design/Analysis.md)의 빈틈을 메운 뒤 코드 포인터를 건다.
- I18: 첨부 기록 중 `queued_command`, `hook_non_blocking_error`를 저장 대상에 넣고, 이벤트 저장소 스키마 3판에서 읽기 커서를 비워 지난 기록을 다시 읽게 한다.
- `src/agentvis/analysis/`에 `build_session`과 모델을 구현하고, 실제 이벤트 저장소의 이 세션으로 결과를 확인한다.
- PR #3(`i22-auto-delete-branches`) 위에 쌓은 브랜치 `m3-t2-analysis-model`에서 진행한다.

### 진행 기록
- 2026-10-31: 로드맵과 연결된 I18을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: 서브에이전트를 띄운 `Agent` 도구의 결과 기록(`toolUseResult`)에 `agentId`가 있고, 서브에이전트 기록의 `agentId`와 같음을 확인했다(이 세션 3건). 메타 파일 이벤트에는 서브에이전트 ID가 남지 않으므로, 연결은 도구 결과의 `agentId`로 한다.
- 2026-10-31: [분석기 설계](design/Analysis.md), [기록 리더 설계](design/Transcript.md#3-기록-변환), [이벤트 저장소 설계](design/Store.md#7-m3-변경)를 먼저 고치고 코드 포인터를 걸었다. 포인터 검사기가 미구현 9건을 보고하는 것을 확인했다.
- 2026-10-31: I18을 구현했다. `attachment` 중 `queued_command`, `hook_non_blocking_error`만 저장하고, 스키마 3판 이동에서 읽기 커서를 비워 지난 기록을 다시 읽게 했다. `attachment` 값이 객체가 아닌 줄에서 오류가 나는 빈틈을 테스트 전에 발견해 고쳤다.
- 2026-10-31: `src/agentvis/analysis/session.py`에 `build_session`과 `SessionView`·`Turn`·`Step`·`ToolCall`을 구현했다. 문맥 압축 뒤 새로 시작된 기록 사슬이 턴을 잃는 경우를 테스트 전에 발견해, 부모로 턴을 찾지 못하면 그 시각 직전의 턴에 넣도록 설계와 코드를 고쳤다.
- 2026-10-31: 실제 이벤트 저장소의 사본(실제 저장소는 스키마를 바꾸지 않기 위해 건드리지 않음)으로 이 세션을 분석했다. 이벤트 1,750개가 21ms에 턴 50개, 도구 호출 401개(실패 14개)로 구성되었다. 작업 중 사람 메시지 5개가 각자 해당 턴에 `user_message`로 들어갔다(예: 2번째 턴의 "파이썬은 무조건 uv 환경에서 써라."). 서브에이전트 기록을 읽자 서브에이전트 3개가 띄운 `Agent` 도구 호출 아래에 연결되었다.
- 2026-10-31: 실제 데이터에서 테스트가 가정하지 못한 기록 두 가지를 찾아 설계부터 고쳤다. 서브에이전트 기록의 첫 지시(부모가 맡긴 지시, 단계로 만들지 않음)와 출처 없는 `isMeta` 안내(`<system-reminder>`, 단계로 만들지 않음)다. 사용자가 `!`로 실행한 셸 명령·출력(`<bash-input>`, `<bash-stdout>`)은 출처 `user_shell` 알림으로 구분했다.

### 결정 사항
- 서브에이전트 연결은 메타 파일이 아니라 띄운 도구 호출의 결과 기록(`toolUseResult.agentId`)으로 한다. 메타 이벤트에는 서브에이전트 ID가 남지 않기 때문이다.
- 실행 중인 실제 서버는 아직 이전 코드다. 이 PR이 병합된 뒤 서버를 다시 띄우면 실제 이벤트 저장소가 3판으로 이동하고 커서가 비어, 다음 hook 이벤트부터 첨부 기록이 채워진다.
- 지난 세션의 서브에이전트 기록은 hook으로 요청되지 않으므로 M2-T4(서버 시작 시 찾기)나 M2-T5(가져오기)에서 채워진다.

### 변경 파일
- 신규: `src/agentvis/analysis/__init__.py`, `src/agentvis/analysis/session.py`, `tests/test_analysis.py`
- 수정: `src/agentvis/transcript.py`, `src/agentvis/store.py`, `tests/test_transcript.py`, `tests/test_store.py`, `docs/design/Analysis.md`, `docs/design/Transcript.md`, `docs/design/Store.md`, `docs/index.md`, `docs/Roadmap.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 한 세션의 원시 이벤트로 턴별 지시 → 사고 과정 → 도구 호출(상태·오류·실행 시간·서브에이전트) → 작업 중 사람 메시지·알림·hook 전달 실패를 구성할 수 있다. M3-T4·M3-T5의 조회 API가 이 결과를 내보낸다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 98개 통과
- 실제 이벤트 저장소 사본 분석: 위 진행 기록 참고

## I22 병합된 PR 브랜치 자동 삭제 설정과 PR 규칙 반영

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시, [PR 규칙](PullRequestRule.md#4-병합)

### 계획
- GitHub 저장소 설정 "Automatically delete head branches"를 켜고 PR 규칙의 병합 후 정리 절차를 고친다.

### 진행 기록
- 2026-10-31: PR #1, #2 병합 후 원격 작업 브랜치를 지우려 했으나 권한 검사에서 원격 브랜치 삭제가 막혔다. 사용자가 명시적으로 지시해 `git push origin --delete i20-pr-rules i21-stacked-prs`로 지웠다. 로컬 브랜치는 `git branch -d`로 지웠다.
- 2026-10-31: 사용자 지시로 `gh api -X PATCH repos/qazcdesnu/AgentVis -F delete_branch_on_merge=true`를 실행해 설정을 켰다. 이 설정은 켠 뒤 병합되는 PR에만 적용된다.

### 결정 사항
- 원격 작업 브랜치 삭제는 GitHub 설정에 맡기고, Claude는 로컬 정리만 한다.

### 변경 파일
- 수정: `docs/PullRequestRule.md`, `docs/Issue.md`, `docs/Done.md`
- GitHub 저장소 설정: `delete_branch_on_merge = true`

### 결과
- PR을 병합하면 원격 작업 브랜치가 자동으로 지워진다.

### 검증
- `gh api` 응답의 `delete_branch_on_merge`: `true`
- `uv run python -m tools.check_docs`, `check_tasks`: 통과

## I21 PR을 번호 순서대로 병합하면 충돌이 생기지 않도록 하는 규칙

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시, [PR 규칙](PullRequestRule.md)

### 계획
- [PR 규칙](PullRequestRule.md)을 바꾼다: 새 작업 브랜치는 병합되지 않은 가장 최근 작업 브랜치에서 만들고, merge commit으로 PR 번호 순서대로 병합하며, 앞 PR을 고치면 뒤 브랜치에 반영한다.
- 기계적으로 검사할 수 있는 "PR은 번호가 앞선 열린 PR을 모두 포함한다"를 검사기와 CI로 만든다.
- 이 작업 자체를 PR #1(`i20-pr-rules`) 위에 쌓은 브랜치(`i21-stacked-prs`)로 진행한다.

### 진행 기록
- 2026-10-31: `i20-pr-rules`에서 `i21-stacked-prs`를 만들고 시작했다. 사용자가 PR #1을 아직 병합하지 않았다.
- 2026-10-31: 원인을 정리했다. 모든 작업이 작업 관리 문서를 고치고 특히 [완료](Done.md)의 맨 위에 기록을 넣으므로, 각 브랜치를 `main`에서 따로 만들면 쌓인 PR이 충돌한다. 또 squash·rebase merge는 커밋을 새로 만들어, 그 커밋을 이미 포함한 뒤 PR과 내용이 겹친다.
- 2026-10-31: [PR 규칙](PullRequestRule.md)을 바꿨다. 새 작업 브랜치는 병합되지 않은 가장 최근 작업 브랜치에서 만들고(없으면 `main`), merge commit으로 PR 번호 순서대로 병합하며, 앞 PR을 고치면 뒤 브랜치에 앞 브랜치를 병합한다(rebase 금지). [작업 관리 규칙](TaskRule.md#41-시작)과 인덱스를 맞췄다.
- 2026-10-31: "PR은 번호가 앞선 열린 PR을 모두 포함한다"를 [PR 순서 검사기](VerificationTools.md#9-pr-순서-검사기)(`tools/check_pr_order.py`)로 만들고, CI에 `gh pr list`로 열린 PR 목록을 받아 검사하는 단계를 넣었다(`pull-requests: read` 권한). 임시 git 저장소 테스트와, 실제 열린 PR(#1)에 대해 이 브랜치가 통과함을 확인했다.

### 결정 사항
- 병합 방식을 I20의 squash merge에서 merge commit으로 바꿨다. `main`의 `Merge pull request #…` 커밋은 커밋 이력 검사에서 제외되므로 커밋 규칙과 충돌하지 않는다.
- PR의 대상은 항상 `main`이다. 앞 PR이 병합되기 전에는 뒤 PR의 변경 목록에 앞 PR의 커밋도 보이지만, 앞 PR이 병합되면 자기 변경만 남는다.

### 변경 파일
- 신규: `tools/check_pr_order.py`, `tests/test_check_pr_order.py`
- 수정: `docs/PullRequestRule.md`, `docs/TaskRule.md`, `docs/VerificationTools.md`, `docs/index.md`, `.github/workflows/verify.yml`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 작업 브랜치를 쌓고 merge commit으로 번호 순서대로 병합하면 충돌이 생기지 않으며, CI가 앞선 PR을 포함하지 않은 PR을 잡는다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 통과
- 실제 열린 PR 목록으로 `check_pr_order --pr 2`: 통과(앞선 열린 PR 1개 포함)

## I20 PR 규칙과 커밋 후 push 규칙 추가

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시, [커밋 규칙](CommitRule.md), [작업 관리 규칙](TaskRule.md)

### 계획
- PR 규칙 문서(`docs/PullRequestRule.md`)에 브랜치 이름, PR 단위·시점, 제목·본문 형식, 병합 방식, CI, push 시점을 정한다.
- PR 템플릿(`.github/pull_request_template.md`)과 CI(`.github/workflows/verify.yml`)를 만든다.
- 커밋 검사기에 PR 제목·브랜치 이름 검사를 더한다(기계적으로 검사할 수 있는 규칙이므로).
- 커밋 규칙, 작업 관리 규칙의 완료 절차, `CLAUDE.md`, 인덱스를 맞춘다.
- 이 작업 자체를 첫 작업 브랜치(`i20-pr-rules`)와 첫 PR로 진행한다.

### 진행 기록
- 2026-10-31: `main`에서 `i20-pr-rules` 브랜치를 만들고 시작했다. 이 컴퓨터에 GitHub CLI(`gh`)가 없어 PR은 push 후 GitHub가 알려 주는 링크로 사용자가 연다.
- 2026-10-31: 사용자 지시로 `brew install gh`로 GitHub CLI 2.103.3을 설치했다. 로그인(`gh auth login`)은 브라우저 인증이 필요해 사용자가 한다. PR 규칙의 PR 만들기를 `gh pr create`로 바꿨다.- 2026-10-31: [PR 규칙](PullRequestRule.md)을 작성했다. 브랜치 이름 `<작업 ID 소문자>-<설명>`, 커밋 후 바로 push, 작업 하나에 PR 하나, 커밋 제목과 같은 PR 제목, [PR 템플릿](../.github/pull_request_template.md), squash merge, 사용자가 병합, CI를 정했다.
- 2026-10-31: 기계적으로 검사할 수 있는 PR 제목·브랜치 이름 규칙을 [커밋 검사기](VerificationTools.md#7-커밋-검사기)의 PR 검사(`--subject`, `--branch`, `check_branch`)로 만들고, 검증 명령 전체와 PR 검사를 실행하는 [CI](VerificationTools.md#8-ci)(`.github/workflows/verify.yml`)를 추가했다.
- 2026-10-31: [커밋 규칙](CommitRule.md)(작업 브랜치에서 커밋 후 push, `main` 직접 커밋 금지, 검사기가 검증하는 범위), [작업 관리 규칙](TaskRule.md#4-작업-흐름)(시작 시 브랜치, 완료 시 커밋·push·PR), `CLAUDE.md`, 인덱스를 맞췄다. [코드 작업 규칙](CodeRule.md#2-디렉터리-구조)의 디렉터리 표에 `.github/`를 넣으면서 I14에서 지적된 `.githooks/` 누락도 함께 고쳤다.

### 결정 사항
- 병합은 squash merge로 해 `main`에 작업당 커밋 하나를 남긴다. GitHub가 붙이는 ` (#번호)`는 커밋 제목 형식에 맞고 길이에만 영향을 준다.
- `main` 보호 규칙(PR 필수, CI 통과 필수)은 GitHub 저장소 설정이라 사용자가 한다.
- 커밋 규칙의 "사용자가 요청할 때 커밋"을 "작업 브랜치에서 커밋 후 push, `main` 반영은 사용자의 PR 병합"으로 바꿨다. 검토 시점이 커밋에서 PR 병합으로 옮겨 갔다.

### 변경 파일
- 신규: `docs/PullRequestRule.md`, `.github/pull_request_template.md`, `.github/workflows/verify.yml`
- 수정: `tools/check_commits.py`, `tests/test_check_commits.py`, `docs/VerificationTools.md`, `docs/CommitRule.md`, `docs/TaskRule.md`, `docs/CodeRule.md`, `docs/index.md`, `CLAUDE.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 모든 변경이 작업 브랜치와 PR을 거쳐 `main`에 합쳐지고, PR마다 CI가 검증 전체와 PR 제목·브랜치 이름을 검사한다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 통과
- `check_commits --subject "I20: …" --branch i20-pr-rules` 통과, 잘못된 제목·브랜치는 문제 3건 보고

## M3-T1 분석기 상세 설계 (파생 모델 스키마, 재계산 방식)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 관련 이슈: I18
- 근거 문서: [시스템 구조의 데이터 모델](Architecture.md#42-파생-모델), [제품 비전](ProductVision.md), [데이터 소스](DataSource.md)

### 계획
- 실제 세션 기록과 hook 이벤트로 턴 경계, 단계 구분, 도구 호출 상태, 서브에이전트 연결, 작업 중 메시지의 위치를 확인한다.
- `docs/design/Analysis.md`에 파생 모델과 계산 규칙, 조회 API 응답 형태를 설계한다.
- 설계 초안을 사용자에게 보여 확인받은 뒤 완료 처리한다(화면에서 무엇을 보게 될지 정하는 설계이기 때문).

### 진행 기록
- 2026-10-31: 사용자 결정으로 로드맵에 우선 진행 순서를 적고 시작했다.
- 2026-10-31: 이 세션의 세션 기록을 조사했다. 사람 입력은 `origin.kind`가 `human`인 `user` 기록(43개, `promptSource`는 `typed`·`suggestion_accepted`)이고, 하위 에이전트 보고는 `peer`·`isMeta`로 구분되었다. 도구 결과 325개가 모두 턴 시작 기록과 같은 `promptId`를 가졌다.
- 2026-10-31: 작업 도중 들어온 사람 메시지가 `queue-operation`으로 큐에 들어간 뒤 `attachment`(`queued_command`, `origin.kind` = `human`)로 모델에게 전달되며, hook 전달 실패가 `attachment`(`hook_non_blocking_error`)로 남는 것을 발견했다. M2에서 `attachment`를 저장하지 않기로 했으므로 I18로 등록하고 M3-T2에 연결했다.
- 2026-10-31: [분석기 설계](design/Analysis.md)를 작성하고 [시스템 구조](Architecture.md#42-파생-모델)와 인덱스에 연결했다. 설계 초안을 사용자에게 보였고, 사용자는 "보면서 나중에 추가하고 고치면 된다"며 권장안대로 확정했다.

### 결정 사항
- 파생 모델은 저장하지 않고 요청할 때마다 원시 이벤트로 계산한다. 이에 따라 [시스템 구조](Architecture.md#3-구성-요소)의 이벤트 저장소 책임에서 파생 모델 저장을 뺐다.
- 사람이 입력한 지시만 턴을 시작한다. 하위 에이전트 보고·작업 알림은 턴 안의 단계다.
- 도구 호출 상태는 확인된 사실만으로 정하고(`success`, `error`, `interrupted`, `running`, `unfinished`), 해석이 필요한 판정은 신호 설계로 미룬다.

### 변경 파일
- 신규: `docs/design/Analysis.md`
- 수정: `docs/Architecture.md`, `docs/index.md`, `docs/Roadmap.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- M3-T2(구성 구현), M3-T4·M3-T5(조회 API)를 [분석기 설계](design/Analysis.md)에 따라 구현할 수 있다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`: 통과

## I19 GitHub 원격 저장소(`qazcdesnu/AgentVis`)에 올리기

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시

### 계획
- 원격 `origin`을 추가하고, 원격 저장소가 비어 있는지 확인한 뒤 커밋된 `main`을 올린다.

### 진행 기록
- 2026-10-31: M3-T1 진행 중 사용자 지시를 받았다. `git remote add origin git@github-qazcdesnu:qazcdesnu/AgentVis.git` 후 `git ls-remote`로 원격이 비어 있음을 확인하고, `git push -u origin main`으로 커밋 18개(`400aabf`까지)를 올렸다. 진행 중이던 M3-T1의 커밋되지 않은 문서는 올리지 않았다.

### 결정 사항
- 커밋된 이력만 올리고 진행 중인 작업은 완료·커밋한 뒤 올린다.

### 변경 파일
- 수정: `docs/Issue.md`, `docs/Done.md`
- git 설정: 원격 `origin`, `main`의 추적 브랜치 `origin/main`

### 결과
- 원격 `main`이 로컬 `main`(`400aabf`)과 같다.

### 검증
- `git ls-remote origin`: `refs/heads/main` = `400aabf`

## M2-T3 hook 이벤트를 받을 때마다 해당 세션 기록 이어 읽기

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [기록 리더 설계](design/Transcript.md#41-hook-이벤트를-받을-때-m2-t3), [수집기 설계](design/Collector.md#2-http-엔드포인트)

### 계획
- 기록 리더 설계 4.1절의 빈틈(읽을 경로 계산, 작업 스레드의 대기열·종료 동작, 테스트용 대기)을 메우고 코드 포인터를 건다.
- `TranscriptReader`와 읽을 경로 계산을 구현하고, 수집기와 `serve`에 연결한다.
- 실제 서버를 다시 띄워 이 세션의 사고 과정·작업 중 메시지가 이벤트 저장소에 쌓이는지 확인한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: [기록 리더 설계 4.1](design/Transcript.md#41-hook-이벤트를-받을-때-m2-t3)의 빈틈을 먼저 메웠다. 읽을 경로 계산(`paths_to_read`), 대기열 동작(기다리는 요청은 합치고 읽는 중 다시 온 요청은 한 번 더), 종료 동작(남은 요청은 버림), 테스트용 대기(`wait_until_idle`)가 대상이었다. [수집기 설계](design/Collector.md)와 [CLI 설계](design/Cli.md)에 연결 방식을 적고, 포인터 검사기가 미구현 6건을 보고하는 것을 확인했다.
- 2026-10-31: `TranscriptReader`와 `paths_to_read`를 구현했다. 수집기는 hook 이벤트를 저장한 뒤 읽기를 요청하고, `serve`는 기록 리더를 시작·정지한다. 스레드를 쓰는 테스트가 있어 전체 테스트를 다섯 번 반복해 모두 통과함을 확인했다.
- 2026-10-31: 실제 서버를 다시 띄웠다. 첫 hook 이벤트에서 이 세션과 ProjInit 세션의 세션 기록이 처음부터 들어왔다. 이 세션에서는 모델 응답 724개, 사용자·도구 결과 362개, 시스템 61개, 작업 중 메시지 20개가 쌓였다. 작업 중 메시지에는 M0-T2 진행 중 사용자가 보낸 "파이썬은 무조건 uv 환경에서 써라."가 있었다.
- 2026-10-31: 실제 대화형 세션에서 `Notification` hook 이벤트(`idle_prompt`, "Claude is waiting for your input")가 들어온 것을 발견해, M1-T6에서 "미확인"이던 [데이터 소스](DataSource.md#23-사용하는-이벤트) 표를 실측으로 고쳤다.

### 결정 사항
- 대기열에 넣는 일은 hook 응답 전에 하되 즉시 끝나고, 실제 읽기는 작업 스레드가 응답과 따로 한다. 응답이 읽기를 기다리지 않게 하기 위해서다.
- 커서가 없는 파일은 처음부터 읽으므로, AgentVis를 켜기 전에 시작된 진행 중 세션도 첫 hook 이벤트 때 시작부터 채워진다.

### 변경 파일
- 수정: `src/agentvis/transcript.py`, `src/agentvis/server.py`, `src/agentvis/cli.py`, `tests/test_transcript.py`, `docs/design/Transcript.md`, `docs/design/Collector.md`, `docs/design/Cli.md`, `docs/DataSource.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- hook 이벤트가 올 때마다 해당 세션 기록이 이어 읽혀, 사고 과정·응답·도구 결과·작업 중 사용자 메시지가 거의 실시간으로 이벤트 저장소에 쌓인다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 84개 통과, 다섯 번 반복 모두 통과
- 실제 서버 실측: 위 진행 기록 참고

## M2-T2 세션 기록 이어 읽기와 원시 이벤트 저장 구현

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [기록 리더 설계](design/Transcript.md), [이벤트 저장소 설계의 M2 변경](design/Store.md#6-m2-변경)
- 관련 이슈: I11

### 계획
- 이벤트 저장소 스키마 2판(읽기 커서), 동시 최초 열기 수정, 잠금 대기 시간, 묶음 저장, 수집 시작 시각 조회를 구현한다(I11 포함).
- 기록 리더의 파일 경로 처리, 기록 변환, 이어 읽기, 서브에이전트 메타 읽기를 구현한다.
- 실제 이벤트 저장소는 백업한 뒤, 사본으로 1판 → 2판 이동을 먼저 확인하고 실제 서버를 새 코드로 다시 띄운다.
- 실제 세션 기록을 임시 이벤트 저장소로 읽어 형식 해석을 확인한다.

### 진행 기록
- 2026-10-31: M2-T2와 연결된 I11을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: [기록 리더 설계](design/Transcript.md) 1~3절과 [이벤트 저장소의 M2 변경](design/Store.md#6-m2-변경)의 심볼을 코드 포인터로 바꾸면서, 빈틈을 문서에서 먼저 메웠다. 기록 루트 밖 경로는 `ValueError`, 아직 없는 파일은 빈 결과, 한 트랜잭션 최대 500줄(`BATCH_LINES`), 메타 파일 읽기 함수 `read_subagent_meta`가 대상이었다. 포인터 검사기가 미구현 14건을 보고하는 것을 확인했다.
- 2026-10-31: 이벤트 저장소를 스키마 2판으로 바꿨다. 버전별 이동 단계(`_MIGRATIONS`), `BEGIN IMMEDIATE` 안에서 버전 재확인, `busy_timeout` 1초, `append_batch`·`cursor`·`first_received_at`이 들어갔다. 기록 리더(`transcript.py`)와 테스트를 작성했다.
- 2026-10-31: 동시 최초 열기 테스트가 간헐적으로 실패했다. 원인을 추적하니 `PRAGMA journal_mode = WAL`이 다른 연결과 겹치면 SQLite가 잠금 대기 없이 바로 `database is locked`를 내는 것이었다(200번 중 10번). 문서에 먼저 적은 뒤 잠금 대기 시간 안에서 다시 시도하게 고쳤고, 4개 스레드로 300번 시험해 실패가 없음을 확인했다. I10 리뷰 때는 10번 중 8번 실패하던 문제다.
- 2026-10-31: 실제 데이터로 확인했다. 실제 이벤트 저장소를 백업(`~/.agentvis/backups/agentvis-before-m2t2-20261030T181259Z.db`, 393개, 1판)하고, 사본에서 2판 이동과 이벤트 보존을 먼저 확인했다. 실제 세션 기록 8개(서브에이전트 기록 포함)를 임시 저장소로 읽어 0.21초에 3,665개를 저장했고, 다시 읽어도 중복이 없었다. 건너뛴 6,970줄은 모두 저장 대상이 아닌 유형이었고 저장 대상 유형에서 놓친 줄은 없었다.
- 2026-10-31: 실제 서버를 새 코드로 다시 띄웠다. 실제 이벤트 저장소가 2판으로 올라갔고(기존 399개 보존, `transcript_cursors` 생성), 이후 hook 이벤트가 계속 저장됨을 확인했다.

### 결정 사항
- 스키마 이동은 버전별 단계 목록으로 관리해, 0판·1판 어느 데이터베이스에서도 차례로 올라가게 했다.
- 묶음 저장은 검증을 먼저 모두 마친 뒤 트랜잭션을 시작해, 검증 실패 시 아무것도 저장하지 않게 했다.
- 이번 태스크는 읽기 기능까지다. hook 수신 시 자동으로 읽는 것은 M2-T3, 서버 시작 시 찾기는 M2-T4에서 붙인다.

### 변경 파일
- 신규: `src/agentvis/transcript.py`, `tests/test_transcript.py`
- 수정: `src/agentvis/store.py`, `tests/test_store.py`, `docs/design/Store.md`, `docs/design/Transcript.md`, `docs/Roadmap.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- 저장소 밖: `~/.agentvis/agentvis.db`(2판으로 이동), 이동 전 백업

### 결과
- 세션 기록을 마지막으로 읽은 위치부터 이어 읽어 원시 이벤트로 저장할 수 있다. 이벤트 저장소는 읽기 커서를 가지며, 동시에 처음 열어도 실패하지 않는다(I11 해결).

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 81개 통과
- 동시 최초 열기 300회 시험, 실제 세션 기록 읽기, 실제 이벤트 저장소 이동: 위 진행 기록 참고

## M2-T1 기록 리더 상세 설계

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [시스템 구조](Architecture.md#31-기록-리더가-실행되는-시점), [데이터 소스](DataSource.md#3-세션-기록-jsonl)
- 관련 이슈: I10, I17, I11

### 계획
- 실제 세션 기록을 조사해 기록과 블록의 대응, 턴 귀속, 중복 제거 키, 서브에이전트 기록, 이어 읽기 조건을 확인한다.
- I10 문서 리뷰가 지적한 M2 관련 문제(서버가 꺼진 동안의 세션 발견, 서브에이전트 기록, 기록·턴 대응, 대량 가져오기 중 잠금)를 설계에 반영한다.
- `docs/design/Transcript.md`를 작성하고 인덱스와 시스템 구조에 연결한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: 로컬 세션 기록 5개(서브에이전트 기록 3개)를 조사했다. `assistant` 기록 1,996개가 모두 내용 블록을 하나씩만 가진다(thinking·text·tool_use가 각각 별도 기록). `promptId`는 `user` 기록에만 있고, `assistant`는 `parentUuid`를 1~20단계 거슬러 올라가야 `promptId`가 있는 기록에 닿는다. `queue-operation`에는 `uuid`가 없다. `api-request-blob` 등 분석과 무관한 기록 유형이 많다. 파일 끝에 줄바꿈 없는 줄은 없었다.
- 2026-10-31: 권한 판정은 모두 `accept`였고 거부(`reject`) 사례는 없었다. 사용자 중단은 `[Request interrupted by user` 문구로 3건 있었다.
- 2026-10-31: 사용자와 두 소스를 비교한 뒤(I17), 세션 기록을 주 내용 출처로, hook을 실시간 신호로 쓰기로 했다. [제품 비전](ProductVision.md#5-결정-사항)의 데이터 수집 결정, [데이터 소스](DataSource.md#1-개요)의 역할과 [두 소스 비교](DataSource.md#4-두-소스-비교), [시스템 구조](Architecture.md)의 흐름·설계 원칙·구성 요소·병합 규칙을 고쳤다. 구성 요소 이름을 "기록 보완기"에서 "기록 리더"로 바꾸고, 로드맵 M2의 제목과 M2-T3·M2-T4 설명을 새 실행 시점에 맞췄다.
- 2026-10-31: 새 구조의 전제("세션 기록은 실시간으로 쓰인다")를 이 세션의 기록 파일로 확인했다. 그 결과 세션 기록은 실행 중인 도구 호출 하나만큼 늦다는 것을 알게 되었다. `tool_use` 기록은 결과가 나온 뒤 결과 기록과 함께 쓰인다. 그래서 "지금 실행 중인 도구"는 hook으로만 바로 알 수 있으며, 이를 [데이터 소스](DataSource.md#4-두-소스-비교)와 기록 리더 설계에 반영했다.
- 2026-10-31: [기록 리더 설계](design/Transcript.md)를 작성했다. I10 문서 리뷰의 M2 관련 지적을 반영했다: 서버가 꺼진 동안의 세션은 기록 루트를 훑어 찾고(커서보다 커진 파일, 수집 시작 이후 새 파일), 서브에이전트 기록과 메타 파일도 읽으며, 기록 하나를 단계 하나로 대응시키고, 가져오기는 500줄 단위 트랜잭션으로 잠금을 짧게 잡는다. [이벤트 저장소 설계](design/Store.md#6-m2-변경)에 스키마 2판(읽기 커서), 묶음 저장, 수집 시작 시각 조회를 더하고, I11의 동시 최초 열기 충돌과 잠금 대기 시간 해결을 넣은 뒤 I11을 M2-T2에 연결했다.

### 결정 사항
- hook 이벤트를 받을 때마다 해당 세션 기록을 이어 읽는다. 파일 감시 장치 없이 거의 실시간으로 내용을 얻기 위해서다.
- 저장하는 세션 기록 유형은 `user`, `assistant`, `system`, `queue-operation`이다. 요청 사본·화면 상태·파일 이력은 분석 질문과 관계없어 건너뛴다.
- 중복 제거 키는 `uuid`, 없으면 줄 원문의 SHA-256이다. 경로·줄 번호는 폴더를 옮기면 바뀌기 때문이다.
- 수집 시작 전의 지난 세션은 자동으로 읽지 않고 `agentvis import`로만 읽는다.
- 기록 리더는 기록 루트(`~/.claude/projects`) 안의 파일만 읽는다.

### 변경 파일
- 신규: `docs/design/Transcript.md`
- 수정: `docs/ProductVision.md`, `docs/DataSource.md`, `docs/Architecture.md`, `docs/design/Store.md`, `docs/design/Collector.md`, `docs/index.md`, `docs/Roadmap.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- M2-T2~M2-T5를 [기록 리더 설계](design/Transcript.md)와 [이벤트 저장소의 M2 변경](design/Store.md#6-m2-변경)에 따라 바로 구현할 수 있다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`: 통과

## H2 수집기가 요청 출처를 검증하지 않아 브라우저의 웹페이지가 가짜 이벤트를 넣을 수 있음

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [수집기 설계](design/Collector.md), [시스템 구조의 설계 원칙](Architecture.md#2-설계-원칙)

### 계획
- Claude Code의 실제 hook 요청 헤더(`Host`, `Origin`, `Content-Type`)를 임시 설정으로 실측한다.
- [수집기 설계](design/Collector.md)에 요청 검증 규칙을 먼저 정한다.
- 서버 앱에 검증을 구현하고, 거부 사례와 정상 사례를 테스트한다.

### 진행 기록
- 2026-10-31: H2를 `[~]`로 바꾸고 시작했다.
- 2026-10-31: 임시 설정과 헤더 기록용 서버로 Claude Code의 실제 hook 요청을 받아 보았다. `Host: 127.0.0.1:<포트>`, `Content-Type: application/json`, `Origin` 없음(클라이언트 `axios/1.15.2`)이어서, 세 가지 검증이 정상 hook을 막지 않음을 확인했다. 실측으로 생긴 임시 세션 기록과 작업 공간은 지웠다.
- 2026-10-31: [수집기 설계](design/Collector.md#21-요청-검증)에 요청 검증 규칙(허용 호스트 이름, `Origin` 거부, `application/json`만 허용)과 실패 응답, 테스트 항목을 먼저 적었다. [데이터 소스](DataSource.md#21-전달-방식)에 요청 헤더 실측을, [시스템 구조](Architecture.md#2-설계-원칙)의 설계 원칙에 브라우저 요청 차단을 반영했다.
- 2026-10-31: `server.py`에 Starlette `TrustedHostMiddleware`와 `Origin`·`Content-Type` 검사를 넣었다. 기존 앱 테스트는 테스트 클라이언트의 기본 `Host: testserver`와 빈 `Content-Type` 때문에 실패했고, 설계대로 실제 hook과 같은 `Host`·`Content-Type`을 쓰게 고쳤다.
- 2026-10-31: 실행 중이던 실제 서버를 정상 종료하고 새 코드로 다시 띄웠다. 실제 서버에서 `Origin` 요청 403, `text/plain` 요청 415, 다른 `Host` 요청 400을 받고 하나도 저장되지 않았으며, 이 세션의 실제 hook 이벤트는 계속 저장됨을 확인했다. 다시 시작하는 몇 초 동안의 이벤트는 받지 못했으며, 이는 M2의 기록 보완이 메울 범위다.

### 결정 사항
- `Host` 검사는 모든 경로에 적용한다. 이후 M3의 조회 API가 DNS 리바인딩으로 읽히는 것도 같은 방식으로 막기 위해서다.
- `Origin`은 값과 관계없이 거부한다. 지금 `/hooks`를 부르는 브라우저 화면이 없기 때문이다. M4에서 웹 UI가 POST를 보내게 되면 그때 자기 출처만 허용하도록 설계를 고친다.

### 변경 파일
- 수정: `src/agentvis/server.py`, `tests/test_collector.py`, `docs/design/Collector.md`, `docs/DataSource.md`, `docs/Architecture.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 같은 컴퓨터의 브라우저 웹페이지나 DNS 리바인딩으로 가짜 이벤트를 넣을 수 없다. 실제 Claude Code hook은 그대로 수집된다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 통과(수집기 테스트 8개 포함)
- 실제 서버 실측: 위 진행 기록 참고

## I10 지금까지의 작업 전체 리뷰와 문제 점검

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시

### 계획
- 작성자의 가정에 묶이지 않도록, 결론을 주지 않은 독립 리뷰어 둘에게 코드 리뷰와 문서·규칙 리뷰를 나눠 맡긴다.
- 리뷰 결과를 직접 재현·확인해 사실인 것만 남기고, 확인된 문제를 이슈로 등록한다.

### 진행 기록
- 2026-10-31: I10을 등록하고 시작했다.
- 2026-10-31: 코드 리뷰어와 문서·규칙 리뷰어 둘에게 작성자의 결론 없이 대상 경로만 주고, 실행으로 확인한 것만 보고하게 했다. 실제 설정 파일·실행 중인 서버·`~/.agentvis`는 건드리지 않도록 했다.
- 2026-10-31: 보고된 문제를 직접 재현했다. 다른 출처·호스트 이름의 가짜 이벤트 저장, 동시 최초 열기 실패(10번 중 8번), 진행 중 기록 안 "없음"의 오판정, 권한 유지 테스트의 무력함이 재현됐다. 문서 쪽에서는 시스템 구조의 hook 예시 URL, 디렉터리 표의 `.githooks/` 누락, 갱신되지 않은 기술 4건, 커밋 검사기가 작업 트리를 읽는 점을 확인했다. 문서 리뷰가 예로 든 `TaskRule.md`의 번호 없는 제목은 코드 블록 안의 예시여서 위반이 아니었다.

### 결정 사항
- 확인된 문제를 성격별로 이슈로 등록했다: H2(수집기 출처 검증, 실제 서버가 실행 중이라 핫픽스), I11(이벤트 저장소 동시 열기), I12(검사기 판정 오류), I13(입력·오류 처리), I14(문서 갱신 누락·형식 규칙), I15(ProjInit 전환과 규칙 원칙 충돌), I16(권한 거부·중단 신호의 확정 시점).
- M2 설계와 관련된 지적(서버가 꺼진 동안의 세션 발견, 서브에이전트 기록, 기록·턴 대응, 대량 가져오기 중 잠금)은 진행 중인 M2-T1에서 반영한다.
- 리뷰어가 "가설"로 표시한 항목 중 확인하지 못한 것(브라우저가 실제로 요청을 보내는지, 설정 파일 동시 쓰기)은 해당 이슈를 처리할 때 확인한다.

### 변경 파일
- 수정: `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 검사기가 잡지 못한 결함과 문서 불일치가 이슈 7건으로 정리되었다.

### 검증
- `uv run python -m tools.check_docs`, `check_tasks`: 통과

## M1-T7 실제 Claude Code 세션으로 M1 완료 기준 확인

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [시스템 구조](Architecture.md#8-구현-순서), [CLI 설계](design/Cli.md#34-hooks-명령)

### 계획
- 사용자 승인에 따라 실제 `~/.claude/settings.json`에 `agentvis hooks install`로 hook을 설치한다.
- `agentvis serve`를 띄우고, 실제 Claude Code 세션(이 세션)의 작업 이벤트가 `~/.agentvis/agentvis.db`에 쌓이는지 확인한다.
- M1 완료 기준: "실제 Claude Code 세션의 hook 이벤트가 이벤트 저장소에 쌓인다."

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: 설치 전 `~/.claude/settings.json`은 `{"theme": "dark"}`였고 `~/.agentvis`는 없었다. `agentvis serve`를 백그라운드로 띄운 뒤 `agentvis hooks install`을 실행했다. 14개 이벤트가 추가되고 `theme`은 그대로였으며, 백업(`~/.agentvis/backups/settings-20261030T173631155420Z.json`)이 원래 내용과 같았다.
- 2026-10-31: Claude Code가 바뀐 설정을 실행 중인 세션에 바로 적용해, 설치 직후부터 이벤트가 쌓였다. 이 세션(AgentVis)뿐 아니라 동시에 실행 중이던 ProjInit 세션과 RecommandShopping 세션의 이벤트도 들어와, 세 프로젝트의 18개 이벤트가 `cwd`로 구분되어 저장되었다.
- 2026-10-31: RecommandShopping 세션의 이벤트 `cwd`가 프로젝트 폴더가 아니라 하위 폴더(`…/backend`)였다. 세션 기록의 시작 경로는 `…/RecommandShopping`이므로, 프로젝트 판정 기준을 "세션의 첫 `cwd`"에서 "세션 기록의 첫 `cwd`"로 [데이터 소스](DataSource.md#26-실측으로-확인한-동작), [시스템 구조](Architecture.md#42-파생-모델), [이벤트 저장소 설계](design/Store.md#3-자료형), [로드맵](Roadmap.md)(M3-T5)에서 바로잡았다.

### 결정 사항
- 실제 설정에 설치한 hook은 그대로 둔다. 서버가 꺼져 있어도 Claude Code 작업은 막히지 않으며(M0-T4 실측), 이후 작업(M2 이후)에서 실제 데이터를 계속 쌓기 위해서다. 되돌리려면 `uv run agentvis hooks uninstall`을 실행한다.
- 원시 이벤트에 `cwd`를 해석 없이 저장한 결정(I9)이 맞았다. 프로젝트 판정 기준을 바꿔도 이미 쌓인 데이터를 다시 수집할 필요가 없다.

### 변경 파일
- 수정: `docs/DataSource.md`, `docs/Architecture.md`, `docs/design/Store.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`
- 저장소 밖: `~/.claude/settings.json`(AgentVis hook 14개 설치), `~/.agentvis/agentvis.db`, `~/.agentvis/backups/`

### 결과
- M1 완료 기준 "실제 Claude Code 세션의 hook 이벤트가 이벤트 저장소에 쌓인다"를 충족했다. 실행 중인 여러 프로젝트의 세션 이벤트가 실시간으로 저장된다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 68개 통과
- `~/.agentvis/agentvis.db`: 세 세션(AgentVis, ProjInit, RecommandShopping)의 `PreToolUse`·`PostToolUse` 이벤트 저장 확인

## M1-T6 "문서" 표기 hook 이벤트를 실측해 데이터 소스 문서 갱신

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [데이터 소스](DataSource.md#23-사용하는-이벤트)

### 계획
- 임시 데이터 디렉터리로 `agentvis serve`를 띄우고, 임시 설정 파일에 `agentvis hooks install --settings`로 hook을 설치한 뒤, 그 설정으로 `claude -p`를 실행해 이벤트를 수집한다. 실제 `~/.claude/settings.json`은 건드리지 않는다.
- 대상: `PermissionRequest`, `PermissionDenied`, `Notification`, `SubagentStart`, `SubagentStop`, `StopFailure`, `PreCompact`, `PostCompact`.
- 수집한 이벤트로 [데이터 소스](DataSource.md#23-사용하는-이벤트) 표의 "확인" 열과 필드를 고친다. 비대화 모드에서 일으킬 수 없는 이벤트는 사유와 함께 "미확인"으로 적는다.
- 실측으로 생긴 임시 세션 기록은 끝나고 지운다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: 임시 `AGENTVIS_HOME`으로 `agentvis serve --port 8797`을 띄우고, 임시 설정 파일에 `agentvis hooks install --settings`로 hook을 설치한 뒤 `claude -p`(Claude Code 2.1.314)를 세 번 실행했다. 서브에이전트 실행과 허용하지 않은 Write 시도, 같은 세션의 `/compact`, 존재하지 않는 모델 지정이었다. 수집기·이벤트 저장소·설치 명령을 실제 Claude Code와 함께 처음 시험한 것이기도 하다. 이벤트 18개가 저장되었다.
- 2026-10-31: `PermissionRequest`, `SubagentStart`/`SubagentStop`, `StopFailure`, `PreCompact`/`PostCompact`를 실측으로 확인했다. `PermissionDenied`는 위험한 명령을 일부러 시켜야 해서, `Notification`은 비대화 모드에서 일으킬 수 없어서 "미확인"으로 남겼다.
- 2026-10-31: `SessionStart`가 `http` hook으로 한 번도 오지 않았다. 공식 hooks 문서에서 `SessionStart`는 `command`, `mcp_tool` hook만 지원한다는 문장을 확인했다. M1-T5의 `HOOK_EVENTS`가 지원하지 않는 이벤트를 등록하고 있었으므로, 문서를 먼저 고친 뒤 `HOOK_EVENTS`에서 빼고 테스트를 맞췄다(15개 → 14개).
- 2026-10-31: 분석에 영향을 주는 동작을 [실측으로 확인한 동작](DataSource.md#26-실측으로-확인한-동작)에 정리했다. 권한이 없어 막힌 도구는 완료 이벤트가 없다는 점, 서브에이전트 이벤트의 `agent_id`, `/compact` 요약 서브에이전트의 `SubagentStop`이 대상이다. 서브에이전트 기록 파일의 위치와 메타 파일 구조도 [세션 기록 위치](DataSource.md#31-위치)에 적었다.
- 2026-10-31: 실측 세션 기록(`~/.claude/projects/…-scratchpad-m1t6-proj/`, 세션 2개와 서브에이전트 기록)과 임시 작업 공간을 지웠다. 지우기 전에 작업 경로가 모두 실측용 임시 폴더임을 확인했다. 실제 `~/.claude/settings.json`은 바뀌지 않았다.

### 결정 사항
- `SessionStart`는 수집하지 않는다. 세션 시작 시각은 첫 이벤트로, 시작 종류는 세션 기록으로 판정한다. 이벤트 하나 때문에 `http`와 다른 hook 방식(`command`)을 섞지 않기 위해서다.
- 수집기 테스트의 "`prompt_id` 없는 본문" 예시를 실제로 오지 않는 `SessionStart` 대신 실측한 `SessionEnd`로 바꿨다.

### 변경 파일
- 수정: `docs/DataSource.md`, `docs/Architecture.md`, `docs/design/Cli.md`, `docs/design/Collector.md`, `src/agentvis/hook_settings.py`, `tests/test_hook_settings.py`, `tests/test_cli.py`, `tests/test_collector.py`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`
- 삭제(저장소 밖): 실측 세션 기록 디렉터리

### 결과
- 사용하는 hook 이벤트 14개 중 12개가 실측으로 확인되었고, 실제 Claude Code의 `http` hook → 수집기 → 이벤트 저장소 흐름이 동작함을 확인했다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 68개 통과

## M1-T5 `agentvis hooks install` / `uninstall` 명령 구현

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [CLI 설계](design/Cli.md#3-hook-설정-편집), [데이터 소스](DataSource.md#23-사용하는-이벤트)

### 계획
- [CLI 설계](design/Cli.md)의 hook 설정 편집과 명령 동작의 빈틈을 메우고 코드 포인터를 건다.
- `src/agentvis/hook_settings.py`와 `cli.py`의 `hooks install`, `hooks uninstall`을 구현한다.
- 테스트는 임시 설정 파일로만 한다. 실제 `~/.claude/settings.json`은 이 태스크에서 건드리지 않는다(실제 설치는 M1-T7에서 사용자 확인 후).

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: 실제 사용자 설정을 고치는 기능이라 설계의 빈틈을 먼저 메웠다. 심볼릭 링크 설정 파일(dotfiles)을 일반 파일로 덮지 않기, 파일 권한 유지, 예상과 다른 구조는 덮어쓰지 않고 `SettingsError`, 변경이 없으면 백업도 만들지 않기, 백업 이름 충돌 방지, 사용자 hook과 섞인 그룹 처리, 명령의 출력·종료 코드가 대상이었다. 그런 뒤 코드 포인터를 걸고 포인터 검사기가 미구현 13건을 보고하는 것을 확인했다.
- 2026-10-31: `hook_settings.py`와 `cli.py`의 `hooks install`/`uninstall`을 작성했다. 처음 쓴 코드에서 도움말 처리와 기본 경로 채우기가 읽기 어려워 처리 함수 안으로 옮겨 정리했다.
- 2026-10-31: 모든 테스트는 임시 설정 파일로만 실행했다. 작업 후 실제 `~/.claude/settings.json`의 수정 시각(10월 19일)이 그대로이고 AgentVis hook이 없음을, `~/.agentvis`가 생기지 않았음을 확인했다.

### 결정 사항
- 이벤트 그룹에 `matcher`를 두지 않는다. 도구 이벤트도 모든 도구를 받아야 하기 때문이다. `matcher` 없는 `http` hook 그룹이 동작하는 것은 M0-T4 실측에서 확인했다.
- 설치는 "기존 AgentVis hook 제거 후 추가"로 구현해, 여러 번 실행하거나 포트를 바꿔도 hook이 하나씩만 남게 했다.
- 변경 여부는 설정 객체 비교로 판단한다. 바뀌지 않으면 파일, 백업 모두 손대지 않는다.

### 변경 파일
- 신규: `src/agentvis/hook_settings.py`, `tests/test_hook_settings.py`
- 수정: `src/agentvis/cli.py`, `tests/test_cli.py`, `docs/design/Cli.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- `uv run agentvis hooks install`로 Claude Code 사용자 설정에 15개 이벤트의 AgentVis hook을 설치하고, `uninstall`로 AgentVis hook만 제거할 수 있다. 바꾸기 전 설정은 `~/.agentvis/backups/`에 백업된다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 68개 통과
- 실제 설정 파일 무변경 확인: 위 진행 기록 참고

## M1-T4 `agentvis serve` 명령 구현

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [CLI 설계](design/Cli.md#2-명령), [수집기 설계](design/Collector.md#2-http-엔드포인트)

### 계획
- [CLI 설계](design/Cli.md)의 `serve` 동작(시작 안내, 포트 검증, 포트 충돌, 종료 시 정리)을 명확히 하고 코드 포인터를 건다.
- `cli.py`에 `serve` 하위 명령을 추가하고 테스트한다.
- 실제로 서버를 띄워 hook 이벤트를 POST하고 저장되는지 확인한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: [CLI 설계](design/Cli.md#21-serve)에 `serve`의 세부 동작(기본 포트 상수, 포트 검증, 시작 안내, 종료 시 정리, 포트 충돌)과 테스트 항목을 먼저 적었다. 이벤트 저장소 기본 경로를 코드 포인터로 걸었다가 포인터 검사기가 역방향 포인터 누락을 보고해, 근거 문서인 [이벤트 저장소 설계](design/Store.md#1-데이터-디렉터리)를 가리키도록 고쳤다.
- 2026-10-31: `cli.py`에 `serve` 하위 명령과 `DEFAULT_PORT`를 추가하고, `uvicorn.run`을 가짜로 바꾼 테스트를 작성했다.
- 2026-10-31: 임시 데이터 디렉터리로 실제 서버를 띄워 확인했다. `/health`, `POST /hooks` 저장, 잘못된 본문 400, SIGINT 정상 종료, 스키마 버전 1·WAL 모드가 설계대로였다. 종료 후 WAL 파일이 0바이트로 정리되어 이벤트 저장소가 닫혔음을 확인했다.
- 2026-10-31: 실측에서 설계와 다른 점 두 가지를 찾아 문서부터 고쳤다. 포트 충돌 시 종료 코드는 1이 아니라 uvicorn의 시작 실패 코드 3이었다(uvicorn 소스의 `sys.exit(STARTUP_FAILURE)`로 확인). 출력이 터미널이 아닐 때 시작 안내가 uvicorn 로그보다 늦게 나와 `flush`를 추가했다.

### 결정 사항
- `serve`는 `--host` 옵션 없이 `127.0.0.1`에만 바인딩한다([설계 원칙](Architecture.md#2-설계-원칙)).
- 포트 충돌 같은 uvicorn의 종료 코드는 그대로 전달한다. 감싸서 바꾸면 원인을 알아보기 어려워진다.

### 변경 파일
- 수정: `src/agentvis/cli.py`, `tests/test_cli.py`, `docs/design/Cli.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- `uv run agentvis serve [--port N]`으로 로컬 서버를 띄우면 hook 이벤트를 받아 `~/.agentvis/agentvis.db`에 저장한다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 54개 통과
- 실제 서버 실측: 위 진행 기록 참고

## M1-T3 수집기 구현

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [수집기 설계](design/Collector.md), [데이터 소스](DataSource.md#2-hook-이벤트)

### 계획
- [수집기 설계](design/Collector.md)의 빈틈을 메우고 구현 심볼을 코드 포인터 링크로 바꾼다.
- `src/agentvis/collector.py`(이벤트 변환)와 `src/agentvis/server.py`(`create_app`, `POST /hooks`, `GET /health`)를 구현한다.
- `tests/test_collector.py`로 설계 문서의 테스트 항목을 확인한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: 설계의 모순을 발견했다. `payload`에 본문 원문 바이트를 남기라면서 경로 처리 함수를 동기 함수로 쓰라고 했는데, FastAPI 동기 함수에서는 원문 바이트를 직접 읽을 수 없다. 문서를 먼저 고쳐 `async def`로 원문을 읽고 SQLite 저장만 스레드 풀로 넘기게 했다. 함께 예외 메시지, 400 응답 내용, 테스트 항목(문자열이 아닌 선택 필드, 모르는 이벤트, 쿼리 문자열)을 보강하고 코드 포인터를 걸었다. 포인터 검사기가 미구현 6건을 보고하는 것을 확인했다.
- 2026-10-31: `collector.py`, `server.py`, `tests/test_collector.py`를 작성했다. 테스트 본문은 실측한 `PostToolUseFailure`의 필드 구성을 따랐다.
- 2026-10-31: 테스트 실행 중 Starlette 1.10의 `StarletteDeprecationWarning`("`httpx` 대신 `httpx2`를 설치하라")을 발견했다. [CLI 설계](design/Cli.md#1-패키지-골격)를 먼저 고친 뒤 `uv remove --dev httpx`, `uv add --dev httpx2`로 바꾸고 경고가 사라진 것을 확인했다.

### 결정 사항
- 수집기의 `InvalidHookEvent`는 `ValueError`를 상속한다. 변환 실패는 잘못된 입력 값이기 때문이다.
- 성공 응답은 빈 JSON 객체 `{}` 하나로 고정했다. 테스트에서 응답 바이트가 정확히 `{}`인지 확인한다.

### 변경 파일
- 신규: `src/agentvis/collector.py`, `src/agentvis/server.py`, `tests/test_collector.py`
- 수정: `docs/design/Collector.md`, `docs/design/Cli.md`, `pyproject.toml`, `uv.lock`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- `create_app(store)`로 만든 앱이 `POST /hooks`로 hook 이벤트를 받아 이벤트 저장소에 원문 그대로 저장하고, `GET /health`로 동작을 확인할 수 있다. M1-T4의 `agentvis serve`가 이 앱을 실행하면 된다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 50개 통과, 경고 없음

## M1-T2 이벤트 저장소 구현

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [이벤트 저장소 설계](design/Store.md), [시스템 구조](Architecture.md#41-원시-이벤트)

### 계획
- [이벤트 저장소 설계](design/Store.md)의 구현 심볼을 코드 포인터 링크로 바꾼다.
- `src/agentvis/store.py`에 데이터 디렉터리, 스키마, `RawEvent`, `EventStore`를 구현한다.
- `tests/test_store.py`로 설계 문서의 테스트 항목을 확인한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: 설계를 다시 읽고 구현 전에 빈틈을 문서에서 메웠다. 스키마 버전 오류의 이름(`SchemaVersionError`), "시간대 보존"의 뜻(같은 시점을 UTC로 보존), 잘못된 `source`·시간대 없는 시각의 처리(`ValueError`), 중복 처리 방식(`ON CONFLICT DO NOTHING`)이 대상이었다. 그런 뒤 구현 심볼을 코드 포인터로 바꾸고, 포인터 검사기가 미구현 11건을 보고하는 것을 확인했다.
- 2026-10-31: `src/agentvis/store.py`와 `tests/test_store.py`를 작성했다.
- 2026-10-31: 설계의 "여러 스레드에서 쓸 수 있다"를 확인하는 테스트가 없어서, 설계 문서의 테스트 항목에 먼저 추가한 뒤 스레드 4개가 동시에 200건을 저장하는 테스트를 작성했다.

### 결정 사항
- 스키마 버전을 다른 어떤 설정보다 먼저 확인한다. 더 새로운 버전의 데이터베이스는 WAL 설정조차 바꾸지 않고 거부한다. 테스트로 확인했다.
- 스키마 생성은 한 트랜잭션 안에서 `user_version` 설정까지 함께 한다. 중간에 실패해도 반쯤 만들어진 스키마가 현재 버전으로 표시되지 않게 하기 위해서다.
- 연결은 자동 커밋 모드로 열어 이벤트 하나를 저장할 때마다 바로 디스크에 반영한다.
- 읽기와 쓰기 모두 잠금 하나로 직렬화한다. 연결 하나를 여러 스레드가 공유하기 때문이다.

### 변경 파일
- 신규: `src/agentvis/store.py`, `tests/test_store.py`
- 수정: `docs/design/Store.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 원시 이벤트를 `cwd`와 함께 저장·조회하는 이벤트 저장소가 생겼다. M1-T3 수집기가 이를 써서 hook 이벤트를 저장할 수 있다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 44개 통과(이벤트 저장소 8개 포함)

## I9 프로젝트 폴더를 선택해 그 프로젝트를 시각화하는 방식 반영

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시, [제품 비전](ProductVision.md)

### 계획
- [제품 비전](ProductVision.md)의 범위와 결정 사항에 프로젝트 단위 보기를 넣는다.
- [데이터 소스](DataSource.md)에 세션 기록 디렉터리 이름으로는 원래 경로를 되돌릴 수 없으니 `cwd`를 쓴다는 내용을 넣는다.
- [시스템 구조](Architecture.md)의 데이터 모델·API에 `cwd`, 프로젝트 모델, 프로젝트 목록 API를 넣는다.
- [이벤트 저장소 설계](design/Store.md), [수집기 설계](design/Collector.md)에 `cwd` 열을 넣는다.
- [로드맵](Roadmap.md)에 프로젝트 목록 API와 프로젝트 선택 화면 태스크를 추가한다.

### 진행 기록
- 2026-10-31: I9를 등록하고 시작했다. 실제 `~/.claude/projects/` 다섯 개를 조사해, 디렉터리 이름은 한글이 사라지고(`AI윤리` → `AI--`) `-`와 `/`가 구분되지 않지만 기록의 `cwd`는 다섯 개 모두 원래 경로와 정확히 일치함을 확인했다.
- 2026-10-31: 계획한 문서를 모두 고쳤다. 수집기 테스트 항목, 구현 순서의 M4 완료 기준, 인덱스의 제품 비전 설명도 함께 맞췄다.

### 결정 사항
- 보기 단위는 프로젝트 폴더다. 화면은 프로젝트 선택에서 시작한다([제품 비전](ProductVision.md#5-결정-사항)).
- hook은 전역으로 설치해 모든 프로젝트의 이벤트를 모으고 화면에서 프로젝트별로 본다. 프로젝트를 선택하기 전의 작업도 놓치지 않기 위해서다.
- 브라우저 폴더 선택 창은 실제 절대 경로를 주지 않으므로, 세션 기록에서 찾은 프로젝트 목록과 경로 직접 입력을 쓴다.
- 프로젝트 목록은 세션 기록 디렉터리 이름이 아니라 기록의 `cwd`로 만든다. 디렉터리 이름 변환은 정보를 잃기 때문이다([데이터 소스](DataSource.md#31-위치)).
- 이벤트 저장소에는 "프로젝트" 대신 이벤트에 적힌 `cwd`를 그대로 저장한다. 세션 중 작업 경로가 바뀔 수 있어 프로젝트는 해석이 필요한 정보이므로, 원시 이벤트에는 사실만 두고 프로젝트는 분석기가 세션의 첫 `cwd`로 판정한다(M3-T5).

### 변경 파일
- 수정: `docs/ProductVision.md`, `docs/DataSource.md`, `docs/Architecture.md`, `docs/design/Store.md`, `docs/design/Collector.md`, `docs/Roadmap.md`, `docs/index.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 프로젝트 폴더 단위 보기가 제품 결정, 데이터 모델, API, 로드맵(M3-T5, M4-T5)에 반영되어, M1-T2 이벤트 저장소를 `cwd` 열을 포함해 구현할 수 있다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 36개 통과

## H1 `.venv`의 파일에 macOS 숨김 속성이 붙어 `agentvis` 패키지를 불러오지 못함

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [이슈](Issue.md)

### 계획
- 사용자가 iCloud Drive의 "데스크탑 및 문서 폴더"를 끄고 파일을 로컬로 옮긴 뒤, 이전 상태와 같은지 확인한다.
- iCloud가 붙인 속성이 남은 `.venv`를 지우고 다시 만든 뒤, 숨김 속성이 다시 붙지 않는지 확인한다.

### 진행 기록
- 2026-10-31: 사용자가 바탕화면·문서 백업(`~/Backup/Desktop-2026-10-31`, `~/Backup/Documents-2026-10-31`) 후 iCloud 동기화를 끄고 파일을 옮겼다. 백업과 비교해 파일·폴더·링크 수, 용량, 체크섬이 모두 같고 두 폴더에 iCloud 연결 속성이 없음을 확인했다.
- 2026-10-31: iCloud 동기화 해제 전 `.venv`의 `site-packages` 항목 36개가 모두 숨김 속성이었다. `.venv`를 지우고 `uv sync`로 다시 만들자 0개가 되었고, 60초 동안 지켜봐도 다시 붙지 않았다(해제 전에는 5초 안에 다시 붙었다).
- 2026-10-31: 임시 조치 없이 검증을 모두 통과했다.

### 결정 사항
- 원인은 `~/Desktop`의 iCloud Drive "데스크탑 및 문서 폴더" 동기화로 판단한다. 동기화를 끄자 현상이 사라졌다.
- 해결 후보 중 `.nosync` 이름 변경이나 프로젝트 이동 대신, 사용자가 iCloud 동기화 자체를 끄는 것으로 정했다.
- ProjInit의 `.venv`에도 이전에 붙은 숨김 속성이 남아 있을 수 있다. ProjInit은 별도 세션에서 작업 중이므로 이 작업에서 건드리지 않는다.

### 변경 파일
- 수정: `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- 저장소 밖: `.venv` 재생성(git으로 관리하지 않음)

### 결과
- `agentvis` 패키지를 임시 조치 없이 불러올 수 있고, 테스트가 정상 실행된다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 36개 통과(임시 조치 없음)
- `uv run agentvis --version`: `agentvis 0.1.0`

## I8 데이터 저장 구성 요소의 이름을 "저장소"에서 "이벤트 저장소"로 변경

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시

### 계획
- 데이터 저장 구성 요소를 가리키는 "저장소"를 "이벤트 저장소"로 바꾼다.
- git 저장소를 뜻하는 곳 중 헷갈릴 만한 곳은 "git 저장소"로 분명히 적는다.

### 진행 기록
- 2026-10-31: I8을 등록하고 시작했다.
- 2026-10-31: 데이터 저장 구성 요소를 뜻하는 "저장소"를 [시스템 구조](Architecture.md), [로드맵](Roadmap.md), [문서 인덱스](index.md), [이벤트 저장소 설계](design/Store.md), [수집기 설계](design/Collector.md), [CLI 설계](design/Cli.md), [작업 관리 규칙](TaskRule.md)과 [커밋 규칙](CommitRule.md)의 예시에서 "이벤트 저장소"로 바꿨다.
- 2026-10-31: git 저장소를 뜻하는 곳 중 [커밋 규칙](CommitRule.md)의 hook 설명과 [코드 작업 규칙](CodeRule.md)의 `uv.lock` 설명을 "git 저장소"로 분명히 적었다.
- 2026-10-31: 검증 중 `tests.test_cli`가 `agentvis`를 불러오지 못하는 문제를 발견했다. 문서 변경과 무관한 실행 환경 문제(`.venv`의 macOS 숨김 속성)라 H1로 등록하고, 임시 조치 직후 테스트를 실행해 통과를 확인했다.

### 결정 사항
- 완료 기록은 당시 상태를 남긴 기록이므로 과거 기록의 "저장소" 표현은 고치지 않는다.
- 검사기 테스트에서 임시 git 저장소를 만드는 등 git 저장소를 뜻하는 나머지 표현은 문맥상 분명해 그대로 둔다.

### 변경 파일
- 수정: `docs/Architecture.md`, `docs/Roadmap.md`, `docs/index.md`, `docs/design/Store.md`, `docs/design/Collector.md`, `docs/design/Cli.md`, `docs/TaskRule.md`, `docs/CommitRule.md`, `docs/CodeRule.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 문서에서 "저장소"는 git 저장소, "이벤트 저장소"는 원시 이벤트를 쌓는 구성 요소(`EventStore`)로 구분된다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 36개 통과(H1 임시 조치 직후 실행)

## M1-T1 uv 패키지 골격 구성

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [CLI 설계](design/Cli.md#1-패키지-골격), [시스템 구조](Architecture.md#7-코드-구성)

### 계획
- [CLI 설계](design/Cli.md)에 M1-T1 범위(패키지, 의존성, 실행 명령, `--version`)를 명확히 하고 구현할 심볼을 코드 포인터로 바꾼다.
- `pyproject.toml`에 `uv_build` 빌드 백엔드와 `[project.scripts]`를 설정하고, `uv add`로 `fastapi`, `uvicorn`, 개발 의존성 `httpx`를 추가한다.
- `src/agentvis/__init__.py`, `src/agentvis/cli.py`(`main`, `--version`)와 테스트를 작성한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다.
- 2026-10-31: [CLI 설계](design/Cli.md#1-패키지-골격)에 M1-T1 범위(`__version__`, `main`, `--version`, 테스트)를 적고 코드 포인터로 걸었다. 포인터 검사기가 미구현 5건을 보고하는 것을 확인한 뒤 구현했다.
- 2026-10-31: 문서를 고치다가 [저장소 설계](design/Store.md)와 인덱스가 저장소를 M1-T1 관련으로 잘못 적고 있는 것을 발견해 M1-T2로 바로잡았다. 패키지 골격은 CLI 설계의 범위다.
- 2026-10-31: 패키지 파일이 없는 상태에서 `uv add`가 프로젝트 빌드에 실패해(`Expected a Python module at: src/agentvis/__init__.py`), 모듈을 먼저 만든 뒤 의존성을 추가했다.
- 2026-10-31: 버전을 `"0.1.0"` 문자열과 비교하던 테스트를 `pyproject.toml`의 값과 비교하도록 고쳤다. 버전을 올릴 때 테스트가 깨지지 않게 하고, 버전 정보가 한 곳에만 있다는 설계를 직접 검증하기 위해서다.

### 결정 사항
- `__version__`은 `importlib.metadata`로 설치된 패키지 메타데이터에서 읽는다. 버전은 `pyproject.toml`에만 적는다.
- M1-T1의 `main`은 `--version`과 도움말만 제공하고, 하위 명령은 M1-T4, M1-T5에서 추가한다.
- 의존성 하한은 `uv add`가 정한 값(`fastapi>=0.162.0`, `uvicorn>=0.54.0`, 개발용 `httpx>=0.28.1`)을 그대로 쓴다. 정확한 버전은 `uv.lock`이 고정한다.

### 변경 파일
- 신규: `src/agentvis/__init__.py`, `src/agentvis/cli.py`, `tests/test_cli.py`
- 수정: `pyproject.toml`, `uv.lock`, `docs/design/Cli.md`, `docs/design/Store.md`, `docs/index.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- `uv run agentvis --version`이 `agentvis 0.1.0`을 출력하고, 이후 태스크가 `agentvis` 패키지에 모듈과 하위 명령을 더할 수 있다.
- FastAPI, uvicorn, httpx가 uv 환경에 설치되어 M1-T2 이후 작업에 쓸 수 있다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 36개 통과
- `uv run agentvis --version`: `agentvis 0.1.0`

## I7 작업 ID 기준 커밋 컨벤션과 커밋 메시지 검사기

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시, [작업 관리 규칙](TaskRule.md), [문서 작업 규칙](DocumentationRule.md#1-문서-우선-원칙)

### 계획
- 커밋 컨벤션 문서(`docs/CommitRule.md`)를 만든다: 메시지 형식, 커밋 단위와 시점, 예외, 강제 장치.
- [검증 도구](VerificationTools.md)에 커밋 검사기 명세를 쓰고 `tools/check_commits.py`와 테스트를 구현한다.
- git `commit-msg` hook(`.githooks/commit-msg`)으로 커밋 시점에 검사기를 실행한다.
- 작업 관리 규칙의 완료 절차, 검증 명령 목록, 인덱스에 반영한다.

### 진행 기록
- 2026-10-31: I7을 등록하고 시작했다.
- 2026-10-31: [커밋 규칙](CommitRule.md)을 먼저 쓰고, [검증 도구](VerificationTools.md#7-커밋-검사기)에 명세를 쓴 뒤 포인터 검사기가 미구현 9건을 보고하는 것을 확인하고 구현했다.
- 2026-10-31: `.githooks/commit-msg`를 만들고 `git config core.hooksPath .githooks`(저장소 로컬 설정)로 켰다. hook 스크립트를 직접 실행해, 범위 표기 메시지는 막고 정상 메시지는 통과시키는 것을 확인했다.

### 결정 사항
- 제목 줄은 `<작업 ID>[, <작업 ID>…]: <요약>`이다. 작업 종류는 ID 접두어(M-T, I, H)가 이미 나타내므로 `feat:`·`fix:` 같은 유형 접두어는 두지 않는다.
- 기존 첫 커밋 `2a80e26`은 이 형식에 맞지 않지만 이력을 고쳐 쓰지 않고 기준 커밋으로 삼아 검사에서 제외한다.
- 이력 검사는 ID 존재만, 커밋 시점 검사는 시작 여부(`[~]`, `[x]`)까지 확인한다. 지금 문서의 상태가 과거 커밋 당시의 상태와 다를 수 있기 때문이다.
- ProjInit 로드맵의 `M0-T6`(커밋 메시지와 작업 ID 연결 규칙)과 같은 내용이다. I5에서 정한 대로 두 저장소의 규칙이 갈라지지 않도록 ProjInit에 알릴 필요가 있다.

### 변경 파일
- 신규: `docs/CommitRule.md`, `tools/check_commits.py`, `tests/test_check_commits.py`, `.githooks/commit-msg`
- 수정: `docs/VerificationTools.md`, `docs/TaskRule.md`, `docs/CodeRule.md`, `docs/index.md`, `CLAUDE.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- git 로컬 설정: `core.hooksPath=.githooks`

### 결과
- 모든 커밋이 작업 ID로 시작하고, 형식에 맞지 않거나 없는·시작하지 않은 작업 ID의 커밋은 커밋 시점에 막힌다.
- 기준 커밋 이후 이력 전체를 명령 하나로 검사할 수 있다.

### 검증
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`, `check_commits`: 통과
- `uv run python -m unittest discover -s tests -t .`: 34개 통과

## I2 hooks 실측 중 생긴 임시 세션 기록 정리 여부 결정

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시

### 계획
- 실측 세션 기록이 더 필요한지 확인하고, 필요 없으면 지운다.

### 진행 기록
- 2026-10-31: 사용자가 "필요 없으면 지워"라고 지시했다. 실측 결과는 [데이터 소스](DataSource.md#2-hook-이벤트)와 M0-T4 완료 기록에 이미 남아 있어 원본 기록은 필요 없다고 판단했다.
- 2026-10-31: `~/.claude/projects/` 아래 실측용 프로젝트 디렉터리(`-private-tmp-claude-501--…-scratchpad-hookprobe-proj`)를 지웠다. 지우기 전에 내용이 실측 세션 2개(`08b5b271…`, `dc739b66…`, 작업 디렉터리는 임시 `hookprobe/proj`)와 빈 `memory/`뿐임을 확인했다.
- 2026-10-31: 실측에 쓴 임시 작업 공간의 파일(hook 설정, 이벤트 덤프, 수집 서버 스크립트)도 함께 지웠다.

### 결정 사항
- 실측 결과는 [데이터 소스](DataSource.md#2-hook-이벤트)와 M0-T4 완료 기록에 문서로 남아 있으므로 원본은 보존하지 않는다.

### 변경 파일
- 수정: `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- 삭제(저장소 밖): `~/.claude/projects/-private-tmp-claude-501--…-scratchpad-hookprobe-proj/`

### 결과
- M2-T5(지난 세션 가져오기)에서 실측용 세션이 섞이지 않는다.

### 검증
- 삭제 후 `~/.claude/projects/`에 실측용 디렉터리가 없음을 확인했다.
- `uv run python -m tools.check_docs`, `check_pointers`, `check_tasks`: 통과

## I5 공통 규칙 체계를 ProjInit 저장소로 분리하고 두 저장소를 git으로 관리

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시, [문서 작업 규칙](DocumentationRule.md)

### 계획
- AgentVis에서 `git init`을 하고 저장소 로컬 사용자 정보(`user.name`, `user.email`)를 설정한다.
- `/Users/qazcde/Desktop/Playground/ProjInit`에 공통 규칙 문서, 빈 작업 관리 문서, 검사기, 테스트, uv 설정을 복사한다. AgentVis 고유 문서(제품 비전, 데이터 소스, 시스템 구조, 상세 설계)는 복사하지 않는다.
- 새 세션이 이 대화의 맥락 없이 시작할 수 있도록 ProjInit의 제품 비전과 로드맵을 작성한다.
- ProjInit에서 검증을 통과시킨 뒤 `git init`과 첫 커밋을 한다.
- AgentVis를 완료 처리하고 첫 커밋을 한다.

### 진행 기록
- 2026-10-31: I5, I6을 등록하고 시작했다.
- 2026-10-31: AgentVis에서 `git init -b main`을 하고 `user.name`, `user.email`을 저장소 로컬 설정으로 넣었다(전역 설정은 바꾸지 않음).
- 2026-10-31: 사용자가 미리 만들어 둔 빈 `ProjInit` 디렉터리에 공통 규칙 문서 6종, `CLAUDE.md`, `tools/`, `tests/`, uv 설정을 복사했다. 인덱스의 제품·상세 설계 항목, 코드 작업 규칙의 `src/` 설명, 작업 관리 규칙의 기록 예시를 ProjInit에 맞게 고쳤다.
- 2026-10-31: ProjInit의 제품 비전(목적, 출발점, 핵심 요구사항, 구성 초안, 알려진 약점, 미결정 사항)과 로드맵(M0~M4)을 작성했다. 이 대화의 논의를 문서로 옮겨 ProjInit 세션이 맥락 없이 시작할 수 있게 하기 위해서다.
- 2026-10-31: ProjInit에서 검증을 모두 통과시키고 같은 로컬 사용자 정보로 첫 커밋(`18e5cf3`)을 했다.

### 결정 사항
- 작업을 둘로 나눴다. 저장소 분리와 git 초기화는 I5에서 끝내고, AgentVis를 ProjInit 패키지로 전환하는 일은 I6으로 남긴다. 전환은 ProjInit의 검사기 패키지와 `upgrade` 명령이 준비된 뒤에 할 수 있기 때문이다.
- 그때까지 AgentVis는 지금의 `tools/`와 규칙 문서를 그대로 쓴다. 두 저장소의 규칙이 갈라질 수 있으므로, AgentVis에서 공통 규칙을 바꾸면 ProjInit에도 같은 변경이 필요한지 확인한다.

### 변경 파일
- AgentVis: `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`, git 저장소 생성
- ProjInit(`/Users/qazcde/Desktop/Playground/ProjInit`): 저장소 전체 생성

### 결과
- 초기화 CLI는 별도 저장소 ProjInit에서 같은 규칙 체계로 개발을 시작할 수 있다.
- AgentVis와 ProjInit 모두 git으로 관리되며, 커밋 작성자는 저장소 로컬 설정의 `qazcdesnu`다.

### 검증
- AgentVis, ProjInit 각각에서 `check_docs`, `check_pointers`, `check_tasks`, 테스트 27개: 모두 통과

## I4 규칙을 프로젝트 문서로만 관리하고, 검사기 동반 방침을 문서화

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시, [문서 작업 규칙](DocumentationRule.md#1-문서-우선-원칙)

### 계획
- [문서 작업 규칙](DocumentationRule.md)에 "규칙은 프로젝트 문서에서만 관리한다"는 원칙과 "규칙을 정하면 검사기를 같은 작업에서 만든다"는 조항을 넣는다.
- `CLAUDE.md`의 핵심 원칙에 같은 내용을 요약한다.
- Claude Code 메모리에 만든 파일(`rules-need-checkers.md`, `MEMORY.md`)을 지운다.

### 진행 기록
- 2026-10-31: 이슈 I4를 등록하고 시작했다.
- 2026-10-31: M0-T6을 마치면서 검사기 동반 방침을 프로젝트 문서가 아닌 Claude Code 메모리(`~/.claude/projects/<프로젝트>/memory/`)에 저장했던 것을 바로잡았다. 메모리 디렉터리는 Claude Code가 프로젝트마다 두는 공간이고, 두 파일은 그 작업에서 직접 만든 것이었다.
- 2026-10-31: 문서에 규칙을 반영하고 두 메모리 파일을 지웠다. 메모리 디렉터리는 비어 있다.

### 결정 사항
- 검사기 동반 조항은 "기계적으로 검사할 수 있는" 규칙에 적용한다. 이번에 추가한 두 원칙은 사람의 판단에 달린 작업 방침이라 검사기를 두지 않는다.

### 변경 파일
- 수정: `docs/DocumentationRule.md`, `CLAUDE.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- 삭제(저장소 밖): `~/.claude/projects/-Users-qazcde-Desktop-Playground-AgentVis/memory/rules-need-checkers.md`, `MEMORY.md`

### 결과
- 프로젝트의 모든 규칙이 `CLAUDE.md`를 루트로 하는 문서 안에만 있다.

### 검증
- `uv run python -m tools.check_docs`: 통과
- `uv run python -m tools.check_pointers`: 통과
- `uv run python -m tools.check_tasks`: 통과
- `uv run python -m unittest discover -s tests -t .`: 27개 통과

## M0-T6 작업 ID 기준 작업 관리 문서 정합성 검사기 구현

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [작업 관리 규칙](TaskRule.md#6-문서-형식), [검증 도구](VerificationTools.md#6-작업-관리-검사기)
- 관련 이슈: I3

### 계획
- 검사기가 해석할 수 있도록 [작업 관리 규칙](TaskRule.md)에 문서 형식(로드맵 줄, 이슈 줄, 기록 제목, 필드)을 명확히 정한다.
- 이슈와 태스크의 연결을 `연결 작업` 필드로 정한다.
- [검증 도구](VerificationTools.md)에 작업 관리 검사기 명세를 쓰고, `tools/check_tasks.py`와 테스트를 구현한다.
- 검증 명령 목록(`CLAUDE.md`, 코드 작업 규칙, 문서 작업 규칙)에 새 검사기를 추가한다.

### 진행 기록
- 2026-10-31: 로드맵에 M0-T6, 이슈에 I3을 등록하고 시작했다.
- 2026-10-31: I1(작업 안에서 처리)과 I3(태스크로 이관)처럼 자체 기록이 없는 이슈가 있어, 이슈의 `연결 작업` 필드를 정했다. 기존 I1, I3의 "처리" 줄을 이 필드로 바꿨다.
- 2026-10-31: 명세를 먼저 쓰고 포인터 검사기가 미구현 심볼 17건을 보고하는 것을 확인한 뒤 구현했다.
- 2026-10-31: 실제 문서 사본의 상태를 일부러 틀리게 바꿔 실행해, 상태·기록 불일치, 연결 작업 상태 불일치, 없는 ID 참조가 모두 보고되는 것을 확인했다.

### 결정 사항
- 연결 작업이 있는 이슈는 자체 기록을 두지 않고 상태를 연결 작업과 같게 맞춘다. 연결은 한 단계만 허용한다([취소와 이관](TaskRule.md#44-취소와-이관)).
- ID 참조는 앞뒤가 영문자·숫자·`-`가 아닐 때 인식한다. `M0-T6으로`처럼 한글 조사가 붙은 ID도 검사하기 위해서다.
- 펜스 밖 줄 읽기와 인라인 코드 제거를 새 검사기도 쓰게 되어 `doclib`의 공개 함수 `iter_prose_lines`, `strip_inline_code`로 바꿨다. 문서에 먼저 반영했다.
- 기존 절 번호의 앵커를 바꾸지 않도록 새 검사기 명세는 [검증 도구](VerificationTools.md)의 6절로 덧붙였다.

### 변경 파일
- 신규: `tools/check_tasks.py`, `tests/test_check_tasks.py`
- 수정: `tools/doclib.py`, `docs/TaskRule.md`, `docs/VerificationTools.md`, `docs/Roadmap.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`, `docs/CodeRule.md`, `docs/DocumentationRule.md`, `CLAUDE.md`

### 결과
- 로드맵·이슈의 상태, 진행 중·완료 기록, 연결 작업, ID 번호 차례, 본문의 ID 참조가 작업 ID 기준으로 자동 검사된다.

### 검증
- `uv run python -m tools.check_docs`: 통과
- `uv run python -m tools.check_pointers`: 통과
- `uv run python -m tools.check_tasks`: 통과
- `uv run python -m unittest discover -s tests -t .`: 27개 통과

## M0-T5 작업 관리 문서 체계와 M1 상세 설계 작성

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [작업 관리 규칙](TaskRule.md), [시스템 구조](Architecture.md)

### 계획
- 로드맵(M-T), 진행 중, 완료, 이슈(I, H) 문서와 그 운영 규칙을 만든다.
- 지금까지의 작업을 M0으로 소급 기록한다.
- M1 구성 요소(저장소, 수집기, CLI)의 상세 설계 문서를 작성한다.

### 결정 사항
- 운영 규칙은 별도 문서 [작업 관리 규칙](TaskRule.md)에 두고, 네 문서는 기록만 담는다.
- 상세 설계 문서는 `docs/design/`에 둔다. 구현할 심볼은 처음에는 인라인 코드로 적고, 태스크를 시작할 때 코드 포인터 링크로 바꾼다. 진행 중인 태스크가 없을 때 [포인터 검사기](VerificationTools.md#4-포인터-검사기)가 통과하는 상태를 유지하기 위해서다. 이 절차를 [코드 작업 규칙](CodeRule.md#1-문서-우선-작업-절차)에 반영했다.
- AgentVis가 설치한 hook은 URL의 `client=agentvis` 쿼리로 식별한다. Claude Code 설정 항목에 임의의 키를 더하지 않기 위해서다.
- hooks 설정 편집 로직을 위한 `agentvis/hook_settings.py` 모듈을 [시스템 구조](Architecture.md#7-코드-구성)에 추가했다.

### 변경 파일
- 신규: `docs/TaskRule.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`, `docs/Issue.md`, `docs/design/Store.md`, `docs/design/Collector.md`, `docs/design/Cli.md`
- 수정: `docs/index.md`, `docs/CodeRule.md`, `docs/Architecture.md`, `CLAUDE.md`

### 결과
- 모든 작업이 ID로 추적되고, 로드맵·진행 중·완료의 상태가 한 규칙으로 연결된다.
- M1의 태스크를 상세 설계 문서에 따라 바로 시작할 수 있다.

### 검증
- `uv run python -m tools.check_docs`: 통과
- `uv run python -m tools.check_pointers`: 통과

## M0-T4 hooks 실측과 시스템 구조 설계

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md#5-결정-사항)

### 계획
- Claude Code hooks의 이벤트와 필드를 공식 문서와 실측으로 확인한다.
- 실시간 수집을 기본으로 하는 시스템 구조를 설계한다.

### 진행 기록
- 2026-10-31: 공식 hooks 참조 문서에서 이벤트 33종과 필드를 조사했다.
- 2026-10-31: 임시 디렉터리에서 `claude -p`(2.1.314)를 `--settings`로 command hook을 걸어 실행했다. 실패 명령(`ls` 없는 경로)과 성공 명령(`echo`)으로 이벤트를 받았다.
- 2026-10-31: 같은 방식으로 `http` hook을 확인했다. 연결이 거부되는 주소로 보낸 hook이 있어도 작업이 막히지 않았고, 살아 있는 서버는 같은 JSON을 POST로 받았다.

### 결정 사항
- Bash의 0이 아닌 종료 코드는 `PostToolUseFailure`로 온다(`error`, `is_interrupt`).
- hook의 `prompt_id`·`tool_use_id`가 세션 기록의 `promptId`·도구 ID와 같아 두 소스를 결합할 수 있다.
- thinking, 작업 중 사용자 메시지, auto 모드가 아닐 때의 권한 거부는 hook으로 오지 않으므로 세션 기록으로 보완한다.
- 수집은 `http` hook, 서버는 FastAPI + uvicorn, 저장소는 SQLite, 실시간 전송은 SSE로 정했다.

### 변경 파일
- 신규: `docs/Architecture.md`
- 수정: `docs/DataSource.md`(재작성), `docs/index.md`, `docs/CodeRule.md`

### 결과
- 데이터 소스별로 얻을 수 있는 정보와 한계가 정리되었고, 구성 요소·데이터 모델·API·구현 순서(M1~M7)가 정해졌다.

### 검증
- `uv run python -m tools.check_docs`: 통과
- `uv run python -m tools.check_pointers`: 통과

## M0-T3 제품 비전과 데이터 소스 정리

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: 사용자 지시 (Claude Code 작업 과정 시각화)

### 계획
- 사용자가 말한 목표를 분석 질문과 진단 신호로 정리한다.
- 원천 데이터인 Claude Code 세션 기록의 구조를 확인한다.

### 진행 기록
- 2026-10-31: 로컬 세션 기록(JSONL)의 기록 유형과 필드를 조사했다. 도구 실패(`is_error`), 작업 중 사용자 메시지(`queue-operation`), 권한 판정(`permissionDecision`)을 확인했다.
- 2026-10-31: 미결정 사항 세 가지를 사용자에게 물어 결정했다.

### 결정 사항
- 데이터 수집은 실시간 우선, 세션 기록으로 보완한다.
- 화면은 로컬 웹 앱이다.
- 추정 신호는 규칙으로 먼저 판정하고, LLM 판정은 나중에 선택 기능으로 더한다.

### 변경 파일
- 신규: `docs/ProductVision.md`, `docs/DataSource.md`
- 수정: `docs/index.md`

### 결과
- 핵심 분석 질문 Q1~Q6, 진단 신호(확정·추정), 범위, 결정 사항이 정해졌다.

### 검증
- `uv run python -m tools.check_docs`: 통과

## M0-T2 코드 작업 규칙, 포인터 규약, 검증 도구 구현

- 시작일: 2026-10-30
- 완료일: 2026-10-30
- 근거 문서: [코드 작업 규칙](CodeRule.md), [포인터 규약](Traceability.md), [검증 도구](VerificationTools.md)
- 관련 이슈: I1

### 계획
- 코드 작업 규칙을 문서로 만든다.
- 문서 ↔ 코드 양방향 포인터 규약을 설계한다.
- 링크·고아 문서 검사기와 포인터 검사기를 구현한다.

### 진행 기록
- 2026-10-30: 문서를 먼저 작성하고, 문서가 가리키는 심볼을 구현했다. 테스트 파일이 생기기 전에 포인터 검사기가 문서에만 있는 테스트 3개를 미구현으로 정확히 보고하는 것을 확인했다.
- 2026-10-30: I1(uv 사용) 지시를 받아 코드 작업 규칙과 실행 명령을 고치고, `uv init`으로 Python 3.12 프로젝트를 구성했다. 3.9 호환 코드를 제거했다.
- 2026-10-30: 테스트 실패 3건은 모두 테스트 픽스처 오류였고, 검사기는 의도대로 동작했다. 픽스처만 고쳤다.

### 결정 사항
- 문서 → 코드 포인터는 줄 번호 대신 AST 한정 이름(`파일.py#Class.method`)을 쓴다.
- 코드 → 문서 포인터는 docstring의 `@doc:` 태그를 기본으로 하고, 상수에는 바로 위 주석을 쓴다.
- 경로를 표시하는 로직이 두 곳에 생겨 `display_path`로 공통화했고, 테스트 공통 기반 `tests/support.py`를 두었다. 둘 다 문서에 먼저 추가했다.

### 변경 파일
- 신규: `docs/CodeRule.md`, `docs/Traceability.md`, `docs/VerificationTools.md`, `tools/doclib.py`, `tools/check_docs.py`, `tools/check_pointers.py`, `tests/support.py`, `tests/test_doclib.py`, `tests/test_check_docs.py`, `tests/test_check_pointers.py`, `pyproject.toml`, `.python-version`, `uv.lock`, `.gitignore`
- 수정: `docs/index.md`, `docs/DocumentationRule.md`, `CLAUDE.md`

### 결과
- 깨진 링크, 고아 문서, 문서 ↔ 코드 포인터의 불일치를 명령 하나로 찾을 수 있다.

### 검증
- `uv run python -m tools.check_docs`: 통과
- `uv run python -m tools.check_pointers`: 통과
- `uv run python -m unittest discover -s tests -t .`: 18개 통과

## M0-T1 문서 규칙과 문서 인덱스 수립

- 시작일: 2026-10-30
- 완료일: 2026-10-30
- 근거 문서: 사용자 지시 (문서 우선 원칙)

### 계획
- 작업마다 읽을 문서를 안내하는 인덱스와 문서 작업 규칙을 만든다.

### 결정 사항
- `CLAUDE.md`는 인덱스와 규칙 문서로 안내하는 역할만 한다.
- 문서 간 링크는 `[문서 이름](상대 경로)`로 걸고, 인덱스에서 도달할 수 없는 고아 문서를 금지한다.

### 변경 파일
- 신규: `CLAUDE.md`, `docs/index.md`, `docs/DocumentationRule.md`

### 결과
- 모든 작업이 인덱스에서 시작하고 문서가 코드보다 먼저 작성되는 규칙이 생겼다.

### 검증
- 수동 확인 (검증 도구는 M0-T2에서 만들었다.)
