"""Verify the bidirectional pointers between documents and code symbols.

@doc: docs/VerificationTools.md#4-포인터-검사기
"""

import argparse
import ast
import io
import re
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

from tools.doclib import (
    CODE_SUFFIXES,
    REPO_ROOT,
    Problem,
    display_path,
    extract_links,
    find_code_files,
    find_doc_files,
    heading_anchors,
    is_external,
    resolve_link,
)

_DOC_TAG_RE = re.compile(r"@doc:\s*(\S+)")
_LINE_ANCHOR_RE = re.compile(r"L\d+(-L?\d+)?")
_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
_DEFINITIONS = (*_FUNCTIONS, ast.ClassDef)


@dataclass(frozen=True)
class SymbolRef:
    """A code symbol identified by its file and qualified name; the module is the empty name.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """

    file: Path
    qualname: str

    def is_related(self, other: "SymbolRef") -> bool:
        if self.file != other.file:
            return False
        mine, theirs = self.qualname, other.qualname
        return (
            mine == theirs
            or not mine
            or not theirs
            or mine.startswith(theirs + ".")
            or theirs.startswith(mine + ".")
        )


@dataclass(frozen=True)
class CodePointer:
    """A pointer from a document line to a code symbol.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """

    doc: Path
    line: int
    symbol: SymbolRef


@dataclass(frozen=True)
class DocPointer:
    """A pointer from a code symbol to the document it is based on.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """

    symbol: SymbolRef
    line: int
    doc: Path
    anchor: str


@dataclass
class ModuleIndex:
    """The AST analysis of one code file.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """

    path: Path
    symbols: dict[str, ast.AST] = field(default_factory=dict)
    doc_pointers: list[DocPointer] = field(default_factory=list)
    problems: list[Problem] = field(default_factory=list)


def index_module(path: Path, root: Path) -> ModuleIndex:
    """Parse a code file into its symbols and its pointers to documents.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """
    index = ModuleIndex(path)
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        index.problems.append(Problem(path, error.lineno or 1, f"파싱 실패: {error.msg}"))
        return index
    index.symbols[""] = tree
    starts: dict[int, str] = {}
    _collect_symbols(tree.body, "", index.symbols, starts, in_function=False)
    for qualname, node in index.symbols.items():
        _add_docstring_pointers(index, root, qualname, node)
    _add_comment_pointers(index, root, source, starts)
    return index


def _collect_symbols(
    body: list[ast.stmt],
    prefix: str,
    symbols: dict[str, ast.AST],
    starts: dict[int, str],
    in_function: bool,
) -> None:
    for node in body:
        if isinstance(node, _DEFINITIONS):
            qualname = prefix + node.name
            symbols[qualname] = node
            starts[min([node.lineno] + [d.lineno for d in node.decorator_list])] = qualname
            _collect_symbols(
                node.body, qualname + ".", symbols, starts, isinstance(node, _FUNCTIONS)
            )
        elif not in_function and isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    symbols[prefix + target.id] = node
                    starts[node.lineno] = prefix + target.id


def _make_doc_pointer(symbol: SymbolRef, line: int, target: str, root: Path) -> DocPointer:
    path_part, _, anchor = target.partition("#")
    return DocPointer(symbol, line, (root / unquote(path_part)).resolve(), unquote(anchor))


def _add_docstring_pointers(index: ModuleIndex, root: Path, qualname: str, node: ast.AST) -> None:
    if not isinstance(node, (ast.Module, *_DEFINITIONS)) or ast.get_docstring(node) is None:
        return
    docstring = node.body[0]
    symbol = SymbolRef(index.path, qualname)
    for offset, line in enumerate(docstring.value.value.splitlines()):
        for match in _DOC_TAG_RE.finditer(line):
            index.doc_pointers.append(
                _make_doc_pointer(symbol, docstring.lineno + offset, match.group(1), root)
            )


def _add_comment_pointers(index: ModuleIndex, root: Path, source: str, starts: dict[int, str]) -> None:
    lines = source.splitlines()
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type != tokenize.COMMENT:
            continue
        matches = list(_DOC_TAG_RE.finditer(token.string))
        if not matches:
            continue
        row, column = token.start
        if lines[row - 1][:column].strip():
            index.problems.append(Problem(index.path, row, "코드 줄 끝의 @doc 주석은 허용되지 않음"))
            continue
        qualname = _symbol_below(lines, row, starts)
        if qualname is None:
            index.problems.append(Problem(index.path, row, "@doc 주석 아래에 심볼 정의가 없음"))
            continue
        symbol = SymbolRef(index.path, qualname)
        for match in matches:
            index.doc_pointers.append(_make_doc_pointer(symbol, row, match.group(1), root))


def _symbol_below(lines: list[str], row: int, starts: dict[int, str]) -> str | None:
    for number in range(row + 1, len(lines) + 1):
        stripped = lines[number - 1].strip()
        if stripped and not stripped.startswith("#"):
            return starts.get(number)
    return None


def _describe(symbol: SymbolRef, root: Path) -> str:
    shown = display_path(symbol.file, root)
    return f"{shown}#{symbol.qualname}" if symbol.qualname else shown


def collect_code_pointers(
    root: Path, modules: dict[Path, ModuleIndex]
) -> tuple[list[CodePointer], list[Problem]]:
    """Gather pointers from documents to code and report those that do not resolve.

    Code files referenced from documents but outside the code roots are indexed into
    ``modules`` on demand.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """
    pointers = []
    problems = []
    for doc in find_doc_files(root):
        doc = doc.resolve()
        for link in extract_links(doc, doc.read_text(encoding="utf-8")):
            if is_external(link.target):
                continue
            path, anchor = resolve_link(link)
            if path.suffix not in CODE_SUFFIXES:
                continue
            if not path.is_file():
                problems.append(Problem(doc, link.line, f"코드 포인터 대상 파일 없음: {link.target}"))
                continue
            if _LINE_ANCHOR_RE.fullmatch(anchor):
                problems.append(Problem(doc, link.line, f"줄 번호 포인터는 금지됨: {link.target}"))
                continue
            if path not in modules:
                modules[path] = index_module(path, root)
            if anchor not in modules[path].symbols:
                problems.append(Problem(doc, link.line, f"AST에 심볼 없음: {link.target}"))
                continue
            pointers.append(CodePointer(doc, link.line, SymbolRef(path, anchor)))
    return pointers, problems


def check_doc_pointers(root: Path, modules: dict[Path, ModuleIndex]) -> list[Problem]:
    """Report pointers from code whose target document or heading anchor is missing.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """
    problems = []
    anchor_cache: dict[Path, set[str]] = {}
    for module in modules.values():
        for pointer in module.doc_pointers:
            target = display_path(pointer.doc, root)
            if pointer.doc.suffix != ".md" or not pointer.doc.is_file():
                problems.append(Problem(module.path, pointer.line, f"근거 문서 없음: {target}"))
                continue
            if not pointer.anchor:
                continue
            if pointer.doc not in anchor_cache:
                anchor_cache[pointer.doc] = heading_anchors(pointer.doc.read_text(encoding="utf-8"))
            if pointer.anchor not in anchor_cache[pointer.doc]:
                problems.append(
                    Problem(module.path, pointer.line, f"앵커 없음: {target}#{pointer.anchor}")
                )
    return problems


def check_coverage(root: Path, modules: dict[Path, ModuleIndex]) -> list[Problem]:
    """Report modules and public top-level symbols in the code roots lacking a document pointer.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """
    problems = []
    for path in find_code_files(root):
        module = modules[path.resolve()]
        tree = module.symbols.get("")
        if tree is None or not tree.body:
            continue
        owners = {pointer.symbol.qualname for pointer in module.doc_pointers}
        if "" not in owners:
            problems.append(Problem(module.path, 1, "모듈 docstring에 @doc 포인터 없음"))
        for qualname, node in module.symbols.items():
            is_public_top_level = qualname and "." not in qualname and not qualname.startswith("_")
            if is_public_top_level and isinstance(node, _DEFINITIONS) and qualname not in owners:
                problems.append(Problem(module.path, node.lineno, f"공개 심볼 {qualname}에 @doc 포인터 없음"))
    return problems


def check_reciprocity(
    root: Path, code_pointers: list[CodePointer], modules: dict[Path, ModuleIndex]
) -> list[Problem]:
    """Report pointers in either direction that have no pointer back between related symbols.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """
    doc_pointers = [pointer for module in modules.values() for pointer in module.doc_pointers]
    problems = []
    for code_pointer in code_pointers:
        if not any(
            pointer.doc == code_pointer.doc and pointer.symbol.is_related(code_pointer.symbol)
            for pointer in doc_pointers
        ):
            problems.append(
                Problem(
                    code_pointer.doc,
                    code_pointer.line,
                    f"역방향 포인터 없음: {_describe(code_pointer.symbol, root)} 또는 관련 심볼이 "
                    f"{display_path(code_pointer.doc, root)}를 가리켜야 함",
                )
            )
    for doc_pointer in doc_pointers:
        if not doc_pointer.doc.is_file():
            continue
        if not any(
            pointer.doc == doc_pointer.doc and pointer.symbol.is_related(doc_pointer.symbol)
            for pointer in code_pointers
        ):
            problems.append(
                Problem(
                    doc_pointer.symbol.file,
                    doc_pointer.line,
                    f"역방향 포인터 없음: {display_path(doc_pointer.doc, root)}가 "
                    f"{_describe(doc_pointer.symbol, root)} 또는 관련 심볼을 가리켜야 함",
                )
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    """Run every pointer check and print problems; return the exit code.

    @doc: docs/VerificationTools.md#4-포인터-검사기
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    root = parser.parse_args(argv).root.resolve()
    modules = {path.resolve(): index_module(path.resolve(), root) for path in find_code_files(root)}
    code_pointers, problems = collect_code_pointers(root, modules)
    problems = (
        [problem for module in modules.values() for problem in module.problems]
        + problems
        + check_doc_pointers(root, modules)
        + check_coverage(root, modules)
        + check_reciprocity(root, code_pointers, modules)
    )
    for problem in problems:
        print(problem.format(root))
    if problems:
        print(f"check_pointers: 문제 {len(problems)}건")
        return 1
    doc_pointer_count = sum(len(module.doc_pointers) for module in modules.values())
    print(f"check_pointers: 통과 (문서→코드 {len(code_pointers)}개, 코드→문서 {doc_pointer_count}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
