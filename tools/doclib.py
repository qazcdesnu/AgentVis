"""Shared project layout constants and markdown parsing for the verification tools.

@doc: docs/VerificationTools.md#2-공통-모듈
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_DOC = "docs/index.md"
ENTRY_DOC = "CLAUDE.md"
DOCS_DIR = "docs"
CODE_ROOTS = ("src", "tools", "tests")
CODE_SUFFIXES = (".py",)

_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")
_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
# A backreference so that ``` `` `x` `` ``` style spans close on the same run length.
_INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)(?:\s+#+)?\s*$")


@dataclass(frozen=True)
class Problem:
    """A single verification failure at a file location.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """

    path: Path
    line: int
    message: str

    def format(self, root: Path) -> str:
        return f"{display_path(self.path, root)}:{self.line}: {self.message}"


def display_path(path: Path, root: Path) -> str:
    """Return the path relative to the repository root when it lies inside it.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


@dataclass(frozen=True)
class Link:
    """A markdown link found in a document.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """

    source: Path
    line: int
    text: str
    target: str


def find_doc_files(root: Path) -> list[Path]:
    """Return the entry document and every markdown file under the docs directory.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    docs = []
    entry = root / ENTRY_DOC
    if entry.is_file():
        docs.append(entry)
    docs_dir = root / DOCS_DIR
    if docs_dir.is_dir():
        docs.extend(sorted(docs_dir.rglob("*.md")))
    return docs


def find_code_files(root: Path) -> list[Path]:
    """Return every code file under the code roots, skipping missing roots.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    files = []
    for code_root in CODE_ROOTS:
        directory = root / code_root
        if not directory.is_dir():
            continue
        for suffix in CODE_SUFFIXES:
            files.extend(sorted(directory.rglob(f"*{suffix}")))
    return files


def iter_prose_lines(text: str) -> Iterator[tuple[int, str]]:
    """Yield (line number, line) for lines outside fenced code blocks.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    fence = None
    for number, line in enumerate(text.splitlines(), start=1):
        match = _FENCE_RE.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield number, line


def strip_inline_code(line: str) -> str:
    """Remove inline code spans from a line.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    return _INLINE_CODE_RE.sub("", line)


def extract_links(source: Path, text: str) -> list[Link]:
    """Return links in prose, ignoring images, fenced code blocks and inline code.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    links = []
    for number, line in iter_prose_lines(text):
        for match in _LINK_RE.finditer(strip_inline_code(line)):
            links.append(Link(source, number, match.group(1), match.group(2)))
    return links


def is_external(target: str) -> bool:
    """Return whether the link target leaves the repository.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    return target.startswith(_EXTERNAL_PREFIXES)


def resolve_link(link: Link) -> tuple[Path, str]:
    """Split a link target into an absolute path and a decoded anchor.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    path_part, _, anchor = link.target.partition("#")
    if path_part:
        path = (link.source.parent / unquote(path_part)).resolve()
    else:
        path = link.source.resolve()
    return path, unquote(anchor)


def slugify(heading: str) -> str:
    """Turn heading text into its anchor.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    text = heading.replace("`", "")
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def heading_anchors(text: str) -> set[str]:
    """Return the anchors of every ATX heading outside code blocks.

    @doc: docs/VerificationTools.md#2-공통-모듈
    """
    anchors = set()
    seen: dict[str, int] = {}
    for _, line in iter_prose_lines(text):
        match = _HEADING_RE.match(line)
        if not match:
            continue
        slug = slugify(match.group(2))
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors
