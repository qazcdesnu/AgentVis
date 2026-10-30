"""Read Claude Code transcript files incrementally into the event store.

@doc: docs/design/Transcript.md
"""

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from agentvis.store import EventStore, RawEvent, TranscriptCursor

# @doc: docs/design/Transcript.md#3-기록-변환
INGESTED_TYPES = ("user", "assistant", "system", "queue-operation")
# @doc: docs/design/Transcript.md#2-이어-읽기
BATCH_LINES = 500


@dataclass(frozen=True)
class ReadResult:
    """What one incremental read of a transcript file did.

    @doc: docs/design/Transcript.md#2-이어-읽기
    """

    stored: int
    skipped: int
    offset: int


def default_projects_dir() -> Path:
    """Return the root directory where Claude Code keeps transcripts.

    @doc: docs/design/Transcript.md#1-읽는-파일
    """
    return Path.home() / ".claude" / "projects"


def subagent_transcript_path(transcript_path: Path, agent_id: str) -> Path:
    """Return the transcript file of a subagent spawned in the given session.

    @doc: docs/design/Transcript.md#1-읽는-파일
    """
    return transcript_path.with_suffix("") / "subagents" / f"agent-{agent_id}.jsonl"


def _inside(path: Path, projects_dir: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(projects_dir.resolve()):
        raise ValueError(f"기록 루트 밖의 경로는 읽지 않음: {path}")
    return resolved


def _block(record: dict) -> dict:
    content = record.get("message", {}).get("content") if isinstance(record.get("message"), dict) else None
    if isinstance(content, list) and content and isinstance(content[0], dict):
        return content[0]
    return {}


def _tool_use_id(record: dict) -> str | None:
    block = _block(record)
    value = block.get("id") if block.get("type") == "tool_use" else block.get("tool_use_id")
    return value if block.get("type") in ("tool_use", "tool_result") and isinstance(value, str) else None


def _text(record: dict, key: str) -> str | None:
    value = record.get(key)
    return value if isinstance(value, str) else None


def record_to_raw(line: bytes) -> RawEvent | None:
    """Convert one transcript line to a raw event, or None if it is not stored.

    @doc: docs/design/Transcript.md#3-기록-변환
    """
    try:
        text = line.decode("utf-8")
        record = json.loads(text)
        occurred_at = datetime.fromisoformat(record["timestamp"])
    except (UnicodeDecodeError, ValueError, KeyError, TypeError):
        return None
    if not isinstance(record, dict) or record.get("type") not in INGESTED_TYPES:
        return None
    session_id = _text(record, "sessionId")
    if session_id is None or occurred_at.utcoffset() is None:
        return None
    uuid = _text(record, "uuid")
    return RawEvent(
        source="transcript",
        kind=record["type"],
        session_id=session_id,
        prompt_id=_text(record, "promptId"),
        tool_use_id=_tool_use_id(record),
        cwd=_text(record, "cwd"),
        occurred_at=occurred_at,
        payload=text,
        dedup_key=f"uuid:{uuid}" if uuid else f"sha256:{hashlib.sha256(line).hexdigest()}",
    )


def read_new_records(store: EventStore, path: Path, projects_dir: Path) -> ReadResult:
    """Read the lines appended to a transcript since the stored cursor and store them.

    @doc: docs/design/Transcript.md#2-이어-읽기
    """
    resolved = _inside(path, projects_dir)
    try:
        file = resolved.open("rb")
    except FileNotFoundError:
        return ReadResult(0, 0, 0)
    with file:
        status = os.fstat(file.fileno())
        cursor = store.cursor(str(resolved))
        offset = cursor.offset if cursor else 0
        if cursor and ((cursor.device, cursor.inode) != (status.st_dev, status.st_ino) or status.st_size < offset):
            offset = 0
        file.seek(offset)
        data = file.read()
    # A line without its newline may still be being written; leave it for the next read.
    complete = data[: data.rfind(b"\n") + 1]
    stored = skipped = 0
    lines = complete.splitlines(keepends=True)
    for start in range(0, len(lines), BATCH_LINES):
        chunk = lines[start : start + BATCH_LINES]
        events = []
        for line in chunk:
            event = record_to_raw(line.rstrip(b"\r\n"))
            if event is None:
                skipped += bool(line.strip())
            else:
                events.append(event)
        offset += sum(len(line) for line in chunk)
        stored += store.append_batch(events, TranscriptCursor(str(resolved), offset, status.st_dev, status.st_ino))
    return ReadResult(stored, skipped, offset)


def read_subagent_meta(store: EventStore, path: Path, projects_dir: Path) -> bool:
    """Store a subagent meta file as a raw event; return whether its content was new.

    @doc: docs/design/Transcript.md#2-이어-읽기
    """
    resolved = _inside(path, projects_dir)
    try:
        content = resolved.read_bytes()
        modified = datetime.fromtimestamp(resolved.stat().st_mtime, UTC)
    except FileNotFoundError:
        return False
    event = RawEvent(
        source="transcript",
        kind="subagent-meta",
        # <session id>/subagents/agent-<id>.meta.json
        session_id=resolved.parent.parent.name,
        prompt_id=None,
        tool_use_id=None,
        cwd=None,
        occurred_at=modified,
        payload=content.decode("utf-8", errors="replace"),
        dedup_key=f"sha256:{hashlib.sha256(content).hexdigest()}",
    )
    return store.append_batch([event]) == 1
