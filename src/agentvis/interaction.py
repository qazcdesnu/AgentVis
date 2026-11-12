"""Screen usage records kept in experiment mode (I60).

@doc: docs/design/WebUI.md#92-api와-기록-파일
"""

import json
import re
import threading
from datetime import UTC, datetime
from pathlib import Path

from agentvis import __version__

# @doc: docs/design/WebUI.md#92-api와-기록-파일
MAX_BODY_BYTES = 64 * 1024
# @doc: docs/design/WebUI.md#92-api와-기록-파일
MAX_EVENTS = 200
_TYPE = re.compile(r"[a-z_]{1,32}")
_AT_CHARS = 40
_DETAIL_CHARS = 2000


class InvalidInteractions(ValueError):
    """The body is not a list of screen usage events the log accepts.

    @doc: docs/design/WebUI.md#92-api와-기록-파일
    """


def parse_events(body: bytes) -> list[dict]:
    """Check a POST body and return its events, or raise InvalidInteractions.

    @doc: docs/design/WebUI.md#92-api와-기록-파일
    """
    if len(body) > MAX_BODY_BYTES:
        raise InvalidInteractions("본문이 너무 큼")
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise InvalidInteractions(f"본문이 UTF-8 JSON이 아님: {error}") from error
    events = data.get("events") if isinstance(data, dict) else None
    if not isinstance(events, list) or len(events) > MAX_EVENTS:
        raise InvalidInteractions(f"'events'가 {MAX_EVENTS}개 이하의 목록이 아님")
    for event in events:
        if not isinstance(event, dict):
            raise InvalidInteractions("항목이 JSON 객체가 아님")
        if not isinstance(event.get("type"), str) or not _TYPE.fullmatch(event["type"]):
            raise InvalidInteractions("'type'이 영문 소문자·_ 1~32자가 아님")
        if not isinstance(event.get("at"), str) or len(event["at"]) > _AT_CHARS:
            raise InvalidInteractions("'at'이 40자 이하 문자열이 아님")
        detail = event.get("detail", {})
        if not isinstance(detail, dict) or len(json.dumps(detail, ensure_ascii=False)) > _DETAIL_CHARS:
            raise InvalidInteractions("'detail'이 2,000자 이하의 객체가 아님")
    return [{"at": event["at"], "type": event["type"], "detail": event.get("detail", {})} for event in events]


class InteractionLog:
    """Append-only JSON Lines file of one participant's screen usage.

    @doc: docs/design/WebUI.md#92-api와-기록-파일
    """

    def __init__(self, path: Path, participant: str) -> None:
        self.path = path
        self.participant = participant
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._write([{"type": "server_start", "participant": participant, "version": __version__}])

    def append(self, events: list[dict]) -> int:
        """Append checked events, one line each, and return how many were written.

        @doc: docs/design/WebUI.md#92-api와-기록-파일
        """
        self._write([{"participant": self.participant, **event} for event in events])
        return len(events)

    def _write(self, records: list[dict]) -> None:
        received_at = datetime.now(UTC).isoformat()
        lines = "".join(json.dumps({"received_at": received_at, **record}, ensure_ascii=False) + "\n" for record in records)
        with self._lock, self.path.open("a", encoding="utf-8") as file:
            file.write(lines)
