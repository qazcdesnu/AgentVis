"""Tests for the web static file checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import hashlib
import io
from contextlib import redirect_stdout

from tests.support import RepoTestCase
from tools.check_web import external_references, main, vendor_problems

_LIB = "console.log('lib http://example.com');\n"
_HASH = hashlib.sha256(_LIB.encode()).hexdigest()


def _table(digest: str = _HASH, extra: str = "") -> str:
    row = (
        "| [lib-1.0.min.js](../../src/agentvis/web/vendor/lib-1.0.min.js) | Lib | 1.0 | "
        f"MIT ([LICENSE-lib.txt](../../src/agentvis/web/vendor/LICENSE-lib.txt)) | npm | `{digest}` |\n"
    )
    return "# 웹 UI\n\n| 파일 | 라이브러리 | 버전 | 라이선스 | 출처 | SHA-256 |\n| --- | --- | --- | --- | --- | --- |\n" + row + extra


class CheckWebTest(RepoTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("src/agentvis/web/index.html", '<script src="vendor/lib-1.0.min.js"></script>\n<script type="module" src="app.js"></script>\n')
        self.write("src/agentvis/web/app.js", 'd3.create("svg"); // http://www.w3.org/2000/svg ok\n')
        self.write("src/agentvis/web/style.css", "body { margin: 0; }\n")
        self.write("src/agentvis/web/vendor/lib-1.0.min.js", _LIB)
        self.write("src/agentvis/web/vendor/LICENSE-lib.txt", "MIT\n")
        self.write("docs/design/WebUI.md", _table())

    def test_clean_repository_passes(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root)]), 0)
        self.assertIn("화면 파일 3개, 라이브러리 파일 2개", output.getvalue())

    def test_absolute_external_address(self) -> None:
        self.write("src/agentvis/web/index.html", '<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>\n')
        problems = external_references(self.root)
        self.assertEqual([(p.line, p.message) for p in problems], [(1, "외부 주소: https://cdn.jsdelivr.net/npm/d3@7")])

    def test_protocol_relative_addresses(self) -> None:
        self.write("src/agentvis/web/style.css", "@font-face { src: url(//fonts.example/a.woff); }\n")
        self.write("src/agentvis/web/app.js", 'import x from "//esm.example/x.js";\n')
        messages = sorted(p.message for p in external_references(self.root))
        self.assertEqual(messages, ["외부 주소(프로토콜 상대): //esm.example/x.js", "외부 주소(프로토콜 상대): //fonts.example/a.woff"])

    def test_comment_slashes_are_not_addresses(self) -> None:
        self.write("src/agentvis/web/app.js", "// import later\nconst a = 1; // from here\n")
        self.assertEqual(external_references(self.root), [])

    def test_vendor_files_are_not_scanned_for_addresses(self) -> None:
        self.assertEqual(external_references(self.root), [])

    def test_unlisted_vendor_file(self) -> None:
        self.write("src/agentvis/web/vendor/extra.js", "x\n")
        messages = [p.message for p in vendor_problems(self.root)]
        self.assertEqual(messages, ["docs/design/WebUI.md의 라이브러리 표에 없는 파일"])

    def test_hash_mismatch(self) -> None:
        self.write("docs/design/WebUI.md", _table("0" * 64))
        self.assertEqual([p.message for p in vendor_problems(self.root)], ["SHA-256 불일치: ../../src/agentvis/web/vendor/lib-1.0.min.js"])

    def test_listed_file_missing(self) -> None:
        (self.root / "src/agentvis/web/vendor/lib-1.0.min.js").unlink()
        self.assertEqual([p.message for p in vendor_problems(self.root)], ["라이브러리 파일 없음: ../../src/agentvis/web/vendor/lib-1.0.min.js"])

    def test_table_inside_code_block_does_not_count(self) -> None:
        self.write("docs/design/WebUI.md", "# 웹 UI\n\n```markdown\n" + _table().split("\n\n", 1)[1] + "```\n")
        self.assertEqual(len(vendor_problems(self.root)), 2)
