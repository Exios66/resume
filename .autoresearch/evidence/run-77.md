# Evidence for run 77

- Commit: `9ee77e5 experiment: Soft main-content page-enter fade once per navigation` (parent `f4b4602`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T04:17:11Z

## Source change (docs/ excluded)
```
 assets/js/site.js         | 23 +++++++++++++++++++++++
 partials/layout/head.html | 12 +++++++++++-
 styles.css                | 13 +++++++++++++
 3 files changed, 47 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=70.5 METRIC audit_s=43.4 METRIC render_s=23 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15104 METRIC gz_projects_index=24968 METRIC gz_case_study=19257 METRIC gz_technical_report=19694 METRIC gz_appendix=11999 METRIC gz_other_page=12452 METRIC gz_styles_css=16850 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `9ee77e5`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 100.94s (0:01:40)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-77-about-1280-dark.png`
- `.hillclimb-shots/run-77-about-1280-light-entering.png`
- `.hillclimb-shots/run-77-about-1280-light-pending.png`
- `.hillclimb-shots/run-77-about-1280-light.png`
- `.hillclimb-shots/run-77-index-375-dark.png`
- `.hillclimb-shots/run-77-index-375-light.png`

Reviewer notes: Opened pending About shot: header and dotted atmosphere remain, paper card fully hidden (opacity 0) under page-pending. Mid-enter and settled About 1280 light: paper fades in with teal/pink top bar, About title and skills intact. Index 375 light/dark settled: hero, pills, CTAs and Now heading readable; no overflow; constellation omitted on phone as before. Dark About 1280 settled looks correct. polish_defects 0; experience_gaps 5. Checks 319 passed / 2 deselected (WebKit recording matrix hang on this host).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
