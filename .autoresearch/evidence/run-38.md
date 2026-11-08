# Evidence for run 38

- Commit: `93c4a03 experiment: remove duplicate back link; reports and appendices keep the Case-study pill` (parent `e68e4f8`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T06:10:04Z

## Source change (docs/ excluded)
```
 projects/langtons-ant/appendix.qmd              |  1 -
 projects/llm-personas/appendix.qmd              |  1 -
 projects/llm-personas/report.qmd                |  1 -
 projects/mailroom-corpus-eda/appendix.qmd       |  1 -
 projects/mailroom-corpus-eda/report.qmd         |  1 -
 projects/mailroom-ml/appendix.qmd               |  1 -
 projects/mailroom-ml/report.qmd                 |  1 -
 projects/mailroom-reloaded/appendix.qmd         |  1 -
 projects/mailroom-reloaded/report.qmd           |  1 -
 projects/natd/appendix.qmd                      |  1 -
 projects/natd/report.qmd                        |  1 -
 projects/psychometric-digital-twin/appendix.qmd |  1 -
 projects/psychometric-digital-twin/report.qmd   |  1 -
 projects/rvl-cdip-classifier/appendix.qmd       |  1 -
 projects/rvl-cdip-classifier/report.qmd         |  1 -
 projects/wave-laboratory/appendix.qmd           |  1 -
 projects/wave-laboratory/report.qmd             |  1 -
 tests/test_appendices.py                        |  9 ++++-----
 tests/test_portfolio_additions.py               | 10 +++++++---
 23 files changed, 11 insertions(+), 29 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=5 METRIC axe_points=0 METRIC layout_points=4 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=53.6 METRIC audit_s=28.4 METRIC render_s=19
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
- Command: `bash autoresearch.checks.sh` on `93c4a03`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 43.11s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-38-aeroglobe-320-light-check.png`
- `.hillclimb-shots/run-38-mailroom-report-375-light-nav.png`

Reviewer notes: Removed the duplicated '← Case study' back link from all 21 report and appendix pages (issue-listed item: reports and appendices keep their way back through the Case-study pill in the project nav; case-study pages keep their '← All projects' back link unchanged). Updated the two tests that pin the removed markup on purpose and said so: tests/test_appendices.py now verifies the Case-study and Technical-report pill targets without requiring a .back link; tests/test_portfolio_additions.py keeps the back-link requirement only for case-study pages. Screenshots reviewed: mailroom-ml report at 375 light shows the pill row and no duplicate back link above the title; aeroglobe at 320 light keeps '← All projects' and its pills. Score equal at 5 (metric-blind cleanup, issue-directed, kept with screenshot evidence). All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
