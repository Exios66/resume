# Ideas backlog (prune as they land)

Done: copy button, scroll-region access, stacked tables, 404 page, résumé contact, search titles, tap targets,
tiny text, separators, balanced headings, wbr in table-cell code, stack classifier (prose column 45+, row label
12+, two-row grids, five-column grids), sticky first column + scroll edge, scoped tabular-nums, AUC / band /
v0 content fixes, labelled prose rows, compact phone header, duplicate back link removed, mobile checks at
375 px dark (segment 4).

Open:
1. Layout findings are 0. The one accepted finding is the "Graduate research, UW–Madison" heading widow
   (UW–Madison is a single unit).
2. Projects page jump links have large row gaps on phones; consider chip styling.
3. Report contents box column misalignment (run 38 removed the duplicate back link; alignment still open).
4. Content consistency (owner facts needed): unify date formats; "Simulations" shortcut vs "Side projects &
   interests" heading; expand "DSHB" on first use.
5. Audit coverage: real Firefox/WebKit, real devices and screen readers were never checked.
6. New audit segments from issue 106 still available: more viewports (768/414), performance budget, chart and
   diagram contrast, link and asset integrity, metadata (titles, canonical, og:image), print layout, reduced
   motion, other engines.


## Next batch after runs 44–49
- Completed: new 414/768 coverage, tablet prose tables, undergraduate credential structure, SVG rendered label-size coverage and readable figures; PR candidates now include durable screenshots and quantitative keep rationale.
- Next visualization audit segment: SVG text/essential mark contrast in both themes (axe excludes much SVG), then forced colors and reduced motion checks. Keep the audit fixed within each segment.
- Next features: report contents alignment, Projects category chips, page-type labels in search results. These are currently metric-blind; define independent visitor-facing evaluation before experimenting.
- Prose backlog: shorten repeated introductory inventories and make report takeaways easier to scan, preserving all claims and source-backed metrics. Owner facts still needed for the open content-accuracy issues.
- Continue screenshots for every progressing PR candidate, with before/after metrics and reason for keeping it. Never publish evidence under docs/.


## PR review and deployment readiness TODOs
- [ ] Validate the complete merge-base diff of PR #107 and triage every unresolved inline review against the current HEAD. Fix confirmed code defects in a separate implementation pass, then rerun validation and resolve only addressed threads.
- [ ] Verify fresh-clone setup on macOS and Linux (amd64 and aarch64), pinned Python/Node Playwright compatibility, browser installation, Quarto extraction/version selection and locale initialization.
- [ ] Remove accidentally published build/test dependencies from `docs/` and prevent them from returning during rendering.
- [ ] Reconcile review evidence paths and stale experiment/backlog summaries against the append-only ledger and archived screenshots.
- [ ] Test the built site on a local dev server: assets, navigation, search, theme persistence, report controls, figures and résumé download at phone/tablet/desktop widths.
- [ ] Test deployment compatibility in a GitHub Pages simulation: serve the build under `/resume/`, use directory index URLs, return the custom 404 for missing nested paths, and verify nested links, CSS/JS/font/image/PDF URLs, canonical metadata and browser errors.
- [ ] Record the dev-server and simulated-deployment results and coverage limits; require the same checks on the final merge candidate. A local simulation does not prove the live CDN, Pages configuration or deployed headers.
- [ ] After an authorized merge/deploy, verify the actual portfolio URL against the built artifact and repeat the critical navigation/search/theme/404/PDF smoke checks.


### Confirmed review follow-up at PR HEAD `0ca9b3b`
- [ ] Fix the Linux Quarto extraction path: the upstream v1.10.19 archive contains `quarto-1.10.19/`, while setup validates `.autoresearch-tools/bin/quarto`.
- [ ] Recognize Linux `aarch64` as ARM64 rather than falling through to the amd64 archive.
- [ ] Install/validate the Chromium revision required by both Playwright clients. Current Node 1.65.0 expects revision 1254; pinned Python 1.64.1 expects revision 1248. The cache-directory wildcard and Node-only doctor do not establish Python readiness.
- [ ] Synchronize all pinned test requirements in an existing venv, including pypdf; propagate installation failures instead of reporting readiness.
- [ ] Validate the pinned Quarto 1.10.19 version for both the QUARTO override and installed PATH selection.
- [ ] Create `.autoresearch-tools/` before writing the Lua locale probe when Quarto is already installed. A fresh worktree otherwise skips the required C-locale detection.
- [ ] Remove the 19 Playwright assets (3,005,955 bytes) accidentally committed under `docs/node_modules/` and exclude test/build dependencies from Quarto resource discovery.
- [ ] Preserve a labelled inline code span's ID on only one split fragment. Pandoc reproduction currently emits three `id="code-ref"` nodes for `long/path/component`.
- [ ] Link archived evidence records to the tracked screenshots rather than ignored `.hillclimb-shots/` paths.
- [ ] Reconcile the run-25 table score (20) with its append-only ledger result (29), and prune the completed 414/768 viewport backlog item. Document that Chromium may be installed in the user cache outside the worktree.

Initial validation (review only, no code fixes or commits): `scripts/hillclimb/hc.sh doctor` passed; `bash autoresearch.checks.sh` passed 197 tests and 611 subtests, with 2 deselected (43.26s). Direct `node autoresearch.audit.cjs` passed with polish_defects=1, layout/axe/errors/structure/lint=0 across all 43 pages. The local `/resume/` simulation returned all 101 referenced local URLs with HTTP 200, directory indexes with 200, the PDF with application/pdf, and a missing nested route with the custom 404 and working `/resume/` recovery links. Browser smoke checks confirmed theme persistence, search (11 calibration results), and phone chart scrolling/tooltip on the dev server. This does not verify a fresh Linux build or the live GitHub Pages deployment.

Open-review triage: 14 unresolved threads, 2 already resolved. The omitted Writing heading-widow and pending run-46 comments are superseded by runs 49 and 46 respectively; do not reintroduce the resolved widow. The RVL result-column heading remains a low-risk clarification of a pre-existing mixed-slice column. CodeAnt skipped the large PR; CodeRabbit's latest check is neutral/rate-limited, not a fresh approval. GitGuardian passed. No pending reviewer assignments.
