# Autoresearch: polish the portfolio site

## Objective
Hill-climb toward a fully polished, professional, beautiful portfolio that builds on the existing design
(Newsreader/Inter/JetBrains Mono, teal accent, light/dark themes, cards, inline SVG charts and diagrams).
Fix what visitors, keyboard users and screen-reader users actually meet; never trade looks for a lower count.

## Metrics
- **Primary:** `polish_defects` (weighted defect points, lower is better), from `autoresearch.audit.cjs` on a fresh render.
  - axe-core violations x impact (critical 10, serious 5, moderate 2, minor 1), 375/414/768/1280 px, light and dark
  - layout: page overflow 20; crushed or clipped table cells 2 each (320 and 375 px); tables wider than the screen 1;
    tap targets < 24 px 1; unique text < 12 px 1 (375 px); invisible focusable controls 5 (per combo)
  - structure: heading skips 2, pages without exactly one h1 2
  - errors: console, network, broken images 10 each
  - lint: no 404 page 10; résumé "Portfolio" text 3; résumé lacks GitHub profile 3; search titles repeat site name 3;
    `mailroom-ml` spelling 1; "Open to Relocation" 1
- **Secondary:** axe_points, layout_points, error_points, structure_points, lint_points, pages, css_kb, audit_s, render_s

## How to run
`bash autoresearch.sh > run.log 2>&1` (renders with Quarto 1.10.19 at /opt/quarto, ~70 s); breakdown in `audit.details.json`.
Checks: `bash autoresearch.checks.sh` (Lua via bundled pandoc, Node, pytest + Chromium; ~70 s).

## Files in scope
`styles.css`, `assets/js/site.js`, `scripts/*.lua`, `scripts/post-render.py`, `partials/**`, `_quarto.yml`, every `.qmd`,
new `404.qmd`, `docs/` (rendered output only, always via `quarto render`), `assets/Jack_Burleson_Resume.pdf`
(regenerate with `scripts/make-resume-pdf.py` whenever `resume.qmd` changes), tests that encode the exact content changed.

## Off limits
`autoresearch.checks.sh` is fixed. `autoresearch.sh` and `autoresearch.audit.cjs` are fixed within each segment; audit extensions require a separate commit and a new baseline. Never hand-edit `docs/`.
Project numbers and claims (must match source repos). Removing or hiding content to dodge a check.

## Constraints and anti-cheating rules
- All checks pass. Do not delete or weaken a test; update a test only when it pins the exact text being changed on purpose.
- Visual review of screenshots for every kept change (SHOT_DIR=... node autoresearch.audit.cjs). A lower count that looks worse is a discard.
- No `display:none`/`aria-hidden` tricks to hide defects; no shrinking content to avoid overflow checks.
- Commit sources + rendered `docs/` together per experiment; restore `docs/sitemap.xml` churn on discards via revert.
- Current branch: `t3/portfolio-search-discovery`; PR #108 stacked on #107. Never work on main.

## Segments
- 0: original audit (served at /docs/). 1: audit serves docs/ at /resume/ like GitHub Pages.
- 2: adds typography (separator that starts a line 2, ends a line 1; heading ending on a one-word line 1, at 375 and 1280 light);
  stretched card links measured by the overlay box; table-cell lines counted from text nodes, not padded code boxes.
- 3: characters clipped by an overflow ancestor are not counted (they are not seen).
- 4: mobile checks (crushed cells, table overflow, tap targets, small text) also run at 375 px dark.
- 5: 414 and 768 px coverage in both themes.
- 6: SVG label size measured after viewBox scaling (one point per undersized figure and viewport/theme).

## What's been tried
| # | Seg | Description | polish_defects | Status |
|---|---|---|---|---|
| 0 | 0 | Baseline (620 axe scrollable-region-focusable, 280 invisible copy buttons, 152 table issues) | 1282 | keep |
| 1 | 0 | Visible text-labelled code copy button | 988 | keep |
| 2 | 0 | Keyboard access (tabindex/role/label) for scrolling tables, code blocks, diagrams | 368 | keep |
| 3 | 0 | Inline code pre-wrap + overflow-wrap anywhere | 657 | discard |
| 4 | 0 | Inline code pre-wrap + break-word | 388 | discard |
| 5 | 0 | Stack text-heavy tables into labelled rows on phones | 311 | keep |
| 6 | 0 | Column-aware table classification; stacked figures label-left value-right | 291 | keep |
| 7 | 0 | Résumé contact shows addresses, adds GitHub, Mailroom-ML spelling, PDF regenerated | 283 | keep |
| 8 | 0 | Custom 404 page (scored badly only because audit served /docs/) | 1105 | discard |
| 9 | 1 | Segment 1 baseline | 283 | keep |
| 10 | 1 | Custom 404 page with site chrome and ways back | 274 | keep |
| 11 | 1 | Search results drop the repeated site name | 271 | keep |
| 12 | 1 | 24 px tap targets: site title, back links | 193 | keep |
| 13 | 1 | Labels and caption code at 12 px minimum; project pager stacks under 480 px | 101 | keep |
| 14 | 1 | Tighter number grids on phones | 87 | keep |
| 15 | 1 | Psychometric band row split into three rows (metric-blind, still worth doing) | 87 | discard |
| 16 | 1 | Tables whose cells hold links now stack (table filter moved to post-render) | 85 | keep |
| 17 | 1 | Hyphenate grid headers on phones | 97 | discard |
| 18 | 2 | Segment 2 baseline | 63 | keep |
| 19 | 2 | Separator splitting (scored badly: audit counted clipped separators) | 162 | discard |
| 20 | 3 | Segment 3 baseline | 63 | keep |
| 21 | 3 | Separators never start or end a wrapped label | 42 | keep |
| 22 | 3 | Balanced heading lines (text-wrap: balance on h1-h3) | 22 | keep |
| 23 | 3 | Baseline on this machine (Quarto 1.10.19, LC_ALL=C) | 22 | keep |
| 24 | 3 | <wbr> after separators in long inline code inside table cells | 20 | keep |
| 25 | 3 | min-width 12ch for first table column on phones | 29 | discard |
| 26 | 3 | Second tightening notch for number grids at 480 px | 20 | discard |
| 27 | 3 | Stack classifier prose threshold 60 -> 45 characters | 19 | keep |
| 28 | 3 | Sticky first column with scroll edge on phone number grids (metric-blind) | 19 | keep |
| 29 | 3 | Stack 4+-column grids whose first column holds a 20+ char row label | 9 | keep |
| 30 | 3 | Scope tabular-nums to numeric cells (metric-blind) | 9 | keep |
| 31 | 3 | Stack grids with 16+ char row labels | 7 | keep |
| 32 | 3 | Low vs high AUC header text | 5 | keep |
| 33 | 3 | Split band shares into one row per band (metric-blind) | 5 | keep |
| 34 | 3 | rvl-cdip appendix v0 cell names its slice (metric-blind) | 5 | keep |
| 35 | 3 | Label prose row headings in stacked tables (metric-blind) | 5 | keep |
| 36 | 3 | Run-comparison header names the subclass condition in prose | 5 | discard |
| 37 | 3 | Compact phone header nav (metric-blind) | 5 | keep |
| 38 | 3 | Remove duplicate back link on report and appendix pages (metric-blind) | 5 | keep |
| 39 | 4 | Baseline: tap targets, small text, crushed cells and table overflow now checked at 375 px dark | 6 | keep |
| 40 | 4 | Stack grids of at most two rows and four or more columns | 3 | keep |
| 41 | 4 | Trim horizontal grid padding at 480 px | 3 | discard |
| 42 | 4 | Stack grids with 12+ char row labels | 2 | keep |
| 43 | 4 | Stack five-plus-column grids with three or more rows | 1 | keep |

## Remaining at 1 point
- Heading widow: 1 ("Graduate research, UW–Madison" at 375 px; UW–Madison is one unit, acceptable). Layout defects are zero (no page overflow, no wide tables, no crushed or clipped cells, no tiny text, no small tap targets in light or dark).

## Remaining at 5 points (superseded: segment 4 landed 0 layout points, see "Remaining at 1 point")
- Tables wider than the screen: 4 findings at the close of segment 3 (AUC band table at 320; mailroom-ml cohort table at 320 and 375; mailroom-ml report run comparison at 320). All have been stacked in segment 4.

## Environment notes from this resume
- This machine's Quarto is 1.9.38; the site was built with 1.10.19. `QUARTO=$PWD/.autoresearch-tools/bin/quarto` points at a locally downloaded 1.10.19.
- This machine's `LANG=C.UTF-8` changed Lua pattern byte semantics (pandoc's embedded Lua treats UTF-8 lead bytes as `%a`), failing `tests/test_charts.lua`'s "4×" formatting and differing from the committed docs. Run the loop with `LC_ALL=C`.

## Remaining at 22 points
- Tables wider than the screen: 13 (see "Remaining at 19 points" above). They scroll and are keyboard reachable.
- Crushed table cells: 4 cells (8 pts), long code paths and model names in narrow columns.
- Heading widow: 1 ("Graduate research, UW–Madison" at 375 px; UW–Madison is one unit, acceptable).

## Learnings
- This machine's default `LANG=C.UTF-8` made pandoc's embedded Lua treat UTF-8 lead bytes as `%a` in patterns
  ("×" matched, `fmt(4, "×")` rendered "4 ×"); `LC_ALL=C` restores byte-based semantics everywhere.
- Inter's `tnum` widens the hyphen ("x-x" 21.7px -> 25.1px measured in the browser), so table-wide
  `font-variant-numeric: tabular-nums` put gaps into labels like DeepSeek-R1-Distill-Llama-8B; it now applies
  to right-aligned cells and .num cells only.
- A stacking classifier works best from three signals: a prose column of 45+ chars, a row label of 16+ chars
  in a 4+-column grid, and plain wordiness; each converted real crush/wide findings.
- `position: sticky` on the first column of phone grids plus a scroll-only edge (`site.js` data-scrolls)
  makes wide number grids readable without gaming the audit.
- The site's browser test pins 44 px nav touch targets; shrink headings only in width, not height.
- Stacked rows whose first cell is a full claim (40+ chars) need their column label displayed
  (tables.lua data-prose-rows, CSS in the 720 px block).
- Quarto base CSS sets `code { white-space: pre }` and relaxes it only for `p code`/`dd code`; table-cell code can't wrap.
- Quarto's copy button needs Bootstrap Icons, which `theme: none` never loads, so it renders 12x2 px.
- `quarto render` rewrites every `lastmod` in `docs/sitemap.xml`; that churn is expected (restore it on discards).
- Quarto's project link resolver rebuilds any table whose cells hold a link and drops attributes a filter added; table
  stacking therefore runs in `scripts/tables.lua` registered `at: post-render`.
- Lua patterns are byte-based: compare multi-byte prefixes (≥ ≤ − ≈ ±) as whole strings.
- `content: attr(data-label) / ""` keeps stacked-table labels from being read twice by screen readers.
- Tests that match `class="kicker"` exactly break when a filter adds classes; match by class membership.
- Hyphenating headers or wrapping inline code anywhere both made layout worse.

## Segment 5 completed
Baseline run 44: 24 points at 414/768 added coverage. Hypothesis: extending only prose-table stacking to 800px removes the 10 crushed tablet cells while preserving desktop grids.

Run 45 kept: 24 → 4; ten crushed tablet cells removed. Run 46 kept: 4 → 2; separating the undergraduate credential from its concentration and GPA removed two orphan separators at 414 px. Facts unchanged; résumé PDF regenerated.

Run 46 kept: 4 → 2. Segment 5 closes with zero layout/axe/error/structure/lint/separator points; two heading widows remain.

## Segment 6: visualization legibility
Add one point per chart/diagram per audited viewport/theme with text rendered below 12px (0.05px tolerance). Measure font size through the SVG screen transform, including scrollable offscreen labels. Baseline before changing any site CSS. Browser confirmed NATD ticks render at 9.75px on a 375px phone; current HTML-only tiny-text check skips SVG.

Segment 6 baseline run 47: 174 points (172 small-SVG figure findings, two heading widows). Run 48 hypothesis: preserve the 640px chart and 800px diagram coordinate widths rather than downscaling text; contain horizontal scrolling, keep captions visible, extend chart scroll guidance through tablet widths and remove minimum widths in print. Prototype confirms 9.75px → 12px phone chart ticks without page overflow.

Run 48 refinement before decision: initial label-size fix scored 2 but screenshots showed cropped desktop diagrams and hidden positive bars on phones. Correctness also caught the initial focused mark tooltip being out of view. Expand diagram width within desktop paper margins, retain print margins, and size bar-label gutters to short category names so the positive zero line stays visible. The Lua collision assertion now checks against the intentionally changed category-label coordinate rather than a fixed 190px gutter. Rebenchmark and rerun all checks on amended commit.

## PR progress evidence policy
For every candidate that proceeds, update its leg PR (#107 through run 52; #108 from run 53) with actual reviewed screenshots, the fixed segment's before/after metrics and findings delta, checks on the experiment commit, and why the candidate was kept. Store review images under `.autoresearch/screenshots/`, outside `docs/`, and embed durable raw image URLs. Include refinements and any failed checks honestly; never advance a candidate on score alone.

Run 48 kept: 174 → 2 after refinement, full checks and reviewed screenshots. Run 49 hypothesis: a 320px minimum for Writing cards (rather than 300px) gives long essay titles and summaries a full tablet row, preserving two columns on desktop and removing the 768px heading widow. Scope only the Writing index. This batch targets four kept candidates, then snapshots the backlog for the next iterations.


## Current hand-off: runs 44–49
Four kept candidates completed this batch. PR #107 includes actual screenshots, metrics, validation and reasons each proceeded. Durable images are in `.autoresearch/screenshots/`; the exact verification commands and limits are in `.autoresearch/verification-2026-11-08.md`.

| Run | Segment | Candidate | Score | Decision |
|---|---|---|---|---|
| 44 | 5 | 414/768 coverage baseline | 24 | baseline keep |
| 45 | 5 | Tablet prose tables | 4 | keep |
| 46 | 5 | Undergraduate education structure | 2 | keep |
| 47 | 6 | Rendered SVG legibility baseline | 174 | baseline keep |
| 48 | 6 | Readable charts/diagrams, adaptive bar-label gutters | 2 | keep after refinement |
| 49 | 6 | Writing cards give titles and summaries tablet room | 1 | keep |

Final gate on experiment 29a03e3: 197 passed, 2 deselected, 611 subtests passed in 44.50s. All 43 pages audited; axe/layout/error/structure/lint/separator points are zero. Only the accepted research heading widow at 375 light remains (UW–Madison is an indivisible name). Initial run-48 tooltip failure was fixed and checked before keeping; no other discarded candidates in this batch. Segment scores are comparable only within a segment.

Next: SVG contrast, then report contents alignment, Projects category chips and page-type search labels. These need new fixed evaluations before metric-blind features can proceed. No live merge/deploy, other engines, real devices, screen readers or external destinations checked. Resume from the saved backlog on the existing branch.


## Review remediation after run 49
Confirmed PR #107 review findings are patched: pinned/synchronized bootstrap, both Chromium clients verified, platform/extraction and locale handling, unique code IDs, excluded local tooling from published output, corrected ledger summary/evidence links/backlog, and clarified the RVL result scope. No benchmark/check rules were weakened or changed. This is review remediation rather than a new score-seeking experiment; polish_defects remains 1. Full gate: 220 passed, 2 deselected, 611 subtests passed (100.63s). Dev-root and /resume/ deployment cases now run in the suite at 375/768/1280, both themes. Four reviewed screenshots and the exact validation record are archived in .autoresearch/. Native Linux execution and live deployment remain open.

## Segment 7: report navigation
Two-candidate batch. Extend the audit before editing the site: one point per visible report contents whose column starts differ by more than 2 CSS px, and one point per contents with any link below a 44×44 CSS px touch area at phone/tablet widths (<=768). Navigation is distinct from inline prose; project nav already uses 44px. Existing buckets stay unchanged. Baseline source is 9d22cf5. Hypothesis 1: a responsive grid aligns columns and keeps DOM reading order row-by-row. Hypothesis 2: full-cell links provide accessible touch areas and clearer focus/hover feedback. Projects chip styling deferred: measured row gap is already 4px. Do not invent a spacing defect.

## Segment 7 completed: runs 50–52
Baseline run 50 at e42480d: 211 = 84 column-alignment + 126 contents touch-target findings + one accepted heading widow. Run 51 source commit 070351d, keep/gate commit a668ed9: 127, all 84 alignment findings removed. The intervening a668ed9 commit only adds the research plan; evidence records the provenance explicitly. Run 52 at 7412851: 1, all 126 touch-target findings removed. No added findings for either candidate. Compare only within segment 7.

Both candidates passed 220 tests, 2 deselected, 611 subtests; run 51 95.70s and run 52 76.46s. Reviewed six captures per candidate at 375/768/1280 in both themes plus the run-52 phone keyboard-focus capture, and two baseline captures. Contents navigation keeps all text, destinations and report claims. Browser verified alignment, 44px targets, focus/Tab/Enter, padded-edge pointer activation and target positioning. The phone contents panel grows to 451.20px for reliable touch targets; screenshots judged readable.

Two-candidate iteration budget complete. See project-improvement-plan.md in the committed snapshot for eight prioritized follow-on hypotheses, required evaluations and prose constraints. Next: structure a report opening around finding/evidence/constraint with all run/split limitations preserved; then project artifact labels and search page-type labels. SVG contrast and platform/deployment checks remain open. No audit/check definitions changed after the segment baseline. No candidate discarded; one baseline screenshot attempt during rendering timed out and was rerun successfully after rendering.

## Leg 2 / segment 8: search discovery
Stacked branch t3/portfolio-search-discovery starts at PR107 review-closeout 2425775. New PR targets t3/resume-auto-research-loops, not main, so its diff contains only this leg. Two candidates: destination-type badges and a page-type filter with shareable URLs. New audit committed before site edits: load real calibration results at every non-layout-only viewport/theme; one point per result missing a visible correct destination-type label; one point per unavailable/incorrect filter behavior. Filter must preserve the query, return exactly the matching subset for case studies/reports/appendices and restore all results. Existing axe/layout/content checks apply to populated search. Check definitions remain fixed.

## Leg 2 complete: runs 53–55 / PR108
PR107 review closeout: all 16 inline threads resolved, no pending assignments; earlier duplicate-run nitpick already fixed. Commit 2425775 strengthens the appendix navigation assertion, 3 targeted tests passed. New branch starts at that exact parent and PR108 targets its branch, not main.

Segment 8 baseline 53 at fda83d9: 100 (88 missing-type-label points, 8 filter points, 3 snippet separator points, accepted research widow). Run 54 fbfef77 kept: 100 → 12; route-derived destination badges, unchanged 11 calibration matches and relevance; full gate 220 passed, 2 deselected, 611 subtests, 137.16s. Run 55 b1e51e7 kept: 12 → 4; native page-type filter, exact subsets/restoration, URL state, empty/error/delayed/no-JavaScript behavior; full gate 225 passed, 2 deselected, 611 subtests, 74.77s. Audit fixed throughout; tests add assertions for intentionally introduced labels/controls.

Two baseline screenshots, six run-54 screenshots and ten run-55 screenshots were opened and reviewed. Extra phone form height accepted for a labelled 46px native control. Arrow/Enter selection was not established by collaborative preview; Tab focus and native selection via the select tool were verified. Targeted tests first hit a noscript-wrapper matcher limitation; paragraph assertion corrected, then six targeted tests passed. No product candidate discarded.

Two-candidate batch complete; next: informative search snippets and separator wrapping (3 newly exposed baseline points), then report finding/evidence/constraint openings, project artifact labels and chart-to-table navigation. Final score 4; all axe/layout/error/structure/lint points zero, with typography only. Native Linux/other engines/real devices/screen readers/live deployment remain unchecked. Current main→PR107→PR108 merge-tree simulation is conflict-free and matches the candidate tree. No actual merge/deploy performed.

Pre-publication correction: source review after run 55 found a print cascade regression (the screen grid rule overrode the earlier form hide rule). Added assertion failed as expected, then fixed in 3eed785 by scoping display:grid to screen media. Fresh render/audit stays 4; full gate on 3eed785 passes 225 tests, 2 deselected, 611 subtests in 77.00s. Three renewed screenshots opened, including actual print media showing the form hidden. Original keep history retained; this is a correctness repair, not a new metric-blind experiment.

## Segment 9: numbered research citations
User requests inline citations and footnote numbers with clear source access and unobstructed reading. Start with NATD's 17 already documented scholarly references, preserving all source URLs, bibliographic text and verification caveats. Shared native Quarto footnotes and site styling support later adoption elsewhere. New fixed criterion before site edits: each of the 17 literature citations must have a visible number, a resolving source note with external source link and return path to its reference. Baseline before converting parenthetical author links. No external source re-verification claimed; this is a formatting/navigation change. One candidate in this batch.

Segment 9 baseline run 56 scored 140 and passed 225 tests/611 subtests, but pre-experiment browser inspection found the literature selector assumed a section container: this site flattens section headings to H2. No product candidate was applied. Correct the audit scope to the report .page in a separate commit and start segment 10 before any UI change. Baseline screenshot attempts with the same bad descendant selector timed out; rerun with the actual H3 ID. Preserve the original baseline record.

## Segment 10 completed: runs 58-59
The committed citation candidate regressed three measured surfaces (64 invisible focusable footnote-ref links, an axe region over the template-level footnotes section, snippet separators). Repaired inside the same idea and the run commit:
- styles.css gives a.footnote-ref 3 px inline padding, so every superscript number is a real clickable box.
- scripts/post-render.py seats the end-of-document footnotes section inside <main> before the footer (Pandoc writes footnotes after the body; a unit test pins the behaviour). The pivot was discovering the footnotes block does not exist in the pandoc AST at filter time (Quarto/HTML template emits it after $body$), so it cannot be moved from an AST filter.
- scripts/post-render.py normalises the flattened search-index body's label separators to semicolons (unit test added), so a snippet wrap can no longer open or close a line with a separator; page markup keeps its dots.
- tests/test_natd.py's reference pin now reads the two links the citation work adds (source + return arrow); said in the log.
Runs 58-59 kept: 140 -> 1 (run-58: citations with repaired seams), then 1 -> 0 (run-59: research.qmd heading 'Graduate research at UW–Madison' — the comma phrasing forced text-wrap: balance into a 2+1 split ending on the single token UW–MADISON; the two-token final line clears the widow check). Full gate after each keep; run-58 233 passed, 2 deselected, 611 subtests in 132.76 s; run-59 233 passed in 108.10 s. Screenshots at 375/414/1280 reviewed (citations, source notes, live search results, the balanced heading).
polish_defects is 0 for the first time: every bucket zero on the audit's full viewport/theme coverage (320/375/414/768/1280).

## PR108 merge preparation
PR107 was already merged into main at f981b6c. Handoff branch reconciliation: remote child still held superseded 6c749ed; its validated amendment 8145ba7 and subsequent zero-score work were local and had mistakenly been pushed to the former parent branch. Recorded the superseded child ancestry while preserving the validated tree, merged current origin/main, and retargeted PR108 to main. Code tree is unchanged from 8435743. Full gate on reconciled 6e90bf7: 233 passed, 2 deselected, 611 subtests in 79.68s; fresh render/audit 0 across 43 pages, all buckets zero (48.3s audit, 20s render). No unresolved threads, requested reviewers or change-request reviews at final review read. No valid review is dismissed without fixing it.

Ten new actual screenshots cover citation prose and Research at 375/1280 in both themes plus phone-light/desktop-dark source notes. All opened and checked for private data. Archived prior run58/59 captures too; run-59-widow-375-light is the BEFORE heading, not the kept outcome. No native Linux, other engines, real devices, screen readers or live CDN verification claimed.

## Segment 11: print reading surfaces
PR108 merged into main at 8d430f2 after reconciled validation, 233 tests/611 subtests and fresh audit 0. New branch t3/portfolio-print-reading starts at that merge. One-candidate budget: keep screen navigation out of printed reading surfaces. Fixed criterion committed before CSS edits: at 1280 light CSS print media, one point per visible screen-navigation container on each of 43 pages; a hidden primary h1 adds one point. Check header/footer, project tabs/contents/pager, search form/suggestions/status/results. Keep main content, citations, source notes and figures. This does not evaluate PDF pagination, printer dialogs or real paper. Hypothesis: later display:flex rules override earlier print-hide selectors; a final print-specific navigation rule restores the intended paper view without changing screen interaction.

Segment11 baseline run60: 38, 233 tests/611 subtests passed, but print title criterion falsely counted Home and Resume because it only selected native h1, whereas both valid level-one headings are divs with role=heading/aria-level=1. Before any product edit, correct selector in its own audit commit and start segment12; real navigation baseline is 36. Initial baseline retained; do not claim those two semantic false positives were site defects. Captured eight actual before print states, confirming pager/suggestions visible and semantic title visible.

## Segment 12 complete: print navigation / PR109
Corrected semantic-heading audit committed before the candidate; baseline run61 at d3305c3: 36, 233 passed/611 subtests (75.10s). Run62 at ab26129: 0, 233 passed, 2 deselected, 611 subtests (78.44s). One CSS selector restores print hiding of project pagers and search suggestions after later flex declarations. All 36 findings removed, none added; all 43 primary titles remain visible. Eight before and eight after print-media captures opened at 375/1280 with light/dark preferences, checked for private data; screen pager navigation and suggestion search exercised in the collaborative browser. No audit/check changes after baseline, no discarded product candidate. The one-candidate budget is complete.

PR108 merged into main as 8d430f2; its deployed home, filtered search, citation/return navigation, research heading, theme persistence, PDF response and custom 404 passed a bounded live smoke check (pr108-live-smoke.md). PR109 starts from that actual merge, not a stack simulation. Next: report finding/evidence/constraint openings and artifact labels need their own fixed evaluation; print pagination, contrast, metadata and asset integrity remain backlogged. Other engines, physical devices, screen readers, native printer dialogs and PDF pagination remain unchecked.

## Segment 13: chart evidence explorer
New leg from merged main 689b6a4, branch t3/portfolio-evidence-explorer, following PR107/108/109. Two-candidate budget: (1) native two-way chart/source-table navigation; (2) coordinated focus/hover row highlighting with a persistent full-source readout. Existing seven generated charts across bars, dumbbell, step and strip reuse their authored tables; no new data or project claims. New fixed audit before source edits: at every normal viewport/theme, one point per chart missing native source/return links with unique targets and focusable landing points, and one per chart whose first/last focused marks do not outline the matching source row and display all its source cells in a visible readout. Existing whole-site checks remain unchanged. Links must work without JS; table values/headers/caveats remain intact; print and forced-colors behavior are manually checked. Subjective design and scientific interpretation remain screenshot/source review judgments, not inferred from the score.

Segment13 complete: run63 baseline112 → run64 ab7ca7a56 → run65 e5c3d670. Run64 gate237 tests/611 subtests75.46s; run65 gate241 tests/611 subtests79.73s. Existing broad checks unchanged; tests added to pin the intentionally introduced interactions. Run64 descriptive-text presentation was refined before its single keep decision. All final screenshots reviewed. Initial audit-edit command failed before applying a product edit; interrupted unscored render was rerun successfully and generated scratch files cleared by the full render.

## Segment14: readable stacked-table captions
Visual review revealed a pre-existing Langton benchmark caption compressed to about72px inside a335px stacked table. Caption content and CSS predate the feature. Extend the audit in its own commit before fixing CSS: one layout point per visible stacked-table caption below90% of its block table width, every normal viewport/theme. Do not compare across segments. One additional candidate to restore caption reading width without changing text, data or native desktop layout.

Segment14 complete: run66 baseline6 → run67 3ed86e70; 249 passed, 2 deselected, 611 subtests passed in 80.98s (0:01:20). Caption reading width restored without changing text or native desktop layout. This additional one-candidate budget and the two-candidate visualization budget are complete. All screenshots reviewed; exact source gates and limits in chart-evidence-verification.md. PR110 is based on merged main689b6a4. Follow-on objectives are ranked in uncovered-aspects-queue.md; contrast, uncertainty-aware storytelling, artifact labels, preferences, performance and portability remain open.

## Segment15: MapReduce effect and uncertainty
Two-candidate leg from merged main bd2605c. Source authentication and checkpoint-review plan in mapreduce-visualization-plan.md. Compare E2 duration with an injected slow worker, then a signed paired-effect interval without one. New fixed audit before product edits; existing correctness-gate definition unchanged. Screenshots and checkpoint review required before every keep. Broader uncovered objectives remain queued.

Segment15 completed: run68 baseline16 → run69 e08048a8 → run70 211e0120. Final gate: 257 passed, 2 deselected, 634 subtests passed in 229.57s (0:03:49). Both ideas refined after screenshot/code review before their single keeps; audit unchanged. Earlier duration gate had one recorded local-server teardown warning; initial interval gate was interrupted for refinement, not claimed as passed. Archived source/review checkpoints and 17 reviewed captures. Two-candidate budget complete; review/merge PR111 next. MapReduce follow-ons and the broader uncovered objectives remain in the queue.
