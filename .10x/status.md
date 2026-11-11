# Status

- Feature: portfolio-experience-v2
- Date: 2026-11-10
- Delivery batch: #131 → #132 → #133 → #134 → #135 → #129, using merge commits. These changes are implemented together in this checkout; GitHub is authoritative for merge status.
- Implemented: CreativeWork JSON-LD on all 14 case studies; gzip budgets for every page type and shared assets; pinned Chromium/Firefox/WebKit setup for both clients; slash search shortcut with no-script semantics and AltGr handling; grouped tooling/tests; Psychometric Digital Twin label clearance with checks across all 15 diagram pages; controlled MapReduce video with live motion, visibility and manual-pause regressions.
- Verification: combined source passed 285 Python/browser tests and 634 subtests, Lua checks, and 28 Node tests. A later docstring-only follow-up passed four focused browser tests. Full final-main verification is recorded in the shipping report, not inferred from branch checks.
- KPI: experience_gaps=125; pages_over_budget=0; projects_without_structured_data=0. Remaining components: 61 images without intrinsic size, 45 later images not lazy, 14 projects sharing the site social card, 5 repository-style titles.
- Coverage: most browser assertions run in Chromium. Firefox/WebKit have targeted chart and video cases. No real-device or physical international-keyboard pass; AltGr is simulated and manual video pause uses browser media events.
- Remaining: #118 motif signoff/redraws; #119 imagery/sizing/lazy loading; #120 social cards; #121 owner display titles/layout; remaining #122–#125 tasks; #126 experience-scored tooling and KPI reduction. #130 landing-page prose and #136 Langton's Ant updates are separate, unstarted tasks in this batch.
- Tooling limitation: the hill-climb ledger scores polish_defects only. KPI reporting does not make it an experience-scored loop. See scripts/hillclimb/README.md and #126 before extending it.
- Next: continue the owner's priority in #118, or take one scoped unchecked #123/#125 task after inspecting current code. Tracker: #117. Do not repeat already shipped schema, budgets, search or browser setup work.
