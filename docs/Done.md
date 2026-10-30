# 완료

이 문서는 끝난 작업의 상세 기록이다. 최신 기록이 맨 위에 온다. 기록 형식은 [작업 관리 규칙](TaskRule.md#5-기록-형식)을 따르며, 할 일 목록은 [로드맵](Roadmap.md)과 [이슈](Issue.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

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
