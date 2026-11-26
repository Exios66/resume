# PR108 reconciliation and merge validation


## PR108 merge preparation
PR107 was already merged into main at f981b6c. Handoff branch reconciliation: remote child still held superseded 6c749ed; its validated amendment 8145ba7 and subsequent zero-score work were local and had mistakenly been pushed to the former parent branch. Recorded the superseded child ancestry while preserving the validated tree, merged current origin/main, and retargeted PR108 to main. Code tree is unchanged from 8435743. Full gate on reconciled 6e90bf7: 233 passed, 2 deselected, 611 subtests in 79.68s; fresh render/audit 0 across 43 pages, all buckets zero (48.3s audit, 20s render). No unresolved threads, requested reviewers or change-request reviews at final review read. No valid review is dismissed without fixing it.

Ten new actual screenshots cover citation prose and Research at 375/1280 in both themes plus phone-light/desktop-dark source notes. All opened and checked for private data. Archived prior run58/59 captures too; run-59-widow-375-light is the BEFORE heading, not the kept outcome. No native Linux, other engines, real devices, screen readers or live CDN verification claimed.

Commands (sourced `. .autoresearch-tools/env.sh`): `scripts/hillclimb/hc.sh doctor` (All tools present), `scripts/hillclimb/hc.sh checks` (233 passed, 2 deselected, 611 subtests), `scripts/hillclimb/hc.sh baseline` (all metrics buckets 0), `git diff --check`. No source changed during reconciliation.

Actual capture commands: `hc.sh shot projects/natd/report.html WIDTH THEME pr108-final-citations-WIDTH-THEME --at '#humans-presume-honesty-and-detect-lies-at-about-chance'`; the Research counterpart uses `research.html --at '#graduate-research-at-uwmadison'`. Both at 375/1280 light/dark. Notes use `--at '#fn1'` at 375 light and 1280 dark.

- [Citation text, phone](screenshots/pr108-final-citations-375-light.png)
- [Citation text, desktop dark](screenshots/pr108-final-citations-1280-dark.png)
- [Source notes, phone](screenshots/pr108-final-notes-375-light.png)
- [Source notes, desktop dark](screenshots/pr108-final-notes-1280-dark.png)
- [Research heading, phone](screenshots/pr108-final-research-375-light.png)
- [Research heading, desktop dark](screenshots/pr108-final-research-1280-dark.png)

Run58: segment10 140→1, numbered sources and accessible note boxes/landmark placement, readable snippets. Run59: 1→0, heading ends in two words while retaining the institution and meaning. Both candidates retain their original ledger records. Existing bibliography verification labels are preserved, not newly authenticated. Screenshots supplement the browser suite and do not prove every interaction.
