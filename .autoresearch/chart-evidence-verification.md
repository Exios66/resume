# Visualization evidence leg — PR110

Base: main merge 689b6a4 (PR109), following PR107/108. Source candidate for the final gate: 3ed86e7. Later commits archive evidence only.

## Fixed segments and decisions

| Segment/run | Source commit | Measured score | Full correctness gate |
|---|---|---:|---|
|13/63 baseline|5353161|112|233 tests/611 subtests,77.37s|
|13/64 native chart/table round trip|ab7ca7a|56|237 tests/611 subtests,75.46s|
|13/65 coordinated marks, rows and readout|e5c3d67|0|241 tests/611 subtests,79.73s|
|14/66 stacked-caption baseline|94a8d3c|6|241 tests/611 subtests,80.33s|
|14/67 caption reading width|3ed86e7|0|249 passed, 2 deselected, 611 subtests passed in 80.98s (0:01:20)|

Two new fixed evaluations were committed before their respective product edits. The first stayed unchanged through runs 64–65. Screenshot review then exposed an existing narrow stacked caption; its CSS and caption markup predate this leg. A separate audit commit and baseline established segment 14 before repair. Scores are comparable within a segment only. Correctness gate definitions were not changed.

The first native-link implementation passed tests but displayed descriptive span text in screenshots. It was refined within the same idea to use accessible names, rendered/audited and checked again before its single keep decision. Superseded candidate hashes 9faa313/bf036e2 were not pushed as keeps. An earlier audit-edit command failed before any product edit; its interrupted, unscored render was rerun successfully. No product candidate was discarded in this leg.

## Behavior and data fidelity

All seven table-generated charts retain their original data, axes, labels, legend, adjacent caveats and source tables. Native View exact values/Return to chart links work without JavaScript and land focus on the table/caption. The persistent source panel derives text from that same table. Lua emits a one-based row index for every mark, including each strip replicate; JavaScript uses that identity rather than fuzzy label matching. Keyboard focus and pointer interaction coordinate both directions without hiding other data or automatically scrolling the other view.

The readout exposes unplotted context such as NATD's persona type and sample size, original precision for both F1 endpoints, and each benchmark's machine/runtime plus all reruns. No new research claims, intervals, results, upstream verification or numeric transformations are introduced. More phone height is accepted for context; wide plots still scroll sideways. Print hides the additional panel/navigation/highlights and retains plots and original tables. Forced-colors emulation keeps visible evidence outlines and readout text; it is not a complete contrast or assistive-technology audit.

Run 67 makes block-layout stacked captions use the available reading width. Native desktop caption layout and authored caption text remain intact. The caption explains that Node engine timing is not browser frame rate, so reducing its vertical word-by-word wrapping preserves an essential limitation.

## Commands and results

Setup was already completed once for this worktree with bash scripts/setup-agent.sh. Every render/audit sourced .autoresearch-tools/env.sh. scripts/hillclimb/hc.sh doctor ended All tools present.

```sh
. .autoresearch-tools/env.sh
scripts/hillclimb/hc.sh segment 'Chart evidence navigation and coordinated source reading'
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh experiment 'Connect charts to exact source tables with native return navigation' scripts/charts.lua styles.css tests/test_charts.lua tests/test_browser.py
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh experiment 'Link chart marks and source rows with a persistent evidence readout' scripts/charts.lua assets/js/site.js styles.css tests/test_browser.py
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh segment 'Preserve full reading width for stacked table captions'
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh experiment 'Restore reading width for stacked table captions' styles.css tests/test_browser.py
scripts/hillclimb/hc.sh checks
python3 -m http.server 8769 --bind 127.0.0.1 --directory docs
.venv/bin/python .autoresearch/capture-chart-evidence.py
.venv/bin/python .autoresearch/inventory-site-evidence.py
```

Capture workflow is the run 65 workflow, originally run from /tmp against its candidate build. Re-run on that revision to reproduce its historical screenshots. hc.sh shot commands captured the baseline, run 64 and run 67 with --at figure.chart or --at table.chart-source and --height 1000/1100. Per-run evidence records list exact image paths, finding removals/additions and check results. All 35 archived screenshots were opened and checked for private data. They show public portfolio content only.

New browser tests pin intentional interactions: no-JS Enter/focus round trips across all seven charts at 375/1280 in both themes; every mark's source-row values and reverse table focus, all strip replicates, and print retention at those widths/themes; caption width/text at 375/414/768/1280 in both themes. Existing all-page, dev-root and simulated /resume/ deployment checks run in the full suite. The collaborative browser also exercised phone pointer round trips and Enigma table-row selection, confirming the matching mark and full source readout without page overflow. Earlier preview clicks timed out against a stale pre-render document; a new document navigation corrected that and passed.

## Broader inventory and remaining scope

The stable build inventory found 43 pages, no missing descriptions/canonical links/og:image fields, unique titles and no missing local destinations or fragment targets. Five local font files total 225640 bytes on disk; this is not measured network transfer. The inventory and its script are archived. No metadata-quality, image-resolution, CLS, paint or external-source claims follow from presence checks.

See uncovered-aspects-queue.md for prioritized follow-on objectives: SVG contrast, uncertainty-aware evidence storytelling, report finding/evidence/constraint structure, saved-figure source navigation, artifact labels, preference behavior, performance, metadata quality, deployment portability and PDF pagination. This leg covers seven generated charts, not every saved figure or simulation.

Not checked: Firefox/WebKit, physical devices, screen readers, fresh native Linux, upstream source reauthentication, native print dialogs/physical printing or PDF pagination. Live deployment is a separate post-merge smoke check; local root/subpath simulation does not prove the live CDN.
