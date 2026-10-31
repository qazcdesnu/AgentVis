"""The local AgentVis web server application.

@doc: docs/design/Collector.md#2-http-엔드포인트
@doc: docs/design/Collector.md#21-요청-검증
@doc: docs/design/Analysis.md#8-조회-api
@doc: docs/design/WebUI.md#5-파일-구성
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from agentvis.analysis.catalog import get_session, get_turn_graph, list_projects, list_sessions
from agentvis.collector import InvalidHookEvent, hook_event_to_raw
from agentvis.store import EventStore
from agentvis.transcript import TranscriptReader, paths_to_read

# @doc: docs/design/Collector.md#21-요청-검증
ALLOWED_HOSTS = ("127.0.0.1", "localhost")
_WEB_DIR = Path(__file__).parent / "web"


def _rejection(request: Request) -> JSONResponse | None:
    # Browsers attach Origin to cross-origin POSTs; Claude Code's hook client does not.
    if "origin" in request.headers:
        return JSONResponse({"error": "브라우저에서 온 요청(Origin 헤더)은 받지 않음"}, status_code=403)
    media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if media_type != "application/json":
        return JSONResponse({"error": "Content-Type이 application/json이 아님"}, status_code=415)
    return None


def create_app(store: EventStore, reader: TranscriptReader | None = None) -> FastAPI:
    """Build the FastAPI app that stores hook events in the given store.

    @doc: docs/design/Collector.md#2-http-엔드포인트
    @doc: docs/design/FlowGraph.md#5-조회-api
    """
    app = FastAPI(title="AgentVis")
    # Rejects DNS-rebinding requests, whose Host is the attacker's domain.
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(ALLOWED_HOSTS))

    @app.post("/hooks")
    async def receive_hook(request: Request) -> JSONResponse:
        rejection = _rejection(request)
        if rejection is not None:
            return rejection
        body = await request.body()
        try:
            event = hook_event_to_raw(body, datetime.now(UTC))
        except InvalidHookEvent as error:
            return JSONResponse({"error": str(error)}, status_code=400)
        await run_in_threadpool(store.append, event)
        if reader is not None:
            for path in paths_to_read(json.loads(event.payload)):
                reader.request(path)
        # An empty object: any field here could change the agent's behavior.
        return JSONResponse({})

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/projects")
    def projects() -> dict:
        return {"projects": jsonable_encoder(list_projects(store))}

    @app.get("/api/sessions")
    def sessions(project: str | None = None) -> dict:
        summaries = []
        for view in list_sessions(store, project):
            summary = jsonable_encoder(view)
            del summary["turns"], summary["preamble"]
            summaries.append(summary)
        return {"sessions": summaries}

    @app.get("/api/sessions/{session_id}")
    def session(session_id: str) -> dict:
        view = get_session(store, session_id)
        if view is None:
            raise HTTPException(status_code=404, detail="세션 없음")
        return jsonable_encoder(view)

    @app.get("/api/sessions/{session_id}/turns/{index}/graph")
    def turn_graph(session_id: str, index: int) -> dict:
        graph = get_turn_graph(store, session_id, index)
        if graph is None:
            raise HTTPException(status_code=404, detail="세션 또는 턴 없음")
        return jsonable_encoder(graph)

    # Mounted last so the API routes above take precedence over static files.
    app.mount("/", StaticFiles(directory=_WEB_DIR, html=True), name="web")
    return app
