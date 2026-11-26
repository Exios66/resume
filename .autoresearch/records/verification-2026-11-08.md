# Verification: continuation runs 44–49

Environment: `bash scripts/setup-agent.sh`, then `. .autoresearch-tools/env.sh` before every render, audit and screenshot. `scripts/hillclimb/hc.sh doctor` ended with `All tools present.` Quarto 1.10.19, C locale, repository Python venv and Chromium.

## Fixed audit segments

- Segment 5 (`2ed7a5a`): 414/768 px added to existing 375/1280, in light and dark; 320 px layout-only remains. All 43 pages. Baseline run 44: 24.
- Segment 6 (`5309c8e`): one point per chart/diagram with SVG text below 12 rendered pixels (0.05 px tolerance), measured through its screen transform. Baseline run 47: 174. No audit or checks changes within either segment.

Commands:

```sh
scripts/hillclimb/hc.sh segment 'Phone 414 and tablet 768 coverage in both themes'
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh log keep 'Segment 5 baseline: 414 and 768 px in both themes'
scripts/hillclimb/hc.sh experiment 'Extend labelled table rows to tablet widths' styles.css
"$QUARTO" render resume.qmd --quiet
.venv/bin/python scripts/make-resume-pdf.py
scripts/hillclimb/hc.sh experiment 'Separate undergraduate credential from concentration and GPA' about.qmd resume.qmd assets/Jack_Burleson_Resume.pdf
scripts/hillclimb/hc.sh segment 'Chart and diagram text stays at least 12 rendered pixels'
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh log keep 'Segment 6 baseline: rendered SVG text legibility'
scripts/hillclimb/hc.sh experiment 'Preserve legible chart and diagram labels across screen sizes' styles.css
# Same-candidate refinement after visual review and the initial tooltip check failure:
AUDIT_LIST=findings.tsv bash autoresearch.sh > run.log 2>&1
git checkout -- docs/sitemap.xml
git add styles.css scripts/charts.lua tests/test_charts.lua docs
git commit --amend --no-edit
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh experiment 'Give essay titles and summaries room on tablets' styles.css writing/index.qmd
```

Every experiment also ran `scripts/hillclimb/hc.sh checks` (which invokes `bash autoresearch.checks.sh`: Lua through bundled Pandoc, Node, Python and real Chromium). Exact experiment commits and results are in [the per-run records](evidence/).

The first run-48 version failed `test_chart_tooltip_hides_on_sideways_scroll_and_stays_on_screen` (1 failed, 22 passed, 2 deselected); it was not kept. Adaptive bar-label gutters and full desktop diagram margins fixed the candidate before re-auditing and passing the full gate on `daf4899`. The Lua negative-label collision assertion now compares to the intentionally changed category-label coordinate, preserving the no-collision requirement.

## Actual screenshots

These commands captured the changed areas; all images were opened, reviewed and checked for private data. Both themes for each width:

```sh
for width in 375 768 1280; do
  for theme in light dark; do
    scripts/hillclimb/hc.sh shot projects/psychometric-digital-twin/report.html "$width" "$theme" "run-45-table-$width-$theme" --at table --text DeepSeek
    scripts/hillclimb/hc.sh shot projects/natd.html "$width" "$theme" "run-48-chart-$width-$theme" --at figure.chart
    scripts/hillclimb/hc.sh shot projects/index.html "$width" "$theme" "run-48-diagram-$width-$theme" --at figure.diagram
    scripts/hillclimb/hc.sh shot writing/index.html "$width" "$theme" "run-49-writing-$width-$theme" --at .card --text 'The Ship of Theseus'
  done
done
for width in 375 414 1280; do
  for theme in light dark; do
    scripts/hillclimb/hc.sh shot about.html "$width" "$theme" "run-46-education-$width-$theme" --at .degree --text 'B.S.'
  done
done
scripts/hillclimb/hc.sh shot resume.html 414 light run-46-resume-414-light --at .degree --text 'B.S.'
scripts/hillclimb/hc.sh shot resume.html 1280 dark run-46-resume-1280-dark --at .degree --text 'B.S.'
scripts/hillclimb/hc.sh shot projects/natd.html 375 light segment-6-before-natd-375-light --at figure.chart
scripts/hillclimb/hc.sh shot projects/index.html 375 dark segment-6-before-ecosystem-375-dark --at figure.diagram
scripts/hillclimb/hc.sh shot writing/index.html 768 light run-49-before-writing-768-light --at .card --text 'The Ship of Theseus'
```

Run-48 screenshots were recaptured after refinement. Earlier unkept images remain only in the ignored local `.hillclimb-shots/refinement-48-initial-*` files. Final evidence is copied to [screenshots/](screenshots/), outside the published site. An additional collaborative-browser screenshot records the chart at scrollLeft 327 with its focused tooltip visible (375 CSS px, 2× pixel density).

## Browser interaction and coverage limits

The collaborative browser confirmed tablet table stacking and desktop grid cells, education paragraphs at 414 px, chart and diagram arrow-key scrolling, tooltip visibility after bringing the chart into view, Escape dismissal, 12 px phone chart/diagram labels and 12.21 px desktop ecosystem labels. The ecosystem diagram fits entirely at desktop (clientWidth = scrollWidth = 846). Writing cards use one 640 px column at 768 and two 368 px columns at 1280. No page overflow in these observed states.

The regenerated PDF has two pages and retains the credential and GPA (checked using `.venv/bin/python` and `pypdf`); the real-browser print regression also passes. The system Python lacked pypdf; the repository venv supplied it.

Not checked: Firefox, WebKit, physical phones/tablets, screen readers, external links and live deployment. The SVG check covers size, not all SVG contrast or semantic quality. Screenshots supplement audit assertions; they do not prove every interaction works. Changes are on the PR branch, not merged to main.


## Final kept results

| Run | Commit | Segment score | Full gate |
|---|---|---|---|
| 45 | 7233502 | 24 → 4 | 197 passed, 2 deselected, 611 subtests; 42.00s |
| 46 | 6cb67bb | 4 → 2 | 197 passed, 2 deselected, 611 subtests; 42.33s |
| 48 | daf4899 | 174 → 2 | 197 passed, 2 deselected, 611 subtests; 43.28s |
| 49 | 29a03e3 | 2 → 1 | 197 passed, 2 deselected, 611 subtests; 44.50s |

Final audit: 43 pages, polish_defects=1; axe/layout/error/structure/lint=0. The one accepted finding is the research heading ending with UW–Madison at 375 px light. Final `git diff --check` passed.
