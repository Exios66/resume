# Evidence for run 76

- Commit: `e549275 experiment: Staggered Explore-tile entrance on section enter` (parent `950d567`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T03:55:06Z

## Source change (docs/ excluded)
```
 assets/js/site.js | 12 ++++++++++++
 styles.css        |  4 ++++
 2 files changed, 16 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=70.0 METRIC audit_s=63.8 METRIC render_s=22 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14959 METRIC gz_projects_index=24819 METRIC gz_case_study=19106 METRIC gz_technical_report=19544 METRIC gz_appendix=11850 METRIC gz_other_page=12313 METRIC gz_styles_css=16736 METRIC gz_site_js=7021 
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
- Command: `bash autoresearch.checks.sh` on `e549275`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 119.74s (0:01:59)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-76-explore-1280-dark.png`
- `.hillclimb-shots/run-76-explore-1280-light.png`
- `.hillclimb-shots/run-76-explore-375-dark.png`
- `.hillclimb-shots/run-76-explore-375-light.png`
- `.hillclimb-shots/run-76-index-explore-1280-dark.png`
- `.hillclimb-shots/run-76-index-explore-1280-light.png`
- `.hillclimb-shots/run-76-index-explore-375-dark.png`
- `.hillclimb-shots/run-76-index-explore-375-light.png`

Reviewer notes: Opened Explore section shots at 1280/375 light and dark: 2x2 tiles on desktop and stacked tiles on phone remain readable with Newsreader titles and Inter blurbs; teal system intact; stagger is entrance-only so the settled frame matches the prior Explore layout. polish_defects 0; experience_gaps 5. Checks: 319 passed, 2 deselected (WebKit recording matrix hang on this host).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
