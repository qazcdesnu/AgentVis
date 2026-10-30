# 분석기 설계

이 문서는 원시 이벤트로 프로젝트·세션·턴·단계·도구 호출을 구성하는 분석기(`src/agentvis/analysis/`)와, 그 결과를 내보내는 조회 API를 설계한다. 파생 모델의 개요는 [시스템 구조](../Architecture.md#42-파생-모델)에, 원천 데이터의 구조는 [데이터 소스](../DataSource.md)에, 무엇을 보여 줘야 하는지는 [제품 비전](../ProductVision.md#2-핵심-분석-질문)에 있다. 관련 태스크는 [로드맵](../Roadmap.md#m3-분석기와-확정-신호)의 M3-T2, M3-T4, M3-T5다. 신호 판정(M3-T3, M5)은 이 문서의 모델 위에 따로 설계한다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

구현할 심볼은 인라인 코드로 적었다. 태스크를 시작할 때 [작업 관리 규칙](../TaskRule.md#41-시작)에 따라 코드 포인터 링크로 바꾼다.

## 1. 계산 방식

- 파생 모델은 저장하지 않고 **요청할 때마다 원시 이벤트로 계산한다.** 원시 이벤트는 변경하지 않고 파생 모델은 언제든 다시 계산할 수 있어야 한다는 [설계 원칙](../Architecture.md#2-설계-원칙)을 가장 단순하게 지키는 방법이다. 규칙을 바꾸면 다음 요청부터 바로 반영되고, 스키마 이동도 필요 없다.
- 세션 하나의 원시 이벤트는 수천 개 수준이다(2026-10-31 이 세션: 약 1,500개). 한 세션의 계산은 메모리에서 충분히 빠르다. 느려지면 그때 세션 단위 캐시를 설계한다.
- 계산은 순수 함수로 만든다. `build_session(events: list[RawEvent]) -> SessionView`처럼 원시 이벤트 목록을 받아 결과를 돌려주며, 이벤트 저장소에 접근하지 않는다. 테스트는 원시 이벤트 목록만으로 한다.

## 2. 프로젝트

- 세션의 **프로젝트 경로**는 그 세션의 세션 기록 중 서브에이전트 기록이 아닌 첫 기록의 `cwd`다([데이터 소스의 실측 동작](../DataSource.md#25-실측으로-확인한-동작)). 세션 기록이 아직 없으면 그 세션의 첫 hook 이벤트 `cwd`를 쓰고, 추정했다는 표시(`project_from_hook`)를 단다.
- 프로젝트는 같은 프로젝트 경로를 가진 세션들의 묶음이다.

| 필드 | 값 |
| --- | --- |
| `path` | 프로젝트 경로 |
| `name` | 경로의 마지막 폴더 이름 |
| `parent` | 상위 경로(홈 디렉터리는 `~`로 줄임) |
| `session_count` | 세션 수 |
| `last_activity` | 세션들의 마지막 이벤트 시각 중 가장 늦은 것 |
| `exists` | 그 폴더가 지금 있는지 |

`list_projects(store) -> list[ProjectView]`가 마지막 활동이 늦은 것부터 돌려준다.

## 3. 턴

턴은 사람이 입력한 지시 하나와 그것을 수행한 과정이다.

**턴의 시작**: `user` 세션 기록 중 `origin.kind`가 `human`이고 내용이 도구 결과가 아닌 기록. 그 기록의 `promptId`가 턴 ID다. 2026-10-31 실측: 이 세션의 사람 입력 43개가 모두 이 조건으로 구분되었다(`promptSource`는 `typed` 또는 `suggestion_accepted`).

**턴에 속하는 기록**

| 기록 | 귀속 방법 |
| --- | --- |
| `promptId`가 있는 기록(사람 입력, 도구 결과) | 그 `promptId`의 턴. 실측: 도구 결과 325개 모두 그 턴 시작 기록과 같은 `promptId`였다. |
| `promptId`가 없는 기록(`assistant`, `system`, `attachment`) | `parentUuid`를 따라 올라가 처음 만나는 턴 귀속 기록의 턴 |
| hook 이벤트 | `prompt_id`의 턴. 없으면(`SessionEnd` 등) 시각상 직전 턴 |
| 하위 에이전트 보고·백그라운드 작업 알림(`origin.kind`가 `peer`, `isMeta`) | 새 턴을 만들지 않고 귀속 방법대로 기존 턴에 단계로 넣는다 |

턴 시작 전에 있는 기록은 세션 머리 단계로 따로 모은다.

| 턴 필드 | 값 |
| --- | --- |
| `prompt_id`, `index` | 턴 ID, 세션 안의 순번(1부터) |
| `prompt` | 사람이 입력한 지시 원문 |
| `started_at`, `ended_at` | 시작 기록 시각, `Stop` hook 시각(없으면 마지막 단계 시각) |
| `state` | `running`(`Stop`이 아직 없고 세션이 끝나지 않음), `ended`, `failed`(`StopFailure`) |
| `steps` | 단계 목록(4절), 시각 순 |
| `tool_call_count`, `failure_count` | 도구 호출 수, 상태가 `error`·`interrupted`인 도구 호출 수 |

## 4. 단계

단계는 턴 안의 시간순 항목이다. 세션 기록의 `assistant` 기록은 모두 내용 블록이 하나이므로([기록 리더 설계](Transcript.md#3-기록-변환)) 기록 하나가 단계 하나다.

| `kind` | 원천 | 주요 필드 |
| --- | --- | --- |
| `thinking` | `assistant`의 `thinking` 블록 | `text` |
| `text` | `assistant`의 `text` 블록 | `text` |
| `tool_call` | `assistant`의 `tool_use` 블록, 같은 `tool_use_id`의 도구 결과·hook 이벤트 | 5절 |
| `user_message` | 작업 도중 사람이 보낸 메시지가 모델에게 전달된 기록(`attachment.type` = `queued_command`, `origin.kind` = `human`) | `text` |
| `notification` | 하위 에이전트 보고, 백그라운드 작업 알림(`queued_command`의 다른 출처, `peer` 기록) | `text`, `source` |
| `compact` | `system`의 `compact_boundary`, `PreCompact`·`PostCompact` hook | `trigger` |
| `hook_failure` | hook 전달 실패(`attachment.type` = `hook_non_blocking_error`). 수집이 빠진 구간을 보여 준다. | `hook_event`, `message` |

- 모든 단계는 `id`(원시 이벤트 `id`), `at`(발생 시각), `source`(`transcript`/`hook`)를 가진다.
- `user_message`, `notification`, `hook_failure`는 첨부 기록이 저장되어야 나온다(I18, M3-T2에서 저장 대상 확장).
- `turn_duration` 같은 나머지 `system` 기록은 단계로 만들지 않고 턴 정보에만 쓴다.

## 5. 도구 호출

같은 `tool_use_id`를 가진 원시 이벤트를 하나로 합친다. 내용은 세션 기록을 우선하고, hook에만 있는 필드를 보탠다([병합 규칙](../Architecture.md#42-파생-모델)).

| 필드 | 값 |
| --- | --- |
| `tool_use_id`, `tool_name`, `input` | `tool_use` 블록(없으면 `PreToolUse`) |
| `status` | 아래 표 |
| `result` | 도구 결과 내용(앞부분만, 길이 제한은 M3-T2에서 정함) |
| `error` | 실패 메시지(도구 결과 또는 `PostToolUseFailure.error`) |
| `duration_ms` | `PostToolUse`·`PostToolUseFailure`의 `duration_ms` |
| `permission_requested` | 같은 턴에서 직전 `PermissionRequest`(같은 `tool_name`, `tool_input`)가 있었는지 |
| `subagent` | 이 호출이 서브에이전트를 띄웠으면 그 서브에이전트의 단계 목록(6절) |

**상태**는 확인된 사실만으로 정한다. 의미 해석이 필요한 판정(권한 거부 확정, 반복 실패, fallback)은 신호 설계(M3-T3, M5, I16)에서 한다.

| `status` | 조건 |
| --- | --- |
| `success` | 도구 결과가 있고 오류 표시(`is_error`)가 없음 |
| `error` | 도구 결과의 `is_error`가 참, 또는 `PostToolUseFailure`(중단 아님) |
| `interrupted` | `PostToolUseFailure.is_interrupt`가 참, `toolUseResult.interrupted`가 참, 또는 결과에 `[Request interrupted by user` 문구 |
| `running` | 결과가 없고 턴이 아직 `running` |
| `unfinished` | 결과가 없는데 턴이 끝남. 권한 거부나 중단의 후보다([실측 동작](../DataSource.md#25-실측으로-확인한-동작)). |

세션 기록은 실행 중인 도구 호출 하나만큼 늦으므로([두 소스 비교](../DataSource.md#4-두-소스-비교)), 지금 실행 중인 도구는 `PreToolUse` hook만으로 `running` 단계로 나타난다.

## 6. 서브에이전트

- 서브에이전트 기록(`isSidechain`이 참, `agentId`)은 같은 턴 구성 규칙으로 단계를 만들되, 부모 세션의 턴에 직접 넣지 않고 그 서브에이전트를 띄운 도구 호출의 `subagent`에 넣는다.
- 연결은 서브에이전트 메타(`subagent-meta`)의 `toolUseId`로 한다. 메타가 없으면 hook의 `SubagentStart`와 같은 턴의 `Agent` 도구 호출을 시각 순서로 짝짓고, 그래도 연결되지 않은 서브에이전트는 턴 끝에 따로 둔다.
- 문맥 압축의 요약 서브에이전트(`agent_type`이 빈 `SubagentStop`)는 `compact` 단계에 붙이고 사용자 작업으로 세지 않는다.

## 7. 세션

| 필드 | 값 |
| --- | --- |
| `session_id`, `project` | 세션 ID, 프로젝트 경로(2절) |
| `title` | 첫 턴의 지시 첫 줄(최대 80자) |
| `started_at`, `last_activity` | 첫·마지막 이벤트 시각 |
| `ended` | `SessionEnd` hook을 받았는지 |
| `turn_count`, `tool_call_count`, `failure_count` | 턴들의 합 |
| `turns` | 턴 목록(상세 조회에서만) |

## 8. 조회 API

| 경로 | 응답 | 태스크 |
| --- | --- | --- |
| `GET /api/projects` | 프로젝트 목록(2절 필드) | M3-T5 |
| `GET /api/sessions?project=<프로젝트 경로>` | 그 프로젝트의 세션 목록(7절 필드, `turns` 제외). 마지막 활동이 늦은 것부터 | M3-T4 |
| `GET /api/sessions/{session_id}` | 세션 상세(7절 필드와 `turns`) | M3-T4 |

- 응답은 JSON이며 필드 이름은 이 문서의 이름(`snake_case`)을 쓴다. 시각은 ISO 8601(UTC)이다.
- 모든 경로는 [요청 검증](Collector.md#21-요청-검증)의 `Host` 검사를 받는다.
- 없는 세션은 `404`다.

## 9. 테스트

`tests/test_analysis.py`에서 실측 형태의 원시 이벤트 목록으로 확인한다.

- 사람 입력만 턴을 시작하고, 하위 에이전트 보고·작업 알림·메타 기록은 턴을 만들지 않는다.
- `promptId`가 없는 기록이 `parentUuid`를 따라 올바른 턴에 들어간다.
- 도구 호출이 세션 기록과 hook 이벤트에서 하나로 합쳐지고, 상태 표의 각 경우가 구분된다. 세션 기록이 아직 없는 실행 중 도구는 hook만으로 `running`이 된다.
- 작업 중 사람 메시지·작업 알림·hook 전달 실패가 각 단계 종류로 나온다.
- 서브에이전트 단계가 띄운 도구 호출 아래에 들어간다.
- 프로젝트 경로는 세션 기록의 첫 `cwd`이며, 하위 폴더 `cwd`를 가진 hook 이벤트에 끌려가지 않는다.
- 조회 API가 필드와 정렬, `404`를 지킨다.
