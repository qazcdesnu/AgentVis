"""Read Claude Code transcript files incrementally into the event store.

@doc: docs/design/Transcript.md
@doc: docs/design/Transcript.md#41-hook-이벤트를-받을-때-m2-t3
"""

import hashlib
import json
import logging
import os
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from agentvis.store import EventStore, RawEvent, TranscriptCursor

# @doc: docs/design/Transcript.md#3-기록-변환
INGESTED_TYPES = ("user", "assistant", "system", "queue-operation", "attachment")
# @doc: docs/design/Transcript.md#3-기록-변환
INGESTED_ATTACHMENTS = ("queued_command", "hook_non_blocking_error")
# @doc: docs/design/Transcript.md#2-이어-읽기
BATCH_LINES = 500

_log = logging.getLogger("agentvis.transcript")


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
    attachment = record.get("attachment")
    if isinstance(attachment, dict):
        value = attachment.get("toolUseID")
        return value if isinstance(value, str) and value.startswith("toolu_") else None
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
    if record["type"] == "attachment":
        attachment = record.get("attachment")
        if not isinstance(attachment, dict) or attachment.get("type") not in INGESTED_ATTACHMENTS:
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


def paths_to_read(hook_event: dict) -> list[Path]:
    """Return the transcript files a hook event says may have new content.

    @doc: docs/design/Transcript.md#41-hook-이벤트를-받을-때-m2-t3
    """
    paths: list[Path] = []
    transcript_path = hook_event.get("transcript_path")
    if isinstance(transcript_path, str):
        paths.append(Path(transcript_path))
        agent_id = hook_event.get("agent_id")
        if isinstance(agent_id, str):
            subagent = subagent_transcript_path(Path(transcript_path), agent_id)
            paths += [subagent, subagent.with_name(f"agent-{agent_id}.meta.json")]
    agent_transcript_path = hook_event.get("agent_transcript_path")
    if isinstance(agent_transcript_path, str):
        paths.append(Path(agent_transcript_path))
    return list(dict.fromkeys(paths))


class TranscriptReader:
    """A background worker that reads requested transcript files one at a time.

    @doc: docs/design/Transcript.md#41-hook-이벤트를-받을-때-m2-t3
    """

    def __init__(self, store: EventStore, projects_dir: Path) -> None:
        self._store = store
        self._projects_dir = projects_dir
        self._pending: dict[Path, None] = {}
        self._busy = False
        self._stopping = False
        self._condition = threading.Condition()
        self._thread = threading.Thread(target=self._run, name="agentvis-transcript-reader", daemon=True)

    def request(self, path: Path) -> None:
        """Queue a file for reading unless it is already waiting.

        @doc: docs/design/Transcript.md#41-hook-이벤트를-받을-때-m2-t3
        """
        with self._condition:
            self._pending.setdefault(path, None)
            self._condition.notify_all()

    def start(self) -> None:
        """Start the worker thread.

        @doc: docs/design/Transcript.md#41-hook-이벤트를-받을-때-m2-t3
        """
        self._thread.start()

    def stop(self) -> None:
        """Finish the file being read, drop the rest, and stop the worker.

        @doc: docs/design/Transcript.md#41-hook-이벤트를-받을-때-m2-t3
        """
        with self._condition:
            self._stopping = True
            self._pending.clear()
            self._condition.notify_all()
        if self._thread.is_alive():
            self._thread.join()

    def wait_until_idle(self, timeout: float) -> bool:
        """Wait until nothing is queued or being read; return False on timeout.

        @doc: docs/design/Transcript.md#41-hook-이벤트를-받을-때-m2-t3
        """
        with self._condition:
            return self._condition.wait_for(lambda: not self._pending and not self._busy, timeout)

    def _run(self) -> None:
        while True:
            with self._condition:
                self._condition.wait_for(lambda: self._pending or self._stopping)
                if self._stopping:
                    return
                path = next(iter(self._pending))
                del self._pending[path]
                self._busy = True
            try:
                self._read(path)
            except Exception:  # noqa: BLE001 - one bad file must not stop the worker
                _log.exception("세션 기록 읽기 실패: %s", path)
            finally:
                with self._condition:
                    self._busy = False
                    self._condition.notify_all()

    def _read(self, path: Path) -> None:
        if path.name.endswith(".meta.json"):
            read_subagent_meta(self._store, path, self._projects_dir)
            return
        result = read_new_records(self._store, path, self._projects_dir)
        if result.skipped:
            _log.info("세션 기록 %s: 저장 %d, 건너뜀 %d", path, result.stored, result.skipped)

