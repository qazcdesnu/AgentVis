"""Tests for adding and removing AgentVis hooks in Claude Code settings.

@doc: docs/design/Cli.md#4-테스트
"""

import copy
import json
import os
import stat
import unittest

from agentvis.hook_settings import (
    HOOK_EVENTS,
    SettingsError,
    backup_settings,
    hook_url,
    install_hooks,
    is_agentvis_hook,
    load_settings,
    save_settings,
    uninstall_hooks,
)
from tests.support import RepoTestCase

_USER_HOOK = {"type": "command", "command": "echo user"}
_USER_SETTINGS = {
    "model": "opus",
    "hooks": {
        "Stop": [{"hooks": [_USER_HOOK]}],
        "PreToolUse": [{"matcher": "Bash", "hooks": [_USER_HOOK]}],
        "CustomEvent": [{"hooks": [{"type": "http", "url": "http://127.0.0.1:9/x"}]}],
    },
    "permissions": {"allow": ["Bash(ls)"]},
}


def _agentvis_urls(settings: dict) -> dict[str, list[str]]:
    return {
        event: [handler["url"] for group in groups for handler in group["hooks"] if is_agentvis_hook(handler)]
        for event, groups in settings.get("hooks", {}).items()
    }


class InstallUninstallTest(unittest.TestCase):
    """@doc: docs/design/Cli.md#4-테스트"""

    def test_install_on_empty_settings_adds_one_hook_per_event(self) -> None:
        self.assertEqual(len(HOOK_EVENTS), 14)
        self.assertNotIn("SessionStart", HOOK_EVENTS)
        installed, count = install_hooks({}, 8765)
        self.assertEqual(count, len(HOOK_EVENTS))
        self.assertEqual(list(installed["hooks"]), list(HOOK_EVENTS))
        for event in HOOK_EVENTS:
            self.assertEqual(
                installed["hooks"][event],
                [{"hooks": [{"type": "http", "url": hook_url(8765), "timeout": 2}]}],
            )

    def test_install_is_idempotent_and_follows_port(self) -> None:
        once, _ = install_hooks(_USER_SETTINGS, 8765)
        twice, _ = install_hooks(once, 8765)
        self.assertEqual(json.dumps(once), json.dumps(twice))
        moved, _ = install_hooks(twice, 9100)
        self.assertTrue(all(urls == [hook_url(9100)] for urls in _agentvis_urls(moved).values() if urls))

    def test_user_hooks_and_other_keys_survive_in_order(self) -> None:
        original = copy.deepcopy(_USER_SETTINGS)
        installed, _ = install_hooks(_USER_SETTINGS, 8765)
        self.assertEqual(_USER_SETTINGS, original)
        self.assertEqual(list(installed), ["model", "hooks", "permissions"])
        self.assertEqual(installed["hooks"]["Stop"][0], {"hooks": [_USER_HOOK]})
        self.assertEqual(installed["hooks"]["CustomEvent"], _USER_SETTINGS["hooks"]["CustomEvent"])
        removed, count = uninstall_hooks(installed)
        self.assertEqual(count, len(HOOK_EVENTS))
        self.assertEqual(json.dumps(removed), json.dumps(_USER_SETTINGS))

    def test_mixed_group_keeps_user_handler(self) -> None:
        mixed = {"hooks": {"Stop": [{"hooks": [_USER_HOOK, {"type": "http", "url": hook_url(1)}]}]}}
        removed, count = uninstall_hooks(mixed)
        self.assertEqual(count, 1)
        self.assertEqual(removed, {"hooks": {"Stop": [{"hooks": [_USER_HOOK]}]}})

    def test_uninstall_drops_emptied_containers(self) -> None:
        installed, _ = install_hooks({"model": "opus"}, 8765)
        self.assertEqual(uninstall_hooks(installed), ({"model": "opus"}, len(HOOK_EVENTS)))
        self.assertEqual(uninstall_hooks({"model": "opus"}), ({"model": "opus"}, 0))

    def test_identification_requires_http_type_and_client_query(self) -> None:
        self.assertTrue(is_agentvis_hook({"type": "http", "url": hook_url(8765)}))
        self.assertFalse(is_agentvis_hook({"type": "command", "command": hook_url(8765)}))
        self.assertFalse(is_agentvis_hook({"type": "http", "url": "http://127.0.0.1:8765/hooks"}))
        self.assertFalse(is_agentvis_hook({"type": "http", "url": "http://x/?client=agentvis2"}))
        self.assertFalse(is_agentvis_hook("not a dict"))

    def test_unexpected_structure_is_refused(self) -> None:
        for settings in ({"hooks": []}, {"hooks": {"Stop": {}}}, {"hooks": {"Stop": ["x"]}}, {"hooks": {"Stop": [{"hooks": {}}]}}):
            with self.subTest(settings=settings), self.assertRaises(SettingsError):
                install_hooks(settings, 8765)


class SettingsFileTest(RepoTestCase):
    """@doc: docs/design/Cli.md#4-테스트"""

    def test_missing_file_is_empty_and_invalid_file_is_refused(self) -> None:
        self.assertEqual(load_settings(self.root / "absent.json"), {})
        for text in ("not json", "[1]"):
            path = self.write("bad.json", text)
            with self.subTest(text=text), self.assertRaises(SettingsError):
                load_settings(path)

    def test_save_round_trip(self) -> None:
        path = self.write("settings.json", "{}\n")
        save_settings(path, _USER_SETTINGS)
        self.assertEqual(load_settings(path), _USER_SETTINGS)
        self.assertEqual([p.name for p in path.parent.iterdir()], ["settings.json"])

    # Windows needs admin rights or developer mode for symlinks and has no POSIX permission bits.
    @unittest.skipIf(os.name == "nt", "심볼릭 링크와 권한 비트는 POSIX 기능")
    def test_save_round_trip_keeps_mode_and_symlink(self) -> None:
        target = self.write("dotfiles/settings.json", "{}\n")
        os.chmod(target, 0o600)
        link = self.root / ".claude" / "settings.json"
        link.parent.mkdir()
        link.symlink_to(target)
        save_settings(link, _USER_SETTINGS)
        self.assertTrue(link.is_symlink())
        self.assertEqual(load_settings(link), _USER_SETTINGS)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
        self.assertTrue(target.read_text(encoding="utf-8").endswith("}\n"))
        self.assertEqual([p.name for p in target.parent.iterdir()], ["settings.json"])

    def test_save_creates_missing_parent(self) -> None:
        path = self.root / "new" / "settings.json"
        save_settings(path, {"모델": "한글"})
        self.assertIn("한글", path.read_text(encoding="utf-8"))

    def test_backup_copies_content_with_unique_names(self) -> None:
        path = self.write("settings.json", '{"a": 1}\n')
        backups = self.root / "backups"
        first = backup_settings(path, backups)
        second = backup_settings(path, backups)
        self.assertNotEqual(first, second)
        self.assertEqual(first.read_text(encoding="utf-8"), '{"a": 1}\n')
        self.assertIsNone(backup_settings(self.root / "absent.json", backups))


if __name__ == "__main__":
    unittest.main()
