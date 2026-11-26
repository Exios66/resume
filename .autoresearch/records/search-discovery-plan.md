# Search discovery leg and next creative experiments

PR #108 is stacked on #107's review-closeout commit `2425775`. This leg makes existing project evidence easier to find: route-derived result labels and a native page-type filter with shareable URLs. It adds no external service, model call, project claim or benchmark value.

## Fixed evaluation

Segment 8 was committed before the UI. The real `calibration` query returns eleven routes. At every non-layout-only viewport/theme, score one point per result without a correct visible destination type and one per absent/incorrect filter behavior. Case studies, reports and appendices must return exact route subsets, preserve the query and restore every original result. Existing accessibility, layout, structure and typography checks also run on populated search. Keep rules require lower score, passing checks, reviewed screenshots and no nearby regression.

## Next creative hypotheses

| Idea | Reader benefit | Evaluation before implementation |
| --- | --- | --- |
| Evidence trail: finding → figure → table → run | Trace an impressive result to its exact scope and supporting values | Inventory source-backed anchors and run/split identifiers; verify every hop and keyboard return; forbid comparisons across incompatible slices |
| Report opening as finding, evidence and constraint | Understand the strongest result and its limitation before reading the method | Verify every statement against the existing report; retain historical release labels, uncertainty and reused-test-split caveats; inspect all three viewport sizes |
| Interactive experiment comparison | Explore changes between existing runs without losing the baseline | Use only published table rows, preserve uncertainty and denominators, and test every displayed value against those rows; visibly distinguish unmatched populations |
| Project artifact explorer | Find live demos, recordings, reports or source code directly | Verify artifact labels against local descriptions and source links; keep all projects reachable without JavaScript; test reset, history, focus and result announcements |
| More informative search excerpts | Show the passage answering the query rather than repeated title/kicker text | Preserve search recall and route ranking, keep provenance and limitations readable, and remove the three exposed separator-wrap points without hiding text |

These are proposals, not implemented claims. Project card artifact labels remain separate from the completed search-result labels. SVG contrast, print pagination, reduced-motion/forced-colors, platform coverage and live deployment remain in the broader backlog.

## Stack integration

1. Merge #107 first. This branch was created after its review closeout; do not copy parent commits into the child diff.
2. If #107 is merged with ancestry preserved, update/fetch `main` and retarget #108 to `main` after checking the diff.
3. If #107 is squash- or rebase-merged, transplant only child-leg commits onto updated `main` (the original parent boundary is `24257754f420fa3fd2fcd89012019b99283a2642`), then retarget and verify again. This may require a lease-protected branch update; no such rewrite or merge was performed in this work.
4. Repeat the final gate and stack comparison if either branch changes executable code. The saved merge-tree simulation only establishes compatibility for the recorded revisions; it does not guarantee future edits.
