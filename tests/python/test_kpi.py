"""The experience KPI script runs on the built site and reports its primary metric."""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_kpi_reports_the_primary_metric_and_no_missing_covers():
    out = subprocess.run([sys.executable, str(ROOT / "scripts/hillclimb/kpi.py")],
                         capture_output=True, text=True, check=True).stdout
    metrics = dict(re.findall(r"METRIC (\w+)=(\d+)", out))
    assert out.startswith("METRIC experience_gaps=")
    assert metrics["cards_without_cover"] == "0"
    assert metrics["pages_over_budget"] == "0"
