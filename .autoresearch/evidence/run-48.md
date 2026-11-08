# Evidence for run 48

- Commit: `daf4899 experiment: Preserve legible chart and diagram labels across screen sizes` (parent `5309c8e`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T09:08:20Z

## Source change (docs/ excluded)
```
 scripts/charts.lua    | 17 ++++++++++++-----
 styles.css            | 27 ++++++++++++++++-----------
 tests/test_charts.lua |  2 +-
 3 files changed, 29 insertions(+), 17 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 174
- This run:
```
METRIC polish_defects=2 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=2 METRIC pages=43 METRIC css_kb=53.9 METRIC audit_s=54.1 METRIC render_s=19 
non-zero: {'heading ends with a one-word line': 2}
```

## Findings delta against the best kept state
Removed (     172):
```
1280	dark	projects/aeroglobe.html	small SVG text	main>div.page>figure.diagram | 11.80px | The live site ships a short OpenSky
1280	dark	projects/degen-llms.html	small SVG text	main>div.page>figure.diagram | 10.89px | same renderers
1280	dark	projects/degen-llms/report.html	small SVG text	main>div.page>figure.diagram | 10.89px | same renderers
1280	dark	projects/digital-mailroom.html	small SVG text	main>div.page>figure.diagram | 11.80px | One LangGraph pipeline joins these parts
1280	dark	projects/index.html	small SVG text	main>section.page-title.page>figure.diagram.diagram-ecosystem | 10.77px | trains
1280	dark	projects/langtons-ant.html	small SVG text	main>div.page>figure.diagram | 10.89px | the one part the tests pin down
1280	dark	projects/llm-personas.html	small SVG text	main>div.page>figure.diagram | 10.89px | Cast: all one model
1280	dark	projects/mailroom-corpus-eda.html	small SVG text	main>div.page>figure.diagram | 10.89px | labels never in the blind config
1280	dark	projects/mailroom-ml.html	small SVG text	main>div.page>figure.diagram | 11.80px | high S
1280	dark	projects/mailroom-reloaded.html	small SVG text	main>div.page>figure.diagram | 11.80px | Escalation
1280	dark	projects/mapreduce-reloaded.html	small SVG text	main>div.page>figure.diagram | 11.80px | Go and Python share
1280	dark	projects/psychometric-digital-twin.html	small SVG text	main>div.page>figure.diagram | 11.80px | same features
1280	dark	projects/psychometric-digital-twin/report.html	small SVG text	main>div.page>figure.diagram | 11.80px | same features
1280	dark	projects/wave-laboratory.html	small SVG text	main>div.page>figure.diagram | 10.89px | same h₀
1280	light	projects/aeroglobe.html	small SVG text	main>div.page>figure.diagram | 11.80px | The live site ships a short OpenSky
1280	light	projects/degen-llms.html	small SVG text	main>div.page>figure.diagram | 10.89px | same renderers
1280	light	projects/degen-llms/report.html	small SVG text	main>div.page>figure.diagram | 10.89px | same renderers
1280	light	projects/digital-mailroom.html	small SVG text	main>div.page>figure.diagram | 11.80px | One LangGraph pipeline joins these parts
1280	light	projects/index.html	small SVG text	main>section.page-title.page>figure.diagram.diagram-ecosystem | 10.77px | trains
1280	light	projects/langtons-ant.html	small SVG text	main>div.page>figure.diagram | 10.89px | the one part the tests pin down
1280	light	projects/llm-personas.html	small SVG text	main>div.page>figure.diagram | 10.89px | Cast: all one model
1280	light	projects/mailroom-corpus-eda.html	small SVG text	main>div.page>figure.diagram | 10.89px | labels never in the blind config
1280	light	projects/mailroom-ml.html	small SVG text	main>div.page>figure.diagram | 11.80px | high S
1280	light	projects/mailroom-reloaded.html	small SVG text	main>div.page>figure.diagram | 11.80px | Escalation
1280	light	projects/mapreduce-reloaded.html	small SVG text	main>div.page>figure.diagram | 11.80px | Go and Python share
1280	light	projects/psychometric-digital-twin.html	small SVG text	main>div.page>figure.diagram | 11.80px | same features
1280	light	projects/psychometric-digital-twin/report.html	small SVG text	main>div.page>figure.diagram | 11.80px | same features
1280	light	projects/wave-laboratory.html	small SVG text	main>div.page>figure.diagram | 10.89px | same h₀
375	dark	projects/aeroglobe.html	small SVG text	main>div.page>figure.diagram | 9.75px | The live site ships a short OpenSky
375	dark	projects/degen-llms.html	small SVG text	main>div.page>figure.diagram | 9.00px | same renderers
375	dark	projects/degen-llms/report.html	small SVG text	main>div.page>figure.diagram | 9.00px | same renderers
375	dark	projects/digital-mailroom.html	small SVG text	main>div.page>figure.diagram | 9.75px | One LangGraph pipeline joins these parts
375	dark	projects/index.html	small SVG text	main>section.page-title.page>figure.diagram.diagram-ecosystem | 10.80px | trains
375	dark	projects/langtons-ant.html	small SVG text	main>div.page>figure.chart.chart-strip | 9.75px | 0
375	dark	projects/langtons-ant.html	small SVG text	main>div.page>figure.diagram | 9.00px | the one part the tests pin down
375	dark	projects/llm-personas.html	small SVG text	main>div.page>figure.diagram | 9.00px | Cast: all one model
375	dark	projects/mailroom-corpus-eda.html	small SVG text	main>div.page>figure.diagram | 9.00px | labels never in the blind config
375	dark	projects/mailroom-corpus-eda/report.html	small SVG text	main>div.page>figure.chart.chart-step | 9.75px | Documents that fit (axis starts at 70%)
375	dark	projects/mailroom-ml.html	small SVG text	main>div.page>figure.diagram | 9.75px | high S
375	dark	projects/mailroom-ml/report.html	small SVG text	main>div.page>figure.chart.chart-dumbbell | 9.75px | 0
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `daf4899`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 43.28s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-48-chart-1280-dark.png`
- `.hillclimb-shots/run-48-chart-1280-light.png`
- `.hillclimb-shots/run-48-chart-375-dark.png`
- `.hillclimb-shots/run-48-chart-375-light.png`
- `.hillclimb-shots/run-48-chart-375-scrolled-tooltip.png`
- `.hillclimb-shots/run-48-chart-768-dark.png`
- `.hillclimb-shots/run-48-chart-768-light.png`
- `.hillclimb-shots/run-48-diagram-1280-dark.png`
- `.hillclimb-shots/run-48-diagram-1280-light.png`
- `.hillclimb-shots/run-48-diagram-375-dark.png`
- `.hillclimb-shots/run-48-diagram-375-light.png`
- `.hillclimb-shots/run-48-diagram-768-dark.png`
- `.hillclimb-shots/run-48-diagram-768-light.png`

Reviewer notes: Opened all twelve final chart/diagram screenshots at 375, 768, 1280 in light/dark, plus the scrolled phone chart with tooltip. Larger text is readable, phone positive/negative bars both begin in view, desktop ecosystem diagram fits fully in its expanded paper margins, captions remain in the viewport, and nearby tables/cards remain intact. No private data visible. Browser measured chart ticks at 12px, diagram edge labels at 12px on phones and 12.21px at desktop, keyboard scrolling in chart/diagram, visible focused tooltip after bringing chart into view, and Escape dismissal. Initial version failed tooltip visibility and cropped desktop diagrams; amended gutter sizing and diagram margins, then reran AUDIT_LIST=findings.tsv bash autoresearch.sh and all checks. Lua assertion now measures collision clearance against the intentionally changed label coordinate. Final delta removes all 172 small-SVG findings, adds none.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
