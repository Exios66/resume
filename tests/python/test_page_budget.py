"""Page transfer budgets: every built page stays within the budget for its type.

Budgets are gzipped HTML bytes, measured on 10 November 2026 with the same
compression level as scripts/hillclimb/kpi.py. The shared stylesheet and script
have their own budgets because every page pays for them. Each budget leaves
roughly 15 percent headroom over the heaviest page of its type, so ordinary
editing does not fail the check but a new figure or a large script does.

Recorded baselines are in .10x/metrics.md under "Page transfer budgets".
"""

import gzip
import pathlib

DOCS = pathlib.Path(__file__).resolve().parents[2] / "docs"

# (measured baseline, budget) in gzip bytes.
PAGE_TYPES = {
    "home": (14127, 16000),
    "projects index": (23702, 26000),
    # Raised on 12 November 2026: #142 grew the heaviest case study to 18,988, and its
    # phone chart drawings add 1,407 bytes less 948 from pruning unused sprite icons.
    "case study": (19433, 20000),
    "technical report": (19345, 22000),
    "appendix": (11018, 13000),
    "other page": (12099, 15000),
}
SHARED = {
    "styles.css": (14935, 20000),
    "assets/js/site.js": (5683, 9000),
}


def gz(path):
    """Return the gzipped byte length of a built file."""
    return len(gzip.compress(path.read_bytes(), 9))


def page_type(rel):
    """Return the budget key for a path relative to docs/."""
    if rel == "index.html":
        return "home"
    if rel == "projects/index.html":
        return "projects index"
    if rel.startswith("projects/"):
        if rel.endswith("/report.html"):
            return "technical report"
        if rel.endswith("/appendix.html"):
            return "appendix"
        if rel.count("/") == 1:
            return "case study"
    return "other page"


def pages():
    """Yield each built page as a docs-relative path, skipping Quarto's libraries."""
    for path in sorted(DOCS.rglob("*.html")):
        rel = path.relative_to(DOCS).as_posix()
        if "site_libs" not in path.parts:
            yield rel


def test_every_page_stays_within_its_transfer_budget():
    assert list(pages()), "docs/ has not been rendered"
    checked = set()
    for rel in pages():
        kind = page_type(rel)
        baseline, budget = PAGE_TYPES[kind]
        size = gz(DOCS / rel)
        checked.add(kind)
        assert size <= budget, f"{kind} over budget: {rel} is {size} bytes, limit {budget} (baseline {baseline})"
    assert checked == set(PAGE_TYPES), f"page types without a built page: {set(PAGE_TYPES) - checked}"


def test_shared_stylesheet_and_script_stay_within_budget():
    for rel, (baseline, budget) in SHARED.items():
        size = gz(DOCS / rel)
        assert size <= budget, f"{rel} is {size} bytes, limit {budget} (baseline {baseline})"
