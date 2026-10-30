# 기록 리더 설계

이 문서는 Claude Code 세션 기록(JSONL)을 이어 읽어 이벤트 저장소에 넣는 기록 리더([transcript 모듈](../../src/agentvis/transcript.py))를 설계한다. 세션 기록의 구조와 두 데이터 소스의 역할은 [데이터 소스](../DataSource.md#1-개요)에, 전체 구조에서의 위치는 [시스템 구조](../Architecture.md#31-기록-리더가-실행되는-시점)에, 저장 방식은 [이벤트 저장소 설계](Store.md)에 있다. 관련 태스크는 [로드맵](../Roadmap.md#m2-세션-기록-읽기)의 M2-T2~M2-T5다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

구현할 심볼은 인라인 코드로 적었다. 태스크를 시작할 때 [작업 관리 규칙](../TaskRule.md#41-시작)에 따라 코드 포인터 링크로 바꾼다. 1~3절과 5절은 M2-T2에서 바꿨다.

## 1. 읽는 파일

| 파일 | 경로 |
| --- | --- |
| 세션 기록 | `<기록 루트>/<프로젝트 경로>/<세션 ID>.jsonl` |
| 서브에이전트 기록 | `<기록 루트>/<프로젝트 경로>/<세션 ID>/subagents/agent-<agent_id>.jsonl` |
| 서브에이전트 메타 | 같은 위치의 `agent-<agent_id>.meta.json` |

- 기록 루트는 [default_projects_dir](../../src/agentvis/transcript.py#default_projects_dir)`()`(`~/.claude/projects`)다. 테스트와 가져오기 명령은 다른 경로를 넘길 수 있다.
- 기록 리더는 기록 루트 안의 파일만 읽는다. hook 이벤트의 `transcript_path`처럼 밖에서 받은 경로는 실제 경로로 바꾼 뒤 기록 루트 안인지 확인하고, 밖이면 읽지 않고 `ValueError`를 낸다. 받은 경로로 임의의 파일을 읽게 하지 않기 위해서다.
- [subagent_transcript_path](../../src/agentvis/transcript.py#subagent_transcript_path)`(transcript_path, agent_id)`는 세션 기록 경로와 `agent_id`로 서브에이전트 기록 경로를 만든다(`.jsonl`을 뗀 경로 + `/subagents/agent-<agent_id>.jsonl`). 2026-10-31 M1-T6 실측 구조를 따른다.

## 2. 이어 읽기

파일마다 마지막으로 읽은 위치(읽기 커서)를 이벤트 저장소에 둔다([이벤트 저장소 설계의 M2 변경](Store.md#6-m2-변경)).

1. 커서 위치부터 파일 끝까지 읽는다.
2. 마지막 줄바꿈까지만 처리한다. 줄바꿈으로 끝나지 않는 마지막 줄은 아직 쓰는 중일 수 있으므로 다음에 읽는다.
3. 줄마다 [3. 기록 변환](#3-기록-변환)을 거쳐 원시 이벤트로 바꾼다.
4. 바꾼 원시 이벤트들과 새 커서 위치를 **한 트랜잭션으로** 저장한다. 한 트랜잭션에는 최대 [BATCH_LINES](../../src/agentvis/transcript.py#BATCH_LINES)(500)줄을 담아 쓰기 잠금을 짧게 잡는다. 둘 중 하나만 저장되면 기록을 잃거나 다시 읽게 되기 때문이다. 다시 읽더라도 중복 제거 키 때문에 중복 저장되지는 않는다.

- 파일 식별자(장치·inode)가 커서에 저장된 것과 다르거나 파일 크기가 커서 위치보다 작으면, 파일이 바뀐 것으로 보고 처음부터 다시 읽는다.
- 서브에이전트 메타 파일은 JSONL이 아니므로 커서 없이 통째로 읽는다([read_subagent_meta](../../src/agentvis/transcript.py#read_subagent_meta)`(store, path, projects_dir) -> bool`, 새로 저장했으면 `True`).
- 아직 없는 파일은 읽을 것이 없는 것으로 보고, 아무것도 저장하지 않은 결과를 돌려준다. hook 이벤트가 세션 기록 파일보다 먼저 올 수 있기 때문이다.
- [read_new_records](../../src/agentvis/transcript.py#read_new_records)`(store, path, projects_dir) -> ReadResult`가 한 파일을 이어 읽는다. [ReadResult](../../src/agentvis/transcript.py#ReadResult)는 저장한 수, 건너뛴 줄 수(해석 실패, 대상이 아닌 유형, 시각 없음), 새 커서 위치를 가진다.

## 3. 기록 변환

[record_to_raw](../../src/agentvis/transcript.py#record_to_raw)`(line: bytes) -> RawEvent | None`는 세션 기록 한 줄을 원시 이벤트로 바꾸고, 저장 대상이 아니면 `None`을 돌려준다.

**저장 대상 유형** [INGESTED_TYPES](../../src/agentvis/transcript.py#INGESTED_TYPES): `user`, `assistant`, `system`, `queue-operation`, `attachment`. `attachment`는 [INGESTED_ATTACHMENTS](../../src/agentvis/transcript.py#INGESTED_ATTACHMENTS)의 `attachment.type`만 저장한다: 작업 중 메시지·작업 알림이 모델에게 전달된 기록 `queued_command`, hook 전달 실패 `hook_non_blocking_error`(I18). 그 밖의 유형(`api-request`, `api-request-blob`, `file-history-*`, `mode`, `ai-title` 등)과 나머지 첨부(도구 목록, 편집 파일 내용 등)는 분석 질문(Q1~Q6)과 관계없는 요청 사본·화면 상태·파일 이력이라 건너뛴다.

| 원시 이벤트 필드 | 값 |
| --- | --- |
| `source` | `"transcript"` |
| `kind` | 기록의 `type` |
| `session_id` | `sessionId` |
| `prompt_id` | `promptId` (`user` 기록에만 있다. 다른 기록은 `None`이며, 턴 귀속은 M3에서 `parentUuid`를 따라 한다) |
| `tool_use_id` | `assistant`의 `tool_use` 블록 `id`, `user`의 `tool_result` 블록 `tool_use_id`, `hook_non_blocking_error` 첨부의 `toolUseID`(`toolu_`로 시작할 때). 그 밖에는 `None` |
| `cwd` | `cwd` (없으면 `None`) |
| `occurred_at` | `timestamp`(ISO 8601, `Z`는 UTC). 없거나 해석할 수 없으면 그 줄을 건너뛴다. |
| `payload` | 줄 원문을 UTF-8로 디코딩한 문자열 |
| `dedup_key` | `uuid`가 있으면 `uuid:<uuid>`, 없으면(`queue-operation` 등) `sha256:<줄 원문 바이트의 SHA-256>` |

- 근거(2026-10-31 실측): `assistant` 기록은 모두 내용 블록을 하나만 가져(사고 과정·응답 텍스트·도구 호출이 각각 별도 기록) 기록 하나가 단계 하나에 대응한다. `promptId`는 `user` 기록에만 있다. `queue-operation`에는 `uuid`가 없다.
- 줄 원문 해시를 쓰는 이유: 파일 경로나 줄 번호는 프로젝트 폴더를 옮기거나 파일이 다시 쓰이면 바뀐다. 같은 내용의 줄이 두 번 나오면 시각까지 같은 같은 사건이므로 하나로 본다.
- 서브에이전트 기록도 같은 규칙으로 바꾼다. 서브에이전트임은 `payload`의 `isSidechain`, `agentId`로 알 수 있다.
- 서브에이전트 메타 파일은 `kind`가 `subagent-meta`인 원시 이벤트로 저장한다. `session_id`는 경로의 세션 ID, `occurred_at`은 파일 수정 시각, `payload`는 파일 내용, `dedup_key`는 `sha256:<내용의 SHA-256>`이다. 서브에이전트가 끝나 `finished`가 바뀌면 새 내용으로 한 번 더 저장된다.

## 4. 실행 시점

### 4.1 hook 이벤트를 받을 때 (M2-T3)

- 수집기는 hook 이벤트를 저장한 뒤 [paths_to_read](../../src/agentvis/transcript.py#paths_to_read)`(hook_event: dict) -> list[Path]`로 읽을 파일을 계산해 기록 리더의 대기열에 넣고 응답한다. 대기열에 넣는 일은 즉시 끝나며, 읽기는 작업 스레드가 응답과 따로 한다.
  - 이벤트의 `transcript_path`
  - 이벤트에 `agent_id`가 있으면 그 서브에이전트의 기록 파일과 메타 파일(`subagent_transcript_path`로 계산)
  - `SubagentStop`의 `agent_transcript_path`
  - 문자열이 아닌 값은 무시하고, 같은 경로는 한 번만 넣는다.
- [TranscriptReader](../../src/agentvis/transcript.py#TranscriptReader)`(store, projects_dir)`는 서버 안의 작업 스레드 하나로 요청을 처리한다.
  - [TranscriptReader.request](../../src/agentvis/transcript.py#TranscriptReader.request)`(path)`: 경로를 대기열에 넣는다. 처리를 기다리는 같은 경로가 이미 있으면 다시 넣지 않는다. 지금 읽고 있는 경로가 다시 요청되면 읽기가 끝난 뒤 한 번 더 읽는다(그 사이 파일이 자랐을 수 있으므로).
  - `.meta.json`으로 끝나는 경로는 `read_subagent_meta`로, 나머지는 `read_new_records`로 읽는다. 커서가 없는 파일은 처음부터 읽으므로, AgentVis를 켜기 전에 시작된 진행 중 세션도 첫 hook 이벤트 때 시작부터 채워진다.
  - 읽기가 실패해도(기록 루트 밖 경로, 입출력 오류 등) hook 응답과 수집, 다음 요청 처리에는 영향을 주지 않으며, 실패는 `agentvis.transcript` 로거로 남긴다.
  - [TranscriptReader.start](../../src/agentvis/transcript.py#TranscriptReader.start)`()`, [TranscriptReader.stop](../../src/agentvis/transcript.py#TranscriptReader.stop)`()`: 작업 스레드를 시작하고 멈춘다. 멈출 때는 지금 읽는 파일까지만 끝내고 남은 요청은 버린다. 버린 요청은 다음 hook 이벤트나 서버 시작 시 찾기(4.2)가 다시 채운다.
  - [TranscriptReader.wait_until_idle](../../src/agentvis/transcript.py#TranscriptReader.wait_until_idle)`(timeout: float) -> bool`: 대기열이 비고 읽는 파일이 없을 때까지 기다린다. 테스트와 실측에서 쓴다.
- `agentvis serve`는 이벤트 저장소와 함께 `TranscriptReader`를 만들어 시작하고, 서버 앱에 넘긴다. 서버가 끝나면 기록 리더를 멈춘 뒤 이벤트 저장소를 닫는다.
- 세션 기록은 실행 중인 도구 호출 하나만큼 늦게 쓰이므로([두 소스 비교](../DataSource.md#4-두-소스-비교)), 실행 중인 도구는 hook 이벤트로 표시되고 결과가 나온 뒤의 hook 이벤트에서 세션 기록이 따라온다.

### 4.2 서버가 시작될 때 (M2-T4)

`find_unread_transcripts(store, projects_dir) -> list[Path]`가 기록 루트의 세션·서브에이전트 기록 중 다음 파일을 찾아 읽기 요청으로 넘긴다.

- 커서가 있고, 파일 크기가 커서 위치와 다르거나 파일 식별자가 다른 파일
- 커서가 없고, 수정 시각이 수집 시작 시각(이벤트 저장소에 처음 이벤트가 들어온 시각) 이후인 파일

이렇게 하면 서버가 꺼진 동안 시작하고 끝난 세션도 찾는다. 수집 시작 전의 지난 세션은 자동으로 읽지 않고 [4.3 지난 세션 가져오기](#43-지난-세션-가져오기-m2-t5)로만 읽는다. 사용자가 원하지 않은 과거 기록을 모두 쌓지 않기 위해서다.

### 4.3 지난 세션 가져오기 (M2-T5)

- `agentvis import --project <경로>`: 세션 기록의 첫 `cwd`가 그 경로인 세션들을 읽는다.
- `agentvis import --all`: 기록 루트의 모든 세션을 읽는다.
- 서버와 다른 프로세스에서 같은 데이터베이스에 쓰므로, 한 트랜잭션에 최대 500줄씩 나눠 저장해 쓰기 잠금을 짧게 잡는다. 서버의 hook 저장이 오래 기다리지 않게 하기 위해서다([이벤트 저장소 설계의 M2 변경](Store.md#6-m2-변경)).
- 읽은 세션 수, 저장한 이벤트 수, 건너뛴 줄 수를 출력한다.

## 5. 형식 변화와 오류

- 세션 기록은 공개 규격이 아니다([주의 사항](../DataSource.md#32-주의-사항)). 해석할 수 없는 줄, 모르는 유형, 시각이 없는 줄은 건너뛰고 수를 센다. 파일 하나의 실패가 다른 파일 읽기를 멈추지 않는다.
- 건너뛴 줄이 있으면 파일 경로와 수를 서버 로그에 남긴다. 형식 변화를 알아차리기 위해서다.
- 세션 기록 읽기가 모두 실패해도 hook 이벤트는 계속 저장되므로 최소한의 실시간 데이터는 남는다.

## 6. 테스트

[tests/test_transcript.py](../../tests/test_transcript.py)에서 임시 기록 루트와 임시 이벤트 저장소로 확인한다. 아래 항목 중 서버 시작 시 찾기(M2-T4)는 해당 태스크에서 추가한다.

- 실측 형태의 `user`(사용자 지시, 도구 결과), `assistant`(thinking, text, tool_use), `system`, `queue-operation` 줄이 표대로 바뀐다. 대상이 아닌 유형·해석할 수 없는 줄·시각 없는 줄은 건너뛰고 수가 세어진다.
- 이어 읽기: 두 번째 읽기는 새로 덧붙인 줄만 저장하고, 줄바꿈 없는 마지막 줄은 다음 읽기로 넘어가며, 같은 파일을 처음부터 다시 읽어도 중복 저장되지 않는다.
- 파일이 바뀌면(크기가 줄거나 식별자가 다름) 처음부터 읽는다.
- 기록 루트 밖의 경로는 읽지 않는다.
- 서브에이전트 기록 경로가 올바르게 만들어지고, 메타 파일은 내용이 바뀔 때만 다시 저장된다.
- 서버 시작 시 찾기는 커서보다 커진 파일과 수집 시작 이후의 새 파일만 고른다.
- `paths_to_read`가 `transcript_path`, 서브에이전트 기록·메타, `agent_transcript_path`를 중복 없이 고르고 문자열이 아닌 값은 무시한다.
- `TranscriptReader`는 같은 파일 요청을 한 번만 처리하고, 읽는 동안 다시 온 요청은 한 번 더 처리하며, 읽기 실패가 다음 요청 처리를 막지 않는다.
- 수집기가 hook 이벤트를 저장한 뒤 `transcript_path`와 서브에이전트 경로로 읽기를 요청하고, 실제 `TranscriptReader`와 함께 쓰면 hook 이벤트 하나로 세션 기록 내용까지 저장된다.
