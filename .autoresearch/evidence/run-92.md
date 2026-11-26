# Evidence for run 92

- Commit: `7ff574e experiment: MapReduce: core-complete status and the five-run E0-E7 rerun` (parent `ca18fe4`)
- Branch: `claude/magical-babbage-0xtnx7`
- Date: 2026-11-26T03:27:15Z

## Source change (docs/ excluded)
```
 projects/index.qmd                      |  6 +--
 projects/mapreduce-reloaded.qmd         | 88 ++++++++++++++++-----------------
 research.qmd                            |  2 +-
 tests/browser/test_browser.py           | 18 +++----
 tests/python/test_mapreduce_reloaded.py | 39 +++++++++------
 5 files changed, 81 insertions(+), 72 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: none
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=78.3 METRIC audit_s=58.6 METRIC render_s=27 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC charts_without_title=0 METRIC figures_without_alt=0 METRIC pages_over_budget=0 METRIC gz_home=14297 METRIC gz_projects_index=24300 METRIC gz_case_study=19697 METRIC gz_technical_report=19144 METRIC gz_appendix=10999 METRIC gz_other_page=11714 METRIC gz_styles_css=18683 METRIC gz_site_js=7946 
non-zero: none
```

## Findings delta against the best kept state
Removed (16):
```
1280	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
1280	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
1280	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
1280	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
375	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
375	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
375	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
375	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
414	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
414	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
414	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
414	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
768	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
768	dark	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
768	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	paired effect interval across no change, with limits
768	light	projects/mapreduce-reloaded.html	MapReduce evidence coverage	slow-worker duration with experiment limits
```
Added (0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `7ff574e`
```
chart unit tests passed
332 passed, 926 subtests passed in 178.44s (0:02:58)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-92-index-card-1280-light.png`
- `.hillclimb-shots/run-92-mapreduce-backups-1280-dark.png`
- `.hillclimb-shots/run-92-mapreduce-eval-1280-light.png`
- `.hillclimb-shots/run-92-mapreduce-eval-375-dark.png`
- `.hillclimb-shots/run-92-mapreduce-top-1280-dark.png`
- `.hillclimb-shots/run-92-mapreduce-top-1280-light.png`
- `.hillclimb-shots/run-92-mapreduce-top-375-dark.png`
- `.hillclimb-shots/run-92-mapreduce-top-375-light.png`

Reviewer notes: Opened all 8 run-92 shots. Top 375/1280 light+dark: kicker reads CORE COMPLETE, WIP tag gone, Status box is three lines of plain status with no commit hashes, stats 24/4/3.7x with short labels. Eval 1280 light: five-row summary table incl. E7 LATE row, scaling chart 3.7/3.1/2x with ideal 4x line. 375 dark: failure-cost chart now seconds (7.9/12.8/26.2/1.2 s) fits phone width, readout and table legible. Backups 1280 dark: 17.9 vs 11.36 s bars, five runs / took turns / one shared VM text, interval prose. Index card 1280 light: Core complete kicker, no WIP tag, body names LATE and eight-experiment evaluation. All values cross-checked against bench/README.md and docs/report.md on MapReduce-Reloaded main 6d93f33 (system at 8f0ddb9, E0 at 3a907de). Not checked: Firefox/WebKit visuals beyond the targeted suite cases, real devices, screen readers.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
