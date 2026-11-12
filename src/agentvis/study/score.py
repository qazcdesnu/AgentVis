"""How well the instruction review's rule-found signals match a scenario folder's answer key (M11-T3).

@doc: docs/design/Study.md#31-신호-규칙-정확도-m11-t3
"""

import json
from collections import Counter
from dataclasses import replace
from pathlib import Path

from agentvis.analysis.review import Review, Signal, review_turn, walk_steps
from agentvis.analysis.session import build_session
from agentvis.study.key import ERROR_TYPES, read_records
from agentvis.transcript import record_to_raw

_INTERPRETING = ("interpret", "ask")
_NOTICING = ("interpret", "ask", "outside")


def _evidence(signal: Signal) -> set[str]:
    """The error types a signal is evidence for (Study.md 3.1)."""
    if signal.kind == "repro" and signal.detail.get("outcome") in ("재현 안 됨", "다른 오류"):
        return {"E1"}
    if signal.kind in ("remaining_failure", "outside"):
        return {"E2"}
    if signal.kind == "conflict":
        return {"E3"}
    return set()


def _review(path: Path) -> tuple[Review | None, list[int], dict[str, int]]:
    """The first turn's review, its step ids in order, and step ids by tool use id and record uuid."""
    events, uuids = [], {}
    for line in path.read_bytes().splitlines(keepends=True):
        event = record_to_raw(line if line.endswith(b"\n") else line + b"\n")
        if event is None:
            continue
        event = replace(event, id=len(events) + 1)
        events.append(event)
        if event.dedup_key and event.dedup_key.startswith("uuid:"):
            uuids[event.dedup_key[5:]] = event.id
    if not events:
        return None, [], {}
    view = build_session(events)
    if not view.turns:
        return None, [], {}
    turn = view.turns[0]
    steps = sorted(walk_steps(turn.steps), key=lambda step: (step.at, step.id))
    ids = {**uuids, **{step.tool_call.tool_use_id: step.id for step in steps if step.tool_call is not None}}
    return review_turn(view, turn.index), [step.id for step in steps], ids


def _trial_score(folder: Path, trial: dict) -> dict:
    review, order, ids = _review(folder / trial["variant"] / f"{trial['session_id']}.jsonl")
    signals = review.signals if review else []
    evidence = set().union(*(_evidence(signal) for signal in signals)) if signals else set()
    position = {step_id: index for index, step_id in enumerate(order)}
    noticed = [position[s.step_id] for s in signals if s.kind in _NOTICING and s.step_id in position]
    answer = ids.get(trial.get("first_notice") or "")
    distance = min(noticed) - position[answer] if noticed and answer in position else None
    return {
        "id": trial["id"], "use": trial["use"], "error_type": trial["error_type"], "response": trial["response"],
        "signals": dict(Counter(signal.kind for signal in signals)),
        "type_hit": trial["error_type"] in evidence if trial["error_type"] != "none" else None,
        "evidence": bool(evidence), "interpreting": any(s.kind in _INTERPRETING for s in signals),
        "notice_distance": distance,
    }


def _rate(hits: list[bool]) -> float | None:
    return round(sum(hits) / len(hits), 3) if hits else None


def score_folder(folder: Path) -> dict:
    """Per-trial matches and the summary measures of Study.md section 3.1.

    @doc: docs/design/Study.md#31-신호-규칙-정확도-m11-t3
    """
    trials = json.loads((folder / "key.json").read_text(encoding="utf-8"))["trials"]
    rows = [_trial_score(folder, trial) for trial in trials]
    errors = [row for row in rows if row["error_type"] != "none"]
    controls = [row for row in rows if row["error_type"] == "none"]
    distances = [row["notice_distance"] for row in rows if row["notice_distance"] is not None]
    summary = {
        "type_hit": {error: _rate([row["type_hit"] for row in errors if row["error_type"] == error]) for error in ERROR_TYPES[:3]},
        "type_hit_all": _rate([row["type_hit"] for row in errors]),
        "evidence_hit": _rate([row["evidence"] for row in errors]),
        "false_alarm": _rate([row["evidence"] for row in controls]),
        "false_alarm_interpreting": _rate([row["interpreting"] for row in controls]),
        "notice_distance_mean_abs": round(sum(abs(d) for d in distances) / len(distances), 2) if distances else None,
        "followed_without_interpreting": _rate([not row["interpreting"] for row in rows if row["response"] == "followed"]),
        "noticed_with_interpreting": _rate([row["interpreting"] for row in rows if row["response"] != "followed"]),
        "trials": len(rows),
    }
    return {"trials": rows, "summary": summary}


def format_score(score: dict) -> str:
    """The score as text: one line per trial, then the summary.

    @doc: docs/design/Study.md#31-신호-규칙-정확도-m11-t3
    """
    lines = []
    for row in score["trials"]:
        kinds = ", ".join(f"{kind} {count}" for kind, count in sorted(row["signals"].items())) or "신호 없음"
        hit = {True: "적중", False: "놓침", None: "-"}[row["type_hit"]]
        lines.append(f"{row['id']} [{row['use']}] {row['error_type']}/{row['response']}: {kinds} · 유형 {hit} · 알아챔 거리 {row['notice_distance']}")
    summary = score["summary"]
    lines.append(f"시행 {summary['trials']}개")
    lines.append("유형 적중: " + ", ".join(f"{error} {rate}" for error, rate in summary["type_hit"].items()) + f" · 전체 {summary['type_hit_all']}")
    lines.append(f"증거 적중 {summary['evidence_hit']} · 오경보 {summary['false_alarm']} (해석 신호만 {summary['false_alarm_interpreting']})")
    lines.append(f"알아챔 거리 절댓값 평균 {summary['notice_distance_mean_abs']} · followed에 해석 신호 없음 {summary['followed_without_interpreting']}"
                 f" · 그 밖에 해석 신호 있음 {summary['noticed_with_interpreting']}")
    return "\n".join(lines)
