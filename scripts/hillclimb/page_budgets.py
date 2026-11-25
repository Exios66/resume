"""Gzip transfer budgets for built portfolio pages.

Shared by scripts/hillclimb/kpi.py and tests/python/test_page_budget.py so the
experience KPI and the correctness gate cannot drift apart. Sizes are gzipped
bytes at compression level 9. Raising a budget is a deliberate pull-request
decision; record the reason and the new measurement in .10x/metrics.md.
"""

# (measured heaviest at the last metrics refresh, budget) in gzip bytes.
PAGE_TYPES = {
    "home": (14296, 16000),
    "projects index": (24305, 26000),
    "case study": (19711, 20000),
    "technical report": (19143, 22000),
    "appendix": (11006, 13000),
    "other page": (11714, 15000),
}
SHARED = {
    "styles.css": (18673, 20000),
    "assets/js/site.js": (7946, 9000),
}


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
