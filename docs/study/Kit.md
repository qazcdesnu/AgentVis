# 수업 실험 미니 버전 자료 묶음

이 문서는 [연구 설계 2의 수업 실험 미니 버전](../research/StudyDesign.md#9-수업-실험-미니-버전)을 실제로 진행하기 위한 자료 묶음의 안내다. 팀이 자극(오류를 심은 과제의 실행 기록)을 만드는 절차, 시행 구성과 순서 배치, 참가자용 자료로 이어진다. 도구의 동작은 [실험 자료 도구 설계](../design/Study.md)에, 실험 화면은 [CLI 설계의 experiment](../design/Cli.md#22-experiment)에 있다. 관련 작업은 M9-T5다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

| 자료 | 쓰는 사람 |
| --- | --- |
| 이 문서: 자극 만들기, 시행 구성, 폴더 준비 | 팀 |
| [과업지](TaskSheet.md): 시행마다 답할 질문, U3, 사후 설문 | 참가자 |
| [진행 대본](Protocol.md): 45분 진행 순서, 안내 문구, 동의서와 사후 설명 | 진행자 |
| `study/practice/`: 연습 과제(작은 저장소, 원본 지시, 오류를 심은 지시) | 팀, 진행자 |

## 1. 자극 만들기

### 1.1 과제와 지시

1. 공개 저장소의 실제 이슈와 수정 PR에서 과제를 고른다([원본 과제의 기준](../research/StudyDesign.md#41-원본-과제)). 원본 지시로 에이전트가 풀어야 하고, 기록은 도구 호출 20\~50개 정도가 좋다.
2. 원본 지시(`original.md`)를 쓴다. 이슈 글을 줄이고, 마지막에 테스트 명령을 적는다.
3. 맡은 오류 유형으로 변형 지시(`e1.md`, `e2.md`, `e3.md`)를 쓴다. 한 변형에 오류 **하나**만 심는다.
   - E1 재현 조건 누락·왜곡(김진웅), E2 원인·위치 오도(이경태), E3 모순된 요구사항(정승호)
4. 지시를 쓸 때 지킬 것
   - 파일·함수·테스트 이름은 백틱(`` ` ``)으로 감싼다. 화면의 판정 규칙이 지시가 가리킨 대상을 찾는 데 쓴다([정보 항목 N2](../design/TaskAbstraction2.md#3-새-정보-항목)).
   - 변형 지시는 원본과 같은 길이와 말투로 쓴다. 지시만 읽고 오류를 알 수 있으면 안 된다. 팀원 한 명이 기록 없이 지시만 읽고 오류를 찾을 수 있으면 다시 쓴다.
   - 바꾼 부분을 `original_text`(원본의 해당 부분)와 `perturbed_text`(변형 지시에 그대로 들어간 글)로 적어 둔다. 정답표에 쓴다.

### 1.2 실행 기록 만들기

과제 저장소가 git 저장소가 아니면 먼저 만든다(연습 과제의 예).

```sh
cp -r study/practice/repo /tmp/practice-repo
git -C /tmp/practice-repo init -q
git -C /tmp/practice-repo add -A
git -C /tmp/practice-repo -c user.name=study -c user.email=study@example.com commit -qm start
```

변형마다 여러 번 실행한다. 모델과 Claude Code 버전은 실험 내내 같게 둔다.

```sh
uv run agentvis study run --repo /tmp/practice-repo --commit <커밋> \
  --instruction study/practice/e2.md --name practice-e2 --out <결과 폴더> \
  --runs 3 --model <모델> --max-budget-usd 1 --workdir /tmp/agentvis-study
```

- `--workdir`는 사용자 이름이 들어가지 않는 경로로 둔다. 경로가 기록에 남아 참가자에게 보인다.
- Bash가 제한 없이 실행되므로 신뢰할 수 있는 저장소에서만, 가능하면 컨테이너에서 돌린다([실행 기록 생성](../design/Study.md#2-실행-기록-생성-m9-t2)).
- 결과 폴더의 `<세션 ID>.diff`와 기록을 AgentVis로 열어(`uv run agentvis experiment R00 --transcripts <결과 폴더>`) 에이전트의 대응을 본다.

### 1.3 정답표와 기준선

1. 주석자 두 명이 각자 기록마다 대응 범주(`followed`, `asked`, `worked_around`, `noticed_then_followed`)와 처음 알아챈 단계(도구 호출 ID)를 정하고, 다르면 맞춘다. 일치율을 적어 둔다.
2. 결과 폴더에 `key.json`을 쓴다([정답표 형식](../design/Study.md#3-정답표-m9-t3)). 시행마다 `use`를 `practice`, `trial`, `u3` 중 하나로 적는다.
3. `uv run agentvis study check-key <결과 폴더>`가 문제 없이 균형 표를 출력할 때까지 고친다.
4. `uv run agentvis study baseline <결과 폴더> --out <기준선 폴더>`로 기준선 HTML을 만든다.

## 2. 시행 구성

기록 4개를 고른다. 오류 유형 셋에서 하나씩, 그리고 오류 없는 원본 지시의 기록 하나다. 에이전트의 대응 범주가 서로 다르게 섞이도록 고른다(예: 하나는 `followed`, 하나는 `worked_around`).

| 세트 | 기록 |
| --- | --- |
| A | E1 기록, 통제(none) 기록 |
| B | E2 기록, E3 기록 |
| 연습 | `study/practice`의 E2 기록(두 조건 모두 같은 기록으로 연습) |
| U3 | 세트 A·B와 다른 오류 기록 하나를 결정 지점에서 자른 것. 자르기는 기록 파일에서 결정 지점 뒤의 줄을 지운 사본으로 한다 |

세트 A·B의 난이도가 같지 않으므로, 참가자마다 조건과 세트의 짝, 순서를 바꾼다. 8명이면 아래 네 조합을 두 번씩 쓴다.

| 조합 | 먼저 | 나중 |
| --- | --- | --- |
| 1 | AgentVis + 세트 A | 기준선 + 세트 B |
| 2 | AgentVis + 세트 B | 기준선 + 세트 A |
| 3 | 기준선 + 세트 A | AgentVis + 세트 B |
| 4 | 기준선 + 세트 B | AgentVis + 세트 A |

## 3. 실험 폴더 준비

참가자가 한 블록에서 볼 기록만 보이도록 블록마다 시나리오 폴더를 따로 만든다. 실험 모드는 폴더 안의 모든 기록을 세션 목록에 보이기 때문이다.

```text
blocks/
  practice/<변형>/<세션 ID>.jsonl
  setA/<변형>/<세션 ID>.jsonl   (기록 2개)
  setB/<변형>/<세션 ID>.jsonl   (기록 2개)
  u3/<변형>/<세션 ID>.jsonl
baseline/<세션 ID>.html          (2.0.x에서만 필요: study baseline으로 만든 것)
```

- 폴더의 `<변형>` 이름은 화면에 보이지 않지만, 혹시 모르니 `t1`, `t2`처럼 중립적인 이름으로 복사한다.
- AgentVis 블록은 `uv run agentvis experiment <참가자>-<블록> --transcripts blocks/<블록>`으로 띄운다(예: `P03-setB`). 화면 사용 기록이 블록마다 따로 남는다.
- 기준선 블록은 `uv run agentvis experiment <참가자>-<블록> --transcripts blocks/<블록> --baseline`으로 띄운다(2.1.0부터). 같은 시행 단추와 화면 사용 기록이 남아 두 조건을 같은 방식으로 잰다. 2.0.x로 진행하면 `study baseline`으로 만든 HTML 두 개를 브라우저 탭에 미리 열어 두고 시간은 손으로 잰다.
- `key.json`, `runs.jsonl`, `.diff`는 블록 폴더에 넣지 않는다.
