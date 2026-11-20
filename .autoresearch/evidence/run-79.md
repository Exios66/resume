# Evidence for run 79

- Commit: `3bbe8e9 experiment: Active nav indicator slides in via transform` (parent `82a6326`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T04:26:35Z

## Source change (docs/ excluded)
```
 styles.css | 36 +++++++++++++++++++++++++++++++++---
 1 file changed, 33 insertions(+), 3 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=71.9 METRIC audit_s=45.5 METRIC render_s=23 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15104 METRIC gz_projects_index=24969 METRIC gz_case_study=19258 METRIC gz_technical_report=19695 METRIC gz_appendix=11999 METRIC gz_other_page=12453 METRIC gz_styles_css=17154 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `3bbe8e9`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 103.12s (0:01:43)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-79-nav-about-1280-dark.png`
- `.hillclimb-shots/run-79-nav-about-1280-light.png`
- `.hillclimb-shots/run-79-nav-home-1280-dark.png`
- `.hillclimb-shots/run-79-nav-home-1280-light-mid.png`
- `.hillclimb-shots/run-79-nav-home-1280-light.png`
- `.hillclimb-shots/run-79-nav-home-375-dark.png`
- `.hillclimb-shots/run-79-nav-home-375-light.png`
- `.hillclimb-shots/run-79-nav-projects-1280-light.png`

Reviewer notes: Opened header crops: settled Home active at 1280/375 light and dark shows the soft accent pill and inset edge behind Home only; About and Projects pages move that same pill to the matching link. Mid-frame Home 1280 light freezes scaleX mid-slide from the left origin — narrower indicator than the settled pill, confirming transform rather than a color pop. Brand teal/pink and Search/theme controls unchanged. polish_defects 0; experience_gaps 5. Checks 319 passed / 2 deselected (WebKit recording matrix hang on this host).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
