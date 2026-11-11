# Chart titles and labels: review and relabel

Goal: every chart on the site has a minimal, professional, informative title and labels: sentence case, no internal shorthand, units on axes, readable category names, and the finding in the title where the data supports one.

## What changed

- **15 static chart SVGs** (6 in the Mailroom-ML report, 9 for RVL-CDIP). Only text changed; the data and marks are untouched. `relabel.py` holds every exact replacement and fails if any is missing. It has already been applied; rerunning it on the edited files fails by design.
  - Mailroom-ML: "Doc-type", "· Arm B (Sep 27)" and "P0 subclass gate" became plain titles. The run and date moved to the subtitle, and legends are capitalised.
  - RVL-CDIP: class names are readable ("File folder" instead of `file_folder`). Titles state the finding or what is shown. f7's point labels are now percentages, matching its axis (they were 0.821 on a % axis). f8 had mathtext in its x-axis label, which is now a plain label. f8's floating "baseline" label sat outside the plot and is now inside, above its line. f8's legend is now drawn last, so the cost axis's gridline no longer strikes through it.
- **Two live chart titles:** the Langton's Ant throughput chart and the Mailroom-ML macro-F1 dumbbell. The dumbbell's row labels also lost their snake_case.
- **Wave Laboratory spectrum draft** (`../track4-wave/`): relabelled in the same PR.

Evidence: `mailroom-ml-before.png` and `-after.png`, `rvl-cdip-before.png` and `-after.png`, plus `live-*.png` for the live charts, in light and dark.

## Reviewed and left as they are

- The MapReduce (3), NATD (2), Corpus-EDA and RVL-CDIP dumbbell live charts already have clear titles and units.
- The 14 architecture diagrams are labelled flows with captions, not data charts.

## Not fixed here (needs the source data or the owner)

- f6 keeps the full model IDs: the rotated labels' positions were computed for those strings.
- f1's v10, v11 and v11.8 ticks sit close together, and f5's value labels cross the dashed overall line. Both are layout problems that need the figures regenerated in the source repositories.
- f8 plots accuracy and cost on two y-axes. Splitting it into two panels would be a redesign and needs the owner's approval first.
