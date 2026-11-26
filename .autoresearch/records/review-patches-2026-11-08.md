# PR #107 review patches and validation

The review baseline was `50d0da4` (site code from `0ca9b3b`). Fourteen inline threads were open, with no pending reviewer assignments. This patch addresses every baseline thread, including documentation clarifications and the two comments superseded by completed runs.

## Patches

- Synchronize the complete Python requirements on every setup, propagate failures, pin Node Playwright to the installed Python requirement, and launch Chromium through both clients. Doctor now checks pypdf, matching Playwright versions, both browser launches and Quarto 1.10.19.
- Enforce Quarto 1.10.19 for overrides, PATH and local installations; select ARM64 for aarch64/arm64 Linux; strip the Linux archive's release-directory prefix. Create the tools directory before probing locale and write a safely quoted environment file with a deterministic C locale.
- Exclude node_modules, .venv and autoresearch tool/data directories from Quarto rendering/resources. A real render removed all 19 tracked Playwright assets (3,005,955 bytes) and the untracked copied .venv assets. A regression rejects local dependencies and research data in docs/.
- Preserve a labelled code span's ID only on its first split fragment; retain classes, data attributes and text on every fragment. The real Pandoc regression verifies one anchor instead of three.
- Correct the run-25 table to the ledger's 29 points; preserve the append-only ledger. Link available archived screenshots from evidence records and remove trailing whitespace from captured metric lines. Update the run-46 completion summary and backlog (the second widow was fixed in run 49).
- Document Chromium cache locations/override and clarify the RVL result header to “Result (tuning slice unless stated)”. No project values changed.

## Commands and results

Environment setup and idempotent rerun:

```sh
bash -n scripts/setup-agent.sh
bash -n scripts/hillclimb/hc.sh
bash scripts/setup-agent.sh
. .autoresearch-tools/env.sh
scripts/hillclimb/hc.sh doctor
```

Both clients use Playwright 1.64.1 and both Chromium launches succeed. Doctor ends `All tools present.` A second setup run also succeeded. Quarto is 1.10.19 and env.sh supplies LC_ALL=C.

Targeted regressions:

```sh
.venv/bin/python -m pytest -q tests/test_agent_setup.py tests/test_tables.py
RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/test_deployment.py
```

Eight bootstrap/table regressions passed. Bootstrap tests use isolated tools, fixture archives and the real tar extractor: macOS flat archive, Linux amd64/aarch64/arm64 nested archives, stale browser cache, existing incomplete venv, install failure, wrong override/PATH version and paths containing spaces. These fixtures do not establish native Linux execution.

The first deployment run passed its 14 HTTP/browser cases but failed the artifact-exclusion assertion because .venv assets were still copied. The exclusions were extended; rendering then passed that assertion. The final full gate includes all 15 deployment tests.

Render, final gate and unchanged audit:

```sh
"$QUARTO" render --quiet
scripts/hillclimb/hc.sh checks
AXE_PATH="$PWD/.autoresearch-tools/node_modules/axe-core/axe.min.js" node autoresearch.audit.cjs
git diff --check
```

- Full gate: **220 passed, 2 deselected, 611 subtests passed in 100.63s**; Lua/Node checks also passed. `All checks passed.`
- Fixed audit: all **43 pages**, **polish_defects=1**, axe/layout/error/structure/lint=0, no new findings (55.6s). Only the accepted UW–Madison heading widow remains.
- The benchmark and correctness-gate definitions were unchanged. Review remediation is not a new score-seeking experiment.
- Sitemap date-only churn was restored after confirming the list of page URLs was unchanged. The complete merge-base diff passes `git diff --check` after metric-line whitespace cleanup.

## Deployment compatibility

`tests/test_deployment.py` serves the real build at both a dev root and `/resume/`, exercises directory indexes and every locally referenced link/asset, and tests navigation, search, theme persistence, chart arrow scrolling, tooltip visibility/Escape, PDF response type/signature and nested custom-404 recovery. Browser cases run at **375, 768 and 1280 px in both themes**. The custom-404 test checks project-prefix recovery links; the root-dev asset crawl excludes the production-specific 404 template.

The collaborative browser additionally checked the changed RVL table under the Pages-prefix server: labelled block rows at 375, the comparison grid at 1280, the updated header/data-label and no page overflow.

## Reviewed visual evidence

```sh
for width in 375 1280; do
  for theme in light dark; do
    scripts/hillclimb/hc.sh shot projects/rvl-cdip-classifier/appendix.html "$width" "$theme" "pr107-review-result-$width-$theme" --at table --text 'Short baseline'
  done
done
```

All four actual screenshots were opened and checked for private data. The column scope is readable in both desktop headers and phone row labels, the v0 control-slice exception is explicit, and surrounding content remains readable.

- [Phone light](screenshots/pr107-review-result-375-light.png)
- [Phone dark](screenshots/pr107-review-result-375-dark.png)
- [Desktop light](screenshots/pr107-review-result-1280-light.png)
- [Desktop dark](screenshots/pr107-review-result-1280-dark.png)

## Limits

Native Linux bootstrap was not run: the installed Docker CLI's daemon did not respond within a minute, and the diagnostic was stopped. Platform/archive handling is covered by fixtures; the actual macOS worktree setup and browser clients were verified. Firefox/WebKit, physical devices, screen readers, external destinations, live GitHub Pages configuration/CDN/headers, and an actual merge/deploy were not checked. Screenshots supplement assertions; they do not prove every interaction works. Live verification remains in the TODO backlog.
