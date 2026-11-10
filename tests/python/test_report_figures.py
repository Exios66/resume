"""Figure coverage for the local technical reports.

Every report that owns a `figures/` directory must show at least one figure, and
every report image must have alt text, a visible caption and bytes identical to
the source asset. Reports without a figures directory are exempt: NATD withholds
its data and MORNINGSTAR has no verified chart to plot.
"""

import unittest
from urllib.parse import unquote, urlsplit

import test_links as checks
from test_portfolio_additions import ContentParser

REPORTS = sorted((checks.ROOT / "projects").glob("*/report.html"))


def parser(page):
    return ContentParser(page)


class ReportFigureTests(unittest.TestCase):
    def test_report_with_figures_directory_shows_at_least_one(self):
        missing = []
        for report in REPORTS:
            slug = report.parent.name
            source = checks.ROOT / "projects" / slug / "figures"
            images = [a for tag, a, _ in parser(report).elements if tag == "img"]
            if source.is_dir() and not images:
                missing.append(slug)
        self.assertEqual(missing, [], f"Reports with unused figure assets: {missing}")

    def test_every_report_image_has_alt_a_caption_and_matching_bytes(self):
        for report in REPORTS:
            with self.subTest(report=checks.rel(report)):
                elements = parser(report).elements
                for tag, image, ancestors in elements:
                    if tag != "img":
                        continue
                    self.assertTrue(checks.attr(image, "alt"), "missing alt")
                    figures = [a for tag, a, _ in ancestors if tag == "figure"]
                    self.assertEqual(len(figures), 1, "image outside a figure")
                    captions = [a for tag, a in parser(report).children(figures[0])
                                if tag == "figcaption"]
                    self.assertEqual(len(captions), 1, "figure without caption")
                    self.assertTrue(parser(report).text(captions[0]))
                    src = checks.attr(image, "src")
                    published = (report.parent / unquote(urlsplit(src).path)).resolve()
                    source = (checks.ROOT / "projects" / report.parent.name / unquote(src)).resolve()
                    self.assertEqual(published.read_bytes(), source.read_bytes(), src)


if __name__ == "__main__":
    unittest.main()
