# Issue #119: real lead captures and stable image loading

Wave Laboratory and Neuron Atlas now lead with their existing, provenance-recorded screenshots. The same images and descriptive alt text moved upward; no image was generated, mocked up or duplicated.

`site.lua` reads local image headers through Pandoc, emits numeric intrinsic width/height, loads a lead image above the first section heading eagerly, keeps a first image below the fold lazy, and uses asynchronous decoding. Missing or unreadable local images stop the build with their path. External URLs are not fetched by the filter. Existing responsive figure CSS still controls displayed size.

## Other live-project decisions

- AeroGlobe: no lead capture added; the portfolio has no real local capture to promote. Its live link remains available.
- Langton's Ant: retain the real colony and turmite captures beside their explanations. A mode-specific colony scene alone would introduce the broader simulator less clearly than its present opening.
- The Mandalay Bay: retain screenshots after the simulation's purpose and limits, so the reader has context before the interface.
- Existing Wave and Neuron captures are suitable for this task; no replacement capture is required. PR #144 separately proposes full-size raster links and phone-header/chart changes; those are not duplicated here.

## Verification

All render/audit commands sourced `.autoresearch-tools/env.sh`.

- `scripts/hillclimb/hc.sh doctor`: All tools present. Setup had already run for this worktree.
- `"$QUARTO" render --quiet`: succeeded; generated output committed with source.
- `"$QUARTO" pandoc lua tests/lua/test_site.lua`: passed, including local dimensions, lead/below-heading loading, per-document reset, missing-image failure and external-image no-I/O behavior.
- `.venv/bin/python -m pytest -q tests/python/test_image_loading.py`: 3 passed; checks every published content image, both lead positions, the below-fold first image, and the Mailroom-ML collapse-gate alt text.
- `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/browser/test_browser.py -k lead_capture`: 12 passed, 75 deselected. Actual image responses are held until geometry is measured, then released and decoded. At 375/768/1280 in both themes, neither image dimensions nor the following element's position changes by a CSS pixel. Both lead images match their natural aspect ratio and the pages do not overflow horizontally.
- `bash autoresearch.checks.sh`: All checks passed. Both Lua suites; 28 Node tests; 310 Python/browser tests and 686 subtests, 111.38 s. No cases skipped or deselected in this full run. Most assertions use Chromium; Firefox/WebKit cases target charts and recording behavior.
- `.venv/bin/python scripts/hillclimb/kpi.py`: experience_gaps 124 on main → 19 here; images_without_size=0, later_images_not_lazy=0, pages_over_budget=0. Remaining gaps: 14 project social cards and 5 repository-style display titles. This does not close #126.
- Source and published résumé PDFs checked with pypdf: both exactly two pages.
- `git diff --check`: clean.

Twelve actual screenshots in this directory cover both pages at 375, 768 and 1280 px in light/dark. Every image was opened and reviewed for layout and sensitive information. Shared-browser inspection also confirmed the lead captures and absence of horizontal overflow at 375 px.

The first Python test run exposed an incorrect parser-ancestor unpack in the new test. The first delayed-response run exposed premature route removal in the new browser test. Both harness errors were corrected before the successful runs above. An early full-gate run was interrupted to apply that test correction; only the final completed run is counted.

No real phones/tablets, screen readers, live deployment, or full Firefox/WebKit page matrix were checked. The geometry test isolates image loading; it is not a claim of zero layout shift from every possible script, font or external embed.

## Review follow-up

- CodeAnt's inline alt-text finding was valid: the chart's dashed 0.75 line is a
  collapse gate, not an accuracy gate. The source alt text now names the grey
  accuracy bars and the orange collapse-share bars separately, and a regression
  assertion pins the wording.
- CodeAnt's eager-loading nitpick was valid for 14 built pages whose first image
  begins below the first section heading. The filter now eager-loads only a lead
  image above the first section heading; a below-fold first image stays lazy. Lua
  and Python tests cover the below-heading and Div-wrapped cases.
- CodeAnt's sitemap-lastmod nitpick is a known generated-output behavior:
  `scripts/hillclimb/hc.sh` restores timestamp-only churn when the URL set is
  unchanged. This branch keeps main's sitemap because the URL set did not change;
  no code change is warranted.
- The lazy first chart exposed a race in the Firefox/WebKit mobile-report test:
  it called `img.decode()` before the image request had started. The test now
  waits for `complete` and a non-zero `naturalWidth` before decoding; both
  engine cases pass.
