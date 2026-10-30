"""Tests for the document-code pointer checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests.support import RepoTestCase
from tools.check_pointers import SymbolRef, index_module, main

_DOC = "# A\n\n## 1. Spec\n\n[run](../src/mod.py#Thing.run) [d](../src/mod.py#_decorated)\n"
_MODULE = """'''Module.

@doc: docs/A.md#1-spec
'''

# @doc: docs/A.md
@staticmethod
def _decorated():
    pass


class Thing:
    '''@doc: docs/A.md'''

    def run(self):
        return 1
"""


class CheckPointersTest(RepoTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("docs/A.md", _DOC)
        self.module = self.write("src/mod.py", _MODULE)

    def run_checker(self) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root)])
        return code, output.getvalue()

    def test_valid_bidirectional_pointers_pass(self) -> None:
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_comment_pointer_attaches_to_decorated_symbol_below(self) -> None:
        index = index_module(self.module, self.root)
        owners = {pointer.symbol.qualname for pointer in index.doc_pointers}
        self.assertEqual(owners, {"", "_decorated", "Thing"})
        self.assertEqual(index.problems, [])

    def test_reports_missing_symbol(self) -> None:
        self.write("docs/A.md", _DOC.replace("Thing.run", "Thing.gone"))
        code, output = self.run_checker()
        self.assertEqual(code, 1)
        self.assertIn("AST에 심볼 없음: ../src/mod.py#Thing.gone", output)

    def test_reports_line_number_pointer(self) -> None:
        self.write("docs/A.md", _DOC.replace("#Thing.run", "#L3"))
        self.assertIn("줄 번호 포인터는 금지됨", self.run_checker()[1])

    def test_reports_unattached_comment_pointers(self) -> None:
        self.write("src/mod.py", _MODULE + "\nLIMIT = 3  # @doc: docs/A.md\n# @doc: docs/A.md\n")
        output = self.run_checker()[1]
        self.assertIn("코드 줄 끝의 @doc 주석은 허용되지 않음", output)
        self.assertIn("@doc 주석 아래에 심볼 정의가 없음", output)

    def test_reports_missing_document_and_anchor(self) -> None:
        self.write("src/mod.py", _MODULE.replace("docs/A.md#1-spec", "docs/A.md#nope\n@doc: docs/Gone.md"))
        output = self.run_checker()[1]
        self.assertIn("앵커 없음: docs/A.md#nope", output)
        self.assertIn("근거 문서 없음: docs/Gone.md", output)

    def test_reports_missing_coverage(self) -> None:
        self.write("src/bare.py", "def helper():\n    pass\n")
        output = self.run_checker()[1]
        self.assertIn("src/bare.py:1: 모듈 docstring에 @doc 포인터 없음", output)
        self.assertIn("공개 심볼 helper에 @doc 포인터 없음", output)

    def test_reports_missing_back_pointers(self) -> None:
        self.write("docs/B.md", "# B\n\n[thing](../src/mod.py#Thing)\n")
        self.write("src/other.py", "'''@doc: docs/A.md'''\n")
        output = self.run_checker()[1]
        self.assertIn("docs/B.md:3: 역방향 포인터 없음: src/mod.py#Thing", output)
        self.assertIn("src/other.py:1: 역방향 포인터 없음: docs/A.md가 src/other.py", output)


class SymbolRefTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_related_means_same_ancestor_or_descendant(self) -> None:
        def ref(name: str, file: str = "a.py") -> SymbolRef:
            return SymbolRef(Path(file), name)

        self.assertTrue(ref("A").is_related(ref("A.b")))
        self.assertTrue(ref("A.b").is_related(ref("")))
        self.assertFalse(ref("A").is_related(ref("AB")))
        self.assertFalse(ref("A").is_related(ref("A", "b.py")))


if __name__ == "__main__":
    unittest.main()
