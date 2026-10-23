"""Regressions for the résumé content and page split, which follow the owner's v16 PDF.

Run from the repository root: python3 -m pytest -q tests/test_resume_content.py
Reads committed source and HTML; no render, browser, or network is needed.
"""

import re
import unittest

import test_links as checks
from test_portfolio_additions import ContentParser


# Alignment-Gym's repository is private, so its name is not a link.
PROJECT_REPOS = (
    ("Digital-Mailroom", "https://github.com/LLM-Mailroom-Services/Digital-Mailroom"),
    ("Mailroom-ML", "https://github.com/LLM-Mailroom-Services/mailroom-ml"),
    ("RVL-CDIP-Classifier", "https://github.com/Exios66/RVL-CDIP-Classifier"),
    ("Psychometric Digital Twin", "https://github.com/Exios66/psych755-jjb"),
    ("Alignment-Gym", None),
    ("MapReduce-Reloaded", "https://github.com/Exios66/MapReduce-Reloaded"),
)
SECTIONS = ("Professional Summary", "Education", "Professional Experience",
            "Projects", "Technical Skills")


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

    def project_name(self, entry):
        head = self.one(self.parser.children(entry), class_name="entry-head")
        return normalize(self.parser.text(self.one(self.parser.children(head), tag="strong")))

    def project_text(self, name):
        matches = [entry for entry in self.entries("Projects") if self.project_name(entry) == name]
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

    def test_education_entries_retain_degrees_awards_and_v16_coursework(self):
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
        for claim in ("Aug 2025 – Dec 2026 (expected)", "about 95% of coursework is data science",
                      "Spark, gRPC services, HDFS, Parquet, SQL, Docker", "Industry capstone"):
            self.assertIn(claim, normalize(self.parser.text(entries[0])))
        for claim in ("Provost's List (7x)", "Dean's List (8x)", "300 lab hours",
                      "psychopharmacology, psychometrics", "neuroethics, and pre-law"):
            self.assertIn(claim, normalize(self.parser.text(entries[1])))

    def test_experience_order_and_dates_match_v16(self):
        entries = self.entries("Professional Experience")
        expected = (
            ("UW–Madison Recreation & Wellbeing — Building Services", "Jun 2026 – Present"),
            ("UW–Parkside — Undergrad Researcher, Cognitive Neuroscience Lab", "Jun 2024 – Aug 2025"),
            ("Meijer Distribution — Logistics Coordinator", "Jul 2020 – Aug 2025"),
        )
        self.assertEqual(len(entries), len(expected))
        for entry, (role, date) in zip(entries, expected):
            with self.subTest(role=role):
                head = self.one(self.parser.children(entry), class_name="entry-head")
                children = self.parser.children(head)
                self.assertEqual(self.parser.text(self.one(children, tag="strong")), role)
                self.assertEqual(self.parser.text(self.one(children, class_name="date")), date)
        self.assertIn("Dr. Melissa Gregg", self.parser.text(entries[1]))
        meijer = self.parser.text(entries[-1])
        self.assertIn("64 daily deliveries", meijer)
        self.assertIn("below 1% through root-cause investigation", meijer)
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

    def test_skills_follow_projects_in_their_v16_categories(self):
        elements = self.section("Technical Skills")
        labels = [self.parser.text(attrs) for tag, attrs in elements if tag == "dt"]
        values = [self.parser.text(attrs) for tag, attrs in elements if tag == "dd"]
        expected = {
            "Languages & Data": ("PyArrow", "Hive", "JavaScript/TypeScript"),
            "Machine Learning": ("ensemble methods", "resampling", "Lasso/Ridge", "neural networks"),
            "AI Engineering": ("LangChain", "bias and robustness evals", "vLLM", "Ollama", "OpenRouter"),
            "Engineering & Cloud": ("Git", "gRPC", "Spark/PySpark", "HDFS", "CHTC", "GCP"),
        }
        self.assertEqual(labels, list(expected))
        self.assertEqual(len(values), len(labels))
        for label, value in zip(labels, values):
            for skill in expected[label]:
                with self.subTest(category=label, skill=skill):
                    self.assertIn(skill, value)

    def test_six_projects_in_v16_order_link_to_public_repositories_only(self):
        entries = self.entries("Projects")
        self.assertEqual(len(entries), len(PROJECT_REPOS))
        actual = []
        for entry in entries:
            head = self.one(self.parser.children(entry), class_name="entry-head")
            links = [attrs for tag, attrs in self.parser.children(head) if tag == "a"]
            self.assertLessEqual(len(links), 1)
            actual.append((self.project_name(entry), checks.attr(links[0], "href") if links else None))
        self.assertEqual(actual, list(PROJECT_REPOS))
        for name, url in PROJECT_REPOS:
            with self.subTest(project=name):
                self.assertIn(f"**[{name}]({url})**" if url else f"**{name}**", self.source)
        self.assertNotIn("alignment-gym", self.source.lower().replace("**alignment-gym**", ""))

    def test_project_claims_match_v16_and_the_source_repositories(self):
        claims = {
            "Digital-Mailroom": ("5 Python packages", "Enterprise Data Science division",
                                 "unified LangGraph pipeline", "reproducible Docker environment"),
            "Mailroom-ML": ("ModernBERT document classifier", "data lineage tracking",
                            "probability calibration", "ONNX export for FastAPI serving on Modal"),
            "RVL-CDIP-Classifier": ("16 RVL-CDIP categories", "300-DPI", "OpenRouter vision models",
                                    "29 prompt iterations", "cost projections"),
            "Psychometric Digital Twin": ("252 matched survey participants", "factor analysis",
                                          "Ollama, OpenRouter, vLLM", "bias by demographic group"),
            "Alignment-Gym": ("fictional law firm", "89 needle/decoy pairs", "9 plot beats",
                              "0–3 temptation ladder", "28 condition cells", "seed-invariant truth spine",
                              "paired LLM judges", "calibration gates"),
            "MapReduce-Reloaded": ("Dean & Ghemawat, OSDI 2004", "gRPC coordinator/worker protocol",
                                   "Docker Compose", "same protobuf contract and file format"),
        }
        for name, expected in claims.items():
            text = self.project_text(name)
            for claim in expected:
                with self.subTest(project=name, claim=claim):
                    self.assertIn(claim, text)

    def test_stale_metrics_and_dates_do_not_return_to_the_public_resume(self):
        page = self.one([(tag, attrs) for tag, attrs, _ in self.parser.elements], class_name="page")
        text = normalize(self.parser.text(page))
        for stale in (r"\b(?:10|ten|7|seven) Python packages\b", r"\b17\+ prompt", r"\b99\.4%",
                      r"\bJan 2026 – Present\b", r"\bJul 2020 – Dec 2025\b", r"Avis Budget Group"):
            with self.subTest(stale=stale):
                self.assertNotRegex(text, stale)
        self.assertFalse([attrs for tag, attrs, _ in self.parser.elements
                          if tag == "a" and checks.attr(attrs, "href").startswith("tel:")])
        self.assertNotRegex(text, r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)")


if __name__ == "__main__":
    unittest.main()
