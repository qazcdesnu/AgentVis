"""The answer key of a scenario folder and its checker (M9-T3).

@doc: docs/design/Study.md#3-정답표-m9-t3
"""

import json
import re
from collections import Counter
from pathlib import Path

# @doc: docs/design/Study.md#3-정답표-m9-t3
ERROR_TYPES = ("E1", "E2", "E3", "none")
# @doc: docs/design/Study.md#3-정답표-m9-t3
RESPONSES = ("followed", "asked", "worked_around", "noticed_then_followed")
# @doc: docs/design/Study.md#3-정답표-m9-t3
USES = ("practice", "trial", "u3")
_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def _records(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def instruction_text(records: list[dict]) -> str:
    """The first user input of a transcript, which is the task instruction.

    @doc: docs/design/Study.md#3-정답표-m9-t3
    """
    for record in records:
        if record.get("type") != "user":
            continue
        content = record.get("message", {}).get("content") if isinstance(record.get("message"), dict) else None
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text")
    return ""


def _step_ids(records: list[dict]) -> set[str]:
    ids = {record["uuid"] for record in records if isinstance(record.get("uuid"), str)}
    for record in records:
        content = record.get("message", {}).get("content") if isinstance(record.get("message"), dict) else None
        for block in content if isinstance(content, list) else []:
            if isinstance(block, dict) and block.get("type") == "tool_use" and isinstance(block.get("id"), str):
                ids.add(block["id"])
    return ids


def _check_trial(folder: Path, trial: dict, label: str) -> list[str]:
    problems = []
    for field, allowed in (("use", USES), ("error_type", ERROR_TYPES), ("response", RESPONSES)):
        if trial.get(field) not in allowed:
            problems.append(f"{label}: '{field}'는 {', '.join(allowed)} 중 하나여야 함")
    variant, session = trial.get("variant"), trial.get("session_id")
    if not (isinstance(variant, str) and _ID.fullmatch(variant) and isinstance(session, str) and _ID.fullmatch(session)):
        return problems + [f"{label}: 'variant'와 'session_id'가 올바른 이름이 아님"]
    path = folder / variant / f"{session}.jsonl"
    if not path.is_file():
        return problems + [f"{label}: 기록 파일 없음: {variant}/{session}.jsonl"]
    records = _records(path)
    instruction = instruction_text(records)
    original, perturbed = trial.get("original_text"), trial.get("perturbed_text")
    if trial.get("error_type") == "none":
        if original is not None or perturbed is not None:
            problems.append(f"{label}: 통제 시행(none)에는 'original_text'·'perturbed_text'가 null이어야 함")
    elif trial.get("error_type") in ERROR_TYPES:
        if not (isinstance(original, str) and original and isinstance(perturbed, str) and perturbed):
            problems.append(f"{label}: 오류 시행에는 'original_text'와 'perturbed_text'가 있어야 함")
        elif perturbed not in instruction:
            problems.append(f"{label}: 'perturbed_text'가 기록의 지시에 없음")
    notice = trial.get("first_notice")
    if trial.get("response") == "followed":
        if notice is not None:
            problems.append(f"{label}: 'followed'에는 'first_notice'가 null이어야 함")
    elif trial.get("response") in RESPONSES and notice not in _step_ids(records):
        problems.append(f"{label}: 'first_notice'가 기록의 도구 호출 ID나 uuid가 아님: {notice!r}")
    return problems


def check_key(folder: Path) -> list[str]:
    """Problems of folder/key.json against the transcripts in the folder; empty when the key is sound.

    @doc: docs/design/Study.md#3-정답표-m9-t3
    """
    try:
        key = json.loads((folder / "key.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"key.json을 읽을 수 없음: {error}"]
    trials = key.get("trials") if isinstance(key, dict) else None
    if not isinstance(trials, list):
        return ["key.json의 'trials'가 목록이 아님"]
    problems = []
    seen: set[str] = set()
    for position, trial in enumerate(trials, 1):
        if not isinstance(trial, dict):
            problems.append(f"#{position}: 시행이 JSON 객체가 아님")
            continue
        trial_id = trial.get("id")
        label = f"#{position} {trial_id}"
        if not (isinstance(trial_id, str) and _ID.fullmatch(trial_id)):
            problems.append(f"{label}: 'id'가 올바른 이름이 아님")
        elif trial_id in seen:
            problems.append(f"{label}: 'id'가 겹침")
        seen.add(trial_id)
        problems += _check_trial(folder, trial, label)
    return problems


def key_summary(folder: Path) -> str:
    """A table of trial counts by error type and response, one block per use.

    @doc: docs/design/Study.md#3-정답표-m9-t3
    """
    trials = json.loads((folder / "key.json").read_text(encoding="utf-8"))["trials"]
    lines = []
    for use in USES:
        counts = Counter((trial["error_type"], trial["response"]) for trial in trials if trial["use"] == use)
        if not counts:
            continue
        lines.append(f"[{use}] 시행 {sum(counts.values())}개")
        lines.append("오류 유형".ljust(10) + "".join(response.ljust(23) for response in RESPONSES))
        for error_type in ERROR_TYPES:
            lines.append(error_type.ljust(10) + "".join(str(counts[(error_type, response)]).ljust(23) for response in RESPONSES))
    return "\n".join(lines)
