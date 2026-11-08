# Evidence for run 49

- Commit: `29a03e3 experiment: Give essay titles and summaries room on tablets` (parent `ad6ede0`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T09:12:05Z

## Source change (docs/ excluded)
```
 styles.css        | 2 ++
 writing/index.qmd | 2 +-
 2 files changed, 3 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 2
- This run:
```
METRIC polish_defects=1 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=54.0 METRIC audit_s=52.5 METRIC render_s=19 
non-zero: {'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       1):
```
768	light	writing/index.html	heading widow	h3 | The Ship of Theseus, Moth-Eaten
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `29a03e3`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 44.50s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-49-before-writing-768-light.png`
- `.hillclimb-shots/run-49-writing-1280-dark.png`
- `.hillclimb-shots/run-49-writing-1280-light.png`
- `.hillclimb-shots/run-49-writing-375-dark.png`
- `.hillclimb-shots/run-49-writing-375-light.png`
- `.hillclimb-shots/run-49-writing-768-dark.png`
- `.hillclimb-shots/run-49-writing-768-light.png`

Reviewer notes: Opened the baseline tablet image and six final screenshots at 375, 768, 1280 px in both themes. At 768 the full essay title and summary have one coherent row; at desktop the two-column card grid remains; phone cards remain readable. No private data visible. Browser confirms one 640px column at 768 and two 368px columns at 1280 with no page overflow. The only removed finding is the Writing title widow at 768; no new findings.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
