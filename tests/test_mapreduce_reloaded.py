"""Regressions for the MapReduce-Reloaded case study.

Run from the repository root: python3 -m pytest -q tests/test_mapreduce_reloaded.py
These checks read committed pages and assets; no render or network is needed beyond a built docs/.
"""

import re
import unittest
import xml.etree.ElementTree as ET

import test_links as checks
from test_portfolio_additions import ContentParser, destination


SITE_URL = "https://exios66.github.io/resume/"
PAGE = "projects/mapreduce-reloaded.html"
CODE_URL = "https://github.com/Exios66/MapReduce-Reloaded"
GROUP_ID = "big-data-distributed-systems"


class MapReduceReloadedTests(unittest.TestCase):
    def read_page(self, name=PAGE):
        path = checks.DOCS / name
        self.assertTrue(path.is_file(), f"Missing published page: {name}")
        return path, ContentParser(path)

    def one(self, parser, tag, **attributes):
        matches = [attrs for element, attrs, _ in parser.elements
                   if element == tag and all(checks.attr(attrs, key) == value
                                             for key, value in attributes.items())]
        self.assertEqual(len(matches), 1, f"Expected one {tag} with {attributes}")
        return matches[0]

    def group_cards(self, parser):
        heading = self.one(parser, "h2", id=GROUP_ID)
        start = next(i for i, (_, attrs, _) in enumerate(parser.elements) if attrs is heading)
        end = next((i for i in range(start + 1, len(parser.elements))
                    if parser.elements[i][0] == "h2"), len(parser.elements))
        return heading, [attrs for _, attrs, _ in parser.elements[start:end] if "card" in checks.classes(attrs)]

    def test_card_sits_in_its_own_group_and_links_to_the_case_study(self):
        page, parser = self.read_page("projects/index.html")
        heading, cards = self.group_cards(parser)
        self.assertEqual(parser.text(heading), "Big data & distributed systems")
        self.assertEqual([checks.attr(card, "id") for card in cards], ["mapreduce-reloaded"])
        headings = [attrs for tag, attrs in parser.children(cards[0]) if tag == "h3"]
        self.assertEqual(len(headings), 1)
        links = [attrs for tag, attrs in parser.children(headings[0]) if tag == "a"]
        self.assertEqual(len(links), 1)
        self.assertEqual(destination(page, links[0]), (checks.DOCS / PAGE).resolve())
        text = parser.text(cards[0])
        self.assertIn("In active development", text)
        self.assertIn("Packet drops are not built yet.", text)
        self.assertNotIn("Object storage, compression and benchmarks are planned.", text)

    def test_group_reuses_an_existing_icon_and_the_sprite_is_unchanged(self):
        _, index = self.read_page("projects/index.html")
        heading, _ = self.group_cards(index)
        uses = [attrs for tag, attrs in index.children(heading) if tag == "use"]
        self.assertEqual([checks.attr(attrs, "href") for attrs in uses], ["#i-layers"])
        symbols = [checks.attr(attrs, "id") for tag, attrs, _ in index.elements if tag == "symbol"]
        self.assertEqual(len(symbols), 20, "The sprite must keep exactly the existing 20 symbols")
        for tag, attrs, _ in self.read_page()[1].elements:
            if tag == "svg" and "icon" in checks.classes(attrs):
                self.assertEqual(checks.attr(attrs, "width"), "1em")
                self.assertEqual(checks.attr(attrs, "height"), "1em")

    def test_navigation_back_link_and_actions_have_exact_destinations(self):
        page, parser = self.read_page()
        nav = self.one(parser, "div", **{"class": "project-nav"})
        links = [attrs for tag, attrs in parser.children(nav) if tag == "a"]
        self.assertEqual({parser.text(link): destination(page, link) for link in links},
                         {"Case study": page.resolve(),
                          "Technical report": "https://github.com/Exios66/MapReduce-Reloaded/blob/main/docs/report.md",
                          "Appendix": (checks.DOCS / "projects/mapreduce-reloaded/appendix.html").resolve(),
                          "Code": CODE_URL})
        current = [link for link in links if checks.attr(link, "aria-current") == "page"]
        self.assertEqual(len(current), 1)
        back = self.one(parser, "a", **{"class": "back"})
        self.assertEqual(destination(page, back), (checks.DOCS / "projects/index.html").resolve())
        actions = self.one(parser, "div", **{"class": "actions"})
        self.assertEqual([checks.attr(attrs, "href") for tag, attrs in parser.children(actions) if tag == "a"],
                         [CODE_URL], "There is no live demo; link only the code")
        self.assertFalse((checks.DOCS / "projects/mapreduce-reloaded/report.html").exists())

    def test_page_keeps_its_work_in_progress_caveat_and_plan(self):
        _, parser = self.read_page()
        kicker = self.one(parser, "span", **{"class": "kicker"})
        self.assertIn("In active development", parser.text(kicker))
        caveat = self.one(parser, "div", **{"class": "caveat"})
        self.assertIn("Work in progress", parser.text(caveat))
        self.assertIn("not built yet", parser.text(caveat))
        self.one(parser, "h2", id="what-is-planned")
        self.assertFalse(any(tag == "img" for tag, _, _ in parser.elements), "No unverified screenshot")

    def test_stats_match_what_was_run(self):
        _, parser = self.read_page()
        values = [parser.text(attrs) for _, attrs, _ in parser.elements
                  if "stat-value" in checks.classes(attrs)]
        self.assertEqual(values, ["24", "336 + 487", "5"])

    def test_diagram_publishes_the_partial_without_geometry_loss(self):
        _, published = self.read_page()
        source = ContentParser(checks.ROOT / "partials/diagrams/_mapreduce-reloaded.qmd")
        diagram = self.one(published, "figure", **{"class": "diagram"})
        original = self.one(source, "figure", **{"class": "diagram"})
        self.assertEqual(diagram, original)
        self.assertEqual(published.children(diagram), source.children(original))
        caption = self.one(published, "figcaption", id=checks.attr(diagram, "aria-labelledby"))
        self.assertTrue(published.text(caption))
        self.assertEqual(checks.attr(diagram, "role"), "img")

    def test_description_canonical_and_sitemap_match_the_source(self):
        _, parser = self.read_page()
        source = (checks.ROOT / "projects/mapreduce-reloaded.qmd").read_text(encoding="utf-8")
        description = re.search(r'^description: "([^"]+)"$', source, re.MULTILINE)
        self.assertIsNotNone(description)
        meta = self.one(parser, "meta", name="description")
        self.assertEqual(checks.attr(meta, "content"), description.group(1).replace("'", "’"))
        canonical = self.one(parser, "link", rel="canonical")
        self.assertEqual(checks.attr(canonical, "href"), SITE_URL + PAGE)
        locations = [node.text for node in ET.parse(checks.DOCS / "sitemap.xml").findall("{*}url/{*}loc")]
        self.assertEqual(locations.count(SITE_URL + PAGE), 1)

    def test_aeroglobe_card_describes_the_live_build_without_overclaiming(self):
        _, parser = self.read_page("projects/index.html")
        card = self.one(parser, "section", id="aeroglobe")
        text = parser.text(card)
        self.assertIn("An early version is live", text)
        self.assertIn("recorded when the site was built", text)
        self.assertIn("full-day playback is planned", text)
        self.assertNotIn("current traffic", text)

    def test_readme_links_the_published_case_study_once(self):
        readme = (checks.ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(readme.count(f"[MapReduce-Reloaded]({SITE_URL}{PAGE})"), 1)


if __name__ == "__main__":
    unittest.main()
