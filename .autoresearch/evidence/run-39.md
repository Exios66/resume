# Evidence for run 39

- Commit: `254d039 Audit segment 4: run the mobile checks at 375 px dark too` (parent `d56240c`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T06:18:03Z

## Source change (docs/ excluded)
```
 autoresearch.audit.cjs | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: none
- This run:
```
METRIC polish_defects=6 METRIC axe_points=0 METRIC layout_points=5 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=53.6 METRIC audit_s=29.6 METRIC render_s=19 
non-zero: {'tables wider than screen': 5, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       0):
```
```
Added (       1):
```
375	dark	projects/mailroom-ml/appendix.html	wide table	main>div.page>table.caption-top | Cohort | Documents | Document-type accuracy | Mean window agreement | Window ECE
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `254d039`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 41.47s
All checks passed.
```

## Visual evidence
- none

Reviewer notes: Segment 4 baseline (the audit commit changes only autoresearch.audit.cjs, no site source). 375 px dark now runs the mobile checks: crushed cells, table overflow, tap targets and small-text. Partially reviewed home screenshots at 1280 and 375 light from the run-23 close-out; dark-theme pages were rendered and audited. New baseline 6 vs the segment 3 best of 5, as expected when a segment widens what is measured: the mailroom-ml cohort table is also wider than the screen at 375 px dark (it was already wide at 375 light and 320). No new tap-target or small-text findings; tables wider: 5, heading widow: 1. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
