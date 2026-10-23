"""Regressions for the résumé content and page split introduced by PR #46.

Run from the repository root: python3 -m pytest -q tests/test_resume_content.py
Reads committed source and HTML; no render, browser, or network is needed.
"""

import re
import unittest

import test_links as checks
from test_portfolio_additions import ContentParser


PROJECT_REPOS = (
    ("Digital-Mailroom", "https://github.com/LLM-Mailroom-Services/Digital-Mailroom"),
    ("Mailroom-ML", "https://github.com/LLM-Mailroom-Services/mailroom-ml"),
    ("Mailroom-Corpus-EDA", "https://github.com/Exios66/Mailroom-Corpus-EDA"),
    ("RVL-CDIP-Classifier", "https://github.com/Exios66/RVL-CDIP-Classifier"),
    ("Psychometric Digital Twin", "https://github.com/Exios66/psych755-jjb"),
    ("Langton's Ant", "https://github.com/Exios66/langtons-ant"),
)
SECTIONS = ("Professional Summary", "Education", "Professional Experience",
            "Technical Skills", "Projects", "Research Training")


def normalize(text):
    # Pandoc uses smart apostrophes and adds a word joiner before external icons.
    return " ".join(text.replace("’", "'").replace("\u2060", "").split())


class ResumeContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = ContentParser(checks.DOCS / "resume.html")
        cls.source = (checks.ROOT / "resume.qmd").read_text(encoding="utf-8")

    def one(self, elements, tag=None, class_name=None):
        matches = [attrs for element, attrs in elements
                   if (tag is None or element == tag)
                   and (class_name is None or class_name in checks.classes(attrs))]
        self.assertEqual(len(matches), 1, f"Expected one {tag or '*'} with class {class_name}")
        return matches[0]

    def section(self, title):
        elements = self.parser.elements
        headings = [(i, attrs) for i, (tag, attrs, _) in enumerate(elements)
                    if tag == "h2" and self.parser.text(attrs) == title]
        self.assertEqual(len(headings), 1, f"Expected one {title} section")
        start, _ = headings[0]
        end = next((i for i in range(start + 1, len(elements))
                    if elements[i][0] == "h2"), len(elements))
        return [(tag, attrs) for tag, attrs, _ in elements[start + 1:end]]

    def entries(self, title):
        return [attrs for tag, attrs in self.section(title)
                if tag == "div" and "entry" in checks.classes(attrs)]

    def project_text(self, name):
        matches = [entry for entry in self.entries("Projects")
                   if any(tag == "a" and normalize(self.parser.text(attrs)) == name
                          for tag, attrs in self.parser.children(entry))]
        self.assertEqual(len(matches), 1, f"Expected one entry for {name}")
        return normalize(self.parser.text(matches[0]))

    def test_source_and_published_sections_follow_the_two_page_order(self):
        source_headings = re.findall(r"^## (.+?)(?: \{[^}]*\})?$", self.source, re.M)
        self.assertEqual(source_headings, list(SECTIONS))
        headings = [self.parser.text(attrs) for tag, attrs, _ in self.parser.elements if tag == "h2"]
        self.assertEqual(headings, list(SECTIONS))

    def test_only_projects_requests_a_new_printed_page(self):
        markers = [(tag, attrs) for tag, attrs, _ in self.parser.elements
                   if "print-new-page" in checks.classes(attrs)]
        self.assertEqual(len(markers), 1)
        tag, attrs = markers[0]
        self.assertEqual((tag, self.parser.text(attrs)), ("h2", "Projects"))
        self.assertEqual(re.findall(r"^## .*print-new-page.*$", self.source, re.M),
                         ["## Projects {.print-new-page}"])

    def test_summary_keeps_the_partner_and_collaboration_context(self):
        paragraphs = [self.parser.text(attrs) for tag, attrs in self.section("Professional Summary")
                      if tag == "p"]
        self.assertEqual(len(paragraphs), 1)
        for claim in ("expected Dec 2026", "American Family Insurance",
                      "biweekly working sessions", "Enterprise Data Science lead"):
            with self.subTest(claim=claim):
                self.assertIn(claim, paragraphs[0])

    def test_moved_education_entries_retain_degrees_and_awards(self):
        entries = self.entries("Education")
        self.assertEqual(len(entries), 2)
        for entry, school, degree, gpa in (
            (entries[0], "University of Wisconsin–Madison", "M.S. Candidate", "GPA 3.85"),
            (entries[1], "University of Wisconsin–Parkside", "B.S., Psychology", "GPA 3.93"),
        ):
            with self.subTest(school=school):
                text = normalize(self.parser.text(entry))
                for claim in (school, degree, gpa):
                    self.assertIn(claim, text)
        for claim in ("Provost's List (7x)", "Dean's List (8x)", "300 lab hours"):
            self.assertIn(claim, normalize(self.parser.text(entries[1])))

    def test_experience_order_and_dates_match_v11(self):
        entries = self.entries("Professional Experience")
        expected = (
            ("UW–Madison Recreation & Wellbeing — Building Services", "Jun 2026 – Present"),
            ("Avis Budget Group — Driver", "Jun 2026 – Present"),
            ("UW–Parkside — Undergraduate Researcher, Cognitive Neuroscience Lab", "Jun 2024 – Aug 2025"),
            ("Meijer Distribution — Logistics Coordinator", "Jul 2020 – Aug 2025"),
        )
        self.assertEqual(len(entries), len(expected))
        for entry, (role, date) in zip(entries, expected):
            with self.subTest(role=role):
                head = self.one(self.parser.children(entry), class_name="entry-head")
                children = self.parser.children(head)
                self.assertEqual(self.parser.text(self.one(children, tag="strong")), role)
                self.assertEqual(self.parser.text(self.one(children, class_name="date")), date)
        self.assertIn("Dr. Melissa Gregg", self.parser.text(entries[2]))
        meijer = self.parser.text(entries[-1])
        self.assertIn("64 daily deliveries", meijer)
        self.assertIn("below 1%", meijer)
        self.assertNotIn("trailers", meijer)

    def test_research_presentations_name_both_venues_on_both_pages(self):
        research = ContentParser(checks.DOCS / "research.html")
        resume_items = [self.parser.text(attrs) for tag, attrs in self.section("Professional Experience")
                        if tag == "li"]
        research_items = [research.text(attrs) for tag, attrs, _ in research.elements if tag == "li"]
        for page, items in (("resume.html", resume_items), ("research.html", research_items)):
            with self.subTest(page=page):
                presentations = [text for text in items if "Presented" in text]
                self.assertEqual(len(presentations), 1)
                for claim in ("2025 Midwestern Psychological Association",
                              "Chicago", "Research in the Rotunda"):
                    self.assertIn(claim, presentations[0])

    def test_expanded_skills_stay_in_their_categories(self):
        elements = self.section("Technical Skills")
        labels = [self.parser.text(attrs) for tag, attrs in elements if tag == "dt"]
        values = [self.parser.text(attrs) for tag, attrs in elements if tag == "dd"]
        expected = {
            "Languages & Data": ("PyArrow", "Hive", "JavaScript/TypeScript"),
            "Machine Learning": ("ensembles", "resampling", "Lasso/Ridge"),
            "AI Engineering": ("LangChain", "vLLM", "Ollama", "OpenRouter"),
            "Tools & Cloud": ("gRPC", "Spark/PySpark", "HDFS", "CHTC", "GCP"),
        }
        self.assertEqual(labels, list(expected))
        self.assertEqual(len(values), len(labels))
        for label, value in zip(labels, values):
            for skill in expected[label]:
                with self.subTest(category=label, skill=skill):
                    self.assertIn(skill, value)

    def test_all_six_project_names_link_to_their_repositories(self):
        entries = self.entries("Projects")
        self.assertEqual(len(entries), len(PROJECT_REPOS))
        actual = []
        for entry in entries:
            head = self.one(self.parser.children(entry), class_name="entry-head")
            link = self.one(self.parser.children(head), tag="a")
            actual.append((normalize(self.parser.text(link)), checks.attr(link, "href")))
        self.assertEqual(actual, list(PROJECT_REPOS))
        for name, url in PROJECT_REPOS:
            with self.subTest(project=name):
                self.assertIn(f"**[{name}]({url})**", self.source)

    def test_project_metrics_retain_their_denominators_and_qualifications(self):
        claims = {
            "Digital-Mailroom": ("7 Python packages", "Enterprise Data Science division",
                                 "one LangGraph pipeline", "cheapest step"),
            "Mailroom-ML": ("95.05% document-type accuracy (307 of 323)",
                            "0.0152 window-level expected calibration error",
                            "held out from training and calibration (also used to compare runs)",
                            "42.8% of fallback filenames", "build-time guard", "485 pytest tests"),
            "Mailroom-Corpus-EDA": ("3,302-document, 5-class", "synthetic insurance claims",
                                   "7-phase audit", "48 figures, 17 tables", "about 200 tests",
                                   "13,753 contract clause annotations"),
            "RVL-CDIP-Classifier": ("16 RVL-CDIP categories", "$0.0004 per image",
                                    "300-DPI", "Tesseract OCR", "29 registered prompt versions",
                                    "v11.8 prompt scored 82.6% on a 1,120-image class-balanced evaluation slice"),
            "Psychometric Digital Twin": ("241 analyzed survey respondents (252 matched)",
                                          "factor analysis", "Ollama, OpenRouter, vLLM",
                                          "personas did not beat the classical models"),
            "Langton's Ant": ("up to 32 colors and 16 states", "unbounded, chunked grid",
                              "20 published machines", "shareable permalinks",
                              "integer-only stepping, seeded randomness", "99 passing tests",
                              "pinned determinism test"),
        }
        for name, expected in claims.items():
            text = self.project_text(name)
            for claim in expected:
                with self.subTest(project=name, claim=claim):
                    self.assertIn(claim, text)

    def test_stale_metrics_and_dates_do_not_return_to_the_public_resume(self):
        page = self.one([(tag, attrs) for tag, attrs, _ in self.parser.elements], class_name="page")
        text = normalize(self.parser.text(page))
        for stale in (r"\b(?:10|ten) Python packages\b", r"\b17\+ prompt", r"\b99\.4%",
                      r"\bJan 2026 – Present\b", r"\bJul 2020 – Dec 2025\b"):
            with self.subTest(stale=stale):
                self.assertNotRegex(text, stale)
        self.assertFalse([attrs for tag, attrs, _ in self.parser.elements
                          if tag == "a" and checks.attr(attrs, "href").startswith("tel:")])
        self.assertNotRegex(text, r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)")


if __name__ == "__main__":
    unittest.main()
