# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## I48 v1.0.0 릴리스

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [PR 규칙의 릴리스](PullRequestRule.md#6-릴리스)

### 계획
- PR 규칙에 릴리스 절차(버전 형식과 위치, 릴리스 PR, 태그, GitHub 릴리스와 노트)를 정하고, 버전 형식을 테스트로 검사한다.
- `pyproject.toml`과 `uv.lock`의 버전을 1.0.0으로 올린다.
- README의 현재 상태와 화면 사용법을 지금 화면에 맞춘다.
- PR을 병합한 뒤 `main`에 `v1.0.0` 태그를 달고 GitHub 릴리스를 만든다.
- 최신 `main`에서 만든 `i48-release-1-0-0`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 지금 버전을 v1.0.0으로 릴리스하라고 지시했다. PR #32~#37은 이미 병합되어 있었다.
- 2026-11-07: PR 규칙 6절(릴리스)을 쓰고, 버전 형식 검사를 CLI 테스트에 더했다. `pyproject.toml`·`uv.lock`을 1.0.0으로 올리고, README의 현재 상태와 화면 사용법을 지금 화면(네 상자, 턴 시퀀스, 실시간 따라가기, JSON 보기, 전체 보기)에 맞췄다. 릴리스 노트에 주요 기능(작업 ID와 함께), 처음 시작 때 스키마 5판 이동으로 모든 기록을 다시 읽는다는 점, 설치 안내를 적었다.

### 결정 사항
- 첫 릴리스를 1.0.0으로 한다(사용자 지시). 버전은 `pyproject.toml` 한 곳에만 두고 `__version__`은 패키지 정보에서 읽는다.
- 사용자가 릴리스를 지시했으므로 릴리스 PR의 병합, 태그, GitHub 릴리스는 Claude가 한다([PR 규칙 6절](PullRequestRule.md#6-릴리스)).

### 변경 파일
- `pyproject.toml`, `uv.lock`, `tests/test_cli.py`, `README.md`
- `docs/PullRequestRule.md`, `docs/index.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- `main`의 릴리스 병합 커밋에 태그 `v1.0.0`이 있고, GitHub 릴리스 https://github.com/qazcdesnu/AgentVis/releases/tag/v1.0.0 에 노트가 있다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 144개 통과(버전 형식 검사 추가). `uv run python -c "import agentvis; print(agentvis.__version__)"`가 `1.0.0`을 출력한다.


## I47 세션 제목과 진행 요약

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [데이터 소스의 세션 제목과 진행 요약](DataSource.md#39-세션-제목과-진행-요약), [분석기 설계의 세션](design/Analysis.md#7-세션)

### 계획
- 데이터 소스에 `ai-title`, `agent-name`, `away_summary` 실측을 적는다.
- 기록 리더가 시각 없는 제목 기록도 저장하고, 저장소 5판에서 읽기 위치를 처음으로 되돌려 이미 읽은 기록에서 제목을 가져온다.
- 분석기가 제목(이름 → AI 제목 → 정리한 첫 지시), 진행 요약, 브랜치를 내고, 제목 기록은 세션 시각 계산에서 뺀다.
- 화면의 세션 목록과 세션 정보 상자를 고친다.
- I46 브랜치 위에 쌓은 `i47-session-title-recap`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 세션 정보를 더 잘 보여 줄 정보를 물었다. 세션 기록 12개에서 `ai-title`(12개 세션, 10~50자, 평균 19.2자), `agent-name`(2개 세션, 17·20자, 같은 세션의 `ai-title`과 같은 값), `away_summary`(12개 세션, 세션마다 3~34개)를 찾았다. 스킬로 시작한 세션 6개의 첫 지시는 `<command-message>…</command-message>`였다. 사용자가 진행을 지시했다.
- 2026-11-07: 데이터 소스 3.9절, 기록 리더 3절, 저장소 11절, 분석기 7절, 웹 UI 2·3절을 먼저 고친 뒤 `transcript.py`(`TIMELESS_TYPES`), `store.py`(5판: 커서 위치 되돌리기), `session.py`(`title_source`, `recap`, `git_branch`, 제목 기록을 세션 시각에서 뺌), `overview.js`(`promptLine`), `app.js`·`style.css`(세션 정보 상자, 목록 제목 두 줄)를 고쳤다.
- 2026-11-07: 실제 저장소를 백업(`~/.agentvis/backups/agentvis-before-v5-20261107T122630Z.db`)한 뒤 서버를 다시 띄웠다. 5판으로 올라가 세션 기록 144개 파일을 다시 읽었고, 제목 기록은 중복 없이 `ai-title` 10개, `agent-name` 2개가 저장되었다. 세션 11개 중 10개가 이름이나 Claude Code 제목을, 1개(제목 기록 없는 짧은 시험 세션)가 첫 지시를 제목으로 쓴다. 10개 모두 진행 요약과 브랜치가 나온다.

### 결정 사항
- 제목은 이름 → Claude Code 제목 → 정리한 첫 지시 순이다. 제목 기록에는 시각이 없어 마지막 값은 저장 순서로 고르고, 세션 시각 계산에서 뺀다.
- 진행 요약은 Claude Code가 생성한 글이라 `요약` 표지를 붙여 확정 사실과 구분한다.
- 남은 점: Claude Code 제목은 세션 처음에 정해지고 바뀌지 않아, 오래 이어진 세션은 지금 하는 일과 다를 수 있다(예: 이 세션의 제목 "문서 규칙 및 docs 구조 설정"). 지금 하는 일은 진행 요약이 보여 준다.

### 변경 파일
- `src/agentvis/transcript.py`, `src/agentvis/store.py`, `src/agentvis/analysis/session.py`, `src/agentvis/web/app.js`, `src/agentvis/web/overview.js`, `src/agentvis/web/style.css`
- `tests/test_transcript.py`, `tests/test_store.py`, `tests/test_analysis.py`
- `docs/DataSource.md`, `docs/design/Transcript.md`, `docs/design/Store.md`, `docs/design/Analysis.md`, `docs/design/WebUI.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 세션 목록과 세션 정보가 Claude Code의 세션 이름·제목으로 보이고, 세션 정보 상자에 진행 요약, 상태, 시간, 브랜치가 보인다. 슬래시 명령으로 시작한 지시는 `/start`처럼 보인다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 144개 통과(I47 테스트 3개 추가).
- 실제 저장소의 5판 이동과 다시 읽기를 위 진행 기록대로 확인했다. 브라우저 화면은 확인하지 않았다(사용자 확인 필요).


## I46 JSON 보기 선택을 칸 종류마다 하나로

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [웹 UI 설계의 단계 표시](design/WebUI.md#3-턴과-단계-표시)

### 계획
- 웹 UI 설계 3절의 "고른 보기 기억" 규칙을 칸 종류마다 하나로 바꾸고 `app.js`를 맞춘다.
- I44 브랜치 위에 쌓은 `i46-json-view-preference`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 입력은 JSON 보기가 유지되는데 결과는 계속 원문으로 돌아간다고 했다. 보기를 칸(도구 호출 × 칸)마다 기억해, 입력은 기본이 정리라 유지되는 것처럼 보이고 결과는 다른 노드(실시간 따라가기로 바뀌는 최신 노드 포함)를 열 때마다 기본인 원문으로 나왔다. 칸 종류(입력, 결과·오류)마다 하나로 기억하고, 한 칸에서 고르면 보이는 같은 종류의 칸이 모두 바뀌게 했다. 선택은 브라우저 저장소에 둔다.

### 결정 사항
- 선택은 보는 사람의 취향이라 해시가 아닌 `localStorage`에 둔다. 저장소를 쓸 수 없으면 기본 보기로 시작한다.

### 변경 파일
- `src/agentvis/web/app.js`
- `docs/design/WebUI.md`, `docs/Issue.md`, `docs/Done.md`

### 결과
- 결과에서 "JSON 정리"를 한 번 고르면 다른 노드, 실시간 갱신, 새로고침 뒤에도 정리 보기로 나온다. 입력도 같다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 141개 통과(화면만 바꿈).
- 브라우저 동작은 확인하지 않았다(사용자 확인 필요).

## I45 JSON 정리 보기의 들여쓰기 4칸

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [웹 UI 설계의 단계 표시](design/WebUI.md#3-턴과-단계-표시)

### 계획
- 웹 UI 설계 3절의 JSON 정리 보기 들여쓰기를 4칸으로 고치고, `app.js`를 맞춘다.
- 사용자가 I44 작업 중에 지시해 같은 브랜치 `i44-full-result`에서 한다.

### 진행 기록
- 2026-11-07: 사용자가 들여쓰기 2칸은 너무 빽빽하다고 했다. 설계를 고친 뒤 `JSON_INDENT = 4`로 입력·결과·오류의 정리 보기를 바꿨다.

### 변경 파일
- `src/agentvis/web/app.js`
- `docs/design/WebUI.md`, `docs/Issue.md`, `docs/Done.md`

### 결과
- JSON 정리 보기가 들여쓰기 4칸으로 보인다. 노드 상세의 입력 기본 보기도 4칸이다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 141개 통과(화면만 바꿈).

## I44 잘린 도구 결과의 전체 보기

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [분석기 설계의 도구 호출](design/Analysis.md#5-도구-호출), [웹 UI 설계의 단계 표시](design/WebUI.md#3-턴과-단계-표시)

### 계획
- 분석기 설계에 결과 미리보기 길이의 이유와 실측, `result_chars`·`error_chars`, 전체 결과 조회 API를 적는다.
- 웹 UI 설계에 "전체 보기" 단추와 예·아니오 확인 대화상자 규칙을 적는다.
- `session.py`, `catalog.py`, `server.py`, `app.js`, `style.css`를 고치고 테스트를 더한다.
- I43 브랜치 위에 쌓은 `i44-full-result`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 2,000자 제한의 이유를 물었다. 저장소는 원본을 모두 보관하고, 분석기가 응답을 만들 때 자른다. 이유는 문서에 없었다. 가장 큰 세션으로 재니 제한이 있으면 응답 4.5MB, 없으면 5.2MB(+16%)였고 계산 시간은 둘 다 0.16초였다. 결과 871개 중 2,000자를 넘는 것은 73개(최장 16,381자, 중앙값 225자)였다. 사용자가 미리보기는 두고 확인을 거쳐 전체를 보게 하라고 지시했다.
- 2026-11-07: 분석기 설계(미리보기 길이의 이유와 실측, `result_chars`·`error_chars`, 전체 결과 API)와 웹 UI 설계(전체 보기와 예·아니오 대화상자)를 먼저 고친 뒤 `session.py`(빌더마다 자르는 길이, 오류도 2,000자로 자름), `catalog.py`(`get_tool_output`), `server.py`(경로), `app.js`·`index.html`·`style.css`(전체 길이 표시, `전체 보기`, `<dialog>` 확인)를 고쳤다. 실제 서버로 확인했다: 이 세션의 잘린 결과 75개 중 가장 긴 16,381자 결과를 0.09초에 전체로 받았고 앞부분이 미리보기와 같았다.

### 결정 사항
- 미리보기 2,000자는 그대로 둔다. 세션 상세는 실시간 갱신 때마다 다시 받으므로 작게 유지하고, 전체는 사용자가 확인한 칸만 받는다.
- 확인 창은 `<dialog>`로 만든다. 브라우저 기본 창은 단추가 "확인·취소"로 나와 사용자가 정한 "예·아니오"를 쓸 수 없다. 처음 초점은 아니오에 둔다.
- 대화상자가 열린 동안 실시간 갱신으로 칸이 바뀌었으면, 예를 누른 뒤 화면 전체를 다시 그린다.

### 변경 파일
- `src/agentvis/analysis/session.py`, `src/agentvis/analysis/catalog.py`, `src/agentvis/server.py`, `src/agentvis/web/app.js`, `src/agentvis/web/index.html`, `src/agentvis/web/style.css`, `tests/test_api.py`
- `docs/design/Analysis.md`, `docs/design/WebUI.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 잘린 결과·오류 칸에 전체 길이와 `전체 보기`가 있고, 예·아니오 확인을 거쳐 예일 때만 전체를 받아 보여 준다. 아니오면 화면은 그대로다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 141개 통과(I44 테스트 1개 추가).
- 브라우저의 대화상자 동작은 확인하지 않았다(사용자 확인 필요).


## I43 JSON 원문·정리 보기 전환

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [웹 UI 설계의 단계 표시](design/WebUI.md#3-턴과-단계-표시)

### 계획
- 웹 UI 설계 3절에 JSON 판정, 두 단추, 기본 보기, 잘린 JSON 안내, 다시 그릴 때 기억하는 규칙을 적는다.
- `app.js`, `style.css`를 고친다.
- I42 브랜치 위에 쌓은 `i43-json-view`에서 진행한다.

### 진행 기록
- 2026-11-07: 저장된 세션 전체의 도구 결과·오류 5,900건을 쟀다. 전체가 올바른 JSON은 96건(서브에이전트 인계 67, TaskStop 12, Bash 9, SendMessage 8)이었다. `{`·`[`로 시작하지만 JSON이 아닌 것이 591건(Read의 `[image]` 483, TOML, JSON 뒤에 일반 출력이 이어진 Bash), 2,000자에서 잘려 해석되지 않는 JSON이 26건이었다. 입력 안의 문자열 값이 JSON인 경우는 5건이었다. 사용자가 GitHub처럼 두 단추를 나란히 두자고 해 I43으로 등록했다.
- 2026-11-07: 웹 UI 설계 3절을 고친 뒤 `app.js`(`textBlock`, `outputBlock`, 입력 안 JSON 문자열 풀기, 칸별 보기 기억)와 `style.css`(붙은 두 단추)를 고쳤다. 실제 데이터로 화면의 판정 논리를 돌려 단추가 붙는 칸 96개, 잘린 JSON 안내 26개로 실측과 같음을 확인했다.

### 결정 사항
- 단추는 글 전체가 JSON으로 해석될 때만 둔다. `{`·`[`로 시작하는지만 보면 `[image]`, TOML 같은 오탐이 583건 넘게 생긴다.
- 기본 보기는 지금까지의 모습 그대로다(결과·오류는 원문, 입력은 정리).

### 변경 파일
- `src/agentvis/web/app.js`, `src/agentvis/web/style.css`
- `docs/design/WebUI.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- JSON인 입력·결과·오류를 `[ 원문 | JSON 정리 ]` 두 단추로 바꿔 보고, 잘린 JSON은 그 사실을 안다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 140개 통과(화면만 바꿈).
- 브라우저 화면은 확인하지 않았다(사용자 확인 필요).


## I42 실시간 따라가기

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [웹 UI 설계의 화면의 갱신](design/WebUI.md#82-화면의-갱신)

### 계획
- 웹 UI 설계 8.2절의 "최신 턴 따라가기"를 "실시간 따라가기"로 바꿔, 따라가는 대상(최신 턴, 주 에이전트 최신 노드), 켜고 끄는 단추, 자동으로 꺼지는 경우, 해시 상태를 적는다.
- `app.js`, `graph.js`, `index.html`, `style.css`를 고친다.
- I41 브랜치 위에 쌓은 `i42-live-follow`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 최신 턴 따라가기에 만족했고, 주 에이전트 최신 노드도 따라가며 맨 위 실시간 단추로 따라가기를 켜고 끄게 해 달라고 지시했다.
- 2026-11-07: 웹 UI 설계 8.2절을 고친 뒤 `app.js`(해시 `live`, 최신 턴·최신 주 에이전트 노드 고르기, 직접 고르면 따라가기 끄기, 맨 위 단추로 켜고 끄기, 끌 때 보던 턴·노드 고정), `graph.js`(따라갈 때 최신 노드를 화면 오른쪽 4분의 1쯤에 둠), `index.html`·`style.css`(단추와 연결 끊김 표시)를 고쳤다. 실제 서버로 이 세션의 진행 중인 턴을 확인했다: 고른 최신 노드가 지금 실행 중인 Bash 호출이었다.

### 결정 사항
- 따라가기를 끄면 보는 위치만 멈추고 내용 갱신은 계속한다. 끈 화면도 최신 결과(실행 중이던 도구의 끝 등)를 보여야 하기 때문이다.
- 켜진 상태에서 직접 턴·노드를 고르면 따라가기를 끈다. 다음 알림이 고른 것을 빼앗지 않게 한다.
- 켜고 끄는 곳은 맨 위 단추 하나다. 턴 선택 상자의 따라가기 단추는 상태 글자로 바꿨다.

### 변경 파일
- `src/agentvis/web/app.js`, `src/agentvis/web/graph.js`, `src/agentvis/web/index.html`, `src/agentvis/web/style.css`
- `docs/design/WebUI.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 실시간 따라가기를 켜면 최신 턴과 주 에이전트의 최신 노드를 따라가며 그 노드의 상태와 상세가 열리고, 끄면 보던 턴·노드에 머문다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 140개 통과(화면만 바꿈).
- 브라우저 화면 동작은 확인하지 않았다(사용자 확인 필요).


## I41 과업별 기능 대응 정리

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [과업과 데이터 추상화](design/TaskAbstraction.md), [시각화 인코딩 설계](design/VisualEncoding.md), [Claude Code 실무 고충 조사](research/ClaudeCodePainPoints.md)

### 계획
- 여섯 과업마다 문제, 사용자가 답할 질문, 필요한 판단을 적고, 그 판단을 돕는 기능과 이유를 구현됨·계획으로 나눠 정리한다.
- 최신 `main`에서 만든 `i41-task-feature-map`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 실시간 시각화를 보며 이 작업을 하라고 지시했다. PR #31까지 병합된 화면 기능을 기준으로 [과업별 기능 대응](design/TaskCoverage.md)을 썼다.

### 결정 사항
- 상태를 정직하게 적는다. 지금 화면은 T3·T5·T6를 직접 돕고, T1·T2의 핵심 판단은 기준 사건 보기(M8-T2)가 있어야 한다. 다음 순서는 로드맵대로 M8-T2 → M8-T3다.

### 변경 파일
- `docs/design/TaskCoverage.md`(새 문서), `docs/design/VisualEncoding.md`, `docs/index.md`, `docs/Issue.md`, `docs/Done.md`

### 결과
- 과업마다 어떤 기능이 문제를 풀거나 덜어 주는지, 왜 그 기능인지, 무엇이 남았는지 한 문서에서 본다. 논문의 설계 절과 유저 스터디 과업 선택에 쓴다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 140개 통과(문서만 바꿈).

## M4-T2 변경 알림 SSE 스트림과 실시간 갱신

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [웹 UI 설계의 실시간 갱신](design/WebUI.md#8-실시간-갱신), [이벤트 저장소 설계의 M4-T2 변경](design/Store.md#10-m4-t2-변경)

### 계획
- 이벤트 저장소에 `changes_since`, 서버에 `GET /api/stream`(SSE)을 설계·구현한다.
- 화면이 알림을 받아 보고 있는 세션만 다시 받아 그리되, 고른 턴·단계·배율·스크롤을 지키고 최신 턴을 따라가게 한다.
- 저장소 질의와 스트림 생성기를 테스트하고, 실제 서버에서 알림이 오는지 확인한다.
- M2-T4 브랜치 위에 쌓은 `m4-t2-live-stream`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 진행 중인 세션을 실시간으로 보고 싶다고 했다. 세션 상세 계산은 가장 큰 세션도 약 0.12초, 세션 목록은 약 1.1초다. 사용자 지시로 H6·I40·M2-T4 뒤에 시작했다.
- 2026-11-07: 웹 UI 설계 8절, 저장소 설계 10절, 분석기 설계의 API 표를 먼저 쓰고 `store.py`(`changes_since`), `server.py`(`stream_changes`, `GET /api/stream`), `app.js`(알림 받기, 보던 세션만 다시 받기, 목록 15초 제한, 끊긴 뒤 모두 다시 받기, 최신 턴 따라가기, 그래프 배율·스크롤 기억, 노드 선택을 해시에), `graph.js`(배율·스크롤 되살리기), `index.html`·`style.css`(연결 표시)를 고쳤다.
- 2026-11-07: 실제 서버로 확인했다: `/api/stream`이 `text/event-stream`, `cache-control: no-cache`로 열리고, 이 세션이 도구를 부를 때마다 이 세션 ID를 담은 `change` 알림이 왔다(25초 동안 4건). 다른 `Host`로 오면 `400`이다.
- 2026-11-07: 스트림을 연 채 Ctrl+C하면 서버가 10초가 지나도 끝나지 않는 문제를 찾았다. uvicorn이 열린 연결을 기다리기 때문이다. 종료 대기 시간 3초만 두면 끝나지만 취소 오류 흔적이 남아, 종료 신호를 받으면 앱에 종료 중 표시를 남기는 `_StoppingServer`를 더했다. 다시 재니 약 1초 만에 오류 없이 끝났다([CLI 설계](design/Cli.md#2-명령)).

### 결정 사항
- 알림은 저장소를 1초마다 이벤트 `id`로 묻는 방식이다. hook으로 들어온 이벤트와 기록 리더가 읽은 이벤트가 같은 길로 알려지고, 수집기·기록 리더에 알림 장치를 따로 달지 않아도 된다.
- 다시 그려도 고른 턴·단계·배율·스크롤을 지킨다. 해시에 `turn`이 없으면 최신 턴을 따라가고, 마지막 턴을 고르면 `turn`을 지운다.
- 목록은 계산이 무거워(약 1.1초) 15초에 한 번까지만 다시 받는다.
- 알림 없이 오래 실행되는 막대를 시계로 늘이는 일은 하지 않았다(흐름 그래프 설계의 나중에 정할 것).

### 변경 파일
- `src/agentvis/store.py`, `src/agentvis/server.py`, `src/agentvis/cli.py`, `src/agentvis/web/app.js`, `src/agentvis/web/graph.js`, `src/agentvis/web/index.html`, `src/agentvis/web/style.css`
- `tests/test_store.py`, `tests/test_api.py`, `tests/test_cli.py`
- `docs/design/WebUI.md`, `docs/design/Store.md`, `docs/design/Analysis.md`, `docs/design/FlowGraph.md`, `docs/design/Cli.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 진행 중인 세션을 띄워 두면 도구 호출마다 화면이 바로 갱신되고, 보던 턴·단계·배율이 그대로 남으며, 새 턴이 시작되면 따라간다. 머리 줄에 실시간 연결 상태가 보인다.
- 스트림을 연 브라우저가 있어도 Ctrl+C로 서버가 바로 끝난다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 140개 통과(M4-T2 테스트 4개 추가).
- 실제 서버의 알림 수신과 종료는 위 진행 기록대로 확인했다. 브라우저 화면 동작은 확인하지 않았다(사용자 확인 필요).


## M2-T4 서버 시작 시 놓친 세션 기록 찾아 읽기

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [기록 리더 설계의 서버가 시작될 때](design/Transcript.md#42-서버가-시작될-때-m2-t4)

### 계획
- 기록 리더 설계 4.2절의 심볼을 코드 포인터로 바꾸고, 찾는 파일 모양·메타 파일·호출 시점을 적는다.
- `find_unread_transcripts`를 구현하고 `agentvis serve`가 기록 리더를 시작한 뒤 찾은 파일을 읽기 요청으로 넘기게 한다.
- 커서보다 커진 파일, 식별자가 바뀐 파일, 수집 시작 이후의 새 파일만 고르는지 테스트한다.
- H6 브랜치 위에 쌓은 `m2-t4-catch-up-on-start`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자 지시로 실시간 갱신(M4-T2) 전에 시작했다. 서버가 꺼진 동안 시작하고 끝난 세션은 그 세션의 hook이 다시 오지 않아 지금은 읽히지 않는다.
- 2026-11-07: 기록 리더 설계 4.2절과 CLI 설계를 고친 뒤 `find_unread_transcripts`를 구현하고 `agentvis serve`에 붙였다. 실제 저장소로 확인했다: 서버를 다시 띄우기 전 142개 파일(한 번도 읽지 않은 파일 16개: 세션 2개, 서브에이전트 기록 14개)을 찾았고, 다시 띄운 뒤 한 번도 읽지 않은 파일은 0개, 세션은 10개에서 11개가 되었다. 남은 2개는 마지막 줄이 아직 쓰이는 중인 파일이다.

### 결정 사항
- 수집 시작 전의 지난 세션은 자동으로 읽지 않는다(설계 그대로). 지난 세션은 M2-T5의 가져오기 명령으로만 읽는다.
- 서브에이전트 메타 파일은 고른 서브에이전트 기록 옆에 있을 때만 함께 넘긴다. 내용이 같으면 다시 저장되지 않으므로 해가 없다.

### 변경 파일
- `src/agentvis/transcript.py`, `src/agentvis/cli.py`, `tests/test_transcript.py`
- `docs/design/Transcript.md`, `docs/design/Cli.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 서버가 꺼진 동안 시작하고 끝난 세션도 서버를 켜면 읽혀 화면에 나타난다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 136개 통과(M2-T4 테스트 1개 추가).


## H6 빠진 hook의 보정과 안내

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [분석기 설계의 턴](design/Analysis.md#3-턴), [데이터 소스의 두 소스 비교](DataSource.md#4-두-소스-비교), [웹 UI 설계의 단계 표시](design/WebUI.md#3-턴과-단계-표시)
- 관련 이슈: I40

### 계획
- 데이터 소스에 hook 전달 실패와 `turn_duration` 실측을 적는다.
- 분석기 설계에 `turn_duration`을 턴 끝 신호로 쓰는 규칙을 적고 구현한다(H6).
- 웹 UI 설계에 빠진 hook 종류별 안내(보완함·확인할 수 없음, 원인)를 적고 화면·그래프 이름을 고친다(I40).
- 최신 `main`에서 만든 `h6-stop-from-transcript`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 hook 전달 실패를 사후에 보정할 수 있는지 물었다. 이 프로젝트 세션의 실패 224건(`PostToolUse` 97, `PreToolUse` 95, `UserPromptSubmit` 20, `Stop` 10, `PostToolUseFailure` 2)이 모두 `ECONNREFUSED`였다. 세션 기록에서 `turn_duration`이 턴 109개 중 102개에 하나씩 있었다(한 턴에 둘 이상인 경우 없음). 사용자가 보정 세 가지(`Stop` 대체, M2-T4, 메시지)를 먼저 하고 M4-T2로 가라고 지시했다.
- 2026-11-07: 데이터 소스 3.8절, 분석기 설계의 턴 끝 신호, 웹 UI 설계의 빠진 hook 안내 표를 먼저 쓰고 `session.py`(`turn_ends`), `graph.py`(노드 이름), `app.js`·`style.css`(안내 문구와 보완·잃음 표시)를 고쳤다. 실제 서버를 다시 띄워 세션 10개를 확인했다: 실행 중으로 남은 턴은 2개였고, 둘 다 지금 실제로 진행 중인 턴(이 세션, 12초 전까지 활동한 다른 프로젝트 세션)이었다.

### 결정 사항
- 턴 끝 신호는 `Stop` hook과 `turn_duration` 기록 둘 다로 본다. 둘 다 있으면 끝 시각은 `Stop` hook 시각이다.
- 빠진 hook 안내는 보완된 것(흐림)과 내용을 잃은 것(경고 색)을 나눈다. 원인은 오류 문구로 판단한다(`ECONNREFUSED`면 서버가 꺼져 있었음).

### 변경 파일
- `src/agentvis/analysis/session.py`, `src/agentvis/analysis/graph.py`, `src/agentvis/web/app.js`, `src/agentvis/web/style.css`, `tests/test_analysis.py`
- `docs/DataSource.md`, `docs/design/Analysis.md`, `docs/design/FlowGraph.md`, `docs/design/WebUI.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 서버가 꺼져 `Stop` hook을 받지 못한 턴도 세션 기록을 읽으면 끝난 것으로 보인다(H6).
- 빠진 hook마다 "무엇을 세션 기록으로 보완했고 무엇을 확인할 수 없는지"와 원인이 한 줄로 보인다(I40).

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 135개 통과(H6 테스트 1개 추가).


## I39 사람이 보낸 메시지의 이름과 모양

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [웹 UI 설계의 단계 표시](design/WebUI.md#3-턴과-단계-표시), [작업 흐름 그래프 설계의 그리기 규칙](design/FlowGraph.md#63-그리기-규칙과-상수)

### 계획
- 웹 UI·흐름 그래프·시각화 인코딩 설계에 두 메시지의 이름과 표시 규칙(사람 = 노란색 계열, 턴 시작 지시 = 원, 작업 중 사용자 메시지 = 마름모)을 적는다.
- 목록 보기, 노드 상세, 턴 선택, 개요 띠의 기호·배지·설명, 그래프 범례의 이름과 모양을 맞춘다.
- I38 브랜치 위에 쌓은 `i39-human-message-naming`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 "지시"와 "사용자 메시지"를 왜 따로 정의했는지 검토하라고 했다. 둘은 기록과 역할이 다르다(턴을 시작하는 사람 입력 대 진행 중인 턴에 전달된 `queued_command`, 정보 항목 D1 대 D2). 나누는 것은 맞지만 화면 이름과 모양이 그 차이와 같은 출처임을 드러내지 못했다. 사용자가 정리를 지시해 I39로 등록했다.
- 2026-11-07: 설계 문서 세 개를 고친 뒤 화면을 맞췄다. 목록·노드 상세·턴 선택·배지·개요 띠 설명의 이름을 "턴 시작 지시", "작업 중 사용자 메시지"로 바꾸고, 턴 시작 지시를 노란 원으로, 개요 띠의 ▲를 그래프와 같은 노란 ◆로 바꿨다. 그래프 노드의 마우스 설명 앞에 종류 이름을 붙였다. 설계안의 완료 주장 기호가 ◆와 겹쳐 깃발 ⚑로 바꿨다.
- 2026-11-07: 사용자가 범례 괄호 설명("세로 점선이 모든 줄을 가로지름")이 필요한지, "압축이 있는 턴"이 무슨 뜻인지 물었다. 범례 글자는 뜻만 적고 모양 설명은 빼며, 긴 설명은 마우스를 올렸을 때 보이게 했다("추정 시각", "줄여 그린 긴 대기"도 같은 기준으로 바꿈). "압축"은 "대화 요약(문맥 압축)"으로 바꾸고 배지·기호에 뜻을 붙였다.
- 2026-11-07: 사용자 확인 뒤 완료 처리했다.

### 결정 사항
- 둘은 기록과 역할이 다르므로(D1 대 D2) 나눠 두되, 사람이 보낸 것은 같은 노란색 계열에 모양만 다르게 한다([웹 UI 설계 3절](design/WebUI.md#3-턴과-단계-표시)).
- 범례 글자에는 뜻만 적고 모양은 견본이 보여 준다. 긴 설명은 마우스를 올렸을 때 보인다.
- "압축"은 "대화 요약(문맥 압축)"으로 부른다. 설계안의 완료 주장 기호는 ◆와 겹쳐 ⚑로 바꿨다.

### 변경 파일
- `src/agentvis/analysis/graph.py`, `src/agentvis/web/graph.js`, `src/agentvis/web/app.js`, `src/agentvis/web/overview.js`, `src/agentvis/web/style.css`
- `docs/design/WebUI.md`, `docs/design/FlowGraph.md`, `docs/design/VisualEncoding.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 턴 시작 지시(노란 원)와 작업 중 사용자 메시지(노란 ◆)가 화면 모든 곳에서 같은 이름과 모양으로 보이고, 대화 요약 같은 용어에는 뜻이 붙는다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 134개 통과(화면과 그래프 이름만 바꿈).
- GitHub Actions(PR #28): `ubuntu-latest`, `macos-latest`, `windows-latest` 모두 통과.

## I38 응답 작성 시간과 그래프 범례

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [데이터 소스의 응답 작성 시간](DataSource.md#37-응답-작성-시간), [작업 흐름 그래프 설계의 노드](design/FlowGraph.md#32-노드)

### 계획
- 생각과 도구 실행 사이 빈칸의 정체를 실측해 데이터 소스에 적는다.
- 흐름 그래프 설계에 `model` 노드의 작성 구간, 도구 호출만 담은 응답의 `model` 노드, 화면의 무늬·범례·막대 맞닿음 규칙을 적는다.
- 그래프 모델과 화면 코드를 고치고 테스트를 더한다.
- I37 브랜치 위에 쌓은 `i38-generation-span`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 생각이나 Bash 사이의 긴 간격이 로깅 오류인지 물었다. 최근 세션 6개에서 주 에이전트의 20초 넘는 빈 구간 227개를 찾았다. 작업 도중의 빈 구간 193개 중 148개는 생각 → 도구 호출, 42개는 도구 호출 → 도구 호출 사이였고, 모두 도구 입력 기록이 남기 전까지의 시간이었다. 입력 중앙값은 5,756자와 4,468자였고 권한 요청은 없었다. 사용자가 작성 시간을 막대로 그리고 범례를 넣으라고 지시했다.
- 2026-11-07: 데이터 소스 3.7절과 흐름 그래프 설계(3.2절 작성 구간, 6.3절 막대·겹침·범례)를 고친 뒤 `graph.py`(`generation_started_at`, `output_chars`, 도구 호출만 담은 응답의 `gen:` 노드), `graph.js`(생각·작성으로 나눈 막대, 빗금, 막대 맞닿음, 범례, 마우스 설명), `app.js`(노드 상세의 생각·작성 시간과 글자 수)를 고쳤다. 실제 서버로 같은 세션 6개를 다시 쟀다: 주 에이전트의 20초 넘는 빈 구간이 227개에서 42개로, 그중 작업 도중의 빈 구간이 193개에서 2개로 줄었다. 남은 것은 대부분 턴이 끝난 뒤의 대기다.
- 2026-11-07: 사용자가 범례의 사용자 메시지 도형이 그래프와 다르다고 했다. 범례는 마름모를 작게(면적 60) 그리고 세로 안내선을 빼먹었으며, 지시 점(반지름 7)과 알림의 속 빈 점도 다르게 그렸다. 범례 견본이 그래프와 같은 크기 상수와 클래스를 쓰도록 고치고, 지시와 알림을 나눴다.
- 2026-11-07: 사용자가 화면을 확인했다. 완료 처리했다.

### 결정 사항
- 빈칸은 "아무도 일하지 않음"만 뜻하게 한다. 작성 시간을 막대로 채우고, 긴 대기만 물결로 줄인다.
- 도구 호출만 담은 응답은 작성에 5초 이상 걸렸을 때만 `model` 노드를 만든다(`GENERATION_NODE_MIN_MS`). 짧은 왕복까지 노드로 만들면 그래프가 어지러워진다.
- 범례 견본은 그래프와 같은 크기 상수와 클래스로 그린다. 사용자가 범례와 그래프의 도형 차이를 찾아 고쳤다.

### 변경 파일
- `src/agentvis/analysis/graph.py`, `src/agentvis/web/graph.js`, `src/agentvis/web/app.js`, `src/agentvis/web/style.css`, `tests/test_graph.py`
- `docs/DataSource.md`, `docs/design/FlowGraph.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 모델이 응답과 도구 입력을 작성한 시간이 빗금 막대로 보이고, 그래프 위 범례가 막대와 기호의 뜻을 알려 준다. 작업 도중의 20초 넘는 빈칸이 193개에서 2개로 줄었다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 134개 통과(작성 구간 테스트 추가, 기존 테스트 2개를 새 규칙에 맞춤).
- GitHub Actions(PR #27): `ubuntu-latest`, `macos-latest`, `windows-latest` 모두 통과.

## I37 세션 전체 흐름의 턴 시퀀스

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [시각화 인코딩 설계의 E1](design/VisualEncoding.md#31-e1-개요-띠), [웹 UI 설계 7절](design/WebUI.md#7-세션-개요-띠와-이동-배지)

### 계획
- 시각화 인코딩 설계의 E1·E3을 턴 단위로 바꾸고, 바꾼 이유와 버린 안(도구 호출 띠)을 남긴다.
- 웹 UI 설계 7절을 턴 시퀀스 규칙으로 다시 쓴다. 범위 고르기와 순서·실제 시간 축은 뺀다.
- `overview.js`와 `app.js`를 고친다.
- H5 브랜치 위에 쌓은 `i37-turn-sequence-overview`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 세션 전체 흐름은 턴 시퀀스를 보여 줘야 하고, 실패가 있는 턴은 빨강으로 보여 주자고 했다. 도구 호출 띠는 칸의 뜻을 알 수 없고 턴 안의 활동은 턴 상자와 겹친다는 지적이다. I37로 등록했다.
- 2026-11-07: 시각화 인코딩 설계의 E1·E3을 턴 단위로 고치고 버린 안과 이유를 남겼다. 요소 이름(E1 개요 띠)과 절 제목은 기존 링크를 지키려고 그대로 두었다. 웹 UI 설계 7절을 다시 쓰고 `overview.js`(턴 요약, 턴 칸, 배지), `app.js`(해시 `width`, 범위·축 상태 제거), `style.css`를 고쳤다. 실제 세션 8개로 턴 요약을 확인했다: 턴별 실패 수의 합이 세션 실패 수와 모두 같았고, 실패 턴마다 첫 실패 단계를 찾았다.
- 2026-11-07: 사용자가 화면을 확인했다("잘 나온다"). 완료 처리했다.

### 결정 사항
- 세션 상자는 턴을, 턴 상자는 단계를 보여 준다. 도구 호출 띠는 칸의 뜻을 알 수 없고 턴 상자와 같은 정보를 되풀이해 버렸다([시각화 인코딩 설계 E1](design/VisualEncoding.md#31-e1-개요-띠)).
- 실패한 턴으로 이동하면 그 턴의 첫 실패 단계도 고른다. 도구 호출 띠의 "실패 단계로 바로 가기"를 이렇게 살렸다.
- 요소 이름(E1 개요 띠)과 절 제목은 기존 링크를 지키려고 그대로 둔다.

### 변경 파일
- `src/agentvis/web/overview.js`, `src/agentvis/web/app.js`, `src/agentvis/web/style.css`
- `docs/design/VisualEncoding.md`, `docs/design/WebUI.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 세션 전체 흐름이 턴 시퀀스로 보인다. 실패한 턴은 빨강과 실패 수로, 작업 중 사용자 메시지와 대화 요약이 있는 턴은 기호로 보이며, 칸을 누르거나 배지로 턴을 고른다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 133개 통과(화면만 바꿈).
- GitHub Actions(PR #26): `ubuntu-latest`, `macos-latest`, `windows-latest` 모두 통과.

## H5 화면 파일 캐시와 사이드바 접기

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [수집기 설계의 HTTP 엔드포인트](design/Collector.md#2-http-엔드포인트), [웹 UI 설계의 화면 구성](design/WebUI.md#2-화면-구성)
- 관련 이슈: I35, I36

### 계획
- 서버가 정적 파일에 `Cache-Control: no-cache`를 붙여, 브라우저가 매번 서버에 바뀌었는지 묻게 한다(바뀌지 않았으면 `304`). 설계 문서를 먼저 고친다.
- 프로젝트·세션 목록에 접기 단추를 두어 각각 좁은 띠로 접고 편다(I35).
- 정적 파일 응답 헤더 테스트를 더하고, 실제 서버로 헤더를 확인한다.
- I34 브랜치 위에 쌓은 `h5-static-cache`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 그래프의 새 시간축 토글을 찾지 못했다. 정적 파일 응답에 캐시 지시가 없어 브라우저가 예전 파일을 쓴 것으로 보고 H5로 등록했다. 같은 지시의 사이드바 접기는 I35로 등록해 이 작업에서 함께 한다.
- 2026-11-07: 설계 문서를 고친 뒤 서버의 정적 파일에 `Cache-Control: no-cache`를 붙이고(`_RevalidatedStaticFiles`), 프로젝트·세션 영역에 접기 단추를 더했다. 실제 서버로 확인했다: `graph.js` 응답에 `cache-control: no-cache`와 `etag`가 있고, 같은 `etag`로 다시 물으면 `304`다.
- 2026-11-07: 사용자가 세션 상세의 네 부분(세션 정보, 세션 전체 개요, 보기 전환, 턴 내용)이 잘 구분되지 않는다고 했다. I36으로 등록해 이 작업에서 함께 한다. 각 부분을 제목이 있는 상자로 묶는다.
- 2026-11-07: 사용자가 보기 전환 단추가 턴 고르기 방식과 흐름 그리는 방식을 함께 바꿔 책임 나누기에 어긋난다고 지적했다. 턴 선택 상자를 두 보기에 공통으로 두고, 단추는 턴 작업 흐름 상자의 제목 줄로 옮겨 그리는 방식만 바꾸게 했다. 목록 보기도 고른 턴 하나만 보여 준다.
- 2026-11-07: 사용자가 사이드바 접기를 확인했다("사이드바 접기 완벽하다"). 완료 처리했다.

### 결정 사항
- 정적 파일에는 `no-cache`를 붙인다. 파일을 보관하지 않는 `no-store`와 달리, 바뀌지 않았으면 `304`로 답해 다시 받지 않는다.
- 사이드바 접힘 상태는 보는 사람의 화면 취향이라 해시가 아닌 브라우저 저장소에 둔다(I35).
- 세션 상세의 상자는 맡는 일이 하나씩이다. 턴 선택은 두 보기에 공통이고, `흐름 그래프 | 목록` 단추는 고른 턴의 흐름을 그리는 방식만 바꾼다(I36, [웹 UI 설계 2절](design/WebUI.md#2-화면-구성)).

### 변경 파일
- `src/agentvis/server.py`, `src/agentvis/web/index.html`, `src/agentvis/web/app.js`, `src/agentvis/web/style.css`, `tests/test_api.py`
- `docs/design/Collector.md`, `docs/design/WebUI.md`, `docs/design/FlowGraph.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 화면 파일을 고친 뒤 일반 새로고침만으로 새 파일이 쓰인다(H5).
- 프로젝트·세션 목록을 각각 접고 펼 수 있다(I35).
- 세션 상세가 세션 정보, 세션 전체 흐름, 턴 선택, 턴 작업 흐름의 네 상자로 나뉜다(I36).

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 133개 통과(캐시 지시와 `304` 테스트 추가).
- GitHub Actions(PR #25): `ubuntu-latest`, `macos-latest`, `windows-latest` 모두 통과.

## I34 흐름 그래프의 시간 비례 시간축

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [작업 흐름 그래프 설계의 화면](design/FlowGraph.md#6-화면), [데이터 소스의 생각 블록](DataSource.md#36-생각-블록과-그-메타데이터)

### 계획
- 생각 기록의 시각이 생각의 시작인지 끝인지 실측해 데이터 소스에 적는다.
- 흐름 그래프 설계에 두 시간축(긴 구간 줄이기, 실제 시간 비례), 물결 생략 표시, 생략을 지나는 막대의 끊김, 생각 막대, 토글 단추와 해시 상태를 적는다.
- 그래프 모델(`model` 노드 구간)과 화면 코드를 고치고 테스트를 더한다.
- I33 브랜치 위에 쌓은 `i34-graph-time-scale`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자가 가로 길이로 시간을 나타내고 긴 구간은 물결로 생략하자고 제안했고, 두 보기를 토글로 전환하자고 지시했다.
- 2026-11-07: 생각 기록 시각을 실측했다. 주 에이전트의 빈 생각 기록 472건 중 464건에서 `기록 시각 − 직전 API 요청 시각 − 걸린 시간`이 0 이상(중앙값 854ms)이었다. 기록 시각은 생각이 끝난 시점이다.
- 2026-11-07: 흐름 그래프 설계(3.2절 `model` 구간, 6.1·6.3절 두 시간축과 물결 생략)를 고친 뒤 `graph.py`, `graph.js`, `app.js`, `style.css`를 고쳤다. 실제 서버로 확인했다: 이 세션 2번 턴(459초)의 생각 노드 19개가 모두 근사 막대가 되었고, 긴 구간 줄이기에서 물결로 줄이는 10초 넘는 간격은 12개(최장 105.9초)다.
- 2026-11-07: 사용자가 단추 이름이 이해되지 않는다고 해 하는 일이 드러나는 이름으로 바꿨다. 사용자가 화면을 확인해 완료 처리했다.

### 결정 사항
- 기본 시간축은 "긴 대기 줄여 보기"다. 10초 이하 간격은 시간에 비례하고, 넘는 간격만 물결로 줄인다. 모든 길이를 실제 시간에 비례시키는 보기는 토글로 둔다([작업 흐름 그래프 설계 6.1](design/FlowGraph.md#61-배치)).
- 생각 기록의 시각은 생각이 끝난 시각이라(실측 98%), 생각을 `기록 시각 − 걸린 시간` ~ `기록 시각`의 근사 막대로 그린다([데이터 소스 3.6](DataSource.md#36-생각-블록과-그-메타데이터)).
- 단추 이름은 하는 일을 드러내는 말로 쓴다(축소, 확대, 전체 보기, 긴 대기 줄여 보기, 실제 시간 길이로 보기).

### 변경 파일
- `src/agentvis/analysis/graph.py`, `src/agentvis/web/graph.js`, `src/agentvis/web/app.js`, `src/agentvis/web/style.css`, `tests/test_graph.py`
- `docs/DataSource.md`, `docs/design/FlowGraph.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 흐름 그래프의 가로 길이가 걸린 시간에 비례한다. 긴 대기는 물결과 실제 길이로 줄여 보이고, 줄인 구간을 지나는 막대에는 물결 끊김이 있다. 생각도 막대로 보인다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 132개 통과(그래프 테스트에 생각 막대 구간 검사 추가).
- GitHub Actions(PR #24): `ubuntu-latest`, `macos-latest`, `windows-latest` 모두 통과.

## M8-T1 세션 개요 띠와 이동 배지

- 시작일: 2026-11-01
- 완료일: 2026-11-07
- 근거 문서: [시각화 인코딩 설계](design/VisualEncoding.md#31-e1-개요-띠), [웹 UI 설계](design/WebUI.md#7-세션-개요-띠와-이동-배지)

### 계획
- 웹 UI 설계에 개요 띠(E1)와 이동 배지(E3)의 데이터, 배치, 상호작용, 해시 상태, 아래 보기 연결을 정한다.
- 세션 상세 응답만으로 화면에서 계산한다. 새 API는 만들지 않는다.
- `overview.js`를 새로 만들고, `app.js`의 해시 상태·목록 보기·그래프 보기를 고른 단계와 범위에 맞게 고친다. `graph.js`에 처음 고른 노드를 받는 인자를 더한다.
- 정적 파일 테스트에 `overview.js`를 더하고, 실제 서버와 브라우저로 화면을 확인한다.
- I32 브랜치 위에 쌓은 `m8-t1-overview-strip`에서 진행한다.

### 진행 기록
- 2026-11-01: 웹 UI 설계에 7절을 썼다.
- 2026-11-01: `overview.js`를 만들고 `app.js`(해시 상태 `step`·`from`·`to`·`axis`, 세션 응답 재사용, 목록 보기의 범위 거르기와 고른 단계 강조), `graph.js`(처음 고른 노드), `style.css`를 고쳤다. 실제 세션 7개로 사건 계산을 Node에서 확인했다: 도구 호출 수와 실패 수가 세션 머리와 모두 같았다.
- 2026-11-07: 사용자가 화면을 확인했다. 개요 띠의 내용은 사용자 검토에 따라 I37에서 턴 시퀀스로 바꿨다. 완료 처리했다.

### 결정 사항
- 개요 띠는 세션 상세 응답만으로 화면에서 계산하고 새 API를 만들지 않는다([웹 UI 설계 7절](design/WebUI.md#7-세션-개요-띠와-이동-배지)).
- 같은 세션 안에서 선택만 바뀌면 세션 응답과 턴 그래프를 다시 받지 않는다. 배지로 연달아 이동할 때 느려지지 않게 하기 위해서다.
- 처음 만든 도구 호출 띠(범위 고르기, 순서·실제 시간 축)는 사용자 검토 뒤 I37에서 턴 시퀀스로 바꿨다. 이 태스크의 결과물인 개요 띠와 이동 배지의 자리, 아래 보기 연결, 해시 상태와 응답 재사용은 그대로 쓰인다.

### 변경 파일
- `src/agentvis/web/overview.js`(새 파일), `src/agentvis/web/app.js`, `src/agentvis/web/graph.js`, `src/agentvis/web/style.css`, `tests/test_api.py`
- `docs/design/WebUI.md`, `docs/index.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 세션 상세 위에 개요 띠와 이동 배지가 있어, 세션 전체에서 볼 곳을 고르고 다음·이전 실패로 바로 간다. 고른 곳이 아래 흐름 그래프와 목록에 이어진다. 띠의 내용은 I37에서 턴 시퀀스가 되었다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 130개 통과(정적 파일 테스트에 `overview.js` 추가).
- GitHub Actions(PR #22): `ubuntu-latest`, `macos-latest`, `windows-latest` 모두 통과.

## I33 내용이 빈 생각 단계에 걸린 시간과 토큰 표시

- 시작일: 2026-11-07
- 완료일: 2026-11-07
- 근거 문서: [데이터 소스의 생각 블록](DataSource.md#36-생각-블록과-그-메타데이터), [분석기 설계의 단계](design/Analysis.md#4-단계)

### 계획
- 생각 블록과 그 메타데이터를 실측해 데이터 소스 문서에 적는다.
- 분석기 설계에 `thinking` 단계의 `detail.duration_ms`, `detail.tokens`를, 흐름 그래프 설계에 `model` 노드 이름 규칙을, 웹 UI 설계에 생각 단계 표시를 적는다.
- 분석기, 그래프, 화면 코드를 고치고 테스트를 더한다.
- 진행 중인 M8-T1 브랜치 위에 쌓은 `i33-thinking-metadata`에서 진행한다.

### 진행 기록
- 2026-11-07: 사용자 질문으로 확인했다. 이 프로젝트 세션의 생각 기록 607개 중 460개는 내용이 비었고, 모두 `thinkingDurationMs`가 있으며 605개에 `thinking_tokens`가 있다. 빈 생각의 걸린 시간은 중앙값 4.2초, 최대 106초다. 사용자가 이 값을 표시하라고 지시했다.
- 2026-11-07: 데이터 소스에 생각 블록 실측을 적고, 분석기·흐름 그래프·웹 UI 설계를 고친 뒤 코드를 고쳤다. 실제 서버를 다시 띄워 확인했다: 이 세션의 생각 단계 615개 모두에 걸린 시간이, 467개에 토큰이 붙었다. 그래프의 생각 노드는 `생각 105.9초`, `생각 14.7초`처럼 나온다.

### 결정 사항
- 생각 토큰은 응답 단위 값이 되풀이되므로 같은 응답의 첫 생각 단계에만 넣는다. 합쳐 셀 때 두 번 세지 않기 위해서다.
- 기록 시각이 생각의 시작인지 끝인지 확인하지 못해, 생각은 구간이 아닌 시점으로 둔다([데이터 소스](DataSource.md#36-생각-블록과-그-메타데이터)).
- 빈 생각 노드는 지우지 않는다. 에이전트가 시간을 쓴 지점이라 과업 T5(시간을 가장 많이 쓴 구간)의 정보다.

### 변경 파일
- `src/agentvis/analysis/session.py`, `src/agentvis/analysis/graph.py`, `src/agentvis/web/app.js`
- `tests/test_analysis.py`, `tests/test_graph.py`
- `docs/DataSource.md`, `docs/design/Analysis.md`, `docs/design/FlowGraph.md`, `docs/design/WebUI.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 생각 단계와 그래프의 생각 노드에 걸린 시간과 토큰이 보인다. 내용이 기록에 남지 않은 생각은 그 사실을 적는다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 132개 통과(I33 테스트 2개 추가).


## I32 과업에 맞춘 시각화 인코딩 설계

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [과업과 데이터 추상화](design/TaskAbstraction.md), [좋은 시각화 원칙 조사](research/VisualizationPrinciples.md), [관련 결과물 조사](research/RelatedWork.md)

### 계획
- 데이터 특성에서 나온 설계 함의와 시각화 원칙으로 설계 원칙을 정한다.
- 화면을 집계 → 선택 → 원본의 세 층으로 구성하고, 요소(E1~E10)마다 정보 항목, 마크, 채널, 상호작용, 과업, 근거, 검토한 대안을 적는다.
- 데이터 유형별 인코딩 규칙, 과업 × 화면 요소 표, 기존 연구와의 차이, 구현 순서를 정리한다.
- 결과를 `docs/design/VisualEncoding.md`로 만든다. 구현은 문서가 확정된 뒤 로드맵 태스크로 나눈다.
- I31 브랜치 위에 쌓은 `i32-visual-encoding`에서 진행한다.

### 진행 기록
- 2026-11-01: 사용자가 I31 검토 결과를 기반으로 진행하라고 지시해 I32를 등록했다.
- 2026-11-01: [시각화 인코딩 설계](design/VisualEncoding.md) 초안을 썼다. 요소 10개, 데이터 유형별 채널 규칙, 과업 × 요소 표, AgentLens와의 차이, 구현 순서 5단계다. 사용자에게 검토를 요청했다.
- 2026-11-01: 사용자가 검토한 대로 진행하라고 지시했다. 설계안을 확정하고, 구현 순서 5단계를 로드맵 M8(M8-T1~M8-T5)로 등록했다.

### 결정 사항
- 기준 사건 보기(E4)를 화면의 중심 요소로 둔다. 과업 연결은 흐름 그래프 간선이 아니라 실행 순서 축 위의 호로 그린다([요소별 인코딩](design/VisualEncoding.md#34-e4-기준-사건-보기)).
- 신호 카드(E2)는 켠 조건만 기준선과 비교한다. 참가자 12명으로 3조건은 검정력이 부족하다([확인할 것](design/VisualEncoding.md#8-확인할-것)).
- 과업 중심 화면(M8)을 다른 남은 태스크보다 먼저 하고, 필요한 판정 규칙(M5)은 해당 M8 태스크 안에서 함께 설계한다([로드맵](Roadmap.md)).

### 변경 파일
- `docs/design/VisualEncoding.md`(새 문서), `docs/design/TaskAbstraction.md`, `docs/Architecture.md`, `docs/Roadmap.md`, `docs/index.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 과업마다 주 경로 화면 요소(E1~E10)와 그 마크·채널·상호작용, 설계 근거와 검토한 대안이 정해져 M8 구현을 시작할 수 있다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 130개 통과(문서만 바꿈).


## I31 과업별 정보 요구와 데이터 특성 분석

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [Claude Code 실무 고충 조사](research/ClaudeCodePainPoints.md), [좋은 시각화 원칙 조사](research/VisualizationPrinciples.md), [데이터 소스](DataSource.md)

### 계획
- 6가지 과업마다 사용자가 원본 기록으로 판정하는 절차를 적고, 그 절차에 필요한 정보 항목을 뽑는다.
- 정보 항목을 공통 사전으로 모아 원천 필드, 데이터 유형, 원본·파생, 확정·추정, 규모를 분석한다.
- 과업 × 정보 항목 표로 공통 항목과 과업 전용 항목을 가른다.
- 결과를 `docs/design/TaskAbstraction.md`로 만들고, 인코딩(시각화 방식) 설계의 입력으로 둔다.
- 최신 `main`에서 만든 브랜치 `i31-task-data-abstraction`에서 진행한다.

### 진행 기록
- 2026-11-01: 사용자 지시로 I31을 등록했다. 이 세션 기록에서 도구 결과의 실제 필드를 확인했다. Bash는 `stdout`·`stderr`·`interrupted`, 종료 코드는 오류 텍스트의 "Exit code N", Edit·Write는 `structuredPatch`·`filePath`·`originalFile`, 응답은 `usage`(토큰)를 가진다.
- 2026-11-01: [과업과 데이터 추상화](design/TaskAbstraction.md) 초안을 썼다. 내용은 판정 절차 6개, 정보 항목 40개(D1~D40), 과업 × 정보 표, 데이터 특성에서 나온 설계 함의 6개다. 사용자에게 검토를 요청했다.
- 2026-11-01: 사용자가 이 검토 결과를 기반으로 다음 단계를 진행하라고 지시했다. 초안을 확정본으로 완료 처리하고, 인코딩 설계는 다음 작업으로 이어 간다.

### 결정 사항
- 정보 목록은 연구자 분석에서 나온 가설로 두고, 형성 확인(팀원·파일럿)에서 고친다([다음 단계](design/TaskAbstraction.md#6-다음-단계)). 그 확인을 기다리지 않고 인코딩 설계를 먼저 진행한다(사용자 지시).

### 변경 파일
- `docs/design/TaskAbstraction.md`(새 문서), `docs/index.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 6가지 과업마다 판정 절차, 필수·보조 정보 항목(D1~D40), 각 항목의 데이터 유형과 원본·파생·확정·추정이 정리되어 인코딩 설계의 입력이 된다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 130개 통과(문서만 바꿈).


## H4 Windows 파일 식별자가 SQLite 정수 범위를 넘는 결함

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [이벤트 저장소 설계](design/Store.md), [기록 리더 설계](design/Transcript.md)

### 계획
- 읽기 커서의 파일 식별자(`device`, `inode`)를 크기 제한이 없는 10진 문자열로 저장하도록 설계를 고친다(스키마 4판).
- 4판 이동은 커서 표를 새 형식으로 다시 만든다. 커서는 버려도 되는 값이라(다시 읽어도 중복 저장되지 않음) 내용을 옮기지 않는다.
- 64비트를 넘는 식별자 테스트와 3판 → 4판 이동 테스트를 더한다.
- 병합 대기 중인 PR #18(`i30-target-venues`) 위에 쌓은 브랜치 `h4-windows-file-id`에서 진행한다.

### 진행 기록
- 2026-11-01: 문서만 바꾼 PR #18의 Windows CI가 기록 리더 테스트 4개에서 실패했다. 파일 식별자를 SQLite 정수 칸에 넣다가 넘친 것이라 H4로 등록했다.
- 2026-11-01: [이벤트 저장소 설계의 H4 변경](design/Store.md#9-h4-변경)대로 스키마 4판을 만들고 커서의 파일 식별자를 10진 문자열로 바꿨다. 64비트를 넘는 식별자 왕복 테스트와 3판 → 4판 이동 테스트를 더했다. 세 운영체제 CI가 통과했다(PR #19).

### 결정 사항
- 커서는 버려도 되는 값이므로 4판 이동에서 옮기지 않고 표를 다시 만든다. 실제 이벤트 저장소는 다음 서버 시작 때 4판으로 올라가고, 세션 기록을 처음부터 다시 읽는다. 원시 이벤트는 중복 저장되지 않는다.

### 변경 파일
- `src/agentvis/store.py`, `src/agentvis/transcript.py`, `tests/test_store.py`
- `docs/design/Store.md`, `docs/design/Transcript.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- Windows에서 파일 식별자가 64비트를 넘어도 세션 기록이 저장된다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 130개 통과(H4 테스트 2개 추가).
- GitHub Actions(PR #19): `ubuntu-latest`, `macos-latest`, `windows-latest` 모두 통과.


## I30 목표 학회 선정과 연구개발 목표 수정

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [제품 비전](ProductVision.md#1-목적), [관련 결과물 조사](research/RelatedWork.md)

### 계획
- 연구 주제와 가까운 탑 학회(IEEE VIS/TVCG, CHI, EuroVis, UIST, VL/HCC, VISSOFT, 소프트웨어 공학 학회)를 비교하는 문서를 만든다.
- 목표 학회와 그에 맞는 논문 구성을 제품 비전에 적고, README와 조사 문서의 "CHI" 표기를 고친다.
- PR #16(`i29-related-work`) 위에 쌓은 브랜치 `i30-target-venues`에서 진행한다.

### 진행 기록
- 2026-11-01: 사용자 지시로 I30을 등록하고 시작했다.
- 2026-11-01: [목표 학회 비교](research/TargetVenues.md)를 새로 만들었다. 연구의 성격이 설계 연구(데이터·과업 추상화, 설계, 평가)이고, 가장 가까운 선례 AgentLens가 IEEE TVCG에 실렸으므로 주 목표를 IEEE VIS(TVCG 게재), 보조 목표를 CHI로 정했다. 제품 비전, README, 인덱스, 시각화 원칙 조사의 "CHI" 표기를 고쳤다. 학회 마감 시기는 통상 주기만 적고 [확인 필요]로 두었다.
- 2026-11-01: 사용자가 목표를 다시 정했다. 1차 목표는 수업 과제의 완수이고, 연구 절차와 논문은 TVCG 기준에 맞춰 수행·작성하며, 학회 제출은 과제를 완성한 뒤 정한다. 제품 비전, README, 인덱스, 목표 학회 비교의 결정 절을 그에 맞게 고쳤다.

### 결정 사항
- 1차 목표는 수업 과제의 완수다. 연구 절차와 논문의 기준은 IEEE TVCG(IEEE VIS 정규 논문), 형식은 설계 연구다. 제출 학회(VIS, CHI, VL/HCC·VISSOFT 등)와 시기는 과제를 완성한 뒤 정한다.
- 화면 재설계 문서에는 과업 짝짓기, 검토한 대안, 버린 이유를 함께 남긴다(VIS 심사 관행).

### 변경 파일
- `docs/research/TargetVenues.md`(새 문서), `docs/ProductVision.md`, `README.md`, `docs/index.md`, `docs/research/VisualizationPrinciples.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 연구개발 목표가 "수업 과제 완수, TVCG 기준의 설계 연구"로 문서에 정해졌고, 학회 비교, 제출 후보, 논문 구성이 남아 있다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 128개 통과(코드 변경 없음).


## I29 관련 결과물 조사와 비교 (경쟁자, 배울 점)

- 시작일: 2026-11-01
- 완료일: 2026-11-01
- 근거 문서: [제품 비전](ProductVision.md#1-목적), [좋은 시각화 원칙 조사](research/VisualizationPrinciples.md)

### 계획
- 경쟁자 조사: 최신 코딩 에이전트 로그·세션·궤적 시각화(Claude Code 전용 도구, 다른 코딩 에이전트 도구, LLM 관측 플랫폼, 2024~2026 학술 시스템). AgentVis와의 유사점·차이점을 표로 비교한다.
- 배울 점 조사: 잘 만든 일반 로그·트레이스·이벤트 시각화(로그 탐색기, 트레이스·성능 도구, 오류·세션 도구, 이벤트 시퀀스·프로세스 마이닝 연구)에서 옮겨 올 설계 아이디어를 뽑는다.
- 결과를 새 문서 `docs/research/RelatedWork.md`로 만들고 인덱스에 잇는다.
- 최신 `main`에서 만든 브랜치 `i29-related-work`에서 진행한다.

### 진행 기록
- 2026-11-01: 사용자 지시로 I29를 등록했다. 두 범주를 웹 조사 서브에이전트 둘에 맡겨 병렬로 시작했다.
- 2026-11-01: 두 조사 보고를 [관련 결과물 조사](research/RelatedWork.md)로 정리하고 인덱스와 README에 이었다. 앞선 조사와 어긋난 사실(AgentLens 게재처, SeaView 참가자 수)은 문서 5절에 적고 [불확실]로 두었다.
- 2026-11-01: 사용자가 IEEE Computer Society 디지털 도서관의 게재 페이지로 AgentLens의 IEEE TVCG(2025년 8호) 게재를 확인해 주었다. 두 조사 문서의 표기와 서지를 고쳤다.

### 결정 사항
- 시각화 형태(서브에이전트 그래프, 시간축)는 이미 여러 도구에 있으므로, 논문의 기여는 "질문과 고충에 맞춘 선별과 그 효과의 실증"으로 잡는다([관련 결과물 조사의 기여 공간](research/RelatedWork.md#34-agentvis의-기여-공간)).
- 화면 재설계의 기본 구조 후보로 "집계 → 선택 → 원본" 세 층(개요 막대, 문제 칸, 이동 배지 위에 지금의 목록·그래프)을 둔다. 확정은 화면 재설계 작업에서 한다.

### 변경 파일
- `docs/research/RelatedWork.md`(새 문서), `docs/index.md`, `README.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 코딩 에이전트 로그 시각화 16개(+학술 시스템 10개)와 AgentVis의 유사점·차이점, 가장 가까운 경쟁자 5개와의 차이, AgentVis에 없는 기능과 그 판단이 표로 정리되어 있다.
- 일반 로그 시각화 도구 18개의 설계 아이디어와 AgentVis에 옮길 상위 10개가 정리되어 있다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 128개 통과(코드 변경 없음).


## I28 Windows·Linux 지원과 README 운영체제별 설치·실행 안내

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [코드 작업 규칙의 운영체제 이식성](CodeRule.md#31-운영체제-이식성), [시스템 구조의 기술 선택](Architecture.md#6-기술-선택)

### 계획
- 지원 운영체제(macOS, Linux, Windows)와 이식성 규칙(경로, UTF-8, 줄바꿈, 운영체제별 테스트, 셸 스크립트)을 문서에 정한다.
- 코드를 규칙에 맞춘다. 대상은 git 출력과 콘솔 출력의 UTF-8 처리, `.gitattributes`, 심볼릭 링크·권한 테스트의 Windows 건너뛰기다.
- CI를 macOS·Linux·Windows 세 곳에서 돌려 실제로 확인하고, 실패를 고친다.
- README.md "3. 설치와 실행"을 운영체제별 안내로 다시 쓴다.
- PR #14(`i27-readme`) 위에 쌓은 브랜치 `i28-cross-platform`에서 진행한다.

### 진행 기록
- 2026-10-31: 코드를 살펴보니 macOS 전용 기능은 없었다. Windows 위험은 세 가지였다. 커밋 검사기가 `git log` 출력을 기본 인코딩으로 해석하는 것, 출력이 파이프로 갈 때 한글이 출력되지 않는 것, git이 줄바꿈을 바꿔 D3 해시가 달라지는 것이다. 심볼릭 링크·권한 테스트도 Windows에서 실패한다. 이식성 규칙을 문서에 정하고 이에 맞춰 고쳤다.
- 2026-10-31: 세 운영체제 CI의 첫 실행에서 macOS·Linux는 통과했다. Windows는 검사기 다섯 개는 통과했지만 테스트 8개가 실패했다. 원인은 네 가지였다. 검사기 메시지의 경로 구분자, 테스트가 `HOME`으로 홈을 바꾼 것(Windows는 `USERPROFILE`), 테스트 파일 쓰기의 CRLF 변환, 같은 시각 백업 이름 충돌이다. 마지막은 제품 결함이라 [CLI 설계](design/Cli.md#33-파일-입출력)에 이름 충돌 규칙을 더하고 고쳤다. 나머지는 [운영체제 이식성](CodeRule.md#31-운영체제-이식성)의 테스트 규칙으로 정하고 고쳤다.
- 2026-10-31: 고친 뒤 세 운영체제 CI가 모두 통과했다. 단위 테스트만으로는 설치·실행을 확인할 수 없어, CI에 실행 확인 단계를 더했다. 임시 데이터 폴더로 서버를 띄워 응답을 보고, 임시 설정 파일로 hook을 설치·제거한다. Windows에서도 hook 14개 설치·제거, 서버 시작, `/health`·`/` 응답을 확인했다.

### 결정 사항
- 지원 운영체제는 macOS, Linux, Windows 10·11이다([시스템 구조의 기술 선택](Architecture.md#6-기술-선택)). Windows에서 Claude Code를 WSL 안에서 쓰면 AgentVis도 WSL 안에서 실행한다(README 3.4절).
- 검사기 메시지의 경로는 운영체제와 관계없이 `/`로 쓴다. 화면의 프로젝트 상위 경로는 그 운영체제의 구분자를 쓴다.

### 변경 파일
- `README.md`, `.gitattributes`(새 파일), `.github/workflows/verify.yml`
- `docs/Architecture.md`, `docs/CodeRule.md`, `docs/VerificationTools.md`, `docs/design/Cli.md`, `docs/design/Store.md`, `docs/design/WebUI.md`, `docs/design/Analysis.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- `src/agentvis/cli.py`, `src/agentvis/hook_settings.py`
- `tools/doclib.py`, `tools/check_commits.py`, `tools/check_docs.py`, `tools/check_pointers.py`, `tools/check_pr_order.py`, `tools/check_tasks.py`, `tools/check_web.py`
- `tests/support.py`, `tests/test_api.py`, `tests/test_store.py`, `tests/test_hook_settings.py`, `tests/test_transcript.py`, `tests/test_check_commits.py`, `tests/test_check_pr_order.py`

### 결과
- macOS, Linux, Windows에서 설치하고 실행할 수 있다. CI가 세 운영체제에서 모든 검증과 실행 확인을 돌린다.
- README.md "3. 설치와 실행"에 운영체제별 도구 설치, 저장소 받기, 공통 실행, 운영체제별 경로·환경 변수 표기, 문제 해결이 있다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 128개 통과(macOS 로컬). Windows에서는 심볼릭 링크·권한 테스트 1개를 건너뛴다.
- GitHub Actions(PR #15): `ubuntu-latest`, `macos-latest`, `windows-latest` 모두 통과(검증 명령, 실행 확인 포함).


## I27 팀 동료를 위한 README.md 작성

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [문서 작업 규칙](DocumentationRule.md)

### 계획
- 문서 작업 규칙에 루트 `README.md`를 두는 예외와 그 역할(소개·안내만, 규칙은 링크로 가리킴)을 정한다.
- 문서 링크 검사기가 README.md의 링크도 검사하고, README.md가 문서 인덱스와 CLAUDE.md로 가는 링크를 가지는지 확인하게 한다.
- 팀 동료가 알아야 할 항목을 정리해 README.md를 쓴다.
- 최신 `main`에서 만든 브랜치 `i27-readme`에서 진행한다.

### 진행 기록
- 2026-10-31: 사용자 지시로 I27을 등록하고 시작했다. PR #12, #13은 병합되어 있었다.
- 2026-10-31: 문서 작업 규칙에 루트 `README.md` 예외와 역할을 정하고, 문서 링크 검사기에 README의 링크 검사와 필수 링크(문서 인덱스, CLAUDE.md) 검사를 더했다.
- 2026-10-31: 팀 동료가 알아야 할 항목을 8개로 정리해 README.md를 썼다. 1) 무엇을 왜 만드는가(연구 목적, 질문, 고충 6가지), 2) 현재 상태, 3) 설치와 실행(hook이 전역 설정을 바꾼다는 점 포함), 4) 데이터와 개인정보(IRB 전제), 5) 저장소 구조, 6) 협업 규칙 요약, 7) 주요 문서, 8) 문제 해결.

### 결정 사항
- README.md는 안내용 요약만 둔다. 규칙 원문은 규칙 문서에 두고 링크로 가리키며, 둘이 어긋나면 규칙 문서가 기준이다([문서 작업 규칙의 형식](DocumentationRule.md#2-형식)).
- README.md에서 코드 파일로 직접 링크하지 않는다. 코드 포인터는 설계 문서가 맡는다.

### 변경 파일
- `README.md`(새 문서)
- `docs/DocumentationRule.md`, `docs/VerificationTools.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- `tools/doclib.py`, `tools/check_docs.py`, `tests/test_check_docs.py`

### 결과
- 저장소 첫 화면에서 팀 동료가 프로젝트 목적, 현재 상태, 설치·실행, 데이터 주의 사항, 협업 규칙을 한 번에 볼 수 있다.
- README.md의 링크가 깨지거나 필수 링크가 빠지면 `check_docs`가 실패한다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 127개 통과(README 검사 2개 추가).


## I25 연구 목적(유저 스터디) 반영과 기초 조사

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [제품 비전](ProductVision.md)

### 계획
- 연구 목적(유저 스터디)을 제품 비전에 적는다.
- 두 주제를 조사해 `docs/research/`에 문서로 남긴다: 좋은 시각화 원칙, Claude Code 바이브 코딩의 실무 고충(커뮤니티 반응).
- 조사 결과에서 AgentVis 화면 개선 방향(중요 정보를 추린 시각화)과 유저 스터디 과제 후보를 뽑는다.
- PR #12(`m4-t8-flow-graph-screen`) 위에 쌓은 브랜치 `i25-research-foundation`에서 진행한다.

### 진행 기록
- 2026-10-31: 사용자가 연구 목적과 조사 주제 두 가지를 지시해 I25로 등록했다. 두 주제를 각각 웹 조사 서브에이전트에 맡겨 병렬로 시작했다.
- 2026-10-31: 사용자가 목적을 더 정확히 했다(대학원 수업 프로젝트, CHI 같은 학회 제출 전 단계, 과제는 데이터 선정·시각화·시각화 필요 이유·유저 스터디·논문). 제품 비전에 반영하고, 시각화 조사에 "시각화가 필요한 이유"와 "CHI 형식 유저 스터디 설계"를 더 맡겼다.
- 2026-10-31: 두 조사 보고를 [좋은 시각화 원칙 조사](research/VisualizationPrinciples.md)와 [Claude Code 바이브 코딩 실무 고충 조사](research/ClaudeCodePainPoints.md)로 정리하고 인덱스에 "연구 조사" 절을 더했다. 서브에이전트가 확인하지 못했다고 표시한 출처는 [불확실]로 남겼다. 사용자 검토를 기다린다.
- 2026-10-31: 사용자가 조사 문서를 확인했다("조사 문서 좋다"). 조사가 고른 6가지 고충으로 유저 스터디를 설계하기로 하고, 사용자 결정을 이슈 I26으로 등록했다.

### 결정 사항
- AgentVis는 연구용 시각화 애플리케이션이다. 화면은 자료를 모두 보여 주기보다 실제 고충에 답하는 정보를 추려 보여 준다([제품 비전](ProductVision.md#1-목적)).

### 변경 파일
- `docs/ProductVision.md`, `docs/index.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`
- `docs/research/VisualizationPrinciples.md`, `docs/research/ClaudeCodePainPoints.md`(새 문서)

### 결과
- 연구 목적(대학원 수업 프로젝트, CHI 형식 논문, 유저 스터디)이 제품 비전에 있다.
- 시각화가 필요한 이유, 시각화 원칙, 같은 분야 연구, 유저 스터디 설계 근거, Claude Code 실무 고충과 그 관찰 가능성이 조사 문서로 정리되어 유저 스터디 설계(I26)를 시작할 수 있다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 125개 통과(코드 변경 없음).
- 사용자 검토: 조사 문서 확인.


## M4-T8 작업 흐름 그래프 화면 (D3)

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [작업 흐름 그래프 설계](design/FlowGraph.md), [웹 UI 설계](design/WebUI.md)
- 관련 이슈: I24

### 계획
- D3 7.9.0을 npm 레지스트리에서 받아 무결성을 확인하고 `web/vendor/`에 넣은 뒤 라이브러리 표에 적는다.
- 확대·이동 방식과 그리기 규칙·상수를 설계 문서에 정한다.
- `graph.js`로 그래프를 그리고, `app.js`에 보기 전환·턴 고르기·노드 상세를 더한다.
- 정적 파일 제공 테스트를 더하고, 미리보기 서버로 사용자가 브라우저에서 확인한다.
- PR #11(`m4-t7-flow-graph-api`) 위에 쌓은 브랜치 `m4-t8-flow-graph-screen`에서 진행한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다. D3 압축 파일의 SHA-512가 레지스트리의 무결성 값과 같았다.
- 2026-10-31: 그냥 휠로 확대하면 페이지 세로 이동을 가로채므로, 확대는 `Ctrl`·`⌘`+휠·핀치·단추로, 이동은 가로 스크롤로 하도록 설계를 고쳤다.
- 2026-10-31: `graph.js`와 `app.js`의 그래프 보기를 만들고, 헤드리스 Chrome으로 이 세션의 35·51번째 턴 화면을 찍어 확인했다. 가로 스크롤 때 줄 이름이 사라져 줄 이름 칸을 고정했고, 끊김 길이 글자가 겹쳐 가까운 글자는 빼도록 설계와 코드를 고쳤다. 사용자 브라우저 확인을 기다린다.
- 2026-10-31: 사용자가 미리보기 서버에서 흐름 그래프 노드의 상세 내용이 잘 나온다고 확인했다. 사용자가 이어서 화면 방향을 "중요한 정보를 추려 쉽게 보이는 시각화"로 바꾸자고 해, 이 그래프는 앞으로 상세 보기로 쓴다.

### 결정 사항
- 확대는 `Ctrl`·`⌘`+휠·핀치·단추로, 이동은 가로 스크롤로 한다. 그냥 휠은 페이지 세로 이동에 남긴다([작업 흐름 그래프 설계의 상호작용](design/FlowGraph.md#62-상호작용)).
- 줄 이름 칸은 가로 스크롤과 따로 고정한다.

### 변경 파일
- `src/agentvis/web/vendor/d3-7.9.0.min.js`, `src/agentvis/web/vendor/LICENSE-d3.txt`(새 파일)
- `src/agentvis/web/graph.js`(새 파일), `src/agentvis/web/app.js`, `src/agentvis/web/index.html`, `src/agentvis/web/style.css`
- `tests/test_api.py`
- `docs/design/FlowGraph.md`, `docs/design/WebUI.md`, `docs/Roadmap.md`, `docs/Issue.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- 세션 상세에서 흐름 그래프와 목록을 오갈 수 있다. 그래프는 턴 하나의 주 에이전트·서브에이전트·백그라운드 작업을 줄로, 도구 호출을 실행 구간 막대로 압축 시간축 위에 그리고, 노드를 누르면 그 단계의 상세를 보여 준다.

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 125개 통과(그래프 화면 파일과 D3 제공 확인 포함).
- 헤드리스 Chrome으로 이 세션의 35·51번째 턴 화면을 찍어 그려짐을 확인했다.
- 브라우저 확인(사용자, 2026-10-31): 흐름 그래프 노드의 상세 내용이 잘 나온다.


## M4-T7 작업 흐름 그래프 모델과 조회 API

- 시작일: 2026-10-31
- 완료일: 2026-10-31
- 근거 문서: [작업 흐름 그래프 설계](design/FlowGraph.md), [분석기 설계](design/Analysis.md)
- 관련 이슈: I24, H3

### 계획
- 분석기에 단계의 `message_id`, 도구 호출의 실행 구간·`approximate`·`background`, 작업 알림 본문 해석을 더한다.
- H3: 서브에이전트 안의 hook 이벤트를 그 서브에이전트의 도구 호출에 합친다.
- `analysis/graph.py`에 `build_turn_graph`를, catalog에 `get_turn_graph`를, 서버 앱에 `GET /api/sessions/{session_id}/turns/{index}/graph`를 만든다.
- 테스트(`tests/test_graph.py`, `tests/test_analysis.py`, `tests/test_api.py`)를 더하고 실제 세션으로 그래프를 확인한다.
- PR #10(`m4-t6-flow-graph-design`) 위에 쌓은 브랜치 `m4-t7-flow-graph-api`에서 진행한다.

### 진행 기록
- 2026-10-31: 로드맵을 `[~]`로 바꾸고 시작했다. 실제 세션을 분석해 보니 서브에이전트 도구 호출 33건이 부모 턴에 hook만 있는 단계로 중복되어 H3으로 등록했다.
- 2026-10-31: 분석기에 `message_id`, 실행 구간(`started_at`, `ended_at`, `approximate`), `background`, 작업 알림 본문 해석을 더하고, 서브에이전트 기록을 hook 적용 전에 만들어 `agent_id`가 있는 hook을 그 서브에이전트에 합쳤다(H3). 서브에이전트 도구 호출의 상태는 부모 턴의 상태를 따른다.
- 2026-10-31: 실제 세션으로 그래프를 그려 보고 두 가지를 설계에 반영했다. 서버처럼 턴보다 오래 사는 백그라운드 작업은 세션이 끝나기 전까지 `running`이다(구현이 설계와 달라 고쳤다). 턴이 멈춘 뒤 작업 알림을 받아 이어서 일하면 그 기록도 같은 턴에 속하므로, 주 에이전트 줄의 끝은 턴 끝과 줄 노드 마지막 시각 중 늦은 것이다.
- 2026-10-31: 미리보기 서버(8766)에서 이 세션의 35번째 턴 그래프가 주 에이전트와 백그라운드 서브에이전트 두 줄, 노드 68개, 간선 74개로 나오고, 없는 턴은 `404`임을 확인했다. hook이 없어 근사한 막대는 0개였다.

### 결정 사항
- 서브에이전트 hook 중 그 서브에이전트 기록이 아직 없는 것은 버린다. 세션 기록을 읽으면 다시 계산되기 때문이다([분석기의 서브에이전트](design/Analysis.md#6-서브에이전트)).

### 변경 파일
- `src/agentvis/analysis/session.py`, `src/agentvis/analysis/graph.py`(새 모듈), `src/agentvis/analysis/catalog.py`, `src/agentvis/server.py`
- `tests/test_graph.py`(새 테스트), `tests/test_analysis.py`, `tests/test_api.py`
- `docs/design/FlowGraph.md`, `docs/design/Analysis.md`, `docs/Issue.md`, `docs/Roadmap.md`, `docs/Ongoing.md`, `docs/Done.md`

### 결과
- `GET /api/sessions/{session_id}/turns/{index}/graph`가 턴 하나의 줄·노드·간선을 돌려준다. 병렬 호출의 갈라짐·합류, 서브에이전트·백그라운드 작업 줄, hook 기준 실행 구간이 들어 있어 M4-T8 화면을 만들 수 있다.
- 서브에이전트 도구 호출이 부모 턴에 중복으로 나오지 않고, hook의 실행 시간과 실패가 서브에이전트 도구 호출에 붙는다(H3).

### 검증
- `check_docs`, `check_pointers`, `check_tasks`, `check_commits`, `check_web` 통과. 단위 테스트 125개 통과(그래프 10개, 분석기 2개, API 1개 추가).


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
