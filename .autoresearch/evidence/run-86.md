# Evidence for run 86

- Commit: `86ffd4d experiment: Explore heading-to-tile gap matches inter-tile rhythm` (parent `1b718f9`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T10:25:55Z

## Source change (docs/ excluded)
```
 styles.css | 5 ++++-
 1 file changed, 4 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=75.5 METRIC audit_s=48.1 METRIC render_s=26 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15103 METRIC gz_projects_index=24968 METRIC gz_case_study=19255 METRIC gz_technical_report=19693 METRIC gz_appendix=11997 METRIC gz_other_page=12451 METRIC gz_styles_css=17850 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `86ffd4d`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 104.46s (0:01:44)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-86-explore-1280-dark.png`
- `.hillclimb-shots/run-86-explore-1280-light.png`
- `.hillclimb-shots/run-86-explore-375-dark.png`
- `.hillclimb-shots/run-86-explore-375-light.png`
- `.hillclimb-shots/run-86-explore-heading-1280-dark.png`
- `.hillclimb-shots/run-86-explore-heading-1280-light.png`
- `.hillclimb-shots/run-86-explore-heading-375-dark.png`
- `.hillclimb-shots/run-86-explore-heading-375-light.png`

Reviewer notes: Opened Explore heading+tile crops at 375/1280 light and dark. Measured heading-border to first tile = 12px and inter-tile/row gap = 12px at both widths (was 22px heading gap). Settled frames: magenta node + EXPLORE rule, then About/Research/Writing/Resume tiles with even rhythm; 1280 stays a balanced 2x2. No content or palette change. polish_defects 0; experience_gaps 5. Checks 319 passed / 2 deselected.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
