# Evidence for run 55

- Commit: `b1e51e7 experiment: Filter search by artifact type with shareable URLs` (parent `fbfef77`)
- Branch: `t3/portfolio-search-discovery`
- Date: 2026-11-08T10:12:37Z

## Source change (docs/ excluded)
```
 assets/js/site.js     | 40 +++++++++++++++++++++++------
 search.qmd            | 12 +++++++++
 styles.css            |  7 ++++--
 tests/test_browser.py | 69 +++++++++++++++++++++++++++++++++++++++++++++++++++
 4 files changed, 118 insertions(+), 10 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 12
- This run:
```
METRIC polish_defects=4 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=4 METRIC pages=43 METRIC css_kb=54.8 METRIC audit_s=48.2 METRIC render_s=20
non-zero: {'separator starts a line': 2, 'separator ends a line': 1, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       8):
```
1280	dark	search.html	search type filtering	No page-type filter for mixed search results
1280	light	search.html	search type filtering	No page-type filter for mixed search results
375	dark	search.html	search type filtering	No page-type filter for mixed search results
375	light	search.html	search type filtering	No page-type filter for mixed search results
414	dark	search.html	search type filtering	No page-type filter for mixed search results
414	light	search.html	search type filtering	No page-type filter for mixed search results
768	dark	search.html	search type filtering	No page-type filter for mixed search results
768	light	search.html	search type filtering	No page-type filter for mixed search results
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `b1e51e7`
```
chart unit tests passed
225 passed, 2 deselected, 611 subtests passed in 74.77s (0:01:14)
All checks passed.
```

## Visual evidence
- [run-55-empty-375-dark.png](../screenshots/run-55-empty-375-dark.png)
- [run-55-filter-375-dark-focus.png](../screenshots/run-55-filter-375-dark-focus.png)
- [run-55-reports-1280-dark.png](../screenshots/run-55-reports-1280-dark.png)
- [run-55-reports-375-light.png](../screenshots/run-55-reports-375-light.png)
- [run-55-search-1280-dark.png](../screenshots/run-55-search-1280-dark.png)
- [run-55-search-1280-light.png](../screenshots/run-55-search-1280-light.png)
- [run-55-search-375-dark.png](../screenshots/run-55-search-375-dark.png)
- [run-55-search-375-light.png](../screenshots/run-55-search-375-light.png)
- [run-55-search-768-dark.png](../screenshots/run-55-search-768-dark.png)
- [run-55-search-768-light.png](../screenshots/run-55-search-768-light.png)

Reviewer notes: Opened ten actual captures: six All pages search states at 375/768/1280 light/dark; filtered reports at 375 light and 1280 dark; empty appendix state at 375 dark; actual 375px dark keyboard-focus capture at 2x density. Responsive form is stacked on phones and side-by-side on tablet/desktop; 46px native selector and text labels remain readable, no overflow or clipped controls. Public portfolio data only. Browser selection gives exactly 3 report routes from 11 calibration matches and q/type URL parameters; Tab from input reaches select with :focus-visible and a 2px outline. Native picker Arrow/Enter selection was not established by preview, so no keyboard-choice pass is claimed. Tests verify exact subsets/order/restoration, URL reloads and invalid types, empty/Escape behavior, delayed/failed index readiness, and working no-JavaScript browse fallback. Initial targeted fallback assertion used the noscript wrapper (Playwright text matcher skips it); scoped to its actual paragraph, rerun 6 passed. Tests-only amend followed by fresh render/audit on b1e51e7: score 12 to 4, all 8 filter findings removed, none added; full gate 225 passed, 2 deselected, 611 subtests passed in 74.77s. Three existing snippet separator points plus the accepted heading widow remain.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.

## Pre-publication correctness review

After the keep, source review found that the later screen grid rule overrode the existing print hide rule. A new real-browser print assertion failed (`form.site-search` visible). Commit `3eed785` scopes grid display to screen media and adds the print assertion to all four viewport/theme cases. This is a correctness repair of the same feature, not a new score-seeking candidate; the original keep record is preserved.

Re-rendered and re-audited with `hc.sh baseline` on the repaired source: score remains 4, zero axe/layout/error/structure/lint points. Full `hc.sh checks` on `3eed785`: 225 passed, 2 deselected, 611 subtests passed in 77.00s; All checks passed. Reviewed two renewed screen captures and the actual print-media capture, verifying the search form is hidden. The capture checks CSS print media, not PDF pagination. No audit/check definitions changed.
