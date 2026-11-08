# Evidence for run 42

- Commit: `370b9a2 experiment: stack grids with 12+ char row labels` (parent `b44f240`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T06:24:53Z

## Source change (docs/ excluded)
```
 scripts/tables.lua | 8 ++++----
 1 file changed, 4 insertions(+), 4 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 3
- This run:
```
METRIC polish_defects=2 METRIC axe_points=0 METRIC layout_points=1 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=53.6 METRIC audit_s=29.8 METRIC render_s=20 
non-zero: {'tables wider than screen': 1, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       1):
```
320	light	projects/psychometric-digital-twin/report.html	wide table	main>div.page>table.caption-top | Agent | Target | Band accuracy | Low vs high AUC
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `370b9a2`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 40.92s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-42-mailroom-320-light-check.png`
- `.hillclimb-shots/run-42-psychometric-320-light-auc-band.png`
- `.hillclimb-shots/run-42-psychometric-320-light-auc.png`

Reviewer notes: Lowered the row-label stack threshold from 16 to 12 characters (scripts/tables.lua). The psychometric AUC band table (rows Random forest / DeepSeek v2, columns Target, Band accuracy, Low vs high AUC) now stacks on phones. Screenshots reviewed: AUC table at 320 light - each row is a bold agent name with TARGET / BAND ACCURACY / LOW VS HIGH AUC labelled figures, clean; the per-tier MAE table at 320 light (shot at 'Random forest') unchanged in its run-29 stack; the release gates table on the mailroom-ml appendix at 320 light unchanged (labelled rows, no clipping). Score 3->2: wide tables 2->1, no new findings anywhere (the audit walks all 43 pages). All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
