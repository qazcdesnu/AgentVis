"""Read raw events from the event store and build session views for the query API.

@doc: docs/design/Analysis.md#8-조회-api
@doc: docs/design/Analysis.md#2-프로젝트
@doc: docs/design/FlowGraph.md#5-조회-api
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from agentvis.analysis.graph import FlowGraph, build_turn_graph
from agentvis.analysis.session import SessionView, build_session
from agentvis.store import EventStore


@dataclass
class ProjectView:
    """Sessions grouped by their project path.

    @doc: docs/design/Analysis.md#2-프로젝트
    """

    path: str
    name: str
    parent: str
    session_count: int
    last_activity: datetime | None
    exists: bool


def _parent(path: Path) -> str:
    home = Path.home()
    parent = path.parent
    return "~" + str(parent)[len(str(home)):] if parent.is_relative_to(home) else str(parent)


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


def get_turn_graph(store: EventStore, session_id: str, index: int) -> FlowGraph | None:
    """Return the flow graph of one turn, or None if the session or turn does not exist.

    @doc: docs/design/FlowGraph.md#5-조회-api
    """
    view = get_session(store, session_id)
    return build_turn_graph(view, index) if view is not None else None


def list_projects(store: EventStore) -> list[ProjectView]:
    """Return the projects of all sessions, latest activity first.

    @doc: docs/design/Analysis.md#2-프로젝트
    """
    grouped: dict[str, list[SessionView]] = {}
    for view in list_sessions(store):
        if view.project is not None:
            grouped.setdefault(view.project, []).append(view)
    projects = []
    for project, views in grouped.items():
        path = Path(project)
        activities = [view.last_activity for view in views if view.last_activity is not None]
        projects.append(
            ProjectView(
                path=project,
                name=path.name or project,
                parent=_parent(path),
                session_count=len(views),
                last_activity=max(activities) if activities else None,
                exists=path.is_dir(),
            )
        )
    # Aware minimum so projects without activity sort last without mixing naive and aware datetimes.
    return sorted(projects, key=lambda project: project.last_activity or datetime.min.replace(tzinfo=UTC), reverse=True)

