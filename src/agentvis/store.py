"""The event store: an append-only SQLite table of raw events.

@doc: docs/design/Store.md
"""

import os
import sqlite3
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType

# @doc: docs/design/Store.md#2-스키마
SCHEMA_VERSION = 1

_SOURCES = ("hook", "transcript")
_COLUMNS = (
    "id, source, kind, session_id, prompt_id, tool_use_id, cwd, "
    "occurred_at, received_at, dedup_key, payload"
)
# Run as one transaction so a crash never leaves a half-created schema marked as current.
_CREATE_SCHEMA = f"""
BEGIN;
CREATE TABLE raw_events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    source       TEXT NOT NULL CHECK (source IN ('hook', 'transcript')),
    kind         TEXT NOT NULL,
    session_id   TEXT,
    prompt_id    TEXT,
    tool_use_id  TEXT,
    cwd          TEXT,
    occurred_at  TEXT NOT NULL,
    received_at  TEXT NOT NULL,
    dedup_key    TEXT UNIQUE,
    payload      TEXT NOT NULL
);
CREATE INDEX raw_events_session ON raw_events (session_id, id);
CREATE INDEX raw_events_prompt ON raw_events (prompt_id);
CREATE INDEX raw_events_tool_use ON raw_events (tool_use_id);
CREATE INDEX raw_events_cwd ON raw_events (cwd);
PRAGMA user_version = {SCHEMA_VERSION};
COMMIT;
"""


class SchemaVersionError(Exception):
    """The database was written by a newer schema version than this program knows.

    @doc: docs/design/Store.md#2-스키마
    """


@dataclass(frozen=True)
class RawEvent:
    """One raw event exactly as received from a hook or read from a transcript.

    @doc: docs/design/Store.md#3-자료형
    """

    source: str
    kind: str
    session_id: str | None
    prompt_id: str | None
    tool_use_id: str | None
    cwd: str | None
    occurred_at: datetime
    payload: str
    dedup_key: str | None = None
    id: int | None = None
    received_at: datetime | None = None


def data_dir() -> Path:
    """Return the data directory, honoring AGENTVIS_HOME; does not create it.

    @doc: docs/design/Store.md#1-데이터-디렉터리
    """
    home = os.environ.get("AGENTVIS_HOME")
    return Path(home).expanduser() if home else Path.home() / ".agentvis"


def default_db_path() -> Path:
    """Return the database file path inside the data directory.

    @doc: docs/design/Store.md#1-데이터-디렉터리
    """
    return data_dir() / "agentvis.db"


def _to_text(moment: datetime) -> str:
    return moment.astimezone(UTC).isoformat()


def _to_event(row: tuple) -> RawEvent:
    (event_id, source, kind, session_id, prompt_id, tool_use_id, cwd,
     occurred_at, received_at, dedup_key, payload) = row
    return RawEvent(
        source=source,
        kind=kind,
        session_id=session_id,
        prompt_id=prompt_id,
        tool_use_id=tool_use_id,
        cwd=cwd,
        occurred_at=datetime.fromisoformat(occurred_at),
        payload=payload,
        dedup_key=dedup_key,
        id=event_id,
        received_at=datetime.fromisoformat(received_at),
    )


class EventStore:
    """A thread-safe handle on the raw event database.

    @doc: docs/design/Store.md#4-이벤트-저장소-api
    """

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        # Autocommit mode: every append is durable on its own, and the schema script manages its transaction.
        self._connection = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        try:
            self._prepare_schema()
        except BaseException:
            self._connection.close()
            raise

    def _prepare_schema(self) -> None:
        # Check the version before anything else so a newer database is never modified.
        version = self._connection.execute("PRAGMA user_version").fetchone()[0]
        if version > SCHEMA_VERSION:
            raise SchemaVersionError(
                f"데이터베이스 스키마 버전 {version}은 이 프로그램이 아는 버전 {SCHEMA_VERSION}보다 새롭다"
            )
        self._connection.execute("PRAGMA journal_mode = WAL")
        if version == 0:
            self._connection.executescript(_CREATE_SCHEMA)

    def append(self, event: RawEvent) -> int | None:
        """Store an event and return its id, or None if its dedup key is already stored.

        @doc: docs/design/Store.md#4-이벤트-저장소-api
        """
        if event.source not in _SOURCES:
            raise ValueError(f"알 수 없는 source: {event.source!r}")
        if event.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at에 시간대 정보가 없다")
        values = (
            event.source,
            event.kind,
            event.session_id,
            event.prompt_id,
            event.tool_use_id,
            event.cwd,
            _to_text(event.occurred_at),
            _to_text(datetime.now(UTC)),
            event.dedup_key,
            event.payload,
        )
        with self._lock:
            cursor = self._connection.execute(
                "INSERT INTO raw_events (source, kind, session_id, prompt_id, tool_use_id, cwd, "
                "occurred_at, received_at, dedup_key, payload) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT (dedup_key) DO NOTHING",
                values,
            )
            return cursor.lastrowid if cursor.rowcount == 1 else None

    def events(self, session_id: str | None = None, after_id: int = 0) -> list[RawEvent]:
        """Return events with id greater than after_id in id order, optionally for one session.

        @doc: docs/design/Store.md#4-이벤트-저장소-api
        """
        query = f"SELECT {_COLUMNS} FROM raw_events WHERE id > ?"
        params: list[object] = [after_id]
        if session_id is not None:
            query += " AND session_id = ?"
            params.append(session_id)
        with self._lock:
            rows = self._connection.execute(query + " ORDER BY id", params).fetchall()
        return [_to_event(row) for row in rows]

    def close(self) -> None:
        """Close the database connection.

        @doc: docs/design/Store.md#4-이벤트-저장소-api
        """
        with self._lock:
            self._connection.close()

    def __enter__(self) -> "EventStore":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
