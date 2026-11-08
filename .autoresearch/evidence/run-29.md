# Evidence for run 29

- Commit: `85fff22 experiment: stack 4+-column grids whose first column holds a 20+ char row label` (parent `4602a06`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:40:07Z

## Source change (docs/ excluded)
```
 scripts/tables.lua | 16 +++++++++++++++-
 1 file changed, 15 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 19
- This run:
```
METRIC polish_defects=9 METRIC axe_points=0 METRIC layout_points=8 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.6 METRIC audit_s=29.3 METRIC render_s=21 
non-zero: {'crushed table cells': 2, 'tables wider than screen': 6, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       8):
```
320	light	projects/mailroom-ml/appendix.html	wide table	main>div.page>table.caption-top | Gate | Actual | Threshold | Result
320	light	projects/natd/report.html	wide table	main>div.page>table.caption-top | Persona group | Sessions | Mean exam change (points) | SD | p
320	light	projects/psychometric-digital-twin/report.html	crushed cell	3 lines | DeepSeek-R1-Distill-Llama-8B
320	light	projects/psychometric-digital-twin/report.html	wide table	main>div.page>table.caption-top | Model | Group MAE | Interpersonal MAE | Group band accuracy | Interpersonal band accuracy
320	light	projects/psychometric-digital-twin/report.html	wide table	main>div.page>table.caption-top | Model | demos | employment | geo | transit
320	light	projects/psychometric-digital-twin/report.html	wide table	main>div.page>table.caption-top | Run | demos | employment | geo | transit
375	light	projects/psychometric-digital-twin/report.html	crushed cell	3 lines | DeepSeek-R1-Distill-Llama-8B
375	light	projects/psychometric-digital-twin/report.html	wide table	main>div.page>table.caption-top | Model | Group MAE | Interpersonal MAE | Group band accuracy | Interpersonal band accuracy
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `85fff22`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 42.91s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-29-natd-320-light-persona.png`
- `.hillclimb-shots/run-29-psychometric-1280-light-model.png`
- `.hillclimb-shots/run-29-psychometric-375-light-model.png`

Reviewer notes: Extended the stack classifier (scripts/tables.lua): a table with 4+ columns whose first column holds a 20+ character row label now stacks on phones (the label column was skipped by the prose-column test before). Screenshots reviewed: psychometric model table at 375 px light - each model name now sits on its own full-width bold line with GROUP MAE / INTERPERSONAL MAE / BAND ACCURACY labels right-aligned, the previously crushed DeepSeek-R1-Distill-Llama-8B name reads on one line; natd persona-group table at 320 px light - Helpful/Deceitful rows stacked, figures on one line, no clip; the same model table at 1280 px unchanged (grid). A noticed artifact (spaces around hyphens in cell text) was measured in the browser: it comes from the table-wide font-variant-numeric: tabular-nums widening hyphens in Inter, not from this change; next experiment scopes tnum to numeric cells. Score 19->9: wide tables 12->6, crushed 6->2, no new findings. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
