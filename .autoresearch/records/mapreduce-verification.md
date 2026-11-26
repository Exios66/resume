# MapReduce visualization leg — PR111

Base main bd2605c (merged PR110), fixed-audit commit 3ff993a. Final visual candidate 211e012. Review-remediated source 06622bf; later metadata commits archive evidence only.

## Measured history

| Run / segment 15 | Source | Score | Full gate |
|---|---|---:|---|
|68 baseline|3ff993a|16|249 passed,2 deselected,611 subtests,92.42s|
|69 duration comparison|e08048a|8|253 passed,2 deselected,1 warning,622 subtests,143.78s|
|70 signed paired interval|211e012|0|257 passed, 2 deselected, 634 subtests passed in 229.57s (0:03:49)|

No added findings for either keep. The audit was committed before product edits and stayed fixed throughout segment 15. Correctness gate definition unchanged; tests were added for intentional behavior and existing assertions extended precisely for compact charts. Wide-chart scrolling assertions remain intact. All 43 pages are included in the broad audit and full browser gate.

## Source and design review checkpoint

Official pinned sources at 4dd1ca4045b2b9f49a63a8f6e757b20b6fb32387 were read directly: [evaluation](https://github.com/Exios66/MapReduce-Reloaded/blob/4dd1ca4045b2b9f49a63a8f6e757b20b6fb32387/docs/evaluation.md#backup-tasks-54), [benchmark notes](https://github.com/Exios66/MapReduce-Reloaded/blob/4dd1ca4045b2b9f49a63a8f6e757b20b6fb32387/bench/README.md#e2-backup-tasks-and-a-straggler). The local Firecrawl service refused connections twice; direct official-source browsing was the fallback. No upstream benchmark or statistical analysis was rerun.

Review separates E2 with an injected straggler (three-run medians, fixed setting order, not drift-controlled) from the no-straggler experiment (ten interleaved pairs, mean paired difference and reported 95% interval). Do not subtract the separate medians to obtain the paired mean. The shared four-worker VM and paper-scale limitations stay intact. New precise duration values match the pinned source; the original overview retains its rounded values. Inline numbered source notes link the pinned artifacts.

This is a per-step self-review, not an independent-agent or bot approval. See mapreduce-checkpoints.md and mapreduce-visualization-plan.md for source/design, post-render diff, visual/function and pre-keep checkpoints.

## Implemented behavior

- Duration bars have a zero baseline and show both ends/values on phone layouts. Source rows retain the median and run count, and the adjacent prose retains fixed-order/VM limitations.
- New interval renderer separates the mean dot, interval whisker/endpoints and dashed no-change reference. Bounds must contain the estimate; the axis must contain zero and every bound. A single estimate is supported while existing chart kinds still require at least two rows.
- The compact signed view fits normal phone widths with readable labels. Sign interpretation and the zero-cost limitation precede the figure. The source table/readout retains mean, both bounds and pair count. The interval describes uncertainty in the mean, not raw run variability.
- Existing focus/hover row linking, native source/return navigation, no-JS access and print fallback apply to all three MapReduce charts. Existing architecture, scaling data, work-in-progress state and unrun LATE caveat are unchanged.

## Refinement checkpoints and limitations observed

The first duration version passed 253 tests/622 subtests but screenshots showed both bar ends clipped on phones. Before its single keep decision, compact 320-unit geometry and readable ticks were added, the benchmark rerun, then the full gate on e08048a passed. That gate reported one local test-server request-thread teardown warning (BrokenPipe/Bad file descriptor); no assertion failed. The warning is recorded, not hidden.

The initial interval scored 0 and its unit tests passed. Screenshot review prompted moving interpretation before the figure, removing an unnecessary scroll cue at normal phone widths and trimming unused final-row space. Its full gate was interrupted (82 tests/204 subtests had passed); it was not claimed as a complete pass. The refined candidate was rendered/audited and fully checked before keep. No product candidate was discarded; both were refined inside their original ideas before a single keep/discard decision.

A direct Lua probe initially used an ambiguous multi-architecture Pandoc glob, and a standalone lua executable is absent. Selecting the first bundled Pandoc as the official gate does ran the unit tests successfully. Full-gate Lua results, not those failed probes, establish validation.

## Exact workflows

Setup was completed once for this worktree with bash scripts/setup-agent.sh. Source .autoresearch-tools/env.sh before each render/audit; scripts/hillclimb/hc.sh doctor ended All tools present.

```sh
. .autoresearch-tools/env.sh
scripts/hillclimb/hc.sh segment 'MapReduce backup effects and uncertainty'
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh experiment 'Visualize MapReduce backup duration with experiment context' projects/mapreduce-reloaded.qmd tests/test_charts.py tests/test_browser.py
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh experiment 'Show MapReduce paired uncertainty around no change' scripts/charts.lua projects/mapreduce-reloaded.qmd styles.css tests/test_charts.py tests/test_charts.lua tests/test_browser.py
scripts/hillclimb/hc.sh checks
python3 -m http.server 8769 --bind 127.0.0.1 --directory docs
.venv/bin/python /tmp/capture-mapreduce-interval.py
```

The capture script is archived as capture-mapreduce-interval.py; run on this source revision to reproduce it. hc.sh shot captured run 69 at 375/1280 in both themes with --at '#mr-backup-duration' --height 1100. Interval captures cover 375/768/1280 in both themes, forced-colors and CSS print. All 17 archived images were opened and checked for private data; only public portfolio content appears. Per-run evidence lists finding deltas, screenshot paths, final gate summaries and reviewer notes.

The full gate covers existing dev-root and simulated /resume/ deployment cases, all pages, no-JS chart navigation, row/mark agreement, native source-note access, print retention and the new geometry/guard cases. Collaborative phone interaction selected the Backups on row and showed its exact median/run count without overflow. Screenshot viewport widths simulate responsive layouts; they do not prove physical-device or assistive-technology behavior.

Not checked: upstream experiment reruns, independent statistical/source-data reproduction, full SVG contrast, Firefox/WebKit, real devices, screen readers, fresh native Linux, native printer dialogs or PDF pagination. Actual live deployment is a separate post-merge smoke check. Zero describes the fixed measured criteria.

## Follow-on research

MapReduce is now integrated into the main uncovered-aspects queue. Next project ideas: source-pinned 1/2/4-worker trajectories with observed ranges, shuffle-phase traces with sampling semantics, failure/recovery comparisons with fixed-order and clock-offset limits, and a clearly illustrative mechanism explorer with a no-JS fallback. Each requires a new fixed evaluation before implementation; see mapreduce-follow-on.md. Essential SVG contrast, broader preference coverage, report structure, artifact labels, performance, metadata quality, portability and PDF pagination remain open.

## PR review remediation and evaluation segment 16

GitHub enumeration returned two unresolved inline threads: CodeAnt's fractional-width failure (ACCEPT) and CodeRabbit's explicit interval-domain expansion (ACCEPT). General CodeAnt comments also identified a missing CPU-condition audit guard (ACCEPT) and an unnecessary scroll hint (already addressed by final visual candidate 211e012). No requested reviewers or change-request reviews were present at enumeration. See pr111-review-remediation.md for native IDs and verification.

The fractional-width failure was reproduced before patching: `plot-width="320.5"` reached integer SVG formatting and failed. Commit ecbabf7 rejects fractional widths before rendering and adds a Lua regression. Audit-only commit 58b3897 starts a new segment, requires the source's 0.2 CPU condition and rejects non-finite/missing interval cells; its browser regression mutates each condition and verifies rejection. Segment 16 baseline scored 0 across 43 pages (audit 77.3s/render 28s); full gate at 58b3897: 258 passed, 2 deselected, 634 subtests in 234.75s, no warnings. Logged run 71 is this baseline, not a visual improvement or a rewrite of segment 15.

Commit 908d5aa preserves explicit interval min/max while retaining nice ticks for inferred ends. Regression cases cover lower-only, upper-only and both non-round bounds plus the no-change reference position. The first assertion used tighter tolerance than the renderer's existing one-decimal SVG coordinates; it was corrected to half the serialization step before the successful Lua run. The authored MapReduce domain is unchanged, so these fixes do not change the 17 reviewed captures. The already-published intermediate 99ce1d9 is retained via ordinary merge reconciliation 52e40a9; no force-push or unknown remote change was discarded.

Final source gate and rerender result: 258 passed, 2 deselected, 634 subtests passed in 166.61s (0:02:46); All checks passed; no warnings, exact source commit 06622bf.

Additional commands:
```sh
. .autoresearch-tools/env.sh
review_quarto_dir="$(dirname "$(readlink -f "$QUARTO")")"
review_pandoc="$(ls "$review_quarto_dir"/tools/*/pandoc | head -1)"
"$review_pandoc" lua tests/test_charts.lua
scripts/hillclimb/hc.sh segment 'MapReduce reviewed source-condition and numeric guards'
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
```

Additional current-source local smoke: `.venv/bin/python /tmp/check-pr111-live.py http://127.0.0.1:8769/` passed eight cases at 375/1280, light/dark, with/without JavaScript. It checks three chart source-focus round trips, two native citation round trips, exact values, geometry order, compact fit, linked readouts when enhanced, print retention and no page errors. Result: `.hillclimb-evidence/pr111-local-smoke.json`. A fresh collaborative phone inspection also confirmed all interval readout fields, ten pairs and no horizontal scrolling. Generated docs are byte-unchanged after the axis guard fix (sitemap churn settled by hc.sh).

Branch sync: fetched origin; current main bd2605c is an ancestor and remote branch history is incorporated. Only PR111 is open in this repository; it has no requested reviewers. Remote publication and re-fetch follow the final gate.

Checkpoint follow-up 06622bf: rejecting a collapsed authored interval domain prevents division by zero after preserving explicit endpoints. Automatic all-zero intervals still receive an expanded inferred domain. Lua regressions cover automatic expansion, explicit equal ends and a collapsed upper-only bound. The 908d5aa full gate was deliberately terminated during checkpoint refinement and is not a completed pass; the final gate runs afresh. The already-rendered site is unchanged by this input-validation-only guard; current-source rerender/diff verification follows.

Final-source render equivalence: `. "$PWD/.autoresearch-tools/env.sh"; "$QUARTO" render projects/mapreduce-reloaded.qmd` succeeded on 06622bf. Only sitemap lastmod changed; comparison after removing lastmod confirmed equality before settling that generated churn. `git diff --name-only -- docs` then returned empty. The final source gate therefore checked the same generated artifacts. The broad 43-page audit immediately preceding the collapsed-domain guard scored0 (95.5s, render36s); the guard changes invalid author input only. No new visual metric improvement is claimed.
