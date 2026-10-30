"""Tests for markdown link extraction and heading anchors.

@doc: docs/VerificationTools.md#5-테스트
"""

import unittest
from pathlib import Path

from tools.doclib import extract_links, heading_anchors, slugify


class ExtractLinksTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_finds_prose_links_with_line_numbers(self) -> None:
        text = "# T\n\nsee [a](a.md) and [b](b.md#x)\n"
        links = extract_links(Path("doc.md"), text)
        self.assertEqual([(l.line, l.text, l.target) for l in links], [(3, "a", "a.md"), (3, "b", "b.md#x")])

    def test_ignores_code_blocks_inline_code_and_images(self) -> None:
        text = "```md\n[a](a.md)\n```\n`[b](b.md)` ![c](c.png)\n~~~\n[d](d.md)\n~~~\n"
        self.assertEqual(extract_links(Path("doc.md"), text), [])


class HeadingAnchorsTest(unittest.TestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def test_slugify_keeps_korean_and_drops_punctuation(self) -> None:
        self.assertEqual(slugify("3. 링크 규칙"), "3-링크-규칙")
        self.assertEqual(slugify("Use `uv` [here](x.md)!"), "use-uv-here")

    def test_duplicate_headings_get_suffixes(self) -> None:
        text = "# A\n## Same\n## Same\n```\n# Hidden\n```\n"
        self.assertEqual(heading_anchors(text), {"a", "same", "same-1"})


if __name__ == "__main__":
    unittest.main()
