#!/usr/bin/env python3
"""Quarto post-render hook.

1. Recreates docs/.nojekyll (Quarto clears the output directory on each render)
   and removes the unused search.json.
2. Prints docs/resume.html to PDF with its @media print rules, so the downloadable
   résumé always matches the page. Needs `pip install playwright` and a Chromium
   build; if either is missing the step is skipped with a warning and the
   committed PDF is left untouched.
3. Drops the " – <site title>" suffix Quarto adds to <title> when the page
   title already names the site, so tabs do not repeat the name.
4. Gives every shape in an inline-SVG diagram plain `fill`/`stroke` presentation
   attributes, so a diagram still draws as outlines (not solid black boxes) if
   styles.css fails to load. The stylesheet's rules override these attributes.
5. Adds a ?v=<content hash> to the site stylesheet and script links, so a
   browser or the Pages CDN never pairs new HTML with a stale cached copy.
"""
import glob
import hashlib
import html
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PDF_NAME = "Jack_Burleson_Resume.pdf"


def find_chromium():
    """Return a Chromium executable path, or None for Playwright's default.

    Prefer an existing CHROMIUM_PATH, then search PLAYWRIGHT_BROWSERS_PATH
    for Chromium builds, choosing the last sorted match of the first pattern
    that matches.
    """
    env = os.environ.get("CHROMIUM_PATH")
    if env and Path(env).exists():
        return env
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")
    for pattern in (f"{base}/chromium-*/chrome-linux*/chrome", f"{base}/chromium/chrome-linux*/chrome"):
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]
    return None  # let Playwright use its own managed browser


def build_pdf():
    """Print docs/resume.html to PDF and copy it to the source assets directory.

    Return True after writing and copying the PDF. Return False with a warning
    if Playwright is unavailable or browser/PDF generation fails. Errors while
    creating the output directory or copying the PDF propagate to the caller.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("post-render: playwright not installed; keeping existing PDF", file=sys.stderr)
        return False

    html = DOCS / "resume.html"
    out = DOCS / "assets" / PDF_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            exe = find_chromium()
            browser = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
            page = browser.new_page()
            page.goto(html.as_uri(), wait_until="networkidle")
            page.emulate_media(media="print")
            page.evaluate("document.fonts.ready")
            page.pdf(
                path=str(out),
                format="Letter",
                print_background=True,
                prefer_css_page_size=True,
                display_header_footer=False,
                tagged=True,
                outline=True,
            )
            browser.close()
    except Exception as exc:  # noqa: BLE001 - never fail the whole render over the PDF
        print(f"post-render: PDF build failed ({exc}); keeping existing PDF", file=sys.stderr)
        return False

    shutil.copyfile(out, ROOT / "assets" / PDF_NAME)
    print(f"post-render: wrote {PDF_NAME}")
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
    """Prepare docs for GitHub Pages, remove the search index, and build the PDF."""
    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").touch()
    (DOCS / "search.json").unlink(missing_ok=True)
    dedupe_titles()
    harden_diagram_pages()
    cache_bust_pages()
    build_pdf()


if __name__ == "__main__":
    main()
