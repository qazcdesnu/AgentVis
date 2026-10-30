# CLI 설계

이 문서는 `agentvis` 명령(`src/agentvis/cli.py`)의 M1 범위와, Claude Code 설정에 hook을 넣고 빼는 로직(`src/agentvis/hook_settings.py`), 패키지 골격을 설계한다. 서버 앱은 [수집기 설계](Collector.md)에, 저장소는 [저장소 설계](Store.md)에 있다. 관련 태스크는 [로드맵](../Roadmap.md#m1-수집-기반)의 M1-T1, M1-T4, M1-T5다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

구현할 심볼은 인라인 코드로 적었다. 태스크를 시작할 때 [작업 관리 규칙](../TaskRule.md#41-시작)에 따라 코드 포인터 링크로 바꾼다.

## 1. 패키지 골격

- 패키지는 `src/agentvis/`에 두며 `pyproject.toml`에 빌드 백엔드(`uv_build`)를 설정한다.
- 런타임 의존성 `fastapi`, `uvicorn`과 테스트용 개발 의존성 `httpx`(FastAPI `TestClient`가 사용)를 [코드 작업 규칙](../CodeRule.md#3-언어와-스타일)에 따라 `uv add`로 추가한다.
- `[project.scripts]`에 `agentvis = "agentvis.cli:main"`을 등록해 `uv run agentvis <하위 명령>`으로 실행한다.

## 2. 명령

| 명령 | 동작 |
| --- | --- |
| `agentvis serve [--port N]` | 기본 경로의 저장소로 서버 앱을 만들어 `127.0.0.1:N`에서 실행한다. 기본 포트는 `8765`. |
| `agentvis hooks install [--port N] [--settings PATH]` | Claude Code 설정 파일에 AgentVis hook을 추가한다. 기본 설정 파일은 `~/.claude/settings.json`. |
| `agentvis hooks uninstall [--settings PATH]` | 설정 파일에서 AgentVis hook만 제거한다. |

- 서버는 루프백 주소(`127.0.0.1`)에만 바인딩하며, 다른 주소를 지정하는 옵션은 두지 않는다([설계 원칙](../Architecture.md#2-설계-원칙)).
- `main(argv: list[str] | None = None) -> int`가 진입점이며 종료 코드를 돌려준다. 하위 명령은 표준 라이브러리 `argparse`로 구성한다.
- `hooks install`, `hooks uninstall`은 바꾼 설정 파일 경로와 백업 경로, 추가·제거한 이벤트 수를 출력한다.

## 3. hook 설정 편집

`hook_settings.py`는 설정 JSON을 다루는 순수 함수와 파일 입출력을 분리한다.

### 3.1 식별

AgentVis hook은 URL의 쿼리 `client=agentvis`로 식별한다. Claude Code 설정 항목에 임의의 키를 더하지 않기 위해서다. 사용자가 직접 만든 hook은 이 쿼리가 없으므로 건드리지 않는다.

| 심볼 | 역할 |
| --- | --- |
| `HOOK_EVENTS` | 등록할 이벤트 이름 튜플. [사용하는 이벤트](../DataSource.md#23-사용하는-이벤트) 표와 같다. |
| `hook_url(port: int) -> str` | `http://127.0.0.1:<port>/hooks?client=agentvis` |
| `is_agentvis_hook(handler: dict) -> bool` | `type`이 `http`이고 URL 쿼리에 `client=agentvis`가 있는지 |

### 3.2 추가와 제거

| 심볼 | 동작 |
| --- | --- |
| `install_hooks(settings: dict, port: int) -> tuple[dict, int]` | 먼저 기존 AgentVis hook을 모두 제거한 뒤, `HOOK_EVENTS`의 각 이벤트에 아래 항목을 하나씩 덧붙인 새 설정과 추가한 수를 돌려준다. 같은 명령을 여러 번 실행해도 결과가 같고, 포트를 바꿔 다시 설치하면 새 포트로 바뀐다. |
| `uninstall_hooks(settings: dict) -> tuple[dict, int]` | AgentVis hook을 제거한 새 설정과 제거한 수를 돌려준다. 그 결과 비게 된 matcher 그룹, 이벤트 목록, `hooks` 객체는 지운다. |

```json
{ "hooks": [ { "type": "http", "url": "http://127.0.0.1:8765/hooks?client=agentvis", "timeout": 2 } ] }
```

- 두 함수는 입력 객체를 바꾸지 않고 새 객체를 돌려준다.
- `hooks` 외의 설정 키와 다른 hook은 순서까지 그대로 둔다.

### 3.3 파일 입출력

| 심볼 | 동작 |
| --- | --- |
| `load_settings(path: Path) -> dict` | 파일이 없으면 `{}`. JSON 객체가 아니면 `SettingsError`를 내고 아무것도 바꾸지 않는다. |
| `backup_settings(path: Path, backup_dir: Path) -> Path \| None` | 파일이 있으면 `backup_dir/settings-<UTC 시각>.json`으로 복사하고 그 경로를 돌려준다. 백업 디렉터리는 데이터 디렉터리 아래 `backups/`다. |
| `save_settings(path: Path, settings: dict) -> None` | 같은 디렉터리의 임시 파일에 쓴 뒤 바꿔치기해 원자적으로 저장한다. 들여쓰기 2칸, `ensure_ascii=False`, 마지막 줄바꿈 포함. |

설치·제거 명령은 `load_settings` → `backup_settings` → `install_hooks`/`uninstall_hooks` → `save_settings` 순서로 실행한다. 바뀐 것이 없으면(제거할 hook이 없으면) 저장하지 않는다.

## 4. 테스트

- `tests/test_hook_settings.py`
  - 빈 설정에 설치하면 `HOOK_EVENTS`의 모든 이벤트에 AgentVis hook이 하나씩 생긴다.
  - 두 번 설치해도 hook이 중복되지 않고, 다른 포트로 설치하면 URL이 바뀐다.
  - 사용자가 만든 hook과 다른 설정 키는 설치·제거 후에도 그대로다.
  - 제거 후 비게 된 그룹·목록·`hooks` 객체가 사라진다.
  - JSON 객체가 아닌 설정 파일은 `SettingsError`를 내고 파일이 바뀌지 않는다.
  - 저장한 파일을 다시 읽으면 같은 설정이고, 백업 파일이 원본과 같다.
- `tests/test_cli.py`
  - 임시 설정 파일 경로로 `hooks install` → `hooks uninstall`을 실행하면 원래 설정으로 돌아온다.
