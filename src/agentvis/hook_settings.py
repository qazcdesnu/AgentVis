"""Add and remove AgentVis hooks in a Claude Code settings file.

@doc: docs/design/Cli.md#3-hook-설정-편집
"""

import copy
import json
import os
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# @doc: docs/design/Cli.md#31-식별
HOOK_EVENTS = (
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "PermissionRequest",
    "PermissionDenied",
    "Notification",
    "SubagentStart",
    "SubagentStop",
    "Stop",
    "StopFailure",
    "PreCompact",
    "PostCompact",
    "SessionEnd",
)
# @doc: docs/design/Cli.md#31-식별
HOOK_TIMEOUT_SECONDS = 2

_CLIENT = "agentvis"


class SettingsError(Exception):
    """The settings file is unreadable or has a structure AgentVis will not touch.

    @doc: docs/design/Cli.md#32-추가와-제거
    """


def hook_url(port: int) -> str:
    """Return the collector URL that identifies AgentVis hooks.

    @doc: docs/design/Cli.md#31-식별
    """
    return f"http://127.0.0.1:{port}/hooks?client={_CLIENT}"


def is_agentvis_hook(handler: object) -> bool:
    """Return whether a hook handler was installed by AgentVis.

    @doc: docs/design/Cli.md#31-식별
    """
    if not isinstance(handler, dict) or handler.get("type") != "http":
        return False
    url = handler.get("url")
    if not isinstance(url, str):
        return False
    return _CLIENT in parse_qs(urlparse(url).query).get("client", [])


def _hooks_object(settings: dict) -> dict:
    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        raise SettingsError("설정의 'hooks'가 객체가 아님")
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            raise SettingsError(f"'hooks.{event}'가 목록이 아님")
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                raise SettingsError(f"'hooks.{event}'에 형식이 다른 그룹이 있음")
    return hooks


def uninstall_hooks(settings: dict) -> tuple[dict, int]:
    """Return settings without AgentVis hooks and how many were removed.

    @doc: docs/design/Cli.md#32-추가와-제거
    """
    hooks = _hooks_object(settings)
    result = copy.deepcopy(settings)
    if "hooks" not in settings:
        return result, 0
    removed = 0
    kept_hooks: dict = {}
    for event, groups in hooks.items():
        kept_groups = []
        for group in groups:
            handlers = [handler for handler in group["hooks"] if not is_agentvis_hook(handler)]
            removed += len(group["hooks"]) - len(handlers)
            if handlers:
                kept_groups.append({**copy.deepcopy(group), "hooks": copy.deepcopy(handlers)})
            elif not group["hooks"]:
                kept_groups.append(copy.deepcopy(group))
        if kept_groups or not groups:
            kept_hooks[event] = kept_groups
    if removed == 0:
        return result, 0
    if kept_hooks:
        result["hooks"] = kept_hooks
    else:
        del result["hooks"]
    return result, removed


def install_hooks(settings: dict, port: int) -> tuple[dict, int]:
    """Return settings with one AgentVis hook per event and how many were added.

    @doc: docs/design/Cli.md#32-추가와-제거
    """
    result, _ = uninstall_hooks(settings)
    hooks = result.setdefault("hooks", {})
    handler = {"type": "http", "url": hook_url(port), "timeout": HOOK_TIMEOUT_SECONDS}
    for event in HOOK_EVENTS:
        hooks.setdefault(event, []).append({"hooks": [dict(handler)]})
    return result, len(HOOK_EVENTS)


def default_settings_path() -> Path:
    """Return the Claude Code user settings file.

    @doc: docs/design/Cli.md#33-파일-입출력
    """
    return Path.home() / ".claude" / "settings.json"


def load_settings(path: Path) -> dict:
    """Read a settings file, treating a missing file as empty settings.

    @doc: docs/design/Cli.md#33-파일-입출력
    """
    if not path.exists():
        return {}
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SettingsError(f"설정 파일이 JSON이 아님: {path}: {error}") from error
    if not isinstance(settings, dict):
        raise SettingsError(f"설정 파일이 JSON 객체가 아님: {path}")
    return settings


def backup_settings(path: Path, backup_dir: Path) -> Path | None:
    """Copy an existing settings file into the backup directory and return the copy.

    @doc: docs/design/Cli.md#33-파일-입출력
    """
    if not path.exists():
        return None
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    target = backup_dir / f"settings-{stamp}.json"
    # Windows clocks tick about every 16 ms, so two quick backups can share a timestamp.
    counter = 0
    while target.exists():
        counter += 1
        target = backup_dir / f"settings-{stamp}-{counter}.json"
    shutil.copyfile(path, target)
    return target


def save_settings(path: Path, settings: dict) -> None:
    """Atomically write settings, writing through symlinks and keeping file permissions.

    @doc: docs/design/Cli.md#33-파일-입출력
    """
    target = path.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = target.stat().st_mode & 0o7777 if target.exists() else None
    text = json.dumps(settings, indent=2, ensure_ascii=False) + "\n"
    descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(text)
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
