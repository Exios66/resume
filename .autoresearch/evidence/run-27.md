# Evidence for run 27

- Commit: `74ce83b experiment: stack tables whose prose column reaches 45 characters` (parent `35d0854`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:30:19Z

## Source change (docs/ excluded)
```
 scripts/tables.lua | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 20
- This run:
```
METRIC polish_defects=19 METRIC axe_points=0 METRIC layout_points=18 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.1 METRIC audit_s=29.8 METRIC render_s=22 
non-zero: {'crushed table cells': 6, 'tables wider than screen': 12, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       1):
```
320	light	projects/natd/report.html	wide table	main>div.page>table.caption-top | Cluster | Sessions | Mean change (points) | Persona mix
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `74ce83b`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 43.26s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-27-natd-320-dark-clusters.png`
- `.hillclimb-shots/run-27-natd-320-light-clusters.png`
- `.hillclimb-shots/run-27-natd-375-light-clusters.png`

Reviewer notes: Lowered the stack classifier's prose-column threshold from 60 to 45 characters in scripts/tables.lua. The NATD clusters table (Persona mix column, up to 48 chars) now stacks on phones instead of being a 4-column scrolling grid. Screenshots reviewed at 320 px light and dark and 375 px light: each cluster row is a bold name with labelled SESSIONS / MEAN CHANGE (POINTS) / PERSONA MIX rows, the 48-character persona-mix text fits on one or two lines with no clipping, no horizontal scroll, both themes look right. Score 20->19: wide tables 13->12, no new findings. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
