"""Convert Claude Code hook POST bodies into raw events.

@doc: docs/design/Collector.md#1-이벤트-변환
"""

import json
from datetime import datetime

from agentvis.store import RawEvent


class InvalidHookEvent(ValueError):
    """The POST body is not a hook event the collector can store.

    @doc: docs/design/Collector.md#1-이벤트-변환
    """


def _optional_text(event: dict, key: str) -> str | None:
    value = event.get(key)
    return value if isinstance(value, str) else None


def hook_event_to_raw(body: bytes, received_at: datetime) -> RawEvent:
    """Turn a hook POST body into a raw event, keeping the body text verbatim.

    @doc: docs/design/Collector.md#1-이벤트-변환
    """
    try:
        text = body.decode("utf-8")
        event = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise InvalidHookEvent(f"본문이 UTF-8 JSON이 아님: {error}") from error
    if not isinstance(event, dict):
        raise InvalidHookEvent("본문이 JSON 객체가 아님")
    for key in ("hook_event_name", "session_id"):
        if not isinstance(event.get(key), str):
            raise InvalidHookEvent(f"'{key}'가 없거나 문자열이 아님")
    return RawEvent(
        source="hook",
        kind=event["hook_event_name"],
        session_id=event["session_id"],
        prompt_id=_optional_text(event, "prompt_id"),
        tool_use_id=_optional_text(event, "tool_use_id"),
        cwd=_optional_text(event, "cwd"),
        occurred_at=received_at,
        payload=text,
    )
