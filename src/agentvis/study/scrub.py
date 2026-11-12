"""A copy of a scenario folder fit to publish: only the lines AgentVis reads, without account fields (M11-T2).

@doc: docs/design/Study.md#5-공개용-익명화-m11-t2
"""

import json
import re
from pathlib import Path

from agentvis.transcript import record_to_raw

# @doc: docs/design/Study.md#5-공개용-익명화-m11-t2
SCRUB_KEYS = ("accountUuid", "organizationUuid", "userEmail")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_HOME = re.compile(r"(?:/Users/|/home/|[A-Za-z]:\\\\?Users\\\\?)([^/\\\s\"']+)")
_ALLOWED_EMAIL = re.compile(r"^noreply@anthropic\.com$|@example\.(?:com|org)$")
_ALLOWED_NAMES = {"study", "runner", "runneradmin"}
_TEXT_SUFFIXES = {".jsonl", ".json", ".diff", ".md", ".txt"}


def _drop_keys(value: object) -> object:
    if isinstance(value, dict):
        return {key: _drop_keys(item) for key, item in value.items() if key not in SCRUB_KEYS}
    if isinstance(value, list):
        return [_drop_keys(item) for item in value]
    return value


def _replace(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def _scrub_transcript(path: Path, replacements: list[tuple[str, str]]) -> str:
    lines = []
    for line in path.read_bytes().splitlines(keepends=True):
        if record_to_raw(line if line.endswith(b"\n") else line + b"\n") is None:
            continue
        record = _drop_keys(json.loads(line))
        lines.append(_replace(json.dumps(record, ensure_ascii=False), replacements) + "\n")
    return "".join(lines)


def personal_findings(folder: Path) -> list[str]:
    """Lines in the folder's text files that look like an email address or a person's home directory.

    @doc: docs/design/Study.md#5-공개용-익명화-m11-t2
    """
    findings = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.suffix not in _TEXT_SUFFIXES:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            where = f"{path.relative_to(folder).as_posix()}:{number}"
            findings += [f"{where}: 이메일: {email}" for email in _EMAIL.findall(line) if not _ALLOWED_EMAIL.search(email)]
            findings += [f"{where}: 홈 경로: {match.group(0)}" for match in _HOME.finditer(line) if match.group(1) not in _ALLOWED_NAMES]
    return findings


def scrub_folder(source: Path, out: Path, replacements: list[tuple[str, str]]) -> list[str]:
    """Write the publishable copy of source into out (which must not exist) and return what still looks personal.

    @doc: docs/design/Study.md#5-공개용-익명화-m11-t2
    """
    if out.exists():
        raise FileExistsError(f"결과 폴더가 이미 있음: {out}")
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".jsonl" and len(relative.parts) >= 2 and path.name != "runs.jsonl":
            target.write_text(_scrub_transcript(path, replacements), encoding="utf-8")
        elif path.suffix in _TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8")
            if path.name.endswith(".meta.json") or path.name == "key.json":
                text = json.dumps(_drop_keys(json.loads(text)), ensure_ascii=False, indent=2) + "\n"
            target.write_text(_replace(text, replacements), encoding="utf-8")
    return personal_findings(out)
