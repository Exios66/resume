# Evidence for run 40

- Commit: `7ee36e0 experiment: stack grids of at most two rows and four or more columns` (parent `254d039`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T06:20:48Z

## Source change (docs/ excluded)
```
 scripts/tables.lua | 9 ++++++++-
 1 file changed, 8 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 6
- This run:
```
METRIC polish_defects=3 METRIC axe_points=0 METRIC layout_points=2 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=53.6 METRIC audit_s=28.4 METRIC render_s=20 
non-zero: {'tables wider than screen': 2, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       3):
```
320	light	projects/mailroom-ml/appendix.html	wide table	main>div.page>table.caption-top | Cohort | Documents | Document-type accuracy | Mean window agreement | Window ECE
375	dark	projects/mailroom-ml/appendix.html	wide table	main>div.page>table.caption-top | Cohort | Documents | Document-type accuracy | Mean window agreement | Window ECE
375	light	projects/mailroom-ml/appendix.html	wide table	main>div.page>table.caption-top | Cohort | Documents | Document-type accuracy | Mean window agreement | Window ECE
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `7ee36e0`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 40.80s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-40-mailroom-appendix-320-light-cohort.png`
- `.hillclimb-shots/run-40-mailroom-appendix-375-dark-cohort.png`

Reviewer notes: Stacking classifier rule: tables with at most two body rows and four or more columns (squat_grid in scripts/tables.lua) stack on phones, so a two-row grid reads as two blocks of labelled figures rather than a scrolled grid. The mailroom-ml cohort table (Single-window / Multi-window x Documents, Doc-type accuracy, Mean window agreement, Window ECE) is the target; the only other table matching, the natd persona-group table, was already stacked. Screenshots reviewed: cohort table at 320 light and 375 dark under the new segment-4 audit: cohort names bold, figures labelled and right-aligned, no clipping, both themes clean. Score 6->3 on the new baseline: wide tables 5->2, no new findings; the previous grid overflowed at 320 light, 375 light and 375 dark. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
