"""Check web screen files for external addresses and vendored libraries against their recorded hashes.

@doc: docs/VerificationTools.md#10-웹-정적-파일-검사기
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

from tools.doclib import REPO_ROOT, Problem, extract_links, is_external, iter_prose_lines, resolve_link

# @doc: docs/VerificationTools.md#10-웹-정적-파일-검사기
WEB_DIR = "src/agentvis/web"
# @doc: docs/VerificationTools.md#10-웹-정적-파일-검사기
VENDOR_DIR = "src/agentvis/web/vendor"
# @doc: docs/VerificationTools.md#10-웹-정적-파일-검사기
WEB_DOC = "docs/design/WebUI.md"
# @doc: docs/VerificationTools.md#10-웹-정적-파일-검사기
ALLOWED_URLS = ("http://www.w3.org/2000/svg", "http://www.w3.org/1999/xlink", "http://www.w3.org/1999/xhtml")

_WEB_SUFFIXES = (".html", ".js", ".css")
_ABSOLUTE_URL_RE = re.compile(r"https?://[^\s\"'`)<>]*")
_RELATIVE_URL_RE = re.compile(r"(?:\bsrc\s*=|\bhref\s*=|\burl\(|\bimport\b|\bfrom\b)\s*[\"'(]?\s*(//[^\s\"'`)<>]*)")
_HASH_CELL_RE = re.compile(r"\|\s*`([0-9a-f]{64})`\s*\|\s*$")


def _is_inside(path: Path, directory: Path) -> bool:
    return path == directory or directory in path.parents


def external_references(root: Path) -> list[Problem]:
    """Return external addresses in our own web files, skipping the vendor directory.

    @doc: docs/VerificationTools.md#10-웹-정적-파일-검사기
    """
    web_dir, vendor_dir = root / WEB_DIR, root / VENDOR_DIR
    if not web_dir.is_dir():
        return []
    problems = []
    for path in sorted(web_dir.rglob("*")):
        if not path.is_file() or path.suffix not in _WEB_SUFFIXES or _is_inside(path, vendor_dir):
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in _ABSOLUTE_URL_RE.finditer(line):
                if not match.group(0).startswith(ALLOWED_URLS):
                    problems.append(Problem(path, number, f"외부 주소: {match.group(0)}"))
            for match in _RELATIVE_URL_RE.finditer(line):
                problems.append(Problem(path, number, f"외부 주소(프로토콜 상대): {match.group(1)}"))
    return problems


def vendor_problems(root: Path) -> list[Problem]:
    """Return vendored files missing from the library table, hash mismatches and missing listed files.

    @doc: docs/VerificationTools.md#10-웹-정적-파일-검사기
    """
    doc, vendor_dir = root / WEB_DOC, (root / VENDOR_DIR).resolve()
    text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
    entry_lines = {}
    for number, line in iter_prose_lines(text):
        hash_match = _HASH_CELL_RE.search(line)
        if line.lstrip().startswith("|") and hash_match:
            entry_lines[number] = hash_match.group(1)
    problems, linked = [], set()
    for link in extract_links(doc, text):
        if link.line not in entry_lines or is_external(link.target):
            continue
        path, _ = resolve_link(link)
        if not _is_inside(path, vendor_dir):
            continue
        linked.add(path)
        first_cell = text.splitlines()[link.line - 1].strip().lstrip("|").split("|", 1)[0]
        if f"]({link.target})" not in first_cell:
            continue
        if not path.is_file():
            problems.append(Problem(doc, link.line, f"라이브러리 파일 없음: {link.target}"))
        elif hashlib.sha256(path.read_bytes()).hexdigest() != entry_lines[link.line]:
            problems.append(Problem(doc, link.line, f"SHA-256 불일치: {link.target}"))
    if vendor_dir.is_dir():
        for path in sorted(vendor_dir.rglob("*")):
            if path.is_file() and path not in linked:
                problems.append(Problem(path, 1, f"{WEB_DOC}의 라이브러리 표에 없는 파일"))
    return problems


def main(argv: list[str] | None = None) -> int:
    """Report problems in the web files and vendored libraries; return the exit code.

    @doc: docs/VerificationTools.md#10-웹-정적-파일-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    problems = external_references(root) + vendor_problems(root)
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_web: 문제 {len(problems)}건")
        return 1
    web_dir, vendor_dir = root / WEB_DIR, root / VENDOR_DIR
    own = [p for p in web_dir.rglob("*") if p.is_file() and p.suffix in _WEB_SUFFIXES and not _is_inside(p, vendor_dir)] if web_dir.is_dir() else []
    vendored = [p for p in vendor_dir.rglob("*") if p.is_file()] if vendor_dir.is_dir() else []
    print(f"check_web: 통과 (화면 파일 {len(own)}개, 라이브러리 파일 {len(vendored)}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
