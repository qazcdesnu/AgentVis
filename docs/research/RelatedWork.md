# 관련 결과물 조사: 경쟁자와 배울 점

이 문서는 AgentVis와 비슷한 기존 결과물을 두 범주로 나눠 조사하고 비교한다.

- **경쟁자**: 최신 코딩 에이전트 로그·세션·궤적 시각화(오픈소스, 소프트웨어, 웹 서비스, 연구). AgentVis와의 유사점과 차이점을 비교해 논문의 기여를 분명히 한다.
- **배울 점**: 아주 잘 만든 일반 로그·트레이스·이벤트 시각화. 경쟁자는 아니지만, AgentVis 화면을 "전부 보여 주기"에서 "중요한 것을 추려 보여 주기"로 바꾸는 데 쓸 설계 아이디어를 가지고 있다.

시각화 원칙과 학술 근거는 [좋은 시각화 원칙 조사](VisualizationPrinciples.md)에, 사용자 고충은 [Claude Code 실무 고충 조사](ClaudeCodePainPoints.md)에 있다. 관련 작업은 이슈 I29다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

## 1. 조사 방법과 한계

- 2026-11-01에 웹 조사 서브에이전트 둘이 범주별로 수집했고, 이 문서는 그 보고를 정리했다.
- 확인 방법은 출처 종류마다 다르다.
  - GitHub 저장소: API로 스타 수, 라이선스, 마지막 활동을 조회하고 README를 읽었다. 스타 수와 날짜는 2026-11-01 조회 값이며 바뀐다.
  - 논문: arXiv 초록 페이지를 열었다.
  - 상용 도구: 공식 문서를 열었다.
- 확인하지 못한 세부는 **[불확실]**로 표시했다. 논문에 인용하기 전에 원문을 다시 확인한다.
- 조사에서 빠진 것:
  - 시간 제약으로 공식 문서를 열지 않았다: Splunk, Axiom, Better Stack, Graylog, Zipkin, rr, LogRocket, LogLens
  - 로그인이 필요해 열지 못했다: Celonis
  - 저장소 정보만 확인했다: AgentOps, W&B Weave, Laminar, Helicone
- README에 적힌 기능은 직접 실행해 보지 않았다.

## 2. 비교 기준: AgentVis의 특징

| 항목 | AgentVis |
| --- | --- |
| 데이터 | Claude Code HTTP hook(실시간 신호)과 세션 기록 JSONL(주 내용)을 세션 단위로 병합. 서브에이전트 기록 연결, 백그라운드 작업과 완료 알림 연결([데이터 소스](../DataSource.md)) |
| 실행 위치 | 로컬(127.0.0.1의 FastAPI 서버, SQLite). 외부 전송 없음. macOS·Linux·Windows |
| 보기 | 프로젝트 → 세션 → 턴. 턴별 단계 목록과, 에이전트별 줄(주·서브·백그라운드)에 실행 구간 막대를 순서를 지키는 압축 시간축 위에 그린 흐름 그래프([작업 흐름 그래프 설계](../design/FlowGraph.md)) |
| 목적 | 2.0.0부터: 사용자의 지시가 틀렸을 때 에이전트의 대응을 보고 지시의 잘못을 찾도록 돕기([연구 설계 2](StudyDesign.md)). 1.x: [핵심 분석 질문](../ProductVision.md#2-핵심-분석-질문) Q1\~Q6(과정, 실패 위치, 실패 종류, 반복, 우회, 지시 오해)에 답하기 |
| 계획 | 2.0.0부터: 지시 패널, 규칙으로 찾은 신호 6종과 근거, 정상 작업 흐림·접기([지시 대조 보기 설계](../design/ReviewView.md)). 심은 오류로 정답을 만들고 검색되는 텍스트 기록 보기와 비교하는 유저 스터디. 1.x: 6가지 고충 판정, Claude Code 기본 UI와 비교하는 유저 스터디 |

## 3. 경쟁자: 코딩 에이전트 로그 시각화

### 3.1 비교표

| 이름 | 유형·라이선스 | 스타·최근 활동 | 데이터 | 로컬/클라우드 | 주요 보기 | 서브에이전트·병렬·백그라운드 | 실패·반복·우회·오해 | 실시간 | 사용자 평가 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **AgentVis** | 연구용 오픈소스 | – | hook + JSONL 병합 | 로컬 | 프로젝트·세션·턴, 단계 목록, 턴별 에이전트 줄 그래프(압축 시간축) | 셋 다. 사용자 끼어들기·문맥 압축 표시 | Q1\~Q6 목표, 판정 예정 | hook 기반(화면은 새로고침) | 예정 |
| agent-flow (patoles) | 오픈소스, Apache-2.0 | 약 1.75k, 2026-10-29 | Claude Code HTTP hook 서버 + JSONL, Codex 기록 | 로컬(VS Code 확장·웹) | 노드 그래프 캔버스, 타임라인, 대화 기록, 파일 주목도 히트맵 | 서브에이전트 분기. 백그라운드는 [불확실] | 없음 | 있음 | 없음 |
| zoetrope | 오픈소스, MIT | 약 1.13k, 2026-10-14 | JSONL(Claude Code, Codex) | 로컬 TUI + 브라우저 | 흐름 그래프(주 → 서브에이전트 → 도구), 스크럽 타임라인, 선택적 공백 압축 | 서브에이전트. 병렬·백그라운드는 [불확실] | 없음 | 있음(따라가기, 재생) | 없음 |
| claude-code-history-viewer | 오픈소스, MIT | 약 2.29k, 2026-10-31 | JSONL 등 여러 에이전트 | 로컬 데스크톱·웹 | 메시지, 분석, 토큰 통계, 최근 편집, 활동 타임라인 | 서브에이전트 세션과 비용 합산 | 없음 | 파일 감시 | 없음 |
| claude-code-hooks-multi-agent-observability (disler) | 오픈소스, 라이선스 표기 없음 | 약 1.56k, 2026-02-08 | hook 12종 → HTTP → SQLite → WebSocket | 로컬 | 이벤트 타임라인, 실시간 맥박 차트, 대화 기록 창, 필터 | 서브에이전트 시작·끝, 여러 에이전트 동시 | 없음 | 있음 | 없음 |
| claude-code-log | 오픈소스, MIT | 약 1.25k, 2026-10-09 | JSONL → HTML·MD | 로컬 | 대화 기록, 접기·필터, 확대 가능한 타임라인, TUI | 에이전트·분기 표시 | 없음 | 있음 | 없음 |
| sniffly (chiphuyen) | 오픈소스, MIT | 약 1.28k, 2025-08-08 | JSONL | 로컬(공유 선택) | 사용 통계, 오류 유형 분류, 지시 이력 | 없음 | 오류 유형 집계 | 없음 | 없음 |
| Claudoscope | 오픈소스, MIT, macOS | 약 268, 2026-10-26 | JSONL + 세션 등록부 + hook | 로컬 | 메뉴바, 세션 탐색, 타임라인, 비용, diff, 보안 | 서브에이전트 비용 | 오류 배지(사용량 한도, 도구 오류), 멈춤 구간 경고 | 있음 | 없음 |
| Coding Agent Visualizer | 오픈소스, MIT | 약 20, 2026-06-23 | JSONL(Claude Code, Codex, Gemini 등 7종) | 로컬 | 실행 그래프, 구간 waterfall, 토큰 flame, 타임라인, 파일 히트맵, 통계·비용, 세션 비교, 주석 | 서브에이전트 접기 | 없음(사람이 주석) | 실시간 꼬리 보기 | 없음 |
| ClaudeScope | 오픈소스, MIT | 약 21, 2026-09-03 | JSONL | 로컬(127.0.0.1) | Gantt 타임라인(사용자·생각·글·도구별 줄), 토큰 차트, 도구별 오류·지연, 이벤트 상세, HTML 보고서 | 언급 없음 | 도구 오류·미완료 호출 표시 | 없음 | 없음 |
| claude-hindsight | 오픈소스, MIT | 약 22, 2026-06-02 | JSONL + hook, 선택적 OTel | 로컬 | 대시보드 지표, 실행 목록·상세, 3D 그래프, 비용 | [불확실] | 오류 강조, 원인 노드 연결 | 있음 | 없음 |
| ccviz | 오픈소스, MIT | 약 1, 2026-06-09 | hook 4종 → SQLite | 로컬 | 사용자 메시지마다 DAG | 병렬 도구 호출을 나란히 | 없음 | 있음(2\~5초) | 없음 |
| Claude Code OpenTelemetry (Anthropic 공식) | 공식 기능 | – | OTel 지표·이벤트·트레이스(베타) | 수집처를 사용자가 지정 | 자체 화면 없음 | 서브에이전트 구간이 부모 아래 중첩 | 도구 결과 성공 여부, API 오류 이벤트 | 있음 | – |
| Agent View (Anthropic 공식, 2026-05 미리보기) | 공식 기능 | – | 내부 | CLI | 세션 목록, 상태, 마지막 턴 미리보기 | 백그라운드 세션 관리 | 상태만 | 있음 | – |
| Arize Phoenix + Claude Code 플러그인 | 오픈소스 플랫폼 + 플러그인 | 플러그인 약 25 | hook → OpenInference 구간 | 자체 호스팅 가능 | 턴별 트레이스 트리 | 서브에이전트 구간이 턴 아래 중첩 | 평가 기능 별도 | 있음 | – |
| Langfuse·LangSmith·Braintrust 연동 | 오픈소스·SaaS | Langfuse 약 36.8k | 턴이 끝날 때 hook에서 기록을 읽음 | Langfuse는 자체 호스팅, 나머지는 주로 클라우드 | 턴별 트레이스, 세션 묶음 | 공식 문서에 서브에이전트 언급 없음 | 플랫폼 평가 기능 | 턴이 끝난 뒤 | – |

### 3.2 학술 시스템

| 이름 | 출처 | 핵심 | 평가 |
| --- | --- | --- | --- |
| AgentStepper | arXiv 2602.06593 | 소프트웨어 개발 에이전트의 대화형 디버거(중단점, 한 단계씩 실행, 편집). 에이전트 코드에 계측 필요 | 12명 사용자 연구 |
| AGDebugger | CHI 2025, arXiv 2503.02068 | 다중 에이전트 대화의 개요와 메시지 수정 후 재실행 | 14명 사용자 연구 |
| AgentGUI | EMNLP 2026 데모, arXiv 2607.26300 | 오래 실행되는 여러 에이전트를 관찰하고 조종. 방향 이탈(drift) 방지 | 문제 식별 38% 빠름(p=0.023) |
| TraceView | arXiv 2606.22110 | 프로그램 수리 에이전트 궤적. 반복되거나 과제에서 벗어난 지점 진단 | 형성 연구 5명 |
| Graphectory Viewer | ASE 2026 도구, arXiv 2608.17195 | 단계를 인식하는 그래프와 Sankey 요약, 성공·실패 실행 비교 | 5명 피험자 내 비교, SWE-agent 뷰어 대비 [불확실] |
| Agent ATO | VISSOFT 2026 NIER, arXiv 2609.08301 | 콘솔 로그를 도구 유형별 타임라인으로 | 정식 평가 없음 |
| SeaView | arXiv 2504.08696 | 환경 실패와 에이전트 실수 구분, 실행 간 비교 | 사용자 연구. 참가자 수는 조사마다 다르게 보고됨 [불확실] |
| InconLens | arXiv 2603.28106 | 여러 실행을 정렬해 갈라지는 지점 탐지 | 사례 연구, 전문가 인터뷰 |
| AgentLens | IEEE TVCG 31(8), 2025. arXiv 2402.08995 | 다중 에이전트 사회 시뮬레이션(Reverie)의 행동 계층과 LLM 요약, 원인 추적([3.6절](#36-agentlens와의-차이)) | 14명, 재생 시스템 대비 |
| Signals | arXiv 2604.00356 | 오정렬·정체·실패·루프 신호 계산. 화면 없음, τ-bench 대상 | – |

**그 밖에 확인한 것**(표에서 뺌)
- opcode(Claudia, 약 22.4k): 세션 관리 GUI이고 시각화 도구가 아니다.
- claude-code-viewer(약 1.3k): 웹 기반 Claude Code 클라이언트다.
- OpenHands trajectory-visualizer: 내보낸 궤적을 타임라인으로 보여 주고 오류를 빨간색으로 표시한다.
- SWE-agent inspector: `.traj` 파일을 보여 주고 성공·실패를 표시한다.
- simonw/claude-code-transcripts(약 1.7k): 대화 기록을 내보내고 공유한다.
- ccusage(약 19.3k): 사용량 전용 도구다.
- Cursor, Aider, Cline, Amp, Gemini CLI, Codex: 자체 궤적 시각화 도구는 찾지 못했다. 위의 여러 에이전트용 뷰어가 이들의 로그를 읽는다.

### 3.3 가장 가까운 경쟁자와의 차이

| 경쟁자 | 같은 점 | 다른 점 |
| --- | --- | --- |
| agent-flow | hook과 JSONL을 함께 쓰는 로컬 실시간 웹, 서브에이전트 분기 그래프, 타임라인과 대화 기록 | 자유 배치 노드 캔버스다. 턴 단위 줄, 실행 시간 막대, 공백 압축, 백그라운드 작업 연결, 문맥 압축 표시가 없다. 실패·반복·우회·오해 분석이 없다. |
| ccviz | hook과 로컬 SQLite, 사용자 메시지마다 그래프, 병렬 호출을 나란히. 구조가 가장 비슷하다 | hook 4종만 쓰고 세션 기록을 병합하지 않는다. 서브에이전트·백그라운드 줄과 시간축이 없다. 실패 분석이 없고 초기 단계(스타 1)다. |
| disler multi-agent observability | hook → HTTP → SQLite → 실시간. 서브에이전트·문맥 압축 등 12종 이벤트 | 이벤트 흐름과 맥박 차트 위주의 모니터링이다. 턴 구조, 실행 구간 막대, 병렬 갈라짐·합류, 사후 분석(Q2\~Q6)이 없다. |
| zoetrope | JSONL로 주 → 서브에이전트 → 도구 흐름 그래프, 타임라인, 공백 압축 옵션 | TUI와 재생 애니메이션이 중심이다. hook을 쓰지 않고, 프로젝트 → 세션 → 턴 탐색과 실패 분석이 없다. |
| Coding Agent Visualizer, ClaudeScope | JSONL을 로컬 시간축 줄·waterfall·Gantt로. ClaudeScope는 도구별 오류·미완료 호출 표시(Q2 일부), CAV는 세션 비교와 주석 | 줄의 기준이 다르다. ClaudeScope는 이벤트 종류, CAV는 호출 깊이로 줄을 나누고 AgentVis는 에이전트별로 나눈다. hook 병합과 백그라운드 연결이 없다. Q3\~Q6 분석이 없다. |

### 3.4 AgentVis의 기여 공간

- **데이터 결합.** 확인한 도구 가운데 다음 셋을 함께 갖춘 것은 없었다.
  - hook과 세션 기록의 병합
  - 백그라운드 작업과 완료 알림의 연결
  - 턴 단위 에이전트별 줄에 순서를 지키는 공백 압축
- **분석.** 실패의 종류, 반복, 우회, 지시 오해, 근거 없는 성공 보고, 테스트 변조를 판정해 보여 주는 오픈소스·상용 도구는 찾지 못했다.
  - 가장 가까운 연구는 Signals다. 신호는 계산하지만 화면이 없다.
  - TraceView는 반복과 과제 이탈 진단을 목표로 한다.
- **평가.** 사용자 연구를 한 것은 모두 논문이고 대상도 달랐다.
  - AgentStepper, AGDebugger, AgentGUI, TraceView, Graphectory Viewer는 직접 만든 에이전트나 벤치마크 실행을 대상으로 했다.
  - **Claude Code 실사용 로그를 대상으로 기본 UI와 비교한 통제 연구는 찾지 못했다.** 이것이 논문의 기여 공간이다.
- **2.0.0의 기여 공간.** 위 셋은 1.x(I29) 기준이다. 연구 설계 2(I62) 뒤의 기여는 [연구 설계 2의 내세울 기여](StudyDesign.md#2-학회-기준에서-본-좋은-연구의-조건)에 있다. 사용자 지시에서 시작한 오류를 사람이 알아보는지 잰 시각화 연구는 찾지 못했다. 가장 가까운 선례와의 차이는 [3.6절](#36-agentlens와의-차이)에 있다.
- **중첩되는 부분.** 서브에이전트 그래프와 시간축 보기는 이미 여러 도구에 있다. 논문에서는 시각화 형태 자체보다 **질문(Q1\~Q6)과 고충에 맞춘 선별, 그리고 그 효과의 실증**을 기여로 내세운다.

### 3.5 경쟁자에게 있고 AgentVis에 없는 기능

| 기능 | 갖춘 도구 | AgentVis 판단 |
| --- | --- | --- |
| 토큰·비용 분석 | CAV, ClaudeScope, hindsight, history-viewer, Claudoscope, ccusage | 고충 조사에서 비용은 시각화보다 요금 문제에 가깝다고 보았다([고충 L](ClaudeCodePainPoints.md#2-고충-분류)). 유저 스터디 범위 밖이며, 필요하면 나중에 넣는다. |
| 세션 간 집계 대시보드, 도구별 통계 | ClaudeScope, sniffly, hindsight | Q3(실패 종류)에 필요하다. 개요 화면에 넣을 후보다. |
| 전문 검색 | CAV, history-viewer | 유저 스터디의 공정성(기준선에도 검색이 있다)과 실제 사용에 필요하다. 넣을 후보다. |
| 두 실행 비교, 갈라지는 지점 정렬 | CAV, SeaView, InconLens, Graphectory | 같은 과제의 여러 실행이 있을 때 의미가 있다. 유저 스터디의 시나리오 설계와 함께 판단한다. |
| 공유·내보내기(민감정보 제거) | ClaudeScope, claude-code-log, claude-code-transcripts | 논문 그림과 참가자 데이터 관리(IRB)에 필요할 수 있다. 민감정보 제거가 전제다. |
| 편집 diff, 파일 히트맵 | CAV, agent-flow, Claudoscope | 고충 "무엇을 했는지 파악"·"읽지 않고 편집"에 직접 쓰인다. 넣을 후보다. |
| 사람이 다는 주석 | CAV, TraceView | Q6("여기서부터 오해") 표시와 정답 주석에 쓸 수 있다. 넣을 후보다. |
| 여러 에이전트 지원 | CAV, zoetrope, agent-flow, history-viewer | 범위 밖. Claude Code에 집중한다. |
| 재생·스크러빙 | zoetrope | 우선순위 낮음. |
| OTel 내보내기 | hindsight, Phoenix, Langfuse | 범위 밖. |
| 개입·조종(중단점, 재실행) | AgentStepper, AGDebugger, AgentGUI | 범위 밖. AgentVis는 관찰 도구다. |

### 3.6 AgentLens와의 차이

AgentLens는 TVCG에 실린 가장 가까운 선례다. 그래서 논문에서 차이를 가장 분명히 써야 한다. 이 절은 2026-11-16에 원문(arXiv:2402.08995 HTML 본문, 부록 없음)을 읽고 정리했다. 비교의 기준은 2.0.0 연구 설계([연구 설계 2](StudyDesign.md))와 화면([지시 대조 보기 설계](../design/ReviewView.md))이다.

**AgentLens가 하는 것** (원문 확인)

- **대상**: LLM 기반 자율 시스템(LLMAS)이다. 평가와 사례는 LLM 에이전트 25개가 사는 사회 시뮬레이션 Reverie 하나다. 다른 LLMAS로 일반화된다고 주장하지만 시험하지는 않았다. 코딩 에이전트는 관련 연구(ChatDev, MetaGPT)에서만 언급한다.
- **데이터**: 사용자가 LLMAS에 기록 코드를 넣어 원시 이벤트를 모은다. 이벤트를 네 층(시스템 상태, 에이전트, 과업, 동작)으로 나눈다. 과업은 지각·생각·행동, 동작은 환경·기억·결정으로 나눈다. "행동"은 한 에이전트가 시간 구간 동안 한 동작의 묶음이다.
- **LLM의 역할**: 따로 둔 요약 LLM이 시점마다 이벤트를 짧은 글과 이모지로 요약한다. 요약을 임베딩하고 변화점 탐지(WIN, 코사인 거리)로 에이전트마다 시간축을 구간으로 나눈다. 구간 나누기는 LLM이 아니라 변화점 탐지가 한다.
- **화면**: 연동된 보기 셋이다.
  - 개요 보기: 에이전트마다 위치의 시간 변화를 색 곡선으로 그리고, 만남을 음영으로 칠한다. 기억 검색 결과를 시점에 강조한다.
  - 에이전트 보기: 특성, 요약·과업·동작을 펼치는 시간축, LLM 결정의 문맥, 시간축 전체의 원인 연결을 보이는 미니맵.
  - 모니터 보기: 시뮬레이션 지도의 재생. 확대와 빨리 감기가 된다.
- **원인 추적**: 명시 원인(기록에 남은 기억 색인)과 암묵 원인(동작 기록 사이의 글 유사도가 임계값 δ를 넘으면 행동 단위로 연결)이다.
- **유저 스터디**: 지역 대학 참가자 14명(컴퓨터과학·소프트웨어공학·사회학 학생 위주, 일부는 LLMAS 개발자)이다.
  - 기준선: 평면 지도 재생과 텍스트 설명·기록(기존 LLMAS 시각화와 같은 형태).
  - 과업: 개별 행동 분석 T1\~T6, 창발 현상(화제 전파, 모임, 예상 밖 행동) T7\~T9.
  - 결과: 개별 과업의 정확도와 시간 모두 유의하게 나아졌다(둘 다 p = 1.2e-3). 시간은 T3에서 78.3%(20.00초 대 92.20초), T6에서 71.6%(51.29초 대 180.67초) 줄었다. T6에서 기준선 참가자의 42% 넘게 실패했다. SUS 평균 67.5였다.
  - 설계 요구는 8명의 인터뷰와 소리 내어 생각하기에서 나왔다.
- **저자가 밝힌 한계**: 개요 보기의 배치를 미리 계산해 에이전트와 시간이 늘면 선이 교차한다. 구간의 잘게 나누는 정도와 유사도 임계값을 사용자가 바꿀 수 없다. 계획·기억 전략의 분석은 아직 없다. 글만 다룬다. 참가자들은 자동 안내를 더 원했다.

**비교**

| 측면 | AgentLens | AgentVis 2.0.0 |
| --- | --- | --- |
| 대상 | 사람 개입 없이 돌아가는 다중 에이전트 사회 시뮬레이션(Reverie, 25개) | 사람 한 명이 지시하는 코딩 에이전트(Claude Code, 서브에이전트 포함)의 세션 |
| 문제의 출발점 | 에이전트의 행동과 창발 현상을 이해하기 | **사용자의 지시가 틀렸을 때**, 에이전트의 대응을 보고 지시의 잘못을 찾기 |
| 데이터 수집 | 대상 시스템에 기록 코드를 넣는다 | 계측 없이 공식 hook과 세션 기록 JSONL을 병합한다 |
| 화면의 축 | 시간과 에이전트(위치 곡선, 시간축) | **지시 문장**. 신호와 근거가 지시 문장을 가리킨다 |
| 정보 줄이기 | LLM 요약과 변화점 구간으로 계층을 만든다 | 정상 작업을 흐리고 접는다. 드문 사건(신호)을 따로 모아 앞에 낸다 |
| 자동 분석 | LLM 요약, 글 유사도의 암묵 원인. 추정임을 따로 표시하지 않는다 | 규칙으로 찾은 신호 6종. "추정" 표지와 근거 원문을 함께 보이고 결론을 쓰지 않는다. LLM 신호는 조건을 갖춘 뒤의 후보다([시각화 원칙 조사 13절](VisualizationPrinciples.md#13-200-화면에-적용할-지침-i66)) |
| 연결의 뜻 | 원인(무엇이 이 행동을 불렀나) | 대조(지시의 어느 문장과 기록의 어느 증거가 어긋나나) |
| 기준선 | 평면 지도 재생과 텍스트 기록 | 검색과 접기가 되는 텍스트 기록 보기(같은 정보) |
| 과업 | 개별 행동 분석, 창발 현상 설명 | 대응 파악(U1), 지시 오류 진단(U2), 교정 결정(U3) |
| 정답 | 과업별 정답(만드는 방법은 본문에서 자세히 확인하지 못했다) | **심은 오류**(재현 조건 누락·왜곡, 원인·위치 오도, 모순 요구)와 오류 없는 통제 시행 |
| 측정 | 정확도, 시간, SUS, 질적 의견 | 정확도, 시간, 신호 탐지 지표(적중·오경보, d′), NASA-TLX, SUS, 화면 사용 기록 |

**겹치는 것과 배울 것**

- 목표가 같다. 둘 다 원시 기록의 정보 밀도를 낮춰 볼 곳을 알려 주려 한다. 방법(요약 계층 대 흐림·접기와 신호)이 다르다.
- 원인 연결 미니맵(에이전트 보기)은 신호 미니맵 후보([13.2의 3](VisualizationPrinciples.md#132-화면-개선-후보-우선순위-순))의 선례다.
- 고정 임계값을 사용자가 바꿀 수 없다는 한계는, 신호 종류마다 정밀도를 보이자는 후보([13.2의 2](VisualizationPrinciples.md#132-화면-개선-후보-우선순위-순))와 같은 문제다. 우리는 규칙의 정밀도를 재서 보인다.
- 참가자가 자동 안내를 더 원했다는 결과는 신호 목록을 두는 근거의 하나다.
- 개요 보기의 선 교차는 우리 흐름 그래프의 화살촉·교차 줄이기 후보([13.2의 15](VisualizationPrinciples.md#132-화면-개선-후보-우선순위-순))와 같은 문제다.
- SUS 67.5를 우리 SUS의 비교 기준으로 쓸 수 있다([시각화 원칙 조사 7절](VisualizationPrinciples.md#7-유저-스터디-설계)).

**논문에 쓸 차이**

1. **문제**: AgentLens는 자율 시스템에서 에이전트가 무엇을 했는지 이해하도록 돕는다. 우리는 사람-에이전트 코딩에서 **사람의 지시에서 시작한 오류**를 사람이 알아보도록 돕는다. 오류의 출처가 사람이라는 점은 AgentLens를 포함해 확인한 시각화 연구에 없었다.
2. **설계**: 시간·에이전트 축 대신 지시 문장을 축으로 두고, 기록과 지시의 어긋남을 규칙으로 찾아 근거와 함께 보인다. 정상 작업은 지우지 않고 뒤로 보낸다.
3. **평가**: 심은 오류로 객관적 정답을 만들고, 오류 없는 통제 시행으로 오경보까지 잰다. AgentLens의 원문에는 오경보 측정이 없다.

## 4. 배울 점: 잘 만든 일반 로그 시각화

### 4.1 도구별 아이디어

| 도구 | 분류 | 대표 설계 아이디어 | AgentVis에 옮길 화면 요소 | 답하는 질문 |
| --- | --- | --- | --- | --- |
| Grafana Explore(Loki) | 로그 탐색 | 수준별로 칠한 로그 양 막대, 같은 줄 묶기(숫자를 지우고 모양만 비교), 한 줄의 앞뒤 문맥, 양·패턴으로 내려가기 | 세션 위 시간 구간별 이벤트 수 막대(성공·실패·사용자 끼어들기 색 구분), "같은 명령 접기"와 ×N | 개요, 반복 |
| Kibana·Elastic AIOps | 로그 탐색 | 급변 구간과 기준 구간을 골라 유의하게 다른 필드·값 순위, 메시지 범주와 분포, 변화점 | 실패가 몰린 구간을 고르면 그 구간에 많은 도구·파일·인자 순위, 오류 메시지 범주 목록 | 실패 위치, 반복 |
| Datadog Log Explorer | 로그 탐색 | 메시지 패턴 묶기와 변하는 부분 강조·분포 미리보기, 오류 이상치·새 패턴을 알리는 배너(Watchdog Insights) | 오류 패턴의 변하는 부분(파일명, 종료 코드)만 강조, 세션을 열면 "새 오류 유형 2, 반복 실패 1" 배너 | 반복, 실패 위치, 개요 |
| Honeycomb BubbleUp | 이상치 분석 | 고른 영역과 나머지를 필드별 분포로 비교 | 실패한 호출(또는 고른 구간)과 나머지의 도구·명령·폴더·직전 행동 분포 비교 패널 | 실패 위치, 오해 |
| Honeycomb Traces | 트레이스 | 오류 구간 수와 그 사이 이동, 깊이별 접기, 검색 일치 수와 이전·다음 | `실패 7 ◀ ▶` 배지, 서브에이전트 깊이별 접기, 검색 일치 강조 | 실패 위치 |
| Jaeger | 트레이스 | 트레이스 요약과 축소 지도, 핵심 경로(critical path) 강조, 두 트레이스의 구조 비교 | 세션 전체 축소 지도, 최종 결과까지의 결정 경로 강조, 같은 과제의 두 세션 비교 | 개요, 오해 |
| Perfetto | 트레이스 | 영역 선택, 중요한 줄 위쪽 고정, 명령 팔레트·키보드 이동 | "사용자 메시지"·"실패" 줄 고정, 키보드 이동 | 개요, 실패 위치 |
| Chrome DevTools Performance | 프로파일러 | 위쪽 개요를 끌어 범위 선택(확대 단계는 경로 표시로), 아래 집계가 그 범위만 반영, 기준을 넘는 부분만 빨갛게 | 개요에서 고른 범위로 아래 목록·집계를 좁힘, 오래 걸린 호출은 넘은 부분만 강조 | 개요, 실패 위치 |
| Speedscope | 프로파일러 | 같은 데이터를 시간순·같은 경로 합치기·함수 표 세 보기로 | "시간순 / 같은 행동 합치기 / 행동별 표" 보기 전환 | 개요, 반복 |
| Flame graph(Gregg) | 프로파일러 | 같은 경로를 합쳐 폭으로 빈도 표현, 두 프로파일 차이 | "지시 → 서브에이전트 → 도구 → 명령" 빈도 그림으로 노력이 몰린 곳 표시 | 개요, 반복 |
| Firefox Profiler | 프로파일러 | 되돌릴 수 있는 변환 쌓기(합치기, 집중, 접기, 버리기) | "이 서브에이전트에 집중", "재시도 묶음 접기", "읽기 계열 합치기" 변환과 그 경로 표시 | 반복, 개요 |
| lnav | 터미널 로그 | `e`·`E`로 오류 사이 이동, 북마크와 그 사이 이동, 히스토그램 전환, 포함·제외 필터 | 키보드만으로 실패·사용자 끼어들기·북마크 사이 이동 | 실패 위치 |
| Seq | 로그 서버 | 저장한 필터(Signals)를 켜고 끄며 AND로 결합, 공유 | "실패", "재시도", "근거 없는 완료 주장", "사용자 정정" 신호 칩 | 전체 |
| Sentry Issues | 오류 추적 | 지문(fingerprint)으로 같은 오류를 이슈 하나로 묶고 횟수·처음·마지막 | 실패를 "도구 + 정규화한 오류"로 묶어 횟수와 처음·마지막 위치 | 반복 |
| Sentry Breadcrumbs·Replay | 오류·세션 | 오류 직전 행동 흔적, 재생 타임라인 위 오류·행동 표식과 동기화된 목록 | 실패 카드에 직전 5\~10개 단계, 아래 스크러버에 실패·끼어들기 표식 | 실패 위치, 우회 |
| Disco | 프로세스 마이닝 | 이벤트 로그에서 프로세스 지도 자동 생성(빈도·반복·시간), 단순화 슬라이더, 같은 순서를 변형(variant)으로 묶기 | 도구 전이 지도(Edit → 테스트 → Edit 루프가 굵은 순환 간선), 드문 경로 숨기기 | 반복, 우회, 개요 |
| LifeFlow, EventFlow | 연구 | 많은 시퀀스를 한 개요로 요약, 기준 사건 정렬, 사용자 주도 단순화 | 여러 세션을 "첫 실패"나 "사용자 정정" 시점에 정렬해 앞뒤 순서 집계 | 오해, 우회 |
| Sequence Synopsis | 연구 | 시퀀스를 묶어 대표 패턴과 차이로 요약 | 반복 시도를 대표 패턴과 차이로 압축("테스트 실패 ×5, 매번 다른 파일만 수정") | 반복, 개요 |

### 4.2 옮길 아이디어 상위 10개

조사 보고가 제안한 순서다. 실제 반영은 화면 재설계에서 [시각화 원칙 조사의 설계 지침](VisualizationPrinciples.md#6-agentvis-설계-지침)과 함께 정한다.

1. **실패 개수 배지와 다음·이전 이동**(Honeycomb, lnav)
   - 도구 막대에 `실패 7 ◀ ▶`, `사용자 개입 3 ◀ ▶`를 둔다.
   - 키를 누르면 목록과 그래프가 함께 그 위치로 간다.
   - 실패가 3%인 세션에서 Q2에 가장 짧게 답한다.
2. **오류 서명별 묶음과 횟수**(Sentry, Datadog, Grafana)
   - "문제" 칸에 `Bash · pytest · AssertionError ×4 (처음 12:03, 마지막 12:19)` 같은 줄을 둔다.
   - 변하는 부분만 강조한다. 이것이 Q4의 답이다.
3. **세션 개요 막대 → 범위 선택 → 아래 집계 연동**(Grafana, Chrome DevTools, Perfetto)
   - 정상은 회색, 실패는 빨강, 사용자 메시지는 세로선으로 그린 얇은 막대를 둔다.
   - 끌어서 고른 범위로 아래가 좁혀진다.
   - "전부 보여 주기" 대신 "어디를 볼지 고르기"로 들어가는 입구다.
4. **재시도 루프 접기**(Firefox Profiler, Speedscope, Sequence Synopsis)
   - 비슷한 Edit → 테스트 실패 주기를 `재시도 루프 ×5 (4분 12초) → 결국 실패`처럼 한 줄로 접는다.
   - 펼치면 시도마다 달라진 부분만 보인다.
5. **실패 직전 흔적**(Sentry, Grafana): 실패 카드에 직전 지시 → 계획 → 도구 호출을 붙인다. 원인과 오해의 시작점(Q6)을 찾을 때 쓴다.
6. **도구 전이 지도**(Disco)
   - 간선의 굵기는 전이 횟수, 노드의 색은 실패율이다.
   - 루프는 순환 간선으로, 우회(Q5)는 "실패 노드 → 다른 도구" 간선으로 드러난다.
   - 조사자 판단이며 문서 근거는 아니다: 한 세션 안에서는 전이 지도만 유효하다. 변형(variant) 분석은 같은 과제를 여러 번 돌린 세션 묶음이 있을 때만 의미가 있고, 행동 이름을 거칠게 추상화하지 않으면 변형이 대부분 1건이 된다.
7. **고정 줄과 신호 칩**(Perfetto, Seq): "사용자 메시지·정정", "실패", "완료 주장" 줄을 위에 고정하고, 신호 칩을 켜고 끄며 결합한다.
8. **선택 대 기준 비교 칸**(Honeycomb BubbleUp, Elastic, Datadog): 실패한 호출과 나머지의 분포를 비교해 "왜 여기서만 실패하나"의 가설을 준다.
9. **자동 요약 배너**(Datadog Watchdog Insights)
   - 세션을 열면 "실패 후 같은 명령 재실행 4회", "마지막 완료 주장 이후 테스트 실행 없음" 같은 카드 2\~3개를 띄운다.
   - 근거 없는 성공 보고(고충 B)의 입구가 된다.
10. **핵심 경로와 축소 지도, 두 세션 구조 비교**(Jaeger)
    - 최종 결과에 기여한 경로만 진하게, 막다른 시도는 흐리게 그린다.
    - 같은 과제의 성공·실패 세션을 겹쳐 보인다.

**공통 구조.** 잘 만든 도구들은 모두 **집계 → 선택 → 원본**의 세 층을 따른다. AgentVis의 기본 화면은 다음 세 가지로 하고, 지금의 단계 목록과 흐름 그래프는 그 아래 원본 층으로 내린다.
- 개요 막대
- 문제 칸(서명별 묶음)
- 이동 배지

## 5. 앞선 조사와 달라진 점

- **AgentLens의 게재처.** 앞선 조사에서는 TVCG 게재가 [불확실]이었고, 이번 조사는 "TVCG 2024"로 보고했다. 2026-11-01에 사용자가 IEEE Computer Society 디지털 도서관의 게재 페이지(https://www.computer.org/csdl/journal/tg/2025/08/10520238/1WDYcwmHhvO)로 **IEEE TVCG 게재를 확인**했다. 그 페이지 주소에 따르면 2025년 8호(31권)다. 두 조사 문서를 모두 고쳤다.
- **SeaView의 참가자 수.** 앞선 조사는 10명으로, 이번 조사는 밝히지 않았다고 보고했다. 논문 인용 전에 원문을 확인한다.
- **Claude Code 전용 도구.** 앞선 조사는 ClaudeScope와 Coding Agent Visualizer 둘만 찾았다. 이번에 더 많은 사용자를 가진 도구(agent-flow, zoetrope, claude-code-history-viewer, disler, claude-code-log, sniffly)를 찾았다. "전부 보여 주기 계열이며 사용자 평가가 없다"는 결론은 같다.

## 6. 출처

**Claude Code·코딩 에이전트 도구**
- https://github.com/patoles/agent-flow
- https://github.com/furkankly/zoetrope
- https://github.com/everettjf/coding-agent-visualizer
- https://github.com/Liuziyu77/ClaudeScope
- https://github.com/disler/claude-code-hooks-multi-agent-observability
- https://github.com/mshubian/ccviz
- https://github.com/Codestz/claude-hindsight
- https://github.com/chiphuyen/sniffly
- https://github.com/jhlee0409/claude-code-history-viewer
- https://github.com/cordwainersmith/Claudoscope
- https://github.com/daaain/claude-code-log
- https://github.com/d-kimuson/claude-code-viewer
- https://github.com/simonw/claude-code-transcripts
- https://github.com/ccusage/ccusage
- https://github.com/winfunc/opcode
- https://github.com/OpenHands/trajectory-visualizer
- https://swe-agent.com/latest/usage/inspector/

**공식 기능과 관측 플랫폼**
- https://code.claude.com/docs/en/monitoring-usage
- https://claude.com/blog/agent-view-in-claude-code
- https://arize.com/docs/phoenix/integrations/coding-agents/claude-code
- https://langfuse.com/integrations/developer-tools/claude-code
- https://docs.langchain.com/langsmith/trace-claude-code
- https://github.com/braintrustdata/braintrust-claude-plugin
- https://docs.laminar.sh/tracing/integrations/claude-agent-sdk

**학술 시스템**
- AgentStepper https://arxiv.org/abs/2602.06593
- AGDebugger https://arxiv.org/abs/2503.02068
- AgentGUI https://arxiv.org/abs/2607.26300
- TraceView https://arxiv.org/abs/2606.22110
- Graphectory Viewer https://arxiv.org/abs/2608.17195
- Agent ATO https://arxiv.org/abs/2609.08301
- SeaView https://arxiv.org/abs/2504.08696
- InconLens https://arxiv.org/abs/2603.28106
- AgentLens https://www.computer.org/csdl/journal/tg/2025/08/10520238/1WDYcwmHhvO (IEEE TVCG), https://arxiv.org/abs/2402.08995
- Signals https://arxiv.org/abs/2604.00356

**일반 로그·트레이스·이벤트 시각화**
- Grafana Logs Drilldown https://grafana.com/docs/grafana/latest/explore/simplified-exploration/logs/
- Grafana Explore 로그 https://grafana.com/docs/grafana/latest/explore/logs-integration/
- Elastic AIOps https://www.elastic.co/docs/explore-analyze/machine-learning/machine-learning-in-kibana/xpack-ml-aiops
- Datadog Log Patterns https://docs.datadoghq.com/logs/explorer/analytics/patterns/
- Datadog Watchdog Insights https://docs.datadoghq.com/logs/explorer/watchdog_insights/
- Honeycomb BubbleUp https://docs.honeycomb.io/investigate/analyze/identify-outliers/
- Honeycomb 트레이스 https://docs.honeycomb.io/investigate/analyze/explore-traces/
- Jaeger UI https://www.jaegertracing.io/docs/latest/frontend-ui/
- Jaeger 트레이스 비교 https://github.com/jaegertracing/jaeger-ui/pull/276
- Perfetto UI https://perfetto.dev/docs/visualization/perfetto-ui
- Chrome DevTools Performance https://developer.chrome.com/docs/devtools/performance/reference
- Speedscope https://github.com/jlfwong/speedscope
- Flame Graphs https://www.brendangregg.com/flamegraphs.html
- Firefox Profiler 변환 https://github.com/firefox-devtools/profiler/blob/main/docs-user/guide-filtering-call-trees.md
- lnav https://lnav.org/features, https://docs.lnav.org/en/latest/hotkeys.html
- Seq Signals https://datalust.co/docs/signals
- Sentry 묶기 https://docs.sentry.io/concepts/data-management/event-grouping/
- Sentry Breadcrumbs https://docs.sentry.io/platforms/python/enriching-events/breadcrumbs/
- Sentry Replay https://docs.sentry.io/product/explore/session-replay/replay-details/
- Disco https://fluxicon.com/disco/
- LifeFlow https://www.cs.umd.edu/hcil/lifeflow/
- EventFlow https://www.cs.umd.edu/~ben/Monroe2013Temporal.pdf
- Sequence Synopsis https://lliquid.github.io/homepage/files/ss_vast17.pdf
- 요약 기법 비교 평가 https://arxiv.org/pdf/2306.02489
