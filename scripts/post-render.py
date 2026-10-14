#!/usr/bin/env python3
"""Quarto post-render hook.

1. Recreates docs/.nojekyll (Quarto clears the output directory on each render)
   and removes the unused search.json.
2. Prints docs/resume.html to PDF with its @media print rules, so the downloadable
   résumé always matches the page. Needs `pip install playwright` and a Chromium
   build; if either is missing the step is skipped with a warning and the
   committed PDF is left untouched.
"""
import glob
import os
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


def main():
    """Prepare docs for GitHub Pages, remove the search index, and build the PDF."""
    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").touch()
    (DOCS / "search.json").unlink(missing_ok=True)
    build_pdf()


if __name__ == "__main__":
    main()
