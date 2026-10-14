"""Unit tests of the PR's rendered-site validator, using synthetic sites only.

Run from the repository root: python3 -m pytest -q tests/test_links_unit.py
"""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_links as checks


class TemporarySiteTestCase(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        override = patch.object(checks, "DOCS", self.docs)
        override.start()
        self.addCleanup(override.stop)
        self.page = self.write("projects/study.html", "<main>Study</main>")

    def write(self, name, text):
        path = self.docs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class PageParserTests(TemporarySiteTestCase):
    def test_ancestors_survive_void_and_self_closing_elements(self):
        self.page.write_text(
            '<figure class="diagram"><img src="chart.svg"/><br>'
            '<svg><path/></svg><figcaption id="caption">A &amp; B</figcaption>'
            '</figure><p>Outside</p>', encoding="utf-8")
        elements = checks.parse(self.page)
        self.assertEqual([tag for tag, _, _ in elements],
                         ["figure", "img", "br", "svg", "path", "figcaption", "p"])
        by_tag = {tag: ancestors for tag, _, ancestors in elements}
        self.assertEqual([tag for tag, _ in by_tag["svg"]], ["figure"])
        self.assertEqual([tag for tag, _ in by_tag["path"]], ["figure", "svg"])
        self.assertEqual([tag for tag, _ in by_tag["figcaption"]], ["figure"])
        self.assertEqual(by_tag["p"], ())

    def test_first_duplicate_attribute_matches_browser_semantics(self):
        parser = checks.PageParser()
        parser.feed('<A HREF="first.html?a=1&amp;b=2" href="second.html" hidden hidden="no">')
        tag, attributes, _ = parser.elements[0]
        self.assertEqual(tag, "a")
        self.assertEqual(attributes, {"href": "first.html?a=1&b=2", "hidden": None})

    def test_mismatched_and_unmatched_closers_do_not_leak_ancestors(self):
        parser = checks.PageParser()
        parser.feed('<div><span></div></missing><svg/></span><p>Outside</p>')
        self.assertEqual(parser.elements[-2][2], ())
        self.assertEqual(parser.elements[-1][2], ())

    def test_attribute_normalization_handles_missing_and_boolean_values(self):
        for attributes in ({}, {"class": None}, {"class": " \t "}):
            with self.subTest(attributes=attributes):
                self.assertEqual(checks.attr(attributes, "class"), "")
                self.assertEqual(checks.classes(attributes), set())
        self.assertEqual(checks.classes({"class": " diagram\twide\ndiagram "}), {"diagram", "wide"})


class LinkHelperTests(TemporarySiteTestCase):
    def test_external_urls_and_local_paths_are_distinguished(self):
        for value in ("https://example.org/page", "HTTP://example.org", "//example.org/a",
                      "mailto:author@example.org", "tel:+15555550100", "data:image/png;base64,AA==",
                      "javascript:void(0)"):
            with self.subTest(value=value):
                self.assertTrue(checks.is_external(value))
        for value in ("", "#caption", "?view=full", "../index.html", "/resume/index.html"):
            with self.subTest(value=value):
                self.assertFalse(checks.is_external(value))

    def test_all_supported_url_attributes_are_extracted(self):
        attributes_by_tag = {
            "a": ("href",), "link": ("href",), "script": ("src",),
            "img": ("src", "srcset"), "source": ("src", "srcset"),
            "iframe": ("src",), "video": ("src", "poster"), "audio": ("src",),
            "use": ("href", "xlink:href"), "image": ("href", "xlink:href"),
        }
        for tag, names in attributes_by_tag.items():
            with self.subTest(tag=tag):
                attributes = {name: f" {name}.svg " for name in names}
                attributes["title"] = "not-a-link.svg"
                self.assertEqual(list(checks.link_values(tag, attributes)),
                                 [f"{name}.svg" for name in names])
        self.assertEqual(list(checks.link_values("div", {"href": "ignore.html"})), [])
        self.assertEqual(list(checks.link_values("a", {})), [])
        self.assertEqual(list(checks.link_values("a", {"href": None})), [""])

    def test_srcset_ignores_empty_candidates_and_keeps_each_url(self):
        attributes = {"src": "fallback.png", "srcset": " , small.png 1x,, big.png 2x, wide.png 640w, "}
        self.assertEqual(list(checks.link_values("img", attributes)),
                         ["fallback.png", "small.png", "big.png", "wide.png"])

    def test_links_decode_paths_and_ignore_query_and_fragment(self):
        self.write("index.html", "Home")
        self.write("assets/a chart.svg", "<svg/>")
        for value in ("study.html", "./study.html?download=1#top", "../index.html",
                      "../assets/a%20chart.svg?size=2#caption", "", "#heading", "?view=full"):
            with self.subTest(value=value):
                self.assertIsNone(checks.link_problem(self.page, value))

    def test_directories_need_a_landing_page_and_missing_files_are_rejected(self):
        self.write("projects/report/index.html", "Report")
        (self.docs / "projects/empty").mkdir()
        self.assertIsNone(checks.link_problem(self.page, "report/"))
        self.assertEqual(checks.link_problem(self.page, "empty/"), "directory without index.html")
        self.assertEqual(checks.link_problem(self.page, "absent.svg"), "missing target")

    def test_absolute_traversing_and_symlink_paths_cannot_escape_docs(self):
        outside = self.root / "private.html"
        outside.write_text("Outside the published site", encoding="utf-8")
        (self.docs / "projects/escape.html").symlink_to(outside)
        for value in ("../../private.html", "%2e%2e/%2e%2e/private.html", "escape.html",
                      "%2Fprivate.html"):
            with self.subTest(value=value):
                self.assertEqual(checks.link_problem(self.page, value), "resolves outside docs/")
        self.assertEqual(checks.link_problem(self.page, "/resume/index.html"),
                         "root-relative link; the site is served under /resume/")

    def test_linked_targets_only_collects_relative_anchor_destinations(self):
        self.page.write_text(
            '<a href="../index.html?x=1#top">Home</a><a href="../index.html">Again</a>'
            '<a href="a%20chart.html">Chart</a><a href="?view=full">Self</a>'
            '<a href="#top">Fragment</a><a href="/resume/">Root</a>'
            '<a href="//example.org">External</a><a href="mailto:a@example.org">Mail</a>'
            '<a>No destination</a><img src="image.png"><link href="style.css">', encoding="utf-8")
        self.assertEqual(checks.linked_targets(self.page), {
            (self.docs / "index.html").resolve(),
            (self.page.parent / "a chart.html").resolve(), self.page.resolve(),
        })

    def test_site_files_filter_suffixes_and_only_the_top_level_library_directory(self):
        self.write("site_libs/vendor.HTML", "Vendor")
        self.write("projects/site_libs/figure.SVG", "<svg/>")
        self.write("assets/figure.SVG", "<svg/>")
        self.write("assets/notes.TXT", "Notes")
        self.write("assets/image.png", "Image")
        (self.docs / "directory.html").mkdir()
        self.assertEqual(list(checks.site_files()),
                         [self.page, self.docs / "site_libs/vendor.HTML"])
        self.assertEqual(list(checks.site_files(checks.TEXT_SUFFIXES, include_libs=False)), sorted([
            self.page, self.docs / "projects/site_libs/figure.SVG",
            self.docs / "assets/figure.SVG", self.docs / "assets/notes.TXT",
        ]))
        self.assertEqual(checks.rel(self.page), "projects/study.html")

    def test_scan_variants_reveals_encoded_and_tag_split_text(self):
        source = '<b>author&#64;exam</b>ple%2Enet'
        variants = checks.scan_variants(source)
        self.assertEqual(variants["raw"], source)
        self.assertEqual(variants["decoded"], '<b>author@exam</b>ple.net')
        self.assertEqual(variants["tags stripped"], 'author&#64;example%2Enet')
        self.assertEqual(variants["decoded, tags stripped"], 'author@example.net')


class ValidatorTests(TemporarySiteTestCase):
    """Prove the checks reject bad fixtures, rather than only passing docs/."""

    def run_check(self, name):
        getattr(checks.RenderedSiteTests(methodName=name), name)()

    def test_internal_link_check_accepts_existing_and_external_targets(self):
        self.write("assets/chart.svg", "<svg/>")
        self.page.write_text(
            '<img src="../assets/chart.svg" srcset="../assets/chart.svg 2x">'
            '<a href="https://example.org/absent">External</a><use href="#marker"/>', encoding="utf-8")
        self.run_check("test_internal_links_resolve")

    def test_internal_link_check_rejects_missing_targets_in_each_url_attribute(self):
        for markup in ('<a href="missing.html">Missing</a>', '<script src="missing.js"></script>',
                       '<img srcset="study.html 1x, missing.png 2x">',
                       '<video poster="missing.jpg"></video>', '<svg><use xlink:href="missing.svg"/></svg>',
                       '<a href="/resume/index.html">Root</a>'):
            with self.subTest(markup=markup):
                self.page.write_text(markup, encoding="utf-8")
                with self.assertRaisesRegex(AssertionError, "broken internal links"):
                    self.run_check("test_internal_links_resolve")

    def test_image_check_accepts_alt_and_explicitly_decorative_images(self):
        self.page.write_text(
            '<img alt="Chart"><img role="presentation"><img role="none">'
            '<img aria-hidden="TRUE"><figure class="diagram" role="img" aria-label="Pipeline">'
            '<svg/></figure><figure class="diagram" role="img" aria-labelledby="title caption">'
            '<svg><title id="title">Pipeline</title></svg><figcaption id="caption">Flow</figcaption>'
            '</figure><svg class="icon"/>', encoding="utf-8")
        self.run_check("test_images_have_alt")

    def test_image_check_rejects_empty_alt_and_invalid_diagram_labels(self):
        for markup in ('<img src="chart.svg">', '<img alt=" \t ">', '<img aria-hidden="false">',
                       '<figure class="diagram" aria-label="Flow"><svg/></figure>',
                       '<figure class="diagram" role="img"><svg/></figure>',
                       '<figure class="diagram" role="img" aria-labelledby="missing"><svg/></figure>'):
            with self.subTest(markup=markup):
                self.page.write_text(markup, encoding="utf-8")
                with self.assertRaisesRegex(AssertionError, "missing image text"):
                    self.run_check("test_images_have_alt")

    def test_forbidden_scan_accepts_public_email_retina_assets_and_ordinary_words(self):
        self.page.write_text('JACKJBURLESON@PROTON.ME image@2x.png image@3x.SVG amfam', encoding="utf-8")
        self.write("site_libs/vendor.svg", "author@example.net")
        self.run_check("test_no_forbidden_strings")

    def test_forbidden_scan_rejects_raw_encoded_and_tag_split_sensitive_text(self):
        for text in ('author@example.net', 'author&#64;example.net', 'author%40example.net',
                     'author@<b>example</b>.net', '12345678-1234-ABCD-9876-1234567890AB',
                     'CONNECT.POSIT.CLOUD', 'braintrust%2Edev/app', 'AM<b>FAM</b>'):
            with self.subTest(text=text):
                self.page.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(AssertionError, "forbidden strings in rendered site"):
                    self.run_check("test_no_forbidden_strings")

    def test_forbidden_scan_checks_non_html_assets(self):
        for name in ("assets/chart.svg", "sitemap.xml", "assets/notes.txt"):
            with self.subTest(name=name):
                asset = self.write(name, "author@example.net")
                try:
                    with self.assertRaisesRegex(AssertionError, "email address"):
                        self.run_check("test_no_forbidden_strings")
                finally:
                    asset.unlink()

    def test_report_wiring_accepts_optional_reports_and_bidirectional_navigation(self):
        self.write("projects/example.html", '<div class="project-nav"><a href="example/report.html">Report</a></div>')
        self.write("projects/example/report.html", '<a href="../example.html">Case study</a>')
        self.run_check("test_each_project_has_report")

    def test_report_wiring_rejects_orphan_report_and_missing_links_or_navigation(self):
        study = self.docs / "projects/example.html"
        report = self.write("projects/example/report.html", '<a href="../example.html">Case study</a>')
        with self.assertRaisesRegex(AssertionError, "missing case study"):
            self.run_check("test_each_project_has_report")
        self.write("projects/example.html", '<div class="project-nav">No report link</div>')
        with self.assertRaisesRegex(AssertionError, "does not link to example/report.html"):
            self.run_check("test_each_project_has_report")
        study.write_text('<div class="project-nav"><a href="example/report.html">Report</a></div>', encoding="utf-8")
        report.write_text("No return link", encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "does not link back"):
            self.run_check("test_each_project_has_report")
        report.write_text('<a href="../example.html">Case study</a>', encoding="utf-8")
        study.write_text('<a href="example/report.html">Report</a>', encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "has no project-nav"):
            self.run_check("test_each_project_has_report")

    def test_authoring_check_reports_each_kind_of_leftover(self):
        for text in ('<!-- src: notes.md -->', '/home/author/file', '/root/file',
                     '<strong>None</strong>', 'TODO: publish results'):
            with self.subTest(text=text):
                self.page.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(AssertionError, "authoring leftovers"):
                    self.run_check("test_no_authoring_leftovers")

    def test_authoring_check_ignores_vendor_pages_and_accepts_clean_content(self):
        self.write("site_libs/vendor.html", "TODO")
        self.run_check("test_no_authoring_leftovers")
