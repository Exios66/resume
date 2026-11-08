# Evidence for run 64

- Commit: `ab7ca7a experiment: Connect charts to exact source tables with native return navigation` (parent `5353161`)
- Branch: `t3/portfolio-evidence-explorer`
- Date: 2026-11-08T17:28:42Z

## Source change (docs/ excluded)
```
 scripts/charts.lua    | 24 ++++++++++++++++++++----
 styles.css            | 11 +++++++++++
 tests/test_browser.py | 27 +++++++++++++++++++++++++++
 tests/test_charts.lua |  2 +-
 4 files changed, 59 insertions(+), 5 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 112
- This run:
```
METRIC polish_defects=56 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=56 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=56.5 METRIC audit_s=52.7 METRIC render_s=22
non-zero: {'chart focus linked to full source row': 56}
```

## Findings delta against the best kept state
Removed (      56):
```
1280	dark	projects/langtons-ant.html	chart evidence navigation	Steps per second: README laptop against three re-runs (millions)
1280	dark	projects/mailroom-corpus-eda/report.html	chart evidence navigation	Share of documents that fit each context window
1280	dark	projects/mailroom-ml/report.html	chart evidence navigation	Per-head subclass macro-F1, Arm B to final run (test split)
1280	dark	projects/mapreduce-reloaded.html	chart evidence navigation	Speedup with four workers over one, 1 GiB input
1280	dark	projects/natd.html	chart evidence navigation	Mean exam change by persona (points)
1280	dark	projects/natd/report.html	chart evidence navigation	Mean exam change by persona (points)
1280	dark	projects/rvl-cdip-classifier.html	chart evidence navigation	Measured exact-match accuracy before and after each change
1280	light	projects/langtons-ant.html	chart evidence navigation	Steps per second: README laptop against three re-runs (millions)
1280	light	projects/mailroom-corpus-eda/report.html	chart evidence navigation	Share of documents that fit each context window
1280	light	projects/mailroom-ml/report.html	chart evidence navigation	Per-head subclass macro-F1, Arm B to final run (test split)
1280	light	projects/mapreduce-reloaded.html	chart evidence navigation	Speedup with four workers over one, 1 GiB input
1280	light	projects/natd.html	chart evidence navigation	Mean exam change by persona (points)
1280	light	projects/natd/report.html	chart evidence navigation	Mean exam change by persona (points)
1280	light	projects/rvl-cdip-classifier.html	chart evidence navigation	Measured exact-match accuracy before and after each change
375	dark	projects/langtons-ant.html	chart evidence navigation	Steps per second: README laptop against three re-runs (millions)
375	dark	projects/mailroom-corpus-eda/report.html	chart evidence navigation	Share of documents that fit each context window
375	dark	projects/mailroom-ml/report.html	chart evidence navigation	Per-head subclass macro-F1, Arm B to final run (test split)
375	dark	projects/mapreduce-reloaded.html	chart evidence navigation	Speedup with four workers over one, 1 GiB input
375	dark	projects/natd.html	chart evidence navigation	Mean exam change by persona (points)
375	dark	projects/natd/report.html	chart evidence navigation	Mean exam change by persona (points)
375	dark	projects/rvl-cdip-classifier.html	chart evidence navigation	Measured exact-match accuracy before and after each change
375	light	projects/langtons-ant.html	chart evidence navigation	Steps per second: README laptop against three re-runs (millions)
375	light	projects/mailroom-corpus-eda/report.html	chart evidence navigation	Share of documents that fit each context window
375	light	projects/mailroom-ml/report.html	chart evidence navigation	Per-head subclass macro-F1, Arm B to final run (test split)
375	light	projects/mapreduce-reloaded.html	chart evidence navigation	Speedup with four workers over one, 1 GiB input
375	light	projects/natd.html	chart evidence navigation	Mean exam change by persona (points)
375	light	projects/natd/report.html	chart evidence navigation	Mean exam change by persona (points)
375	light	projects/rvl-cdip-classifier.html	chart evidence navigation	Measured exact-match accuracy before and after each change
414	dark	projects/langtons-ant.html	chart evidence navigation	Steps per second: README laptop against three re-runs (millions)
414	dark	projects/mailroom-corpus-eda/report.html	chart evidence navigation	Share of documents that fit each context window
414	dark	projects/mailroom-ml/report.html	chart evidence navigation	Per-head subclass macro-F1, Arm B to final run (test split)
414	dark	projects/mapreduce-reloaded.html	chart evidence navigation	Speedup with four workers over one, 1 GiB input
414	dark	projects/natd.html	chart evidence navigation	Mean exam change by persona (points)
414	dark	projects/natd/report.html	chart evidence navigation	Mean exam change by persona (points)
414	dark	projects/rvl-cdip-classifier.html	chart evidence navigation	Measured exact-match accuracy before and after each change
414	light	projects/langtons-ant.html	chart evidence navigation	Steps per second: README laptop against three re-runs (millions)
414	light	projects/mailroom-corpus-eda/report.html	chart evidence navigation	Share of documents that fit each context window
414	light	projects/mailroom-ml/report.html	chart evidence navigation	Per-head subclass macro-F1, Arm B to final run (test split)
414	light	projects/mapreduce-reloaded.html	chart evidence navigation	Speedup with four workers over one, 1 GiB input
414	light	projects/natd.html	chart evidence navigation	Mean exam change by persona (points)
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `ab7ca7a`
```
chart unit tests passed
237 passed, 2 deselected, 611 subtests passed in 75.46s (0:01:15)
All checks passed.
```

## Visual evidence
- [run-64-navigation-1280-dark.png](../screenshots/run-64-navigation-1280-dark.png)
- [run-64-navigation-1280-light.png](../screenshots/run-64-navigation-1280-light.png)
- [run-64-navigation-375-dark.png](../screenshots/run-64-navigation-375-dark.png)
- [run-64-navigation-375-light.png](../screenshots/run-64-navigation-375-light.png)

Reviewer notes: All four final run-64 screenshots opened: NATD at 375/1280, light/dark. Compact 44px evidence links fit the phone and desktop views; charts, tables and adjacent caveats remain readable and unchanged. Initial screenshot review exposed visible descriptive span text; that same-idea presentation defect was repaired with accessible link names and spacing, then re-rendered/audited and checked on ab7ca7a before decision. Score 112 to 56: all 56 navigation findings removed, no added findings. Full gate: 237 passed, 2 deselected, 611 subtests in 75.46s. Automated no-JS Enter round trips cover all seven chart pages at both widths/themes; collaborative phone pointer activation lands focus on TABLE and returns to FIGCAPTION. Earlier preview clicks saw a stale document and timed out; fresh navigation established the current controls and passed. All screenshots are public site content. Not checked: other browser engines, real devices, screen readers, native PDF pagination or external sources.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
