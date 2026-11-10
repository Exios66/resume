#!/usr/bin/env python3
"""Experience KPIs for the portfolio, measured on the built site in docs/.

Run after a render: python3 scripts/hillclimb/kpi.py
Prints METRIC lines in the same form as autoresearch.sh. The primary metric is experience_gaps
(lower is better, target 0): the number of countable gaps between the built site and the
portfolio experience v2 roadmap. Targets and rules are in .10x/metrics.md.
It reads files only. It starts no browser and changes nothing.
"""
import gzip
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
BUDGET = {"index.html": 16000, "projects/index.html": 26000}  # gzip bytes of the HTML
REPO_STYLE = re.compile(r"^[A-Za-z0-9]+(-[A-Za-z0-9]+)+$")     # for example Mailroom-Corpus-EDA


def text(rel):
    return (DOCS / rel).read_text(encoding="utf-8")


def gz(rel):
    return len(gzip.compress((DOCS / rel).read_bytes(), 9))


def main():
    slugs = sorted(p.stem for p in (ROOT / "projects").glob("*.qmd") if p.stem != "index")
    index = text("projects/index.html")
    m = {}

    cards = re.findall(r'<div[^>]*class="[^"]*\bcard\b[^"]*"[^>]*>', index)
    m["cards_without_cover"] = len(slugs) - index.count('<div class="card-cover"')
    titles = re.findall(r"<h3[^>]*>\s*<a [^>]*>(.*?)</a>", index, re.S)
    m["repo_style_titles"] = sum(bool(REPO_STYLE.match(re.sub(r"<[^>]+>", "", t).strip())) for t in titles)

    pages = [f"projects/{s}.html" for s in slugs]
    og = [re.search(r'property="og:image" content="([^"]*)"', text(p)) for p in pages]
    m["projects_without_own_social_card"] = sum(1 for s, o in zip(slugs, og) if not o or s not in o.group(1))
    m["projects_without_structured_data"] = sum("application/ld+json" not in text(p) for p in pages)

    unsized = eager = 0
    for page in DOCS.rglob("*.html"):
        body = page.read_text(encoding="utf-8").split("<main", 1)[-1]
        for i, tag in enumerate(re.findall(r"<img\b[^>]*>", body)):
            unsized += not ("width=" in tag and "height=" in tag)
            eager += i > 0 and 'loading="lazy"' not in tag
    m["images_without_size"] = unsized
    m["later_images_not_lazy"] = eager

    over = 0
    for rel, limit in BUDGET.items():
        size = gz(rel)
        m["gz_" + rel.replace("/", "_").replace(".html", "")] = size
        over += size > limit
    m["pages_over_budget"] = over
    m["gz_styles_css"] = gz("styles.css")
    m["gz_site_js"] = gz("assets/js/site.js")

    gaps = ("cards_without_cover", "repo_style_titles", "projects_without_own_social_card",
            "projects_without_structured_data", "images_without_size", "later_images_not_lazy", "pages_over_budget")
    print(f"METRIC experience_gaps={sum(m[k] for k in gaps)}")
    for k, v in m.items():
        print(f"METRIC {k}={v}")
    print(f"INFO project_cards_seen={len(cards)} projects={len(slugs)}", file=sys.stderr)


if __name__ == "__main__":
    main()
