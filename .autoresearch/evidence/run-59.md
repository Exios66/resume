# Evidence for run 59

- Commit: `a8c5e1a experiment: rephrase the graduate heading so balance ends on two words` (parent `8145ba7`)
- Branch: `t3/portfolio-search-discovery`
- Date: 2026-11-08T11:11:47Z

## Source change (docs/ excluded)
```
 research.qmd | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 1
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=55.8 METRIC audit_s=96.1 METRIC render_s=44
non-zero: none
```

## Findings delta against the best kept state
Removed (      75):
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
375	light	research.html	heading widow	h2 | Graduate research, UW–Madison
375	light	search.html	separator starts line	ul.search-results>li>p | …: technical report ModernBERT ingest classifier · training, calibration, routin
414	dark	projects/natd/report.html	axe	region x1
414	dark	projects/natd/report.html	invisible focusable	div.page>p>a.footnote-ref
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `a8c5e1a`
```
chart unit tests passed
233 passed, 2 deselected, 611 subtests passed in 108.10s (0:01:48)
All checks passed.
```

## Visual evidence
- [run-59-research-375-light-graduate.png](../screenshots/run-59-research-375-light-graduate.png)
- [run-59-widow-375-light.png](../screenshots/run-59-widow-375-light.png)

Reviewer notes: Rephrased research.qmd's second section heading from 'Graduate research, UW–Madison' to 'Graduate research at UW–Madison' (same meaning; the comma left text-wrap: balance only a 2+1 split whose last line was the single token UW–MADISON, which this audit has counted as a widow since segment 3 and the owner had accepted). Screenshot reviewed at 375 light: the uppercase heading now balances as 'GRADUATE RESEARCH / AT UW–MADISON', ending on two words; the section's kicker and bullet entries below are unchanged. Score 1->0: polish_defects zero for the first time in this endeavour (axe, layout, error, structure, type and lint buckets all zero across the 43 pages and all viewports the audit covers). All checks pass (233 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
