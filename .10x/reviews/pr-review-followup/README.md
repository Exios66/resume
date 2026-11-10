# Review follow-up verification — 2026-11-10

Merge order: #131 → #132 → #133 → #134 → #135 → #129. Each branch contains its predecessor; use merge commits in order to preserve ancestry. No PR was merged by this workflow.

## Findings

- #131: the general concern about missing rendered CreativeWork is stale. The current head already contains the generated markup on all 14 case studies. Three structured-data tests pass.
- #132: accepted the general headroom wording finding. Documented the actual page and shared-asset margins.
- #133: accepted inline thread PRRT_kwDOU_Onzs614qoc (doctor silently selected a different cache), plus the general finding that fake setup probes did not distinguish engines. Removed the cache fallback from doctor and checks; added independently modeled client/engine readiness and regressions for missing Firefox/WebKit and cache selection.
- #134: accepted the general AltGr finding, duplicate missing-JavaScript ARIA findings, and hint-color finding. Installed semantic metadata with the handler, allowed AltGraph slash, inherited link color, and added browser regressions.
- #135: addressed the general docstring coverage warning on the five undocumented changed test functions. Preserved all earlier features through the file relocation, including moving the new page-budget and structured-data tests.
- #129: accepted five inline threads representing three defects: live reduced-motion changes (PRRT_kwDOU_Onzs614H_p, PRRT_kwDOU_Onzs614IN5, PRRT_kwDOU_Onzs614RDZ), the half-visible threshold (PRRT_kwDOU_Onzs614RDc), and manual pause preservation (PRRT_kwDOU_Onzs614RDf). Browser tests exercise real media events and observer behavior across Chromium, Firefox, and WebKit at 375 and 1280 CSS px.

## Exact commands and results

Run from the repository root unless stated otherwise. Before rendering or auditing, source the generated environment.

```sh
bash scripts/setup-agent.sh
. .autoresearch-tools/env.sh
scripts/hillclimb/hc.sh doctor
```

Setup ran in both used worktrees. The final setup verified Chromium, Firefox, and WebKit for both Node and Python clients. Doctor ended with `All tools present.`

On #131, before the file relocation:

```sh
. .autoresearch-tools/env.sh
.venv/bin/python -m pytest -q tests/test_structured_data.py
```

Result: 3 passed.

On #133, before the file relocation:

```sh
. .autoresearch-tools/env.sh
.venv/bin/python -m pytest -q tests/test_agent_setup.py tests/test_page_budget.py
```

Result: 15 passed.

On #134, before the file relocation:

```sh
. .autoresearch-tools/env.sh
"$QUARTO" render --quiet
"$QUARTO" pandoc lua tests/test_site.lua
RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/test_browser.py -k 'slash or no_script or unavailable_script'
bash autoresearch.checks.sh
```

Lua checks passed; 4 targeted browser tests passed; full gate: 278 passed, 634 subtests passed. Log: checks-134.log. A standalone `lua` command was unavailable; Quarto's bundled Pandoc Lua ran the required checks successfully.

On #135, in /Users/morningstar/.t3/worktrees/resume/t3-easy-issues:

```sh
. .autoresearch-tools/env.sh
"$QUARTO" render --quiet
bash autoresearch.checks.sh
.venv/bin/python scripts/hillclimb/kpi.py
```

Full gate: 279 passed, 634 subtests passed. Log: checks-135.log. The diagram regression visits all 15 pages containing inline diagrams. KPI: experience_gaps=125, pages_over_budget=0, projects_without_structured_data=0.

On final #129, after incorporating all five preceding PRs:

```sh
. .autoresearch-tools/env.sh
"$QUARTO" render --quiet
RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/browser/test_browser.py -k recording
bash autoresearch.checks.sh
.venv/bin/python scripts/hillclimb/kpi.py
git diff --check
```

6 targeted video cases passed. Full gate: 285 passed, 634 subtests passed; Lua checks passed; 28 Node tests passed. Log: checks-129.log. KPI: experience_gaps=125, pages_over_budget=0, projects_without_structured_data=0. Shared gzip CSS=15,063 bytes; JavaScript=6,493 bytes. No validation failures remain. Generated sitemap timestamp-only changes were restored after renders.

## Evidence and coverage limits

The shared browser exercised slash navigation and focused search at 1280×800 and 375×812 CSS px. Screenshots: search-hover-1280-light.png, search-focus-1280-light.png, search-focus-375-light.png. Recording: search-desktop-mobile.mp4. Video screenshots: video-1280-light.png (1280×900 viewport) and video-375-light.png (375×812 viewport). Mobile PNGs use the browser's 2× display scale. Evidence stays outside docs/. Screenshots were inspected; the recording's page states were inspected. The video contains the existing public source recording's workstation hostname, as already documented on #129; no credentials or private session links were added.

The full suite primarily exercises Chromium, with the repository's targeted Firefox/WebKit checks and the six new video cases in all three engines. Tests cover both themes and multiple widths through the existing suite. AltGr is modeled using a synthetic modifier state; no physical international keyboard or real-device pass was performed. Manual pause is exercised through the browser's media pause API, which dispatches the same pause event as native controls. External forms were not submitted and no external state was tested through site links. Review summaries are not resolvable GitHub threads; their findings were investigated and recorded here. No audit scoring logic was changed.
