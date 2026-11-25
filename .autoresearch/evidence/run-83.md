# Evidence for run 83

- Commit: `b576270 experiment: Hide leftover decorative chrome in print and forced-colors` (parent `0883509`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T10:08:11Z

## Source change (docs/ excluded)
```
 styles.css | 30 +++++++++++++++++++++++++++---
 1 file changed, 27 insertions(+), 3 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=75.0 METRIC audit_s=41.6 METRIC render_s=22 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15104 METRIC gz_projects_index=24968 METRIC gz_case_study=19257 METRIC gz_technical_report=19694 METRIC gz_appendix=11999 METRIC gz_other_page=12454 METRIC gz_styles_css=17626 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `b576270`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 99.96s (0:01:39)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-83-cards-forced-1280.png`
- `.hillclimb-shots/run-83-index-1280-light.png`
- `.hillclimb-shots/run-83-index-375-light.png`
- `.hillclimb-shots/run-83-index-forced-1280.png`
- `.hillclimb-shots/run-83-index-print-1280.png`
- `.hillclimb-shots/run-83-nav-1280-light.png`
- `.hillclimb-shots/run-83-project-forced-1280.png`
- `.hillclimb-shots/run-83-project-print-1280.png`
- `.hillclimb-shots/run-83-search-print-1280.png`

Reviewer notes: Opened print crops: home print drops header/footer, pink node markers, atmosphere and Explore card chrome — content remains as plain reading; Search print keeps title/kicker only (form and suggestion chips hidden as before). Project print keeps All projects + title + lead figure without project-nav pills. Forced-colors home/project/cards: dotted washes and gradient fills gone; Home/Projects active use system Highlight pill; Case study active matches; card borders are CanvasText hairlines without glow or cover sheen. Screen 1280/375 light still looks normal. polish_defects 0; experience_gaps 5. Checks 319 passed / 2 deselected.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
