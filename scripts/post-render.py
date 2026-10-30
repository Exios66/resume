#!/usr/bin/env python3
"""Quarto post-render hook.

1. Recreates docs/.nojekyll (Quarto clears the output directory on each render)
   and removes the unused search.json.
2. Publishes the committed résumé PDF (assets/Jack_Burleson_Resume.pdf) to
   docs/assets unchanged. The PDF is the owner's own two-page layout, not a
   print of resume.html, so the render never rebuilds or rewrites it.
3. Drops the " – <site title>" suffix Quarto adds to <title> when the page
   title already names the site, so tabs do not repeat the name.
4. Gives every shape in an inline-SVG diagram plain `fill`/`stroke` presentation
   attributes, so a diagram still draws as outlines (not solid black boxes) if
   styles.css fails to load. The stylesheet's rules override these attributes.
5. Adds a ?v=<content hash> to the site stylesheet and script links, so a
   browser or the Pages CDN never pairs new HTML with a stale cached copy.
"""
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PDF_NAME = "Jack_Burleson_Resume.pdf"


def publish_pdf():
    """Copy the committed résumé PDF to docs/assets.

    Return True after copying. Return False with a warning, leaving docs/
    untouched, if the source PDF is missing. Errors while creating the output
    directory or copying the PDF propagate to the caller.
    """
    source = ROOT / "assets" / PDF_NAME
    if not source.is_file():
        print(f"post-render: {source} is missing; résumé PDF not published", file=sys.stderr)
        return False
    out = DOCS / "assets" / PDF_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, out)
    print(f"post-render: published {PDF_NAME}")
    return True


def site_title():
    """Return website.title from _quarto.yml, or None if it is not set."""
    try:
        config = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    match = re.search(r"""^website:\n(?:[ \t]+.*\n)*?[ \t]+title:\s*(["']?)(.+?)\1\s*$""", config, re.M)
    return match.group(2) if match else None


def dedupe_title(text, site):
    """Remove Quarto's site-title suffix from <title> when the page title already contains it."""
    escaped = re.escape(html.escape(site, quote=False))

    def fix(match):
        page = match.group(1)
        return f"<title>{page}</title>" if re.search(escaped, page) else match.group(0)

    return re.sub(r"<title>([^<]*?) – " + escaped + r"</title>", fix, text, count=1)


def dedupe_titles():
    """Apply dedupe_title to every rendered page."""
    site = site_title()
    if not site:
        return
    for page in DOCS.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        fixed = dedupe_title(text, site)
        if fixed != text:
            page.write_text(fixed, encoding="utf-8")


CACHE_BUSTED = ("styles.css", "assets/js/site.js")


def asset_versions():
    """Return {relative path: short sha256} for each CACHE_BUSTED file present in docs/."""
    versions = {}
    for rel in CACHE_BUSTED:
        path = DOCS / rel
        if path.is_file():
            versions[rel] = hashlib.sha256(path.read_bytes()).hexdigest()[:10]
    return versions


def cache_bust(text, versions):
    """Append ?v=<hash> to href/src links that point at a versioned asset (any ../ depth)."""
    for rel, version in versions.items():
        pattern = r'((?:href|src)="(?:\.\./)*' + re.escape(rel) + r')(?:\?v=[0-9a-f]+)?"'
        text = re.sub(pattern, lambda m: f'{m.group(1)}?v={version}"', text)
    return text


def cache_bust_pages():
    """Apply cache_bust to every rendered page."""
    versions = asset_versions()
    if not versions:
        return
    for page in DOCS.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        fixed = cache_bust(text, versions)
        if fixed != text:
            page.write_text(fixed, encoding="utf-8")


SVG_SHAPE = re.compile(r"<(rect|circle|ellipse|path|line|polygon|polyline)(\s[^<>]*?)?(/?)>")
DIAGRAM = re.compile(r'<figure class="diagram".*?</figure>', re.S)


def harden_shape(match):
    """Add fill/stroke defaults to one diagram shape that carries a d-* class.

    Shapes without a d-* class (such as the arrowhead inside <marker>) and
    attributes already present are left alone.
    """
    tag, attrs, close = match.group(1), match.group(2) or "", match.group(3)
    if not re.search(r'\sclass="[^"]*\bd-', attrs):
        return match.group(0)
    extra = ""
    if not re.search(r"\sfill=", attrs):
        extra += ' fill="none"'
    if not re.search(r"\sstroke=", attrs):
        extra += ' stroke="currentColor"'
    return f"<{tag}{attrs}{extra}{close}>" if extra else match.group(0)


def harden_diagrams(text):
    """Apply harden_shape to every shape inside each <figure class="diagram">."""
    return DIAGRAM.sub(lambda figure: SVG_SHAPE.sub(harden_shape, figure.group(0)), text)


def harden_diagram_pages():
    """Apply harden_diagrams to every rendered page."""
    for page in DOCS.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        fixed = harden_diagrams(text)
        if fixed != text:
            page.write_text(fixed, encoding="utf-8")


def visible_text(fragment):
    """Return element text with tags removed and whitespace collapsed."""
    text = re.sub(r"<[^>]+>", " ", fragment)
    return " ".join(html.unescape(text).split())


def build_search_index():
    """Write a small title-and-description index for the header search field."""
    pages = []
    for page in sorted(DOCS.rglob("*.html")):
        if "site_libs" in page.parts:
            continue
        source = page.read_text(encoding="utf-8")
        title = re.search(r"<title>([^<]*)</title>", source)
        description = re.search(r'<meta name="description" content="([^"]*)"', source)
        heading = re.search(r"<h1\b[^>]*>(.*?)</h1>", source, re.S)
        name = visible_text(heading.group(1)) if heading else (html.unescape(title.group(1)) if title else page.stem)
        pages.append({
            "title": name,
            "url": page.relative_to(DOCS).as_posix(),
            "text": html.unescape(description.group(1)) if description else "",
        })
    target = DOCS / "assets" / "search-index.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"post-render: indexed {len(pages)} pages")


def wrap_tables(text):
    """Give each top-level table a horizontal scroll container."""
    if 'class="table-scroll"' in text:
        return text
    return re.sub(r"<table\b.*?</table>", lambda match: f'<div class="table-scroll">{match.group(0)}</div>', text, flags=re.S)


def wrap_table_pages():
    """Apply wrap_tables to every rendered page."""
    for page in DOCS.rglob("*.html"):
        if "site_libs" in page.parts:
            continue
        text = page.read_text(encoding="utf-8")
        fixed = wrap_tables(text)
        if fixed != text:
            page.write_text(fixed, encoding="utf-8")


def main():
    """Prepare docs for GitHub Pages, build the search index, and publish the PDF."""
    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").touch()
    # Quarto's own search.json is unused; the header reads assets/search-index.json.
    (DOCS / "search.json").unlink(missing_ok=True)
    dedupe_titles()
    harden_diagram_pages()
    wrap_table_pages()
    build_search_index()
    cache_bust_pages()
    publish_pdf()


if __name__ == "__main__":
    main()
