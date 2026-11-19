"""The experience KPI script runs on the built site and reports its primary metric."""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "hillclimb"))
import kpi as kpi_mod  # noqa: E402

REQUIRED = (
    "experience_gaps",
    "cards_without_cover",
    "repo_style_titles",
    "projects_without_own_social_card",
    "projects_without_structured_data",
    "images_without_size",
    "later_images_not_lazy",
    "pages_over_budget",
    "charts_without_title",
    "figures_without_alt",
    "gz_home",
    "gz_projects_index",
    "gz_case_study",
    "gz_technical_report",
    "gz_appendix",
    "gz_other_page",
    "gz_styles_css",
    "gz_site_js",
)


def test_alt_attr_ignores_data_alt_and_requires_real_alt():
    assert kpi_mod.ALT_ATTR.search('<img data-alt="cover">') is None
    assert kpi_mod.ALT_ATTR.search('<img alt="cover">').group(1) == "cover"
    assert kpi_mod.figures_without_alt('<main><img data-alt="cover"></main>') == 1
    assert kpi_mod.figures_without_alt('<main><img alt="cover"></main>') == 0
    assert (
        kpi_mod.figures_without_alt(
            '<main><figure><img alt="Same"><figcaption>Same</figcaption></figure></main>'
        )
        == 1
    )


def test_kpi_reports_the_primary_metric_and_no_missing_covers():
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts/hillclimb/kpi.py")],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    metrics = dict(re.findall(r"METRIC (\w+)=(\d+)", out))
    assert out.startswith("METRIC experience_gaps=")
    for name in REQUIRED:
        assert name in metrics, f"missing METRIC {name}"
    assert metrics["cards_without_cover"] == "0"
    assert metrics["pages_over_budget"] == "0"
    assert metrics["charts_without_title"] == "0"
    assert metrics["figures_without_alt"] == "0"
    assert int(metrics["experience_gaps"]) == sum(
        int(metrics[k])
        for k in REQUIRED
        if k != "experience_gaps" and not k.startswith("gz_")
    )
