"""Checks the rendered site in docs/ for broken links, alt text, forbidden strings, and project report wiring.

Run from the repository root: python3 -m pytest -q tests/test_links.py
"""

import html
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import unittest

import pytest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

if not DOCS.is_dir():
    pytest.skip("docs/ has not been rendered", allow_module_level=True)

VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                       "link", "meta", "param", "source", "track", "wbr"})
# Attributes that hold URLs, per tag. srcset is a comma-separated list; only the URL of each candidate is checked.
LINK_ATTRS = {
    "a": ("href",), "link": ("href",), "script": ("src",), "img": ("src", "srcset"),
    "source": ("src", "srcset"), "iframe": ("src",), "video": ("src", "poster"), "audio": ("src",),
    "use": ("href", "xlink:href"), "image": ("href", "xlink:href"),
}
PAGE_SUFFIXES = (".html", ".htm")
TEXT_SUFFIXES = (".html", ".htm", ".svg", ".xml", ".txt")
TAG_PATTERN = re.compile(r"<[^>]+>")
ALLOWED_EMAIL = "jackjburleson@proton.me"
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Retina asset names such as image@2x.png match EMAIL_PATTERN; a file extension is not a mail domain.
FILE_EXTENSIONS = frozenset({"css", "gif", "html", "jpeg", "jpg", "js", "json", "pdf", "png", "svg", "webp"})
UUID_PATTERN = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
                          re.IGNORECASE)
FORBIDDEN_TEXT = ("connect.posit.cloud", "braintrust.dev/app")
FORBIDDEN_UPPERCASE = ("AMFAM",)


class PageParser(HTMLParser):
    """Records every start tag with its attributes and the open elements that enclose it."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.open_elements = []
        # Each entry is (tag, attributes, ancestors), where ancestors is a tuple of (tag, attributes).
        self.elements = []

    def handle_starttag(self, tag, attrs):
        """Record the tag and its ancestors, then track non-void tags as open elements."""
        attributes = first_attributes(attrs)
        self.elements.append((tag, attributes, tuple(self.open_elements)))
        if tag not in VOID_TAGS:
            self.open_elements.append((tag, attributes))

    def handle_startendtag(self, tag, attrs):
        self.elements.append((tag, first_attributes(attrs), tuple(self.open_elements)))

    def handle_endtag(self, tag):
        """Close the matching open element and its descendants, ignoring unmatched end tags."""
        for depth in range(len(self.open_elements) - 1, -1, -1):
            if self.open_elements[depth][0] == tag:
                del self.open_elements[depth:]
                return


def first_attributes(attrs):
    """Return attributes as a dict in which the first occurrence of a duplicate name wins."""
    attributes = {}
    for name, value in attrs:
        attributes.setdefault(name, value)
    return attributes


def parse(path):
    """Return the start tags of one rendered page, in document order."""
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.elements


def attr(attributes, name):
    """Return an attribute value with surrounding whitespace removed; absent or valueless gives ''."""
    return (attributes.get(name) or "").strip()


def classes(attributes):
    """Return the set of class tokens on an element."""
    return set(attr(attributes, "class").split())


def rel(path):
    """Return a path relative to docs/ for failure messages."""
    return path.relative_to(DOCS).as_posix()


def site_files(suffixes=PAGE_SUFFIXES, include_libs=True):
    """Yield the files under docs/ whose suffix (any case) is listed, optionally skipping docs/site_libs/."""
    for path in sorted(DOCS.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if not include_libs and path.relative_to(DOCS).parts[0] == "site_libs":
            continue
        yield path


def is_external(value):
    """Return True for absolute URLs and scheme-based links such as mailto:, tel:, data: and javascript:."""
    parts = urlsplit(value)
    return bool(parts.scheme or parts.netloc)


def link_values(tag, attributes):
    """Yield each URL-bearing attribute value on one element; srcset yields the URL of each candidate."""
    for name in LINK_ATTRS.get(tag, ()):
        if name not in attributes:
            continue
        if name == "srcset":
            for candidate in attr(attributes, name).split(","):
                if candidate.split():
                    yield candidate.split()[0]
        else:
            yield attr(attributes, name)


def link_problem(page, value):
    """Return why an internal link is broken, or None when it resolves to a file inside docs/."""
    if value.startswith("/"):
        return "root-relative link; the site is served under /resume/"
    path = unquote(urlsplit(value).path)
    candidate = page.parent / path if path else page
    target = candidate.resolve()
    try:
        target.relative_to(DOCS.resolve())
    except ValueError:
        return "resolves outside docs/"
    if target.is_dir():
        return None if (target / "index.html").is_file() else "directory without index.html"
    return None if target.is_file() else "missing target"


def linked_targets(page):
    """Return the resolved paths of every internal a href on a page."""
    targets = set()
    for tag, attributes, _ in parse(page):
        if tag != "a" or "href" not in attributes:
            continue
        value = attr(attributes, "href")
        if value.startswith("#") or is_external(value) or value.startswith("/"):
            continue
        path = unquote(urlsplit(value).path)
        targets.add((page.parent / path if path else page).resolve())
    return targets


def scan_variants(source):
    """Return the text forms a forbidden string could hide in: raw, decoded, and each with tags removed."""
    decoded = html.unescape(unquote(source))
    return {
        "raw": source,
        "decoded": decoded,
        "tags stripped": TAG_PATTERN.sub("", source),
        "decoded, tags stripped": TAG_PATTERN.sub("", decoded),
    }


class RenderedSiteTests(unittest.TestCase):
    """Checks the HTML that GitHub Pages serves from docs/."""

    def test_internal_links_resolve(self):
        """Every internal URL attribute (href, src, srcset, xlink:href, poster) points at a real file."""
        failures = []
        for page in site_files():
            for tag, attributes, _ in parse(page):
                for value in link_values(tag, attributes):
                    if value.startswith("#") or is_external(value):
                        continue
                    problem = link_problem(page, value)
                    if problem:
                        failures.append(f"{rel(page)} -> {value} ({problem})")
        self.assertFalse(failures, "broken internal links:\n" + "\n".join(failures))

    def test_images_have_alt(self):
        """Every img has alt text unless decorative; diagram SVGs have a label whose referenced ids exist."""
        failures = []
        for page in site_files():
            elements = parse(page)
            ids = {attr(attributes, "id") for _, attributes, _ in elements}
            for tag, attributes, ancestors in elements:
                if tag == "img":
                    decorative = (attr(attributes, "role") in ("presentation", "none")
                                  or attr(attributes, "aria-hidden").lower() == "true")
                    if not decorative and not attr(attributes, "alt"):
                        failures.append(f"{rel(page)} -> <img src={attr(attributes, 'src')!r}> has no alt text")
                elif tag == "svg":
                    for _, figure in (ancestor for ancestor in ancestors
                                      if ancestor[0] == "figure" and "diagram" in classes(ancestor[1])):
                        referenced = attr(figure, "aria-labelledby").split()
                        if attr(figure, "role") != "img" or not (attr(figure, "aria-label") or referenced):
                            failures.append(f"{rel(page)} -> <svg> inside figure.diagram needs "
                                            "role=\"img\" and aria-label or aria-labelledby")
                        for ref in referenced:
                            if ref not in ids:
                                failures.append(f"{rel(page)} -> figure.diagram aria-labelledby names "
                                                f"missing id {ref!r}")
        self.assertFalse(failures, "missing image text:\n" + "\n".join(failures))

    def test_no_forbidden_strings(self):
        """Rendered pages contain no private email addresses, UUIDs, service URLs or internal names."""
        patterns = [(text, re.compile(re.escape(text), re.IGNORECASE)) for text in FORBIDDEN_TEXT]
        patterns += [(text, re.compile(re.escape(text))) for text in FORBIDDEN_UPPERCASE]
        failures = []
        for page in site_files(suffixes=TEXT_SUFFIXES, include_libs=False):
            source = page.read_text(encoding="utf-8")
            for form, text in scan_variants(source).items():
                found = []
                for match in EMAIL_PATTERN.finditer(text):
                    address = match.group(0).lower()
                    if address != ALLOWED_EMAIL and address.rsplit(".", 1)[-1] not in FILE_EXTENSIONS:
                        found.append((match, "email address"))
                for match in UUID_PATTERN.finditer(text):
                    found.append((match, "UUID"))
                for label, pattern in patterns:
                    for match in pattern.finditer(text):
                        found.append((match, f"forbidden text {label!r}"))
                for match, kind in found:
                    line = text.count("\n", 0, match.start()) + 1
                    failures.append(f"{rel(page)}:{line} ({form}) -> {kind} {match.group(0)!r}")
        self.assertFalse(failures, "forbidden strings in rendered site:\n" + "\n".join(dict.fromkeys(failures)))

    def test_each_project_has_report(self):
        """Each report has a case study that links to it and is linked back, and case studies have a project nav."""
        projects = DOCS / "projects"
        failures = []
        for report in sorted(projects.glob("*/report.html")):
            slug = report.parent.name
            study = projects / f"{slug}.html"
            if not study.is_file():
                failures.append(f"{rel(report)} -> missing case study {rel(study)}")
                continue
            if report.resolve() not in linked_targets(study):
                failures.append(f"{rel(study)} does not link to {slug}/report.html")
            if study.resolve() not in linked_targets(report):
                failures.append(f"{rel(report)} does not link back to ../{slug}.html")
        for study in sorted(projects.glob("*.html")):
            if study.name == "index.html" or not (projects / study.stem / "report.html").is_file():
                continue
            if not any("project-nav" in classes(attributes) for _, attributes, _ in parse(study)):
                failures.append(f"{rel(study)} has no project-nav")
        self.assertFalse(failures, "project report wiring:\n" + "\n".join(failures))

    def test_no_authoring_leftovers(self):
        """Source-citation comments, local paths and Quarto's empty callout titles stay out of published pages."""
        leftovers = ("<!-- src", "/home/", "/root/", "<strong>None</strong>", "TODO")
        failures = []
        for page in site_files(include_libs=False):
            source = page.read_text(encoding="utf-8")
            for text in leftovers:
                if text in source:
                    line = source.count("\n", 0, source.index(text)) + 1
                    failures.append(f"{rel(page)}:{line} -> {text!r}")
        self.assertFalse(failures, "authoring leftovers in rendered site:\n" + "\n".join(failures))


class PortfolioRegressionTests(unittest.TestCase):
    """Contracts for the case studies, reports, and diagrams introduced by PR #7."""

    REPORT_SLUGS = ("mailroom-ml", "mailroom-reloaded", "rvl-cdip-classifier", "wave-laboratory",
                    "degen-llms", "llm-personas", "psychometric-digital-twin", "mailroom-corpus-eda", "natd")
    FIGURE_SLUGS = ("mailroom-ml", "mailroom-reloaded", "rvl-cdip-classifier", "wave-laboratory",
                    "degen-llms", "psychometric-digital-twin", "mailroom-corpus-eda")
    STUDY_SLUGS = ("digital-mailroom", "aeroglobe", "langtons-ant", "mapreduce-reloaded", *REPORT_SLUGS)

    def test_expected_case_studies_and_reports_are_published(self):
        """Verify every expected case study and report is published with one main landmark and heading."""
        # Explicit paths prevent glob-based checks from passing if a whole report
        # or project disappears from the generated site.
        pages = [f"projects/{slug}.html" for slug in self.STUDY_SLUGS]
        pages += [f"projects/{slug}/report.html" for slug in self.REPORT_SLUGS]
        for name in pages:
            with self.subTest(page=name):
                page = DOCS / name
                self.assertTrue(page.is_file(), f"Missing published page: {name}")
                elements = parse(page)
                self.assertEqual(sum(tag == "main" for tag, _, _ in elements), 1)
                self.assertEqual(sum(tag == "h1" for tag, _, _ in elements), 1)

    def test_project_navigation_links_both_pages_and_marks_only_the_current_page(self):
        for slug in self.STUDY_SLUGS:
            study = DOCS / "projects" / f"{slug}.html"
            report = DOCS / "projects" / slug / "report.html"
            pages = (study, report) if slug in self.REPORT_SLUGS else (study,)
            expected = {page.resolve() for page in pages}
            for page in pages:
                with self.subTest(page=rel(page)):
                    links = [attributes for tag, attributes, ancestors in parse(page)
                             if tag == "a" and any("project-nav" in classes(parent)
                                                   for _, parent in ancestors)]
                    current = [attributes for attributes in links
                               if attr(attributes, "aria-current") == "page"]
                    self.assertEqual(len(current), 1, f"{rel(page)} needs one current project tab")
                    current_path = unquote(urlsplit(attr(current[0], "href")).path)
                    self.assertEqual((page.parent / current_path).resolve(), page.resolve())
                    destinations = {(page.parent / unquote(urlsplit(attr(attributes, "href")).path)).resolve()
                                    for attributes in links if not is_external(attr(attributes, "href"))}
                    self.assertTrue(expected <= destinations, f"{rel(page)} is missing a project tab")

    def test_new_diagrams_have_captions_and_resolvable_svg_references(self):
        names = ["projects/index.html"] + [f"projects/{slug}.html" for slug in self.STUDY_SLUGS]
        for name in names:
            with self.subTest(page=name):
                elements = parse(DOCS / name)
                ids = [attr(attributes, "id") for _, attributes, _ in elements if attr(attributes, "id")]
                self.assertEqual(len(ids), len(set(ids)), "Duplicate ids can break SVG and caption references")
                diagrams = [attributes for tag, attributes, _ in elements
                            if tag == "figure" and "diagram" in classes(attributes)]
                self.assertTrue(diagrams, f"{name} lost its architecture diagram")
                for diagram in diagrams:
                    children = [(tag, attributes) for tag, attributes, ancestors in elements
                                if any(parent is diagram for _, parent in ancestors)]
                    captions = {attr(attributes, "id") for tag, attributes in children if tag == "figcaption"}
                    references = set(attr(diagram, "aria-labelledby").split())
                    self.assertTrue(references and references <= captions, "Diagram must name its caption")
                    svgs = [attributes for tag, attributes in children if tag == "svg"]
                    self.assertEqual(len(svgs), 1)
                    self.assertEqual(attr(svgs[0], "aria-hidden"), "true")
                    self.assertEqual(attr(svgs[0], "focusable"), "false")
                    local_ids = {attr(attributes, "id") for _, attributes in children}
                    for _, attributes in children:
                        for value in attributes.values():
                            for reference in re.findall(r"url\(#([^)]+)\)", value or ""):
                                self.assertIn(reference, local_ids, "SVG marker references must resolve in the diagram")

    def test_new_projects_are_discoverable_from_home_about_and_project_cards(self):
        featured = {"digital-mailroom", "mailroom-ml", "rvl-cdip-classifier", "wave-laboratory"}
        for name, slugs in (("index.html", featured), ("projects/index.html", set(self.STUDY_SLUGS))):
            with self.subTest(page=name):
                page = DOCS / name
                destinations = {(page.parent / unquote(urlsplit(attr(attributes, "href")).path)).resolve()
                                for tag, attributes, ancestors in parse(page)
                                if tag == "a" and not is_external(attr(attributes, "href"))
                                and any("card" in classes(parent) for _, parent in ancestors)}
                expected = {(DOCS / "projects" / f"{slug}.html").resolve() for slug in slugs}
                self.assertTrue(expected <= destinations, f"{name} is missing project cards")
        self.assertIn((DOCS / "projects/wave-laboratory.html").resolve(), linked_targets(DOCS / "about.html"))

    def test_report_figures_are_published_without_corruption(self):
        for slug in self.FIGURE_SLUGS:
            with self.subTest(project=slug):
                sources = sorted((ROOT / "projects" / slug / "figures").glob("*"))
                figures = [source for source in sources if source.suffix.lower() in (".svg", ".jpg")]
                self.assertTrue(figures, f"{slug} lost its report figures")
                for source in figures:
                    target = DOCS / source.relative_to(ROOT)
                    self.assertTrue(target.is_file(), f"Missing published figure: {rel(target)}")
                    self.assertEqual(target.read_bytes(), source.read_bytes(), f"Figure changed during publishing: {source.name}")
