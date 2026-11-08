# Evidence for run 30

- Commit: `d7beb51 experiment: scope tabular-nums to numeric cells` (parent `85fff22`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T05:42:37Z

## Source change (docs/ excluded)
```
 styles.css | 5 ++++-
 1 file changed, 4 insertions(+), 1 deletion(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 9
- This run:
```
METRIC polish_defects=9 METRIC axe_points=0 METRIC layout_points=8 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=1 METRIC pages=43 METRIC css_kb=52.9 METRIC audit_s=28.9 METRIC render_s=19 
non-zero: {'crushed table cells': 2, 'tables wider than screen': 6, 'heading ends with a one-word line': 1}
```

## Findings delta against the best kept state
Removed (       0):
```
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `d7beb51`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 43.36s
All checks passed.
```

## Visual evidence
- `.hillclimb-shots/run-30-mailroom-375-light-tnum.png`
- `.hillclimb-shots/run-30-natd-320-dark-tnum.png`
- `.hillclimb-shots/run-30-psychometric-1280-light-tnum.png`

Reviewer notes: Scoped font-variant-numeric: tabular-nums (styles.css) from whole tables to right-aligned cells and .num cells. In the browser I measured Inter's tnum widening 'x-x' from 21.7px to 25.1px, which is what put visible gaps around hyphens in cell labels like DeepSeek-R1-Distill-Llama-8B. Screenshots reviewed: psychometric model table at 1280 light - model name now renders DeepSeek-R1-Distill-Llama-8B tightly and still wraps at separators; natd persona table at 320 dark - figure values (+12.3, -1.0, 6.3, 0.002) stay aligned in their labelled rows (td.num keeps tnum); mailroom-ml cohort table at 375 light - right-aligned figures (Documents, accuracy, agreement) keep digit alignment. Score equal at 9 (metric-blind): this is backlog idea 4 from the hand-off, kept on screenshot evidence per the owner's note that such improvements are kept with evidence. All checks pass (197 tests).

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
