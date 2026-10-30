# 수집기 설계

이 문서는 Claude Code의 hook 이벤트를 받아 이벤트 저장소에 넣는 수집기([collector 모듈](../../src/agentvis/collector.py))와 이를 노출하는 웹 서버 앱([server 모듈](../../src/agentvis/server.py))의 M1 범위를 설계한다. 받는 이벤트의 형식은 [hook 이벤트](../DataSource.md#2-hook-이벤트)에, 저장 방식은 [이벤트 저장소 설계](Store.md)에 있다. 관련 태스크는 [로드맵](../Roadmap.md#m1-수집-기반)의 M1-T3이다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

구현 심볼은 M1-T3을 시작하면서 [작업 관리 규칙](../TaskRule.md#41-시작)에 따라 코드 포인터 링크로 바꿨다.

## 1. 이벤트 변환

[hook_event_to_raw](../../src/agentvis/collector.py#hook_event_to_raw)`(body: bytes, received_at: datetime) -> RawEvent`는 POST 본문을 원시 이벤트로 바꾸는 순수 함수다.

| 원시 이벤트 필드 | 값 |
| --- | --- |
| `source` | `"hook"` |
| `kind` | 본문의 `hook_event_name` |
| `session_id` | 본문의 `session_id` |
| `prompt_id` | 본문의 `prompt_id` (없으면 `None`) |
| `tool_use_id` | 본문의 `tool_use_id` (없으면 `None`) |
| `cwd` | 본문의 `cwd` (없으면 `None`) |
| `occurred_at` | `received_at`. hook 본문에는 발생 시각이 없으므로 받은 시각을 쓴다. |
| `payload` | 본문 원문을 UTF-8로 디코딩한 문자열 |
| `dedup_key` | `None` |

다음 경우에는 [InvalidHookEvent](../../src/agentvis/collector.py#InvalidHookEvent) 예외를 낸다. 예외 메시지는 사유를 담는다.

- 본문이 UTF-8 JSON 객체가 아니다.
- `hook_event_name` 또는 `session_id`가 없거나 문자열이 아니다.

`prompt_id`, `tool_use_id`, `cwd`가 문자열이 아닌 값이면 `None`으로 둔다. 모르는 이벤트 이름도 그대로 저장한다. 형식이 바뀌어도 데이터를 버리지 않기 위해서다([데이터 소스 주의 사항](../DataSource.md#32-주의-사항)).

## 2. HTTP 엔드포인트

[create_app](../../src/agentvis/server.py#create_app)`(store: EventStore) -> FastAPI`가 앱을 만든다. M1에서 제공하는 경로는 다음과 같다.

| 경로 | 동작 | 응답 |
| --- | --- | --- |
| `POST /hooks` | 본문을 `hook_event_to_raw`로 바꿔 저장한다. 쿼리 문자열(`client=agentvis`)은 무시한다. | 성공: `200`, 본문 `{}`. 변환 실패: `400`, 본문 `{"error": "<InvalidHookEvent 메시지>"}`. |
| `GET /health` | 서버 동작 확인 | `200`, 본문 `{"status": "ok"}` |

- 요청은 [2.1 요청 검증](#21-요청-검증)을 통과해야 처리한다.
- 응답 본문 `{}`에는 어떤 필드도 넣지 않는다. Claude Code는 hook 응답 JSON의 필드(`decision`, `continue` 등)로 에이전트 동작을 바꾸므로, 수집기가 에이전트 동작에 영향을 주지 않도록 하기 위해서다.
- 저장 이외의 처리(분석, 알림)는 M1에서 하지 않는다. M3 이후에도 응답을 보낸 뒤에 처리한다([설계 원칙](../Architecture.md#2-설계-원칙)).
- `POST /hooks` 처리 함수는 비동기 함수(`async def`)로 작성하고 `await request.body()`로 본문 원문 바이트를 읽는다. `payload`에 원문을 그대로 남기려면 FastAPI가 본문을 해석하기 전의 바이트가 필요하기 때문이다. SQLite 저장은 `starlette.concurrency.run_in_threadpool`로 스레드 풀에서 실행해 이벤트 루프를 막지 않는다.

### 2.1 요청 검증

서버는 `127.0.0.1`에만 바인딩하지만, 그것만으로는 같은 컴퓨터의 브라우저에서 열린 웹페이지가 보내는 요청을 막지 못한다. `Content-Type: text/plain`인 POST는 브라우저가 사전 확인 없이 다른 출처로 보낼 수 있고, DNS 리바인딩을 쓰면 공격자 도메인이 `127.0.0.1`로 풀린다. 그래서 아래 순서로 요청을 검증하고, 하나라도 통과하지 못하면 저장하지 않는다.

| 순서 | 대상 | 조건 | 실패 응답 |
| --- | --- | --- | --- |
| 1 | 모든 경로 | `Host` 헤더의 호스트 이름이 [ALLOWED_HOSTS](../../src/agentvis/server.py#ALLOWED_HOSTS)(`127.0.0.1`, `localhost`) 중 하나다. DNS 리바인딩 요청은 `Host`가 공격자 도메인이다. | `400` (Starlette `TrustedHostMiddleware`) |
| 2 | `POST /hooks` | `Origin` 헤더가 없다. 브라우저는 다른 출처로 POST할 때 `Origin`을 붙이고, Claude Code는 붙이지 않는다. | `403`, `{"error": "<사유>"}` |
| 3 | `POST /hooks` | `Content-Type`의 미디어 타입이 `application/json`이다(`charset` 같은 매개변수는 허용). | `415`, `{"error": "<사유>"}` |

실측(H2, Claude Code 2.1.314): Claude Code의 `http` hook 요청은 `Host: 127.0.0.1:<포트>`, `Content-Type: application/json`이고 `Origin`이 없다(클라이언트 `axios`). 따라서 이 검증은 정상 hook을 막지 않는다.

## 3. 테스트

[tests/test_collector.py](../../tests/test_collector.py)에서 확인한다. 앱 테스트는 FastAPI의 `TestClient`와 임시 디렉터리의 이벤트 저장소를 쓴다.

- 실측한 `PostToolUseFailure` 본문이 올바른 원시 이벤트로 바뀐다(`kind`, 결합 키, `cwd`, `payload` 원문).
- `prompt_id`가 없는 `SessionEnd` 본문도 저장된다.
- JSON이 아니거나, JSON 객체가 아니거나, `hook_event_name`이 없는 본문은 `400`을 받고 저장되지 않는다.
- 문자열이 아닌 `prompt_id`·`tool_use_id`·`cwd`는 `None`이 되고, 모르는 이벤트 이름도 저장된다.
- 쿼리 문자열(`?client=agentvis`)이 붙은 요청도 같게 처리된다.
- `POST /hooks`의 성공 응답 본문은 정확히 `{}`다.
- `GET /health`가 `{"status": "ok"}`를 돌려준다.
- 요청 검증: `Host`가 허용 목록 밖이면 `400`, `Origin`이 있으면 `403`, `Content-Type`이 `text/plain`이거나 없으면 `415`를 받고, 어느 경우도 저장되지 않는다. `Host: localhost:<포트>`와 `Content-Type: application/json; charset=utf-8`은 통과한다. 앱 테스트의 `TestClient`는 `base_url="http://127.0.0.1:8765"`로 실제 hook과 같은 `Host`를 쓴다.
