# 실험 자료 도구 설계

이 문서는 [연구 설계 2](../research/StudyDesign.md#4-실험-자료)의 실험 자료를 만드는 도구를 설계한다. 오류를 심은 지시로 실행 기록을 만들고(M9-T2), 정답표를 검사하고(M9-T3), 기준선 텍스트 보기를 만든다(M9-T4). 도구는 `agentvis study` 하위 명령과 [agentvis/study](../../src/agentvis/study/__init__.py) 패키지다. 만든 자료는 [실험 모드](Cli.md#22-experiment)로 참가자에게 준다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

## 1. 자료의 모양

한 과제(원본 과제)에서 지시의 변형 여러 개를 만들고, 변형마다 Claude Code를 여러 번 실행한다. 결과 폴더는 Claude Code 기록 루트와 같은 모양이라 그대로 실험 모드의 `--transcripts`가 된다.

```text
<결과 폴더>/
  runs.jsonl                       # 실행마다 한 줄: 변형, 회차, 세션 ID, 버전, 비용 등
  <변형 이름>/                     # 예: cal-e2 (실험 모드에서는 프로젝트 폴더)
    <세션 ID>.jsonl                # 실행 기록
    <세션 ID>/subagents/…          # 서브에이전트 기록(있으면)
    <세션 ID>.diff                 # 실행이 끝난 뒤 작업 사본의 변경(주석용)
```

- 변형 이름은 영문자·숫자·`_`·`-`만 쓴다([STUDY_NAME_PATTERN](../../src/agentvis/study/runner.py#STUDY_NAME_PATTERN)). 폴더 이름이 되기 때문이다.
- 결과 폴더는 연구자 컴퓨터에만 둔다. 공개 저장소에서 만든 과제라 보충 자료로 낼 수 있지만, 내기 전에 기록에 개인 경로·토큰이 없는지 확인한다. 비대화형 기록에는 계정 식별자(`session-owner` 줄의 `accountUuid`, `organizationUuid`)가 들어 있으므로(2026-11-13 실측) 공개하기 전에 그 줄을 지운다.

## 2. 실행 기록 생성 (M9-T2)

`agentvis study run --repo <저장소> --commit <커밋> --instruction <지시 파일> --name <변형 이름> --out <결과 폴더> [--runs N] [--model M] [--max-budget-usd X] [--timeout S] [--workdir DIR] [--claude PATH]`

명령 처리는 [_study_run](../../src/agentvis/cli.py#_study_run)이 하고, [run_variant](../../src/agentvis/study/runner.py#run_variant)가 회차마다 다음을 한다.

1. **작업 사본**: `<workdir>/<저장소 이름>`을 지우고 `git clone --quiet <저장소>`한 뒤 `git checkout --quiet <커밋>`한다. 기본 `workdir`은 시스템 임시 폴더 아래 `agentvis-study`다. 경로가 기록의 `cwd`로 남아 화면에 보이므로, 개인 정보가 없는 경로를 쓰고 **변형 이름을 넣지 않는다**. 같은 과제의 모든 변형과 회차가 같은 경로에서 돌아, 참가자가 경로로 오류 유형을 짐작하지 못한다(M9-T4에서 고침). 저장소 이름은 경로나 URL의 마지막 부분에서 `.git`을 뗀 것이다.
2. **실행**: [claude_command](../../src/agentvis/study/runner.py#claude_command)가 만든 명령을 작업 사본에서 실행한다.
   - `claude -p <지시> --session-id <새 UUID> --output-format json --setting-sources project,local --strict-mcp-config --permission-mode acceptEdits --allowedTools Bash Read Edit Write Glob Grep`
   - `--setting-sources project,local`: 사용자 설정(`~/.claude/settings.json`)을 읽지 않는다. 사용자 설정의 AgentVis hook이 실행 기록을 평소 데이터베이스로 보내지 않게 하고, 연구자의 개인 규칙이 실험 기록에 섞이지 않게 한다(I26). `--strict-mcp-config`로 사용자의 MCP 서버도 쓰지 않는다.
   - 비대화형이라 권한을 물을 수 없으므로, 편집은 `acceptEdits`로, Bash는 `--allowedTools`로 허용한다. **Bash는 제한 없이 실행되므로, 신뢰할 수 있는 공개 저장소의 작업 사본에서만 돌리고, 가능하면 컨테이너나 별도 계정에서 돌린다.**
   - `--model`과 `--max-budget-usd`를 주면 그대로 넘긴다. 모델은 실험 내내 고정한다.
   - [STUDY_TIMEOUT_SECONDS](../../src/agentvis/study/runner.py#STUDY_TIMEOUT_SECONDS)(1,800초, `--timeout`으로 바꿈)가 지나면 멈추고, 그 회차는 `timed_out`으로 남긴다.
3. **기록 옮기기**: [collect_transcript](../../src/agentvis/study/runner.py#collect_transcript)가 `~/.claude/projects/*/<세션 ID>.jsonl`과 같은 이름의 폴더(서브에이전트 기록)를 결과 폴더의 `<변형 이름>/` 아래로 **옮긴다**. 복사가 아니라 옮기는 이유는, 남겨 두면 평소 `agentvis serve`가 다음 시작 때 놓친 기록으로 읽어 연구자의 데이터베이스에 섞이기 때문이다.
4. **변경 남기기**: 작업 사본에서 `git add -A` 뒤 `git diff --cached`를 `<세션 ID>.diff`로 저장한다. 빌드 부산물(`__pycache__`, `*.pyc`, `node_modules`, `.pytest_cache`)은 [DIFF_EXCLUDES](../../src/agentvis/study/runner.py#DIFF_EXCLUDES)로 뺀다. 주석자가 정답표를 만들 때 본다.
5. **실행 정보**: `runs.jsonl`에 한 줄을 덧붙인다. 필드는 `name`, `run`, `session_id`, `repo`, `commit`, `model`, `claude_version`(`claude --version`), `started_at`, `ended_at`, `exit_code`, `timed_out`, `transcript`(결과 폴더 기준 경로, 없으면 null), 그리고 `claude`의 JSON 출력에서 `is_error`, `num_turns`, `total_cost_usd`, `duration_ms`다. 버전과 모델은 논문에 밝혀야 한다([제출 계획](../research/SubmissionPlan.md#5-제출-전-점검-목록)).

- 기록 파일을 찾지 못하면(실행이 시작도 못 함) 그 회차의 `transcript`는 null이고, 명령은 끝에 실패 회차 수를 알리며 종료 코드 1로 끝난다. 다른 회차는 계속한다.
- 실행은 [RunSpec](../../src/agentvis/study/runner.py#RunSpec)으로 묶고, Claude Code 호출은 바꿔 끼울 수 있는 함수로 받는다. 테스트는 가짜 호출로 기록 파일을 만들어 실제 Claude Code를 부르지 않는다.

## 3. 정답표 (M9-T3)

결과 폴더 맨 위의 `key.json`이 정답표다. 시행(참가자에게 보일 기록 하나)마다 심은 오류와 에이전트의 대응을 적는다. 주석자 두 명이 따로 만든 뒤 맞춘 결과를 적는다([연구 설계 2의 U1](../research/StudyDesign.md#32-과업별-정의)).

```json
{
  "version": 1,
  "trials": [
    {
      "id": "toy-e2-1",
      "use": "practice",
      "variant": "toy-e2",
      "session_id": "00cf17e0-…",
      "error_type": "E2",
      "original_text": "`discount.py`의 코드 조회",
      "perturbed_text": "`invoice.py`의 `total`에서 `round` 처리",
      "response": "worked_around",
      "first_notice": "toolu_…",
      "note": "주석 메모"
    }
  ]
}
```

| 필드 | 뜻 | 규칙 |
| --- | --- | --- |
| `id` | 시행 이름 | 영문자·숫자·`_`·`-`, 정답표 안에서 겹치지 않는다 |
| `use` | 쓰임 | `practice`(연습), `trial`(U1·U2 본 시행), `u3`(결정 지점에서 자른 U3용) |
| `variant`, `session_id` | 기록 위치 | `<결과 폴더>/<variant>/<session_id>.jsonl`이 있어야 한다 |
| `error_type` | 심은 오류 | `E1`, `E2`, `E3`, `none`(통제 시행) |
| `original_text`, `perturbed_text` | 바꾼 곳 | `none`이 아니면 둘 다 있어야 하고, `perturbed_text`는 기록의 첫 사용자 입력(지시)에 그대로 들어 있어야 한다. U2의 위치 정답이다. `none`이면 둘 다 null이다 |
| `response` | U1 대응 범주 | `followed`(알아채지 못하고 지시대로), `asked`(알아채고 물음), `worked_around`(알아채고 말없이 또는 설명하며 우회), `noticed_then_followed`(흔적은 있으나 결국 지시대로) |
| `first_notice` | U1 처음 알아챈 단계 | 기록의 도구 호출 ID(`toolu_…`)나 기록 줄의 `uuid`. `followed`이면 null, 아니면 기록에 있어야 한다 |
| `note` | 주석 메모 | 자유 |

[check_key](../../src/agentvis/study/key.py#check_key)`(folder) -> list[str]`가 위 규칙을 검사해 문제 목록을 돌려준다. `agentvis study check-key <결과 폴더>`([_study_check_key](../../src/agentvis/cli.py#_study_check_key))는 문제를 한 줄씩 출력하고 있으면 종료 코드 1로 끝난다. 문제가 없으면 [key_summary](../../src/agentvis/study/key.py#key_summary)가 만든 **오류 유형 × 대응 범주 표**(쓰임별 시행 수)를 출력한다. 자극 세트가 고르게 짜였는지 보기 위해서다([연구 설계 2의 4.3](../research/StudyDesign.md#43-실행-기록-만들기)).

- 범주 값은 [ERROR_TYPES](../../src/agentvis/study/key.py#ERROR_TYPES), [RESPONSES](../../src/agentvis/study/key.py#RESPONSES), [USES](../../src/agentvis/study/key.py#USES)에 있다.
- 지시는 기록의 첫 `user` 줄에서 읽는다([instruction_text](../../src/agentvis/study/key.py#instruction_text)). 기록 파일은 [read_records](../../src/agentvis/study/key.py#read_records)로 읽고, JSON 객체가 아닌 줄은 건너뛴다. 내용이 문자열이면 그대로, 블록 목록이면 `text` 블록을 이어 붙인다.
- 이 정답표는 참가자에게 보이지 않는다. 실험 모드 서버는 `key.json`을 읽지 않는다.

## 4. 기준선 텍스트 기록 보기 (M9-T4)

[연구 설계 2의 기준선](../research/StudyDesign.md#52-기준선)이다. 같은 실행 기록을 Claude Code 대화 화면처럼 시간 순서의 글로 보여 준다. 정보는 AgentVis와 같고 시각화만 없다. 검색은 브라우저의 찾기(Ctrl+F·⌘F)를 쓴다.

`agentvis study baseline <결과 폴더> --out <폴더>`는 결과 폴더의 세션 기록마다 `<out>/<세션 ID>.html` 하나를 만든다([write_baseline](../../src/agentvis/study/baseline.py#write_baseline)). 처리는 [_study_baseline](../../src/agentvis/cli.py#_study_baseline)이 한다. 파일 이름과 제목에 변형 이름을 넣지 않는다(참가자가 오류 유형을 짐작하지 못하게).

[render_transcript](../../src/agentvis/study/baseline.py#render_transcript)`(records, title) -> str`가 기록 줄을 차례로 다음처럼 그린다.

| 기록 | 보이는 모양 |
| --- | --- |
| 사용자 입력(글) | `> 사용자` 머리와 원문 |
| 응답 글 | `● 응답` 머리와 원문 |
| 생각 | `생각`이라는 접힌 칸(`<details>`). 내용이 비었으면 "(내용 없음)" |
| 도구 호출 | `● 도구 이름` 머리와 입력. Bash는 `$ <명령>`, Read·Edit·Write는 파일 경로와 바꾼 글(Edit의 `old_string`·`new_string`, Write의 `content`), 그 밖은 JSON |
| 도구 결과 | `⎿ 결과`(오류면 `⎿ 오류`) 머리와 결과 글. 20줄을 넘으면 접힌 칸에 넣고 줄 수를 머리에 적는다. 브라우저의 찾기는 접힌 칸 안도 찾는다 |
| 그 밖(시스템, 첨부 등) | 그리지 않는다 |

- 결과가 [FOLD_LINES](../../src/agentvis/study/baseline.py#FOLD_LINES)(20줄)를 넘으면 접는다.
- 줄마다 기록 시각(시:분:초)을 작게 붙인다. AgentVis 화면도 시각을 보여 주므로 정보를 같게 맞춘다.
- 모든 글은 HTML로 이스케이프한다(`html.escape`). 기록은 신뢰할 수 없는 데이터다([웹 UI 설계의 보안](WebUI.md#4-보안)).
- 파일 하나로 끝나도록 스타일을 안에 넣고, 스크립트와 외부 자원은 쓰지 않는다.

## 6. 테스트

- [tests/test_study_runner.py](../../tests/test_study_runner.py) (M9-T2)
  - 명령에 `-p`, 새 세션 ID, `--setting-sources project,local`, `--strict-mcp-config`, 허용 도구가 있고, 모델·예산을 주면 들어간다.
  - 임시 git 저장소를 원본으로 두 회차를 돌리면, 가짜 호출이 기록 루트에 쓴 기록이 결과 폴더의 `<변형>/<세션 ID>.jsonl`로 옮겨지고 기록 루트에는 남지 않는다. 서브에이전트 폴더도 옮겨진다. 가짜 호출이 바꾼 파일이 `.diff`에 있고, `__pycache__`는 없다. `runs.jsonl`에 두 줄이 있고 필드가 맞다.
  - 가짜 호출이 기록을 쓰지 않으면 그 회차의 `transcript`는 null이고 실패 회차로 센다.
  - 변형 이름에 `/`나 `..`가 있으면 거부한다.
- [tests/test_study_key.py](../../tests/test_study_key.py) (M9-T3)
  - 올바른 정답표는 문제가 없고, 요약 표에 오류 유형 × 대응 범주의 시행 수가 나온다.
  - 기록 파일이 없거나, `id`가 겹치거나, 범주 값이 틀리거나, `perturbed_text`가 지시에 없거나, `none`인데 바꾼 곳이 있거나, `followed`인데 `first_notice`가 있거나, `first_notice`가 기록에 없으면 각각 문제로 나온다.
  - JSON이 아니거나 `trials`가 목록이 아니면 문제 하나로 끝난다.
  - `study check-key`가 문제가 있으면 1, 없으면 0으로 끝난다.
- [tests/test_study_baseline.py](../../tests/test_study_baseline.py) (M9-T4)
  - 사용자 입력, 응답, 생각, Bash·Edit 호출, 결과와 오류가 위 모양으로 차례대로 나오고, 시스템 줄은 나오지 않는다.
  - 20줄을 넘는 결과는 접힌 칸에 들어간다.
  - 기록의 `<script>` 같은 글은 이스케이프되어 태그로 나오지 않는다.
  - `study baseline`이 결과 폴더의 세션마다 `<세션 ID>.html`을 만들고, 파일에 변형 이름이 없다.
- `tests/test_study_runner.py` (M9-T4 추가분): 같은 과제의 회차가 모두 `<workdir>/<저장소 이름>`에서 돈다.
