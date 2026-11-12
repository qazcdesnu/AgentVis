# 다른 코딩 에이전트 기록과 정보 항목 대응표

이 문서는 AgentVis의 정보 항목(처음 설계의 D 항목과 연구 설계 2의 N 항목)이 Claude Code 밖의 코딩 에이전트 기록에서도 얻어지는지 정리한다. 논문의 기여를 "Claude Code 도구"가 아니라 "코딩 에이전트 실행 기록"의 수준으로 쓰기 위해서다([수업 이후 학회 제출 계획의 점검 목록](SubmissionPlan.md#5-제출-전-점검-목록)). 정보 항목의 정의는 [과업과 데이터 추상화](../design/TaskAbstraction.md#3-정보-항목-사전)와 [과업과 데이터 추상화 2](../design/TaskAbstraction2.md#3-새-정보-항목)에 있다. 관련 작업은 M11-T5다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

## 1. 조사 방법과 한계

- 2026-11-13에 웹 검색으로 각 에이전트의 기록 형식을 찾았다. **대부분 공식 문서가 아니라** 커뮤니티의 역공학 글, 기록을 읽는 제3자 도구의 소스, 데이터셋 설명이었다(출처는 5절).
- 기록 형식은 버전마다 바뀐다. Codex CLI는 같은 해 안에서도 기록 줄 종류가 달라졌다는 보고가 있다.
- 실제 기록 파일을 열어 확인하지 않았다. 표의 "확인 수준"은 출처의 성격이다. 논문에 쓰기 전에 각 에이전트로 짧은 과제를 실행해 실제 기록으로 확인해야 한다(6절).

| 에이전트 | 기록 위치와 형식 | 단위 | 확인 수준 |
| --- | --- | --- | --- |
| Claude Code | `~/.claude/projects/<프로젝트>/<세션>.jsonl`, 줄마다 JSON 기록. hook 이벤트(공식 규격) | 세션 | 실측([데이터 소스](../DataSource.md)) |
| Codex CLI | `~/.codex/sessions/<연>/<월>/<일>/rollout-<시각>-<uuid>.jsonl`. 줄마다 시각·종류·내용. 종류는 `session_meta`, `turn_context`, `response_item`(메시지, 추론, `function_call`·`function_call_output`, `custom_tool_call`), `event_msg`(사용자 메시지, 에이전트 메시지, 토큰 수 등), `compacted` | 세션 | 커뮤니티 문서·제3자 도구 소스(여럿이 일치) |
| OpenHands | 이벤트 흐름(행동 Action과 관찰 Observation). 대화마다 trajectory로 내보내기(`/trajectory`). 명령 실행 결과 관찰에 성공 여부 필드가 붙는다 | 대화 | 공식 문서 일부 + 소스 사본 |
| SWE-agent | 인스턴스마다 `<instance_id>.traj`(JSON). 생각·행동·관찰의 차례(trajectory)와 끝 상태. mini-swe-agent는 `messages`와 `info`(`exit_status`, `submission`)를 담은 다른 형식 | 과제 하나 | 저장소 사본 문서, 데이터셋 설명 |
| Cursor 에이전트 | CLI는 `~/.cursor/chats`, IDE는 작업 공간 저장소의 SQLite(`state.vscdb`)라는 보고가 있다. 형식은 공개되지 않았다 | 대화 | 포럼 글(직원 답변 포함). 형식은 확인 못 함 |

## 2. 대응표

기호: ○ 기록에 그대로 있음, △ 다른 필드에서 끌어낼 수 있거나 일부만 있음, ✕ 없음, ? 확인 못 함.

| 정보 항목 | Claude Code | Codex CLI | OpenHands | SWE-agent | Cursor |
| --- | --- | --- | --- | --- | --- |
| D1·N1 사람의 지시 | ○ 사람 입력 `user` 기록 | ○ 사용자 메시지(`event_msg`, `response_item` 메시지) | ○ 사용자 메시지 행동 | ○ 첫 사용자 메시지(문제 글) | ? |
| D2 작업 중 사용자 메시지 | ○ 대기열 첨부 | △ 같은 턴 안의 사용자 메시지로 구분해야 함 | ○ 사용자 메시지 행동(시각) | ✕ 사람이 끼어들지 않는 실행 | ? |
| D6 응답 글 | ○ `text` 블록 | ○ 에이전트 메시지 | ○ 에이전트 메시지 행동 | ○ 응답·생각 | ? |
| D8 생각 | ○ `thinking`(가려질 수 있음) | △ 추론 항목(요약이나 암호화된 내용) | △ 생각 행동 | ○ 생각(`thought`) | ? |
| D10·D11 도구 종류와 입력 | ○ `tool_use` 이름·입력 | ○ `function_call` 이름·인자(JSON 문자열), `custom_tool_call` | ○ 행동 종류(명령 실행, 파일 읽기·편집 등)와 인자 | △ 행동이 명령 문자열이라 파싱해야 함 | ? |
| D14·D15 상태와 종료 코드 | ○ 결과의 오류 표시, `Exit code N` | △ 출력 기록의 메타데이터(버전에 따라 다름) | ○ 명령 결과 관찰의 종료 코드·성공 여부 | ✕ 관찰 글에만 있음 | ? |
| D16 출력 | ○ 결과 글 | ○ `function_call_output` | ○ 관찰 내용 | ○ 관찰 | ? |
| D24 바꾼 파일 | ○ Edit·Write의 경로 | △ 패치 적용 도구의 패치에서 경로 추출 | ○ 파일 편집 행동의 경로 | △ 편집 명령 파싱, 끝의 제출 패치 | ? |
| D31 실행 순서와 시각 | ○ 기록마다 시각 | ○ 줄마다 시각 | ○ 이벤트마다 시각 | △ 차례는 있으나 절대 시각이 없고 실행 시간만 있음 | ? |
| D33 서브에이전트 | ○ 서브에이전트 기록 | ? | ○ 위임 행동 | ✕ | ? |
| D35 문맥 압축 | ○ `compact_boundary` | ○ `compacted` 기록 | ○ 압축(condensation) 이벤트 | △ 기록 처리기가 줄이지만 기록에 남지 않음 | ? |
| N4 사용자에게 한 질문 | ○ 질문 도구, 마지막 응답 | △ 마지막 에이전트 메시지 | ○ 사용자에게 묻는 행동 | ✕ 사람이 없는 실행 | ? |
| N6\~N8 테스트 실행과 결과 | ○ Bash 명령·출력(분석기 규칙) | ○ 셸 호출·출력 | ○ 명령 실행·관찰 | △ 명령·관찰 글 | ? |

## 3. 연구 설계 2에 주는 의미

- **세 과업에 필요한 정보는 Codex CLI와 OpenHands에도 있다.** 지시 대조 모델(N1\~N9)이 쓰는 것은 지시 글, 응답 글, 도구 호출의 종류·입력·출력, 바뀐 파일, 시각이다. 두 에이전트 모두 이것을 기록한다. 따라서 과업 추상화(U1\~U3)와 정보 항목은 Claude Code에 묶이지 않는다. 논문에는 이 표를 부록으로 넣고, 규칙의 입력이 무엇인지로 일반성을 주장한다.
- **SWE-agent는 사람이 없는 벤치마크 실행이다.** 대응 파악(U1)의 "사용자에게 물었나"와 작업 중 사용자 메시지가 없다. 대신 연구 설계 2의 실험 자료(SWE-bench 방식 과제)와 같은 상황이라, 오류를 심은 과제로 만든 SWE-agent 기록을 지시 대조 화면에 넣는 것은 가능하다(도구 입력을 파싱해야 함).
- **Cursor 에이전트는 형식이 공개되지 않아** 지금은 대상에서 뺀다. 논문의 한계에 적는다.
- **종료 코드는 에이전트마다 다르다.** Claude Code도 성공한 Bash에는 종료 코드가 없어 출력 요약으로 결과를 정했다([테스트 사건](../design/Analysis.md#51-테스트-사건과-완료-보고)). 출력 요약으로 정하는 규칙은 다른 에이전트에도 그대로 쓸 수 있다.

## 4. 다른 에이전트를 읽으려면

AgentVis의 분석기는 원시 이벤트(세션 ID, 종류, 시각, 원문)를 입력으로 받는다([시스템 구조의 데이터 모델](../Architecture.md#41-원시-이벤트)). 다른 에이전트를 읽으려면 그 기록을 Claude Code 기록과 같은 모양의 원시 이벤트(사람 입력, 응답, `tool_use`·`tool_result`)로 바꾸는 변환기를 두면 되고, 지시 대조 규칙은 바꾸지 않아도 된다. 이 변환기는 지금 범위가 아니며, 논문에서 일반성을 실제로 보여야 하면 Codex CLI 변환기부터 만든다(기록 위치와 형식이 가장 잘 알려져 있다).

## 5. 출처

- Codex CLI: [Codex (OpenAI) Session Files Structure](https://lin-guanguo.github.io/llm-memory-research/agent-cli/codex-session-files/), [codex session file schema](https://lin-guanguo.github.io/llm-memory-research/agent-cli/codex-session-file-schema/), [Reverse engineering Codex CLI rollout traces (DEV)](https://dev.to/milkoor/reverse-engineering-codex-cli-rollout-traces-3b9b), [toolpath-codex types (docs.rs)](https://docs.rs/toolpath-codex/0.3.0/toolpath_codex/types/), [Codex CLI Session Analytics](https://codex.danielvaughan.com/2026/03/30/codex-cli-session-analytics-jsonl-rollout)
- OpenHands: [OpenHands trajectory route (공식 문서)](https://docs.all-hands.dev/modules/python/openhands/server/routes/trajectory), [Agent SDK 이벤트 API (공식 문서)](https://docs.openhands.dev/sdk/guides/agent-server/api-reference/events/get-conversation-event.md), [event serialization 소스 사본](https://huggingface.co/spaces/Backup-bdg/OpenHands/blob/main/openhands/events/serialization/event.py)
- SWE-agent: [trajectories 문서(저장소 사본)](https://github.com/Ericsongyl/SWE-agent/blob/main/trajectories), [mini-swe-agent 기록 데이터셋 예](https://huggingface.co/datasets/arpandeepk/swe-cleanroom-trajs)
- Cursor: [Where are cursor chats stored? (포럼)](https://forum.cursor.com/t/where-are-cursor-chats-stored/77295.md), [IDE와 CLI 저장소가 따로임 (포럼)](https://forum.cursor.com/t/local-ide-agent-chats-and-the-agent-cli-still-use-separate-session-stores/165486)

## 6. 확인할 것

- [ ] Codex CLI로 짧은 과제를 실행해 실제 기록에서 2절의 Codex 열을 확인한다(종료 코드 메타데이터, 패치 도구의 경로, 서브에이전트 유무).
- [ ] OpenHands로 같은 과제를 실행해 trajectory를 내보내 확인한다.
- [ ] SWE-agent의 `.traj` 예제 파일로 필드 이름을 확인한다.
