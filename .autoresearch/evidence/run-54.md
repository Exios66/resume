# Evidence for run 54

- Commit: `fbfef77 experiment: Label search results by destination type` (parent `fda83d9`)
- Branch: `t3/portfolio-search-discovery`
- Date: 2026-11-08T10:06:18Z

## Source change (docs/ excluded)
```
 assets/js/site.js     | 14 ++++++++++++++
 styles.css            |  1 +
 tests/test_browser.py |  5 +++++
 3 files changed, 20 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 100
- This run:
```
METRIC polish_defects=12 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=8 METRIC lint_points=0 METRIC type_points=4 METRIC pages=43 METRIC css_kb=54.5 METRIC audit_s=54.4 METRIC render_s=21 
non-zero: {'separator starts a line': 2, 'separator ends a line': 1, 'heading ends with a one-word line': 1, 'search type filtering': 8}
```

## Findings delta against the best kept state
Removed (      88):
```
1280	dark	search.html	search destination type	/resume/about.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/index.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/projects/digital-mailroom.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/projects/index.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/projects/mailroom-ml.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/projects/mailroom-ml/appendix.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/projects/mailroom-ml/report.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/projects/mailroom-reloaded/appendix.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/projects/mailroom-reloaded/report.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/projects/psychometric-digital-twin/report.html | missing or incorrect destination type
1280	dark	search.html	search destination type	/resume/resume.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/about.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/index.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/projects/digital-mailroom.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/projects/index.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/projects/mailroom-ml.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/projects/mailroom-ml/appendix.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/projects/mailroom-ml/report.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/projects/mailroom-reloaded/appendix.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/projects/mailroom-reloaded/report.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/projects/psychometric-digital-twin/report.html | missing or incorrect destination type
1280	light	search.html	search destination type	/resume/resume.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/about.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/index.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/projects/digital-mailroom.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/projects/index.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/projects/mailroom-ml.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/projects/mailroom-ml/appendix.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/projects/mailroom-ml/report.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/projects/mailroom-reloaded/appendix.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/projects/mailroom-reloaded/report.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/projects/psychometric-digital-twin/report.html | missing or incorrect destination type
375	dark	search.html	search destination type	/resume/resume.html | missing or incorrect destination type
375	light	search.html	search destination type	/resume/about.html | missing or incorrect destination type
375	light	search.html	search destination type	/resume/index.html | missing or incorrect destination type
375	light	search.html	search destination type	/resume/projects/digital-mailroom.html | missing or incorrect destination type
375	light	search.html	search destination type	/resume/projects/index.html | missing or incorrect destination type
375	light	search.html	search destination type	/resume/projects/mailroom-ml.html | missing or incorrect destination type
375	light	search.html	search destination type	/resume/projects/mailroom-ml/appendix.html | missing or incorrect destination type
375	light	search.html	search destination type	/resume/projects/mailroom-ml/report.html | missing or incorrect destination type
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `fbfef77`
```
chart unit tests passed
220 passed, 2 deselected, 611 subtests passed in 137.16s (0:02:17)
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-54-search-1280-dark.png`
- `.hillclimb-shots/run-54-search-1280-light.png`
- `.hillclimb-shots/run-54-search-375-dark.png`
- `.hillclimb-shots/run-54-search-375-light.png`
- `.hillclimb-shots/run-54-search-768-dark.png`
- `.hillclimb-shots/run-54-search-768-light.png`

Reviewer notes: Opened six actual search captures at 375/768/1280 in light/dark plus two baseline captures. Destination-type labels are readable above the link without displacing the URL/snippet relationship, clipping or overflow. Public portfolio data only. Collaborative browser confirmed the same 11 calibration matches and all expected route labels, and activated the Technical report link to Mailroom-ML technical report. Full gate 220 passed, 2 deselected, 611 subtests passed in 137.16s. Tests now pin the deliberately added labels for case study/report/appendix. 88 missing-label findings removed, no added findings; 100 to 12. Existing snippet separator findings remain visible and are not hidden.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
