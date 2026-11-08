# Evidence for run 28

- Commit: `4602a06 experiment: sticky first column with scroll edge on phone number grids` (parent `74ce83b`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:33:51Z

## Source change (docs/ excluded)
```
 styles.css | 8 ++++++++
 1 file changed, 8 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 19
- This run:
```
METRIC polish_defects=19 METRIC axe_points=0 METRIC layout_points=18 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.6 METRIC audit_s=30.0 METRIC render_s=19
non-zero: {'crushed table cells': 6, 'tables wider than screen': 12, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       0):
```
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `4602a06`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 40.96s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-28-mailroom-375-light-grid.png`
- `.hillclimb-shots/run-28-natd-320-dark-grid.png`
- `.hillclimb-shots/run-28-natd-320-light-grid.png`
- `.hillclimb-shots/run-28-natd-375-light-grid.png`

Reviewer notes: Sticky first column on phone number grids (styles.css, <=720px), with a soft right-edge shadow only while the table actually scrolls (site.js data-scrolls). Screenshots reviewed: NATD persona-group grid at 320 light and dark - label column holds while the table scrolls, shadow gives a mild 'more to the right' cue (slightly visible over the Sessions digits, judged acceptable); mailroom-ml appendix cohort grid at 375 light - sticky labels; NATD at 375 light - table fits with no shadow, no artefacts. Score equal at 19: this is a metric-blind readability improvement that issue #106 lists as a next goal (sticky first column on phones); keeping on the strength of the reviewed screenshots. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
