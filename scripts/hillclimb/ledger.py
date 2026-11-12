#!/usr/bin/env python3
"""Experiment ledger for the polish hill-climb (autoresearch.jsonl).

  ledger.py status                         segment, best, streak and a verdict for the next step
  ledger.py segment "<name>"               start a new segment (a changed audit or target); writes a config header
  ledger.py segment "<name>" --metric experience_gaps --gate polish_defects=0
                                           start an experience-scored segment: the named metric is scored,
                                           and every gate metric must be at or better than its limit
  ledger.py log <status> "<desc>" [asi]    append the run whose metrics are in run.log; status is keep, discard,
                                           crash or checks_failed; asi is a JSON object of notes that survive reverts.
                                           keep/discard require the scored metric, gates apply to keep only, and
                                           crash/checks_failed record whatever run.log does contain
  ledger.py pause "<note>"                 mark the session paused (still resumable)
  ledger.py table                          print every run as a Markdown table
  ledger.py next                           print the number the next logged run will get
  ledger.py best                           print the best kept metric in the current segment

The log is append-only. Run numbers climb across segments; counts and streaks use the current segment only.
Each segment's config names its scored metric (`metricName`); `polish_defects` is the default for
segments started without `--metric`.
"""

import json
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "autoresearch.jsonl"
RUN_LOG = ROOT / "run.log"
DEFAULT_PRIMARY = "polish_defects"
STATUSES = ("keep", "discard", "crash", "checks_failed")


def records():
    if not LOG.exists():
        return []
    return [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines() if line.strip()]


def append(record):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def current_config(rows):
    configs = [r for r in rows if r.get("type") == "config"]
    return configs[-1] if configs else None


def current_segment(rows):
    config = current_config(rows)
    return config.get("segment", 0) if config else None


def primary(rows):
    """The metric the current segment scores; the segment config owns the name."""
    config = current_config(rows)
    return (config or {}).get("metricName", DEFAULT_PRIMARY)


def runs(rows, segment=None):
    out = [r for r in rows if r.get("status") in STATUSES and "run" in r]
    return out if segment is None else [r for r in out if r.get("segment") == segment]


def metrics_from_run_log(scored):
    if not RUN_LOG.exists():
        sys.exit("run.log not found: run the benchmark first (scripts/hillclimb/hc.sh experiment ...)")
    found = dict(re.findall(r"^METRIC (\w+)=([-\d.]+)$", RUN_LOG.read_text(encoding="utf-8"), re.M))
    if scored not in found:
        sys.exit(f"run.log has no METRIC {scored}; the benchmark failed. Log it as crash only after reading run.log.")
    return {k: float(v) if "." in v else int(v) for k, v in found.items()}


def confidence(values):
    """Best improvement over the segment baseline in units of median absolute deviation."""
    if len(values) < 3:
        return None
    median = statistics.median(values)
    mad = statistics.median(abs(v - median) for v in values) or 1
    return round(abs(values[0] - min(values)) / mad, 2)


def head_commit():
    out = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else "unknown"


def cmd_log(status, description, asi="{}"):
    if status not in STATUSES:
        sys.exit(f"status must be one of {', '.join(STATUSES)}")
    rows = records()
    segment = current_segment(rows)
    if segment is None:
        sys.exit('no config header: run  ledger.py segment "<name>"  first')
    scored = primary(rows)
    if status in ("keep", "discard"):
        metrics = metrics_from_run_log(scored)
        if status == "keep":
            for gate, limit in sorted((current_config(rows) or {}).get("gates", {}).items()):
                if gate not in metrics:
                    sys.exit(f"run.log has no METRIC {gate} for the segment's gate; the benchmark must print it")
                if metrics[gate] > limit:
                    sys.exit(f"gate failed: {gate}={metrics[gate]} > {limit}; fix it, or log the run as checks_failed")
    else:
        # A crash or checks_failed run may have no usable benchmark output; record
        # whatever metrics run.log does contain and let the verdict logic react.
        metrics = {}
        if RUN_LOG.exists():
            metrics = {k: float(v) if "." in v else int(v) for k, v in
                       re.findall(r"^METRIC (\w+)=([-\d.]+)$", RUN_LOG.read_text(encoding="utf-8"), re.M)}
    commit = head_commit()
    previous = [r["metric"] for r in runs(rows, segment)]
    record = {
        "run": max([r["run"] for r in runs(rows)] or [-1]) + 1,
        "commit": commit,
        "metric": metrics.pop(scored, None),
        "metrics": metrics,
        "status": status,
        "description": description,
        "timestamp": int(time.time()),
        "segment": segment,
        "asi": json.loads(asi),
    }
    record["confidence"] = confidence(previous + [record["metric"]])
    append(record)
    print(f"logged run {record['run']} ({status}) {scored}={record['metric']} segment={segment}")


def cmd_segment(name, *options):
    metric, gates = DEFAULT_PRIMARY, {}
    index = 0
    while index < len(options):
        if options[index] == "--metric" and index + 1 < len(options):
            metric = options[index + 1]
            index += 2
        elif options[index] == "--gate" and index + 1 < len(options):
            key, _, value = options[index + 1].partition("=")
            gates[key] = float(value) if "." in value else int(value)
            index += 2
        else:
            sys.exit(f"unknown segment option {options[index]!r}; use --metric <name> or --gate <name>=<limit>")
    rows = records()
    segment = current_segment(rows)
    segment = 0 if segment is None else segment + 1
    config = {"type": "config", "name": name, "metricName": metric, "metricUnit": "points",
              "bestDirection": "lower", "segment": segment}
    if gates:
        config["gates"] = gates
    append(config)
    append({"type": "status", "state": "running", "timestamp": int(time.time())})
    gates_note = f"; gates {gates}" if gates else ""
    print(f"segment {segment}: {name}, scoring {metric}{gates_note}. Run the baseline next and log it as keep.")


def cmd_pause(note):
    append({"type": "status", "state": "running", "note": note, "timestamp": int(time.time())})
    print("paused (resumable)")


def cmd_status():
    rows = records()
    if not rows:
        print('VERDICT=setup  (no autoresearch.jsonl; restore with hc.sh restore, or start with ledger.py segment "<name>")')
        return
    segment = current_segment(rows)
    seg_runs = runs(rows, segment)
    statuses = [r for r in rows if r.get("type") == "status"]
    state = statuses[-1]["state"] if statuses else "running"
    streak = 0
    for r in reversed(seg_runs):
        if r["status"] in ("discard", "crash"):
            streak += 1
        else:
            break
    kept = [r for r in seg_runs if r["status"] == "keep"]
    best = min(kept, key=lambda r: r["metric"]) if kept else None
    print(f"SEGMENT={segment}")
    print(f"SEGMENT_RUNS={len(seg_runs)}")
    print(f"BEST={best['metric'] if best else 'none'} at {best['commit'] if best else '-'} ({best['description'] if best else ''})")
    print(f"LAST={seg_runs[-1]['status'] + ' ' + str(seg_runs[-1]['metric']) if seg_runs else 'none'}")
    print(f"STREAK={streak}")
    print(f"STATE={state}")
    if state != "running":
        verdict = "concluded (ask the owner before resuming)"
    elif streak > 8:
        verdict = "wall (stop and report, or start a genuinely different segment)"
    elif streak >= 3:
        verdict = "rethink (change approach: re-read sources, consult the ideas backlog)"
    elif not seg_runs:
        verdict = "baseline (run the benchmark on the unchanged tree and log it as keep)"
    else:
        verdict = "continue"
    print(f"VERDICT={verdict}")


def cmd_table():
    print("| # | Seg | Description | metric | Status |\n|---|---|---|---|---|")
    for r in runs(records()):
        print(f"| {r['run']} | {r.get('segment')} | {r['description']} | {r['metric']} | {r['status']} |")


def cmd_next():
    print(max([r["run"] for r in runs(records())] or [-1]) + 1)


def cmd_best():
    rows = records()
    kept = [r["metric"] for r in runs(rows, current_segment(rows)) if r["status"] == "keep"]
    print(min(kept) if kept else "none")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    command, args = argv[0], argv[1:]
    handlers = {"log": cmd_log, "segment": cmd_segment, "pause": cmd_pause, "status": cmd_status, "table": cmd_table,
                "next": cmd_next, "best": cmd_best}
    if command not in handlers:
        sys.exit(__doc__)
    handlers[command](*args)


if __name__ == "__main__":
    os.chdir(ROOT)
    main(sys.argv[1:])
