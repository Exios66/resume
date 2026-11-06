"""Wiring and content checks for the project appendices."""

import xml.etree.ElementTree as ET

import test_links as checks
from test_portfolio_additions import ContentParser, destination

SITE = "https://exios66.github.io/resume/"
CASES = {
    "mailroom-ml": ("0.9598", "0.7387", "0.3589", "0.1774", "541", "0.94"),
    "mailroom-corpus-eda": ("3,302", "1,100", "22,591", "2,530", "323"),
}


def page(name):
    path = checks.DOCS / "projects" / name / "appendix.html"
    assert path.is_file(), f"Missing appendix: {path}"
    return path, ContentParser(path)


def test_each_appendix_links_case_study_report_and_back():
    for slug in CASES:
        path, parser = page(slug)
        expected_study = (checks.DOCS / "projects" / f"{slug}.html").resolve()
        back = next(a for tag, a, _ in parser.elements if "back" in checks.classes(a))
        assert destination(path, back) == expected_study
        links = {parser.text(a): destination(path, a) for tag, a, _ in parser.elements
                 if tag == "a" and "back" not in checks.classes(a)}
        assert links["Case study"] == expected_study
        assert links["Technical report"] == (checks.DOCS / "projects" / slug / "report.html").resolve()
        nav = next(a for tag, a, _ in parser.elements if "project-nav" in checks.classes(a))
        current = [a for tag, a in parser.children(nav)
                   if tag == "a" and checks.attr(a, "aria-current") == "page"]
        assert len(current) == 1
        assert destination(path, current[0]) == path.resolve()


def test_case_study_and_report_link_the_appendix():
    for slug in CASES:
        appendix = (checks.DOCS / "projects" / slug / "appendix.html").resolve()
        for name in (f"projects/{slug}.html", f"projects/{slug}/report.html"):
            assert appendix in checks.linked_targets(checks.DOCS / name), name


def test_appendix_numbers_and_sitemap_entries():
    for slug, claims in CASES.items():
        _, parser = page(slug)
        text = " ".join(t for t, _ in parser.text_fragments)
        for claim in claims:
            assert claim in text, (slug, claim)
        assert not any(tag == "img" for tag, _, _ in parser.elements)
    locations = [n.text for n in ET.parse(checks.DOCS / "sitemap.xml").findall("{*}url/{*}loc")]
    for slug in CASES:
        assert locations.count(f"{SITE}projects/{slug}/appendix.html") == 1
