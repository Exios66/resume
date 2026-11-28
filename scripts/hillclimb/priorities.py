#!/usr/bin/env python3
"""Choose the next hill-climb experiment from the evidence, not only from the fixed benchmark.

The loop's scored metric stays fixed within a segment (polish_defects or experience_gaps). This tool
answers a different question: *where* is the next experiment most likely to make the site better?
It combines three kinds of evidence into a posterior per improvement area:

1. Outcomes. Every logged run is classified into an area (its ASI ``area`` key, else keywords in its
   description). Keeps and failures update a Beta posterior of "an experiment here gets kept", with an
   empirical-Bayes prior from the whole ledger, so areas that keep failing cool off and new areas start
   at the site-wide rate instead of zero.
2. Need. The latest discovery probes (``probes.cjs``, appended to ``autoresearch.probes.jsonl``), the
   latest benchmark metrics (polish findings, experience gaps, page-weight pressure against
   ``page_budgets.py``) and judged backlog items tagged ``#area/<name>`` give each area a size.
   A signal that grew since the previous probe record counts extra: a regression or a newly exposed
   weak point is surprising evidence and should be looked at soon.
3. Uncertainty. Thompson sampling draws a keep-rate from each posterior and multiplies it by the need,
   many times over; ``P(best)`` is how often each area wins. Little-tried areas keep a wide posterior,
   so they still win sometimes; that is how the loop keeps exploring new weak points.

It also proposes segment changes, without making them:
- *promote*: a probe signal seen in three or more probe records that experiments have already moved
  is a candidate for a scored metric in the next segment (a separate, reviewed commit; see
  ``.10x/metrics.md``, "Adaptive priorities").
- *retire*: an area kept under 20% of the time after six or more attempts needs a different approach
  or an owner decision.

Usage:
    python3 scripts/hillclimb/priorities.py [--seed N] [--draws N] [--json]

Never use this to rescue a run: it ranks work; it does not score it.
"""
import argparse
import json
import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "autoresearch.jsonl"
PROBES = ROOT / "autoresearch.probes.jsonl"
IDEAS = ROOT / "autoresearch.ideas.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import page_budgets  # noqa: E402

# Each area: the evidence that sizes it, the words that classify untagged runs, and a value weight
# (how much a visitor gains per unit of need; accessibility and weight outrank taste).
AREAS = {
    # Fact and wording runs come first so their words ("measured", "count") do not count as layout work.
    "content": {"probes": [], "keywords": ["test run", "tests", "count", "readme", "fact", "source repo", "wording",
                                           "claim", "figure from", "numbers"],
                "value": 1.0, "summary": "project facts and wording checked against their sources"},
    "weight": {"probes": [], "keywords": ["weight", "gzip", "budget", "bytes", "trim", "minif", "comment"],
               "value": 1.2, "summary": "page and asset transfer weight against budgets"},
    "focus": {"probes": ["focus_unseen"], "keywords": ["focus", "keyboard", "tabindex"],
              "value": 1.3, "summary": "visible keyboard focus"},
    "touch": {"probes": ["tap_near_miss"], "keywords": ["tap", "touch", "target", "44"],
              "value": 1.0, "summary": "phone touch targets beyond the 24 px minimum"},
    "alignment": {"probes": ["row_misalign", "cover_empty"],
                  "keywords": ["align", "card", "cover", "row", "grid", "gap", "spacing", "pill", "tile"],
                  "value": 0.9, "summary": "grid rows, card rhythm and cover panels"},
    "readability": {"probes": ["measure", "centered_prose"],
                    "keywords": ["measure", "line length", "centred", "centered", "hero", "prose", "paragraph",
                                 "widow", "wrap", "reading"],
                    "value": 1.0, "summary": "line length and text alignment"},
    "type": {"probes": ["type_sprawl"], "keywords": ["font", "typograph", "heading", "kicker", "type scale", "size"],
             "value": 0.7, "summary": "type scale consistency"},
    "colour": {"probes": ["svg_contrast", "colour_sprawl"], "keywords": ["contrast", "colour", "color", "dark", "theme"],
               "value": 1.1, "summary": "contrast and palette consistency"},
    "motion": {"probes": ["motion_reduced", "layout_shift"],
               "keywords": ["motion", "animation", "transition", "reduced", "shift", "cls", "drift"],
               "value": 1.1, "summary": "motion preferences and layout stability"},
    "audit": {"probes": [], "keywords": ["axe", "table", "stack", "crushed", "overflow", "separator", "label", "svg"],
              "value": 1.2, "summary": "findings of the fixed polish audit"},
    "experience": {"probes": [], "keywords": ["social", "og", "lazy", "image", "screenshot", "title", "structured"],
                   "value": 1.0, "summary": "experience KPI gaps that are not owner-blocked"},
}
FAIL = {"discard", "crash", "checks_failed"}
OWNER_BLOCKED = {"repo_style_titles"}  # .10x/metrics.md: only the owner can close these
EXPERIENCE_GAPS = ("cards_without_cover", "projects_without_own_social_card", "projects_without_structured_data",
                   "images_without_size", "later_images_not_lazy", "charts_without_title", "figures_without_alt",
                   "pages_over_budget", "repo_style_titles")


def current_run(ledger_rows):
    """Measurements of the site as it stands: the last kept run, with its scored metric put back.

    A discarded, crashed or failed run is reverted, so its measurements describe a site that no longer exists;
    it still counts in the outcome tally. ``ledger.py`` moves the scored value out of ``metrics`` into
    ``metric``; it goes back under its segment's ``metricName`` (``polish_defects`` when none is set).
    """
    kept = [r for r in ledger_rows if "run" in r and r.get("status") == "keep"]
    if not kept:
        return None
    run = dict(kept[-1], metrics=dict(kept[-1].get("metrics") or {}))
    if run.get("metric") is not None:
        names = {c.get("segment"): c.get("metricName") for c in ledger_rows if c.get("type") == "config"}
        run["metrics"].setdefault(names.get(run.get("segment")) or "polish_defects", run["metric"])
    return run


def read_jsonl(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def classify(run):
    """Area of a logged run: its ASI ``area`` if valid, else the first area whose keyword it mentions."""
    asi = run.get("asi") if isinstance(run.get("asi"), dict) else {}
    if asi.get("area") in AREAS:
        return asi["area"]
    text = " ".join(str(x) for x in (run.get("description", ""), asi.get("hypothesis", ""))).lower()
    for name, area in AREAS.items():
        if any(re.search(r"(?<![a-z])" + re.escape(k), text) for k in area["keywords"]):
            return name
    return None


def outcomes(runs):
    """(keeps, failures) per area; baselines are not experiments and do not count."""
    tally = {name: [0, 0] for name in AREAS}
    for run in runs:
        if "run" not in run or run.get("description", "").strip().lower() == "baseline":
            continue
        area = classify(run)
        if area is None:
            continue
        if run.get("status") == "keep":
            tally[area][0] += 1
        elif run.get("status") in FAIL:
            tally[area][1] += 1
    return tally


def prior(tally, strength=2.0):
    """Empirical-Bayes Beta prior: the ledger-wide keep rate, worth ``strength`` pseudo-runs."""
    keeps = sum(k for k, _ in tally.values())
    fails = sum(f for _, f in tally.values())
    rate = (keeps + 1) / (keeps + fails + 2)
    return strength * rate, strength * (1 - rate)


def weight_pressure(metrics):
    """Need from transfer weight: rows at 90% of budget count 1, at 95% count 2, over budget 4."""
    rows = {
        "home": "gz_home", "projects index": "gz_projects_index", "case study": "gz_case_study",
        "technical report": "gz_technical_report", "appendix": "gz_appendix", "other page": "gz_other_page",
    }
    pairs = [(metrics.get(key), page_budgets.PAGE_TYPES[kind][1], kind) for kind, key in rows.items()]
    pairs += [(metrics.get("gz_styles_css"), page_budgets.SHARED["styles.css"][1], "styles.css"),
              (metrics.get("gz_site_js"), page_budgets.SHARED["assets/js/site.js"][1], "site.js")]
    need, notes = 0, []
    for size, budget, kind in pairs:
        if not size:
            continue
        share = size / budget
        points = 4 if share > 1 else 2 if share >= 0.95 else 1 if share >= 0.9 else 0
        if points:
            need += points
            notes.append(f"{kind} {share:.0%}")
    return need, notes


def judged(ideas_text):
    """Open backlog items tagged #area/<name> (a judged finding from a screenshot review)."""
    counts = {}
    for line in ideas_text.splitlines():
        if re.match(r"\s*-\s*\[ \]", line):
            for name in re.findall(r"#area/([a-z]+)", line):
                if name in AREAS:
                    counts[name] = counts.get(name, 0) + 1
    return counts


def comparable(probe_rows):
    """Probe records that can stand for the whole site: full-site runs whose every page was measured.

    A spot check with ``--pages`` must not read as a site-wide drop, and a run with capture errors would read
    missing measurements as zero signals. Both stay in the log for diagnosis. Records written before the probe
    runner marked ``full`` count as full when they cover the most pages among such records.
    """
    clean = [r for r in probe_rows if not r.get("errors")]
    legacy = max((r.get("pages", 0) for r in clean if "full" not in r), default=0)
    return [r for r in clean if r.get("full", r.get("pages", 0) == legacy)]


def basis(row):
    """Records with the same probe version and page inventory measure the same thing, so counts compare.

    A record written before inventories were kept has no basis: an equal page count does not prove the same
    pages, so it is never compared for growth or promotion. A fresh full-site capture starts the history.
    """
    return (row.get("version", 1), row["inventory"]) if row.get("inventory") else None


def by_basis(probe_rows):
    """Records grouped by basis, in log order; records with no basis belong to no group."""
    groups = {}
    for row in probe_rows:
        if basis(row) is not None:
            groups.setdefault(basis(row), []).append(row)
    return list(groups.values())


def same_basis_pairs(probe_rows):
    """Consecutive (earlier, later) records on the same basis: the only pairs where a count change means anything."""
    return [pair for group in by_basis(probe_rows) for pair in zip(group, group[1:])]


def waivers(ideas_text):
    """Probe counts a person judged acceptable: ``#waive/<probe>=<count>`` anywhere in the backlog.

    A waived signal adds no need until its count rises above the waived count, so a regression still shows.
    """
    return {k: int(v) for k, v in re.findall(r"#waive/([a-z_]+)=(\d+)", ideas_text)}


def needs(latest_run, probe_rows, judged_counts, waived=None):
    """Need per area (log-scaled so one huge count cannot drown every other area) plus its evidence."""
    latest = probe_rows[-1]["probes"] if probe_rows else {}
    # Growth only counts against an earlier record of the same pages and probe version.
    key = basis(probe_rows[-1]) if probe_rows else None
    earlier = [r for r in probe_rows[:-1] if key is not None and basis(r) == key]
    previous = earlier[-1]["probes"] if earlier else {}
    metrics = (latest_run or {}).get("metrics", {})
    out = {}
    for name, area in AREAS.items():
        need, notes = 0.0, []
        for key in area["probes"]:
            count = latest.get(key, {}).get("count", 0)
            if not count:
                continue
            if waived and key in waived and count <= waived[key]:
                notes.append(f"{key}={count} (waived up to {waived[key]})")
                continue
            grown = previous and count > previous.get(key, {}).get("count", 0)
            need += math.log1p(count) * (1.5 if grown else 1.0)
            example = (latest[key].get("examples") or [""])[0]
            notes.append(f"{key}={count}{' (grew)' if grown else ''}" + (f": {example}" if example else ""))
        if name == "weight":
            pressure, rows = weight_pressure(metrics)
            need += pressure
            notes += rows
        if name == "audit" and metrics.get("polish_defects"):
            need += math.log1p(metrics["polish_defects"])
            notes.append(f"polish_defects={metrics['polish_defects']}")
        if name == "experience":
            open_gaps = {k: v for k, v in metrics.items() if k in EXPERIENCE_GAPS and k not in OWNER_BLOCKED and v}
            for key, value in open_gaps.items():
                need += math.log1p(value)
                notes.append(f"{key}={value}")
        if judged_counts.get(name):
            need += judged_counts[name]
            notes.append(f"judged backlog items={judged_counts[name]}")
        out[name] = (need * area["value"], notes)
    return out


def rank(tally, need, draws=4000, seed=0):
    """Thompson sampling: how often each area has the highest sampled keep-rate x need."""
    if draws < 1:
        raise ValueError("draws must be at least 1")
    rng = random.Random(seed)
    a0, b0 = prior(tally)
    names = [n for n in AREAS if need[n][0] > 0]
    wins = {n: 0 for n in names}
    for _ in range(draws if names else 0):
        best = max(names, key=lambda n: rng.betavariate(a0 + tally[n][0], b0 + tally[n][1]) * need[n][0])
        wins[best] += 1
    rows = []
    for n in AREAS:
        k, f = tally[n]
        rows.append({"area": n, "keeps": k, "fails": f, "keep_rate": (a0 + k) / (a0 + b0 + k + f),
                     "need": round(need[n][0], 2), "p_best": wins.get(n, 0) / draws,
                     "evidence": need[n][1], "summary": AREAS[n]["summary"]})
    rows.sort(key=lambda r: (-r["p_best"], -r["need"]))
    return rows


def probe_count(row, key):
    return row["probes"].get(key, {}).get("count", 0)


def proposals(tally, probe_rows, runs=()):
    """Segment-level suggestions: promote persistent signals that kept work moved; retire cold areas.

    Persistence and the drop are both judged within one basis (same pages and probe version): the signal must
    show in three records of that basis, and a kept run in its area must be logged between two of them whose
    count fell. Records with no inventory never count toward either.
    """
    promote, retire = [], []
    keeps = [r for r in runs if r.get("status") == "keep" and "run" in r
             and r.get("description", "").strip().lower() != "baseline"]
    for name, area in AREAS.items():
        stamps = [r.get("timestamp", 0) for r in keeps if classify(r) == name]
        for key in area["probes"]:
            for group in by_basis(probe_rows):
                seen = len([r for r in group if probe_count(r, key)])
                moved = any(probe_count(b, key) < probe_count(a, key)
                            and any(a.get("timestamp", 0) < t <= b.get("timestamp", 0) for t in stamps)
                            for a, b in zip(group, group[1:]))
                if seen >= 3 and moved:
                    promote.append(f"{key} ({name}): seen in {seen} comparable probe records and lowered by a kept {name} run")
                    break
        k, f = tally[name]
        if k + f >= 6 and (k + 1) / (k + f + 2) < 0.2:
            retire.append(f"{name}: {k} kept of {k + f} (posterior keep rate under 20%); change approach or ask the owner")
    return promote, retire


def positive_int(text):
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--draws", type=positive_int, default=4000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    ledger_rows = read_jsonl(LEDGER)
    runs = [r for r in ledger_rows if "run" in r]
    probe_rows = comparable([r for r in read_jsonl(PROBES) if r.get("type") == "probe"])
    tally = outcomes(runs)
    ideas = IDEAS.read_text(encoding="utf-8") if IDEAS.exists() else ""
    need = needs(current_run(ledger_rows), probe_rows, judged(ideas), waivers(ideas))
    rows = rank(tally, need, args.draws, args.seed)
    promote, retire = proposals(tally, probe_rows, runs)
    if args.json:
        print(json.dumps({"areas": rows, "promote": promote, "retire": retire}, indent=2))
        return 0
    print(f"{len(runs)} logged runs, {len(probe_rows)} probe records")
    print(f"{'area':12} {'P(best)':>8} {'need':>6} {'keep':>5} {'kept/tried':>10}  evidence")
    for r in rows:
        tried = r["keeps"] + r["fails"]
        print(f"{r['area']:12} {r['p_best']:8.0%} {r['need']:6.2f} {r['keep_rate']:5.0%} {r['keeps']:>4}/{tried:<5}  "
              + ("; ".join(r["evidence"][:3]) or "-"))
    best = next((r for r in rows if r["p_best"] > 0), None)
    if best:
        print(f"NEXT area={best['area']} ({best['summary']}); log the run with ASI {{\"area\": \"{best['area']}\"}}")
    for line in promote:
        print("PROMOTE", line)
    for line in retire:
        print("RETIRE", line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
