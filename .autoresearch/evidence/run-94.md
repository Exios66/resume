# Evidence for run 94

- Commit: `0200a26 experiment: AeroGlobe: verified live features, measured tests, one-line status instead of a date wall` (parent `648a4a0`)
- Branch: `claude/magical-babbage-0xtnx7`
- Date: 2026-11-26T03:42:54Z

## Source change (docs/ excluded)
```
 projects/aeroglobe.qmd                   | 18 +++++++-----------
 tests/python/test_portfolio_additions.py | 15 ++++++++-------
 2 files changed, 15 insertions(+), 18 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=78.3 METRIC audit_s=52.4 METRIC render_s=26 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14297 METRIC gz_projects_index=24300 METRIC gz_case_study=19697 METRIC gz_technical_report=19144 METRIC gz_appendix=10999 METRIC gz_other_page=11714 METRIC gz_styles_css=18683 METRIC gz_site_js=7946 
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
- Command: `bash autoresearch.checks.sh` on `0200a26`
```
chart unit tests passed
332 passed, 926 subtests passed in 136.42s (0:02:16)
All checks passed.
```

## Visual evidence
- `.autoresearch/screenshots/run-94-aeroglobe-built-1280-light.png`
- `.autoresearch/screenshots/run-94-aeroglobe-top-1280-dark.png`
- `.autoresearch/screenshots/run-94-aeroglobe-top-1280-light.png`
- `.autoresearch/screenshots/run-94-aeroglobe-top-375-dark.png`
- `.autoresearch/screenshots/run-94-aeroglobe-top-375-light.png`

Reviewer notes: Opened run-94 shots (top 375/1280 light+dark, built 1280 light). Intro is two sentences instead of a paragraph of snapshot dates; caveat is one short status naming the 8 Nov deploy, labeled sample day and no real historical day, with one source link; stats 451 tests / 4 stages / 8,091 TS lines read cleanly and wrap on phone. Built list now includes route search, history panel, time-zone overlay, logbook (verified on the live site: Timeline, Time zones, Logbook, Search flights controls present on 26 Nov) plus icon LOD and the honest 54-of-56-files test note. Sources: own vitest run on aeroglobe a011ff7 (451 passed, 2 files need a release-hosted tz file, HTTP 401), gh-pages e2efcb1 deploy 2026-11-08, git ls-tree line count. Not checked: other engines, real devices.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
