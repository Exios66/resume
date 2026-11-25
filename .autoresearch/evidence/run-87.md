# Evidence for run 87

- Commit: `b612eb1 experiment: Align wrapped section-heading lines with the node marker` (parent `7d6b587`)
- Branch: `cursor/craft-harden-1d08`
- Date: 2026-11-20T14:04:17Z

## Source change (docs/ excluded)
```
 projects/natd/appendix.qmd | 2 +-
 styles.css                 | 7 +++++++
 2 files changed, 8 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=75.9 METRIC audit_s=42.4 METRIC render_s=22 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15104 METRIC gz_projects_index=24968 METRIC gz_case_study=19257 METRIC gz_technical_report=19694 METRIC gz_appendix=11999 METRIC gz_other_page=12452 METRIC gz_styles_css=18002 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `b612eb1`
```
chart unit tests passed
321 passed, 705 subtests passed in 106.66s (0:01:46)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-87-appendix-375-dark.png`
- `.hillclimb-shots/run-87-appendix-375-light.png`
- `.hillclimb-shots/run-87-research-1280-dark.png`
- `.hillclimb-shots/run-87-research-1280-light.png`
- `.hillclimb-shots/run-87-research-375-dark.png`
- `.hillclimb-shots/run-87-research-375-light.png`

Reviewer notes: 375 light and dark research: the magenta node sits on line 1 of GRADUATE RESEARCH / AT UW-MADISON, and line 2 starts at the same left edge as line 1, clear of the node; the teal rule stays under the heading. 1280 light and dark: the heading is one line, GRADUATE RESEARCH AT UW-MADISON, node and rule unchanged from the single-line rhythm. Appendix 375 light and dark: WITHHELD and UNTIL AUTHENTICATION share that inset (the first line is short because a non-breaking space keeps until authentication together); PROVENANCE and QUESTIONS STILL OPEN share the same inset. Body text does not collide with the nodes. Dark rules stay visible.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
