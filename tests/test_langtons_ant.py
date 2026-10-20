"""Regressions for the Langton's Ant case study.

Run from the repository root: python3 -m pytest -q tests/test_langtons_ant.py
These checks read committed pages and assets; no render or network is needed beyond a built docs/.
"""

import re
import unittest
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

import test_links as checks
from test_portfolio_additions import ContentParser, destination


SITE_URL = "https://exios66.github.io/resume/"
PAGE = "projects/langtons-ant.html"
DEMO_URL = "https://exios66.github.io/langtons-ant/"
CODE_URL = "https://github.com/Exios66/langtons-ant"
FIGURE = "classic-ant-highway.png"
SIDE_PROJECT_CARDS = ["wave-laboratory", "langtons-ant", "the-mandalay-bay"]


class LangtonsAntTests(unittest.TestCase):
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

    def test_card_sits_in_the_side_projects_group_and_links_to_the_case_study(self):
        page, parser = self.read_page("projects/index.html")
        heading = self.one(parser, "h2", id="side-projects-interests")
        start = next(i for i, (_, attrs, _) in enumerate(parser.elements) if attrs is heading)
        end = next((i for i in range(start + 1, len(parser.elements))
                    if parser.elements[i][0] == "h2"), len(parser.elements))
        cards = [attrs for _, attrs, _ in parser.elements[start:end] if "card" in checks.classes(attrs)]
        self.assertCountEqual([checks.attr(card, "id") for card in cards], SIDE_PROJECT_CARDS)
        card = next(card for card in cards if checks.attr(card, "id") == "langtons-ant")
        headings = [attrs for tag, attrs in parser.children(card) if tag == "h3"]
        self.assertEqual(len(headings), 1)
        links = [attrs for tag, attrs in parser.children(headings[0]) if tag == "a"]
        self.assertEqual(len(links), 1)
        self.assertEqual(destination(page, links[0]), (checks.DOCS / PAGE).resolve())
        kickers = [attrs for _, attrs in parser.children(card) if "kicker" in checks.classes(attrs)]
        self.assertEqual(len(kickers), 1)
        self.assertIn("version 0.1.0", parser.text(kickers[0]))
        tags = [attrs for _, attrs in parser.children(card) if "tag" in checks.classes(attrs)]
        self.assertTrue(tags, "Card needs at least one tag")

    def test_group_icon_is_unchanged_and_no_icon_was_added_for_this_page(self):
        _, index = self.read_page("projects/index.html")
        heading = self.one(index, "h2", id="side-projects-interests")
        uses = [attrs for tag, attrs in index.children(heading) if tag == "use"]
        self.assertEqual([checks.attr(attrs, "href") for attrs in uses], ["#i-waves"])
        _, parser = self.read_page()
        symbols = [checks.attr(attrs, "id") for tag, attrs, _ in parser.elements if tag == "symbol"]
        self.assertEqual(len(symbols), 20, "The sprite must keep exactly the existing 20 symbols")
        self.assertEqual(len(symbols), len(set(symbols)))
        for tag, attrs, _ in parser.elements:
            if tag == "svg" and "icon" in checks.classes(attrs):
                self.assertEqual(checks.attr(attrs, "width"), "1em")
                self.assertEqual(checks.attr(attrs, "height"), "1em")

    def test_navigation_back_link_and_actions_have_exact_destinations(self):
        page, parser = self.read_page()
        nav = self.one(parser, "div", **{"class": "project-nav"})
        links = [attrs for tag, attrs in parser.children(nav) if tag == "a"]
        self.assertEqual({parser.text(link): destination(page, link) for link in links},
                         {"Case study": page.resolve(), "Code": CODE_URL, "Live demo": DEMO_URL})
        current = [link for link in links if checks.attr(link, "aria-current") == "page"]
        self.assertEqual(len(current), 1)
        self.assertEqual(destination(page, current[0]), page.resolve())
        back = self.one(parser, "a", **{"class": "back"})
        self.assertEqual(destination(page, back), (checks.DOCS / "projects/index.html").resolve())
        actions = self.one(parser, "div", **{"class": "actions"})
        action_links = [checks.attr(attrs, "href") for tag, attrs in parser.children(actions) if tag == "a"]
        self.assertEqual(action_links, [DEMO_URL, CODE_URL])
        main_nav = self.one(parser, "nav", **{"aria-label": "Main"})
        marked = [link for tag, link in parser.children(main_nav)
                  if tag == "a" and checks.attr(link, "aria-current") == "page"]
        self.assertEqual(len(marked), 1)
        self.assertEqual(destination(page, marked[0]), (checks.DOCS / "projects/index.html").resolve())

    def test_it_is_a_case_study_only(self):
        self.assertFalse((checks.DOCS / "projects/langtons-ant/report.html").exists())
        self.assertFalse((checks.ROOT / "projects/langtons-ant/report.qmd").exists())
        _, parser = self.read_page()
        nav = self.one(parser, "div", **{"class": "project-nav"})
        self.assertNotIn("Technical report", parser.text(nav))

    def test_diagram_publishes_the_partial_without_geometry_loss(self):
        _, published = self.read_page()
        source = ContentParser(checks.ROOT / "partials/diagrams/_langtons-ant.qmd")
        diagram = self.one(published, "figure", **{"class": "diagram"})
        original = self.one(source, "figure", **{"class": "diagram"})
        self.assertEqual(diagram, original)
        self.assertEqual(published.children(diagram), source.children(original))
        caption = self.one(published, "figcaption", id=checks.attr(diagram, "aria-labelledby"))
        original_caption = self.one(source, "figcaption", id=checks.attr(original, "aria-labelledby"))
        self.assertTrue(published.text(caption))
        self.assertEqual(published.text(caption), source.text(original_caption))
        self.assertEqual(checks.attr(diagram, "role"), "img")

    def test_screenshot_has_alt_caption_provenance_and_identical_published_bytes(self):
        page, parser = self.read_page()
        source_dir = checks.ROOT / "projects/langtons-ant/figures"
        manifest = (source_dir / "MANIFEST.txt").read_text(encoding="utf-8")
        images = [(attrs, ancestors) for tag, attrs, ancestors in parser.elements if tag == "img"]
        self.assertEqual([urlsplit(checks.attr(attrs, "src")).path.rsplit("/", 1)[-1] for attrs, _ in images],
                         [FIGURE])
        image, ancestors = images[0]
        alt = checks.attr(image, "alt")
        self.assertGreater(len(alt.split()), 20, "Screenshot needs descriptive alt text")
        figures = [attrs for tag, attrs in ancestors if tag == "figure"]
        self.assertEqual(len(figures), 1)
        captions = [attrs for tag, attrs in parser.children(figures[0]) if tag == "figcaption"]
        self.assertEqual(len(captions), 1)
        self.assertTrue(parser.text(captions[0]), "Figure needs a visible caption")
        self.assertIn(f"{FIGURE} <- captured for this site:", manifest)
        self.assertIn("step 15,181", manifest)
        target = (page.parent / unquote(urlsplit(checks.attr(image, "src")).path)).resolve()
        self.assertEqual(target, (checks.DOCS / "projects/langtons-ant/figures" / FIGURE).resolve())
        self.assertEqual(target.read_bytes(), (source_dir / FIGURE).read_bytes())
        self.assertLess(target.stat().st_size, 200_000, "Keep the case study light; the demo GIF is too large")
        self.assertEqual(target.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_page_keeps_its_honesty_sections(self):
        _, parser = self.read_page()
        kicker = self.one(parser, "span", **{"class": "kicker"})
        self.assertIn("version 0.1.0", parser.text(kicker))
        self.assertNotIn("What does not work yet", " ".join("".join(d for d, _ in parser.text_fragments).split()))
        sources = self.one(parser, "h2", id="where-the-mathematics-comes-from")
        start = next(i for i, (_, attrs, _) in enumerate(parser.elements) if attrs is sources)
        end = next((i for i in range(start + 1, len(parser.elements))
                    if parser.elements[i][0] == "h2"), len(parser.elements))
        hosts = [urlsplit(checks.attr(attrs, "href")).netloc for tag, attrs, _ in parser.elements[start:end]
                 if tag == "a"]
        self.assertEqual(hosts.count("arxiv.org"), 5)
        self.assertIn("deepblue.lib.umich.edu", hosts)
        self.assertIn("github.com", hosts)
        body = self.one(parser, "div", **{"class": "page"})
        text = parser.text(body)
        for phrase in ("not from me", "None of the following is my work", "one laptop"):
            self.assertIn(phrase, text)
        self.assertNotIn("—", text, "Avoid em dashes in the body")

    def test_stats_match_what_was_run(self):
        _, parser = self.read_page()
        values = [parser.text(attrs) for _, attrs, _ in parser.elements
                  if "stat-value" in checks.classes(attrs)]
        self.assertEqual(values, ["38", "20", "64 × 64"])

    def test_description_canonical_and_sitemap_match_the_source(self):
        _, parser = self.read_page()
        source = (checks.ROOT / "projects/langtons-ant.qmd").read_text(encoding="utf-8")
        description = re.search(r'^description: "([^"]+)"$', source, re.MULTILINE)
        self.assertIsNotNone(description)
        for attribute, key in (("name", "description"), ("property", "og:description"),
                               ("name", "twitter:description")):
            meta = self.one(parser, "meta", **{attribute: key})
            # Pandoc turns the straight apostrophe in the source into a typographic one.
            self.assertEqual(checks.attr(meta, "content"), description.group(1).replace("'", "\u2019"))
        canonical = self.one(parser, "link", rel="canonical")
        self.assertEqual(checks.attr(canonical, "href"), SITE_URL + PAGE)
        locations = [node.text for node in ET.parse(checks.DOCS / "sitemap.xml").findall("{*}url/{*}loc")]
        self.assertEqual(locations.count(SITE_URL + PAGE), 1)
        self.assertNotIn(SITE_URL + "projects/langtons-ant/report.html", locations)

    def test_readme_links_the_published_case_study_once(self):
        readme = (checks.ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(readme.count(f"[Langton's Ant]({SITE_URL}{PAGE})"), 1)


if __name__ == "__main__":
    unittest.main()
