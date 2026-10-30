# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

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
- 2026-10-31: RecommandShopping 세션의 이벤트 `cwd`가 프로젝트 폴더가 아니라 하위 폴더(`…/backend`)였다. 세션 기록의 시작 경로는 `…/RecommandShopping`이므로, 프로젝트 판정 기준을 "세션의 첫 `cwd`"에서 "세션 기록의 첫 `cwd`"로 [데이터 소스](DataSource.md#25-실측으로-확인한-동작), [시스템 구조](Architecture.md#42-파생-모델), [이벤트 저장소 설계](design/Store.md#3-자료형), [로드맵](Roadmap.md)(M3-T5)에서 바로잡았다.

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
- 2026-10-31: 분석에 영향을 주는 동작을 [실측으로 확인한 동작](DataSource.md#25-실측으로-확인한-동작)에 정리했다. 권한이 없어 막힌 도구는 완료 이벤트가 없다는 점, 서브에이전트 이벤트의 `agent_id`, `/compact` 요약 서브에이전트의 `SubagentStop`이 대상이다. 서브에이전트 기록 파일의 위치와 메타 파일 구조도 [세션 기록 위치](DataSource.md#31-위치)에 적었다.
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
