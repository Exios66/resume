"""Layout checks for the downloadable résumé PDF.

The layout follows the owner's v16 PDF: page 1 holds the summary, education
and experience; page 2 holds the projects, then the technical skills. Section headings are letter-spaced in print, so whitespace is
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
PROJECTS = ("Digital-Mailroom", "Mailroom-ML", "RVL-CDIP-Classifier",
            "Psychometric Digital Twin", "Alignment-Gym", "MapReduce-Reloaded")


def squash(text):
    return re.sub(r"\s+", "", text).upper().replace("’", "'").replace("ʼ", "'")


@unittest.skipIf(pypdf is None, "pypdf not installed")
class ResumePdfLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader = pypdf.PdfReader(str(PDF))
        cls.raw_pages = [page.extract_text() for page in cls.reader.pages]
        cls.pages = [squash(text) for text in cls.raw_pages]

    def test_two_pages(self):
        self.assertEqual(len(self.pages), 2)

    def test_page_one_is_summary_education_experience(self):
        first = self.pages[0]
        for heading in ("PROFESSIONALSUMMARY", "EDUCATION", "PROFESSIONALEXPERIENCE"):
            self.assertIn(heading, first)
        # "(see Projects)" in the M.S. entry is the only mention of projects on page 1.
        self.assertEqual(first.count("PROJECTS"), 1)
        self.assertIn("(SEEPROJECTS)", first)
        self.assertNotIn("TECHNICALSKILLS", first)
        self.assertLess(first.index("EDUCATION"), first.index("PROFESSIONALEXPERIENCE"))

    def test_page_two_starts_with_projects(self):
        second = self.pages[1]
        self.assertTrue(second.startswith("PROJECTS"), second[:40])
        for name in PROJECTS:
            self.assertIn(squash(name), second)

    def test_no_tuning_slice_or_stale_figures(self):
        text = "".join(self.pages)
        for stale in ("99.4%", "17+PROMPT", "AVISBUDGETGROUP", "7PYTHONPACKAGES"):
            self.assertNotIn(stale, text)

    def test_summary_precedes_education(self):
        first = self.pages[0]
        self.assertLess(first.index("PROFESSIONALSUMMARY"), first.index("EDUCATION"))

    def test_page_one_contains_complete_education_and_experience(self):
        first = self.pages[0]
        for text in ("GPA 3.85", "GPA 3.93", "300 lab hours", "neuroethics, and pre-law",
                     "Building Services", "Undergrad Researcher", "Meijer Distribution",
                     "64 daily deliveries", "resolve logistics exceptions before shipment"):
            with self.subTest(text=text):
                self.assertIn(squash(text), first)
                self.assertNotIn(squash(text), self.pages[1])

    def test_complete_skills_follow_the_last_project_on_page_two(self):
        second = self.pages[1]
        self.assertLess(second.index(squash(PROJECTS[-1])), second.index("TECHNICALSKILLS"))
        for text in ("LANGUAGES & DATA", "MACHINE LEARNING", "AI ENGINEERING", "ENGINEERING & CLOUD",
                     "Hugging Face, PyArrow", "ONNX + FastAPI deployment on Modal", "AWS, Azure, GCP"):
            with self.subTest(text=text):
                self.assertIn(squash(text), second[second.index("TECHNICALSKILLS"):])

    def test_printed_headings_and_role_extract_as_words_for_ats(self):
        # Do not squash here: that would hide a regression to spaced-out letters.
        for page, phrases in ((0, ("PROFESSIONAL SUMMARY", "EDUCATION", "PROFESSIONAL EXPERIENCE",
                                    "MACHINE LEARNING • DATA SCIENCE • AI ENGINEERING & SAFETY")),
                              (1, ("PROJECTS", "TECHNICAL SKILLS"))):
            text = " ".join(self.raw_pages[page].split()).upper()
            for phrase in phrases:
                with self.subTest(page=page + 1, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_project_figures_survive_pdf_export(self):
        second = self.pages[1]
        for text in ("5 Python packages", "16 RVL-CDIP categories", "29 prompt iterations",
                     "252 matched survey participants", "89 needle/decoy pairs",
                     "28 condition cells", "Dean & Ghemawat, OSDI 2004"):
            with self.subTest(text=text):
                self.assertIn(squash(text), second)

    def test_project_repository_links_survive_pdf_export(self):
        expected = (
            "https://github.com/LLM-Mailroom-Services/Digital-Mailroom",
            "https://github.com/LLM-Mailroom-Services/mailroom-ml",
            "https://github.com/Exios66/RVL-CDIP-Classifier",
            "https://github.com/Exios66/psych755-jjb",
            "https://github.com/Exios66/MapReduce-Reloaded",
        )
        links = [annotation.get_object().get("/A", {}).get("/URI")
                 for annotation in self.reader.pages[1].get("/Annots", [])]
        for url in expected:
            with self.subTest(url=url):
                self.assertIn(url, links)
        # Alignment-Gym is a private repository; the PDF must not link to it.
        self.assertFalse([url for url in links if url and "alignment-gym" in url.lower()])

    def test_header_links_the_portfolio_and_omits_the_phone_number(self):
        links = [annotation.get_object().get("/A", {}).get("/URI")
                 for annotation in self.reader.pages[0].get("/Annots", [])]
        self.assertIn("https://exios66.github.io/resume/", links)
        self.assertFalse([url for url in links if url and url.startswith("tel:")])
        self.assertNotRegex(self.raw_pages[0], r"(?<!\d)\d{3}[-.\s]\d{3}[-.\s]\d{4}(?!\d)")


class ResumePdfAssets(unittest.TestCase):
    def test_source_and_downloaded_pdf_are_identical(self):
        self.assertEqual((ROOT / "assets" / PDF.name).read_bytes(), PDF.read_bytes())


if __name__ == "__main__":
    unittest.main()
