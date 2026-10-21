"""Regressions for the bug report template's Markdown headings.

Run from the repository root: python3 -m pytest -q tests/test_issue_templates.py
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BugReportHeadingTests(unittest.TestCase):
    def setUp(self):
        template = (ROOT / ".github/ISSUE_TEMPLATE/bug_report.md").read_text(encoding="utf-8")
        # Exclude GitHub's YAML metadata from the Markdown body.
        self.body = template.split("\n---\n", 1)[1]

    def test_description_starts_at_level_two_and_reproduction_is_nested_one_level_below(self):
        headings = re.findall(r"^(#{1,6})[ \t]+(.+)$", self.body, re.MULTILINE)
        self.assertEqual(headings[:2], [("##", "Describe the bug"), ("###", "To Reproduce")])

    def test_changed_headings_have_a_blank_line_before_their_content(self):
        lines = self.body.splitlines()
        for heading in ("## Describe the bug", "### To Reproduce"):
            with self.subTest(heading=heading):
                self.assertEqual(lines.count(heading), 1)
                index = lines.index(heading)
                self.assertLess(index + 1, len(lines), "Heading must be followed by content")
                self.assertEqual(lines[index + 1], "", f"{heading} needs a blank line after it")


if __name__ == "__main__":
    unittest.main()
