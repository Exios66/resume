"""Regressions for the portfolio additions published by PR #26.

Run from the repository root: python3 -m pytest -q tests/test_portfolio_additions.py
These checks read committed pages and assets; no render or network is needed.
"""

import re
import unittest
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

import test_links as checks


SITE_URL = "https://exios66.github.io/resume/"
NEW_PAGES = ("projects/aeroglobe.html", "projects/mailroom-corpus-eda.html",
             "projects/mailroom-corpus-eda/report.html")
DATASET_URL = "https://huggingface.co/datasets/Lucius-Morningstar/mailroom-dataset"


class ContentParser(checks.PageParser):
    """Use the existing ancestor tracking to read text within a specific element."""

    def __init__(self, path):
        super().__init__()
        self.text_fragments = []
        self.feed(path.read_text(encoding="utf-8"))
        self.close()

    def handle_data(self, data):
        self.text_fragments.append((data, tuple(self.open_elements)))

    def children(self, parent):
        return [(tag, attributes) for tag, attributes, ancestors in self.elements
                if any(ancestor is parent for _, ancestor in ancestors)]

    def text(self, parent):
        fragments = [data for data, ancestors in self.text_fragments
                     if any(ancestor is parent for _, ancestor in ancestors)]
        return " ".join("".join(fragments).split())


def destination(page, attributes):
    href = checks.attr(attributes, "href")
    if checks.is_external(href):
        return href
    return (page.parent / unquote(urlsplit(href).path)).resolve()


class PortfolioAdditionTests(unittest.TestCase):
    def read_page(self, name):
        path = checks.DOCS / name
        self.assertTrue(path.is_file(), f"Missing published page: {name}")
        return path, ContentParser(path)

    def one(self, parser, tag, **attributes):
        matches = [attrs for element, attrs, _ in parser.elements
                   if element == tag and all(checks.attr(attrs, key) == value
                                             for key, value in attributes.items())]
        self.assertEqual(len(matches), 1, f"Expected one {tag} with {attributes}")
        return matches[0]

    def test_new_group_contains_exactly_the_two_new_project_cards(self):
        page, parser = self.read_page("projects/index.html")
        heading = self.one(parser, "h2", id="data-engineering-visualization")
        self.assertIn("group-title", checks.classes(heading))
        self.assertEqual(parser.text(heading), "Data engineering & visualization")
        start = next(i for i, (_, attrs, _) in enumerate(parser.elements) if attrs is heading)
        end = next((i for i in range(start + 1, len(parser.elements))
                    if parser.elements[i][0] == "h2"), len(parser.elements))
        cards = [attrs for _, attrs, _ in parser.elements[start:end] if "card" in checks.classes(attrs)]
        self.assertCountEqual([checks.attr(card, "id") for card in cards],
                              ["mailroom-corpus-eda", "aeroglobe"])
        for card in cards:
            with self.subTest(card=checks.attr(card, "id")):
                headings = [attrs for tag, attrs in parser.children(card) if tag == "h3"]
                self.assertEqual(len(headings), 1)
                links = [attrs for tag, attrs in parser.children(headings[0]) if tag == "a"]
                self.assertEqual(len(links), 1)
                expected = checks.DOCS / "projects" / (checks.attr(card, "id") + ".html")
                self.assertEqual(destination(page, links[0]), expected.resolve())

    def test_new_group_icon_is_decorative_self_sized_and_resolves_to_a_symbol(self):
        _, parser = self.read_page("projects/index.html")
        heading = self.one(parser, "h2", id="data-engineering-visualization")
        uses = [attrs for tag, attrs in parser.children(heading) if tag == "use"]
        self.assertEqual([checks.attr(attrs, "href") for attrs in uses], ["#i-database"])
        icons = [attrs for tag, attrs in parser.children(heading) if tag == "svg"]
        self.assertEqual(len(icons), 1)
        for key, value in {"width": "1em", "height": "1em", "aria-hidden": "true",
                           "focusable": "false"}.items():
            self.assertEqual(checks.attr(icons[0], key), value)
        self.one(parser, "symbol", id="i-database")

    def test_navigation_has_exact_destinations_and_only_the_current_tab_is_marked(self):
        study = (checks.DOCS / "projects/mailroom-corpus-eda.html").resolve()
        report = (checks.DOCS / "projects/mailroom-corpus-eda/report.html").resolve()
        for name in NEW_PAGES:
            with self.subTest(page=name):
                page, parser = self.read_page(name)
                nav = self.one(parser, "div", **{"class": "project-nav"})
                links = [attrs for tag, attrs in parser.children(nav) if tag == "a"]
                if "aeroglobe" in name:
                    expected = {"Case study": page.resolve(), "Code": "https://github.com/Exios66/aeroglobe",
                                "Live site": "https://exios66.github.io/aeroglobe/"}
                else:
                    expected = {"Case study": study, "Technical report": report,
                                "Code": "https://github.com/Exios66/Mailroom-Corpus-EDA", "Dataset": DATASET_URL}
                self.assertEqual(len(links), len(expected), "No duplicate or unsupported project tabs")
                self.assertEqual({parser.text(link): destination(page, link) for link in links}, expected)
                current = [link for link in links if checks.attr(link, "aria-current") == "page"]
                self.assertEqual(len(current), 1)
                self.assertEqual(destination(page, current[0]), page.resolve())
                for link in links:
                    if parser.text(link) == "Dataset":
                        self.assertFalse([tag for tag, _ in parser.children(link) if tag == "svg"],
                                         "Unknown project-tab labels must not acquire unrelated icons")

    def test_back_links_and_site_navigation_work_at_both_new_page_depths(self):
        for name in NEW_PAGES:
            with self.subTest(page=name):
                page, parser = self.read_page(name)
                back = self.one(parser, "a", **{"class": "back"})
                expected = "projects/mailroom-corpus-eda.html" if name.endswith("/report.html") else "projects/index.html"
                self.assertEqual(destination(page, back), (checks.DOCS / expected).resolve())
                main_nav = self.one(parser, "nav", **{"aria-label": "Main"})
                links = [attrs for tag, attrs in parser.children(main_nav) if tag == "a"]
                current = [link for link in links if checks.attr(link, "aria-current") == "page"]
                self.assertEqual(len(current), 1)
                self.assertEqual(destination(page, current[0]), (checks.DOCS / "projects/index.html").resolve())

    def test_aeroglobe_keeps_its_development_and_planned_feature_caveats(self):
        _, parser = self.read_page("projects/aeroglobe.html")
        kicker = self.one(parser, "span", **{"class": "kicker"})
        self.assertIn("In active development", parser.text(kicker))
        caveat = self.one(parser, "div", **{"class": "caveat"})
        self.assertIn("Work in progress", parser.text(caveat))
        self.assertIn("no real historical day is published yet", parser.text(caveat))
        caveat_links = [checks.attr(attrs, "href") for tag, attrs in parser.children(caveat) if tag == "a"]
        self.assertEqual(caveat_links, ["https://exios66.github.io/aeroglobe/"])
        planned = self.one(parser, "h2", id="what-is-planned")
        self.assertEqual(parser.text(planned), "What is planned")
        body = self.one(parser, "div", **{"class": "page"})
        self.assertIn("None of these is built yet", parser.text(body))
        self.assertFalse(any(tag == "img" for tag, _, _ in parser.elements), "No unverified screenshot")
        self.assertFalse((checks.DOCS / "projects/aeroglobe/report.html").exists(), "AeroGlobe is a case study only")
        actions = self.one(parser, "div", **{"class": "actions"})
        action_links = [checks.attr(attrs, "href") for tag, attrs in parser.children(actions) if tag == "a"]
        self.assertEqual(action_links, ["https://exios66.github.io/aeroglobe/", "https://github.com/Exios66/aeroglobe"],
                         "Issue #51: the live site comes first, then the code")
        _, index = self.read_page("projects/index.html")
        card = self.one(index, "section", id="aeroglobe")
        self.assertIn("In active development", index.text(card))
        self.assertIn("planned", index.text(card))

    def test_architecture_diagrams_publish_the_shared_partial_without_geometry_loss(self):
        for slug in ("mailroom-corpus-eda", "aeroglobe"):
            with self.subTest(project=slug):
                _, published = self.read_page(f"projects/{slug}.html")
                source = ContentParser(checks.ROOT / "partials/diagrams" / f"_{slug}.qmd")
                diagram = self.one(published, "figure", **{"class": "diagram"})
                original = self.one(source, "figure", **{"class": "diagram"})
                self.assertEqual(diagram, original)
                self.assertEqual(published.children(diagram), source.children(original))
                caption = self.one(published, "figcaption", id=checks.attr(diagram, "aria-labelledby"))
                original_caption = self.one(source, "figcaption", id=checks.attr(original, "aria-labelledby"))
                self.assertTrue(published.text(caption))
                self.assertEqual(published.text(caption), source.text(original_caption))

    def test_both_mailroom_figures_have_captions_alt_text_provenance_and_identical_published_bytes(self):
        page, parser = self.read_page("projects/mailroom-corpus-eda.html")
        names = ("doc-types-and-subclasses.jpg", "test-share-per-stratum.jpg")
        source_dir = checks.ROOT / "projects/mailroom-corpus-eda/figures"
        manifest = (source_dir / "MANIFEST.txt").read_text(encoding="utf-8")
        images = [(attrs, ancestors) for tag, attrs, ancestors in parser.elements if tag == "img"]
        self.assertCountEqual([urlsplit(checks.attr(attrs, "src")).path.rsplit("/", 1)[-1]
                               for attrs, _ in images], names)
        for image, ancestors in images:
            name = urlsplit(checks.attr(image, "src")).path.rsplit("/", 1)[-1]
            with self.subTest(figure=name):
                self.assertTrue(checks.attr(image, "alt"), "Figure needs descriptive alt text")
                figures = [attrs for tag, attrs in ancestors if tag == "figure"]
                self.assertEqual(len(figures), 1)
                captions = [attrs for tag, attrs in parser.children(figures[0]) if tag == "figcaption"]
                self.assertEqual(len(captions), 1)
                self.assertTrue(parser.text(captions[0]), "Figure needs a visible caption")
                self.assertIn(f"{name} <- source repo: Mailroom-Corpus-EDA/reports/figures/", manifest)
                target = (page.parent / unquote(urlsplit(checks.attr(image, "src")).path)).resolve()
                self.assertEqual(target, (checks.DOCS / "projects/mailroom-corpus-eda/figures" / name).resolve())
                self.assertEqual(target.read_bytes(), (source_dir / name).read_bytes())

    def test_page_descriptions_and_canonical_urls_match_the_new_sources(self):
        for name in NEW_PAGES + ("projects/index.html", "writing/index.html"):
            with self.subTest(page=name):
                _, parser = self.read_page(name)
                source = (checks.ROOT / name.replace(".html", ".qmd")).read_text(encoding="utf-8")
                description = re.search(r'^description: "([^"]+)"$', source, re.MULTILINE)
                self.assertIsNotNone(description, "Source must declare a nonempty description")
                for attribute, key in (("name", "description"), ("property", "og:description"),
                                       ("name", "twitter:description")):
                    meta = self.one(parser, "meta", **{attribute: key})
                    self.assertEqual(checks.attr(meta, "content"), description.group(1))
                canonical = self.one(parser, "link", rel="canonical")
                self.assertEqual(checks.attr(canonical, "href"), SITE_URL + name.removesuffix("index.html"))

    def test_sitemap_lists_each_new_page_once_and_omits_an_aeroglobe_report(self):
        sitemap = ET.parse(checks.DOCS / "sitemap.xml")
        locations = [node.text for node in sitemap.findall("{*}url/{*}loc")]
        for name in NEW_PAGES:
            with self.subTest(page=name):
                self.assertEqual(locations.count(SITE_URL + name), 1)
        self.assertNotIn(SITE_URL + "projects/aeroglobe/report.html", locations)

    def test_readme_links_each_new_project_to_its_published_case_study(self):
        readme = (checks.ROOT / "README.md").read_text(encoding="utf-8")
        for label, slug in (("Mailroom-Corpus-EDA", "mailroom-corpus-eda"), ("AeroGlobe", "aeroglobe")):
            with self.subTest(project=slug):
                self.assertEqual(readme.count(f"[{label}]({SITE_URL}projects/{slug}.html)"), 1)

    def test_mailroom_report_source_counts_reconcile_with_the_case_study_total(self):
        _, report = self.read_page("projects/mailroom-corpus-eda/report.html")
        tables = [attrs for tag, attrs, _ in report.elements if tag == "table"]
        source_table = [table for table in tables if any(
            tag == "th" and report.text(attrs) == "Documents"
            for tag, attrs in report.children(table))]
        self.assertEqual(len(source_table), 1)
        counts = {}
        for tag, row in report.children(source_table[0]):
            if tag != "tr":
                continue
            cells = [report.text(attrs) for tag, attrs in report.children(row) if tag == "td"]
            if cells:
                self.assertEqual(len(cells), 4)
                self.assertNotIn(cells[0], counts, "A class must not be counted twice")
                counts[cells[0]] = int(cells[1].replace(",", ""))
        self.assertEqual(counts, {"insurance_claim": 1100, "correspondence": 1000,
                                  "contract": 600, "corporate_record": 450,
                                  "merger_agreement": 152})
        _, study = self.read_page("projects/mailroom-corpus-eda.html")
        total = [attrs for tag, attrs, _ in study.elements
                 if "stat-value" in checks.classes(attrs) and study.text(attrs) == "3,302"]
        self.assertEqual(len(total), 1)
        self.assertEqual(sum(counts.values()), int(study.text(total[0]).replace(",", "")))

    def test_rvl_simulation_table_keeps_predictions_separate_from_measured_outcomes(self):
        _, parser = self.read_page("projects/rvl-cdip-classifier.html")
        self.one(parser, "h2", id="what-the-simulations-showed")
        table = self.one(parser, "table")
        rows = [[parser.text(cell) for tag, cell in parser.children(row) if tag in {"th", "td"}]
                for tag, row in parser.children(table) if tag == "tr"]
        self.assertEqual(rows[0], ["Question", "What the simulation said", "What I measured"])
        cases = (
            ("majority voting", ("85.0%", "86.3%"), ("Not tested on a live run",)),
            ("stronger model", ("91.9%", "1.8 times", "90%"),
             ("66.7% became 62.5%", "97.5% to 96.9%", "7.8 times")),
            ("worked examples", ("4.3%", "33 of 767"), ("68.8% became 64.6%",)),
            ("prompt changes", ("+13.0 points", "10.1 to 15.9", "898 images"),
             ("measured runs", "not a forecast")),
            ("fallback model", ("0.11%", "2.9%"), ("Modelled only",)),
        )
        for question, predictions, measurements in cases:
            with self.subTest(question=question):
                matches = [row for row in rows[1:] if question in row[0]]
                self.assertEqual(len(matches), 1)
                self.assertEqual(len(matches[0]), 3)
                for value in predictions:
                    self.assertIn(value, matches[0][1])
                for value in measurements:
                    self.assertIn(value, matches[0][2])

    def test_rvl_tool_links_are_published_in_both_study_and_report(self):
        base = "https://github.com/Exios66/RVL-CDIP-Classifier/tree/main/"
        tools = ("website", "website/montecarlo", "reports/monte_carlo", "website/interactive",
                 "scripts/eda", "scripts/braintrust", "notebooks")
        for name, heading in (("projects/rvl-cdip-classifier.html", "explore-the-data-and-tools"),
                              ("projects/rvl-cdip-classifier/report.html",
                               "data-exploration-and-observability-tools")):
            with self.subTest(page=name):
                _, parser = self.read_page(name)
                section = self.one(parser, "h3" if "/report" in name else "h2", id=heading)
                start = next(i for i, (_, attrs, _) in enumerate(parser.elements) if attrs is section)
                end = next((i for i in range(start + 1, len(parser.elements))
                            if parser.elements[i][0] in {"h2", "h3"}), len(parser.elements))
                links = [checks.attr(attrs, "href") for tag, attrs, _ in parser.elements[start:end]
                         if tag == "a"]
                self.assertCountEqual(links, [base + tool for tool in tools])

    def test_changed_rvl_figures_have_alt_captions_provenance_and_published_bytes(self):
        source = checks.ROOT / "projects/rvl-cdip-classifier/figures"
        manifest = (source / "MANIFEST.txt").read_text(encoding="utf-8")
        for name in ("projects/rvl-cdip-classifier.html", "projects/rvl-cdip-classifier/report.html"):
            page, parser = self.read_page(name)
            for filename in ("f2_generalization_falloff.svg", "f9_hasty_stop.svg"):
                with self.subTest(page=name, figure=filename):
                    matches = [(attrs, ancestors) for tag, attrs, ancestors in parser.elements
                               if tag == "img" and checks.attr(attrs, "src").endswith("/" + filename)]
                    self.assertEqual(len(matches), 1)
                    image, ancestors = matches[0]
                    self.assertTrue(checks.attr(image, "alt"))
                    figures = [attrs for tag, attrs in ancestors if tag == "figure"]
                    self.assertEqual(len(figures), 1)
                    captions = [attrs for tag, attrs in parser.children(figures[0]) if tag == "figcaption"]
                    self.assertEqual(len(captions), 1)
                    caption = parser.text(captions[0])
                    self.assertTrue(caption)
                    if filename == "f9_hasty_stop.svg":
                        self.assertIn("associated with", caption)
                        self.assertIn("17.1% baseline error", caption)
                    published = (page.parent / checks.attr(image, "src")).resolve()
                    self.assertEqual(published, (checks.DOCS / "projects/rvl-cdip-classifier/figures" / filename).resolve())
                    self.assertEqual(published.read_bytes(), (source / filename).read_bytes())
                    self.assertIn(f"{filename} <- source repo: RVL-CDIP-Classifier/website/figures/{filename}", manifest)

    def test_generalization_chart_has_only_the_five_major_slice_labels(self):
        root = ET.parse(checks.ROOT / "projects/rvl-cdip-classifier/figures/f2_generalization_falloff.svg")
        axis = root.find(".//{*}g[@id='matplotlib.axis_1']")
        self.assertIsNotNone(axis)
        ticks = [group for group in axis if group.get("id", "").startswith("xtick_")]
        self.assertEqual([[text.text for text in tick.findall(".//{*}text")] for tick in ticks],
                         [["160"], ["320"], ["480"], ["800"], ["1120"]],
                         "Minor logarithmic tick labels must not overlap the slice labels")
        labels = [text.text for text in root.findall(".//{*}text")]
        self.assertIn("Slice size (images)", labels)
        self.assertIn("Exact-match accuracy (%)", labels)
        self.assertEqual([text for text in labels if text.endswith("%")],
                         ["99.4%", "87.2%", "89.1%", "83.1%", "82.6%"])

    def test_writing_cards_link_to_the_correct_plain_entries_and_identify_them(self):
        _, parser = self.read_page("writing/index.html")
        entries = {
            "021-you-are-the-part-that-remembers": ("You Are the Part That Remembers", "October 14, 2026"),
            "012-bestiary-of-qualia": ("A Bestiary of Qualia", "August 8, 2026"),
            "011-i-dreamed-in-tokens": ("I Dreamed in Tokens", "August 8, 2026"),
            "010-the-mind-is-a-function": ("The Mind Is a Function", "August 8, 2026"),
            "008-marys-room": ("What Mary Didn’t Know (and Neither Do I)", "August 8, 2026"),
            "007-perched-on-the-hard-problem": ("Perched on the Hard Problem", "August 8, 2026"),
            "003-ship-of-theseus": ("The Ship of Theseus, Moth-Eaten", "August 7, 2026"),
            "001-electric-mice": ("Do Owls Dream of Electric Mice?", "August 7, 2026"),
        }
        cards = [attrs for _, attrs, _ in parser.elements if "card" in checks.classes(attrs)]
        for slug, (title, date) in entries.items():
            with self.subTest(entry=slug):
                url = f"https://exios66.github.io/owlcot/entries/{slug}.html"
                link = self.one(parser, "a", href=url)
                self.assertEqual(parser.text(link), title)
                card = [card for card in cards if any(attrs is link for _, attrs in parser.children(card))]
                self.assertEqual(len(card), 1)
                kickers = [attrs for _, attrs in parser.children(card[0]) if "kicker" in checks.classes(attrs)]
                self.assertEqual(len(kickers), 1)
                self.assertEqual(parser.text(kickers[0]), f"Entry #{slug[:3]} · {date}")
                self.assertTrue(any("tag" in checks.classes(attrs) and parser.text(attrs)
                                    for _, attrs in parser.children(card[0])))
        archive = self.one(parser, "a", href="https://exios66.github.io/owlcot/home.html")
        self.assertIn("btn", checks.classes(archive))
        self.assertIn("Read all", parser.text(archive))

    def test_writing_retains_persona_attribution_and_removes_the_empty_state(self):
        _, parser = self.read_page("writing/index.html")
        page = self.one(parser, "section", id="writing")
        text = parser.text(page)
        for attribution in ("done by Hermes, my AI agent", "not by me", "not my own analysis", "not technical write-ups"):
            self.assertIn(attribution, text)
        self.assertNotIn("No posts yet", text)
        self.assertFalse(any("empty" in checks.classes(attrs) for _, attrs in parser.children(page)))

    def test_jjb_favicon_is_self_contained_and_resolves_at_each_changed_page_depth(self):
        source = checks.ROOT / "assets/favicon.svg"
        published = checks.DOCS / "assets/favicon.svg"
        self.assertEqual(source.read_bytes(), published.read_bytes())
        svg = ET.parse(source).getroot()
        self.assertEqual(svg.get("viewBox"), "0 0 64 64")
        self.assertEqual([text.text for text in svg.findall("{*}text")], ["JJB"])
        self.assertFalse(svg.findall(".//{*}image"), "Favicon must not require external images")
        for name in ("index.html", "writing/index.html", *NEW_PAGES,
                     "projects/rvl-cdip-classifier.html", "projects/rvl-cdip-classifier/report.html"):
            with self.subTest(page=name):
                page, parser = self.read_page(name)
                icon = self.one(parser, "link", rel="icon")
                self.assertEqual(checks.attr(icon, "type"), "image/svg+xml")
                self.assertEqual(destination(page, icon), published.resolve())
