"""The local AgentVis web server application.

@doc: docs/design/Collector.md#2-http-엔드포인트
"""

from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from agentvis.collector import InvalidHookEvent, hook_event_to_raw
from agentvis.store import EventStore


def create_app(store: EventStore) -> FastAPI:
    """Build the FastAPI app that stores hook events in the given store.

    @doc: docs/design/Collector.md#2-http-엔드포인트
    """
    app = FastAPI(title="AgentVis")

    @app.post("/hooks")
    async def receive_hook(request: Request) -> JSONResponse:
        body = await request.body()
        try:
            event = hook_event_to_raw(body, datetime.now(UTC))
        except InvalidHookEvent as error:
            return JSONResponse({"error": str(error)}, status_code=400)
        await run_in_threadpool(store.append, event)
        # An empty object: any field here could change the agent's behavior.
        return JSONResponse({})

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
