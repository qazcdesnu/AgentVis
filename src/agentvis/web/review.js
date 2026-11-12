// Instruction review box: the turn's instruction as numbered sentences, and the rule-found signals that point at them.
// Spec: docs/design/ReviewView.md section 3. All text is untrusted: only ever use textContent.

const CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳";
const TARGET_KIND = { path: "파일 경로", symbol: "코드 이름", test: "테스트 이름", command: "명령" };

export const SIGNAL_KIND = {
  interpret: ["❝", "해석", "에이전트가 지시를 다시 말하거나 지시와 다르게 말한 문장"],
  ask: ["?", "질문", "에이전트가 사용자에게 물은 것"],
  outside: ["↗", "지시 밖", "지시가 가리키지 않은 파일을 읽거나 바꾼 것"],
  repro: ["◇", "재현", "소스를 고치기 전에 돌린 테스트의 결과"],
  remaining_failure: ["✕", "남은 실패", "지시가 가리킨 곳을 고친 뒤에도 실패한 테스트"],
  conflict: ["⇄", "충돌", "한 테스트가 통과로 바뀔 때 다른 테스트가 실패로 바뀐 것"],
};

export function sentenceNumber(index) {
  return index <= CIRCLED.length ? CIRCLED[index - 1] : `(${index})`;
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

function formatClock(iso) {
  if (!iso) return "";
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleTimeString("ko-KR", { hour12: false });
}

// One sentence of the instruction, its targets marked inside the original wording.
function sentenceNode(prompt, sentence, count, selected, onSentence) {
  const node = el("span", "rv-sentence");
  if (selected) node.classList.add("selected");
  node.append(el("span", "rv-number", sentenceNumber(sentence.index)));
  let cursor = sentence.start;
  for (const target of sentence.targets) {
    if (target.start > cursor) node.append(prompt.slice(cursor, target.start));
    const code = el("code", "rv-target", prompt.slice(target.start, target.end));
    code.title = `${TARGET_KIND[target.kind] || target.kind} (지시가 가리킨 대상, 추정)`;
    node.append(code);
    cursor = target.end;
  }
  if (sentence.end > cursor) node.append(prompt.slice(cursor, sentence.end));
  if (count) {
    const chip = el("button", "rv-chip", `신호 ${count}`);
    chip.type = "button";
    chip.title = selected ? "거르기 해제" : "이 문장을 가리키는 신호만 보기";
    node.append(chip);
  }
  node.addEventListener("click", () => onSentence(selected ? null : sentence.index));
  return node;
}

function instructionNode(prompt, review, counts, state, onSentence) {
  const wrap = el("div", "rv-instruction");
  let cursor = 0;
  for (const sentence of review.sentences) {
    if (sentence.start > cursor) wrap.append(prompt.slice(cursor, sentence.start));
    wrap.append(sentenceNode(prompt, sentence, counts.get(sentence.index) || 0, state.sentence === sentence.index, onSentence));
    cursor = sentence.end;
  }
  if (cursor < prompt.length) wrap.append(prompt.slice(cursor));
  return wrap;
}

function signalRow(signal, state, onStep) {
  const [symbol, name, meaning] = SIGNAL_KIND[signal.kind] || ["•", signal.kind, ""];
  const row = el("li", "rv-signal");
  if (String(signal.step_id) === String(state.step)) row.classList.add("selected");
  row.tabIndex = 0;
  row.title = `${name}: ${meaning}. 누르면 그 단계를 엽니다.`;
  row.append(
    el("span", "rv-time", formatClock(signal.at)),
    el("span", "rv-kind", `${symbol} ${name}`),
    el("span", "rv-summary", signal.summary),
    el("span", "rv-ref", signal.sentence ? sentenceNumber(signal.sentence) : ""),
  );
  const open = () => onStep(signal.step_id);
  row.addEventListener("click", open);
  row.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      open();
    }
  });
  return row;
}

// Draws the review of one turn into container (docs/design/ReviewView.md sections 3.1 and 3.2).
export function renderReview(container, prompt, review, state, { onSentence, onStep }) {
  const counts = new Map();
  for (const signal of review.signals) {
    if (signal.sentence) counts.set(signal.sentence, (counts.get(signal.sentence) || 0) + 1);
  }
  const head = el("div", "rv-head", "지시");
  const signals = state.sentence ? review.signals.filter((signal) => signal.sentence === state.sentence) : review.signals;
  const listHead = el("div", "rv-head", "신호 ");
  listHead.append(el("span", "rv-estimated", "추정"));
  if (state.sentence) {
    const clear = el("button", "rv-clear", `문장 ${sentenceNumber(state.sentence)}만 보기 ✕`);
    clear.type = "button";
    clear.addEventListener("click", () => onSentence(null));
    listHead.append(" · ", clear);
  }
  let body;
  if (signals.length) {
    body = el("ul", "rv-signals");
    body.append(...signals.map((signal) => signalRow(signal, state, onStep)));
  } else {
    body = el("p", "empty", state.sentence ? "이 문장을 가리키는 신호가 없습니다." : "규칙으로 찾은 신호가 없습니다.");
    body.title = "신호가 없다는 것이 지시에 잘못이 없다는 뜻은 아닙니다.";
  }
  container.replaceChildren(head, instructionNode(prompt, review, counts, state, onSentence), listHead, body);
}
