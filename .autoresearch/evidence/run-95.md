# Evidence for run 95

- Commit: `52d01ef experiment: Degen LLMs measured test run; plainer projects-index review note` (parent `0200a26`)
- Branch: `claude/magical-babbage-0xtnx7`
- Date: 2026-11-26T03:54:20Z

## Source change (docs/ excluded)
```
 projects/degen-llms.qmd        | 4 ++--
 projects/degen-llms/report.qmd | 6 +++---
 projects/index.qmd             | 2 +-
 3 files changed, 6 insertions(+), 6 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=78.3 METRIC audit_s=53.0 METRIC render_s=25 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14297 METRIC gz_projects_index=24199 METRIC gz_case_study=19697 METRIC gz_technical_report=19144 METRIC gz_appendix=10999 METRIC gz_other_page=11714 METRIC gz_styles_css=18683 METRIC gz_site_js=7946 
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
- Command: `bash autoresearch.checks.sh` on `52d01ef`
```
chart unit tests passed
332 passed, 926 subtests passed in 131.76s (0:02:11)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-95-degen-stats-375-dark.png`
- `.hillclimb-shots/run-95-index-top-1280-dark.png`
- `.hillclimb-shots/run-95-index-top-1280-light.png`
- `.hillclimb-shots/run-95-index-top-375-light.png`

Reviewer notes: Opened run-95 shots. Projects index 1280 light/dark and 375 light: the three-sentence defensive snapshot disclaimer is now one line (checked against each repository on 26 Nov 2026; WIP tag meaning), category jump links unchanged. Degen 375 dark: stat 419 + 18 with label 'all passing when re-run on 26 November 2026' wraps cleanly. Degen report 1280 light: test table lists 419 passed, 18 Node scripts passed (13 smoke, 5 regression), browser smoke test marked not run; the stale '12 scripts' row and the leftover '7 of 12 superseded' edit note are gone. Sources: own pytest (419 passed) and node runs (18/18 + import check) on degen-llms 80399bf. Not checked: browser smoke test, other engines, devices.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
