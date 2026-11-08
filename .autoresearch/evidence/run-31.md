# Evidence for run 31

- Commit: `2ef68af experiment: stack grids with 16+ char row labels` (parent `d7beb51`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:45:25Z

## Source change (docs/ excluded)
```
 scripts/tables.lua | 8 ++++----
 1 file changed, 4 insertions(+), 4 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 9
- This run:
```
METRIC polish_defects=7 METRIC axe_points=0 METRIC layout_points=6 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.9 METRIC audit_s=30.2 METRIC render_s=18 
non-zero: {'crushed table cells': 2, 'tables wider than screen': 4, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       2):
```
320	light	projects/psychometric-digital-twin/report.html	wide table	main>div.page>table.caption-top | Group | n | MAE at demos | Mean signed error at demos | MAE at transit | Mean signed error at transi
375	light	projects/psychometric-digital-twin/report.html	wide table	main>div.page>table.caption-top | Group | n | MAE at demos | Mean signed error at demos | MAE at transit | Mean signed error at transi
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `2ef68af`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 41.80s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-31-psychometric-320-light-group.png`
- `.hillclimb-shots/run-31-psychometric-375-light-group.png`

Reviewer notes: Lowered the row-label stacking threshold from 20 to 16 characters (scripts/tables.lua). The psychometric-digital-twin 6-column group table (first column 'Other employment' = 16 chars) now stacks on phones. Screenshots reviewed at 320 px and 375 px light: each group (Full-time, Part-time, Other employment) is a bold heading with N / MAE AT DEMOS / MEAN SIGNED ERROR AT DEMOS / MAE AT TRANSIT / MEAN SIGNED ERROR AT TRANSIT labelled rows, figures right-aligned, nothing clipped or overflowing; the 320 px label column no longer squeezes 6 columns into ~285 px. Score 9->7: wide tables 6->4, no new findings. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
