# 데이터 소스

이 문서는 AgentVis가 분석하는 원천 데이터인 Claude Code hook 이벤트와 세션 기록의 위치, 구조, 한계를 정리한다. 이 데이터로 무엇을 판정하는지는 [제품 비전](ProductVision.md#3-진단-신호)에, 데이터를 받아 처리하는 구조는 [시스템 구조](Architecture.md)에 있다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## 1. 개요

| 소스 | 시점 | 역할 |
| --- | --- | --- |
| hook 이벤트 | 실시간(Claude Code가 보냄) | 신호. "방금 이 세션에 무슨 일이 있었다"와 그 세션 기록 파일 경로(`transcript_path`)를 알려 준다. hook에만 있는 정보를 더하고, 세션 기록 읽기가 실패할 때의 안전망이 된다. |
| 세션 기록 (JSONL) | 실시간(작업하는 동안 계속 쓰임) | 주 내용. 사고 과정, 응답, 도구 호출과 결과, 작업 중 사용자 메시지, 권한 판정, 대화 구조가 있다. hook 이벤트가 올 때마다 이어 읽고, 서버가 꺼져 있던 동안의 작업과 지난 세션도 여기서 읽는다. |

두 소스에 각각 무엇이 있는지는 [4. 두 소스 비교](#4-두-소스-비교)에 있다.

두 소스는 아래 키로 결합한다. 2026-10-31에 Claude Code 2.1.314에서 실측으로 일치를 확인했다.

| 결합 키 | hook 이벤트 필드 | 세션 기록 필드 |
| --- | --- | --- |
| 세션 | `session_id` | `sessionId` |
| 턴(사용자 지시 하나) | `prompt_id` | `user` 기록의 `promptId` |
| 도구 호출 | `tool_use_id` | `tool_use.id`, `tool_result.tool_use_id` |
| 세션 기록 파일 | `transcript_path` | (파일 경로 자체) |

## 2. hook 이벤트

Claude Code는 작업 중 정해진 시점에 hook을 실행하고, 이벤트 내용을 JSON으로 넘긴다. 공식 규격은 Claude Code hooks 참조 문서(https://code.claude.com/docs/en/hooks)에 있다.

### 2.1 전달 방식

- hook 종류 중 `http`는 이벤트 JSON을 지정한 URL로 POST한다(`Content-Type: application/json`). 본문은 `command` hook이 stdin으로 받는 JSON과 같다. (실측 확인)
- 받는 쪽 서버가 꺼져 있어도 Claude Code 작업은 계속 진행된다. (실측 확인: 연결이 거부되는 주소로 보낸 `PreToolUse` hook이 도구 실행을 막지 않았다.)
- 요청 헤더는 `Host: 127.0.0.1:<포트>`, `Content-Type: application/json`이며 `Origin`은 없다(클라이언트 `axios`). (H2 실측)
- `http` hook은 응답을 기다리는 동안 에이전트를 멈춘다. 따라서 받는 쪽은 즉시 응답해야 하며, hook 설정에 짧은 `timeout`을 둔다.

### 2.2 공통 필드

`session_id`, `transcript_path`, `cwd`, `hook_event_name`, `permission_mode`, `prompt_id`(턴 안의 이벤트), `effort`. 서브에이전트 안에서 발생한 이벤트에는 `agent_id`, `agent_type`이 붙는다.

### 2.3 사용하는 이벤트

| 이벤트 | 시점 | 주요 필드 | 확인 |
| --- | --- | --- | --- |
| `UserPromptSubmit` | 사용자 지시 제출 | `prompt`, `prompt_id` | 실측 |
| `PreToolUse` | 도구 실행 직전 | `tool_name`, `tool_input`, `tool_use_id` | 실측 |
| `PostToolUse` | 도구 성공 | `tool_response`, `tool_use_id`, `duration_ms` | 실측 |
| `PostToolUseFailure` | 도구 실패 (Bash의 0이 아닌 종료 코드 포함) | `error`(표시용 문자열), `is_interrupt`, `tool_use_id`, `duration_ms` | 실측 |
| `PermissionRequest` | 권한 확인이 필요한 도구 호출. 비대화 모드(`-p`)에서도 발생한다. | `tool_name`, `tool_input`, `permission_suggestions` (`tool_use_id` 없음) | 실측 |
| `PermissionDenied` | auto 모드에서 권한 거부 | `tool_name`, `tool_use_id`, `reason` | 미확인 |
| `Notification` | 알림 | `message`, `notification_type` | 미확인 |
| `SubagentStart` / `SubagentStop` | 서브에이전트 시작·종료 | `agent_id`, `agent_type`, `agent_transcript_path`·`last_assistant_message`(종료 시) | 실측 |
| `Stop` | 턴 종료 | `last_assistant_message` | 실측 |
| `StopFailure` | API 오류로 턴 실패 | `error`(예: `model_not_found`), `last_assistant_message`, `error_details`(있을 때만) | 실측 |
| `PreCompact` / `PostCompact` | 문맥 압축 | `trigger` (`manual`, `auto`), `custom_instructions`(시작 시), `compact_summary`(종료 시) | 실측 |
| `SessionEnd` | 세션 종료 | `reason` (비대화 모드에서는 `other`) | 실측 |

- "실측"은 직접 받아 확인한 것이다. M0-T4(command hook, 2026-10-31)와 M1-T6(AgentVis 수집기와 `http` hook, 2026-10-31, Claude Code 2.1.314)에서 확인했다.
- "미확인"은 공식 문서에만 근거한 것이다. `PermissionDenied`는 auto 모드가 위험하다고 판정한 명령에서만 생기므로 일부러 일으키지 않았다. `Notification`은 대화형 화면의 알림이라 비대화 모드에서 일으킬 수 없었다. 실제 세션에서 수집되면 이 표를 고친다.
- `SessionStart`는 `http` hook을 지원하지 않으므로(공식 문서: "Only `type: "command"` and `type: "mcp_tool"` hooks are supported") 사용하지 않는다. M1-T6에서 `http` hook으로 세 세션을 실행해 한 번도 오지 않음을 확인했다. M0-T4에서는 command hook으로 받았다(`source`: `startup`, `resume`, `clear`, `compact`, `fork`).
- `PostToolBatch`(위 도구 이벤트와 중복)와 `MessageDisplay`(화면 표시용 스트리밍 조각)는 사용하지 않는다.

### 2.4 hook으로 얻을 수 없는 정보

| 정보 | 상태 | 보완 방법 |
| --- | --- | --- |
| 세션 시작과 시작 종류(`SessionStart`) | `http` hook 미지원 | 시작 시각은 세션의 첫 이벤트로, 시작 종류(재개, 압축 후 등)는 세션 기록으로 판정 |
| 모델의 사고 과정(thinking)과 중간 응답 텍스트 | 이벤트 없음 | 세션 기록의 `assistant` 기록 |
| 작업 도중 들어온 사용자 메시지 | 이벤트로 문서화되어 있지 않음 | 세션 기록의 `queue-operation` |
| auto 모드가 아닐 때 사용자의 권한 거부 | 거부 이벤트 없음 | 아래 [실측으로 확인한 동작](#25-실측으로-확인한-동작)의 "완료 이벤트 없는 `PreToolUse`", 세션 기록의 `permissionDecision`과 도구 결과 |
| 텍스트 생성 중 사용자 중단(Esc) | 이벤트 없음 (도구 실행 중 중단만 `is_interrupt`로 옴) | 세션 기록 |
| AgentVis 서버가 꺼져 있던 동안의 이벤트 | 유실 | 세션 기록 |

### 2.5 실측으로 확인한 동작

M1-T6에서 확인한, 분석에 영향을 주는 동작이다.

- **권한이 없어 막힌 도구 호출**: `PreToolUse` → `PermissionRequest` 다음에 `PostToolUse`도 `PostToolUseFailure`도 오지 않는다. 따라서 완료 이벤트가 없는 `PreToolUse`는 권한 거부나 중단의 후보다. `PermissionRequest`에는 `tool_use_id`가 없으므로 같은 턴의 직전 `PreToolUse`(같은 `tool_name`, `tool_input`)와 짝짓는다.
- **서브에이전트 안의 이벤트**: 서브에이전트가 실행한 도구 이벤트에도 `agent_id`, `agent_type`이 붙는다. 서브에이전트를 띄운 도구(`Agent`) 호출은 `agent_id` 없이 `PreToolUse`·`PostToolUse`로 오고, 그 사이에 `SubagentStart`·서브에이전트의 이벤트·`SubagentStop`이 온다.
- **이벤트의 `cwd`는 그 시점의 작업 위치다**: 프로젝트의 하위 폴더일 수 있다. M1-T7에서 `…/RecommandShopping`에서 시작한 세션의 이벤트가 `…/RecommandShopping/backend`를 `cwd`로 가지고 왔다. AgentVis를 설치하기 전에 시작된 세션은 받은 첫 이벤트부터 하위 폴더일 수 있으므로, 세션의 프로젝트 경로는 hook 이벤트가 아니라 `transcript_path`가 가리키는 세션 기록의 첫 `cwd`로 정한다.
- **문맥 압축의 요약 서브에이전트**: `/compact`는 요약을 서브에이전트로 실행하며, `SubagentStart` 없이 `agent_type`이 빈 문자열인 `SubagentStop`만 `PreCompact`와 `PostCompact` 사이에 온다. 사용자 작업의 서브에이전트와 구분해야 한다.

## 3. 세션 기록 (JSONL)

### 3.1 위치

- Claude Code는 세션 하나를 JSONL 파일 하나로 저장한다: `~/.claude/projects/<프로젝트 경로>/<세션 ID>.jsonl`. hook 이벤트의 `transcript_path`가 이 파일을 가리킨다.
- `<프로젝트 경로>`는 작업 디렉터리의 절대 경로에서 영문자·숫자가 아닌 문자를 `-`로 바꾼 문자열이다. 예: `/Users/me/app` → `-Users-me-app`
- 이 변환은 정보를 잃는다. 한글 같은 문자는 사라지고(`…/course/AI윤리` → `…-course-AI--`), 원래 경로의 `-`와 경로 구분자 `/`가 구분되지 않는다(`2026-2/course` → `2026-2-course`). 따라서 디렉터리 이름으로 원래 경로를 되돌리지 않는다. 원래 경로는 기록의 `cwd` 필드에서 읽는다. 2026-10-31에 실제 디렉터리 다섯 개에서 `cwd`가 원래 경로와 정확히 일치함을 확인했다.
- 파일의 한 줄이 기록(record) 하나이며, 각 기록은 `type` 필드를 가진 JSON 객체다. 파일은 세션이 진행되는 동안 뒤에 계속 덧붙는다.
- 서브에이전트의 기록은 부모 세션 파일과 따로 `<세션 ID>/subagents/agent-<agent_id>.jsonl`에 저장된다. `<agent_id>`는 hook 이벤트의 `agent_id`와 같다. 각 기록에는 `isSidechain: true`, `agentId`, 부모의 `sessionId`·`promptId`가 있다. 옆의 `agent-<agent_id>.meta.json`에는 `agentType`, `description`, 서브에이전트를 띄운 도구 호출 ID(`toolUseId`), 중첩 깊이(`spawnDepth`), `finished`가 있다. 문맥 압축의 요약 서브에이전트는 기록 파일이 생기지 않았다. (M1-T6 실측)

### 3.2 주의 사항

- 이 형식은 Anthropic이 공개 규격으로 문서화한 것이 아니다. 아래 내용은 2026-10-31에 실제 기록 파일을 관찰해 정리한 것이며, Claude Code 버전에 따라 바뀔 수 있다.
- 따라서 파서는 모르는 `type`이나 필드를 만나도 실패하지 않고 건너뛰어야 한다. 각 기록의 `version` 필드(Claude Code 버전)를 보존해 형식 변화를 추적할 수 있게 한다.
- 기록에는 사용자의 프롬프트, 파일 내용, 명령 출력이 그대로 들어 있다. 외부로 전송하지 않는다.

### 3.3 관찰된 기록 유형

| `type` | 내용 | 분석에서의 쓰임 |
| --- | --- | --- |
| `user` | 사용자 메시지, 또는 도구 실행 결과(`tool_result` 블록) | 지시(턴)의 시작, 도구 결과와 오류 |
| `assistant` | 모델 응답. `text`, `thinking`, `tool_use` 블록 | 에이전트의 판단과 도구 호출 |
| `system` | 시스템 이벤트. `subtype`으로 구분 (`turn_duration`, `compact_boundary`, `stop_hook_summary` 등) | 턴 경계, 문맥 압축 시점 |
| `queue-operation` | 에이전트가 작업하는 도중 들어온 사용자 메시지의 대기열 처리 (`enqueue`, `dequeue`, `remove`) | 작업 중 정정 신호 |
| `attachment` | 대화에 덧붙은 부가 문맥 | 보조 정보 |
| `file-history-snapshot`, `file-history-delta` | 파일 변경 추적 | 어떤 파일이 바뀌었는지 |
| 그 밖의 유형 | `api-request`, `mode`, `permission-mode`, `ai-title`, `last-prompt` 등 | 현재는 사용하지 않음 |

### 3.4 주요 필드

| 필드 | 위치 | 의미 |
| --- | --- | --- |
| `uuid`, `parentUuid` | `user`, `assistant`, `system`, `attachment` | 기록 간 부모-자식 관계. 대화 흐름을 트리로 복원한다. |
| `timestamp` | 대부분의 기록 | 시각 (ISO 8601) |
| `sessionId` | 모든 기록 | 세션 식별자 |
| `promptId` | `user` | 턴 식별자. hook의 `prompt_id`와 같다. |
| `isSidechain` | `user`, `assistant` 등 | 서브에이전트 등 본 흐름 밖의 기록인지 |
| `message.content[]` | `user`, `assistant` | 내용 블록 목록 (`text`, `thinking`, `tool_use`, `tool_result`) |
| `tool_use.id`, `tool_result.tool_use_id` | 내용 블록 | 도구 호출과 그 결과를 짝짓는다. hook의 `tool_use_id`와 같다. |
| `tool_result.is_error` | 내용 블록 | 도구 실패 여부 |
| `toolUseResult` | `user` | 도구 실행 결과의 구조화된 상세 |
| `permissionDecision` | `user` | 도구 실행에 대한 권한 판정 |
| `cwd`, `gitBranch`, `version` | 대부분의 기록 | 작업 디렉터리(절대 경로), 브랜치, Claude Code 버전. 세션 기록의 첫 `cwd`가 그 세션의 프로젝트 경로다. |

## 4. 두 소스 비교

2026-10-31에 로컬 세션 기록(세션 5개, 서브에이전트 기록 3개)과 hook 실측(M0-T4, M1-T6, H2)으로 확인했다. 이 비교에 따라 세션 기록을 주 내용 출처로, hook을 신호로 쓴다(I17).

**세션 기록에만 있는 것**

| 정보 | 세션 기록의 위치 |
| --- | --- |
| 모델의 사고 과정, 중간 응답 텍스트 | `assistant` 기록의 `thinking`, `text` 블록 |
| 작업 도중 들어온 사용자 메시지 | `queue-operation` |
| 권한 판정, 사용자 중단 | `user` 기록의 `permissionDecision`, `[Request interrupted by user` 문구 |
| 기록 간 부모-자식 관계 | `uuid`, `parentUuid` |
| 모델, 토큰 사용량, 응답 종료 사유 | `assistant` 기록의 `message.model`, `message.usage`, `message.stop_reason` |
| 턴 소요 시간, 문맥 압축 지점 | `system` 기록의 `turn_duration`(`durationMs`), `compact_boundary` |
| 구조화된 도구 결과 | `user` 기록의 `toolUseResult`(Bash의 `stdout`·`stderr`·`interrupted`, 파일 편집의 `structuredPatch` 등) |
| hook을 설치하기 전이나 서버가 꺼져 있던 동안의 작업 | 파일 전체 |

**hook에만 있는 것**

| 정보 | hook 이벤트 | 비고 |
| --- | --- | --- |
| 권한 확인 요청과 제안된 권한 옵션 | `PermissionRequest` | 세션 기록에는 판정 결과만 있다. |
| 도구별 실행 시간 | `PostToolUse`·`PostToolUseFailure`의 `duration_ms` | 세션 기록에서는 기록 시각의 차이로만 추정할 수 있다. |
| 서브에이전트 시작·종료 시점, 세션 종료 사유, 알림 | `SubagentStart`·`SubagentStop`, `SessionEnd`, `Notification` | 서브에이전트의 기록 자체는 별도 파일로 있다. |
| API 오류로 인한 턴 실패 코드 | `StopFailure`의 `error` | 세션 기록에 남는지는 확인하지 못했다. |

**그 밖의 차이**

- hook은 공식 문서로 정해진 규격이고, 세션 기록은 공개 규격이 아니라 버전에 따라 바뀔 수 있다([주의 사항](#32-주의-사항)).
- hook은 일이 생기면 먼저 알려 주고, 세션 기록은 직접 읽으러 가야 한다. 세션 기록도 작업하는 동안 계속 쓰이므로, hook을 읽을 때를 알리는 신호로 쓰면 둘의 장점을 함께 얻는다.
- 세션 기록은 실행 중인 도구 호출 하나만큼 늦다. 도구 호출 기록(`tool_use`)의 `timestamp`는 호출 시각이지만, 파일에는 그 호출의 결과가 나온 뒤에 결과 기록과 함께 쓰인다. (2026-10-31 실측: 실행 중인 호출은 파일에 없고, 바로 앞 호출은 호출·결과 기록이 모두 있었다.) 따라서 "지금 실행 중인 도구"는 hook의 `PreToolUse`로만 바로 알 수 있다. 오래 걸리는 명령이나 서브에이전트 작업이 이에 해당한다.

