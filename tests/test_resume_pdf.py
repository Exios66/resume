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
        cls.reader = pypdf.PdfReader(str(PDF))
        cls.raw_pages = [page.extract_text() for page in cls.reader.pages]
        cls.pages = [squash(text) for text in cls.raw_pages]

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

    def test_summary_precedes_education(self):
        first = self.pages[0]
        self.assertLess(first.index("PROFESSIONALSUMMARY"), first.index("EDUCATION"))

    def test_page_one_contains_complete_education_experience_and_skills(self):
        first = self.pages[0]
        for text in ("GPA 3.85", "GPA 3.93", "300 lab hours", "Building Services",
                     "Avis Budget Group", "Undergraduate Researcher", "Meijer Distribution",
                     "64 daily deliveries", "AWS, Azure, GCP"):
            with self.subTest(text=text):
                self.assertIn(squash(text), first)
                self.assertNotIn(squash(text), self.pages[1])

    def test_research_training_follows_the_last_project_on_page_two(self):
        second = self.pages[1]
        self.assertNotIn("RESEARCHTRAINING", self.pages[0])
        self.assertLess(second.index(squash(PROJECTS[-1])), second.index("RESEARCHTRAINING"))
        for text in ("Conflicts of Interest 2025", "IRB Training for Students and Faculty 2025"):
            self.assertIn(squash(text), second)

    def test_printed_headings_and_role_extract_as_words_for_ats(self):
        # Do not squash here: that would hide a regression to spaced-out letters.
        for page, phrases in ((0, ("PROFESSIONAL SUMMARY", "EDUCATION", "PROFESSIONAL EXPERIENCE",
                                    "TECHNICAL SKILLS", "AI / MACHINE LEARNING • DATA SCIENCE")),
                              (1, ("PROJECTS", "RESEARCH TRAINING"))):
            text = " ".join(self.raw_pages[page].split()).upper()
            for phrase in phrases:
                with self.subTest(page=page + 1, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_project_metrics_and_caveats_survive_pdf_export(self):
        second = self.pages[1]
        for text in ("95.05% document-type accuracy (307 of 323)",
                     "0.0152 window-level expected calibration error",
                     "held out from training and calibration (also used to compare runs)",
                     "synthetic insurance claims", "29 registered prompt versions",
                     "v11.8 prompt scored 82.6% on a 1,120-image class-balanced evaluation slice",
                     "241 analyzed survey respondents (252 matched)",
                     "personas did not beat the classical models", "99 passing tests"):
            with self.subTest(text=text):
                self.assertIn(squash(text), second)

    def test_project_repository_links_survive_pdf_export(self):
        expected = (
            "https://github.com/LLM-Mailroom-Services/Digital-Mailroom",
            "https://github.com/LLM-Mailroom-Services/mailroom-ml",
            "https://github.com/Exios66/Mailroom-Corpus-EDA",
            "https://github.com/Exios66/RVL-CDIP-Classifier",
            "https://github.com/Exios66/psych755-jjb",
            "https://github.com/Exios66/langtons-ant",
        )
        links = [annotation.get_object().get("/A", {}).get("/URI")
                 for annotation in self.reader.pages[1].get("/Annots", [])]
        for url in expected:
            with self.subTest(url=url):
                self.assertIn(url, links)


class ResumePdfAssets(unittest.TestCase):
    def test_source_and_downloaded_pdf_are_identical(self):
        self.assertEqual((ROOT / "assets" / PDF.name).read_bytes(), PDF.read_bytes())


if __name__ == "__main__":
    unittest.main()
