# Evidence for run 52

- Commit: `7412851 experiment: Make report contents links easier to activate` (parent `a668ed9`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T09:52:25Z

## Source change (docs/ excluded)
```
 styles.css | 2 ++
 1 file changed, 2 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 127
- This run:
```
METRIC polish_defects=1 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=54.3 METRIC audit_s=57.4 METRIC render_s=36
non-zero: {'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (     126):
```
375	dark	projects/aeroglobe/appendix.html	contents touch targets	main>div.page>nav.page-toc | 5 links below 44px
375	dark	projects/degen-llms/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	dark	projects/degen-llms/report.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	dark	projects/digital-mailroom/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	dark	projects/langtons-ant/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	dark	projects/llm-personas/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	dark	projects/llm-personas/report.html	contents touch targets	main>div.page>nav.page-toc | 7 links below 44px
375	dark	projects/mailroom-corpus-eda/appendix.html	contents touch targets	main>div.page>nav.page-toc | 7 links below 44px
375	dark	projects/mailroom-corpus-eda/report.html	contents touch targets	main>div.page>nav.page-toc | 7 links below 44px
375	dark	projects/mailroom-ml/appendix.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	dark	projects/mailroom-ml/report.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	dark	projects/mailroom-reloaded/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	dark	projects/mailroom-reloaded/report.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	dark	projects/natd/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	dark	projects/natd/report.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	dark	projects/psychometric-digital-twin/appendix.html	contents touch targets	main>div.page>nav.page-toc | 5 links below 44px
375	dark	projects/psychometric-digital-twin/report.html	contents touch targets	main>div.page>nav.page-toc | 5 links below 44px
375	dark	projects/rvl-cdip-classifier/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	dark	projects/rvl-cdip-classifier/report.html	contents touch targets	main>div.page>nav.page-toc | 9 links below 44px
375	dark	projects/wave-laboratory/appendix.html	contents touch targets	main>div.page>nav.page-toc | 5 links below 44px
375	dark	projects/wave-laboratory/report.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	light	projects/aeroglobe/appendix.html	contents touch targets	main>div.page>nav.page-toc | 5 links below 44px
375	light	projects/degen-llms/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	light	projects/degen-llms/report.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	light	projects/digital-mailroom/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	light	projects/langtons-ant/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	light	projects/llm-personas/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	light	projects/llm-personas/report.html	contents touch targets	main>div.page>nav.page-toc | 7 links below 44px
375	light	projects/mailroom-corpus-eda/appendix.html	contents touch targets	main>div.page>nav.page-toc | 7 links below 44px
375	light	projects/mailroom-corpus-eda/report.html	contents touch targets	main>div.page>nav.page-toc | 7 links below 44px
375	light	projects/mailroom-ml/appendix.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	light	projects/mailroom-ml/report.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	light	projects/mailroom-reloaded/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	light	projects/mailroom-reloaded/report.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	light	projects/natd/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	light	projects/natd/report.html	contents touch targets	main>div.page>nav.page-toc | 8 links below 44px
375	light	projects/psychometric-digital-twin/appendix.html	contents touch targets	main>div.page>nav.page-toc | 5 links below 44px
375	light	projects/psychometric-digital-twin/report.html	contents touch targets	main>div.page>nav.page-toc | 5 links below 44px
375	light	projects/rvl-cdip-classifier/appendix.html	contents touch targets	main>div.page>nav.page-toc | 4 links below 44px
375	light	projects/rvl-cdip-classifier/report.html	contents touch targets	main>div.page>nav.page-toc | 9 links below 44px
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `7412851`
```
chart unit tests passed
220 passed, 2 deselected, 611 subtests passed in 76.46s (0:01:16)
All checks passed.
```

## Visual evidence
- [run-52-contents-1280-dark.png](../screenshots/run-52-contents-1280-dark.png)
- [run-52-contents-1280-light.png](../screenshots/run-52-contents-1280-light.png)
- [run-52-contents-375-dark-focus.png](../screenshots/run-52-contents-375-dark-focus.png)
- [run-52-contents-375-dark.png](../screenshots/run-52-contents-375-dark.png)
- [run-52-contents-375-light.png](../screenshots/run-52-contents-375-light.png)
- [run-52-contents-768-dark.png](../screenshots/run-52-contents-768-dark.png)
- [run-52-contents-768-light.png](../screenshots/run-52-contents-768-light.png)

Reviewer notes: Opened all six contents screenshots at 375/768/1280 px light/dark and an additional actual 375px dark keyboard-focus capture (2x density). Full-cell targets are 44px tall, no overflow or text clipping; phone panel is 451.20px tall and keeps the historical caveat and following summary distinct. Extra vertical space accepted for reliable touch navigation. Desktop browser: Tab moves to System and data, :focus-visible true, 2px outline plus background; Enter activates #system-and-data, heading settles at 84.11px below the fixed header. Phone pointer at x330 y439 activates #results from the far-right padded area, target settles at 15.91px; no sticky header on this phone layout. Seven screenshots contain only public portfolio content. All 126 touch-target findings removed, zero added. Full gate 220 passed, 2 deselected, 611 subtests passed in 76.46s.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
