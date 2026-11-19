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
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from page_budgets import PAGE_TYPES, SHARED, page_type  # noqa: E402

DOCS = ROOT / "docs"
REPO_STYLE = re.compile(r"^[A-Za-z0-9]+(-[A-Za-z0-9]+)+$")  # for example Mailroom-Corpus-EDA
CHART_FIGURE = re.compile(
    r'<figure\b[^>]*class="[^"]*\bchart\b[^"]*"[^>]*>(.*?)</figure>', re.S
)
CHART_TITLE = re.compile(
    r'<figcaption[^>]*class="[^"]*\bchart-title\b[^"]*"[^>]*>(.*?)</figcaption>', re.S
)
IMG_TAG = re.compile(r"<img\b[^>]*>")
# Require a real `alt` attribute; `\balt` also matches inside `data-alt`.
ALT_ATTR = re.compile(r'(?<![\w-])alt="([^"]*)"')
FIGCAPTION = re.compile(r"<figcaption\b[^>]*>(.*?)</figcaption>", re.S)
FIGURE = re.compile(r"<figure\b[^>]*>(.*?)</figure>", re.S)


def text(rel):
    return (DOCS / rel).read_text(encoding="utf-8")


def gz_bytes(data):
    return len(gzip.compress(data, 9))


def gz(rel):
    return gz_bytes((DOCS / rel).read_bytes())


def strip_tags(html):
    return re.sub(r"<[^>]+>", "", html).strip()


def charts_without_title(html):
    missing = 0
    for match in CHART_FIGURE.finditer(html):
        title = CHART_TITLE.search(match.group(0))
        if not title or not strip_tags(title.group(1)):
            missing += 1
    return missing


def figures_without_alt(html):
    """Count images with empty alt, or alt that only repeats the surrounding figcaption."""
    missing = 0
    for figure in FIGURE.finditer(html):
        block = figure.group(0)
        captions = [strip_tags(c) for c in FIGCAPTION.findall(block)]
        captions = [c for c in captions if c]
        for tag in IMG_TAG.findall(block):
            alt_match = ALT_ATTR.search(tag)
            alt = alt_match.group(1).strip() if alt_match else ""
            if not alt or any(alt == caption for caption in captions):
                missing += 1
    stripped = FIGURE.sub("", html)
    for tag in IMG_TAG.findall(stripped):
        alt_match = ALT_ATTR.search(tag)
        alt = alt_match.group(1).strip() if alt_match else ""
        if not alt:
            missing += 1
    return missing


def main():
    slugs = sorted(p.stem for p in (ROOT / "projects").glob("*.qmd") if p.stem != "index")
    index = text("projects/index.html")
    m = {}

    cards = re.findall(r'<div[^>]*class="[^"]*\bcard\b[^"]*"[^>]*>', index)
    m["cards_without_cover"] = len(slugs) - index.count('<div class="card-cover"')
    titles = re.findall(r"<h3[^>]*>\s*<a [^>]*>(.*?)</a>", index, re.S)
    m["repo_style_titles"] = sum(
        bool(REPO_STYLE.match(re.sub(r"<[^>]+>", "", t).strip())) for t in titles
    )

    pages = [f"projects/{s}.html" for s in slugs]
    og = [re.search(r'property="og:image" content="([^"]*)"', text(p)) for p in pages]
    m["projects_without_own_social_card"] = sum(
        1 for s, o in zip(slugs, og) if not o or s not in o.group(1)
    )
    m["projects_without_structured_data"] = sum(
        "application/ld+json" not in text(p) for p in pages
    )

    unsized = eager = chart_gaps = alt_gaps = 0
    heaviest = {kind: ("", 0) for kind in PAGE_TYPES}
    over = 0
    for page in DOCS.rglob("*.html"):
        if "site_libs" in page.parts:
            continue
        rel = page.relative_to(DOCS).as_posix()
        raw = page.read_bytes()
        html = raw.decode("utf-8")
        body = html.split("<main", 1)[-1]
        for i, tag in enumerate(IMG_TAG.findall(body)):
            unsized += not ("width=" in tag and "height=" in tag)
            eager += i > 0 and 'loading="lazy"' not in tag
        chart_gaps += charts_without_title(body)
        alt_gaps += figures_without_alt(body)

        kind = page_type(rel)
        size = gz_bytes(raw)
        if size > heaviest[kind][1]:
            heaviest[kind] = (rel, size)
        if size > PAGE_TYPES[kind][1]:
            over += 1

    m["images_without_size"] = unsized
    m["later_images_not_lazy"] = eager
    m["charts_without_title"] = chart_gaps
    m["figures_without_alt"] = alt_gaps
    m["pages_over_budget"] = over

    for kind, (rel, size) in heaviest.items():
        key = "gz_" + kind.replace(" ", "_")
        m[key] = size
        if rel:
            print(
                f"INFO heaviest_{key}={rel}:{size}/{PAGE_TYPES[kind][1]}",
                file=sys.stderr,
            )

    m["gz_styles_css"] = gz("styles.css")
    m["gz_site_js"] = gz("assets/js/site.js")
    for rel, (_measured, limit) in SHARED.items():
        size = m["gz_styles_css"] if rel.endswith(".css") else m["gz_site_js"]
        if size > limit:
            print(f"INFO shared_over_budget={rel}:{size}/{limit}", file=sys.stderr)

    gaps = (
        "cards_without_cover",
        "repo_style_titles",
        "projects_without_own_social_card",
        "projects_without_structured_data",
        "images_without_size",
        "later_images_not_lazy",
        "pages_over_budget",
        "charts_without_title",
        "figures_without_alt",
    )
    print(f"METRIC experience_gaps={sum(m[k] for k in gaps)}")
    for k, v in m.items():
        print(f"METRIC {k}={v}")
    print(
        f"INFO project_cards_seen={len(cards)} projects={len(slugs)}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
