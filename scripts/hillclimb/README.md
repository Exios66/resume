# Portfolio tooling command map

Start in the repository root. Read `AGENTS.md`, `.10x/status.md`, `.10x/handoff.md`, and the live issue before choosing work. `.github/BUILDING.md` explains the render pipeline; `.claude/skills/portfolio-hillclimb/SKILL.md` owns measured polish experiments.

## Prepare once per worktree

```sh
bash scripts/setup-agent.sh
. .autoresearch-tools/env.sh
scripts/hillclimb/hc.sh doctor
```

Setup synchronizes pinned Python and Node dependencies, verifies all three browser engines for each client, selects Quarto 1.10.19, and writes the shell environment. Source it in every new shell that renders, tests Lua, or audits. Doctor must finish with `All tools present.` Do not rely on an older worktree's environment file: its Quarto path may point into that other checkout. Standalone Lua is optional.

Leave `PLAYWRIGHT_BROWSERS_PATH` unset for Playwright's standard user cache, or set it consistently before setup and all verification. No helper silently switches to an /opt cache. Setup may download browser revisions but does not install OS packages; report a missing host prerequisite rather than declaring success.

## Choose the smallest useful check

Run these after sourcing the environment. Add narrowly required regressions when fixing behavior; do not create tests that merely mirror implementation or repeat the full gate for comment-only changes.

| Changed behavior | Focused command |
| --- | --- |
| Site filter, navigation markup, JSON-LD | `"$QUARTO" pandoc lua tests/lua/test_site.lua` |
| Chart renderer | `"$QUARTO" pandoc lua tests/lua/test_charts.lua` |
| Theme bootstrapping and built icons | `node --test tests/node/theme.test.cjs tests/node/icons.test.cjs` |
| Bootstrap, engine readiness, cache selection | `.venv/bin/python -m pytest -q tests/python/test_agent_setup.py` |
| Rendered structured data or page budgets | `.venv/bin/python -m pytest -q tests/python/test_structured_data.py tests/python/test_page_budget.py` |
| Search, typing, no-script shortcut semantics | `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/browser/test_browser.py -k 'slash or no_script or unavailable_script'` |
| Diagram labels against arrows and borders | `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/browser/test_browser.py -k diagram_text` |
| Recorded video motion, visibility, manual pause | `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/browser/test_browser.py -k recording` |
| Complete correctness gate after a source render | `bash autoresearch.checks.sh` |
| Documentation only | Inspect links/commands against current source, then `git diff --check` |

Render source changes with `"$QUARTO" render --quiet` before checks that read `docs/`. Never hand-edit generated HTML, cache keys or the search index. Inspect sitemap changes: restore timestamp-only churn only when the URL set is unchanged. Keep genuine URL additions/removals.

The complete gate runs Lua and Node tests plus Python/browser tests. Most browser assertions use Chromium. Firefox/WebKit have targeted mobile-chart cases and the recording matrix at 375 and 1280 px. Inspect current parametrization before claiming coverage; do not equate successful installation with a full browser matrix. Native Safari/iOS, Android, screen-reader sessions and physical international keyboards need their own evidence.

## Evidence for an interaction or visual change

```sh
. .autoresearch-tools/env.sh
scripts/hillclimb/hc.sh shot search.html 375 light review-search-375-light --height 812
scripts/hillclimb/hc.sh shot search.html 1280 dark review-search-1280-dark --height 900
scripts/hillclimb/hc.sh shot projects/psychometric-digital-twin.html 375 light review-diagram --at .diagram --height 900
```

These commands serve `docs/` under `/resume/` and write PNGs to `.hillclimb-shots/` by default. `SHOT_OUT` selects another evidence directory. The script captures pages; it does not exercise keyboard shortcuts, media controls or hover states for you. Use the shared browser when available or the relevant browser test to exercise those controls, then capture the actual state. Open every evidence image and check for private data before sharing it. Add 768 px and both themes when the task's acceptance criteria require them. Screenshots supplement behavior assertions.

For ordinary reviews, keep curated evidence in `.10x/reviews/<task>/`. For hill-climb keeps, use `run-N-*` names plus `hc.sh evidence` and the exact-commit check stamp. Preserve logs and explicitly report skipped cases, simulated inputs and untested devices.

## Measured polish versus experience work

- `hc.sh baseline` / `hc.sh experiment` render and run the polish audit; `hc.sh findings` audits the existing build without rendering.
- `hc.sh checks` runs the correctness gate and stamps HEAD. `hc.sh evidence`, `hc.sh log`, `hc.sh snapshot` and `hc.sh restore` manage the measured experiment record; follow the skill's ordering.
- `.venv/bin/python scripts/hillclimb/kpi.py` reads the rendered site and reports `experience_gaps`, its components, transfer sizes and page-budget violations. It does not render or change the site. To pick the next change, read "How to raise each metric" in `.10x/metrics.md`. It lists where each gap comes from, the lever that closes it, and the budgets to protect.
- **Experience-scored segments:** `autoresearch.sh` runs `kpi.py` after the polish audit, so one benchmark prints both metric sets. Start an experience segment with `hc.sh segment "<name>" --metric experience_gaps --gate polish_defects=0`, run `hc.sh baseline`, and the ledger scores `experience_gaps` while refusing to log a run whose `polish_defects` gate fails. Regression tests: `tests/python/test_ledger.py`.
- Ordinary feature/review fixes and documentation updates do not need fabricated polish wins. Keep the audit/check definitions fixed within each measured segment. Never lower thresholds or alter scoring to rescue an experiment.

## Reviews, shipping and handoff

Fetch all review-thread pages and general review comments, including CodeAnt nitpick summaries. Record each valid fix, verified stale finding or justified rejection. Resolve only fixed, verified, pushed threads; post dispositions for non-thread summaries. Read check output when a review is cancelled, and distinguish cancelled/skipped reviews from completed analysis.

Before an authorized stacked merge, record expected head SHAs and validate ancestry. Merge each approved layer with `gh pr merge <number> --merge --match-head-commit <sha>` after its checks and reviews are ready. Retarget the next layer to main after its parent lands, confirm the current diff/head and mergeability, then continue. Do not delete branches while they are still PR bases. Do not bypass a failed required check. Finish with a main-branch render/check when integration warrants it and verify that generated output matches the committed site.

Close only fully shipped issues. Keep partial tracks open with checked completed subtasks, merged PR links, evidence, remaining work and limitations. Update `.10x/status.md` and `.10x/handoff.md`. Use app-native PR watching for asynchronous checks rather than polling. Never put private session URLs or tool attribution footers in public messages.
