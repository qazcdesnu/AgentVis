# CLI 설계

이 문서는 `agentvis` 명령(`src/agentvis/cli.py`)의 M1 범위와, Claude Code 설정에 hook을 넣고 빼는 로직(`src/agentvis/hook_settings.py`), 패키지 골격을 설계한다. 서버 앱은 [수집기 설계](Collector.md)에, 이벤트 저장소는 [이벤트 저장소 설계](Store.md)에 있다. 관련 태스크는 [로드맵](../Roadmap.md#m1-수집-기반)의 M1-T1, M1-T4, M1-T5다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

구현할 심볼은 인라인 코드로 적었다. 태스크를 시작할 때 [작업 관리 규칙](../TaskRule.md#41-시작)에 따라 코드 포인터 링크로 바꾼다.

## 1. 패키지 골격

M1-T1에서 만든다.

- 패키지는 `src/agentvis/`에 두며 `pyproject.toml`에 빌드 백엔드(`uv_build`)를 설정한다.
- 런타임 의존성 `fastapi`, `uvicorn`과 테스트용 개발 의존성 `httpx2`(FastAPI `TestClient`가 사용)를 [코드 작업 규칙](../CodeRule.md#3-언어와-스타일)에 따라 `uv add`로 추가한다. 처음에는 `httpx`를 썼으나 Starlette 1.10이 `TestClient`의 `httpx` 사용을 폐기 예정으로 표시해 M1-T3에서 `httpx2`로 바꿨다.
- `[project.scripts]`에 `agentvis = "agentvis.cli:main"`을 등록해 `uv run agentvis <하위 명령>`으로 실행한다.
- [agentvis 패키지](../../src/agentvis/__init__.py)는 [`__version__`](../../src/agentvis/__init__.py#__version__)으로 설치된 패키지의 버전(`pyproject.toml`의 `version`)을 제공한다. 버전은 `importlib.metadata`로 읽어, 버전 정보가 한 곳에만 있게 한다.
- [cli 모듈](../../src/agentvis/cli.py)의 [main](../../src/agentvis/cli.py#main)은 [2. 명령](#2-명령)의 진입점이다. M1-T1에서는 `--version` 옵션(`agentvis <버전>` 출력)만 있으며, 하위 명령 없이 실행하면 도움말을 출력하고 종료 코드 0을 돌려준다. 하위 명령은 M1-T4, M1-T5에서 추가한다.

## 2. 명령

| 명령 | 동작 |
| --- | --- |
| `agentvis serve [--port N]` | 기본 경로의 이벤트 저장소로 서버 앱을 만들어 `127.0.0.1:N`에서 실행한다. 기본 포트는 `8765`. |
| `agentvis hooks install [--port N] [--settings PATH]` | Claude Code 설정 파일에 AgentVis hook을 추가한다. 기본 설정 파일은 `~/.claude/settings.json`. |
| `agentvis hooks uninstall [--settings PATH]` | 설정 파일에서 AgentVis hook만 제거한다. |

- 서버는 루프백 주소(`127.0.0.1`)에만 바인딩하며, 다른 주소를 지정하는 옵션은 두지 않는다([설계 원칙](../Architecture.md#2-설계-원칙)).
- `main(argv: list[str] | None = None) -> int`가 진입점이며 종료 코드를 돌려준다. 하위 명령은 표준 라이브러리 `argparse`로 구성한다.
- `hooks install`, `hooks uninstall`은 바꾼 설정 파일 경로와 백업 경로, 추가·제거한 이벤트 수를 출력한다.

### 2.1 serve

M1-T4에서 만든다.

- 기본 포트는 [DEFAULT_PORT](../../src/agentvis/cli.py#DEFAULT_PORT)(`8765`)다. `hooks install`의 기본 포트도 같은 상수를 쓴다.
- `--port`는 1~65535 정수만 받는다. 그 밖의 값은 `argparse` 오류(종료 코드 2)로 끝난다.
- 이벤트 저장소는 [이벤트 저장소 설계의 기본 경로](Store.md#1-데이터-디렉터리)(`default_db_path()`)로 연다. 시작할 때 `AgentVis 서버: http://127.0.0.1:<포트>` 와 `데이터베이스: <경로>` 두 줄을 출력한다. uvicorn 로그보다 먼저 보이도록 바로 내보낸다(`flush`).
- 서버는 `uvicorn.run(app, host="127.0.0.1", port=<포트>)`로 실행한다. 서버가 끝나면(Ctrl+C 포함) 이벤트 저장소를 닫고 종료 코드 0을 돌려준다.
- 포트를 이미 다른 프로세스가 쓰고 있으면 uvicorn이 `address already in use` 오류를 출력하고 시작 실패 종료 코드 3(`uvicorn.config.STARTUP_FAILURE`)으로 끝난다. 이 경우에도 이벤트 저장소를 닫는다. (M1-T4 실측으로 확인)

## 3. hook 설정 편집

M1-T5에서 만든다. [hook_settings 모듈](../../src/agentvis/hook_settings.py)은 설정 JSON을 다루는 순수 함수와 파일 입출력을 분리한다.

### 3.1 식별

AgentVis hook은 URL의 쿼리 `client=agentvis`로 식별한다. Claude Code 설정 항목에 임의의 키를 더하지 않기 위해서다. 사용자가 직접 만든 hook은 이 쿼리가 없으므로 건드리지 않는다.

| 심볼 | 역할 |
| --- | --- |
| [HOOK_EVENTS](../../src/agentvis/hook_settings.py#HOOK_EVENTS) | 등록할 이벤트 이름 튜플. [사용하는 이벤트](../DataSource.md#23-사용하는-이벤트) 표의 15개와 같다. |
| [HOOK_TIMEOUT_SECONDS](../../src/agentvis/hook_settings.py#HOOK_TIMEOUT_SECONDS) | hook의 `timeout`. `2`. 수집기는 즉시 응답하므로 짧게 둔다([전달 방식](../DataSource.md#21-전달-방식)). |
| [hook_url](../../src/agentvis/hook_settings.py#hook_url) `(port: int) -> str` | `http://127.0.0.1:<port>/hooks?client=agentvis` |
| [is_agentvis_hook](../../src/agentvis/hook_settings.py#is_agentvis_hook) `(handler: object) -> bool` | 객체이고, `type`이 `http`이며, URL 쿼리의 `client` 값에 `agentvis`가 있는지 |

### 3.2 추가와 제거

| 심볼 | 동작 |
| --- | --- |
| [install_hooks](../../src/agentvis/hook_settings.py#install_hooks) `(settings: dict, port: int) -> tuple[dict, int]` | 먼저 기존 AgentVis hook을 모두 제거한 뒤, `HOOK_EVENTS`의 각 이벤트 목록 끝에 아래 그룹을 하나씩 덧붙인 새 설정과 추가한 수를 돌려준다. 그룹에 `matcher`를 두지 않아 모든 도구에 적용된다. 같은 명령을 여러 번 실행해도 결과가 같고, 포트를 바꿔 다시 설치하면 새 포트로 바뀐다. |
| [uninstall_hooks](../../src/agentvis/hook_settings.py#uninstall_hooks) `(settings: dict) -> tuple[dict, int]` | AgentVis hook을 제거한 새 설정과 제거한 수를 돌려준다. 한 그룹에 사용자 hook이 함께 있으면 AgentVis hook만 빼고 그룹은 남긴다. 그 결과 비게 된 그룹, 이벤트 목록, `hooks` 객체는 지운다. |

```json
{ "hooks": [ { "type": "http", "url": "http://127.0.0.1:8765/hooks?client=agentvis", "timeout": 2 } ] }
```

- 두 함수는 입력 객체를 바꾸지 않고 새 객체를 돌려준다.
- `hooks` 외의 설정 키와 다른 hook은 순서까지 그대로 둔다.
- 설정 구조가 예상과 다르면(`hooks`가 객체가 아님, 이벤트 값이 목록이 아님, 그룹이 객체가 아니거나 그룹의 `hooks`가 목록이 아님) [SettingsError](../../src/agentvis/hook_settings.py#SettingsError)를 낸다. 알 수 없는 구조를 덮어써 사용자 설정을 망가뜨리지 않기 위해서다.

### 3.3 파일 입출력

| 심볼 | 동작 |
| --- | --- |
| [default_settings_path](../../src/agentvis/hook_settings.py#default_settings_path) `() -> Path` | `~/.claude/settings.json` (Claude Code 사용자 설정) |
| [load_settings](../../src/agentvis/hook_settings.py#load_settings) `(path: Path) -> dict` | 파일이 없으면 `{}`. JSON이 아니거나 JSON 객체가 아니면 `SettingsError`를 낸다. |
| [backup_settings](../../src/agentvis/hook_settings.py#backup_settings) `(path: Path, backup_dir: Path) -> Path \| None` | 파일이 있으면 `backup_dir/settings-<UTC 시각, 마이크로초까지>.json`으로 내용을 복사하고 그 경로를 돌려준다. 파일이 없으면 `None`. 백업 디렉터리는 데이터 디렉터리 아래 `backups/`다. |
| [save_settings](../../src/agentvis/hook_settings.py#save_settings) `(path: Path, settings: dict) -> None` | 경로가 심볼릭 링크면 링크가 가리키는 실제 파일에 쓴다. 같은 디렉터리의 임시 파일에 쓴 뒤 바꿔치기해 원자적으로 저장하고, 원래 파일이 있었으면 그 권한을 유지한다. 들여쓰기 2칸, `ensure_ascii=False`, 마지막 줄바꿈 포함. 부모 디렉터리가 없으면 만든다. |

설치·제거 명령은 `load_settings` → `install_hooks`/`uninstall_hooks` 순서로 새 설정을 계산하고, 설정이 실제로 바뀌는 경우에만 `backup_settings` → `save_settings`를 실행한다. 바뀌지 않으면 백업도 저장도 하지 않는다.

### 3.4 hooks 명령

- `agentvis hooks install [--port N] [--settings PATH]`: 기본 포트는 [DEFAULT_PORT](../../src/agentvis/cli.py#DEFAULT_PORT), 기본 설정 파일은 `default_settings_path()`다. `설정 파일: <경로>`, `백업: <경로 또는 "없음(새 파일)">`, `추가한 hook: <수>개 (<URL>)`를 출력한다. 이미 같은 설치가 되어 있으면 `변경 없음`을 출력한다.
- `agentvis hooks uninstall [--settings PATH]`: `설정 파일: <경로>`, `백업: <경로>`, `제거한 hook: <수>개`를 출력한다. 제거할 hook이 없으면 `제거할 AgentVis hook 없음`을 출력한다.
- `SettingsError`가 나면 사유를 표준 오류에 출력하고 종료 코드 1로 끝나며 파일은 바뀌지 않는다. 성공하면 종료 코드 0이다.
- `hooks`만 입력하면 `hooks`의 도움말을 출력하고 종료 코드 0이다.

## 4. 테스트

- [tests/test_cli.py](../../tests/test_cli.py) (M1-T1, M1-T4)
  - `main(["--version"])`이 `agentvis <버전>`을 출력하고, 그 버전이 `__version__`과 같다.
  - 인자 없이 실행하면 도움말을 출력하고 0을 돌려준다.
  - `serve`가 `uvicorn.run`을 `127.0.0.1`과 기본 포트(또는 `--port` 값)로 호출하고, `AGENTVIS_HOME` 아래 데이터베이스를 연다. 테스트에서는 `uvicorn.run`을 가짜로 바꿔 서버를 실제로 띄우지 않는다.
  - 범위를 벗어난 `--port`는 종료 코드 2로 거부된다.
  - `uvicorn.run`이 시작 실패(`SystemExit(3)`)로 끝나도 이벤트 저장소가 닫힌다.
- [tests/test_hook_settings.py](../../tests/test_hook_settings.py) (M1-T5)
  - 빈 설정에 설치하면 `HOOK_EVENTS`의 모든 이벤트에 AgentVis hook이 하나씩 생긴다.
  - 두 번 설치해도 hook이 중복되지 않고, 다른 포트로 설치하면 URL이 바뀐다.
  - 사용자가 만든 hook과 다른 설정 키는 설치·제거 후에도 순서까지 그대로다. 같은 그룹에 섞인 사용자 hook도 남는다.
  - 제거 후 비게 된 그룹·목록·`hooks` 객체가 사라지고, 입력 객체는 바뀌지 않는다.
  - 구조가 예상과 다른 설정과 JSON 객체가 아닌 설정 파일은 `SettingsError`를 낸다.
  - 저장한 파일을 다시 읽으면 같은 설정이고, 권한이 유지되며, 심볼릭 링크는 링크로 남고 대상 파일이 바뀐다. 백업 파일은 원본과 같고 이름이 겹치지 않는다.
- [tests/test_cli.py](../../tests/test_cli.py) (M1-T5 추가분)
  - 임시 설정 파일로 `hooks install` → `hooks uninstall`을 실행하면 원래 설정으로 돌아오고, 백업은 `AGENTVIS_HOME/backups/`에 생긴다.
  - 같은 설치를 다시 하면 `변경 없음`을 출력하고 백업을 만들지 않는다.
  - 잘못된 설정 파일이면 종료 코드 1이고 파일이 바뀌지 않는다.
