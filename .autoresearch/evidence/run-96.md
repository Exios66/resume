# Evidence for run 96

- Commit: `d3f74ea experiment: Measured test runs replace grep counts: Mailroom-ML, Corpus EDA, Wave appendix, Reloaded report` (parent `52d01ef`)
- Branch: `claude/magical-babbage-0xtnx7`
- Date: 2026-11-26T04:06:00Z

## Source change (docs/ excluded)
```
 projects/mailroom-corpus-eda.qmd        |  2 +-
 projects/mailroom-corpus-eda/report.qmd |  2 +-
 projects/mailroom-ml.qmd                |  2 +-
 projects/mailroom-reloaded/report.qmd   |  2 +-
 projects/wave-laboratory/appendix.qmd   | 10 +++++-----
 tests/python/test_appendices.py         |  2 +-
 6 files changed, 10 insertions(+), 10 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=78.3 METRIC audit_s=56.1 METRIC render_s=29 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14297 METRIC gz_projects_index=24199 METRIC gz_case_study=19697 METRIC gz_technical_report=19144 METRIC gz_appendix=10999 METRIC gz_other_page=11714 METRIC gz_styles_css=18683 METRIC gz_site_js=7946 
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
- Command: `bash autoresearch.checks.sh` on `d3f74ea`
```
chart unit tests passed
332 passed, 926 subtests passed in 141.93s (0:02:21)
All checks passed.
```

## Visual evidence
- `.autoresearch/screenshots/run-96-eda-report-1280-dark.png`
- `.autoresearch/screenshots/run-96-eda-tests-375-light.png`
- `.autoresearch/screenshots/run-96-ml-tests-1280-light.png`
- `.autoresearch/screenshots/run-96-wave-appendix-375-dark.png`

Reviewer notes: Opened run-96 shots. Corpus EDA case study 375 light: Tests bullet states 1,114 tests and the 26 Nov result (1,046 passed, 67 skipped, 1 failed) with a link to the report section; no more 'counted, not run'. EDA report 1280 dark: Tests section replaces the old unpinned 200-test run with the pinned re-run and skip/failure reasons (36 sibling repo, 15 dataset snapshot; review-portal fixture failure). Wave appendix 375 dark: stacked table now Suite/Result with 40 and 932 passed and browser tests '51 defined; not run here'; stale 'Count at the snapshot' header gone. Mailroom-ML 1280 light: test bullet shows 384 passed / 55 skipped core suite. Sources: own runs (Mailroom-Corpus-EDA aed8481 pytest junit; mailroom-ml 01c2272 pytest -m 'not fullcorpus'; wave-laboratory 3211918 vitest). test_appendices pin updated on purpose (25 in 9 files -> 40 passed in 9 files). Not checked: other engines, devices.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
