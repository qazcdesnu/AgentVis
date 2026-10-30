"""The event store: an append-only SQLite table of raw events.

@doc: docs/design/Store.md
@doc: docs/design/Store.md#6-m2-변경
@doc: docs/design/Store.md#7-m3-변경
@doc: docs/design/Store.md#8-조회-보조
"""

import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType

# @doc: docs/design/Store.md#2-스키마
SCHEMA_VERSION = 3

_SOURCES = ("hook", "transcript")
_BUSY_TIMEOUT_MS = 1000
_COLUMNS = (
    "id, source, kind, session_id, prompt_id, tool_use_id, cwd, "
    "occurred_at, received_at, dedup_key, payload"
)
_INSERT = (
    "INSERT INTO raw_events (source, kind, session_id, prompt_id, tool_use_id, cwd, "
    "occurred_at, received_at, dedup_key, payload) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
    "ON CONFLICT (dedup_key) DO NOTHING"
)
# MIGRATIONS[n] takes a database from schema version n to n + 1.
_MIGRATIONS = (
    (
        """CREATE TABLE raw_events (
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
        )""",
        "CREATE INDEX raw_events_session ON raw_events (session_id, id)",
        "CREATE INDEX raw_events_prompt ON raw_events (prompt_id)",
        "CREATE INDEX raw_events_tool_use ON raw_events (tool_use_id)",
        "CREATE INDEX raw_events_cwd ON raw_events (cwd)",
    ),
    (
        """CREATE TABLE transcript_cursors (
            path        TEXT PRIMARY KEY,
            offset      INTEGER NOT NULL,
            device      INTEGER NOT NULL,
            inode       INTEGER NOT NULL,
            updated_at  TEXT NOT NULL
        )""",
    ),
    # The transcript reader stores more record types now; forget read positions to re-read old records.
    ("DELETE FROM transcript_cursors",),
)


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


@dataclass(frozen=True)
class TranscriptCursor:
    """Where reading of one transcript file should resume.

    @doc: docs/design/Store.md#6-m2-변경
    """

    path: str
    offset: int
    device: int
    inode: int


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


def _values(event: RawEvent, received_at: str) -> tuple:
    if event.source not in _SOURCES:
        raise ValueError(f"알 수 없는 source: {event.source!r}")
    if event.occurred_at.utcoffset() is None:
        raise ValueError("occurred_at에 시간대 정보가 없다")
    return (
        event.source,
        event.kind,
        event.session_id,
        event.prompt_id,
        event.tool_use_id,
        event.cwd,
        _to_text(event.occurred_at),
        received_at,
        event.dedup_key,
        event.payload,
    )


class EventStore:
    """A thread-safe handle on the raw event database.

    @doc: docs/design/Store.md#4-이벤트-저장소-api
    """

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        # Autocommit mode: every append is durable on its own; multi-statement work uses explicit BEGIN.
        self._connection = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        try:
            self._connection.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")
            self._prepare_schema()
        except BaseException:
            self._connection.close()
            raise

    def _version(self) -> int:
        return self._connection.execute("PRAGMA user_version").fetchone()[0]

    def _refuse_newer(self, version: int) -> None:
        if version > SCHEMA_VERSION:
            raise SchemaVersionError(
                f"데이터베이스 스키마 버전 {version}은 이 프로그램이 아는 버전 {SCHEMA_VERSION}보다 새롭다"
            )

    def _enable_wal(self) -> None:
        # Switching to WAL needs an exclusive lock, and SQLite reports a conflict immediately
        # instead of waiting; WAL persists in the file, so a retry succeeds once anyone switched it.
        deadline = time.monotonic() + _BUSY_TIMEOUT_MS / 1000
        while True:
            try:
                self._connection.execute("PRAGMA journal_mode = WAL")
                return
            except sqlite3.OperationalError as error:
                if "locked" not in str(error) or time.monotonic() >= deadline:
                    raise
                time.sleep(0.01)

    def _prepare_schema(self) -> None:
        # Check before anything else so a newer database is never modified.
        self._refuse_newer(self._version())
        self._enable_wal()
        if self._version() == SCHEMA_VERSION:
            return
        # Re-read under the write lock: another connection may have migrated meanwhile.
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            version = self._version()
            self._refuse_newer(version)
            for statements in _MIGRATIONS[version:]:
                for statement in statements:
                    self._connection.execute(statement)
            self._connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            self._connection.execute("COMMIT")
        except BaseException:
            self._connection.execute("ROLLBACK")
            raise

    def append(self, event: RawEvent) -> int | None:
        """Store an event and return its id, or None if its dedup key is already stored.

        @doc: docs/design/Store.md#4-이벤트-저장소-api
        """
        values = _values(event, _to_text(datetime.now(UTC)))
        with self._lock:
            cursor = self._connection.execute(_INSERT, values)
            return cursor.lastrowid if cursor.rowcount == 1 else None

    def append_batch(self, events: list[RawEvent], cursor: TranscriptCursor | None = None) -> int:
        """Store events and advance a transcript cursor in one transaction; return how many were new.

        @doc: docs/design/Store.md#6-m2-변경
        """
        received_at = _to_text(datetime.now(UTC))
        rows = [_values(event, received_at) for event in events]
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                inserted = sum(self._connection.execute(_INSERT, row).rowcount for row in rows)
                if cursor is not None:
                    self._connection.execute(
                        "INSERT INTO transcript_cursors (path, offset, device, inode, updated_at) "
                        "VALUES (?, ?, ?, ?, ?) ON CONFLICT (path) DO UPDATE SET offset = excluded.offset, "
                        "device = excluded.device, inode = excluded.inode, updated_at = excluded.updated_at",
                        (cursor.path, cursor.offset, cursor.device, cursor.inode, received_at),
                    )
                self._connection.execute("COMMIT")
            except BaseException:
                self._connection.execute("ROLLBACK")
                raise
        return inserted

    def cursor(self, path: str) -> TranscriptCursor | None:
        """Return the stored read position of a transcript file, if any.

        @doc: docs/design/Store.md#6-m2-변경
        """
        with self._lock:
            row = self._connection.execute(
                "SELECT path, offset, device, inode FROM transcript_cursors WHERE path = ?", (path,)
            ).fetchone()
        return TranscriptCursor(*row) if row else None

    def first_received_at(self) -> datetime | None:
        """Return when the first event was stored, i.e. when collection started.

        @doc: docs/design/Store.md#6-m2-변경
        """
        with self._lock:
            row = self._connection.execute("SELECT received_at FROM raw_events ORDER BY id LIMIT 1").fetchone()
        return datetime.fromisoformat(row[0]) if row else None

    def session_ids(self) -> list[str]:
        """Return the session ids that appear in raw events, in order of first appearance.

        @doc: docs/design/Store.md#8-조회-보조
        """
        with self._lock:
            rows = self._connection.execute(
                "SELECT session_id FROM raw_events WHERE session_id IS NOT NULL GROUP BY session_id ORDER BY MIN(id)"
            ).fetchall()
        return [row[0] for row in rows]

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
