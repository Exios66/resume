# Evidence for run 98

- Commit: `e72a531 experiment: Hero: drop the clip-art constellation, larger darker lede` (parent `123d099`)
- Branch: `claude/magical-babbage-0xtnx7`
- Date: 2026-11-26T17:04:57Z

## Source change (docs/ excluded)
```
 styles.css | 33 +++++----------------------------
 1 file changed, 5 insertions(+), 28 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=72.6 METRIC audit_s=61.2 METRIC render_s=32 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14296 METRIC gz_projects_index=24199 METRIC gz_case_study=19697 METRIC gz_technical_report=19144 METRIC gz_appendix=10999 METRIC gz_other_page=11714 METRIC gz_styles_css=17644 METRIC gz_site_js=7946 
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
- Command: `bash autoresearch.checks.sh` on `e72a531`
```
chart unit tests passed
332 passed, 926 subtests passed in 163.45s (0:02:43)
All checks passed.
```

## Visual evidence
- `.autoresearch/screenshots/run-98-home-1280-dark.png`
- `.autoresearch/screenshots/run-98-home-1280-light.png`
- `.autoresearch/screenshots/run-98-home-375-dark.png`
- `.autoresearch/screenshots/run-98-home-375-light.png`

Reviewer notes: Opened all four run-98 shots. 1280 light/dark: the wireframe constellations beside the name are gone; only the soft glow remains, so the hero reads as name, role, statement, contacts, actions. The lede is darker (ink 78%) and 1.12rem across 5 balanced lines in a 54ch measure. 375 light/dark: the lede is 1.02rem with text-wrap pretty, 8 lines, last line 'someone checks.' rather than a lone word; chips and buttons unchanged. Not checked: other pages (hero is home only), real devices.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
