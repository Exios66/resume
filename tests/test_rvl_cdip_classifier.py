"""Regressions for the RVL-CDIP case study's majority-voting forecast.

Run from the repository root: python3 -m pytest -q tests/test_rvl_cdip_classifier.py
These checks read the source and committed HTML; no render or network is needed.
"""

import re
import unittest

import test_links as checks
from test_portfolio_additions import ContentParser


class VotingForecastTests(unittest.TestCase):
    def setUp(self):
        question = "Would majority voting help?"
        source = (checks.ROOT / "projects/rvl-cdip-classifier.qmd").read_text(encoding="utf-8")
        source_rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]
                       for line in source.splitlines() if line.lstrip().startswith("|")]
        parser = ContentParser(checks.DOCS / "projects/rvl-cdip-classifier.html")
        published_rows = [[parser.text(cell) for tag, cell in parser.children(row) if tag == "td"]
                          for tag, row, _ in parser.elements if tag == "tr"]
        self.rows = {}
        for name, rows in (("source", source_rows), ("published", published_rows)):
            matches = [row for row in rows if row and row[0] == question]
            self.assertEqual(len(matches), 1, f"{name} needs exactly one majority-voting row")
            self.assertEqual(len(matches[0]), 3, f"{name} needs separate forecast and measurement cells")
            self.rows[name] = matches[0]

    def test_forecast_identifies_the_pool_and_excludes_repeated_reads_of_one_classifier(self):
        # Scope assertions to the row: the surrounding prose already had this caveat before PR #44.
        for name, (_, forecast, _) in self.rows.items():
            with self.subTest(page=name):
                self.assertIn("Forecast from the pooled, mixed-model corpus", forecast)
                self.assertIn("not repeated reads of one fixed classifier", forecast)

    def test_each_read_count_is_paired_with_its_forecast_accuracy(self):
        for name, (_, forecast, _) in self.rows.items():
            with self.subTest(page=name):
                pairs = re.findall(r"\b(\d+) reads,\s*(\d+\.\d+)%", forecast)
                self.assertEqual(pairs, [("7", "85.0"), ("25", "86.3")])

    def test_cost_scaling_is_explicitly_assumed_and_not_a_measured_rerun_cost(self):
        for name, (_, forecast, _) in self.rows.items():
            with self.subTest(page=name):
                self.assertIn("Cost is assumed to scale with the number of reads", forecast)
                self.assertIn("it is not a measured rerun cost", forecast)

    def test_forecast_has_no_claimed_live_measurement(self):
        for name, (_, _, measured) in self.rows.items():
            with self.subTest(page=name):
                self.assertEqual(measured, "Not tested on a live run.")

    def test_published_voting_row_matches_the_source(self):
        self.assertEqual(self.rows["published"], self.rows["source"])


if __name__ == "__main__":
    unittest.main()
