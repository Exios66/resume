# Evidence for run 33

- Commit: `359e50a experiment: split band shares into one row per band` (parent `bf549ab`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:50:30Z

## Source change (docs/ excluded)
```
 projects/psychometric-digital-twin/report.qmd | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=5 METRIC axe_points=0 METRIC layout_points=4 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.9 METRIC audit_s=28.7 METRIC render_s=21 
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
- Command: `bash autoresearch.checks.sh` on `359e50a`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 40.76s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-33-psychometric-320-light-bands.png`
- `.hillclimb-shots/run-33-psychometric-375-dark-bands.png`

Reviewer notes: Split the psychometric band-share row into one row per band: 'Low band (13 or less) / Moderate band (14-19) / High band (20 or more)', each with its own Group CA and Interpersonal CA share; the audit-blind change issue #106 lists as goal 3. Screenshots reviewed at 320 px light and 375 px dark: three labelled band rows with figures in their own columns instead of one cell carrying 'Low (13 or less) / moderate (14-19) / high (20 or more)' and slashes of percentages; no cell wraps more than two lines, both themes clean. Score equal at 5 (metric-blind, kept on screenshot evidence per the owner's note). All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
