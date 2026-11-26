# Evidence for run 93

- Commit: `648a4a0 experiment: Measured test counts for Wave Laboratory and Mailroom Reloaded; current Neuron Atlas provenance` (parent `7ff574e`)
- Branch: `claude/magical-babbage-0xtnx7`
- Date: 2026-11-26T03:37:02Z

## Source change (docs/ excluded)
```
 projects/mailroom-reloaded.qmd        |  2 +-
 projects/mailroom-reloaded/report.qmd | 12 ++++++++++--
 projects/neuron-atlas.qmd             |  2 +-
 projects/wave-laboratory.qmd          |  4 ++--
 projects/wave-laboratory/report.qmd   | 10 +++++-----
 5 files changed, 19 insertions(+), 11 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 5
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=78.3 METRIC audit_s=51.9 METRIC render_s=26 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14297 METRIC gz_projects_index=24300 METRIC gz_case_study=19697 METRIC gz_technical_report=19144 METRIC gz_appendix=10999 METRIC gz_other_page=11714 METRIC gz_styles_css=18683 METRIC gz_site_js=7946 
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
- Command: `bash autoresearch.checks.sh` on `648a4a0`
```
chart unit tests passed
332 passed, 926 subtests passed in 136.40s (0:02:16)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-93-mrl-report-1280-light.png`
- `.hillclimb-shots/run-93-mrl-stats-1280-dark.png`
- `.hillclimb-shots/run-93-mrl-stats-375-dark.png`
- `.hillclimb-shots/run-93-neuron-limits-1280-dark.png`
- `.hillclimb-shots/run-93-wave-report-375-light.png`
- `.hillclimb-shots/run-93-wave-stats-1280-light.png`
- `.hillclimb-shots/run-93-wave-stats-375-light.png`

Reviewer notes: Opened run-93 shots. Wave stats 375/1280 light: third stat reads 972 tests passing on main on 26 Nov (932 unit, 40 validation); paragraph names 11 hulls, says live demo predates clouds/sun shafts/hull-water contact, keeps Stokes/cnoidal/Boussinesq as planned. Wave report 375: test table is run results (932/40) plus 51 Playwright definitions labelled as definitions. Mailroom Reloaded stats 375/1280 dark: 1,844 stat label wraps cleanly. Report 1280 light: new 2026-11-26 re-run table above the historical 2026-10-11 table. Neuron Atlas 1280 dark: provenance paragraph no longer names internal issue #89, keeps branch link, says only later change is one browser test. Sources: own runs of vitest (wave-laboratory 3211918), uv run pytest + ruff + node --test (mailroom-reloaded 8c35413), git diff a580008..7d15c18 (LLM_Viz). Not checked: Wave Lab Playwright suite, mailroom-reloaded live/docker tests, other engines, real devices.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
