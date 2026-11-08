# Evidence for run 43

- Commit: `c83df08 experiment: stack five-plus-column grids with three or more rows` (parent `370b9a2`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T06:28:18Z

## Source change (docs/ excluded)
```
 scripts/tables.lua | 6 +++++-
 1 file changed, 5 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 2
- This run:
```
METRIC polish_defects=1 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=53.6 METRIC audit_s=30.7 METRIC render_s=20 
non-zero: {'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       1):
```
320	light	projects/mailroom-ml/report.html	wide table	main>div.page>table.caption-top | Run | Epochs | Doc-type acc. | Subclass acc. (type correct) | Window ECE
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `c83df08`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 39.96s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-43-mailroom-report-320-light-run.png`
- `.hillclimb-shots/run-43-mailroom-report-375-dark-run.png`

Reviewer notes: New classifier rule: number grids of five or more columns with three or more rows (wide_grid in scripts/tables.lua) stack on phones; their columns cannot get wider than ~55-60 px at 320 regardless of type trimming, so they scrolled or clipped at every narrow screen. The mailroom-ml report run-comparison table (Run, Epochs, Doc-type acc., Subclass acc., Window ECE x 4 runs) is the last one. Screenshots reviewed: run comparison at 320 light and 375 dark: each run is a bold label with EPOCHS / DOC-TYPE ACC. / SUBCLASS ACC. (TYPE CORRECT) / WINDOW ECE labelled figures, clean in both themes. Score 2->1: layout points now 0 across all 43 pages; the audit walk reports no other changed pages. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
