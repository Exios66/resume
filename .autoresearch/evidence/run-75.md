# Evidence for run 75

- Commit: `950d567 Cancel prior theme-switching cleanup on rapid toggles.` (parent `3bbdaea`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T03:45:32Z

## Source change (docs/ excluded)
```
 partials/layout/scripts.html |  8 +++++-
 tests/node/theme.test.cjs    | 65 ++++++++++++++++++++++++++++++++++++++++----
 2 files changed, 66 insertions(+), 7 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=69.8 METRIC audit_s=44.1 METRIC render_s=22 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14883 METRIC gz_projects_index=24741 METRIC gz_case_study=19027 METRIC gz_technical_report=19470 METRIC gz_appendix=11773 METRIC gz_other_page=12236 METRIC gz_styles_css=16674 METRIC gz_site_js=6897 
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
- Command: `bash autoresearch.checks.sh` on `950d567`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 139.73s (0:02:19)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-75-index-1280-light.png`
- `.hillclimb-shots/run-75-mailroom-chart-1280-dark.png`
- `.hillclimb-shots/run-75-mailroom-chart-1280-light.png`
- `.hillclimb-shots/run-75-mailroom-chart-375-dark.png`
- `.hillclimb-shots/run-75-mailroom-chart-375-light.png`

Reviewer notes: Opened mailroom-ml report chart shots at 1280/375 light and dark: dumbbell marks (dots, links, values) are fully visible after enter — draw-in completed; Contract row readout and linked table still work; teal palette intact; phone shows sideways-scroll hint. Index 1280 light still shows constellation and Explore tiles. polish_defects 0; experience_gaps 5. Chart draw-in landed in 3bbdaea; peer theme-timer cleanup 950d567 is current HEAD. Checks: 319 passed, 2 deselected (WebKit recording matrix hang on this host).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
