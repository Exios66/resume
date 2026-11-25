# Evidence for run 85

- Commit: `21f688b experiment: Phone header matches page inset with row breathing room` (parent `3260e34`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T10:17:53Z

## Source change (docs/ excluded)
```
 styles.css | 12 +++++++-----
 1 file changed, 7 insertions(+), 5 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=75.3 METRIC audit_s=42.4 METRIC render_s=22 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15104 METRIC gz_projects_index=24969 METRIC gz_case_study=19259 METRIC gz_technical_report=19694 METRIC gz_appendix=11999 METRIC gz_other_page=12452 METRIC gz_styles_css=17751 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `21f688b`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 99.96s (0:01:39)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-85-about-375-light.png`
- `.hillclimb-shots/run-85-header-1280-dark.png`
- `.hillclimb-shots/run-85-header-1280-light.png`
- `.hillclimb-shots/run-85-header-375-dark.png`
- `.hillclimb-shots/run-85-header-375-light.png`
- `.hillclimb-shots/run-85-hero-375-light.png`
- `.hillclimb-shots/run-85-projects-375-dark.png`

Reviewer notes: Opened phone header crops vs prior: at 375 light/dark the header side inset now matches the page (20px), so Writing and the theme toggle sit farther from the screen edge; a 4px row-gap separates the title, primary nav, and Resume/Search rows. Home active pill and brand diamond unchanged. Hero CTA stack from run 84 still reads as primary-full then Resume|Email. At 1280 light/dark the sticky desktop header is unchanged (rule is max-width 720). polish_defects 0; experience_gaps 5. Checks 319 passed / 2 deselected.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
