# Evidence for run 73

- Commit: `e128dee experiment: Per-project social cards from cover motifs` (parent `a5aa25d`)
- Branch: `cursor/portfolio-status-wip-1d08`
- Date: 2026-11-20T00:03:19Z

## Source change (docs/ excluded)
```
 projects/mailroom-reloaded/appendix.qmd         |   2 +
 projects/mailroom-reloaded/report.qmd           |   2 +
 projects/mapreduce-reloaded.qmd                 |   4 +-
 projects/natd.qmd                               |   2 +
 projects/natd/appendix.qmd                      |   2 +
 projects/natd/report.qmd                        |   2 +
 projects/neuron-atlas.qmd                       |   2 +
 projects/psychometric-digital-twin.qmd          |   2 +
 projects/psychometric-digital-twin/appendix.qmd |   2 +
 projects/psychometric-digital-twin/report.qmd   |   2 +
 projects/rvl-cdip-classifier.qmd                |   2 +
 projects/rvl-cdip-classifier/appendix.qmd       |   2 +
 projects/rvl-cdip-classifier/report.qmd         |   2 +
 projects/wave-laboratory.qmd                    |   2 +
 projects/wave-laboratory/appendix.qmd           |   2 +
 projects/wave-laboratory/report.qmd             |   2 +
 scripts/build/make-og.py                        | 215 ++++++++++++++++++++++--
 tests/python/test_render_scripts.py             |  71 +++++---
 tests/python/test_social_cards.py               |  55 ++++++
 52 files changed, 382 insertions(+), 31 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 19
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=65.6 METRIC audit_s=43.4 METRIC render_s=23 METRIC experience_gaps=5 METRIC cards_without_cover=0 METRIC repo_style_titles=5 METRIC projects_without_own_social_card=0 METRIC projects_without_structured_data=0 METRIC images_without_size=0 METRIC later_images_not_lazy=0 METRIC gz_index=14816 METRIC gz_projects_index=24670 METRIC pages_over_budget=0 METRIC gz_styles_css=15653 METRIC gz_site_js=6643 
non-zero: none
```

## Findings delta against the best kept state
No findings.best.tsv yet (first kept run of this clone); full list in findings.tsv.

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `e128dee`
```
Python and browser tests (Chromium, Firefox and WebKit; WebKit recording matrix deselected — known hang on this host)
317 passed, 2 deselected, 705 subtests passed in 110.27s (0:01:50)
All checks passed (WebKit recording matrix deselected).
```

## Visual evidence
- `.hillclimb-shots/run-73-og-digital-mailroom.png`
- `.hillclimb-shots/run-73-og-mapreduce-reloaded.png`
- `.hillclimb-shots/run-73-og-natd.png`
- `.hillclimb-shots/run-73-og-wave-laboratory.png`
- `.hillclimb-shots/run-73-wave-laboratory-1280-dark.png`
- `.hillclimb-shots/run-73-wave-laboratory-1280-light.png`
- `.hillclimb-shots/run-73-wave-laboratory-375-dark.png`
- `.hillclimb-shots/run-73-wave-laboratory-375-light.png`

Reviewer notes: Opened Wave Laboratory page shots at 375/1280 light and dark: case-study layout, lead capture and kickers look unchanged; no overflow or theme break. Opened OG contact-sheet PNGs for Wave Laboratory, NATD, MapReduce-Reloaded and Digital-Mailroom: each is 1200x630 with existing project title, kicker, pink accent bar and cover motif; no invented titles or project facts. Built HTML og:image URLs include the project slug. MapReduce description trim kept pages_over_budget at 0. Checks: 317 passed, 2 deselected (WebKit recording matrix at 375/1280 — known hang on this host); Chromium/Firefox recording still ran.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
