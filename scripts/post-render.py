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


def main():
    """Prepare docs for GitHub Pages, remove the search index, and publish the PDF."""
    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").touch()
    (DOCS / "search.json").unlink(missing_ok=True)
    dedupe_titles()
    harden_diagram_pages()
    cache_bust_pages()
    publish_pdf()


if __name__ == "__main__":
    main()
