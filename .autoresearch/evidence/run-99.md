# Evidence for run 99

- Commit: `af930b6 experiment: About: give the closing résumé button room after Research Training` (parent `e72a531`)
- Branch: `claude/magical-babbage-0xtnx7`
- Date: 2026-11-26T17:09:44Z

## Source change (docs/ excluded)
```
 styles.css | 2 ++
 1 file changed, 2 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=72.7 METRIC audit_s=63.3 METRIC render_s=32 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14296 METRIC gz_projects_index=24199 METRIC gz_case_study=19697 METRIC gz_technical_report=19144 METRIC gz_appendix=10999 METRIC gz_other_page=11715 METRIC gz_styles_css=17699 METRIC gz_site_js=7946 
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
- Command: `bash autoresearch.checks.sh` on `af930b6`
```
chart unit tests passed
332 passed, 926 subtests passed in 164.11s (0:02:44)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-99-about-1280-dark.png`
- `.hillclimb-shots/run-99-about-1280-light.png`
- `.hillclimb-shots/run-99-about-375-dark.png`
- `.hillclimb-shots/run-99-about-375-light.png`

Reviewer notes: Opened run-99 About shots at 1280 light and 375 dark (1280 dark and 375 light also captured). The résumé button now sits 28px below the Research Training list instead of touching it, matching the section rhythm; the button and the list are otherwise unchanged; the card bottom padding still frames it. Not checked: real devices.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
