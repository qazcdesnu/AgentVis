# AgentVis

AgentVis는 Claude Code 에이전트가 작업한 과정을 수집해 브라우저에서 보여 주는 로컬 시각화 도구입니다. 팀 동료가 이 저장소를 처음 받았을 때 알아야 할 내용을 정리했습니다.

이 문서는 안내용 요약입니다. 규칙의 원문은 [CLAUDE.md](CLAUDE.md)와 [문서 인덱스](docs/index.md)에서 시작하는 프로젝트 문서에 있고, 둘이 다르면 규칙 문서가 기준입니다.

## 1. 무엇을, 왜 만드는가

- **연구 프로젝트입니다**([제품 비전의 목적](docs/ProductVision.md#1-목적)).
  - 1차 목표: 대학원 수업 과제를 4주 안에 완수합니다. 연구 절차와 논문은 IEEE TVCG(IEEE VIS 정규 논문)의 기준에 맞춰 설계 연구(design study) 형식으로 수행하고 씁니다.
  - 학회 제출은 과제를 완성한 뒤 정합니다. 후보와 근거: [목표 학회 비교](docs/research/TargetVenues.md)
- **연구 질문**: Claude Code로 실제 바이브 코딩을 할 때 이 시각화 도구를 함께 쓰면 코딩 작업이 얼마나 수월해지는가.
- **과제**는 다섯 가지입니다.
  1. 분석할 데이터(Claude Code 작업 기록)를 고른다.
  2. 고른 데이터를 이해하기 쉽게 시각화한다.
  3. 시각화가 왜 필요한지 설명한다.
  4. 유저 스터디를 설계하고 수행한다.
  5. 논문을 쓴다.
- **화면과 유저 스터디는 여섯 과업(T1\~T6)을 기준으로 만듭니다.** 과업은 [Claude Code 실무 고충 조사](docs/research/ClaudeCodePainPoints.md#4-시각화와-유저-스터디에-맞는-우선순위)에서 고른 고충이고, 과업마다 사용자가 답할 질문은 [과업과 데이터 추상화](docs/design/TaskAbstraction.md#4-과업별-분석)에 있습니다. 괄호는 대응하는 핵심 분석 질문입니다.

  | 과업 | 사용자가 답할 질문 |
  | --- | --- |
  | T1 근거 없는 성공 보고 | 마지막에 말한 "완료·통과"가 실제 실행 결과로 뒷받침되나? (Q2) |
  | T2 테스트 변조·건너뛰기 | 실패를 코드로 고쳤나, 테스트를 바꾸거나 건너뛰었나? (Q2, Q5) |
  | T3 무엇을 했는지 파악 | 무엇을 읽고 바꿨나? 읽지 않고 바꾼 파일은? 서브에이전트는 무엇을 했나? (Q1) |
  | T4 문맥 압축 전후 행동 변화 | 대화 요약 뒤 규칙을 잊었나? 언제부터 어겼나? (Q6) |
  | T5 루프·반복 실패 | 시간을 가장 많이 쓴 곳과 그 이유는? 같은 실패를 몇 번 되풀이했나? (Q3, Q4) |
  | T6 지시 위반 지점 | 어디서부터 사용자의 의도에서 벗어났나? 지시를 잘못 이해한 경우와 지시·설정 자체가 틀린 경우를 모두 본다. (Q6) |

- **제품이 답하려는 핵심 분석 질문**은 Q1\~Q6입니다([제품 비전](docs/ProductVision.md#2-핵심-분석-질문)). Q1 어떤 과정을 거쳤나, Q2 어디서 실패했나, Q3 어떤 종류의 작업에서 실패했나, Q4 같은 실패가 반복되었나, Q5 실패 뒤 어떤 우회가 있었나, Q6 어디서부터 사용자의 의도에서 벗어났나(지시를 잘못 이해했거나, 지시·설정 자체가 틀렸는데 따랐거나). Q3\~Q5의 자동 판정은 아직 없습니다([2절](#2-현재-상태-v103-2026-11-07)).

## 2. 현재 상태 (v1.0.3, 2026-11-07)

| 구분 | 내용 |
| --- | --- |
| 된 것 | hook 수집과 세션 기록(JSONL) 이어 읽기, 서버를 켤 때 놓친 기록 찾기, 빠진 hook의 보정, 이벤트 저장소(SQLite), 세션·턴·단계·도구 호출 분석, 조회 API, 실시간 갱신(SSE)과 최신 작업 따라가기, 웹 화면(세션 정보·턴 시퀀스·턴 흐름 그래프·단계 목록) |
| 설계·조사 | [과업과 데이터 추상화](docs/design/TaskAbstraction.md), [시각화 인코딩 설계](docs/design/VisualEncoding.md), [과업별 기능 대응](docs/design/TaskCoverage.md), [좋은 시각화 원칙 조사](docs/research/VisualizationPrinciples.md), [Claude Code 실무 고충 조사](docs/research/ClaudeCodePainPoints.md), [관련 결과물 조사](docs/research/RelatedWork.md) |
| 다음 | 기준 사건 보기와 과업 연결(M8-T2, 과업 T1·T2·T6), 파일 행렬과 문제 칸(M8-T3), 유저 스터디 설계(이슈 I26) |
| 아직 없는 것 | 지난 세션 가져오기(`agentvis import`), 실패·반복·우회의 자동 판정, 신호 카드 |

여섯 과업마다 지금 어떤 기능이 있고 무엇이 남았는지는 [과업별 기능 대응](docs/design/TaskCoverage.md)에 있습니다. 사용자 쪽 오류(잘못된 지시·설정)를 유저 스터디 과업으로 쓸 근거는 [고충 조사 6절](docs/research/ClaudeCodePainPoints.md#6-사용자-쪽-오류에서-시작하는-고충)에 있습니다.

**유저 스터디의 결정 사항**은 [이슈](docs/Issue.md)의 I26에 있습니다.
- 대상: 참가자 12명, 기간은 2026-11-01 기준 4주
- 과업: 현장 과업(실제 바이브 코딩)을 기본으로 하되 통제 과업도 함께 준비
- 기준선: Anthropic 기본 UI(터미널, Claude 웹 원격 제어)만으로 하는 바이브 코딩
- 실험 자료: 실험용 시나리오
- 정답 주석: 팀원 3명
- IRB: 수업이 끝난 뒤 받습니다. 지금부터 받는다고 생각하고 준비합니다(아래 4절).
- 아직 정할 것: 실험 장비와 Claude 계정·요금제(모델 고정), 문맥 압축 문항을 다루는 방법, 12명 모집(시기·경로), 두 단계 질문 방식(기억 → 화면). 지시·설정을 일부러 틀리게 만든 과업을 쓸지도 정합니다([고충 조사 6.4절](docs/research/ClaudeCodePainPoints.md#64-유저-스터디에-주는-함의)).

진행 상황은 [로드맵](docs/Roadmap.md), [진행 중](docs/Ongoing.md), [완료](docs/Done.md), [이슈](docs/Issue.md)에서 봅니다.

## 3. 설치와 실행

AgentVis는 macOS, Linux, Windows 10·11에서 설치하고 실행할 수 있습니다. 세 운영체제 모두 CI에서 같은 검증을 돌립니다([운영체제 이식성](docs/CodeRule.md#31-운영체제-이식성)). 운영체제에 따라 다른 것은 도구 설치 방법과 경로 표기뿐이고, AgentVis 명령은 모두 `uv run ...`으로 같습니다.

### 3.1 필요한 것

| 도구 | 용도 | 비고 |
| --- | --- | --- |
| [uv](https://docs.astral.sh/uv/) | Python 설치와 실행 | Python 3.12는 uv가 알아서 받습니다. Python을 따로 설치할 필요가 없고, 시스템 `python3`는 쓰지 않습니다. |
| git | 저장소 받기, 커밋 | Windows에서는 Git for Windows가 필요합니다. 커밋 메시지 검사 hook을 실행하고, Claude Code도 씁니다. |
| [Claude Code](https://code.claude.com/) | 기록을 수집할 대상 | 설치 방법은 공식 문서를 따릅니다. |
| 웹 브라우저 | 화면 보기 | Chrome, Edge, Firefox, Safari 최신판 |

### 3.2 macOS

터미널에서 실행합니다.

```sh
# 도구 설치 (이미 있으면 건너뜀)
xcode-select --install                                   # git (Xcode 명령행 도구)
curl -LsSf https://astral.sh/uv/install.sh | sh          # uv (또는 brew install uv)
curl -fsSL https://claude.ai/install.sh | bash           # Claude Code

# 저장소 받기
git clone git@github.com:qazcdesnu/AgentVis.git
cd AgentVis
uv sync                                  # 가상 환경과 의존성 설치
git config core.hooksPath .githooks      # 커밋 메시지 검사 hook 켜기 (처음 한 번)
```

저장소를 iCloud가 동기화하는 폴더(데스크탑, 문서)에 두지 않습니다. 동기화 중에 `.venv` 파일에 숨김 속성이 붙어 패키지를 불러오지 못할 수 있습니다([8. 문제 해결](#8-문제-해결)).

### 3.3 Linux

Ubuntu·Debian 기준입니다. Fedora 등에서는 `apt` 대신 그 배포판의 패키지 관리자(`dnf` 등)를 씁니다.

```sh
# 도구 설치 (이미 있으면 건너뜀)
sudo apt update && sudo apt install -y git curl
curl -LsSf https://astral.sh/uv/install.sh | sh          # uv
curl -fsSL https://claude.ai/install.sh | bash           # Claude Code
# uv·claude 설치 후 새 터미널을 열거나 `source ~/.bashrc`로 PATH를 다시 읽습니다.

# 저장소 받기
git clone git@github.com:qazcdesnu/AgentVis.git
cd AgentVis
uv sync
git config core.hooksPath .githooks
```

화면이 없는 원격 서버에서 실행하면 브라우저로 직접 열 수 없습니다. 이때는 내 컴퓨터에서 `ssh -L 8765:127.0.0.1:8765 <서버>`로 포트를 넘겨 받아 엽니다.

### 3.4 Windows

PowerShell에서 실행합니다.

```powershell
# 도구 설치 (이미 있으면 건너뜀)
winget install --id Git.Git -e                                                   # Git for Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # uv (또는 winget install --id astral-sh.uv -e)
irm https://claude.ai/install.ps1 | iex                                          # Claude Code
# 설치 후 PowerShell을 새로 열어 PATH를 다시 읽습니다.

# 저장소 받기
git clone git@github.com:qazcdesnu/AgentVis.git
cd AgentVis
uv sync
git config core.hooksPath .githooks
```

- **Claude Code와 AgentVis는 같은 환경에서 실행합니다.**
  - Claude Code를 Windows에 바로 설치했다면 AgentVis도 Windows(PowerShell)에서 실행합니다.
  - Claude Code를 WSL 안에서 쓴다면 AgentVis도 WSL 안에서 [Linux 안내](#33-linux)대로 실행합니다.
  - 둘이 다른 환경에 있으면 hook이 서버에 닿지 않고, 세션 기록 폴더도 서로 다릅니다.
- 커밋 메시지 검사 hook은 Git for Windows의 `sh`가 실행합니다. 따로 설정할 것은 없습니다.
- 줄바꿈은 저장소의 `.gitattributes`가 LF로 고정합니다. `core.autocrlf` 설정과 관계없이 그대로 둡니다.

### 3.5 실행 (세 운영체제 공통)

1. 수집 서버를 띄웁니다. 터미널 하나를 계속 열어 둡니다.

   ```sh
   uv run agentvis serve                 # http://127.0.0.1:8765, 다른 포트는 --port
   ```

2. Claude Code에 AgentVis hook을 설치합니다. 처음 한 번만 하면 됩니다.

   ```sh
   uv run agentvis hooks install         # 제거: uv run agentvis hooks uninstall
   ```

3. Claude Code로 평소처럼 작업합니다.
4. 브라우저에서 `http://127.0.0.1:8765/`를 엽니다. 화면은 실시간으로 갱신되고, 맨 위 `● 실시간 따라가기`가 켜져 있으면 진행 중인 세션의 최신 턴과 노드를 따라갑니다([3.7절](#37-화면-사용법)).

### 3.6 꼭 알아야 할 점

- **hook은 전역 설정을 바꿉니다.** `hooks install`은 Claude Code 사용자 설정 파일에 hook 14개를 추가합니다. 그래서 이 컴퓨터의 **모든 프로젝트**에서 Claude Code를 쓸 때마다 이벤트가 서버로 갑니다.
  - 기존 설정은 바꾸기 전에 AgentVis 데이터 폴더의 `backups/`에 백업됩니다.
  - `hooks uninstall`은 AgentVis hook만 지웁니다.
  - Windows에서 Claude Code가 설정 파일을 쓰는 중이면 저장이 실패할 수 있습니다. 그때는 잠시 뒤 다시 실행합니다.
- **서버가 꺼져 있어도 Claude Code 작업은 막히지 않습니다.** hook 전송만 실패하고, Claude Code에 hook 오류 알림이 보일 수 있습니다. 그 사이 작업은 서버를 다시 켤 때 세션 기록에서 찾아 읽습니다. 빠진 턴 끝(`Stop`)도 세션 기록으로 보정하고, 화면은 빠진 신호마다 무엇을 보완했고 무엇을 확인할 수 없는지 적습니다.
- **수집을 시작한 뒤의 작업만 보입니다.** 처음 hook을 설치하기 전의 지난 세션을 가져오는 명령은 아직 없습니다.
- **올린 뒤 첫 시작은 오래 걸릴 수 있습니다.** v1.0.0부터 저장소가 5판으로 올라가며 세션 기록을 한 번 처음부터 다시 읽습니다. 이미 저장된 이벤트는 중복 저장되지 않습니다.
- **경로**는 운영체제마다 표기가 다릅니다.

  | 내용 | macOS·Linux | Windows |
  | --- | --- | --- |
  | Claude Code 사용자 설정 | `~/.claude/settings.json` | `%USERPROFILE%\.claude\settings.json` |
  | Claude Code 세션 기록 | `~/.claude/projects/` | `%USERPROFILE%\.claude\projects\` |
  | AgentVis 데이터(이벤트 저장소, 설정 백업) | `~/.agentvis/` | `%USERPROFILE%\.agentvis\` |

- **실험이나 시험용 데이터는 따로 둡니다.** `AGENTVIS_HOME`을 지정하면 실제 데이터와 섞이지 않습니다.

  ```sh
  # macOS·Linux
  AGENTVIS_HOME=/tmp/agentvis-test uv run agentvis serve --port 8766
  ```

  ```powershell
  # Windows PowerShell
  $env:AGENTVIS_HOME = "$env:TEMP\agentvis-test"; uv run agentvis serve --port 8766
  ```

  hook을 시험하려고 `claude -p`를 돌릴 때는 사용자 설정을 빼고 실행해야 실제 저장소에 섞이지 않습니다([데이터 소스의 실측 방법](docs/DataSource.md#24-실측-방법)).

### 3.7 화면 사용법

| 영역 | 기능 |
| --- | --- |
| 왼쪽 | 프로젝트. 세션 기록의 작업 폴더 기준으로 묶습니다. `◂`로 접습니다. |
| 가운데 | 세션. Claude Code가 지은 제목, 턴·도구·실패 수를 보여 줍니다. `◂`로 접습니다. |
| 오른쪽 | 세션 상세. 아래 네 상자입니다. |

세션 상세의 네 상자:

1. **세션 정보**: 제목, Claude Code의 진행 요약(`요약` 표지), 상태·시간·브랜치·턴·도구·실패 수.
2. **세션 전체 흐름**: 턴마다 칸 하나. 실패가 있는 턴은 빨강(`✕개수`), 작업 중 사용자 메시지가 있는 턴은 노란 ◆, 대화 요약(문맥 압축)이 있는 턴은 점선입니다. 칸을 누르거나 배지(`실패한 턴 ◀ ▶` 등, 단축키 `[` `]`)로 턴을 고릅니다.
3. **턴 선택**: 볼 턴을 고르고, 턴 시작 지시 전문을 봅니다.
4. **턴 작업 흐름**: `흐름 그래프 | 목록`으로 그리는 방식을 바꿉니다.
   - 흐름 그래프: 주 에이전트, 서브에이전트, 백그라운드 작업이 각각 한 줄입니다. 가로 길이가 걸린 시간이고, 10초 넘는 대기는 물결(≈)로 줄입니다(`시간축: 긴 대기 줄여 보기 | 실제 시간 길이로 보기`). 도구 실행은 상태 색 막대, 생각은 회색, 응답·도구 입력 작성은 빗금 막대입니다. 그래프 위 범례에 뜻이 있습니다.
   - 노드를 누르면 아래에 상세가 나옵니다. JSON인 입력·결과는 `[ 원문 | JSON 정리 ]`로 바꿔 보고, 2,000자에서 잘린 결과는 `전체 보기`로 확인을 거쳐 전체를 받습니다.

- **실시간 따라가기**: 맨 위 `● 실시간 따라가기`가 켜져 있으면 진행 중인 세션의 최신 턴과 주 에이전트 최신 노드를 따라갑니다. 누르면 지금 화면에 머뭅니다. 직접 턴이나 노드를 고르면 저절로 꺼집니다.
- **선택 상태는 주소(URL)에 남습니다.** 따라가기를 끈 화면의 주소를 공유하면 같은 턴·노드가 열립니다. 단, 같은 데이터를 가진 컴퓨터에서만 그렇습니다.

## 4. 데이터와 개인정보

- **모든 데이터는 로컬에만 있습니다.**
  - 이벤트 저장소: AgentVis 데이터 폴더의 `agentvis.db`
  - Claude Code 원본 기록: Claude Code 세션 기록 폴더
  - 운영체제별 위치는 [3.6절](#36-꼭-알아야-할-점)의 표에 있습니다.
  - 서버는 `127.0.0.1`에서만 받고, 다른 주소에서 온 요청과 브라우저 출처가 붙은 요청은 거부합니다([요청 검증](docs/design/Collector.md#21-요청-검증)).
- **작업 기록에는 민감한 내용이 그대로 들어 있습니다.** 프롬프트, 파일 내용, 명령 출력, 경로가 모두 남습니다.
  - DB 파일이나 세션 기록을 저장소에 커밋하지 않습니다.
  - 메신저나 공유 드라이브에 올리지 않습니다.
  - 외부 서비스(공개 웹 페이지 등)에 붙여 넣지 않습니다.
- **지금 AgentVis는 LLM을 부르지 않습니다.** 화면의 `요약`(진행 요약)은 Claude Code가 세션 기록에 이미 남긴 글을 보여 주는 것입니다.
- **앞으로 LLM 요약을 쓰면 데이터가 밖으로 나갑니다.** 사용은 허용됐지만, 그때는 기록이 Anthropic API로 전송되므로 참가자 동의서에 그 사실을 적어야 합니다.
- **IRB를 받는다는 전제로 진행합니다.** 참가자 데이터는 다음 원칙으로 다룹니다.
  - 실험 자료는 실험용 시나리오로 만듭니다. 개인 작업 기록은 실험 자료로 쓰지 않습니다.
  - 참가자 데이터는 참가자 번호로만 저장합니다.
  - 동의 없이 수집하지 않습니다.
  - 보관 위치와 삭제 시점을 정해 둡니다.

## 5. 저장소 구조

| 경로 | 내용 |
| --- | --- |
| `CLAUDE.md` | 작업 절차와 핵심 원칙. 사람과 Claude Code 모두 가장 먼저 읽습니다. |
| `docs/` | 모든 문서. 시작점은 [문서 인덱스](docs/index.md)입니다. |
| `docs/design/` | 연구 설계(과업과 데이터 추상화, 시각화 인코딩 설계, 과업별 기능 대응)와 구성 요소별 상세 설계(수집기, 기록 리더, 이벤트 저장소, 분석기, 웹 UI, 흐름 그래프, CLI) |
| `docs/research/` | 연구 조사 문서 |
| `src/agentvis/` | 제품 코드: 서버, 수집기, 기록 리더, 이벤트 저장소, 분석기(`analysis/`), 웹 화면(`web/`) |
| `src/agentvis/web/vendor/` | 저장소에 넣은 외부 라이브러리(D3 7.9.0). 외부 CDN은 쓰지 않습니다([이유](docs/design/WebUI.md#11-저장소에-넣은-라이브러리)). |
| `tools/` | 규칙 검사기(문서 링크, 문서↔코드 포인터, 작업 관리, 커밋, 웹 파일) |
| `tests/` | 단위 테스트(`unittest`) |
| `.githooks/`, `.github/` | 커밋 메시지 검사 hook, CI(GitHub Actions)와 PR 템플릿 |

전체 구조와 데이터 흐름은 [시스템 구조](docs/Architecture.md)에 있습니다.

## 6. 협업 규칙 요약

Claude Code로 이 저장소에서 작업하면 [CLAUDE.md](CLAUDE.md)가 자동으로 적용됩니다. 사람이 직접 작업할 때도 같은 규칙을 따릅니다.

1. **문서가 먼저입니다.** 코드를 바꾸기 전에 관련 문서를 먼저 쓰거나 고치고, 문서대로 코드를 씁니다. 코드를 먼저 바꾸고 문서를 맞추지 않습니다([문서 작업 규칙](docs/DocumentationRule.md), [코드 작업 규칙](docs/CodeRule.md)).
2. **규칙은 저장소 문서에만 둡니다.** 개인 메모, Claude Code 메모리, 저장소 밖 파일에 규칙을 두지 않습니다.
3. **모든 작업에는 ID가 있습니다.** 로드맵 태스크(`M<n>-T<m>`), 이슈(`I<n>`), 핫픽스(`H<n>`)입니다. 계획에 없는 일은 이슈로 먼저 등록합니다. 상태는 `[ ]`, `[~]`, `[x]`이고, 진행 중·완료 기록을 남깁니다([작업 관리 규칙](docs/TaskRule.md)).
4. **브랜치·커밋·PR**
   - 작업마다 `<작업 ID 소문자>-<설명>` 브랜치를 만듭니다. 출발점은 병합되지 않은 가장 최근 작업 브랜치, 없으면 `main`입니다.
   - 커밋 제목은 `<작업 ID>: <요약>`이고, 커밋하면 바로 push합니다.
   - `main`에는 PR로만 합칩니다. PR은 번호 순서대로 "Create a merge commit"으로 병합하고, 병합된 브랜치는 자동으로 지워집니다([커밋 규칙](docs/CommitRule.md), [PR 규칙](docs/PullRequestRule.md)).
5. **기계적으로 검사할 수 있는 규칙을 새로 만들면, 같은 작업에서 검사기도 만듭니다.**
6. **작업을 끝내기 전에 아래를 모두 통과시킵니다.** CI도 같은 검사를 돌립니다([검증 도구](docs/VerificationTools.md)).

   ```sh
   uv run python -m tools.check_docs
   uv run python -m tools.check_pointers
   uv run python -m tools.check_tasks
   uv run python -m tools.check_commits
   uv run python -m tools.check_web
   uv run python -m unittest discover -s tests -t .
   ```

## 7. 주요 문서

| 읽을 때 | 문서 |
| --- | --- |
| 처음 | [제품 비전](docs/ProductVision.md), [시스템 구조](docs/Architecture.md), [데이터 소스](docs/DataSource.md) |
| 연구·논문 | [목표 학회 비교](docs/research/TargetVenues.md), [좋은 시각화 원칙 조사](docs/research/VisualizationPrinciples.md), [Claude Code 실무 고충 조사](docs/research/ClaudeCodePainPoints.md), [관련 결과물 조사](docs/research/RelatedWork.md), [과업과 데이터 추상화](docs/design/TaskAbstraction.md), [시각화 인코딩 설계](docs/design/VisualEncoding.md), [과업별 기능 대응](docs/design/TaskCoverage.md) |
| 화면 작업 | [시각화 인코딩 설계](docs/design/VisualEncoding.md), [웹 UI 설계](docs/design/WebUI.md), [작업 흐름 그래프 설계](docs/design/FlowGraph.md), [분석기 설계](docs/design/Analysis.md) |
| 할 일 | [로드맵](docs/Roadmap.md), [이슈](docs/Issue.md) |
| 전체 목록 | [문서 인덱스](docs/index.md) |

## 8. 문제 해결

| 증상 | 해결 |
| --- | --- |
| `ModuleNotFoundError: No module named 'agentvis'` (macOS) | 저장소가 iCloud 동기화 폴더(데스크탑·문서) 안에 있으면 `.venv` 파일에 숨김 속성이 붙어 생깁니다(이슈 H1). iCloud "데스크탑 및 문서" 동기화를 끄거나 저장소를 동기화 밖으로 옮긴 뒤 `.venv`를 지우고 `uv sync`를 다시 실행합니다. |
| `uv`·`claude` 명령을 찾을 수 없음 | 설치 직후에는 PATH가 반영되지 않았을 수 있습니다. 터미널(PowerShell)을 새로 엽니다. |
| 커밋할 때 `uv: command not found` (Windows) | 커밋 hook은 Git for Windows의 `sh`에서 돕니다. uv 설치 후 Git Bash·PowerShell을 새로 열거나 컴퓨터에 다시 로그인해 PATH를 반영합니다. |
| hook이 서버에 닿지 않음 (Windows + WSL) | Claude Code와 AgentVis가 같은 환경(둘 다 Windows, 또는 둘 다 WSL)에서 실행되는지 확인합니다([3.4절](#34-windows)). |
| 서버 시작 시 포트 사용 중 | 이미 다른 `agentvis serve`가 떠 있습니다. 그 서버를 쓰거나 `--port`로 다른 포트를 씁니다. hook은 설치할 때의 포트로 보내므로, 포트를 바꾸면 `hooks install --port <포트>`로 다시 설치합니다. |
| 화면에 세션이 안 보임 | 서버가 켜져 있는지(`http://127.0.0.1:8765/health`), hook이 설치되어 있는지 확인합니다. hook 설치 전의 세션은 보이지 않습니다. |
| 브라우저에서 400 오류 | `http://127.0.0.1:<포트>/` 또는 `http://localhost:<포트>/`로 엽니다. 다른 호스트 이름은 거부됩니다. |
| 화면이 갱신되지 않음 | 맨 위가 `○ 연결 끊김`이면 서버가 꺼진 것입니다. 서버를 다시 켜면 저절로 다시 이어지고, 끊긴 동안의 변경을 한 번에 받습니다. |
| 고친 뒤에도 예전 화면이 보임 | v1.0.0 이전에서 올렸다면 브라우저가 예전 파일을 들고 있을 수 있습니다. 한 번만 강력 새로고침(macOS `⌘+Shift+R`, Windows·Linux `Ctrl+Shift+R`)합니다. 그 뒤로는 일반 새로고침으로 충분합니다. |
| 올린 뒤 첫 시작이 오래 걸림 | 저장소가 5판으로 올라가며 세션 기록을 한 번 다시 읽는 중입니다([3.6절](#36-꼭-알아야-할-점)). 끝날 때까지 기다립니다. |
| 커밋이 거부됨 | 커밋 메시지가 `<작업 ID>: <요약>` 형식이 아니거나, 그 ID가 시작(`[~]`)되지 않았습니다. 오류 메시지대로 고칩니다. |
