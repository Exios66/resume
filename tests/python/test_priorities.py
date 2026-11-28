"""Unit tests of the adaptive prioritizer, using temporary session state."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "hillclimb"))

import priorities  # noqa: E402


def run(n, status, description, area=None, timestamp=0, **metrics):
    asi = {"area": area} if area else {}
    return {"run": n, "status": status, "description": description, "asi": asi, "metrics": metrics,
            "timestamp": timestamp}


def probe(timestamp=0, **counts):
    return {"type": "probe", "timestamp": timestamp,
            "probes": {k: {"count": v, "examples": [f"{k} example"]} for k, v in counts.items()}}


def full(row, pages=43, inventory="a", errors=()):
    return dict(row, version=2, full=True, pages=pages, inventory=inventory, errors=list(errors))


class Classify(unittest.TestCase):
    def test_asi_area_wins_over_keywords(self):
        self.assertEqual(priorities.classify(run(1, "keep", "card gap", area="weight")), "weight")

    def test_keywords_classify_untagged_runs(self):
        self.assertEqual(priorities.classify(run(1, "keep", "Explore tiles: arrow affordance")), "alignment")
        self.assertEqual(priorities.classify(run(1, "keep", "Stronger focus ring on chips")), "focus")
        self.assertEqual(priorities.classify(run(1, "keep", "Measured test runs replace grep counts")), "content")

    def test_unknown_area_in_asi_falls_back_to_keywords(self):
        self.assertEqual(priorities.classify(run(1, "keep", "dark theme contrast", area="nonsense")), "colour")

    def test_baselines_are_not_experiments(self):
        tally = priorities.outcomes([run(1, "keep", "baseline", area="weight"), run(2, "discard", "x", area="weight")])
        self.assertEqual(tally["weight"], [0, 1])


class Posterior(unittest.TestCase):
    def test_prior_follows_ledger_keep_rate(self):
        tally = {name: [0, 0] for name in priorities.AREAS}
        tally["alignment"] = [8, 0]
        a, b = priorities.prior(tally)
        self.assertAlmostEqual(a + b, 2.0)
        self.assertGreater(a, b)

    def test_failures_cool_an_area_with_equal_need(self):
        tally = {name: [0, 0] for name in priorities.AREAS}
        tally["focus"] = [0, 6]
        tally["touch"] = [3, 0]
        need = {name: (0.0, []) for name in priorities.AREAS}
        need["focus"] = (3.0, [])
        need["touch"] = (3.0, [])
        rows = {r["area"]: r for r in priorities.rank(tally, need, draws=2000, seed=1)}
        self.assertGreater(rows["touch"]["p_best"], rows["focus"]["p_best"])
        self.assertAlmostEqual(sum(r["p_best"] for r in rows.values()), 1.0)

    def test_untried_area_wins_near_ties(self):
        # Need decides most picks; the wide posterior of an untried area wins a fair share of near-ties.
        tally = {name: [0, 0] for name in priorities.AREAS}
        tally["alignment"] = [20, 2]
        need = {name: (0.0, []) for name in priorities.AREAS}
        need["alignment"] = (3.0, [])
        need["motion"] = (3.0, [])
        rows = {r["area"]: r for r in priorities.rank(tally, need, draws=4000, seed=2)}
        self.assertGreater(rows["motion"]["p_best"], 0.2)
        self.assertGreater(rows["alignment"]["p_best"], rows["motion"]["p_best"] / 2)

    def test_no_need_means_no_pick(self):
        tally = {name: [0, 0] for name in priorities.AREAS}
        need = {name: (0.0, []) for name in priorities.AREAS}
        self.assertTrue(all(r["p_best"] == 0 for r in priorities.rank(tally, need, draws=100)))

    def test_ranking_is_reproducible_with_a_seed(self):
        tally = {name: [1, 1] for name in priorities.AREAS}
        need = {name: (1.0, []) for name in priorities.AREAS}
        self.assertEqual(priorities.rank(tally, need, 500, 7), priorities.rank(tally, need, 500, 7))


class Need(unittest.TestCase):
    def test_probe_counts_and_growth_size_need(self):
        steady = priorities.needs(None, [full(probe(measure=10)), full(probe(measure=10))], {})["readability"][0]
        grown = priorities.needs(None, [full(probe(measure=5)), full(probe(measure=10))], {})["readability"][0]
        self.assertGreater(steady, 0)
        self.assertGreater(grown, steady)

    def test_waived_signal_adds_no_need_until_it_grows(self):
        waived = priorities.waivers("cover drawings are framed on purpose #waive/cover_empty=10")
        self.assertEqual(waived, {"cover_empty": 10})
        held = priorities.needs(None, [probe(cover_empty=10)], {}, waived)["alignment"]
        self.assertEqual(held[0], 0)
        self.assertIn("waived", held[1][0])
        self.assertGreater(priorities.needs(None, [probe(cover_empty=12)], {}, waived)["alignment"][0], 0)

    def test_spot_checks_are_not_compared_with_full_runs(self):
        whole, spot = dict(probe(measure=300), pages=43), dict(probe(measure=0), pages=1)
        self.assertEqual(priorities.comparable([whole, spot, whole]), [whole, whole])

    def test_a_smaller_full_site_run_still_becomes_latest(self):
        old, new = full(probe(measure=300), pages=43), full(probe(measure=20), pages=42, inventory="b")
        spot = dict(probe(measure=0), version=2, full=False, pages=1, inventory="c", errors=[])
        rows = priorities.comparable([old, new, spot])
        self.assertEqual(rows, [old, new])
        self.assertEqual(priorities.needs(None, rows, {})["readability"][1], ["measure=20: measure example"])

    def test_failed_captures_are_not_evidence(self):
        good, failed = full(probe(measure=30)), full(probe(measure=0), errors=["about.html HTTP 500"])
        self.assertEqual(priorities.comparable([good, failed]), [good])
        self.assertGreater(priorities.needs(None, priorities.comparable([good, failed]), {})["readability"][0], 0)

    def test_growth_compares_only_the_same_pages(self):
        small, large = full(probe(measure=5), inventory="a"), full(probe(measure=10), pages=44, inventory="b")
        across = priorities.needs(None, [small, large], {})["readability"]
        self.assertNotIn("(grew)", across[1][0])
        within = priorities.needs(None, [small, full(probe(measure=10), inventory="a")], {})["readability"]
        self.assertIn("(grew)", within[1][0])

    def test_records_without_an_inventory_are_never_compared(self):
        # Equal page counts do not prove the same pages, so legacy records start no growth or promotion history.
        legacy = [dict(probe(10, tap_near_miss=n), pages=43) for n in (9, 5, 5)]
        self.assertNotIn("(grew)", priorities.needs(None, [legacy[1], dict(legacy[0], timestamp=20)], {})["touch"][1][0])
        self.assertEqual(priorities.same_basis_pairs(legacy), [])
        tally = {name: [0, 0] for name in priorities.AREAS}
        keep = [run(5, "keep", "bigger buttons", area="touch", timestamp=15)]
        self.assertEqual(priorities.proposals(tally, legacy, keep)[0], [])

    def test_weight_pressure_uses_page_budgets(self):
        css_budget = priorities.page_budgets.SHARED["styles.css"][1]
        points, notes = priorities.weight_pressure({"gz_styles_css": int(css_budget * 0.96)})
        self.assertEqual(points, 2)
        self.assertIn("styles.css 96%", notes)
        self.assertEqual(priorities.weight_pressure({"gz_styles_css": int(css_budget * 0.5)})[0], 0)
        self.assertEqual(priorities.weight_pressure({"gz_styles_css": css_budget + 1})[0], 4)

    def test_owner_blocked_titles_add_no_need(self):
        latest = run(9, "keep", "x", repo_style_titles=5)
        self.assertEqual(priorities.needs(latest, [], {})["experience"][0], 0)

    def test_owner_blocked_set_decides_which_gaps_count(self):
        latest = run(9, "keep", "x", repo_style_titles=5, figures_without_alt=2)
        saved = priorities.OWNER_BLOCKED
        self.addCleanup(setattr, priorities, "OWNER_BLOCKED", saved)
        priorities.OWNER_BLOCKED = {"repo_style_titles", "figures_without_alt"}
        self.assertEqual(priorities.needs(latest, [], {})["experience"][0], 0)
        priorities.OWNER_BLOCKED = set()
        self.assertGreater(priorities.needs(latest, [], {})["experience"][0], 0)

    def test_judged_backlog_tags_count_only_open_items(self):
        text = "- [ ] cover crop #area/alignment\n- [x] done #area/alignment\n- [ ] odd #area/unknown\n"
        self.assertEqual(priorities.judged(text), {"alignment": 1})


class Proposals(unittest.TestCase):
    def test_persistent_signal_lowered_by_a_keep_in_its_area_is_promoted(self):
        tally = {name: [0, 0] for name in priorities.AREAS}
        tally["touch"] = [1, 0]
        rows = [full(probe(10, tap_near_miss=9)), full(probe(20, tap_near_miss=5)), full(probe(30, tap_near_miss=5))]
        promote, _ = priorities.proposals(tally, rows, [run(5, "keep", "bigger buttons", area="touch", timestamp=15)])
        self.assertTrue(any(p.startswith("tap_near_miss") for p in promote))

    def test_drop_without_a_keep_in_that_area_between_records_is_not_promoted(self):
        tally = {name: [0, 0] for name in priorities.AREAS}
        rows = [full(probe(10, tap_near_miss=9)), full(probe(20, tap_near_miss=5)), full(probe(30, tap_near_miss=5))]
        elsewhere = [run(5, "keep", "x", area="weight", timestamp=15), run(6, "keep", "y", area="touch", timestamp=25)]
        self.assertEqual(priorities.proposals(tally, rows, elsewhere)[0], [])

    def test_legacy_record_does_not_count_toward_persistence(self):
        tally = {name: [0, 0] for name in priorities.AREAS}
        legacy = dict(probe(5, tap_near_miss=9), pages=43)
        rows = [legacy, full(probe(10, tap_near_miss=9)), full(probe(20, tap_near_miss=5))]
        keep = [run(5, "keep", "bigger buttons", area="touch", timestamp=15)]
        self.assertEqual(priorities.proposals(tally, rows, keep)[0], [])
        rows.append(full(probe(30, tap_near_miss=5)))
        self.assertEqual(len(priorities.proposals(tally, rows, keep)[0]), 1)

    def test_signal_that_never_moved_is_not_promoted(self):
        tally = {name: [0, 0] for name in priorities.AREAS}
        tally["touch"] = [1, 0]
        rows = [full(probe(10, tap_near_miss=5)), full(probe(20, tap_near_miss=5)), full(probe(30, tap_near_miss=5))]
        promote, _ = priorities.proposals(tally, rows, [run(5, "keep", "x", area="touch", timestamp=15)])
        self.assertEqual(promote, [])

    def test_cold_area_is_flagged_for_retirement(self):
        tally = {name: [0, 0] for name in priorities.AREAS}
        tally["type"] = [0, 7]
        _, retire = priorities.proposals(tally, [])
        self.assertTrue(any(r.startswith("type:") for r in retire))


class Command(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        saved = (priorities.LEDGER, priorities.PROBES, priorities.IDEAS)
        self.addCleanup(lambda: setattr_all(saved))
        priorities.LEDGER, priorities.PROBES, priorities.IDEAS = root / "l.jsonl", root / "p.jsonl", root / "i.md"
        priorities.LEDGER.write_text(json.dumps(run(1, "keep", "baseline", gz_styles_css=19500)) + "\n", encoding="utf-8")
        priorities.PROBES.write_text(json.dumps(probe(measure=40)) + "\n", encoding="utf-8")

    def test_json_output_names_every_area(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(priorities.main(["--json", "--draws", "200"]), 0)
        data = json.loads(out.getvalue())
        self.assertEqual({r["area"] for r in data["areas"]}, set(priorities.AREAS))

    def test_zero_draws_is_refused(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            priorities.main(["--draws", "0"])
        with self.assertRaises(ValueError):
            priorities.rank({n: [0, 0] for n in priorities.AREAS}, {n: (1.0, []) for n in priorities.AREAS}, draws=0)

    def test_text_output_names_the_next_area(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            priorities.main(["--draws", "200"])
        self.assertRegex(out.getvalue(), r"NEXT area=(readability|weight) ")


def setattr_all(saved):
    priorities.LEDGER, priorities.PROBES, priorities.IDEAS = saved


if __name__ == "__main__":
    unittest.main()
