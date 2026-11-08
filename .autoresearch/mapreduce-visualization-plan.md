# MapReduce visualization leg and review checkpoints

Base: merged main bd2605c (PR110). No open PRs existed at the initial review read. All earlier work remains intact.

## Source authentication checkpoint

Pinned source revision: 4dd1ca4045b2b9f49a63a8f6e757b20b6fb32387. Official repository evaluation and benchmark README checked directly after the local Firecrawl endpoint refused connections twice. No upstream experiment was rerun.

- E2 with an injected slow worker: backups off17.58s, on11.24s; medians of three runs per setting. Fixed setting order, not drift-controlled. The portfolio overview rounds these to17.6/11.2; new source tables retain the pinned precision.
- E2-pairs without a slow worker: mean on-minus-off difference−0.11s, reported95% paired interval−0.38 to+0.16s; ten interleaved pairs. The interval crosses zero and does not prove zero cost. Do not mix this mean difference with the separate medians8.03/8.20.
- Shared course VM: four containers on4vCPU/8GB, one disk. No comparison of absolute throughput to the paper's large cluster, no measured LATE result.

Source links:
https://github.com/Exios66/MapReduce-Reloaded/blob/4dd1ca4045b2b9f49a63a8f6e757b20b6fb32387/docs/evaluation.md#backup-tasks-54
https://github.com/Exios66/MapReduce-Reloaded/blob/4dd1ca4045b2b9f49a63a8f6e757b20b6fb32387/bench/README.md#e2-backup-tasks-and-a-straggler

## Two-candidate measured segment

1. Add a zero-based duration comparison for E2 with the slow worker. Keep design limits adjacent, retain source table/footnote and existing chart navigation/readout.
2. Add a reusable signed effect-interval chart for E2-pairs without a slow worker. Show mean, bounds and no-change reference; negative means faster with backups. Do not label the interval as raw variability, independent replications or proof of zero cost.

Fixed audit before source edits: at every normal viewport/theme, one point per missing/incorrect duration comparison with the exact values/design caveats; one per missing/incorrect interval with exact mean/bounds/pair count, correct geometry across zero, and uncertainty caveat. Existing whole-site checks remain. No audit change to rescue an experiment.

## Checkpoint review for each step

Before implementation: confirm source values, estimand, conditions, units, limitations, expected SVG geometry and keyboard/no-JS/print behavior.
After candidate render: review source diff against this plan, exact source-table/mark agreement, axis zero/bounds, unique targets, row identity, tests added only for intended new markup/behavior. Check all affected figures at375/1280 in both themes, plus relevant tablet/preference states.
Before keep: full correctness gate on exact candidate commit, reviewed screenshots, findings delta and keep/discard record.
Before merge: review the entire main-to-PR diff, enumerate reviewer requests/unresolved threads, patch valid findings and revalidate; resolve only addressed threads. A skipped bot is not an approval. Normal expected-head merge only after checks.

Remaining contrast, broader preference coverage, report prose, artifact labels, performance, portability and PDF pagination stay queued; this leg explicitly advances uncertainty-aware visualization through MapReduce.
