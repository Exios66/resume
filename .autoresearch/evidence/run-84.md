# Evidence for run 84

- Commit: `3260e34 experiment: Phone hero CTAs: primary full row, secondary pair below` (parent `2b3cc57`)
- Branch: `cursor/design-motion-1d08`
- Date: 2026-11-20T10:14:05Z

## Source change (docs/ excluded)
```
 styles.css                    | 8 +++++---
 tests/python/test_qa_fixes.py | 7 +++++--
 2 files changed, 10 insertions(+), 5 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=75.1 METRIC audit_s=42.4 METRIC render_s=22 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=15104 METRIC gz_projects_index=24968 METRIC gz_case_study=19259 METRIC gz_technical_report=19694 METRIC gz_appendix=11999 METRIC gz_other_page=12452 METRIC gz_styles_css=17676 METRIC gz_site_js=7199 
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
- Command: `bash autoresearch.checks.sh` on `3260e34`
```
chart unit tests passed
319 passed, 2 deselected, 705 subtests passed in 100.18s (0:01:40)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-84-actions-375-dark.png`
- `.hillclimb-shots/run-84-actions-375-light.png`
- `.hillclimb-shots/run-84-actions-414-light.png`
- `.hillclimb-shots/run-84-cta-1280-dark.png`
- `.hillclimb-shots/run-84-cta-1280-light.png`
- `.hillclimb-shots/run-84-cta-375-dark.png`
- `.hillclimb-shots/run-84-cta-375-light.png`

Reviewer notes: Opened hero CTA crops: at 375 light/dark View projects sits alone full-width; Resume and Email me share a second row with equal widths and a 10px gutter — no longer a single edge-to-edge trio. Contact chips and Now heading unchanged. At 1280 light/dark the three CTAs remain one centered row as before. polish_defects 0; experience_gaps 5. Checks 319 passed / 2 deselected. Updated test_qa_fixes to pin the intentional phone stack.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
