# Evidence for run 89

- Commit: `e4e4f5d experiment: Break the research degree kicker after the colon on phones` (parent `6b377d3`)
- Branch: `cursor/craft-harden-1d08`
- Date: 2026-11-20T14:15:12Z

## Source change (docs/ excluded)
```
 research.qmd | 2 +-
 styles.css   | 5 +++++
 2 files changed, 6 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=76.1 METRIC audit_s=43.3 METRIC render_s=23 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15103 METRIC gz_projects_index=24968 METRIC gz_case_study=19255 METRIC gz_technical_report=19694 METRIC gz_appendix=11996 METRIC gz_other_page=12449 METRIC gz_styles_css=18086 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `e4e4f5d`
```
chart unit tests passed
321 passed, 705 subtests passed in 107.67s (0:01:47)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-89-research-1280-dark.png`
- `.hillclimb-shots/run-89-research-1280-light.png`
- `.hillclimb-shots/run-89-research-375-dark.png`
- `.hillclimb-shots/run-89-research-375-light.png`

Reviewer notes: 375 light and dark: the degree kicker breaks after the colon, so line 1 is M.S. IN PSYCHOLOGY: and line 2 is DATA SCIENCE IN HUMAN BEHAVIOR, with the date and GPA on their own lines below; the heading node still aligns both lines of GRADUATE RESEARCH AT UW-MADISON. 1280 light and dark: the degree stays one line, M.S. IN PSYCHOLOGY: DATA SCIENCE IN HUMAN BEHAVIOR, and the date and GPA share the next line. No new rag, no split inside Data Science, and the separator dots stay in the clipped gutter.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
