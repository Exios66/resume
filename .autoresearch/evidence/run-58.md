# Evidence for run 58

- Commit: `8145ba7 experiment: Add readable numbered research citations and source notes` (parent `62427b3`)
- Branch: `t3/portfolio-search-discovery`
- Date: 2026-11-08T11:03:59Z

## Source change (docs/ excluded)
```
 _quarto.yml                        |   2 +
 projects/natd/report.qmd           |  61 ++++++++++++++--------
 scripts/post-render.py             |  35 ++++++++++++-
 styles.css                         |  17 ++++++
 tests/fixtures/natd-citations.json | 104 +++++++++++++++++++++++++++++++++++++
 tests/test_browser.py              |  47 +++++++++++++++++
 tests/test_citations.py            |  16 ++++++
 tests/test_render_scripts.py       |  13 +++++
 tests/test_site_integrity.py       |   7 +++
 9 files changed, 278 insertions(+), 24 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 140
- This run:
```
METRIC polish_defects=1 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=55.8 METRIC audit_s=78.2 METRIC render_s=30
non-zero: {'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (     136):
```
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 1
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 10
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 11
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 12
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 13
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 14
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 15
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 16
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 17
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 2
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 3
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 4
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 5
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 6
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 7
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 8
1280	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 9
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 1
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 10
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 11
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 12
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 13
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 14
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 15
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 16
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 17
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 2
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 3
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 4
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 5
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 6
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 7
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 8
1280	light	projects/natd/report.html	research citation navigation	Missing numbered research citation 9
375	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 1
375	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 10
375	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 11
375	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 12
375	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 13
375	dark	projects/natd/report.html	research citation navigation	Missing numbered research citation 14
```
Added (      72):
```
1280	dark	projects/natd/report.html	axe	region x1
1280	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	light	projects/natd/report.html	axe	region x1
1280	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
1280	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	dark	projects/natd/report.html	axe	region x1
375	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	light	projects/natd/report.html	axe	region x1
375	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
375	light	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
414	dark	projects/natd/report.html	axe	region x1
414	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
414	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
414	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `8145ba7`
```
chart unit tests passed
233 passed, 2 deselected, 611 subtests passed in 132.76s (0:02:12)
All checks passed.
```

## Visual evidence
- [run-58-citations-1280-light-footnotes.png](../screenshots/run-58-citations-1280-light-footnotes.png)
- [run-58-citations-375-light.png](../screenshots/run-58-citations-375-light.png)
- [run-58-citations-414-light-search.png](../screenshots/run-58-citations-414-light-search.png)

Reviewer notes: Completed the numbered-citation experiment (segment 10) with three repairs inside the same idea, then amended the run commit. (1) a.footnote-ref now carries 3px inline padding so every superscript citation number stays a real, clickable box (the audit had counted 64 invisible focusable findings across the eight viewport-theme combos). (2) scripts/post-render.py seats the end-of-document footnotes section inside <main> before the footer with a pinning unit test - Pandoc writes footnotes after the body, leaving top-level content outside any landmark (axe 'region' on every combo). (3) the flattened search-index body reads the label dot separators as semicolons (unit test added; '.a number x / 1.5'-style multiplication dots no longer exist in body prose) so a snippet wrap cannot start or end a line with a separator. Also updated the natd test that pinned one link per reference: each source entry now has the numbered source plus the return arrow, which is exactly what this experiment adds. Screenshots reviewed: home/report page at 375 light; natd source notes at 1280 light (numbered entries with doi links, verification tags and return arrows, no clutter); search results at 414 light for a live query with the type chips and a snippet that reads cleanly. Score 140 -> 1: axe 0, layout 0, type 1 (the accepted heading widow); the 17 inequivalent parenthetical links are gone from the reading text. All checks pass (233 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
