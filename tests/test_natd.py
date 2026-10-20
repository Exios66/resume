"""Checks for the NATD (The Neural Architecture of Truth and Deception) case study and report.

Run from the repository root after a render: python3 -m pytest -q tests/test_natd.py
"""

import re
import unittest
import xml.etree.ElementTree as ET

import test_links as checks
from test_portfolio_additions import SITE_URL, ContentParser, destination

STUDY = "projects/natd.html"
REPORT = "projects/natd/report.html"
CODE_URL = "https://github.com/Exios66/truth-deception-architecture"


class NatdTests(unittest.TestCase):
    def read_page(self, name):
        path = checks.DOCS / name
        self.assertTrue(path.is_file(), f"Missing published page: {name}")
        return path, ContentParser(path)

    def page_text(self, name):
        _, parser = self.read_page(name)
        return " ".join("".join(data for data, _ in parser.text_fragments).split())

    def test_provenance_caveat_is_visible_on_the_case_study_and_the_report(self):
        for name in (STUDY, REPORT):
            with self.subTest(page=name):
                _, parser = self.read_page(name)
                caveats = [attrs for _, attrs, _ in parser.elements if "caveat" in checks.classes(attrs)]
                self.assertTrue(caveats, f"{name} lost its caveat")
                first = parser.text(caveats[0])
                self.assertIn("provenance", first.lower())
                self.assertRegex(first, r"(?i)not confirmed|unconfirmed")
                self.assertIn("exploratory", first.lower())
                # The caveat comes before the first findings heading, so it leads the page.
                names = [(tag, attrs) for tag, attrs, _ in parser.elements]
                first_caveat = next(i for i, (_, attrs) in enumerate(names) if attrs is caveats[0])
                first_h2 = next(i for i, (tag, _) in enumerate(names) if tag == "h2")
                self.assertLess(first_caveat, first_h2 + 1)

    def test_byline_is_the_site_owner_and_the_draft_byline_is_not_published(self):
        for name in (STUDY, REPORT):
            with self.subTest(page=name):
                text = self.page_text(name)
                self.assertIn("Jack J. Burleson", text)
                self.assertNotIn("Jefferson", text)
        self.assertIn("Dr. Melissa Gregg", self.page_text(REPORT))

    def test_pages_have_no_unavailable_chart_embeds_or_fabricated_figures(self):
        for name in (STUDY, REPORT):
            with self.subTest(page=name):
                _, parser = self.read_page(name)
                self.assertNotIn("[embed", self.page_text(name))
                self.assertFalse([1 for tag, _, _ in parser.elements if tag == "img"],
                                 "The source write-up has no available charts; do not add images")

    def test_headline_numbers_match_the_source_write_up(self):
        study = self.page_text(STUDY)
        report = self.page_text(REPORT)
        for text in ("+12.3", "−1.0", "1 of 18", "6.3 to 20.3", "0.1% to 27.3%"):
            self.assertIn(text, study)
        for text in ("13.3-point gap", "95% confidence interval of 6.3 to 20.3", "t(14.5) = 4.04",
                     "Mann-Whitney p = 0.004", "+11.6 points (95% CI 2.9 to 20.3, p = 0.013)",
                     "paired t(4) = 4.8, p = 0.009", "exact 95% CI 0.1% to 27.3%",
                     "9.1%; 95% CI 0.2% to 41.3%", "r = 0.97", "NASA-TLX 4.77"):
            self.assertIn(text, report)

    def test_hedges_from_the_source_are_kept(self):
        report = self.page_text(REPORT)
        for text in ("nine-person exploratory study", "Treat every p-value as descriptive",
                     "regression to the mean", "partly confounded with person",
                     "mixed-effects models were not refit"):
            self.assertIn(text, report)

    def test_cluster_table_reconciles_with_18_sessions(self):
        _, parser = self.read_page(REPORT)
        tables = [attrs for tag, attrs, _ in parser.elements if tag == "table"]
        clusters = next(t for t in tables if "Persona mix" in parser.text(t))
        cells = [parser.text(attrs) for tag, attrs in parser.children(clusters) if tag == "td"]
        sessions = [int(cells[i]) for i in range(1, len(cells), 4)]
        self.assertEqual(sessions, [9, 4, 5])
        self.assertEqual(sum(sessions), 18)

    def test_references_list_30_works_each_with_a_link_and_verification_tag(self):
        _, parser = self.read_page(REPORT)
        h2s = [(i, attrs) for i, (tag, attrs, _) in enumerate(parser.elements) if tag == "h2"]
        heading = next(i for i, attrs in h2s if checks.attr(attrs, "id") == "references")
        items = []
        for tag, attrs, ancestors in parser.elements[heading:]:
            if tag == "li":
                items.append(attrs)
        self.assertEqual(len(items), 30)
        for item in items:
            with self.subTest(reference=parser.text(item)[:40]):
                self.assertRegex(parser.text(item), r"\[(Verified|Partly verified)[^\]]*\]")
                links = [a for t, a in parser.children(item) if t == "a"]
                self.assertEqual(len(links), 1)
                self.assertTrue(checks.attr(links[0], "href").startswith("https://"))

    def test_nav_back_link_and_code_action(self):
        study, parser = self.read_page(STUDY)
        nav = [attrs for _, attrs, _ in parser.elements if "project-nav" in checks.classes(attrs)]
        self.assertEqual(len(nav), 1)
        links = {parser.text(a): destination(study, a)
                 for t, a in parser.children(nav[0]) if t == "a"}
        self.assertEqual(links, {"Case study": study.resolve(),
                                 "Technical report": (checks.DOCS / REPORT).resolve(),
                                 "Code": CODE_URL})
        actions = [attrs for _, attrs, _ in parser.elements if "actions" in checks.classes(attrs)]
        hrefs = {checks.attr(a, "href") for t, a in parser.children(actions[0]) if t == "a"}
        self.assertIn(CODE_URL, hrefs)

    def test_research_page_links_to_the_case_study_and_keeps_its_other_content(self):
        page, parser = self.read_page("research.html")
        targets = {destination(page, attrs) for tag, attrs, _ in parser.elements if tag == "a"}
        self.assertIn((checks.DOCS / STUDY).resolve(), targets)
        text = self.page_text("research.html")
        for expected in ("Dr. Melissa Gregg", "2025 Midwestern Psychological Association conference",
                         "Psychometric Digital Twin"):
            self.assertIn(expected, text)

    def test_projects_index_card_sits_under_a_group_with_a_sized_brain_icon(self):
        page, parser = self.read_page("projects/index.html")
        heading = next(attrs for tag, attrs, _ in parser.elements
                       if tag == "h2" and parser.text(attrs) == "Cognitive neuroscience")
        self.assertIn("group-title", checks.classes(heading))
        icons = [attrs for tag, attrs in parser.children(heading) if tag == "svg"]
        self.assertEqual(len(icons), 1)
        self.assertEqual((checks.attr(icons[0], "width"), checks.attr(icons[0], "height")), ("1em", "1em"))
        uses = [attrs for tag, attrs in parser.children(heading) if tag == "use"]
        self.assertEqual([checks.attr(u, "href") for u in uses], ["#i-brain"])
        cards = [attrs for tag, attrs, ancestors in parser.elements
                 if tag == "a" and any("card" in checks.classes(p) for _, p in ancestors)
                 and destination(page, attrs) == (checks.DOCS / STUDY).resolve()]
        self.assertEqual(len(cards), 1)

    def test_sitemap_and_readme_list_the_project(self):
        locations = [n.text for n in ET.parse(checks.DOCS / "sitemap.xml").findall("{*}url/{*}loc")]
        for name in (STUDY, REPORT):
            self.assertEqual(locations.count(SITE_URL + name), 1, name)
        readme = (checks.ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(readme.count(f"]({SITE_URL}projects/natd.html)"), 1)

    def test_design_diagram_states_only_facts_from_the_write_up(self):
        _, parser = self.read_page(STUDY)
        text = self.page_text(STUDY)
        for fact in ("9 participants", "Helpful personas", "Athena, Milgrim", "7 sessions",
                     "Deceitful personas", "Alan, Enigma, Scarlet", "11 sessions"):
            self.assertIn(fact, text)
        self.assertEqual(sum(1 for _, attrs, _ in parser.elements
                             if "diagram" in checks.classes(attrs)), 1)


if __name__ == "__main__":
    unittest.main()
