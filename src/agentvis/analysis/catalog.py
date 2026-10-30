"""Read raw events from the event store and build session views for the query API.

@doc: docs/design/Analysis.md#8-조회-api
"""

from agentvis.analysis.session import SessionView, build_session
from agentvis.store import EventStore


def list_sessions(store: EventStore, project: str | None = None) -> list[SessionView]:
    """Return every session (optionally of one project), latest activity first.

    @doc: docs/design/Analysis.md#8-조회-api
    """
    views = [build_session(store.events(session_id=session_id)) for session_id in store.session_ids()]
    if project is not None:
        views = [view for view in views if view.project == project]
    return sorted(views, key=lambda view: view.last_activity or view.started_at, reverse=True)


def get_session(store: EventStore, session_id: str) -> SessionView | None:
    """Return one session view, or None if the session has no raw events.

    @doc: docs/design/Analysis.md#8-조회-api
    """
    events = store.events(session_id=session_id)
    return build_session(events) if events else None
