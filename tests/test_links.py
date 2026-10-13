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
        attributes = first_attributes(attrs)
        self.elements.append((tag, attributes, tuple(self.open_elements)))
        if tag not in VOID_TAGS:
            self.open_elements.append((tag, attributes))

    def handle_startendtag(self, tag, attrs):
        self.elements.append((tag, first_attributes(attrs), tuple(self.open_elements)))

    def handle_endtag(self, tag):
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
