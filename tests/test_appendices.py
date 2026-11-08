"""Wiring and content checks for the project appendices."""

import xml.etree.ElementTree as ET

import test_links as checks
from test_portfolio_additions import ContentParser, destination

SITE = "https://exios66.github.io/resume/"
ALL = ("aeroglobe", "degen-llms", "digital-mailroom", "langtons-ant", "llm-personas",
       "mailroom-corpus-eda", "mailroom-ml", "mailroom-reloaded", "natd",
       "psychometric-digital-twin", "rvl-cdip-classifier", "wave-laboratory")
CASES = {
    "mailroom-ml": ("0.9598", "0.7387", "0.3589", "0.1774", "541", "0.94"),
    "mailroom-corpus-eda": ("3,302", "1,100", "22,591", "2,530", "323"),
    "langtons-ant": ("6219b3fb", "9,977", "20"),
    "rvl-cdip-classifier": ("82.6%", "99.4%", "29"),
    "wave-laboratory": ("25 in 9 files", "18.5 m", "11.9 m"),
    "natd": ("nine-participant", "withheld", "#80"),
    "llm-personas": ("13", "12", "not internally consistent"),
}


def page(slug):
    path = checks.DOCS / "projects" / slug / "appendix.html"
    assert path.is_file(), f"Missing appendix: {path}"
    return path, ContentParser(path)


def test_every_appendix_links_case_study_and_report():
    all_projects = (checks.DOCS / "projects").resolve()
    for slug in ALL:
        path, parser = page(slug)
        study = all_projects / f"{slug}.html"
        # The standalone back link was removed on purpose (duplicate of the
        # Case-study pill in the project nav); the pill is the way back.
        links = {parser.text(a): destination(path, a) for tag, a, _ in parser.elements if tag == "a"}
        nav = next(a for tag, a, _ in parser.elements if "project-nav" in checks.classes(a))
        nav_links = {parser.text(a): destination(path, a) for tag, a in parser.children(nav) if tag == "a"}
        assert nav_links["Case study"] == study
        if (checks.DOCS / "projects" / slug / "report.html").is_file():
            assert links["Technical report"] == all_projects / slug / "report.html"
        current = [a for tag, a in parser.children(nav)
                   if tag == "a" and checks.attr(a, "aria-current") == "page"]
        assert len(current) == 1
        assert destination(path, current[0]) == path.resolve()


def test_case_study_and_report_link_the_appendix():
    for slug in ALL:
        appendix = (checks.DOCS / "projects" / slug / "appendix.html").resolve()
        pages = [f"projects/{slug}.html"]
        if (checks.DOCS / "projects" / slug / "report.html").is_file():
            pages.append(f"projects/{slug}/report.html")
        for name in pages:
            assert appendix in checks.linked_targets(checks.DOCS / name), name


def test_appendix_numbers_sitemap_and_no_images():
    for slug, claims in CASES.items():
        _, parser = page(slug)
        text = " ".join(t for t, _ in parser.text_fragments)
        for claim in claims:
            assert claim in text, (slug, claim)
    for slug in ALL:
        _, parser = page(slug)
        assert not any(tag == "img" for tag, _, _ in parser.elements), slug
    locations = [n.text for n in ET.parse(checks.DOCS / "sitemap.xml").findall("{*}url/{*}loc")]
    for slug in ALL:
        assert locations.count(f"{SITE}projects/{slug}/appendix.html") == 1
