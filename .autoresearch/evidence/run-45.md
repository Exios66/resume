# Evidence for run 45

- Commit: `7233502 experiment: Extend labelled table rows to tablet widths` (parent `2ed7a5a`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T08:56:21Z

## Source change (docs/ excluded)
```
 styles.css | 42 +++++++++++++++++++++++-------------------
 1 file changed, 23 insertions(+), 19 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 24
- This run:
```
METRIC polish_defects=4 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=4 METRIC pages=43 METRIC css_kb=53.6 METRIC audit_s=50.7 METRIC render_s=19 
non-zero: {'separator ends a line': 2, 'heading ends with a one-word line': 2}
```

## Findings delta against the best kept state
Removed (      10):
```
768	dark	projects/mailroom-corpus-eda/report.html	crushed cell	3 lines | reports/tables/integrity_report.json
768	dark	projects/mailroom-ml/report.html	crushed cell	4 lines | training/eval/eval_modernbert.py, training/eval/compare_runs.py
768	dark	projects/psychometric-digital-twin/report.html	crushed cell	3 lines | DeepSeek-R1-Distill-Llama-8B
768	dark	projects/rvl-cdip-classifier/report.html	crushed cell	4 lines | website/montecarlo/⁠, reports/monte_carlo/⁠
768	dark	projects/rvl-cdip-classifier/report.html	crushed cell	5 lines | scripts/datasets/, scripts/braintrust/create_braintrust_*_dataset.py, src/image_
768	light	projects/mailroom-corpus-eda/report.html	crushed cell	3 lines | reports/tables/integrity_report.json
768	light	projects/mailroom-ml/report.html	crushed cell	4 lines | training/eval/eval_modernbert.py, training/eval/compare_runs.py
768	light	projects/psychometric-digital-twin/report.html	crushed cell	3 lines | DeepSeek-R1-Distill-Llama-8B
768	light	projects/rvl-cdip-classifier/report.html	crushed cell	4 lines | website/montecarlo/⁠, reports/monte_carlo/⁠
768	light	projects/rvl-cdip-classifier/report.html	crushed cell	5 lines | scripts/datasets/, scripts/braintrust/create_braintrust_*_dataset.py, src/image_
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `7233502`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 42.00s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-45-table-1280-dark.png`
- `.hillclimb-shots/run-45-table-1280-light.png`
- `.hillclimb-shots/run-45-table-375-dark.png`
- `.hillclimb-shots/run-45-table-375-light.png`
- `.hillclimb-shots/run-45-table-768-dark.png`
- `.hillclimb-shots/run-45-table-768-light.png`

Reviewer notes: Opened all six run-45 screenshots at 375, 768, and 1280 px in light and dark. Model names and labels remain readable, tablet rows use the full column, and desktop keeps the comparison grid. No private information visible. Collaborative browser confirmed block rows at 768 and table cells at 1280 with no page overflow. Delta removes exactly ten crushed-cell findings; typography unchanged.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
