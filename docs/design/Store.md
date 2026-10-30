# 저장소 설계

이 문서는 원시 이벤트를 저장하고 조회하는 저장소(`src/agentvis/store.py`)를 설계한다. 구성 요소 전체에서의 위치는 [시스템 구조](../Architecture.md#3-구성-요소)에, 원시 이벤트의 정의는 [데이터 모델](../Architecture.md#41-원시-이벤트)에 있다. 관련 태스크는 [로드맵](../Roadmap.md#m1-수집-기반)의 M1-T1, M1-T2다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

구현할 심볼은 인라인 코드로 적었다. 태스크를 시작할 때 [작업 관리 규칙](../TaskRule.md#41-시작)에 따라 코드 포인터 링크로 바꾼다.

## 1. 데이터 디렉터리

- 기본 경로는 `~/.agentvis/`이다. 환경 변수 `AGENTVIS_HOME`이 있으면 그 경로를 쓴다.
- 데이터베이스 파일은 데이터 디렉터리 아래 `agentvis.db`다.
- 디렉터리가 없으면 저장소를 열 때 만든다.

| 심볼 | 역할 |
| --- | --- |
| `data_dir() -> Path` | 데이터 디렉터리 경로를 돌려준다. 만들지는 않는다. |
| `default_db_path() -> Path` | `data_dir() / "agentvis.db"` |

## 2. 스키마

SQLite 테이블 하나로 원시 이벤트를 저장한다. 파생 모델 테이블은 M3에서 설계한다.

```sql
CREATE TABLE raw_events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    source       TEXT NOT NULL CHECK (source IN ('hook', 'transcript')),
    kind         TEXT NOT NULL,
    session_id   TEXT,
    prompt_id    TEXT,
    tool_use_id  TEXT,
    occurred_at  TEXT NOT NULL,   -- ISO 8601, UTC
    received_at  TEXT NOT NULL,   -- ISO 8601, UTC. 저장소에 들어온 시각
    dedup_key    TEXT UNIQUE,     -- NULL 허용. NULL끼리는 충돌하지 않는다.
    payload      TEXT NOT NULL    -- 받은 JSON 원문
);
CREATE INDEX raw_events_session ON raw_events (session_id, id);
CREATE INDEX raw_events_prompt ON raw_events (prompt_id);
CREATE INDEX raw_events_tool_use ON raw_events (tool_use_id);
```

- 스키마 버전은 `PRAGMA user_version`으로 관리하며 현재 버전은 1이다. 저장소를 열 때 버전이 0이면 위 스키마를 만들고 1로 설정한다. 알 수 없는 더 높은 버전이면 오류를 낸다.
- `PRAGMA journal_mode = WAL`을 설정한다. 서버가 쓰는 동안 다른 프로세스(CLI 등)가 읽을 수 있게 하기 위해서다.
- `payload`는 받은 JSON을 다시 직렬화하지 않고 원문 문자열 그대로 저장한다. 원시 이벤트는 변경하지 않는다는 [설계 원칙](../Architecture.md#2-설계-원칙)을 따른다.

## 3. 자료형

`RawEvent`는 원시 이벤트 하나를 나타내는 불변 dataclass다.

| 필드 | 타입 | 비고 |
| --- | --- | --- |
| `source` | `str` | `"hook"` 또는 `"transcript"` |
| `kind` | `str` | |
| `session_id` | `str \| None` | |
| `prompt_id` | `str \| None` | |
| `tool_use_id` | `str \| None` | |
| `occurred_at` | `datetime` | 시간대 정보 필수 |
| `payload` | `str` | JSON 원문 |
| `dedup_key` | `str \| None` | 기본값 `None` |
| `id` | `int \| None` | 저장 전 `None`, 조회 결과에는 값이 있다. |
| `received_at` | `datetime \| None` | 저장 전 `None`, 조회 결과에는 값이 있다. |

## 4. 저장소 API

`EventStore` 클래스가 데이터베이스 연결 하나를 감싼다.

| 심볼 | 동작 |
| --- | --- |
| `EventStore(path: Path)` | 부모 디렉터리를 만들고 연결을 연 뒤 스키마를 준비한다. 여러 스레드에서 쓸 수 있게 연결을 공유하고 쓰기는 잠금으로 직렬화한다. |
| `EventStore.append(event: RawEvent) -> int \| None` | 이벤트를 저장하고 `id`를 돌려준다. `received_at`은 저장 시각으로 채운다. `dedup_key`가 이미 있으면 저장하지 않고 `None`을 돌려준다. |
| `EventStore.events(session_id: str \| None = None, after_id: int = 0) -> list[RawEvent]` | `id`가 `after_id`보다 큰 이벤트를 `id` 순서로 돌려준다. `session_id`를 주면 그 세션만 돌려준다. |
| `EventStore.close() -> None` | 연결을 닫는다. |

`EventStore`는 컨텍스트 관리자(`with`)로도 쓸 수 있으며, 블록을 나갈 때 `close()`를 호출한다.

## 5. 테스트

`tests/test_store.py`에서 임시 디렉터리의 데이터베이스로 다음을 확인한다.

- 저장한 이벤트를 같은 값으로 다시 읽는다(`payload` 원문 보존, 시각의 시간대 보존).
- `dedup_key`가 같은 이벤트는 두 번째 저장에서 `None`을 돌려주고 저장되지 않는다. `dedup_key`가 `None`인 이벤트는 여러 개 저장된다.
- `session_id`, `after_id` 조건으로 조회한다.
- 스키마 버전이 더 높은 데이터베이스를 열면 오류가 난다.
- `AGENTVIS_HOME`을 설정하면 `data_dir()`이 그 경로를 돌려준다.
