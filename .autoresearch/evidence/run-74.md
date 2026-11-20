# Evidence for run 74

- Commit: `a9f29cb Add Explore tiles and theme cross-fade on the motion scale` (parent `7a27c57`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T03:38:34Z

## Source change (docs/ excluded)
```
 .10x/metrics.md                   | 13 ++++----
 index.qmd                         | 17 +++++++---
 partials/layout/scripts.html      |  6 ++++
 projects/mapreduce-reloaded.qmd   |  2 +-
 scripts/hillclimb/page_budgets.py |  2 +-
 styles.css                        | 70 +++++++++++++++++++++++++++++++++++++--
 tests/node/theme.test.cjs         | 11 +++++-
 7 files changed, 106 insertions(+), 15 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=66.5 METRIC audit_s=45.6 METRIC render_s=23 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14816 METRIC gz_projects_index=24669 METRIC gz_case_study=18984 METRIC gz_technical_report=19401 METRIC gz_appendix=11717 METRIC gz_other_page=12181 METRIC gz_styles_css=15970 METRIC gz_site_js=6643 
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
- Command: `bash autoresearch.checks.sh` on `a9f29cb`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 111.24s (0:01:51)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-74-index-1280-dark.png`
- `.hillclimb-shots/run-74-index-1280-light.png`
- `.hillclimb-shots/run-74-index-375-dark.png`
- `.hillclimb-shots/run-74-index-375-light.png`

Reviewer notes: Opened index shots at 1280 light/dark: constellation flanks the hero name in both themes, teal/pink brand intact, no overflow. At 375 light/dark the constellation is correctly omitted (under 768px). Motion is CSS-only; reduced-motion and print already hide or kill the animation. polish_defects stayed 0; experience_gaps stayed 5 (repo-style titles). Checks: 319 passed, 2 deselected (WebKit recording matrix known hang on this host); Chromium/Firefox recording still ran.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
