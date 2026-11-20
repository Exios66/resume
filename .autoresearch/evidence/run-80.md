# Evidence for run 80

- Commit: `2a939f0 experiment: Project-nav active pill slides like header nav` (parent `d0a5f57`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T09:56:02Z

## Source change (docs/ excluded)
```
 styles.css | 29 +++++++++++++++++++++++++++--
 1 file changed, 27 insertions(+), 2 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=72.8 METRIC audit_s=42.3 METRIC render_s=23 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15105 METRIC gz_projects_index=24969 METRIC gz_case_study=19259 METRIC gz_technical_report=19694 METRIC gz_appendix=11999 METRIC gz_other_page=12452 METRIC gz_styles_css=17270 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `2a939f0`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 98.83s (0:01:38)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-80-ml-nav-1280-light.png`
- `.hillclimb-shots/run-80-ml-nav-375-dark.png`
- `.hillclimb-shots/run-80-nav-1280-dark.png`
- `.hillclimb-shots/run-80-nav-1280-light-mid.png`
- `.hillclimb-shots/run-80-nav-1280-light.png`
- `.hillclimb-shots/run-80-nav-375-dark.png`
- `.hillclimb-shots/run-80-nav-375-light.png`

Reviewer notes: Opened Neuron Atlas and Mailroom-ML project-nav crops: settled Case study active at 375/1280 light and dark is a soft accent pill with inset edge (matching header Projects), not the old filled gradient/glow. Mid-frame 1280 light freezes scaleX mid-slide from the left — narrower soft fill under Case study only, confirming transform slide. Inactive Code/Live demo/report pills unchanged. polish_defects 0; experience_gaps 5. Checks 319 passed / 2 deselected (WebKit recording matrix hang on this host).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
