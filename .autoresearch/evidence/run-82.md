# Evidence for run 82

- Commit: `0883509 experiment: Search and contact chips hover like Explore tiles` (parent `7dd8e4f`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T10:03:45Z

## Source change (docs/ excluded)
```
 styles.css | 22 ++++++++++++++++++++--
 1 file changed, 20 insertions(+), 2 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=74.1 METRIC audit_s=41.8 METRIC render_s=21 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15104 METRIC gz_projects_index=24969 METRIC gz_case_study=19259 METRIC gz_technical_report=19694 METRIC gz_appendix=11999 METRIC gz_other_page=12453 METRIC gz_styles_css=17538 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `0883509`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 98.74s (0:01:38)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-82-contact-hover-375-light.png`
- `.hillclimb-shots/run-82-search-1280-dark.png`
- `.hillclimb-shots/run-82-search-1280-light.png`
- `.hillclimb-shots/run-82-search-375-dark.png`
- `.hillclimb-shots/run-82-search-375-light.png`
- `.hillclimb-shots/run-82-search-focus-1280-light.png`
- `.hillclimb-shots/run-82-search-hover-1280-dark.png`
- `.hillclimb-shots/run-82-search-hover-1280-light.png`
- `.hillclimb-shots/run-82-search-hover-375-light.png`

Reviewer notes: Opened search suggestion crops: settled Try chips at 375/1280 light and dark keep soft teal wash and thin inset edge. Hover on calibration (1280 light/dark) strengthens the inset border to Explore-like accent mix and lifts 1px — no outer glow. Focus 1280 light adds a solid accent outline around calibration. Contact hover 375 light: LinkedIn link chip gets the stronger border/fill while the non-link location chip stays muted. polish_defects 0; experience_gaps 5. Checks 319 passed / 2 deselected.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
