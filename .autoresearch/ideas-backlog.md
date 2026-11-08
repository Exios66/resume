# Ideas backlog (prune as they land)

Done: copy button, scroll-region access, stacked tables, 404 page, résumé contact, search titles, tap targets,
tiny text, separators, balanced headings, wbr in table-cell code, stack classifier (prose column 45+, row label
12+, two-row grids, five-column grids), sticky first column + scroll edge, scoped tabular-nums, AUC / band /
v0 content fixes, labelled prose rows, compact phone header, duplicate back link removed, mobile checks at
375 px dark (segment 4).

Open:
1. Layout findings are 0. The one accepted finding is the "Graduate research, UW–Madison" heading widow
   (UW–Madison is a single unit). The second widow found in run 46, the Writing title at 768 px, was fixed in run 49.
2. Projects category chip styling is deferred: browser measurement shows 44px targets and a 4px row gap already. Establish a navigation benefit before changing presentation.
3. Completed in runs 51–52: report contents columns align, reading order matches the grid, and full-cell links provide 44px targets with hover/focus feedback.
4. Content consistency (owner facts needed): unify date formats; "Simulations" shortcut vs "Side projects &
   interests" heading; expand "DSHB" on first use.
5. Audit coverage: real Firefox/WebKit, real devices and screen readers were never checked.
6. New audit segments from issue 106 still available: performance budget, chart and
   diagram contrast, link and asset integrity, metadata (titles, canonical, og:image), print layout, reduced
   motion, other engines.


## Next batch after runs 44–49
- Completed: new 414/768 coverage, tablet prose tables, undergraduate credential structure, SVG rendered label-size coverage and readable figures; PR candidates now include durable screenshots and quantitative keep rationale.
- Next visualization audit segment: SVG text/essential mark contrast in both themes (axe excludes much SVG), then forced colors and reduced motion checks. Keep the audit fixed within each segment.
- Completed: report contents alignment and 44px targets, measured in segment 7 (211 → 127 → 1). Next: report opening structure, project artifact labels and search page-type labels; define their evaluation before experimenting. Category chips remain deferred pending a demonstrated benefit.
- Prose backlog: shorten repeated introductory inventories and make report takeaways easier to scan, preserving all claims and source-backed metrics. Owner facts still needed for the open content-accuracy issues.
- Continue screenshots for every progressing PR candidate, with before/after metrics and reason for keeping it. Never publish evidence under docs/.


## PR review and deployment readiness TODOs
- [x] Validate the complete merge-base diff of PR #107 and triage every unresolved inline review against the current HEAD. Fix confirmed code defects in a separate implementation pass, then rerun validation and resolve only addressed threads.
- [ ] Verify fresh-clone setup on macOS and Linux (amd64 and aarch64), pinned Python/Node Playwright compatibility, browser installation, Quarto extraction/version selection and locale initialization.
- [x] Remove accidentally published build/test dependencies from `docs/` and prevent them from returning during rendering.
- [x] Reconcile review evidence paths and stale experiment/backlog summaries against the append-only ledger and archived screenshots.
- [x] Test the built site on a local dev server: assets, navigation, search, theme persistence, report controls, figures and résumé download at phone/tablet/desktop widths.
- [x] Test deployment compatibility in a GitHub Pages simulation: serve the build under `/resume/`, use directory index URLs, return the custom 404 for missing nested paths, and verify nested links, CSS/JS/font/image/PDF URLs, canonical metadata and browser errors.
- [x] Record the dev-server and simulated-deployment results and coverage limits; require the same checks on the final merge candidate. A local simulation does not prove the live CDN, Pages configuration or deployed headers.
- [ ] After an authorized merge/deploy, verify the actual portfolio URL against the built artifact and repeat the critical navigation/search/theme/404/PDF smoke checks.


### Confirmed review follow-up at PR HEAD `0ca9b3b`
- [x] Fix the Linux Quarto extraction path: the upstream v1.10.19 archive contains `quarto-1.10.19/`, while setup validates `.autoresearch-tools/bin/quarto`.
- [x] Recognize Linux `aarch64` as ARM64 rather than falling through to the amd64 archive.
- [x] Install/validate the Chromium revision required by both Playwright clients. Current Node 1.65.0 expects revision 1254; pinned Python 1.64.1 expects revision 1248. The cache-directory wildcard and Node-only doctor do not establish Python readiness.
- [x] Synchronize all pinned test requirements in an existing venv, including pypdf; propagate installation failures instead of reporting readiness.
- [x] Validate the pinned Quarto 1.10.19 version for both the QUARTO override and installed PATH selection.
- [x] Create `.autoresearch-tools/` before writing the Lua locale probe when Quarto is already installed. A fresh worktree otherwise skips the required C-locale detection.
- [x] Remove the 19 Playwright assets (3,005,955 bytes) accidentally committed under `docs/node_modules/` and exclude test/build dependencies from Quarto resource discovery.
- [x] Preserve a labelled inline code span's ID on only one split fragment. Pandoc reproduction currently emits three `id="code-ref"` nodes for `long/path/component`.
- [x] Link archived evidence records to the tracked screenshots rather than ignored `.hillclimb-shots/` paths.
- [x] Reconcile the run-25 table score (20) with its append-only ledger result (29), and prune the completed 414/768 viewport backlog item. Document that Chromium may be installed in the user cache outside the worktree.

Initial validation (review only, no code fixes or commits): `scripts/hillclimb/hc.sh doctor` passed; `bash autoresearch.checks.sh` passed 197 tests and 611 subtests, with 2 deselected (43.26s). Direct `node autoresearch.audit.cjs` passed with polish_defects=1, layout/axe/errors/structure/lint=0 across all 43 pages. The local `/resume/` simulation returned all 101 referenced local URLs with HTTP 200, directory indexes with 200, the PDF with application/pdf, and a missing nested route with the custom 404 and working `/resume/` recovery links. Browser smoke checks confirmed theme persistence, search (11 calibration results), and phone chart scrolling/tooltip on the dev server. This does not verify a fresh Linux build or the live GitHub Pages deployment.

Review baseline before patches: 14 unresolved threads, 2 already resolved. The omitted Writing heading-widow and pending run-46 comments are superseded by runs 49 and 46 respectively; do not reintroduce the resolved widow. The RVL result-column heading remains a low-risk clarification of a pre-existing mixed-slice column. CodeAnt skipped the large PR; CodeRabbit's latest check is neutral/rate-limited, not a fresh approval. GitGuardian passed. No pending reviewer assignments.


Patch validation supersedes that initial review: all confirmed code/documentation findings are patched, including the RVL result-column heading clarification. Bootstrap/table regressions and deployment compatibility checks are now automated. Full gate: **220 passed, 2 deselected, 611 subtests passed** (100.63s); fixed audit remains **1**, with zero new findings. See [review-patches-2026-11-08.md](.autoresearch/review-patches-2026-11-08.md) for commands, evidence and limits. Native Linux setup remains unchecked; archive/architecture paths were tested with fixtures and the real tar extractor. Live deployment remains pending an authorized merge.

## Next batch after runs 50–52
- See [project-improvement-plan.md](project-improvement-plan.md) for eight brainstormed experiments with visitor benefits, evaluation criteria, scope and risks.
- Priority: report opening finding/evidence/constraint structure, project artifact labels, search page-type labels (completed in run 54; filtering in run 55), reproducibility panel, chart-to-table navigation. Optional category filters need evidence that jump links are insufficient, plus no-JavaScript/reset/history behavior.
- Keep historical M9b/M9c distinctions and reused-test-split caveats, RVL tuning/control slices and usable-row denominators. No new project claims or numbers without source verification.
- Segment 7 complete: 211 → 127 → 1, two keeps, no discards, no new findings. Both candidates passed 220 tests and 611 subtests; screenshots archived with evidence. Only the accepted research UW–Madison widow remains.

## Leg 2 / PR108 completed
- [x] Destination-type labels in search, run 54: 100 → 12 in segment 8, no lost/added results.
- [x] Native page-type filter, exact subsets/order restoration, shareable q/type URLs and safe readiness/fallback behavior, run 55: 12 → 4.
- [ ] Next measurable polish: search snippet separator wrapping at 375/414 (3 typography points newly exposed by the populated-search baseline). Prefer informative body context over repeated title/kicker text while retaining provenance and claims.
- [ ] Next creative leg: report evidence-first openings; project cards with explicit live-demo/recording/report/source artifact distinctions; chart-to-table navigation. Establish the evaluation before changing the UI.
- PR107 and PR108 are merged; PR108 merge is 8d430f2. PR109 starts from that actual main revision.

Pre-publication print-form regression repaired in 3eed785; screen-only grid rule and four print assertions, full gate 225 passed/611 subtests. Print pagination and pre-existing search-suggestion print styling remain unmeasured backlog items.

Done in segment 10: numbered citations and source notes on the NATD report (runs 58-59), end-of-document
footnotes seated inside main, snippet separators flattened to semicolons, footnote-ref boxes, and the
heading widow cleared by rephrasing. polish_defects is 0.

Open (segments must be re-baselined per issue 106's contract before adding checks):
1. Chart and diagram contrast under dark theme (SVG text/lines), reduced motion and forced colors.
2. Link and asset integrity: internal anchors and natural-vs-displayed image size.
3. Metadata coverage: unique title and description, canonical URL, og:image per page.
4. Performance budget: page weight, font files, CLS and largest paint from Playwright's timeline.
5. Print layout: report-page table and figure breaks (the resume already prints on two pages).
6. Search: page type labels live; informative snippets gate may be worth a segment of its own.
7. Other engines (Firefox/WebKit), real devices, screen readers, live deployment.

## Segment 12 completion
- [x] Print navigation cascade: project pagers and search suggestions hidden in print; 36 → 0, run62. Screen interactions preserved.
- [x] Bounded live deployment smoke for merged PR108 (see pr108-live-smoke.md); broad live coverage and native Linux remain open.
- [ ] Print report table/figure pagination and native PDF output need a separate evaluation.
- [ ] Next creative candidate: evidence-first report opening with explicit finding, evidence and constraint, retaining every historical split/run caveat.

## Visualization evidence leg / PR110
- [x] Native chart-to-table and return navigation without JavaScript across seven generated charts (run64).
- [x] Coordinated mark/source-row focus and persistent full-source context, including benchmark replicates (run65).
- [x] Full reading width for stacked table captions, preserving the benchmark limitation text (run67).
- [x] Static inventory of 43 built pages: metadata presence, unique titles, local destinations and fragment targets; see site-coverage-inventory.json for limits.
- [ ] Follow uncovered-aspects-queue.md: essential SVG contrast first, then uncertainty-aware evidence ladder/report prose, saved-figure source links and artifact labels. Preferences/performance/native portability/PDF pagination remain open.

## MapReduce next focus
- [x] Source-pinned backup-duration comparison, three-run/fixed-order limits adjacent.
- [x] Signed mean/95% interval from ten interleaved pairs, zero-crossing uncertainty visible.
- [ ] Follow-on: worker scaling shape, shuffle-phase interpretation and failure recovery, only after authenticating the matching source data and defining fixed evaluations.
- Review checkpoints: source/design before edit, diff/visual/function after render, evidence before keep, entire PR and open reviews before merge.
