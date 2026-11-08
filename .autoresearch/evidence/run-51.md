# Evidence for run 51

- Commit: `a668ed9 Rebuild site with updated stylesheet` (parent `070351d`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T09:48:38Z

## Source change (docs/ excluded)
```
 .autoresearch/project-improvement-plan.md | 35 +++++++++++++++++++++++++++++++
 1 file changed, 35 insertions(+)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 211
- This run:
```
METRIC polish_defects=127 METRIC axe_points=0 METRIC layout_points=126 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=54.1 METRIC audit_s=49.6 METRIC render_s=20
non-zero: {'report contents touch targets < 44px': 126, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (      84):
```
1280	dark	projects/aeroglobe/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/degen-llms/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/degen-llms/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/digital-mailroom/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/langtons-ant/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/llm-personas/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/llm-personas/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/mailroom-corpus-eda/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/mailroom-corpus-eda/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/mailroom-ml/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/mailroom-ml/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/mailroom-reloaded/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/mailroom-reloaded/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/natd/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/natd/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/psychometric-digital-twin/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/psychometric-digital-twin/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/rvl-cdip-classifier/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/rvl-cdip-classifier/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/wave-laboratory/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	dark	projects/wave-laboratory/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/aeroglobe/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/degen-llms/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/degen-llms/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/digital-mailroom/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/langtons-ant/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/llm-personas/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/llm-personas/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/mailroom-corpus-eda/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/mailroom-corpus-eda/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/mailroom-ml/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/mailroom-ml/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/mailroom-reloaded/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/mailroom-reloaded/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/natd/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/natd/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/psychometric-digital-twin/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/psychometric-digital-twin/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/rvl-cdip-classifier/appendix.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
1280	light	projects/rvl-cdip-classifier/report.html	contents column offset	main>div.page>nav.page-toc | column start offset 3.00px
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `a668ed9`
```
chart unit tests passed
220 passed, 2 deselected, 611 subtests passed in 95.70s (0:01:35)
All checks passed.
```

## Visual evidence
- [run-51-contents-1280-dark.png](../screenshots/run-51-contents-1280-dark.png)
- [run-51-contents-1280-light.png](../screenshots/run-51-contents-1280-light.png)
- [run-51-contents-375-dark.png](../screenshots/run-51-contents-375-dark.png)
- [run-51-contents-375-light.png](../screenshots/run-51-contents-375-light.png)
- [run-51-contents-768-dark.png](../screenshots/run-51-contents-768-dark.png)
- [run-51-contents-768-light.png](../screenshots/run-51-contents-768-light.png)

Reviewer notes: Opened all six contents screenshots at 375/768/1280 px in light/dark. Desktop and tablet columns now start at the same height; row-by-row visual order matches DOM order. Phone remains one readable column; bullets, caveat and surrounding summary remain visible. Browser confirmed equal first-row y=484.82 at 1280, no overflow, and Results click reached #results at 83.97px below the fixed header after scrolling settled. No private data in captures. All 84 alignment findings removed; no added findings. Full gate 220 passed, 2 deselected, 611 subtests passed in 95.70s.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.

## Source commit provenance

The CSS experiment and generated site are in `070351d`. A documentation-only workspace commit `a668ed9` added the research plan while checks ran; it changed no site, audit or test files. The gate stamped `a668ed9`, which is the recorded keep commit. The source diff for this candidate is `git diff e42480d 070351d -- styles.css`; the evidence header parent alone shows the intervening documentation commit, not the CSS experiment.
