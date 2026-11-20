# Evidence for run 88

- Commit: `6b377d3 experiment: Center timeline nodes on the rail` (parent `b612eb1`)
- Branch: `cursor/craft-harden-1d08`
- Date: 2026-11-20T14:08:22Z

## Source change (docs/ excluded)
```
 styles.css | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=75.9 METRIC audit_s=42.8 METRIC render_s=22 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15104 METRIC gz_projects_index=24969 METRIC gz_case_study=19256 METRIC gz_technical_report=19694 METRIC gz_appendix=11999 METRIC gz_other_page=12453 METRIC gz_styles_css=18000 METRIC gz_site_js=7199 
non-zero: none
```

## Findings delta against the best kept state
Removed (0):
```
```
Added (0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `6b377d3`
```
chart unit tests passed
321 passed, 705 subtests passed in 105.92s (0:01:45)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-88-timeline-1280-dark.png`
- `.hillclimb-shots/run-88-timeline-1280-light.png`
- `.hillclimb-shots/run-88-timeline-375-dark.png`
- `.hillclimb-shots/run-88-timeline-375-light.png`

Reviewer notes: 375 light and dark mailroom report: teal timeline disks sit on the gradient rail, one per entry, vertically with the first line of Run 3, Arm A, Arm B, Final run and Decode sweep; the rail runs through the disk, not beside it. 1280 light and dark: the same five disks sit on the rail through the full iteration list, and the Iteration history heading node stays clear of the rail. Measured dot center minus rail center is 0px at both 375 and 1280 (was -3px). Text does not collide with the nodes.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
