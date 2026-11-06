#!/usr/bin/env python3
"""Regenerate assets/Jack_Burleson_Resume.pdf from the rendered resume page.

Run after `quarto render resume.qmd`; the print stylesheet supplies the two-page
letter layout and hides the site chrome.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "resume.html"
OUT = ROOT / "assets" / "Jack_Burleson_Resume.pdf"
with sync_playwright() as p:
    # Let Playwright resolve the browser it installed; a glob over the cache can
    # pick a revision this package does not support.
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(PAGE.as_uri(), wait_until="load")
    page.evaluate("document.fonts.ready")
    page.pdf(path=str(OUT), prefer_css_page_size=True, print_background=True)
    browser.close()
print(f"wrote {OUT.relative_to(ROOT)}")
