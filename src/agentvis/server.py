"""The local AgentVis web server application.

@doc: docs/design/Collector.md#2-http-엔드포인트
@doc: docs/design/Collector.md#21-요청-검증
"""

from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from agentvis.collector import InvalidHookEvent, hook_event_to_raw
from agentvis.store import EventStore

# @doc: docs/design/Collector.md#21-요청-검증
ALLOWED_HOSTS = ("127.0.0.1", "localhost")


def _rejection(request: Request) -> JSONResponse | None:
    # Browsers attach Origin to cross-origin POSTs; Claude Code's hook client does not.
    if "origin" in request.headers:
        return JSONResponse({"error": "브라우저에서 온 요청(Origin 헤더)은 받지 않음"}, status_code=403)
    media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if media_type != "application/json":
        return JSONResponse({"error": "Content-Type이 application/json이 아님"}, status_code=415)
    return None


def create_app(store: EventStore) -> FastAPI:
    """Build the FastAPI app that stores hook events in the given store.

    @doc: docs/design/Collector.md#2-http-엔드포인트
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
        # An empty object: any field here could change the agent's behavior.
        return JSONResponse({})

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
