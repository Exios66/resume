"""Cross-page integrity checks for the rendered site.

Covers the report contents list, the previous/next project pager, the search
index, and two failure modes that are invisible until a reader hits them:
duplicate element ids and pages missing from the sitemap.
"""

import html
import json
import re
import unittest
import xml.etree.ElementTree as ET

import test_links as checks

SITE = "https://exios66.github.io/resume/"
ORDER = ["neuron-atlas", "digital-mailroom", "mailroom-ml", "mailroom-reloaded",
         "rvl-cdip-classifier", "mailroom-corpus-eda", "aeroglobe", "mapreduce-reloaded",
         "psychometric-digital-twin", "natd", "llm-personas", "wave-laboratory",
         "langtons-ant", "degen-llms"]
ID = re.compile(r'\sid="([^"]+)"')


def pages():
    return [p for p in checks.site_files(include_libs=False)]


def project_pages():
    return sorted(p for p in (checks.DOCS / "projects").rglob("*.html"))


class ReportContentsTests(unittest.TestCase):
    def navs(self, page):
        elements = checks.parse(page)
        return [(attributes, ancestors) for tag, attributes, ancestors in elements
                if tag == "nav" and "page-toc" in checks.classes(attributes)]

    def test_reports_and_appendices_have_a_contents_list_that_resolves(self):
        checked = 0
        for page in project_pages():
            is_report = page.name in ("report.html", "appendix.html")
            elements = checks.parse(page)
            navs = [(attributes, ancestors) for tag, attributes, ancestors in elements
                    if tag == "nav" and "page-toc" in checks.classes(attributes)]
            if not is_report:
                self.assertEqual(navs, [], f"{checks.rel(page)} should not carry a contents list")
                continue
            checked += 1
            self.assertEqual(len(navs), 1, f"{checks.rel(page)} needs one contents list")
            nav, _ = navs[0]
            links = [a for tag, a, ancestors in elements
                     if tag == "a" and any(parent is nav for _, parent in ancestors)]
            headings = {checks.attr(a, "id"): tag for tag, a, _ in elements if tag in ("h2", "h3")}
            ids = set(ID.findall(page.read_text(encoding="utf-8")))
            self.assertGreaterEqual(len(links), 3, f"{checks.rel(page)} lists too few sections")
            for link in links:
                href = checks.attr(link, "href")
                self.assertTrue(href.startswith("#"), f"{checks.rel(page)}: {href}")
                self.assertIn(href[1:], ids, f"{checks.rel(page)}: broken {href}")
                self.assertEqual(headings.get(href[1:]), "h2",
                                 f"{checks.rel(page)}: {href} is not a level-2 heading")
        self.assertGreaterEqual(checked, 9)


class ProjectPagerTests(unittest.TestCase):
    def pager(self, page):
        elements = checks.parse(page)
        return next((attributes for tag, attributes, _ in elements
                     if tag == "nav" and "project-pager" in checks.classes(attributes)), None)

    def targets(self, page):
        elements = checks.parse(page)
        found = []
        for tag, attributes, ancestors in elements:
            if tag != "a":
                continue
            if not any("project-pager" in checks.classes(parent) for _, parent in ancestors):
                continue
            href = checks.attr(attributes, "href")
            found.append((checks.attr(attributes, "rel"), (page.parent / href).resolve()))
        return found

    def test_every_project_page_has_the_expected_previous_and_next(self):
        all_projects = (checks.DOCS / "projects").resolve()
        seen = set()
        for page in project_pages():
            slug = page.relative_to(checks.DOCS / "projects").parts[0].removesuffix(".html")
            if slug not in ORDER:
                continue
            seen.add(slug)
            self.assertIsNotNone(self.pager(page), f"{checks.rel(page)} has no pager")
            index = ORDER.index(slug)
            expected = {}
            if index > 0:
                expected["prev"] = all_projects / f"{ORDER[index - 1]}.html"
            if index < len(ORDER) - 1:
                expected["next"] = all_projects / f"{ORDER[index + 1]}.html"
            self.assertEqual(dict(self.targets(page)), expected, checks.rel(page))
        self.assertEqual(seen, set(ORDER))


class SearchTests(unittest.TestCase):
    def test_search_page_has_a_form_status_and_results_container(self):
        page = checks.DOCS / "search.html"
        self.assertTrue(page.is_file())
        elements = checks.parse(page)
        self.assertTrue([a for tag, a, _ in elements
                         if tag == "form" and "site-search" in checks.classes(a)])
        self.assertTrue([a for tag, a, _ in elements if checks.attr(a, "id") == "search-status"])
        self.assertTrue([a for tag, a, _ in elements if checks.attr(a, "id") == "search-results"])
        self.assertTrue([a for tag, a, _ in elements if tag == "noscript"])

    def test_search_index_covers_every_public_page_once(self):
        entries = json.loads((checks.DOCS / "search-index.json").read_text(encoding="utf-8"))
        listed = [entry["u"] for entry in entries]
        public = [p.relative_to(checks.DOCS).as_posix() for p in pages() if p.name != "search.html"]
        self.assertEqual(sorted(listed), sorted(public))
        self.assertEqual(len(listed), len(set(listed)))
        for entry in entries:
            self.assertTrue(entry["t"])
            self.assertNotIn("<", entry["b"] + entry["h"])
            self.assertIn(entry["u"], {p.relative_to(checks.DOCS).as_posix() for p in pages()})


class RenderingIntegrityTests(unittest.TestCase):
    def test_no_page_has_duplicate_ids(self):
        for page in pages():
            ids = ID.findall(page.read_text(encoding="utf-8"))
            duplicates = {value for value in ids if ids.count(value) > 1}
            self.assertFalse(duplicates, f"{checks.rel(page)}: duplicate ids {sorted(duplicates)}")

    def test_every_page_is_in_the_sitemap_once(self):
        locations = [node.text for node in ET.parse(checks.DOCS / "sitemap.xml").findall("{*}url/{*}loc")]
        for page in pages():
            rel = page.relative_to(checks.DOCS).as_posix()
            self.assertEqual(locations.count(SITE + rel), 1, rel)

    def test_no_rendered_page_leaks_source_paths_or_todo(self):
        for page in pages():
            text = page.read_text(encoding="utf-8")
            for marker in ("/Users/", "C:\\", "TODO", "<!-- src"):
                self.assertNotIn(marker, text, f"{checks.rel(page)}: {marker}")


if __name__ == "__main__":
    unittest.main()
