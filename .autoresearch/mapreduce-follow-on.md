# MapReduce visualization follow-on queue

Current leg: connected duration comparison and uncertainty interval, with per-step self-review checkpoints. New fixed evaluations precede source changes; every keep needs full checks, inspected screenshots and a source/claim review.

1. **Scaling trajectories.** Expand the existing four-worker summary into 1/2/4-worker views only from the pinned E0 source table. Distinguish per-workload medians and observed min/max ranges; avoid treating three observations as confidence intervals. Keep the shared disk, one-VM setup and grep outlier visible. Check curves against the existing 4-worker speedups and keep source values discoverable.
2. **Shuffle-phase story.** Connect input/shuffle/output traces to the architecture diagram using the matching saved rates CSV, not an illustrative animation presented as measurement. State the sampling/commit-counting semantics, redundant backup fetches and cache caveats. Establish trace/axis/source checks first.
3. **Failure and recovery.** A source-pinned E3 comparison can show worker-loss timing and completion cost. Keep fixed run order, clock-offset uncertainty, one-of-four worker loss and checksum-agreement limitations beside the visualization; do not imply independently proved correctness.
4. **Mechanism exploration.** A schematic interactive map→partition→shuffle→reduce view could explain data movement without claiming measured timing. Label it as illustrative, preserve byte-oracle/protobuf/hash guarantees, work without animation and maintain a no-JS diagram/table fallback.

Broader queue remains: essential SVG contrast, preference coverage, report finding/evidence/constraint openings, artifact labels, performance budgets, metadata quality, native portability and actual PDF pagination. The MapReduce interval is the first concrete uncertainty-aware visualization in that queue, not completion of every uncertainty or visualization objective.
