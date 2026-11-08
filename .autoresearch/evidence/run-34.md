# Evidence for run 34

- Commit: `62c69e7 experiment: rlv-cdip appendix v0 cell names its slice` (parent `359e50a`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:55:23Z

## Source change (docs/ excluded)
```
 projects/rvl-cdip-classifier/appendix.qmd | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=5 METRIC axe_points=0 METRIC layout_points=4 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.9 METRIC audit_s=29.3 METRIC render_s=19 
non-zero: {'tables wider than screen': 4, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       0):
```
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `62c69e7`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 41.99s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-34-rvl-appendix-375-light-v0.png`
- `.hillclimb-shots/run-34-rvl-appendix-375-light.png`

Reviewer notes: Fixed the carried-over review point from PR 103 (CodeAnt nitpick 2): the rvl-cdip appendix 'Prompt history' row for v0 held '66.1% on 800' under a 'Tuning-slice result' column, so on phones the stacked row read as a tuning-slice score that names a different slice. The cell now reads '66.1% on the 800-image control slice (529 of 800), not the tuning slice'; the 66.1% number and its 529/800 provenance are exactly those in the RVL-CDIP report table (v0, 800-image slice, Control), nothing invented. Screenshot reviewed at 375 px light: the stacked row shows the explanatory cell under TUNING-SLICE RESULT with no contradiction. Score equal at 5 (content-correctness, metric-blind, kept with screenshot evidence). All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
