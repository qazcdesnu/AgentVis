"""The baseline condition: a transcript as plain chronological text in one HTML file (M9-T4).

@doc: docs/design/Study.md#4-기준선-텍스트-기록-보기-m9-t4
"""

import json
from datetime import datetime
from html import escape
from pathlib import Path

from agentvis.study.key import read_records

# @doc: docs/design/Study.md#4-기준선-텍스트-기록-보기-m9-t4
FOLD_LINES = 20
_STYLE = """
:root { color-scheme: light dark; --muted: #6b7280; --line: #d1d5db; --error: #b91c1c; --bg: #ffffff; --fg: #111827; }
@media (prefers-color-scheme: dark) { :root { --muted: #9ca3af; --line: #374151; --error: #f87171; --bg: #111827; --fg: #e5e7eb; } }
body { margin: 0 auto; max-width: 980px; padding: 16px; background: var(--bg); color: var(--fg);
       font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
h1 { font-size: 15px; }
.item { border-top: 1px solid var(--line); padding: 6px 0; }
.head { font-weight: 600; }
.time { color: var(--muted); font-weight: 400; margin-left: 8px; font-size: 11px; }
.error .head { color: var(--error); }
pre { margin: 4px 0 0; white-space: pre-wrap; overflow-wrap: anywhere; }
summary { cursor: pointer; color: var(--muted); }
"""


def _time(record: dict) -> str:
    try:
        return datetime.fromisoformat(record["timestamp"]).astimezone().strftime("%H:%M:%S")
    except (KeyError, TypeError, ValueError):
        return ""


def _item(head: str, body: str, time: str, kind: str = "", fold: bool = False, summary: str = "") -> str:
    text = f"<pre>{escape(body)}</pre>"
    if fold:
        text = f"<details><summary>{escape(summary)}</summary>{text}</details>"
    return (f'<div class="item {kind}"><div class="head">{escape(head)}<span class="time">{escape(time)}</span></div>'
            f"{text}</div>")


def _tool_input(name: str, data: dict) -> str:
    if name == "Bash" and isinstance(data.get("command"), str):
        return f"$ {data['command']}"
    if name in ("Edit", "Write", "Read") and isinstance(data.get("file_path"), str):
        parts = [data["file_path"]]
        if name == "Edit":
            parts += ["--- 바꾸기 전", str(data.get("old_string", "")), "+++ 바꾼 뒤", str(data.get("new_string", ""))]
        if name == "Write":
            parts += ["+++ 내용", str(data.get("content", ""))]
        return "\n".join(parts)
    return json.dumps(data, ensure_ascii=False, indent=2)


def _result_text(block: dict) -> str:
    content = block.get("content")
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if isinstance(part, dict))
    return content if isinstance(content, str) else ""


def render_transcript(records: list[dict], title: str) -> str:
    """One self-contained HTML page showing the transcript in order, every text escaped.

    @doc: docs/design/Study.md#4-기준선-텍스트-기록-보기-m9-t4
    """
    items = []
    for record in records:
        kind, time = record.get("type"), _time(record)
        content = record.get("message", {}).get("content") if isinstance(record.get("message"), dict) else None
        if kind == "user" and isinstance(content, str):
            items.append(_item("> 사용자", content, time))
            continue
        for block in content if kind in ("user", "assistant") and isinstance(content, list) else []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text" and kind == "assistant":
                items.append(_item("● 응답", block.get("text", ""), time))
            elif block.get("type") == "text" and kind == "user":
                items.append(_item("> 사용자", block.get("text", ""), time))
            elif block.get("type") == "thinking":
                items.append(_item("생각", block.get("thinking") or "(내용 없음)", time, fold=True, summary="펼치기"))
            elif block.get("type") == "tool_use":
                data = block.get("input") if isinstance(block.get("input"), dict) else {}
                items.append(_item(f"● {block.get('name', '도구')}", _tool_input(str(block.get("name")), data), time))
            elif block.get("type") == "tool_result":
                text, error = _result_text(block), bool(block.get("is_error"))
                lines = text.count("\n") + 1
                head = "⎿ 오류" if error else "⎿ 결과"
                fold = lines > FOLD_LINES
                items.append(_item(head, text, time, "error" if error else "", fold, f"{lines}줄 펼치기"))
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title>'
            f"<style>{_STYLE}</style></head><body><h1>{escape(title)}</h1>{''.join(items)}</body></html>\n")


def write_baseline(folder: Path, out: Path) -> list[Path]:
    """Write <out>/<session>.html for every session transcript in a scenario folder.

    @doc: docs/design/Study.md#4-기준선-텍스트-기록-보기-m9-t4
    """
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for path in sorted(folder.glob("*/*.jsonl")):
        target = out / f"{path.stem}.html"
        target.write_text(render_transcript(read_records(path), f"실행 기록 {path.stem[:8]}"), encoding="utf-8")
        written.append(target)
    return written
