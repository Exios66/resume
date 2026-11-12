"""Unit tests of the experience-scored ledger, using temporary session state."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "hillclimb"))

import ledger  # noqa: E402


class LedgerSession(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        ledger.LOG = self.root / "autoresearch.jsonl"
        ledger.RUN_LOG = self.root / "run.log"
        ledger.ROOT = self.root

    def write_run_log(self, **metrics):
        ledger.RUN_LOG.write_text(
            "".join(f"METRIC {name}={value}\n" for name, value in metrics.items()), encoding="utf-8")

    def records(self):
        return [json.loads(line) for line in ledger.LOG.read_text(encoding="utf-8").splitlines()]

    def out(self, function, *args):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            function(*args)
        return buffer.getvalue()

    def test_default_segment_keeps_the_polish_primary(self):
        self.out(ledger.cmd_segment, "polish")
        self.write_run_log(polish_defects=2, render_s=45)
        self.out(ledger.cmd_log, "keep", "baseline")
        config = self.records()[0]
        self.assertEqual(config["metricName"], "polish_defects")
        self.assertNotIn("gates", config)
        run = self.records()[-1]
        self.assertEqual((run["metric"], run["status"]), (2, "keep"))
        self.assertEqual(run["metrics"]["render_s"], 45)

    def test_experience_segment_scores_its_own_metric_with_a_gate(self):
        self.out(ledger.cmd_segment, "experience", "--metric", "experience_gaps", "--gate", "polish_defects=0")
        config = self.records()[0]
        self.assertEqual(config["metricName"], "experience_gaps")
        self.assertEqual(config["gates"], {"polish_defects": 0})
        self.write_run_log(polish_defects=0, experience_gaps=19, images_without_size=0)
        self.out(ledger.cmd_log, "keep", "baseline")
        run = self.records()[-1]
        self.assertEqual((run["metric"], run["status"]), (19, "keep"))
        self.assertEqual(run["metrics"]["polish_defects"], 0)
        self.assertEqual(run["metrics"]["images_without_size"], 0)
        self.assertEqual(self.out(ledger.cmd_best).strip(), "19")

    def test_gate_failure_and_missing_scored_metric_stop_the_log(self):
        self.out(ledger.cmd_segment, "experience", "--metric", "experience_gaps", "--gate", "polish_defects=0")
        self.write_run_log(polish_defects=2, experience_gaps=19)
        with self.assertRaises(SystemExit) as failed:
            ledger.cmd_log("keep", "over the gate")
        self.assertIn("gate failed: polish_defects=2 > 0", str(failed.exception))
        self.write_run_log(images_without_size=0)
        with self.assertRaises(SystemExit) as missing:
            ledger.cmd_log("keep", "no scored metric")
        self.assertIn("run.log has no METRIC experience_gaps", str(missing.exception))
        self.assertEqual(self.records(), [self.records()[0], self.records()[1]],
                         "failed logs must not append a run record")

    def test_segment_option_and_status_use_the_segment_metric(self):
        with self.assertRaises(SystemExit) as bad:
            self.out(ledger.cmd_segment, "experience", "--primary", "experience_gaps")
        self.assertIn("unknown segment option", str(bad.exception))
        self.out(ledger.cmd_segment, "experience", "--metric", "experience_gaps", "--gate", "polish_defects=0")
        self.write_run_log(polish_defects=0, experience_gaps=19)
        self.out(ledger.cmd_log, "keep", "baseline")
        status = self.out(ledger.cmd_status)
        self.assertIn("SEGMENT=0", status)
        self.assertIn("BEST=19 at unknown", status)
        self.assertIn("VERDICT=continue", status)
        table = self.out(ledger.cmd_table)
        self.assertIn("| metric |", table)
        self.assertIn("| 0 | 0 | baseline | 19 | keep |", table)


if __name__ == "__main__":
    unittest.main()
