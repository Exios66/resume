# Evidence for run 32

- Commit: `bf549ab experiment: Low vs high AUC header text` (parent `2ef68af`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:48:14Z

## Source change (docs/ excluded)
```
 projects/psychometric-digital-twin/report.qmd | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 7
- This run:
```
METRIC polish_defects=5 METRIC axe_points=0 METRIC layout_points=4 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.9 METRIC audit_s=29.9 METRIC render_s=21
non-zero: {'tables wider than screen': 4, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       2):
```
320	light	projects/psychometric-digital-twin/report.html	crushed cell	4 lines | Low-vs-high AUC
320	light	projects/psychometric-digital-twin/report.html	wide table	main>div.page>table.caption-top | Agent | Target | Band accuracy | Low-vs-high AUC
```
Added (       1):
```
320	light	projects/psychometric-digital-twin/report.html	wide table	main>div.page>table.caption-top | Agent | Target | Band accuracy | Low vs high AUC
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `bf549ab`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 42.99s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-32-psychometric-320-light-auc.png`

Reviewer notes: Renamed the psychometric AUC table header from 'Low-vs-high AUC' to 'Low vs high AUC' (same meaning; the hyphenated compound was one unbreakable token that wrapped badly in its narrow column). Screenshot reviewed at 320 px light with the sticky first column: the four-row grid, agent and target cells and the charts below read as before; the AUC column now wraps into the short words 'Low / vs / high / AUC' instead of lines fragmented from an 11-character token; the table still overflows at 320 px, one of the four remaining wide grids where content clips at the screen edge until swiped. The crushed-cell finding (2 pts) is gone: score 7->5. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
