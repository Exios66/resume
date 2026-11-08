# MapReduce review checkpoints (self-review)

## Before candidate1
- Official pinned evaluation and benchmark README agree on17.58/11.24s medians, three runs, saved fixed ordering. Preserve not-drift-controlled limitation and shared-VM context.
- Reuse existing zero-based bars, native source table, source-row readout and no-JS links; add no new renderer for duration. No median difference/relative-effect calculation or claims about independent machines.
- Planned tests: exact mark values, three-run/fixed-order context, full shared chart navigation/no-JS/print tests and native numbered citation target.

## Before candidate2
- Mean−0.11 and interval−0.38/+0.16 are paired estimates from ten interleaved pairs, not the difference of the separate on/off medians. Zero crossing is essential.
- New interval renderer must enforce bounds containing mean and axis containing all bounds/zero; source precision preserved. Plan geometric tests for point/zero inside whisker, invalid-bound and clipped-axis failure, empty input and single-estimate support.
- Direction is explicitly on-minus-off: negative faster, positive slower; do not prove zero cost. Preserve source/control/keyboard/print behavior.
- Scratch code review removed a redundant tooltip assignment before implementation. No code or audit change needed to rescue a measured result.

## Duration screenshot checkpoint
The first candidate passed253 tests/622 subtests (155.94s) but phone screenshots clipped both bar ends, hiding their relative lengths. Refine within the same idea before its single keep decision:320-unit geometry with readable tick sizes, both value labels visible without sideways scroll at375px. Preserve wide-chart arrow-key checks, and add the precise no-overflow expectation for compact charts. Plan the interval as a compact signed plot too, so its mean, bounds and zero reference can be seen together on phones. Audit remains unchanged.

## Interval screenshot checkpoint
The first interval render scored0 and unit/geometry checks passed; its full gate was interrupted to apply visual-review refinements before the single keep decision. Remove the generic scroll cue where the compact plot fits, shorten unused final-row plot space, and move sign/zero-cost interpretation before the plot so the limitation is read alongside the claim. Keep320px overflow guidance. Re-render/audit and full checks are required on the refined commit; do not claim the interrupted gate passed.

## Final interval and pre-publication self-review
- Final source211e012: interval point/bounds/reference positions agree with the pinned source table and independent fixed audit fractions. Unit guards reject excluded estimates/clipped axes/empty interval input; default chart row requirements remain intact.
- All8 final interval captures reviewed, with caveats before the figure, correct zero crossing, readable values and no unnecessary normal-phone scroll cue. Print keeps exact source values; forced colors retains visible marks. Native citation2/return path exercised in the collaborative browser.
- Full gate:257 tests,2 deselected,634 subtests,229.57s, no warnings. Earlier request-thread teardown warning is confined to the duration gate; no warning in this final gate.
- Source render/diff reviewed for escaping, unique targets/row identities, plot widths, default chart compatibility and precise test changes. No valid unresolved implementation finding at this checkpoint. Final GitHub review request/thread enumeration follows publication; this record does not claim independent review or bot approval.
