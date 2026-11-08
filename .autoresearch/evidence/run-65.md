# Evidence for run 65

- Commit: `e5c3d67 experiment: Link chart marks and source rows with a persistent evidence readout` (parent `ab7ca7a`)
- Branch: `t3/portfolio-evidence-explorer`
- Date: 2026-11-08T17:33:02Z

## Source change (docs/ excluded)
```
 assets/js/site.js     | 64 ++++++++++++++++++++++++++++++++++++++++++++++++++-
 scripts/charts.lua    | 14 +++++------
 styles.css            | 22 ++++++++++++++++++
 tests/test_browser.py | 38 ++++++++++++++++++++++++++++++
 4 files changed, 130 insertions(+), 8 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 56
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=58.2 METRIC audit_s=47.8 METRIC render_s=19
non-zero: none
```

## Findings delta against the best kept state
Removed (      56):
```
1280	dark	projects/langtons-ant.html	chart linked reading	Steps per second: README laptop against three re-runs (millions)
1280	dark	projects/mailroom-corpus-eda/report.html	chart linked reading	Share of documents that fit each context window
1280	dark	projects/mailroom-ml/report.html	chart linked reading	Per-head subclass macro-F1, Arm B to final run (test split)
1280	dark	projects/mapreduce-reloaded.html	chart linked reading	Speedup with four workers over one, 1 GiB input
1280	dark	projects/natd.html	chart linked reading	Mean exam change by persona (points)
1280	dark	projects/natd/report.html	chart linked reading	Mean exam change by persona (points)
1280	dark	projects/rvl-cdip-classifier.html	chart linked reading	Measured exact-match accuracy before and after each change
1280	light	projects/langtons-ant.html	chart linked reading	Steps per second: README laptop against three re-runs (millions)
1280	light	projects/mailroom-corpus-eda/report.html	chart linked reading	Share of documents that fit each context window
1280	light	projects/mailroom-ml/report.html	chart linked reading	Per-head subclass macro-F1, Arm B to final run (test split)
1280	light	projects/mapreduce-reloaded.html	chart linked reading	Speedup with four workers over one, 1 GiB input
1280	light	projects/natd.html	chart linked reading	Mean exam change by persona (points)
1280	light	projects/natd/report.html	chart linked reading	Mean exam change by persona (points)
1280	light	projects/rvl-cdip-classifier.html	chart linked reading	Measured exact-match accuracy before and after each change
375	dark	projects/langtons-ant.html	chart linked reading	Steps per second: README laptop against three re-runs (millions)
375	dark	projects/mailroom-corpus-eda/report.html	chart linked reading	Share of documents that fit each context window
375	dark	projects/mailroom-ml/report.html	chart linked reading	Per-head subclass macro-F1, Arm B to final run (test split)
375	dark	projects/mapreduce-reloaded.html	chart linked reading	Speedup with four workers over one, 1 GiB input
375	dark	projects/natd.html	chart linked reading	Mean exam change by persona (points)
375	dark	projects/natd/report.html	chart linked reading	Mean exam change by persona (points)
375	dark	projects/rvl-cdip-classifier.html	chart linked reading	Measured exact-match accuracy before and after each change
375	light	projects/langtons-ant.html	chart linked reading	Steps per second: README laptop against three re-runs (millions)
375	light	projects/mailroom-corpus-eda/report.html	chart linked reading	Share of documents that fit each context window
375	light	projects/mailroom-ml/report.html	chart linked reading	Per-head subclass macro-F1, Arm B to final run (test split)
375	light	projects/mapreduce-reloaded.html	chart linked reading	Speedup with four workers over one, 1 GiB input
375	light	projects/natd.html	chart linked reading	Mean exam change by persona (points)
375	light	projects/natd/report.html	chart linked reading	Mean exam change by persona (points)
375	light	projects/rvl-cdip-classifier.html	chart linked reading	Measured exact-match accuracy before and after each change
414	dark	projects/langtons-ant.html	chart linked reading	Steps per second: README laptop against three re-runs (millions)
414	dark	projects/mailroom-corpus-eda/report.html	chart linked reading	Share of documents that fit each context window
414	dark	projects/mailroom-ml/report.html	chart linked reading	Per-head subclass macro-F1, Arm B to final run (test split)
414	dark	projects/mapreduce-reloaded.html	chart linked reading	Speedup with four workers over one, 1 GiB input
414	dark	projects/natd.html	chart linked reading	Mean exam change by persona (points)
414	dark	projects/natd/report.html	chart linked reading	Mean exam change by persona (points)
414	dark	projects/rvl-cdip-classifier.html	chart linked reading	Measured exact-match accuracy before and after each change
414	light	projects/langtons-ant.html	chart linked reading	Steps per second: README laptop against three re-runs (millions)
414	light	projects/mailroom-corpus-eda/report.html	chart linked reading	Share of documents that fit each context window
414	light	projects/mailroom-ml/report.html	chart linked reading	Per-head subclass macro-F1, Arm B to final run (test split)
414	light	projects/mapreduce-reloaded.html	chart linked reading	Speedup with four workers over one, 1 GiB input
414	light	projects/natd.html	chart linked reading	Mean exam change by persona (points)
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `e5c3d67`
```
chart unit tests passed
241 passed, 2 deselected, 611 subtests passed in 79.73s (0:01:19)
All checks passed.
```

## Visual evidence
- [run-65-bars-1280-dark.png](../screenshots/run-65-bars-1280-dark.png)
- [run-65-bars-1280-light.png](../screenshots/run-65-bars-1280-light.png)
- [run-65-bars-375-dark.png](../screenshots/run-65-bars-375-dark.png)
- [run-65-bars-375-light.png](../screenshots/run-65-bars-375-light.png)
- [run-65-bars-forced-colors.png](../screenshots/run-65-bars-forced-colors.png)
- [run-65-bars-print.png](../screenshots/run-65-bars-print.png)
- [run-65-dumbbell-1280-dark.png](../screenshots/run-65-dumbbell-1280-dark.png)
- [run-65-dumbbell-1280-light.png](../screenshots/run-65-dumbbell-1280-light.png)
- [run-65-dumbbell-375-dark.png](../screenshots/run-65-dumbbell-375-dark.png)
- [run-65-dumbbell-375-light.png](../screenshots/run-65-dumbbell-375-light.png)
- [run-65-step-1280-dark.png](../screenshots/run-65-step-1280-dark.png)
- [run-65-step-1280-light.png](../screenshots/run-65-step-1280-light.png)
- [run-65-step-375-dark.png](../screenshots/run-65-step-375-dark.png)
- [run-65-step-375-light.png](../screenshots/run-65-step-375-light.png)
- [run-65-strip-1280-dark.png](../screenshots/run-65-strip-1280-dark.png)
- [run-65-strip-1280-light.png](../screenshots/run-65-strip-1280-light.png)
- [run-65-strip-375-dark.png](../screenshots/run-65-strip-375-dark.png)
- [run-65-strip-375-light.png](../screenshots/run-65-strip-375-light.png)
- [run-65-strip-print.png](../screenshots/run-65-strip-print.png)

Reviewer notes: Opened all 19 run-65 captures: four chart types at 375/1280 in light/dark, one forced-colors state, two print states. Coordinated mark outlines, selected source-row outlines and persistent labelled values agree. NATD retains Type and Sessions; paired F1 shows both endpoints; context chart retains its 70% axis note; benchmark strips retain both machine labels, raw README context and every rerun. More phone height is accepted to expose exact context without horizontal scrolling. No data, axes, tables or project caveats changed. Print hides the new panel/navigation/highlights while retaining charts and tables; forced-colors screenshot retains visible linked outlines/readout. Full gate on e5c3d67: 241 passed, 2 deselected, 611 subtests in 79.73s. Score 56 to 0, no added findings. Collaborative phone row activation selects Enigma and its matching plotted mark without page overflow. Screenshot review also exposes an existing stacked-table caption at about 72px wide; unchanged caption CSS/markup predates this leg. Address it next in a new fixed segment, not by changing this evaluation. Images are public site content. Not checked: other engines, physical devices, screen readers, native PDF pagination, all SVG contrast or external-source reauthentication.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
