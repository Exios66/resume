#!/usr/bin/env python3
"""Regenerate assets/og-image.png (1200x630 social preview) from scripts/og-image.html."""
import glob
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")
hits = sorted(glob.glob(f"{base}/chromium-*/chrome-linux*/chrome"))

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=hits[-1]) if hits else p.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 630})
    page.goto((ROOT / "scripts" / "og-image.html").as_uri(), wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.screenshot(path=str(ROOT / "assets" / "og-image.png"))
    browser.close()
print("wrote assets/og-image.png")
