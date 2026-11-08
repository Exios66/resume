#!/usr/bin/env python3
"""Experiment ledger for the polish hill-climb (autoresearch.jsonl).

  ledger.py status                         segment, best, streak and a verdict for the next step
  ledger.py segment "<name>"               start a new segment (a changed audit or target); writes a config header
  ledger.py log <status> "<desc>" [asi]    append the run whose metrics are in run.log; status is keep, discard,
                                           crash or checks_failed; asi is a JSON object of notes that survive reverts
  ledger.py pause "<note>"                 mark the session paused (still resumable)
  ledger.py table                          print every run as a Markdown table

The log is append-only. Run numbers climb across segments; counts and streaks use the current segment only.
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
PRIMARY = "polish_defects"
STATUSES = ("keep", "discard", "crash", "checks_failed")


def records():
    if not LOG.exists():
        return []
    return [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines() if line.strip()]


def append(record):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def current_segment(rows):
    configs = [r for r in rows if r.get("type") == "config"]
    return configs[-1].get("segment", len(configs) - 1) if configs else None


def runs(rows, segment=None):
    out = [r for r in rows if r.get("status") in STATUSES and "run" in r]
    return out if segment is None else [r for r in out if r.get("segment") == segment]


def metrics_from_run_log():
    if not RUN_LOG.exists():
        sys.exit("run.log not found: run the benchmark first (scripts/hillclimb/hc.sh experiment ...)")
    found = dict(re.findall(r"^METRIC (\w+)=([-\d.]+)$", RUN_LOG.read_text(encoding="utf-8"), re.M))
    if PRIMARY not in found:
        sys.exit(f"run.log has no METRIC {PRIMARY}; the benchmark failed. Log it as crash only after reading run.log.")
    return {k: float(v) if "." in v else int(v) for k, v in found.items()}


def confidence(values):
    """Best improvement over the segment baseline in units of median absolute deviation."""
    if len(values) < 3:
        return None
    median = statistics.median(values)
    mad = statistics.median(abs(v - median) for v in values) or 1
    return round(abs(values[0] - min(values)) / mad, 2)


def cmd_log(status, description, asi="{}"):
    if status not in STATUSES:
        sys.exit(f"status must be one of {', '.join(STATUSES)}")
    rows = records()
    segment = current_segment(rows)
    if segment is None:
        sys.exit('no config header: run  ledger.py segment "<name>"  first')
    metrics = metrics_from_run_log()
    commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout.strip()
    previous = [r["metric"] for r in runs(rows, segment)]
    record = {
        "run": max([r["run"] for r in runs(rows)] or [-1]) + 1,
        "commit": commit,
        "metric": metrics.pop(PRIMARY),
        "metrics": metrics,
        "status": status,
        "description": description,
        "timestamp": int(time.time()),
        "segment": segment,
        "asi": json.loads(asi),
    }
    record["confidence"] = confidence(previous + [record["metric"]])
    append(record)
    print(f"logged run {record['run']} ({status}) {PRIMARY}={record['metric']} segment={segment}")


def cmd_segment(name):
    rows = records()
    segment = current_segment(rows)
    segment = 0 if segment is None else segment + 1
    append({"type": "config", "name": name, "metricName": PRIMARY, "metricUnit": "points",
            "bestDirection": "lower", "segment": segment})
    append({"type": "status", "state": "running", "timestamp": int(time.time())})
    print(f"segment {segment}: {name}. Run the baseline next and log it as keep.")


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
    print("| # | Seg | Description | " + PRIMARY + " | Status |\n|---|---|---|---|---|")
    for r in runs(records()):
        print(f"| {r['run']} | {r.get('segment')} | {r['description']} | {r['metric']} | {r['status']} |")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    command, args = argv[0], argv[1:]
    handlers = {"log": cmd_log, "segment": cmd_segment, "pause": cmd_pause, "status": cmd_status, "table": cmd_table}
    if command not in handlers:
        sys.exit(__doc__)
    handlers[command](*args)


if __name__ == "__main__":
    os.chdir(ROOT)
    main(sys.argv[1:])
