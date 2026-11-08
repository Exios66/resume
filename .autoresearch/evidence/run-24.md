# Evidence for run 24

- Commit: `dfaefc3 experiment: <wbr> after separators in long inline code inside table cells` (parent `13c9afb`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:20:56Z

## Source change (docs/ excluded)
```
 scripts/tables.lua | 41 +++++++++++++++++++++++++++++++++++++++++
 1 file changed, 41 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 22
- This run:
```
METRIC polish_defects=20 METRIC axe_points=0 METRIC layout_points=19 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.1 METRIC audit_s=29.8 METRIC render_s=19 
non-zero: {'crushed table cells': 6, 'tables wider than screen': 13, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       1):
```
375	light	projects/mailroom-ml/appendix.html	crushed cell	clipped 2 lines | training/eval/eval_modernbert.py, --subset test --sample 0
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `dfaefc3`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 43.86s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-24-mailroom-ml-appendix-375-light-cell.png`
- `.hillclimb-shots/run-24-mailroom-ml-appendix-375-light-full.png`
- `.hillclimb-shots/run-24-mailroom-ml-appendix-375-light.png`
- `.hillclimb-shots/run-24-psychometric-320-light-cell.png`
- `.hillclimb-shots/run-24-psychometric-320-light-full.png`
- `.hillclimb-shots/run-24-psychometric-320-light.png`

Reviewer notes: Added <wbr> after path and name separators in long inline code inside table cells via scripts/tables.lua (filter, threshold 14 chars). Screenshots reviewed: mailroom-ml appendix at 375 px light full page - the 'Recorded by' code now wraps as training/eval/ / eval_modernbert.py at separators instead of clipping past its cell; page top unchanged. Psychometric report at 320 px light full page - renders cleanly; the DeepSeek-R1 model-name cell still wraps to 3 lines (severed findings unchanged for it, developing follow-up needed: min-width for code columns). Findings went 22 -> 20: removed the clipped code cell (mailroom-ml appendix, 375) and one more crushed cell; model name (2 viewports) and 'Low-vs-high AUC' header remain. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
