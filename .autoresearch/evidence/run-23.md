# Evidence for run 23

- Commit: `13c9afb Merge pull request #103 from Exios66/claude/serene-fermat-yr920i` (parent `a84c471`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:16:12Z

## Source change (docs/ excluded)
```
 partials/diagrams/_rvl-cdip.qmd            |   2 +-
 partials/diagrams/_wave-lab.qmd            |   2 +-
 resume.qmd                                 |   7 ++-
 scripts/post-render.py                     |  14 +++--
 scripts/site.lua                           |  41 ++++++++++++++
 scripts/tables.lua                         |  80 ++++++++++++++++++++++++++
 styles.css                                 |  88 ++++++++++++++++++++++++++---
 tests/icons.test.cjs                       |   7 ++-
 tests/test_browser.py                      |  10 +++-
 tests/test_langtons_ant.py                 |  10 +++-
 tests/test_links.py                        |  12 +++-
 tests/test_links_unit.py                   |  11 ++++
 tests/test_mapreduce_reloaded.py           |   9 ++-
 tests/test_portfolio_additions.py          |   6 +-
 tests/test_render_scripts.py               |   6 ++
 tests/test_resume_content.py               |   4 +-
 tests/test_resume_pdf.py                   |   8 ++-
 tests/test_site.lua                        |  23 +++++++-
 tests/test_site_integrity.py               |   8 ++-
 38 files changed, 516 insertions(+), 51 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 22
- This run:
```
METRIC polish_defects=22 METRIC axe_points=0 METRIC layout_points=21 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.1 METRIC audit_s=28.7 METRIC render_s=20 
non-zero: {'crushed table cells': 8, 'tables wider than screen': 13, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
No findings.best.tsv yet (first kept run of this clone); full list in findings.tsv.

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `13c9afb`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 48.74s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-23-home-1280-light.png`
- `.hillclimb-shots/run-23-home-375-light.png`

Reviewer notes: Baseline on this machine, no new source change (run captures the current best state merged in PR 103). Screenshots of the home page at 1280 and 375 px light reviewed: desktop hero and chips render as on the live site; 375 px matches the hand-off state (mobile nav wraps to two rows, a known backlog item, scored neutral). Score 22 = hand-off value; all checks pass with Quarto 1.10.19 under LC_ALL=C (this machine's default LANG=C.UTF-8 changes Lua pattern syntax classes, so a C locale is required).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
