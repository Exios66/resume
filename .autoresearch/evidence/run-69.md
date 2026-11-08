# Evidence for run 69

- Commit: `e08048a experiment: Visualize MapReduce backup duration with experiment context` (parent `3ff993a`)
- Branch: `t3/portfolio-mapreduce-visuals`
- Date: 2026-11-08T18:15:03Z

## Source change (docs/ excluded)
```
 projects/mapreduce-reloaded.qmd | 19 +++++++++++++++++++
 scripts/charts.lua              | 11 ++++++++---
 styles.css                      |  5 +++++
 tests/test_browser.py           | 42 +++++++++++++++++++++++++++++++++++++----
 tests/test_charts.lua           |  5 +++++
 tests/test_charts.py            |  2 +-
 6 files changed, 76 insertions(+), 8 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 16
- This run:
```
METRIC polish_defects=8 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=8 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=58.5 METRIC audit_s=102.7 METRIC render_s=49
non-zero: {'MapReduce evidence coverage': 8}
```

## Findings delta against the best kept state
Removed (       8):
```
1280	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
1280	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
375	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
375	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
414	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
414	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
768	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
768	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `e08048a`
```
chart unit tests passed
253 passed, 2 deselected, 1 warning, 622 subtests passed in 143.78s (0:02:23)
All checks passed.
```

## Visual evidence
- [run-69-duration-1280-dark.png](../screenshots/run-69-duration-1280-dark.png)
- [run-69-duration-1280-light.png](../screenshots/run-69-duration-1280-light.png)
- [run-69-duration-375-dark.png](../screenshots/run-69-duration-375-dark.png)
- [run-69-duration-375-light.png](../screenshots/run-69-duration-375-light.png)

Reviewer notes: Opened all four final run-69 captures at375/1280 in light/dark, plus the original before states and the two archived initial phone captures. Screenshot checkpoint caught clipped bar ends in the first version; the compact320-unit refinement now shows both bar ends, values and readable ticks on phones without scrolling. Desktop emphasizes the same two durations. Source table, three-run count, fixed-order/not-drift-controlled context, shared-VM scope and numbered source citation remain clear. Source/diff checkpoint reviewed the pinned17.58/11.24 values, zero-based duration axis, default-width charts unchanged, explicit width guard and tests for the intentional compact behavior. Full gate on e08048a:253 passed,2 deselected,1 local test-server teardown warning,622 subtests in143.78s; All checks passed. The warning reports BrokenPipe/Bad file descriptor in request-thread shutdown, not a failed assertion; retain it as a validation limitation. Score16 to8 with no added findings. Collaborative phone row activation selected Backups on and showed11.24s/3runs without page overflow. Public content only. Not checked: upstream benchmark reruns, other engines, physical devices, screen readers, native Linux or PDF pagination.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
