"""Tests for the document link checker.

@doc: docs/VerificationTools.md#5-테스트
"""

import unittest

from tests.support import RepoTestCase
from tools.check_docs import check_entry, check_links, check_readme, find_orphans


class CheckDocsTest(RepoTestCase):
    """@doc: docs/VerificationTools.md#5-테스트"""

    def setUp(self) -> None:
        super().setUp()
        self.write("CLAUDE.md", "# C\n\n[index](docs/index.md)\n")
        self.write("docs/index.md", "# Index\n\n[rule](Rule.md#1-intro)\n")
        self.write("docs/Rule.md", "# Rule\n\n## 1. Intro\n\n[back](index.md)\n")
        self.write("README.md", "# R\n\n[index](docs/index.md) [rules](CLAUDE.md)\n")

    def test_clean_repository_passes(self) -> None:
        problems = check_links(self.root) + check_entry(self.root) + check_readme(self.root) + find_orphans(self.root)
        self.assertEqual(problems, [])

    def test_reports_missing_file_and_anchor(self) -> None:
        self.write("docs/Rule.md", "# Rule\n\n## 1. Intro\n\n[gone](Gone.md) [bad](index.md#nope)\n")
        messages = [problem.message for problem in check_links(self.root)]
        self.assertEqual(messages, ["링크 대상 없음: Gone.md", "앵커 없음: index.md#nope"])

    def test_skips_external_and_code_links(self) -> None:
        self.write("docs/Rule.md", "# Rule\n\n## 1. Intro\n\n[w](https://x.y) [c](../missing.py#f)\n")
        self.assertEqual(check_links(self.root), [])

    def test_reports_orphan(self) -> None:
        orphan = self.write("docs/Orphan.md", "# Orphan\n\n[index](index.md)\n")
        self.assertEqual([problem.path for problem in find_orphans(self.root)], [orphan])

    def test_reports_entry_without_index_link(self) -> None:
        self.write("CLAUDE.md", "# C\n")
        self.assertEqual(len(check_entry(self.root)), 1)

    def test_readme_links_are_checked_and_required_links_reported(self) -> None:
        self.write("README.md", "# R\n\n[index](docs/index.md) [gone](docs/Gone.md)\n")
        self.assertEqual([problem.message for problem in check_links(self.root)], ["링크 대상 없음: docs/Gone.md"])
        self.assertEqual([problem.message for problem in check_readme(self.root)], ["README에 CLAUDE.md 링크 없음"])

    def test_reports_missing_readme(self) -> None:
        (self.root / "README.md").unlink()
        self.assertEqual([problem.message for problem in check_readme(self.root)], ["README 없음"])


if __name__ == "__main__":
    unittest.main()
