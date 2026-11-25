#!/usr/bin/env python3
"""Regenerate site and per-project Open Graph images (1200x630).

Default: assets/og-image.png from scripts/build/og-image.html.
Project mode: assets/og/<slug>.png from each project's title, kicker and cover motif.

  python3 scripts/build/make-og.py
  python3 scripts/build/make-og.py --project wave-laboratory
  python3 scripts/build/make-og.py --all-projects

Needs Chromium via Playwright. Exits non-zero if the browser is missing or a
capture fails; never writes a blank image after a failed shot.
"""
from __future__ import annotations

import argparse
import glob
import html
import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
SITE_OG = ROOT / "assets" / "og-image.png"
PROJECT_OG_DIR = ROOT / "assets" / "og"
COVERS = ROOT / "partials" / "covers"
PROJECTS = ROOT / "projects"
OG_HTML = ROOT / "scripts" / "build" / "og-image.html"

# Standalone dark-theme palette matching styles.css card covers on dark paper.
COVER_CSS = """
.card-cover {
  color: #8fdde6;
  background: #131c20;
  overflow: hidden;
}
.card-cover svg { display: block; width: 100%; height: 100%; fill: none; stroke: none; }
.card-cover :is(.cv-line, .cv-accent, .cv-page) {
  stroke: currentColor; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}
.card-cover .cv-line { stroke-opacity: .42; }
.card-cover .cv-faint { stroke-opacity: .24; }
.card-cover .cv-dash { stroke-dasharray: 4 4; }
.card-cover .cv-page { stroke-opacity: .5; fill: #131c20; }
.card-cover .cv-soft { fill: currentColor; fill-opacity: .1; }
.card-cover .cv-fill, .card-cover .cv-dot { fill: currentColor; }
.card-cover .cv-dotsoft { fill: currentColor; fill-opacity: .2; }
.card-cover .cv-accent.cv-dash { fill: none; }
.card-cover .cv-pop { color: #fe01b1; }
.card-cover .cv-shade { fill: currentColor; fill-opacity: .1; }
.card-cover .cv-glow { fill: currentColor; fill-opacity: .07; }
.card-cover .cv-under { fill: #131c20; }
.card-cover .cv-crate {
  stroke: currentColor; stroke-width: 1; stroke-opacity: .6; fill: #131c20;
  vector-effect: non-scaling-stroke;
}
.card-cover .cv-crate.cv-soft { fill: color-mix(in srgb, currentColor 22%, #131c20); fill-opacity: 1; }
.card-cover .cv-cut {
  stroke: #131c20; stroke-width: 1.2; stroke-linecap: round; fill: none;
  vector-effect: non-scaling-stroke;
}
.card-cover circle.cv-cut { fill: none; }
.card-cover .cv-grid {
  stroke: currentColor; stroke-width: 1; stroke-opacity: .09;
  vector-effect: non-scaling-stroke;
}
.card-cover .cv-tick {
  stroke: #131c20; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round;
}
"""


def chromium_executable() -> str | None:
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")
    hits = sorted(glob.glob(f"{base}/chromium-*/chrome-linux*/chrome"))
    return hits[-1] if hits else None


def launch_browser(playwright):
    exe = chromium_executable()
    try:
        return playwright.chromium.launch(executable_path=exe) if exe else playwright.chromium.launch()
    except Exception as err:  # noqa: BLE001 - surface a clear Chromium-missing message
        print(f"Chromium is required to render social cards: {err}", file=sys.stderr)
        raise SystemExit(1) from err


def project_slugs() -> list[str]:
    return sorted(p.stem for p in COVERS.glob("*.svg"))


def read_title_kicker(slug: str) -> tuple[str, str]:
    path = PROJECTS / f"{slug}.qmd"
    if not path.is_file():
        raise FileNotFoundError(f"missing case study for cover {slug}: {path}")
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+?)(?:\s+\{[^}]*\})?\s*$", text, re.M)
    kicker_match = re.search(r"\[([^\]]+)\]\{\.kicker\}", text)
    if not title_match:
        raise ValueError(f"no H1 title in {path}")
    title = title_match.group(1).strip()
    kicker = kicker_match.group(1).strip() if kicker_match else "Project"
    return title, kicker


def project_card_html(slug: str) -> str:
    title, kicker = read_title_kicker(slug)
    svg_path = COVERS / f"{slug}.svg"
    if not svg_path.is_file():
        raise FileNotFoundError(f"missing cover motif: {svg_path}")
    svg = svg_path.read_text(encoding="utf-8").strip()
    # Decorative motif: strip any accidental script; keep the authored SVG markup.
    if "<script" in svg.lower():
        raise ValueError(f"cover motif must not contain script: {svg_path}")
    safe_title = html.escape(title)
    safe_kicker = html.escape(kicker)
    return f"""<!doctype html>
<meta charset="utf-8">
<style>
  @font-face {{ font-family: "Inter"; font-weight: 600; src: url("{(ROOT / 'assets/fonts/inter-latin-600-normal.woff2').as_uri()}") format("woff2"); }}
  @font-face {{ font-family: "Newsreader"; font-weight: 200 800; font-style: normal; src: url("{(ROOT / 'assets/fonts/newsreader-latin-opsz-normal.woff2').as_uri()}") format("woff2"); }}
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ width: 1200px; height: 630px; background: #0d1316; font-family: "Inter", sans-serif; color: #e6edef; }}
  .card {{
    position: relative; width: 1200px; height: 630px; padding: 72px 96px 64px;
    border-top: 14px solid #fe01b1;
    background: radial-gradient(900px 500px at 88% 108%, #16303a 0%, #0d1316 70%);
  }}
  .role {{
    font-weight: 600; font-size: 22px; letter-spacing: .12em; text-transform: uppercase;
    color: #4fc1cd; max-width: 920px; line-height: 1.35;
  }}
  h1 {{
    margin-top: 22px; font: 600 72px/1.05 "Newsreader", Georgia, serif;
    font-optical-sizing: auto; letter-spacing: .02em; max-width: 920px;
  }}
  .motif {{
    position: absolute; right: 64px; bottom: 56px; width: 480px; height: 180px;
    border-radius: 16px; border: 1px solid #25333a; overflow: hidden;
  }}
  .motif .card-cover {{ width: 100%; height: 100%; }}
  .url {{
    position: absolute; left: 96px; bottom: 56px; font-weight: 600; font-size: 24px;
    letter-spacing: .06em; color: #4fc1cd;
  }}
  {COVER_CSS}
</style>
<div class="card">
  <div class="role">{safe_kicker}</div>
  <h1>{safe_title}</h1>
  <div class="url">exios66.github.io/resume</div>
  <div class="motif" aria-hidden="true"><div class="card-cover">{svg}</div></div>
</div>
"""


def capture(page, destination: Path, *, goto: str | None = None, content: str | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Keep a .png suffix so Playwright accepts the path; rename only after a real capture.
    tmp = destination.with_name(destination.stem + ".partial.png")
    if tmp.exists():
        tmp.unlink()
    if goto is not None:
        page.goto(goto, wait_until="networkidle")
    else:
        assert content is not None
        page.set_content(content, wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.screenshot(path=str(tmp))
    if not tmp.is_file() or tmp.stat().st_size < 1000:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"refusing blank or tiny social card for {destination}")
    tmp.replace(destination)


def write_site_card(page) -> None:
    capture(page, SITE_OG, goto=OG_HTML.as_uri())
    print("wrote assets/og-image.png")


def write_project_card(page, slug: str) -> None:
    out = PROJECT_OG_DIR / f"{slug}.png"
    capture(page, out, content=project_card_html(slug))
    print(f"wrote assets/og/{slug}.png")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--project", metavar="SLUG", help="render one project social card")
    group.add_argument("--all-projects", action="store_true", help="render every project social card")
    args = parser.parse_args(argv)

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            page = browser.new_page(viewport={"width": 1200, "height": 630})
            if args.project:
                write_project_card(page, args.project)
            elif args.all_projects:
                for slug in project_slugs():
                    write_project_card(page, slug)
            else:
                write_site_card(page)
        finally:
            browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
