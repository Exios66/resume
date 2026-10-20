"""The Digital-Mailroom capstone is seven Python packages. Keep every page that counts them in agreement.

Run from the repository root after a render: python3 -m pytest -q tests/test_digital_mailroom_claims.py
"""

import re
import unittest

import test_links as checks


def visible_text(path):
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


class DigitalMailroomPackageCountTests(unittest.TestCase):
    def test_no_page_claims_ten_python_packages(self):
        stale = re.compile(r"\b(?:ten|10)\s+(?:python\s+)?packages\b", re.I)
        for page in checks.DOCS.rglob("*.html"):
            if "site_libs" in page.parts:
                continue
            with self.subTest(page=str(page.relative_to(checks.DOCS))):
                self.assertIsNone(stale.search(visible_text(page)))

    def test_case_study_resume_and_diagram_say_seven(self):
        study = visible_text(checks.DOCS / "projects/digital-mailroom.html")
        for text in ("Python packages: entity extraction", "split the work into seven packages",
                     "Seven Python packages covering", "the seven Python packages cover"):
            self.assertIn(text, study)
        self.assertRegex(study, r"\b7 Python packages: entity extraction|\b7\s+Python packages\b")
        self.assertIn("7 Python packages covering entity extraction", visible_text(checks.DOCS / "resume.html"))

    def test_readme_and_both_project_cards_say_seven_packages(self):
        readme = (checks.ROOT / "README.md").read_text(encoding="utf-8")
        line = next(l for l in readme.splitlines() if l.startswith("- [Digital-Mailroom]"))
        self.assertIn("seven Python packages", line)
        for name in ("index.html", "projects/index.html"):
            with self.subTest(page=name):
                self.assertIn("Seven Python packages and one LangGraph pipeline"
                              if name == "index.html" else "seven Python packages and one LangGraph pipeline",
                              visible_text(checks.DOCS / name))


if __name__ == "__main__":
    unittest.main()
