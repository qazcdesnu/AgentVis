"""Tests for the event store.

@doc: docs/design/Store.md#5-테스트
"""

import os
import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from unittest import mock

from agentvis.store import (
    SCHEMA_VERSION,
    EventStore,
    RawEvent,
    SchemaVersionError,
    TranscriptCursor,
    data_dir,
    default_db_path,
)
from tests.support import RepoTestCase

_KST = timezone(timedelta(hours=9))
_EVENT = RawEvent(
    source="hook",
    kind="PostToolUseFailure",
    session_id="s1",
    prompt_id="p1",
    tool_use_id="toolu_1",
    cwd="/Users/me/app",
    occurred_at=datetime(2026, 10, 31, 10, 0, tzinfo=_KST),
    payload='{"hook_event_name": "PostToolUseFailure",  "error": "Exit code 1"}',
)


class EventStoreTest(RepoTestCase):
    """@doc: docs/design/Store.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.path = self.root / "data" / "agentvis.db"
        self.store = EventStore(self.path)
        self.addCleanup(self.store.close)

    def test_round_trip_preserves_values(self) -> None:
        event_id = self.store.append(_EVENT)
        [stored] = self.store.events()
        self.assertEqual(stored.id, event_id)
        self.assertEqual(stored.payload, _EVENT.payload)
        self.assertEqual(stored.occurred_at, _EVENT.occurred_at)
        self.assertEqual(stored.occurred_at.tzinfo, UTC)
        self.assertEqual(stored.occurred_at.hour, 1)
        self.assertIsNotNone(stored.received_at)
        self.assertEqual(replace(stored, id=None, received_at=None, occurred_at=_EVENT.occurred_at), _EVENT)

    def test_rejects_invalid_source_and_naive_time(self) -> None:
        with self.assertRaises(ValueError):
            self.store.append(replace(_EVENT, source="other"))
        with self.assertRaises(ValueError):
            self.store.append(replace(_EVENT, occurred_at=datetime(2026, 10, 31, 10, 0)))
        self.assertEqual(self.store.events(), [])

    def test_dedup_key_skips_repeats_but_none_does_not(self) -> None:
        keyed = replace(_EVENT, source="transcript", dedup_key="uuid-1")
        self.assertIsNotNone(self.store.append(keyed))
        self.assertIsNone(self.store.append(keyed))
        self.assertIsNotNone(self.store.append(_EVENT))
        self.assertIsNotNone(self.store.append(_EVENT))
        self.assertEqual(len(self.store.events()), 3)

    def test_filters_by_session_and_after_id(self) -> None:
        first = self.store.append(_EVENT)
        self.store.append(replace(_EVENT, session_id="s2"))
        third = self.store.append(_EVENT)
        self.assertEqual([event.id for event in self.store.events(session_id="s1")], [first, third])
        self.assertEqual([event.id for event in self.store.events(session_id="s1", after_id=first)], [third])
        self.assertEqual(len(self.store.events(after_id=first)), 2)

    def test_concurrent_appends_from_threads(self) -> None:
        def append_many() -> list[int | None]:
            return [self.store.append(_EVENT) for _ in range(50)]

        with ThreadPoolExecutor(max_workers=4) as pool:
            ids = [event_id for result in pool.map(lambda _: append_many(), range(4)) for event_id in result]
        self.assertEqual(len(set(ids)), 200)
        self.assertEqual(len(self.store.events()), 200)

    def test_session_ids_in_first_appearance_order(self) -> None:
        for session_id in ("s2", "s1", "s2", None):
            self.store.append(replace(_EVENT, session_id=session_id))
        self.assertEqual(self.store.session_ids(), ["s2", "s1"])

    def test_newer_schema_version_is_refused_and_left_untouched(self) -> None:
        self.store.close()
        connection = sqlite3.connect(self.path)
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")
        connection.close()
        with self.assertRaises(SchemaVersionError):
            EventStore(self.path)
        connection = sqlite3.connect(self.path)
        self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION + 1)
        self.assertEqual(connection.execute("SELECT count(*) FROM raw_events").fetchone()[0], 0)
        connection.close()

    def test_reopening_keeps_existing_events(self) -> None:
        self.store.append(_EVENT)
        self.store.close()
        with EventStore(self.path) as reopened:
            self.assertEqual(len(reopened.events()), 1)


_SCHEMA_V1 = """
CREATE TABLE raw_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL CHECK (source IN ('hook', 'transcript')),
    kind TEXT NOT NULL, session_id TEXT, prompt_id TEXT, tool_use_id TEXT, cwd TEXT,
    occurred_at TEXT NOT NULL, received_at TEXT NOT NULL, dedup_key TEXT UNIQUE, payload TEXT NOT NULL
);
INSERT INTO raw_events (source, kind, session_id, occurred_at, received_at, payload)
VALUES ('hook', 'Stop', 's-old', '2026-10-31T00:00:00+00:00', '2026-10-31T00:00:01+00:00', '{}');
PRAGMA user_version = 1;
"""


class StoreM2Test(RepoTestCase):
    """@doc: docs/design/Store.md#6-m2-변경"""

    def test_version_1_database_is_migrated_and_keeps_events(self) -> None:
        path = self.root / "v1.db"
        connection = sqlite3.connect(path)
        connection.executescript(_SCHEMA_V1)
        connection.close()
        with EventStore(path) as store:
            self.assertEqual([event.session_id for event in store.events()], ["s-old"])
            self.assertIsNone(store.cursor("/x"))
        connection = sqlite3.connect(path)
        self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
        connection.close()

    def test_version_2_database_is_migrated_and_cursors_are_reset(self) -> None:
        path = self.root / "v2.db"
        with EventStore(path) as store:
            store.append_batch([replace(_EVENT, source="transcript", dedup_key="uuid:1")], TranscriptCursor("/p/s.jsonl", 9, 1, 2))
        connection = sqlite3.connect(path)
        connection.execute("PRAGMA user_version = 2")
        connection.commit()
        connection.close()
        with EventStore(path) as store:
            self.assertIsNone(store.cursor("/p/s.jsonl"))
            self.assertEqual(len(store.events()), 1)

    def test_concurrent_first_open_succeeds(self) -> None:
        for attempt in range(10):
            path = self.root / f"race{attempt}.db"
            errors: list[BaseException] = []

            def open_and_close() -> None:
                try:
                    EventStore(path).close()
                except BaseException as error:  # noqa: BLE001 - collected for the assertion below
                    errors.append(error)

            with ThreadPoolExecutor(max_workers=3) as pool:
                for _ in range(3):
                    pool.submit(open_and_close)
            self.assertEqual(errors, [], f"attempt {attempt}")

    def test_append_batch_stores_events_and_cursor_together(self) -> None:
        with EventStore(self.root / "a.db") as store:
            self.assertIsNone(store.first_received_at())
            cursor = TranscriptCursor("/p/s.jsonl", 120, 1, 2)
            keyed = [replace(_EVENT, source="transcript", dedup_key=f"uuid:{n}") for n in range(3)]
            self.assertEqual(store.append_batch(keyed, cursor), 3)
            self.assertEqual(store.cursor("/p/s.jsonl"), cursor)
            moved = TranscriptCursor("/p/s.jsonl", 300, 1, 2)
            self.assertEqual(store.append_batch(keyed[1:] + [replace(keyed[0], dedup_key="uuid:9")], moved), 1)
            self.assertEqual(store.cursor("/p/s.jsonl"), moved)
            first = store.first_received_at()
            self.assertEqual(first, store.events()[0].received_at)

    def test_append_batch_is_all_or_nothing(self) -> None:
        with EventStore(self.root / "a.db") as store:
            bad = [replace(_EVENT, dedup_key="uuid:1"), replace(_EVENT, source="other", dedup_key="uuid:2")]
            with self.assertRaises(ValueError):
                store.append_batch(bad, TranscriptCursor("/p/s.jsonl", 10, 1, 2))
            self.assertEqual(store.events(), [])
            self.assertIsNone(store.cursor("/p/s.jsonl"))


class DataDirTest(RepoTestCase):
    """@doc: docs/design/Store.md#5-테스트"""

    def test_agentvis_home_overrides_default(self) -> None:
        with mock.patch.dict(os.environ, {"AGENTVIS_HOME": str(self.root)}):
            self.assertEqual(data_dir(), self.root)
            self.assertEqual(default_db_path(), self.root / "agentvis.db")
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch("pathlib.Path.home", return_value=self.root):
            self.assertEqual(data_dir(), self.root / ".agentvis")
        self.assertFalse((self.root / ".agentvis").exists())


if __name__ == "__main__":
    unittest.main()
