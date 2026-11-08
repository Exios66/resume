# Evidence for run 62

- Commit: `ab26129 experiment: Keep screen navigation out of printed reading surfaces` (parent `d3305c3`)
- Branch: `t3/portfolio-print-reading`
- Date: 2026-11-08T17:11:57Z

## Source change (docs/ excluded)
```
 styles.css | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 36
- This run:
```
METRIC polish_defects=0 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=0 METRIC pages=43 METRIC css_kb=55.8 METRIC audit_s=49.1 METRIC render_s=21
non-zero: none
```

## Findings delta against the best kept state
Removed (      36):
```
1280	light	projects/aeroglobe.html	print navigation	.project-pager
1280	light	projects/aeroglobe/appendix.html	print navigation	.project-pager
1280	light	projects/degen-llms.html	print navigation	.project-pager
1280	light	projects/degen-llms/appendix.html	print navigation	.project-pager
1280	light	projects/degen-llms/report.html	print navigation	.project-pager
1280	light	projects/digital-mailroom.html	print navigation	.project-pager
1280	light	projects/digital-mailroom/appendix.html	print navigation	.project-pager
1280	light	projects/langtons-ant.html	print navigation	.project-pager
1280	light	projects/langtons-ant/appendix.html	print navigation	.project-pager
1280	light	projects/llm-personas.html	print navigation	.project-pager
1280	light	projects/llm-personas/appendix.html	print navigation	.project-pager
1280	light	projects/llm-personas/report.html	print navigation	.project-pager
1280	light	projects/mailroom-corpus-eda.html	print navigation	.project-pager
1280	light	projects/mailroom-corpus-eda/appendix.html	print navigation	.project-pager
1280	light	projects/mailroom-corpus-eda/report.html	print navigation	.project-pager
1280	light	projects/mailroom-ml.html	print navigation	.project-pager
1280	light	projects/mailroom-ml/appendix.html	print navigation	.project-pager
1280	light	projects/mailroom-ml/report.html	print navigation	.project-pager
1280	light	projects/mailroom-reloaded.html	print navigation	.project-pager
1280	light	projects/mailroom-reloaded/appendix.html	print navigation	.project-pager
1280	light	projects/mailroom-reloaded/report.html	print navigation	.project-pager
1280	light	projects/mapreduce-reloaded.html	print navigation	.project-pager
1280	light	projects/natd.html	print navigation	.project-pager
1280	light	projects/natd/appendix.html	print navigation	.project-pager
1280	light	projects/natd/report.html	print navigation	.project-pager
1280	light	projects/neuron-atlas.html	print navigation	.project-pager
1280	light	projects/psychometric-digital-twin.html	print navigation	.project-pager
1280	light	projects/psychometric-digital-twin/appendix.html	print navigation	.project-pager
1280	light	projects/psychometric-digital-twin/report.html	print navigation	.project-pager
1280	light	projects/rvl-cdip-classifier.html	print navigation	.project-pager
1280	light	projects/rvl-cdip-classifier/appendix.html	print navigation	.project-pager
1280	light	projects/rvl-cdip-classifier/report.html	print navigation	.project-pager
1280	light	projects/wave-laboratory.html	print navigation	.project-pager
1280	light	projects/wave-laboratory/appendix.html	print navigation	.project-pager
1280	light	projects/wave-laboratory/report.html	print navigation	.project-pager
1280	light	search.html	print navigation	.search-suggest
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `ab26129`
```
chart unit tests passed
233 passed, 2 deselected, 611 subtests passed in 78.44s (0:01:18)
All checks passed.
```

## Visual evidence
- [run-62-print-project-1280-dark.png](../screenshots/run-62-print-project-1280-dark.png)
- [run-62-print-project-1280-light.png](../screenshots/run-62-print-project-1280-light.png)
- [run-62-print-project-375-dark.png](../screenshots/run-62-print-project-375-dark.png)
- [run-62-print-project-375-light.png](../screenshots/run-62-print-project-375-light.png)
- [run-62-print-search-1280-dark.png](../screenshots/run-62-print-search-1280-dark.png)
- [run-62-print-search-1280-light.png](../screenshots/run-62-print-search-1280-light.png)
- [run-62-print-search-375-dark.png](../screenshots/run-62-print-search-375-dark.png)
- [run-62-print-search-375-light.png](../screenshots/run-62-print-search-375-light.png)

Reviewer notes: Reviewed all eight run-62 print captures: project and Search at 375/1280, light/dark preferences. Project figures, captions, lessons and stack remain; previous/next boxes disappear. Search keeps its title and description; screen-only suggestion chips disappear as intended by the existing print policy. Eight before captures show those controls leaking into print. All images contain only public site content. Browser screen checks confirm pager navigation and calibration suggestion search still work, with no phone overflow. Findings remove 36 print-navigation points and add none; all 43 primary titles remain visible. Full gate on ab26129: 233 passed, 2 deselected, 611 subtests in 78.44s. Not checked: PDF pagination, native printer dialogs, physical printers, other engines/devices or screen readers.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
