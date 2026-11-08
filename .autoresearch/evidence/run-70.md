# Evidence for run 70

- Commit: `211e012 experiment: Show MapReduce paired uncertainty around no change` (parent `e08048a`)
- Branch: `t3/portfolio-mapreduce-visuals`
- Date: 2026-11-08T18:27:39Z

## Source change (docs/ excluded)
```
 projects/mapreduce-reloaded.qmd | 17 ++++++++++++
 scripts/charts.lua              | 57 +++++++++++++++++++++++++++++++++++++++--
 styles.css                      | 14 ++++++++++
 tests/test_browser.py           | 32 +++++++++++++++++++++++
 tests/test_charts.lua           | 24 +++++++++++++++++
 tests/test_charts.py            |  2 +-
 6 files changed, 143 insertions(+), 3 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 8
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=59.2 METRIC audit_s=91.4 METRIC render_s=53
non-zero: none
```

## Findings delta against the best kept state
Removed (       8):
```
1280	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
1280	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
375	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
375	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
414	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
414	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
768	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
768	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `211e012`
```
chart unit tests passed
257 passed, 2 deselected, 634 subtests passed in 229.57s (0:03:49)
All checks passed.
```

## Visual evidence
- [run-70-interval-1280-dark.png](../screenshots/run-70-interval-1280-dark.png)
- [run-70-interval-1280-light.png](../screenshots/run-70-interval-1280-light.png)
- [run-70-interval-375-dark.png](../screenshots/run-70-interval-375-dark.png)
- [run-70-interval-375-light.png](../screenshots/run-70-interval-375-light.png)
- [run-70-interval-768-dark.png](../screenshots/run-70-interval-768-dark.png)
- [run-70-interval-768-light.png](../screenshots/run-70-interval-768-light.png)
- [run-70-interval-forced-colors.png](../screenshots/run-70-interval-forced-colors.png)
- [run-70-interval-print.png](../screenshots/run-70-interval-print.png)

Reviewer notes: All eight final run-70 images opened:375/768/1280 light/dark, forced-colors, print; initial phone state also reviewed. The compact plot shows mean, both bounds and dashed zero together, with sign/zero-cost interpretation before the figure. No misleading normal-phone scroll cue; 320px guidance retained. Source table/readout retains all three values and ten-pair count; native print retains data/plot and hides interactive decoration. Forced-colors interval remains visible. Source/diff checkpoint reviewed exact paired values, bounds-containing-mean and zero-containing-domain guards, one-estimate support, source-row identity, escaped markup, unchanged existing chart behavior and tests. Full gate on211e012:257 passed,2 deselected,634 subtests in229.57s; no warnings, All checks passed. Score8 to0, no added findings. Original interval gate was interrupted for same-idea visual refinement and is not a full pass claim. Collaborative phone source-row activation matched all values, chart fit without scrolling, citation2 reachedfn2 inside main and backlink returned focus tofnref2. Public content only; no private data. Not checked: upstream benchmark/statistical reproduction, full SVG contrast, other engines, physical devices, screen readers, native Linux, native PDF pagination or printing.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
