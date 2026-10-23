"""Layout checks for the downloadable résumé PDF.

Page 1 holds the summary, education, experience and skills; page 2 holds the
projects. Section headings are letter-spaced in print, so whitespace is
stripped before matching.
"""

import re
import unittest
from pathlib import Path

try:
    import pypdf
except ImportError:  # pragma: no cover - optional dependency
    pypdf = None

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "docs" / "assets" / "Jack_Burleson_Resume.pdf"
PROJECTS = ("Digital-Mailroom", "Mailroom-ML", "Mailroom-Corpus-EDA", "RVL-CDIP-Classifier",
            "Psychometric Digital Twin", "Langton's Ant")


def squash(text):
    return re.sub(r"\s+", "", text).upper().replace("’", "'").replace("ʼ", "'")


@unittest.skipIf(pypdf is None, "pypdf not installed")
class ResumePdfLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = [squash(page.extract_text()) for page in pypdf.PdfReader(str(PDF)).pages]

    def test_two_pages(self):
        self.assertEqual(len(self.pages), 2)

    def test_page_one_is_education_experience_skills(self):
        first = self.pages[0]
        for heading in ("PROFESSIONALSUMMARY", "EDUCATION", "PROFESSIONALEXPERIENCE", "TECHNICALSKILLS"):
            self.assertIn(heading, first)
        self.assertNotIn("PROJECTS", first)
        self.assertLess(first.index("EDUCATION"), first.index("PROFESSIONALEXPERIENCE"))
        self.assertLess(first.index("PROFESSIONALEXPERIENCE"), first.index("TECHNICALSKILLS"))

    def test_page_two_starts_with_projects(self):
        second = self.pages[1]
        self.assertTrue(second.startswith("PROJECTS"), second[:40])
        for name in PROJECTS:
            self.assertIn(squash(name), second)

    def test_no_tuning_slice_or_stale_figures(self):
        text = "".join(self.pages)
        for stale in ("99.4%", "17+PROMPT"):
            self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main()
