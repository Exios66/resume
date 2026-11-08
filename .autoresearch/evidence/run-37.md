# Evidence for run 37

- Commit: `e68e4f8 experiment: compact phone header nav` (parent `f582dc2`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T06:05:45Z

## Source change (docs/ excluded)
```
 styles.css | 9 ++++++++-
 1 file changed, 8 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=5 METRIC axe_points=0 METRIC layout_points=4 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=53.6 METRIC audit_s=27.2 METRIC render_s=20
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
- Command: `bash autoresearch.checks.sh` on `e68e4f8`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 41.15s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-37-index-320-light-header.png`
- `.hillclimb-shots/run-37-index-375-light-header.png`
- `.hillclimb-shots/run-37-mailroom-375-dark-header.png`

Reviewer notes: Compact phone header (styles.css, <=720px): the site title takes its own flex line, nav links keep their 44 px touch height but drop horizontal padding to 8 px at .84rem, and the theme toggle rides the last link row. First attempt shrank touch heights to 40 px and failed the site's own browser test that pins 44 px nav targets; fixed inside the same run with git commit --amend (44 px restored), rendered and re-audited. Screenshots reviewed: index at 375 light - title row + two link rows with the toggle next to Search instead of its own row; index at 320 light - same shape, no overlap; score equal at 5 (metric-blind, backlog item 5 from the hand-off, kept on screenshot evidence with 44 px targets intact and all browser tests passing).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
