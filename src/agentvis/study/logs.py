"""One summary row per trial from the experiment server's screen usage logs (M11-T4).

@doc: docs/design/Study.md#7-화면-사용-기록-요약-m11-t4
"""

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

# Kinds of clicked screen elements, by class prefix, then by id or tag (first match wins).
# @doc: docs/design/Study.md#7-화면-사용-기록-요약-m11-t4
ELEMENT_KINDS = (
    ("class", ("rv-sentence", "rv-chip", "rv-number", "rv-target", "rv-clear", "rv-instruction"), "지시 문장"),
    ("class", ("rv-signal",), "신호 목록"),
    ("class", ("g-node",), "그래프 노드"),
    ("class", ("g-",), "그래프 조작"),
    ("class", ("step", "quiet-run"), "단계 목록"),
    ("class", ("ov-",), "세션 개요"),
    ("class", ("turn-select", "turn-picker"), "턴 선택"),
    ("class", ("view-toggle", "json-toggle"), "보기 전환"),
    ("id", ("live", "refresh"), "머리줄"),
    ("tag", ("a",), "기록 링크"),
    ("tag", ("summary",), "접기·펴기"),
    # Logs written before M11-T4 have no classes for SVG elements.
    ("tag", ("g", "rect", "circle", "path", "text"), "그래프 노드"),
)
COLUMNS = ("participant", "block", "condition", "version", "run", "trial", "start", "end", "seconds",
           "clicks", "keys", "finds", "scrolls", "views", "elements")
_COUNTED = {"click": "clicks", "key": "keys", "find": "finds", "scroll": "scrolls", "hash": "views"}


def element_kind(detail: dict) -> str:
    """The kind of screen element a click landed on.

    @doc: docs/design/Study.md#7-화면-사용-기록-요약-m11-t4
    """
    classes = [name for name in detail.get("classes") or [] if isinstance(name, str)]
    for field, prefixes, kind in ELEMENT_KINDS:
        if field == "class" and any(name.startswith(prefix) for name in classes for prefix in prefixes):
            return kind
        if field == "id" and detail.get("id") in prefixes:
            return kind
        if field == "tag" and detail.get("tag") in prefixes:
            return kind
    return f"<{detail.get('tag') or '?'}>"


def _seconds(start: str, end: str) -> float | None:
    try:
        return round((datetime.fromisoformat(end.replace("Z", "+00:00")) - datetime.fromisoformat(start.replace("Z", "+00:00"))).total_seconds(), 1)
    except (AttributeError, ValueError):
        return None


def _summarize_file(path: Path) -> list[dict]:
    rows, run, info, current = [], 0, {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind, detail = entry.get("type"), entry.get("detail") or {}
        if kind == "server_start":
            run, current = run + 1, None
            info = {"participant": entry.get("participant"), "condition": entry.get("condition") or "agentvis", "version": entry.get("version")}
            continue
        if kind == "trial_start":
            current = {**info, "block": path.parent.name, "run": run, "trial": detail.get("trial"), "start": entry.get("at"),
                       "end": None, "seconds": None, **{column: 0 for column in _COUNTED.values()}, "_elements": Counter()}
            rows.append(current)
            continue
        if current is None:
            continue
        if kind == "trial_end":
            current["end"], current["seconds"] = entry.get("at"), _seconds(current["start"], entry.get("at"))
            current = None
            continue
        if kind == "click" and detail.get("id") == "trial":
            continue
        if kind in _COUNTED:
            current[_COUNTED[kind]] += 1
        if kind == "click":
            current["_elements"][element_kind(detail)] += 1
    for row in rows:
        row["elements"] = "; ".join(f"{name} {count}" for name, count in row.pop("_elements").most_common())
    return rows


def summarize_logs(paths: list[Path]) -> list[dict]:
    """Trial rows from the given interactions.jsonl files, or every such file under the given folders.

    @doc: docs/design/Study.md#7-화면-사용-기록-요약-m11-t4
    """
    files = []
    for path in paths:
        files += sorted(path.rglob("interactions.jsonl")) if path.is_dir() else [path]
    return [row for path in files for row in _summarize_file(path)]


def write_csv(rows: list[dict], path: Path) -> None:
    """The trial rows as a CSV file with the columns of Study.md section 7.

    @doc: docs/design/Study.md#7-화면-사용-기록-요약-m11-t4
    """
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
