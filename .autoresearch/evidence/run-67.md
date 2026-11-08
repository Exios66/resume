# Evidence for run 67

- Commit: `3ed86e7 experiment: Restore reading width for stacked table captions` (parent `94a8d3c`)
- Branch: `t3/portfolio-evidence-explorer`
- Date: 2026-11-08T17:39:20Z

## Source change (docs/ excluded)
```
 styles.css            |  1 +
 tests/test_browser.py | 20 ++++++++++++++++++++
 2 files changed, 21 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 6
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=58.3 METRIC audit_s=47.6 METRIC render_s=22
non-zero: none
```

## Findings delta against the best kept state
Removed (       6):
```
375	dark	projects/langtons-ant.html	narrow table caption	main>div.page>table.chart-source.caption-top | caption 71.6px / table 335.0px
375	light	projects/langtons-ant.html	narrow table caption	main>div.page>table.chart-source.caption-top | caption 71.6px / table 335.0px
414	dark	projects/langtons-ant.html	narrow table caption	main>div.page>table.chart-source.caption-top | caption 71.6px / table 374.0px
414	light	projects/langtons-ant.html	narrow table caption	main>div.page>table.chart-source.caption-top | caption 71.6px / table 374.0px
768	dark	projects/langtons-ant.html	narrow table caption	main>div.page>table.chart-source.caption-top | caption 71.6px / table 640.0px
768	light	projects/langtons-ant.html	narrow table caption	main>div.page>table.chart-source.caption-top | caption 71.6px / table 640.0px
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `3ed86e7`
```
chart unit tests passed
249 passed, 2 deselected, 611 subtests passed in 80.98s (0:01:20)
All checks passed.
```

## Visual evidence
- [run-67-caption-1280-dark.png](../screenshots/run-67-caption-1280-dark.png)
- [run-67-caption-1280-light.png](../screenshots/run-67-caption-1280-light.png)
- [run-67-caption-375-dark.png](../screenshots/run-67-caption-375-dark.png)
- [run-67-caption-375-light.png](../screenshots/run-67-caption-375-light.png)
- [run-67-caption-414-dark.png](../screenshots/run-67-caption-414-dark.png)
- [run-67-caption-414-light.png](../screenshots/run-67-caption-414-light.png)
- [run-67-caption-768-dark.png](../screenshots/run-67-caption-768-dark.png)
- [run-67-caption-768-light.png](../screenshots/run-67-caption-768-light.png)

Reviewer notes: Opened all eight run-67 screenshots at 375/414/768/1280, light/dark, plus both segment14 before captures. The caption now spans its stacked table and reads in normal lines above the data; desktop retains native bottom-caption layout. Authored text, two benchmark rows, header labels, source controls and historical limitations remain unchanged. Browser measurement at 375: caption/table widths both335px and caption height115.5px, versus71.6px/335px and567px before. Score6 to0: six narrow-caption findings removed, none added; whole-site buckets zero. Full gate on3ed86e7:249 passed,2 deselected,611 subtests in80.98s. Public portfolio content only; no private data in images. Not checked: other engines, physical devices, screen readers, native Linux, native PDF pagination/printing, full SVG contrast or external-source reauthentication.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
