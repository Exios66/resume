# PR108: typed search and artifact filtering

This leg starts at PR107 review-closeout `2425775` and targets `t3/resume-auto-research-loops`. PR107 has 16 resolved inline threads and no pending reviewer assignments at the final read. Its earlier summary nitpicks were checked: the duplicate run-28 row was already absent, and its appendix-navigation test was strengthened (3 targeted tests passed). This does not assert a fresh bot approval.

## Experiments and results

| Run / commit | Behavior | Segment-8 score | Full correctness gate |
| --- | --- | --- | --- |
| 53 / `fda83d9` | Baseline with populated search | 100 | 220 passed, 2 deselected, 611 subtests; 86.12s |
| 54 / `fbfef77` | Route-derived destination labels | 12 | 220 passed, 2 deselected, 611 subtests; 137.16s |
| 55 / `b1e51e7` | Native type selector and shareable query/type URLs | 4 | 225 passed, 2 deselected, 611 subtests; 74.77s |
| Repair / `3eed785` | Preserve the existing print-form hide behavior | 4 | 225 passed, 2 deselected, 611 subtests; 77.00s |

The audit was committed before UI edits and stayed fixed. It evaluates actual calibration matches at each non-layout-only viewport/theme: destination labels must describe their routes; filter subsets must be exact, preserve the query and restore the complete ordered result set. The gate script stayed unchanged. Test additions pin deliberately introduced labels/controls and their required behavior.

Run 54 removes 88 missing-label findings with no added findings. The same eleven calibration destinations and ranking remain. Run 55 removes all eight filter findings, with no added findings. For calibration, the subsets are three reports, two appendices, two case studies and four other pages. The selector measures 46px high; phone controls stack, tablet/desktop controls share a row.

Final audit: 43 pages, axe/layout/error/structure/lint=0, typography=4. These four points are three separator-wrap points in a populated search snippet (375/414 light) and the accepted UW–Madison heading widow. Scores compare only within segment 8; the earlier audit's score of 1 did not inspect populated search. No candidate was discarded.

## Commands

Setup had already completed for this worktree. All render/audit/check/screenshot commands sourced the pinned environment:

```sh
. .autoresearch-tools/env.sh
scripts/hillclimb/hc.sh doctor
node --check autoresearch.audit.cjs
scripts/hillclimb/hc.sh segment 'Typed search results and artifact filtering'
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh log keep 'Baseline typed portfolio discovery'
scripts/hillclimb/hc.sh experiment 'Label search results by destination type' assets/js/site.js styles.css tests/test_browser.py
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh experiment 'Filter search by artifact type with shareable URLs' assets/js/site.js styles.css search.qmd
RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/test_browser.py -k 'search_type_filter or search_without_javascript or search_before_index'
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
git diff --check
git diff fda83d9 -- autoresearch.audit.cjs autoresearch.checks.sh
```

Doctor ended `All tools present.` The final diff command is empty: neither evaluation nor gate definition changed after baseline. The filter candidate was amended to include its new interaction checks, then rendered/audited again before the gate and keep. See the exact keep records and observations in [run 54](evidence/run-54.md) and [run 55](evidence/run-55.md).

The first targeted fallback assertion used the `noscript` wrapper, which Playwright's text matcher skips. Inspecting the rendered HTML confirmed the paragraph; scoping the assertion to `noscript p` passed. The six targeted cases then passed (21 deselected).

Final source review subsequently caught a real print cascade regression. This command failed before the repair, with the form unexpectedly visible:

```sh
RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/test_browser.py -k search_type_filter -x
```

The screen grid rule is now inside `@media screen`; the new print assertion runs in all four phone/desktop theme cases. After rendering/auditing, commit `3eed785` passes the entire gate. Original keep history is retained; the follow-up is a correctness repair of the feature rather than a new scored experiment.

## Visual and interaction evidence

Opened and reviewed **21 actual captures**: two baseline, six label-candidate, ten filter-candidate, and three after the print repair. No private data observed. All evidence is outside the published site.

- [Baseline phone](screenshots/segment-8-before-search-375-light.png) and [desktop](screenshots/segment-8-before-search-1280-light.png).
- [Run 54 phone labels](screenshots/run-54-search-375-light.png) and [desktop dark](screenshots/run-54-search-1280-dark.png).
- [Final phone search](screenshots/run-55-final-search-375-light.png) and [final filtered desktop](screenshots/run-55-final-reports-1280-dark.png).
- [Filtered phone](screenshots/run-55-reports-375-light.png), [empty state](screenshots/run-55-empty-375-dark.png), and [phone keyboard focus](screenshots/run-55-filter-375-dark-focus.png) (375 CSS px at 2× density).
- [Print-media form visibility](screenshots/run-55-print-1280-light.png). This verifies CSS print media, not PDF pagination; pre-existing suggestion-link print styling remains separate backlog work.

Screenshots used `hc.sh shot 'search.html?q=calibration' <width> <theme> run-54-search-<width>-<theme>` and the equivalent run-55 names, at 375/768/1280 in light/dark. Filtered URLs add `&type=report`; the empty capture uses `q=zzzznothing&type=appendix`. The final print capture uses the repository Playwright runtime with `page.emulate_media(media='print')`, asserts the form is hidden, and saves an actual browser screenshot.

The collaborative browser on the Pages-prefix simulation confirmed unchanged match count, correct route labels, report-link navigation, native type selection, q/type URL updates, no page overflow and Tab focus on the selector with a 2px visible outline. Arrow/Enter attempts did not establish changed native-picker selection in the preview, so no keyboard-choice pass is claimed. Browser tests establish exact subsets/order/restoration, reload/invalid URL handling, empty/Escape behavior, delayed/failed index readiness, no-JavaScript fallback navigation and print form visibility at both widths/themes. The full suite also checks the site at dev-root and simulated `/resume/` deployment URLs.

## Merge order

[Saved stack simulation](pr108-stack-validation.json): current main `13c9afb`, PR107 `2425775`, candidate `3eed785`. `git merge-tree --write-tree` plus an unreferenced `git commit-tree` object simulates merging PR107 first, then this branch. Both merges are conflict-free and the resulting tree matches the candidate. No branch, merge or deployment was changed by the simulation.

Keep PR108 based on PR107 until the parent lands. With merge ancestry preserved, fetch/update and retarget to main. After a squash/rebase merge, transplant only child-leg commits onto updated main before retargeting; original parent boundary is `24257754f420fa3fd2fcd89012019b99283a2642`. Recheck if either side changes. See [the leg plan](search-discovery-plan.md).

## Limits and next work

Native Linux, Firefox/WebKit, physical devices, screen readers, external destinations, live hosting and actual merge/deployment remain unchecked. Browser screenshots do not establish every interaction or printed-page layout. No live publication or merge was performed.

Next: informative search excerpts and their separator wrapping; evidence-first report openings; project artifact displays; chart-to-table evidence trails and validated run comparisons. These hypotheses and their required evaluations are in [the creative research queue](search-discovery-plan.md).
