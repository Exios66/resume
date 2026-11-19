"""Page transfer budgets: every built page stays within the budget for its type.

Budgets are gzipped HTML bytes, measured with the same compression level as
scripts/hillclimb/kpi.py. The shared stylesheet and script have their own
budgets because every page pays for them. Each budget leaves roughly 15 percent
headroom over the heaviest page of its type, so ordinary editing does not fail
the check but a new figure or a large script does.

Budgets and classification live in scripts/hillclimb/page_budgets.py so the
experience KPI and this gate cannot drift. Recorded baselines are in
.10x/metrics.md under "Page transfer budgets".
"""

import gzip
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "hillclimb"))
from page_budgets import PAGE_TYPES, SHARED, page_type  # noqa: E402

DOCS = ROOT / "docs"


def gz(path):
    """Return the gzipped byte length of a built file."""
    return len(gzip.compress(path.read_bytes(), 9))


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
        assert size <= budget, (
            f"{kind} over budget: {rel} is {size} bytes, limit {budget} "
            f"(baseline {baseline})"
        )
    assert checked == set(PAGE_TYPES), (
        f"page types without a built page: {set(PAGE_TYPES) - checked}"
    )


def test_shared_stylesheet_and_script_stay_within_budget():
    for rel, (baseline, budget) in SHARED.items():
        size = gz(DOCS / rel)
        assert size <= budget, (
            f"{rel} is {size} bytes, limit {budget} (baseline {baseline})"
        )


def test_kpi_and_gate_share_the_same_page_budgets():
    """kpi.py must classify pages with the same helper the gate uses."""
    assert page_type("index.html") == "home"
    assert page_type("projects/index.html") == "projects index"
    assert page_type("projects/mapreduce-reloaded.html") == "case study"
    assert page_type("projects/natd/report.html") == "technical report"
    assert page_type("projects/langtons-ant/appendix.html") == "appendix"
    assert page_type("resume.html") == "other page"
