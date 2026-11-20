# Handoff

Read `AGENTS.md`, `.github/BUILDING.md`, `scripts/hillclimb/README.md`, this file, `.10x/status.md`, and the live issue before editing. Run `bash scripts/setup-agent.sh` once per worktree and source `.autoresearch-tools/env.sh` in every render/audit shell. Doctor must end with `All tools present.`

## Current state (2026-11-19)

Project stage was checked against the source repositories, not guessed. AeroGlobe and MapReduce-Reloaded keep their "in active development" kickers and now also carry a WIP tag on the project index and the case study. AeroGlobe's planned list no longer says the logbook, time-zone overlay, history panel and route search are unbuilt; the README at `a011ff7` (8 November 2026) describes them as built, and the page says they were not re-run here. The appendix checklist matches that split. A real historical day is still not claimed on the live site. MapReduce charts stay the 11 November `def9c62` snapshot. The caveat records the later README summary at `6d93f33`, with the 3.7× word-count figure from E0 at `3a907de` (the other experiments in that README ran at `8f0ddb9`) and the planned section no longer says E7 was never run. AeroGlobe's narrative stays the 23 October snapshot; its 282 declarations and 8,090 TypeScript lines stay the 30 October recount. Wave Laboratory's October grep count stays; the README at `261979b` reports 632 passing tests, not re-run here. Neuron Atlas findings stay the 6 November review; `main` later moved to `7d15c18`. The corpus report still describes `v9.2`; the analysis README at `aed84818` still pins that loader, and `v9.4` is not called staged.

The MapReduce case study stays under its 19,000-byte gzip budget (18,981 after the social-card keep trimmed the meta description). Do not add a long paragraph to that page without cutting something else.

Per-project Open Graph cards shipped in hill-climb run 73 (`e128dee`): `scripts/build/make-og.py` writes `assets/og/<slug>.png` from each cover motif; project front matter points `image:` at the absolute URL. `experience_gaps` is **5** (only #121 repo-style titles). Owner contact-sheet signoff of the 14 cards is still needed; do not invent display titles.

Résumé employment was not edited. The résumé regression forbids returning `Jan 2026 – Present` and `Avis Budget Group`. #71 stays open until the owner chooses the wording and the regression is updated with it.

`.github/BUILDING.md` no longer claims invisible HTML TODOs in the sources; those comments are gone and open gaps stay on the issues.

Next priority: #121 owner titles, #118 motif signoff, residual #122–#125, and #153. Start an experience segment before experience-scored keeps. KPI tooling expansion (full-site budgets + chart/alt guards) lives on stacked PR #161.

## Current state (2026-11-12)

#119 shipped in #148 (merge `2b11221`). Wave Laboratory and Neuron Atlas lead with existing real captures; `site.lua` sizes local content images from their headers, with lead-image eager loading above the first section heading and lazy loading elsewhere. Current `experience_gaps=19`; this does not mean #126 is complete.

#146, #147 and #148 merged to main on 2026-11-12 (merge commits `21ecacc`, `d743cb8`, `2b11221`). The private-research wording, RVL-CDIP hosted-study links and lead-capture/image-loading behavior are all in main; keep them when re-rendering.

Next priority: #120 social cards, #121 display titles/layout, #118 motif signoff, residual #122–#125 tasks, #126 milestones (its experience-scored ledger/benchmark tooling is shipped; start the experience segment and baseline before experience-scored keeps), and #153 ELIZA-Terminal refinement for Parkside inclusion. The older batch notes below describe historical contributions. #138–#142 and #145–#148 have since merged; #130, #136, #137 and #119 are closed with evidence. #114 is closed after its remaining content shipped in #146. #144 is another open PR with phone chart/header and full-size raster-link changes; shipped #148 does not duplicate those features.

## Implemented batch

#131 adds project JSON-LD; #132 enforces transfer budgets; #133 aligns three-engine setup and verification caches; #134 adds slash search with progressive shortcut metadata; #135 groups supporting files and fixes diagram label collisions; #129 adds the MapReduce status recording and preserves motion preferences/manual pauses. The batch merges in that order with merge commits. Use GitHub for actual merge state rather than assuming an open historical PR has shipped.

All CodeAnt inline findings and general nitpicks in this batch were inspected, including duplicate no-script ARIA and manual-pause findings. Valid defects were fixed and verified; the old missing-rendered-schema concern was already superseded by current HTML. Summary nitpicks cannot be resolved as threads: PR dispositions and `.10x/reviews/pr-review-followup/README.md` record the result. CodeRabbit's later docstring-only warning was fixed and carried through the stack.

Evidence from review follow-up is under `.10x/reviews/pr-review-followup/`; diagram evidence is under `.10x/reviews/psych-twin-label/`; existing video evidence is under `.10x/reviews/track4-b/`. Keep evidence outside docs/. The checked-in source recording includes its already-public workstation hostname. No private session URLs belong in public PRs, issues or logs.

## Remaining work and boundaries

- The approved design remains `.10x/specs/2026-11-10-portfolio-experience-v2-design.md`. Owner priority is Track 1 first. #118 retains motif redraw/signoff work; diagram collision repair does not complete that visual review.
- #119 shipped in #148, with real lead screenshots, intrinsic dimensions/lazy loading and delayed-image geometry checks. #120 still needs project-specific social cards and owner review; set matching image-alt when adding image front matter.
- #121 display titles and remaining layout decisions need the owner. Do not invent replacements or project results.
- #123 slash shortcut is implemented, but the phone header, full active section rail, category/filter work and motif-bearing project pager are not completed by this batch. Existing report/appendix TOCs and plain project pager links should not be rebuilt blindly.
- #124 has the diagram regression and #115 recording contribution; chart conversions, new chart kinds and other visualisations remain. Existing chart restyles require the owner's draft review as specified in #124.
- #125 structured data, transfer budgets and secondary-engine setup/tests are implemented. Broader content, forced-colour coverage and owner phone/tablet checks remain; close only the shipped subtasks.
- #122 video behavior now follows live reduced motion, visibility and manual pause. This does not complete the roadmap's motion scale, transitions, motif/chart animation or print/forced-colour matrix.
- #126 is at experience_gaps=19 on main (124 before #148). Its experience-scored ledger/benchmark tooling is shipped in this PR: the segment config names the scored metric, `autoresearch.sh` prints both metric sets, and a `polish_defects=0` gate is enforced on keeps. Start the experience segment and baseline before experience-scored keeps.
- #130 and #137 were completed by #138; #136 was completed by #142. The issue closures cite their evidence.

## Verification and shipping

Use the command map for focused checks and `bash autoresearch.checks.sh` after behavior changes. Before this documentation update, combined behavior passed 285 tests/634 subtests plus 28 Node tests and Lua checks; later docstrings passed four focused browser cases. Final integration results and issue dispositions belong in the shipping report. Do not claim prior branch checks ran on a later main merge commit.

For authorized PR merges, confirm current head/checks, merge with --merge and --match-head-commit, retarget the next layer to main and verify each result. Keep branches while downstream PRs use them. Close complete issues after shipping; update partial tracks with actual merged PRs, evidence and remaining scope. App-native PR watchers should be stopped on handback.
