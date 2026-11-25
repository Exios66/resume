# Evidence for run 78

- Commit: `f3cabe7 experiment: Focus-visible ring eases out without a glow` (parent `9ee77e5`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T04:21:14Z

## Source change (docs/ excluded)
```
 styles.css | 14 ++++++++++++++
 1 file changed, 14 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=71.1 METRIC audit_s=43.7 METRIC render_s=23 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15104 METRIC gz_projects_index=24969 METRIC gz_case_study=19259 METRIC gz_technical_report=19694 METRIC gz_appendix=11998 METRIC gz_other_page=12452 METRIC gz_styles_css=16982 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `f3cabe7`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 100.36s (0:01:40)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-78-about-link-focus-1280-light-mid.png`
- `.hillclimb-shots/run-78-about-link-focus-1280-light.png`
- `.hillclimb-shots/run-78-index-cta-focus-375-dark-mid.png`
- `.hillclimb-shots/run-78-index-cta-focus-375-dark.png`
- `.hillclimb-shots/run-78-index-cta-focus-375-light-mid.png`
- `.hillclimb-shots/run-78-index-cta-focus-375-light.png`
- `.hillclimb-shots/run-78-index-nav-focus-1280-dark-mid.png`
- `.hillclimb-shots/run-78-index-nav-focus-1280-dark.png`
- `.hillclimb-shots/run-78-index-nav-focus-1280-light-mid.png`
- `.hillclimb-shots/run-78-index-nav-focus-1280-light.png`

Reviewer notes: Opened CTA focus shots at 375 light/dark: View projects shows a solid accent outline (white/teal edge on the filled button), not a blurred glow; mid and settled frames differ only by offset. Nav About focus at 1280 light/dark: thin solid accent rectangle around the link, Home active pill unchanged. About page inline project link focus at 1280 light: solid accent outline on the link, body copy and skills layout intact. polish_defects 0; experience_gaps 5. Checks 319 passed / 2 deselected (WebKit recording matrix hang on this host).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
