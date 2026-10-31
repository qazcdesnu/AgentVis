# 좋은 시각화 원칙 조사

이 문서는 AgentVis 화면 설계와 유저 스터디 설계의 근거를 모은다. 다루는 내용은 다음과 같다.

- 시각화가 왜 필요한지
- 좋은 시각화 원칙
- 같은 분야의 시스템과 연구
- CHI 형식 시각화 논문의 유저 스터디 설계

[제품 비전의 연구 목적](../ProductVision.md#1-목적) 가운데 "시각화가 필요한 이유", "이해하기 쉬운 시각화", "유저 스터디"에 대응한다. 사용자가 실제로 겪는 고충은 [Claude Code 바이브 코딩 실무 고충 조사](ClaudeCodePainPoints.md)에 있다. 관련 작업은 이슈 I25다. 전체 문서 목록은 [문서 인덱스](../index.md)에서 확인한다.

## 1. 조사 방법과 한계

- 2026-10-31에 웹 조사 서브에이전트가 수집했고, 이 문서는 그 보고를 정리했다.
- 출처의 존재와 서지는 웹 검색으로 확인했다. 확인 수준은 출처마다 다르다.
  - **본문 확인:** AgentLens, AgentStepper, TraceView, SeaView, AGDebugger. AgentStepper와 TraceView는 요약 사이트를 거쳐 확인했다.
  - **초록·서지 확인:** 나머지 출처.
- 확인하지 못한 세부에는 **[불확실]**을 붙였다. 논문에 인용하기 전에 원문으로 다시 확인한다.
- 같은 이름의 논문이 없어 인용하지 않은 것: "Watch Me Think".

## 2. 시각화가 필요한 이유

### 2.1 이론: 외부 인지와 계산 효율

- **같은 정보라도 다이어그램이 문장보다 계산 효율이 높을 수 있다.** 다이어그램은 정보를 위치로 색인해 찾는 비용을 줄인다. 관련된 요소가 공간적으로 붙어 있어서 추론이 지각으로 바뀐다(Larkin & Simon 1987).
- **외부 표상은 작업 기억의 부담을 덜어 준다.** 계산을 밖으로 넘기고, 문제를 다시 표상하고, 그래픽 제약을 활용하는 방식으로 작동한다(Scaife & Rogers 1996).
- **시각화는 인지를 증폭한다.** 기억·처리 자원을 늘리고, 찾는 일을 줄이며, 패턴 탐지와 지각적 추론을 돕는다(Card, Mackinlay & Shneiderman 1999). 기제의 정확한 문구는 [불확실]이다.

**AgentVis에 대한 논거.** Claude Code의 대화 화면과 세션 기록은 전형적인 문장형 표상이다. 실패 위치(Q2), 같은 실패의 반복(Q4), 실패 뒤의 우회(Q5)를 찾으려면 수백 줄을 기억하며 훑어야 한다. 시각화는 이것을 두 가지 방식으로 바꾼다.
- 시간과 줄 위치로 정보를 색인하고 실패를 눈에 띄게 하면, "기억하며 찾는 일"이 "보는 일"로 바뀐다.
- 여러 턴과 세션에 걸친 패턴(Q3, Q4)은 작업 기억 용량을 넘는다. 외부 표상이 이 부분을 맡는다.

### 2.2 같은 분야 사용자가 보고한 난점

- **긴 기록에서 오류 위치 찾기.** AGDebugger(CHI 2025)의 형성 인터뷰에서 에이전트 개발자 5명이 핵심 난점으로 "긴 에이전트 대화를 검토해 오류 위치를 찾는 것"을 꼽았다.
- **커뮤니티의 같은 목소리.** Claude Code 커뮤니티도 같은 난점을 말한다. 무엇을 읽고 했는지 보이지 않는다는 불만이 있고, 압축 전 대화를 보려면 세션 기록(JSONL)을 직접 해석하는 수밖에 없다는 불만도 있다([고충 조사의 D·E](ClaudeCodePainPoints.md#2-고충-분류)).
- **긴 이벤트 시퀀스는 나열로는 읽기 어렵다.** 시퀀스가 많거나 길면 개별 기록을 나열하는 방식으로는 공통 경로와 예외를 찾기 어렵다. 그래서 집계와 단순화가 필요하다(LifeFlow, Malik et al., [4.8절](#48-긴-이벤트-시퀀스의-집계와-단순화)).

### 2.3 텍스트·로그 조건과 비교한 실증 연구

| 연구 | 비교 | 결과 |
| --- | --- | --- |
| Cornelissen, Zaidman & van Deursen (IEEE TSE 2011) | Eclipse 대 Eclipse + 실행 트레이스 시각화(EXTRAVIS), 대표 이해 과업 8개 | 시간 22% 단축, 정답률 43% 증가(둘 다 유의) |
| Beschastnikh et al., ShiViz (ACM TOSEM 2020) | 분산 시스템 로그 대 시공간 다이어그램, 학생 109명(통제 실험 39명) | 시스템 이해 질문의 정답이 유의하게 많고 효과 크기가 매우 컸다 |
| Ko & Myers, Whyline (CHI 2004) | 도구 유무, 소규모 | 디버깅 시간이 약 1/8로 줄었다. 수치는 2차 자료로만 확인했다 [불확실] |
| AgentLens (arXiv:2402.08995) | 기본 재생 시스템, 14명 | 정확도와 시간 모두 유의하게 개선, 시간 33~78% 단축 |
| AgentStepper (arXiv:2602.06593) | 편집기에서 원시 로그 열람, 12명 | 버그 식별 17% → 60%(유의), NASA-TLX 좌절감 5.4 → 2.4. 궤적 이해 점수는 64% → 67%로 거의 같았다 |
| EvalLM (CHI 2024) | 수동 평가, 12명 | 검토한 출력 2배, 프롬프트 수정 59% 감소. 시각화 도구는 아니지만 LLM 결과물을 원시 형태로 검토하는 조건을 기준선으로 삼은 CHI 사례 |

**종합.** 실행 트레이스, 분산 로그, LLM 에이전트 궤적 모두에서 시각화가 텍스트·로그 조건보다 정확도나 시간을 개선했다. 다만 효과는 과업 유형에 따라 다르다. AgentStepper에서 보듯 **실패를 찾는 과업에서는 크고, 일반적인 이해 과업에서는 작을 수 있다.** 그래서 논문의 가설은 "Q2·Q4·Q5처럼 위치를 찾고 비교하는 과업에서 이득이 크다"처럼 좁게 세운다.

**자동 판정만으로는 부족한 이유.** 다중 에이전트 실행에서 결정적 오류 단계를 자동으로 찾는 최고 방법의 정확도는 14.2%였다(Who&When, ICML 2025). "어디서부터 틀렸나"(Q6)는 아직 자동으로 답하기 어렵다. 따라서 사람이 보고 판단하도록 돕는 시각화가 필요하다.

## 3. AgentVis에 맞춘 해석: 질문과 화면 요소 짝짓기

Munzner의 중첩 모델과 과업 추상화([4.2절](#42-중첩-모델과-과업-추상화))에 따르면, 화면 요소는 어떤 과업(질문)에 답하는지 짝지어야 한다. 짝이 없는 요소는 기본 화면에서 빼고 상세 보기로 옮긴다. 사용자가 받은 "모든 것을 시각화했다"는 인상은 이 추상화 단계가 빠졌다는 신호다. 이 짝짓기 표는 화면 개선 설계에서 만들며, 유저 스터디의 과업 목록으로도 그대로 쓴다.

## 4. 좋은 시각화 원칙

### 4.1 개요 먼저, 확대·걸러 보기, 필요할 때 상세

- **원칙.** 인터페이스는 "Overview first, zoom and filter, then details-on-demand" 순서로 움직인다. 이 밖의 과업으로 relate(관계 보기), history, extract가 있다(Shneiderman 1996).
- **AgentVis.** 지금은 턴 하나를 열면 모든 막대가 같은 무게로 그려져 개요 단계가 없다.
  - 세션 단위 개요를 둔다. 턴마다 단계 수, 실패, 재시도를 보여 준다.
  - 원문은 누를 때만 보여 준다.
  - relate는 같은 실패의 반복을 서로 잇는 것(Q4)에 대응한다.

### 4.2 중첩 모델과 과업 추상화

- **원칙.** 설계는 네 단계로 나뉜다: 도메인 상황, 데이터·과업 추상화, 인코딩·상호작용, 알고리즘. 단계마다 실패하는 방식과 검증 방법이 다르다(Munzner 2009). 과업은 why·what·how로 서술한다(Brehmer & Munzner 2013).
- **AgentVis.** 각 질문을 why·what·how로 다시 정의한다. 예를 들어 Q2는 why가 "위치 찾기", what이 "실패 단계", how가 "상태 색과 걸러 보기"다. 이 정의는 [3절](#3-agentvis에-맞춘-해석-질문과-화면-요소-짝짓기)의 짝짓기 표로 이어진다.

### 4.3 데이터-잉크, small multiples, sparkline

- **원칙.** 데이터를 나타내지 않는 잉크는 지운다. 같은 틀을 반복하는 small multiples는 비교를 쉽게 하고, 단어 크기의 sparkline은 맥락을 준다(Tufte 1983, 2006). 책 원문이 아니라 2차 요약으로 확인했다 [불확실].
- **AgentVis.**
  - 턴 목록의 각 행에 sparkline을 넣는다. 단계 순서, 도구, 성공·실패를 보여 주는 작은 띠다.
  - 성공한 Read·Grep처럼 반복되는 막대는 회색으로 낮춘다.

### 4.4 전주의 속성과 주의

- **원칙.** 색상, 크기 같은 일부 특징은 한 번 보는 순간 눈에 띈다. 하지만 강조 채널을 여러 개 섞으면 효과가 떨어진다(Healey & Enns 2012).
- **AgentVis.** 실패는 약 3%로 드문 사건이다. 강한 채널 하나만 실패에 주고, 나머지는 채도를 낮춘다. 도구 종류까지 색으로 구분하면 실패가 묻히므로 도구는 아이콘이나 이름으로 나타낸다.

### 4.5 시각 채널의 효과 순위

- **원칙.** 정량 판단의 정확도는 다음 순서로 낮아진다(Cleveland & McGill 1984).
  1. 공통 축 위의 위치
  2. 정렬되지 않은 위치
  3. 길이
  4. 각도
  5. 면적
  6. 부피·곡률
  7. 음영·채도
- **AgentVis.**
  - "어떤 종류가 몇 번 실패했나"(Q3)는 공통 축 막대로 보여 준다.
  - 시간 간격을 압축한 가로축은 위치 판단을 왜곡하므로 압축 표시를 반드시 둔다. 지금 그래프의 끊김 표시가 여기에 해당한다.

### 4.6 초점과 맥락(fisheye)

- **원칙.** 관심도는 사전 중요도에서 현재 초점과의 거리를 뺀 값이다. 초점 주변은 자세히, 먼 곳은 요약해 보여 준다(Furnas 1986).
- **AgentVis.**
  - 실패, 사용자 끼어들기, 서브에이전트 생성은 사전 중요도를 높게 둔다.
  - 실패를 고르면 직전 맥락과 직후의 우회 단계를 펼치고 나머지는 접는다. 이것이 Q5에 직접 답한다.

### 4.7 의미 확대(semantic zoom)

- **원칙.** 확대하면 크기만 커지는 것이 아니라 표현이 바뀐다. 원전(Bederson & Hollan, Pad++)의 서지는 확인하지 못했다 [불확실]. AgentLens가 확대 구간을 다시 요약하는 방식으로 이 원칙을 쓴다.
- **AgentVis.** 확대 단계를 턴 → 단계 묶음 → 도구 호출 → 원문의 3~4단계로 둔다.

### 4.8 긴 이벤트 시퀀스의 집계와 단순화

- **원칙.**
  - 공통 경로를 흐름으로 합친다(LifeFlow, CHI 2011).
  - 정보 손실과 간결함의 균형을 맞춰 패턴을 뽑는다(Sequence Synopsis, VAST 2017).
  - 분석 초점을 좁히는 전략으로 추출, 시간 접기, 패턴 단순화, 반복이 있다(Malik et al., IUI 2015).
  - 요약 기법 비교 연구에서는 Sequence Synopsis가 요약 품질은 가장 높았지만 이해에 가장 오래 걸렸다(Zinat et al., EuroVis 2023). EventFlow는 서베이 언급만 확인했다 [불확실].
- **AgentVis.**
  - 연속된 같은 종류 단계는 접는다. 예: "Read ×7", "Edit → 테스트 실패 → Edit 재시도 ×3".
  - 정교한 요약은 해석 비용이 크므로, 유저 스터디용으로는 단순하고 설명할 수 있는 규칙 기반 접기를 쓴다.

### 4.9 색과 접근성

- **원칙.**
  - 색만으로 정보를 전달하지 않는다(WCAG 1.4.1).
  - 이해에 필요한 그래픽 요소는 인접 색과 3:1 이상의 대비를 갖춘다(WCAG 1.4.11).
- **AgentVis.**
  - 실패에는 색과 함께 기호(✕)나 빗금 같은 두 번째 채널을 준다.
  - 성공·실패를 빨강·초록만으로 구분하지 않는다.

## 5. 같은 분야의 시스템과 연구

### 5.1 분산 트레이스와 프로파일러

- **트레이스 표준형.** 트레이스는 흔히 시간축 위 작업별 줄(waterfall, Gantt)로 그린다. AgentVis의 지금 그래프도 이 형태다.
- **집계 시각화.**
  - Jaeger의 트레이스 비교는 경로를 트리로 줄인 뒤 차이를 표시한다.
  - Flame graph는 시간이 아니라 호출 경로로 병합해, 반복 경로를 넓은 칸 하나로 합친다(Gregg 2016).
  - 여러 트레이스를 집계한 시각화가 디버깅에 필요하다는 주장도 있다(arXiv:2010.13681, 저자명 [불확실]).
- **AgentVis.** 개별 턴 진단에는 waterfall이 맞지만, Q3·Q4 같은 횡단 질문에는 약하다. 세션·프로젝트 단위로 "도구 → 명령 유형 → 결과"를 병합한 집계 보기가 필요하다.

### 5.2 LLM 관측 제품

- **공통 패턴.**
  - 실행 단위의 계층 트리와 입출력(LangSmith)
  - 트리와 시간축 보기의 전환(Langfuse)
  - 반복 호출을 접는 집계 그래프와 실행 순서대로 펼친 그래프의 전환(Langfuse 에이전트 그래프)
  - 검색할 수 있는 이어 붙인 로그 보기(Langfuse)
  - 구간 종류 체계(OpenAI Agents SDK Tracing)
- **원본, 집계·접힌 보기, 원문 로그의 3층 구조로 수렴한다.**
- **Q4·Q6은 다루지 않는다.** 실패의 원인 지점(Q6)이나 반복 실패(Q4)를 직접 다루는 제품은 없다. 이것이 AgentVis가 차별화할 지점이다.
- **확인하지 못한 것.** Phoenix의 화면 세부와 AgentOps, W&B Weave는 확인하지 못했다 [불확실].

### 5.3 Claude Code 전용 시각화 도구

- **확인한 도구.** ClaudeScope(시간축, 토큰·도구 보기, 이벤트 상세)와 Coding Agent Visualizer(실행 그래프, 구간 waterfall, 토큰 비용 flame graph)가 있다.
- **공통점.** 둘 다 "전부 보여 주기" 계열이고, 유저 스터디 근거는 찾지 못했다.
- **AgentVis의 차별점.** 질문 중심 설계와 유저 스터디로 차별화할 수 있다. 이 도구들은 비교 조건 후보도 된다.

### 5.4 학술 연구

| 연구 | 설계 | 평가 | 교훈 |
| --- | --- | --- | --- |
| AgentLens (arXiv:2402.08995, TVCG 게재 표기 [불확실]) | 원시 이벤트를 행동 계층으로 구조화, 시점별 LLM 요약, 확대 구간 재요약, 원인 추적, 연동된 보기 3개 | 14명, 재생 시스템 대비 정확도·시간 개선, SUS 67.5 | 요약과 계층이 정보 밀도를 낮췄다. 긴 시간축 탐색과 초보자 안내는 부족했다. |
| AGDebugger (CHI 2025) | 메시지 이력 개요, 메시지 수정 후 그 지점부터 다시 실행 | 형성 인터뷰 5명, 사용자 연구 14명 | 긴 대화에서 오류 위치 찾기가 핵심 난점이다. |
| AgentStepper (arXiv:2602.06593) | 에이전트↔LLM, 에이전트↔도구 대화를 나란히 배치, 이벤트별 한 줄 요약(직전과의 차이 강조), 도구 호출별 diff | 12명, 원시 로그 대비 | 실패 찾기에서는 효과가 컸고 이해에서는 작았다. |
| TraceView (arXiv:2606.22110) | 생각·행동·결과 단계로 정규화, 반복 개요에서 상세로 이동 | 형성 연구 5명 | 훑어보기와 개요·상세 구조는 높게 평가됐다. 그래프 해석성과 미리보기 길이는 낮게 평가됐다. 짧은 노드 요약과 마우스 올림 미리보기를 요청받았다. |
| SeaView (arXiv:2504.08696) | 환경·설정 실패와 에이전트 실수를 구분, 실행 간 비교 | 10명, 자기보고 | 실패의 종류 구분이 유용하다. |
| InconLens (arXiv:2603.28106) | 여러 실행을 의미 단위로 정렬해 갈라지는 지점 탐지 | 사례 연구, 전문가 인터뷰 | |
| Who&When (ICML 2025) | 실패의 책임 에이전트와 시점 귀속 | 최고 방법도 결정적 오류 단계 정확도 14.2% | Q6 자동 판정이 어렵다. |
| MAST (NeurIPS 2025 D&B) | 다중 에이전트 실패 모드 14개, 대분류 3개 | | 실패 분류 체계(Q3)의 참고 |

**연구들이 수렴하는 설계 패턴.**
1. 계층 요약에서 원문으로 내려가는 구조
2. 단계마다 짧은 요약. 특히 직전과 무엇이 다른지를 강조한다.
3. 원인과 결과의 연결
4. 실행 간 비교와 갈라지는 지점 탐지
5. 환경 실패와 에이전트 실수의 구분
6. 긴 시간축을 탐색하기 위한 축소 지도(minimap)

**되풀이된 불만.** 그래프가 해석하기 어렵다. 긴 시간축은 탐색하기 어렵다. 초보자 안내가 부족하다.

## 6. AgentVis 설계 지침

조사 보고가 제안한 순서다. 화면 개선 설계에서 [고충 조사의 우선순위](ClaudeCodePainPoints.md#4-시각화와-유저-스터디에-맞는-우선순위)와 함께 확정한다.

1. **질문과 화면 요소의 짝짓기 표를 먼저 만든다**(Munzner). 어떤 질문에도 답하지 않는 요소는 상세 보기로 옮긴다. 이 표가 유저 스터디 과업 목록이 된다.
2. **세션 개요에 턴별 sparkline 띠를 둔다**(Shneiderman, Tufte). 펼치지 않아도 실패 위치와 재시도가 보이게 한다. Q2·Q4의 진입점이다.
3. **강한 강조는 실패에만 준다**(Healey & Enns, WCAG). 실패는 고채도와 기호로, 나머지는 저채도로 그린다. 도구 종류는 색이 아닌 기호와 이름으로 나타낸다.
4. **연속된 단계를 기본으로 접는다**(LifeFlow, Malik et al., Langfuse). 펼친 보기와 전환할 수 있게 한다.
5. **의미 확대를 둔다**: 턴 → 단계 묶음 → 도구 호출 → 원문(AgentLens, TraceView). 원문은 누를 때만 보여 준다.
6. **실패를 고르면 앞뒤를 펼친다**(Furnas). 직전 맥락과 이후 우회 사슬이 이어져 보이게 한다(Q5).
7. **같은 실패의 반복을 잇는다**(Shneiderman의 relate). 같은 도구, 비슷한 명령, 같은 오류를 묶어 "같은 실패 3번째"처럼 표시한다(Q4).
8. **세션·프로젝트 단위의 실패 집계 보기를 둔다**(Cleveland & McGill, flame graph, SeaView). 도구·실패 유형별 공통 축 막대로 그리고, 환경 실패와 에이전트 실수를 구분한다(Q3).
9. **사용자 메시지를 의도의 기준축으로 고정한다**(AgentStepper, Who&When). 지시와 작업 중 정정을 시간축의 기준점으로 두고, 사용자가 "여기서부터 오해"를 표시할 수 있게 한다. 자동 판정은 보조로만 쓴다(Q6).
10. **단계마다 한 줄 요약을 둔다**(AgentLens, AgentStepper, TraceView). 노드 이름과 마우스 올림 미리보기는 짧게 한다.
11. **압축한 시간축은 그 사실을 밝힌다**(Cleveland & McGill). 실제 시간과 순서 보기를 전환할 수 있게 한다.
12. **유저 스터디는 "실패 찾기" 과업과 "과정 이해" 과업을 나눈다**(AgentStepper, Lam et al., North).

## 7. 유저 스터디 설계

### 7.1 평가 시나리오와 연구 구성

- **평가 시나리오.** Lam et al.(2012)의 7가지 평가 시나리오 가운데 AgentVis에 맞는 것은 사용자 성능(UP), 사용자 경험(UE), 시각적 데이터 분석·추론(VDAR)이다.
- **방법 선택에 대한 경고.**
  - 통제 실험만으로는 시각화 도구의 가치를 다 담지 못한다. 현실 과업, 장기 사례, 벤치마크 데이터를 함께 쓴다(Plaisant 2004).
  - 설계 초기의 성급한 통제 평가는 약한 과학이 될 수 있다. 방법은 연구 질문에 맞춰 고른다(Greenberg & Buxton 2008).
- **권장 구성.**
  1. **형성 연구:** 바이브 코딩 사용자 5~8명을 인터뷰해, 질문 Q1~Q6과 [고충](ClaudeCodePainPoints.md)이 실제로 있는지 확인한다.
  2. **통제 비교 실험:** UP, UE를 잰다.
  3. **자유 탐색 세션:** VDAR을 보며, 통찰 기반 평가로 분석한다.

### 7.2 실험 설계

- **피험자 내 설계.** 적은 표본에서도 검정력이 높아 CHI 도구 논문에서 흔하다. 다만 순서·학습 효과를 막아야 한다.
  - 조건 순서를 라틴 방진으로 맞춘다.
  - 조건마다 길이, 실패 수, 서브에이전트 유무를 맞춘 서로 다른 세션 기록 세트를 쓴다.
- **피험자 간 설계.** 학습 효과는 없지만 표본이 많이 필요하다.
- **기준선 후보.**
  1. Claude Code 화면이나 `/resume`의 대화 기록 그대로
  2. 원시 JSONL을 편집기로 열람(AgentStepper의 기준선)
  3. 검색할 수 있는 단순 텍스트 기록 보기

  공정성을 위해 3을 권한다. 검색 같은 기본 기능은 같게 두고 시각화 유무만 달리해야 효과를 시각화에 돌릴 수 있다. 기존 도구(ClaudeScope 등)를 둘째 비교 조건으로 넣으면 "전부 보여 주는 시간축 대 질문 중심 설계"를 비교할 수 있다. 다만 표본과 시간이 늘어난다.
- **과업.**
  - **통제 과업.** 미리 모아 정답을 주석한 실제 세션 기록에서, 질문마다 정답이 있는 문항을 만든다.
    - 예: "이 턴에서 처음 실패한 도구 호출은?", "같은 오류가 몇 번 반복됐나?", "에이전트가 지시를 처음 잘못 이해한 단계는?"
    - 고충 조사의 과업 후보도 쓸 수 있다. 예: 근거 없는 성공 보고 판정, 테스트 변조 탐지.
  - **Q6의 정답은 주관적이다.** 연구자 두 명이 따로 주석하고 일치도(Cohen's κ)를 보고한다.
  - **현실 과업.** 참가자 본인의 최근 세션을 불러와 "무엇이 잘못됐고 다음에는 어떻게 지시하겠는가"에 답하게 한다. 생태적 타당성을 위한 것이며, "바이브 코딩이 수월해지는가"라는 연구 목적과 직접 이어진다.
- **측정.**
  - 행동 측정: 정확도, 완료 시간
  - 설문: 작업 부하 NASA-TLX(Hart & Staveland 1988, Raw TLX가 흔하다), 사용성 SUS(Brooke 1996, 서지 [불확실]). AgentLens의 SUS 67.5를 비교 기준으로 삼을 수 있다.
  - 질적 자료: 사후 반구조화 인터뷰
  - 자유 탐색 단계: 소리 내어 생각하기와 통찰 코딩(North 2006)
  - 상호작용 로그: 어떤 보기를 얼마나 썼는지 기록해 설계 요소별 기여를 분석한다.
  - 소리 내어 생각하기는 시간을 늘리므로, 시간을 재는 블록에서는 쓰지 않는다.

### 7.3 참가자 수

| 근거 | 참가자 수 |
| --- | --- |
| CHI 2014 논문들의 최빈값(Caine 2016) | 12 |
| AGDebugger, AgentLens | 14 |
| AgentStepper, EvalLM | 12 |
| SeaView | 10 |
| ShiViz 통제 실험 | 39 |

피험자 내 설계로 12~16명을 권한다. 가능하면 앞선 연구의 효과 크기로 검정력을 근거 짓는다.

### 7.4 흔한 함정

1. **허수아비 기준선.** 기준선에 검색 같은 기본 기능이 없으면 효과가 부풀려진다.
2. **학습·순서 효과.** 순서를 맞추고, 조건별로 동등한 기록 세트를 쓰고, 연습 시간을 같게 준다.
3. **도구에 맞춘 과업.** 과업이 형성 연구나 실제 고충에서 나왔다는 근거를 남긴다.
4. **천장·바닥 효과.** 기록이 짧으면 기준선도 쉽게 맞힌다. 실패가 여러 번 섞인 긴 턴을 쓴다.
5. **숙련도 차이.** Claude Code 사용 경험을 미리 받아 공변량으로 쓰거나 층화한다.
6. **자기보고 편향.** "유용했다"는 응답만으로는 약하다. 정확도와 시간 같은 행동 측정을 함께 쓴다.
7. **통계.** 적은 표본에는 비모수 검정(Wilcoxon 등)이나 혼합효과 모형(참가자·과업을 무작위 효과로)을 쓰고 효과 크기를 보고한다.

### 7.5 본뜰 만한 논문

1. **AGDebugger (CHI 2025):** 형성 인터뷰, 사용자 연구, 사용 전략의 질적 분석. LLM 에이전트 디버깅 도구의 CHI 틀이다.
2. **AgentStepper (arXiv 2026):** 원시 로그 기준선, 이해 과업과 버그 찾기 과업 분리, NASA-TLX. 동료 심사 게재처는 확인하지 못했다.
3. **AgentLens:** 시각화 시스템과 재생 시스템을 비교해 과업 유형별 정확도·시간을 쟀고, SUS와 질적 의견을 함께 받았다.
4. **Cornelissen et al. (IEEE TSE 2011):** 대표 과업을 정하는 절차와 시간·정답률 보고 방식의 정석.
5. **EvalLM (CHI 2024):** 형성 인터뷰와 기준선 비교 연구.

### 7.6 초안

- **참가자와 조건.** Claude Code 사용자 12~16명. 피험자 내 2조건(텍스트 기록 보기 대 AgentVis)을 라틴 방진으로 배치한다.
- **기록 세트.** 조건마다 실제 세션 기록 2개를 쓴다. 길이, 실패 수, 서브에이전트 유무를 맞춘다.
- **과업과 측정.** 질문마다 정답 과업 1~2개를 두고 정확도와 시간을 잰다. 블록마다 NASA-TLX를 받는다.
- **자유 탐색.** 참가자 본인 세션으로 15분 동안 탐색하며 소리 내어 생각하고, 통찰을 코딩한다.
- **사후.** SUS와 인터뷰. 인터뷰에서는 "다음 지시를 어떻게 바꾸겠는가"를 물어 바이브 코딩 개선 효과를 확인한다.
- **가설.**
  - H1: AgentVis는 Q2·Q4·Q5 과업에서 정확도를 높이고 시간을 줄인다.
  - H2: Q1 이해 과업에서는 차이가 작다.
  - H3: AgentVis는 작업 부하를 낮춘다.

## 8. 출처

**이론과 원칙**
- Shneiderman, B. (1996). The Eyes Have It: A Task by Data Type Taxonomy for Information Visualizations. IEEE Symp. Visual Languages, 336–343. https://drum.lib.umd.edu/handle/1903/5784
- Munzner, T. (2009). A Nested Model for Visualization Design and Validation. IEEE TVCG 15(6), 921–928.
- Brehmer, M., & Munzner, T. (2013). A Multi-Level Typology of Abstract Visualization Tasks. IEEE TVCG 19(12), 2376–2385. https://www.cs.ubc.ca/labs/imager/tr/2013/MultiLevelTaskTypology/
- Tufte, E. R. (1983/2001). The Visual Display of Quantitative Information; (2006) Beautiful Evidence. Graphics Press. [불확실: 2차 요약으로 확인]
- Healey, C. G., & Enns, J. T. (2012). Attention and Visual Memory in Visualization and Computer Graphics. IEEE TVCG 18(7), 1170–1188. https://www.csc2.ncsu.edu/faculty/healey/download/tvcg.12a.pdf
- Cleveland, W. S., & McGill, R. (1984). Graphical Perception. JASA 79(387), 531–554.
- Furnas, G. W. (1986). Generalized Fisheye Views. CHI '86, 16–23. https://cspages.ucalgary.ca/~saul/581/exer.eps/4furnas86.pdf
- Wongsuphasawat, K. et al. (2011). LifeFlow: Visualizing an Overview of Event Sequences. CHI '11. https://www.cs.umd.edu/projects/hcil/lifeflow
- Chen, Y., Xu, P., & Ren, L. (2017). Sequence Synopsis: Optimize Visual Summary of Temporal Event Data. IEEE VAST.
- Malik, S., Du, F. et al. (2015). Coping with Volume and Variety in Temporal Event Sequences. IUI 2015. https://researcher.ibm.com/publications/coping-with-volume-and-variety-in-temporal-event-sequences-strategies-for-sharpening-analytic-focus
- Zinat et al. (2023). A Comparative Evaluation of Visual Summarization Techniques for Event Sequences. CGF (EuroVis). https://diglib.eg.org/handle/10.1111/cgf14821
- W3C, Understanding SC 1.4.11 Non-text Contrast. https://w3c.github.io/wcag21/understanding/non-text-contrast
- Larkin, J. H., & Simon, H. A. (1987). Why a Diagram is (Sometimes) Worth Ten Thousand Words. Cognitive Science 11(1), 65–99.
- Scaife, M., & Rogers, Y. (1996). External Cognition: How Do Graphical Representations Work? IJHCS 45, 185–213.
- Card, S. K., Mackinlay, J. D., & Shneiderman, B. (1999). Readings in Information Visualization: Using Vision to Think. Morgan Kaufmann.

**텍스트·로그 기준선과의 비교**
- Cornelissen, B., Zaidman, A., & van Deursen, A. (2011). A Controlled Experiment for Program Comprehension through Trace Visualization. IEEE TSE 37(3), 341–355. https://azaidman.github.io/publications/cornelissenTSE2010.pdf
- Beschastnikh, I. et al. (2020). Visualizing Distributed System Executions. ACM TOSEM 29(2). https://homes.cs.washington.edu/~mernst/pubs/visualize-distributed-tosem2020-abstract.html
- Ko, A. J., & Myers, B. A. (2004). Designing the Whyline. CHI 2004. [수치 불확실]
- Kim, T. S. et al. (2024). EvalLM. CHI 2024. https://arxiv.org/abs/2309.13633

**같은 분야의 시스템과 연구**
- Lu, J., Pan, B. et al. (2024). AgentLens: Visual Analysis for Agent Behaviors in LLM-based Autonomous Systems. https://arxiv.org/abs/2402.08995
- Epperson, W. et al. (2025). Interactive Debugging and Steering of Multi-Agent AI Systems (AGDebugger). CHI 2025. https://arxiv.org/abs/2503.02068
- Hutter, R., & Pradel, M. (2026). AgentStepper: Interactive Debugging of Software Development Agents. https://arxiv.org/abs/2602.06593
- Sajadi, A. et al. (2026). TraceView: Interactive Visualization of Agentic Program Repair Trajectories. arXiv:2606.22110.
- Bula, T. et al. (2025). SeaView: Software Engineering Agent Visual Interface for Enhanced Workflow. https://arxiv.org/abs/2504.08696
- Yan, S. et al. (2026). InconLens. https://arxiv.org/abs/2603.28106
- Zhang, S. et al. (2025). Which Agent Causes Task Failures and When? ICML 2025. https://arxiv.org/abs/2505.00212
- Cemri, M. et al. (2025). Why Do Multi-Agent LLM Systems Fail? https://arxiv.org/abs/2503.13657
- Gregg, B. (2016). The Flame Graph. ACM Queue 14(2). https://queue.acm.org/detail.cfm?id=2927301
- Jaeger blog, Trace comparisons arrive in Jaeger 1.7. https://medium.com/jaegertracing/trace-comparisons-arrive-in-jaeger-1-7-a97ad5e2d05d
- Langfuse 에이전트 그래프 문서. https://langfuse.com/docs/observability/features/agent-graphs
- LangSmith 문서. https://docs.smith.langchain.com/tracing/faq/logging_and_viewing
- OpenAI Agents SDK Tracing. https://openai.github.io/openai-agents-python/tracing/
- ClaudeScope. https://liuziyu77.github.io/ClaudeScope/
- Coding Agent Visualizer. https://everettjf.github.io/coding-agent-visualizer/

**평가 방법**
- Lam, H. et al. (2012). Empirical Studies in Information Visualization: Seven Scenarios. IEEE TVCG 18(9), 1520–1536.
- North, C. (2006). Toward Measuring Visualization Insight. IEEE CG&A 26(3), 6–9.
- Hart, S. G., & Staveland, L. E. (1988). Development of NASA-TLX. Human Mental Workload, 139–183.
- Brooke, J. (1996). SUS: A "quick and dirty" usability scale. [서지 불확실]
- Plaisant, C. (2004). The Challenge of Information Visualization Evaluation. AVI 2004, 109–116.
- Greenberg, S., & Buxton, B. (2008). Usability Evaluation Considered Harmful (Some of the Time). CHI 2008, 111–120.
- Caine, K. (2016). Local Standards for Sample Size at CHI. CHI '16, 981–992. https://core.ac.uk/download/268650359.pdf
