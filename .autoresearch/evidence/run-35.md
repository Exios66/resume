# Evidence for run 35

- Commit: `8a0f281 experiment: label prose row headings in stacked tables` (parent `62c69e7`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:59:17Z

## Source change (docs/ excluded)
```
 scripts/tables.lua | 7 +++++++
 styles.css         | 5 +++++
 2 files changed, 12 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=5 METRIC axe_points=0 METRIC layout_points=4 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=53.1 METRIC audit_s=28.8 METRIC render_s=18
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
- Command: `bash autoresearch.checks.sh` on `8a0f281`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 40.43s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-35-index-1440-light-check.png`
- `.hillclimb-shots/run-35-llm-personas-375-light-labels.png`
- `.hillclimb-shots/run-35-mailroom-appendix-375-dark-labels.png`
- `.hillclimb-shots/run-35-natd-appendix-320-light-labels.png`
- `.hillclimb-shots/run-35-natd-appendix-320-light.png`
- `.hillclimb-shots/run-35-natd-appendix-375-light.png`

Reviewer notes: Fixed the last carried-over review point from PR 103 (CodeAnt nitpick 1): in stacked tables the bold first cell doubles as a row heading, which hid the first column's meaning on the natd appendix 'What the pilot supports' table (hidden header, unlabelled claim). tables.lua now marks tables whose first column carries 40+ character prose (data-prose-rows) and styles.css shows that column's label above the bold row text, the same style as other stacked labels. Screenshots reviewed: natd appendix at 320 light - every claim now sits under SUPPORTED, with NOT SUPPORTED below; llm-personas report at 375 light - ROLE labels above Judge/Architect etc.; digital-mailroom appendix at 375 dark - PUBLIC ON THIS SITE / NOT PUBLISHED labels; index at 1440 light unchanged (the rule is inside the 720 px block). Score equal at 5 (metric-blind readability, kept with screenshot evidence, issue-directed). 8 tables across 7 pages gain label rows. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
