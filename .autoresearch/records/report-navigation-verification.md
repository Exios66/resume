# Report navigation: runs 50–52

The portfolio-hillclimb workflow measured two improvements across 21 report/appendix contents boxes. All report prose, heading destinations, project claims and numbers remain unchanged.

| Run | Change | Segment-7 score | Gate |
| --- | --- | --- | --- |
| 50 | Baseline, audit commit `e42480d` | 211 | 220 passed, 2 deselected, 611 subtests; 71.80s |
| 51 | Responsive grid, source `070351d`, keep `a668ed9` | 127 | 220 passed, 2 deselected, 611 subtests; 95.70s |
| 52 | Full-cell links and hover/focus feedback, `7412851` | 1 | 220 passed, 2 deselected, 611 subtests; 76.46s |

Segment 7 adds one point per contents box with column-start offset above 2 CSS px and one per box containing a target below 44×44 CSS px at widths up to 768. These are project usability criteria, not a claim that WCAG requires 44px for every inline link. The audit was committed before the baseline and stayed fixed throughout both candidates. The correctness gate was unchanged. Scores compare only within this segment.

Run 51 removes all 84 alignment findings; run 52 removes all 126 target findings. No new findings. Final audit covers all 43 pages at 375/414/768/1280 in light/dark, plus 320 for layout. Axe/layout/error/structure/lint points are zero; the sole remaining finding is the accepted UW–Madison heading widow.

## Exact commands

The existing worktree setup had already completed. Every render/audit/check/screenshot command below used the environment file:

```sh
. .autoresearch-tools/env.sh
scripts/hillclimb/hc.sh doctor
node --check autoresearch.audit.cjs
scripts/hillclimb/hc.sh segment 'Report contents alignment and touch navigation'
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh log keep 'Baseline report navigation evaluation'
scripts/hillclimb/hc.sh experiment 'Align report contents in reading order' styles.css
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh experiment 'Make report contents links easier to activate' styles.css
scripts/hillclimb/hc.sh checks
git diff --check
```

Doctor ended `All tools present.` Each candidate also used `hc.sh evidence` with the inspected screenshot/browser observations and `hc.sh log keep` with its hypothesis, result and next action. See [run 51](evidence/run-51.md) and [run 52](evidence/run-52.md) for those records. A documentation-only workspace commit landed between the run-51 experiment and gate; the record explicitly identifies both commits and the source diff.

```sh
for width in 375 768 1280; do
  for theme in light dark; do
    # Executed separately after each experiment, with run=51 or run=52.
    scripts/hillclimb/hc.sh shot projects/mailroom-ml/report.html "$width" "$theme" "run-$run-contents-$width-$theme" --at .page-toc
  done
done
```

## Visual and interaction evidence

Opened all 12 candidate screenshots, both baseline screenshots, and the additional actual phone keyboard-focus capture. They contain public portfolio content, with no private data observed. Archive: [screenshots](screenshots/).

- [Baseline desktop](screenshots/segment-7-before-contents-1280-light.png) and [phone](screenshots/segment-7-before-contents-375-light.png).
- [Run 51 desktop](screenshots/run-51-contents-1280-light.png): aligned row starts and reading order. Phone remains one column; tablet/desktop have two.
- [Run 52 phone](screenshots/run-52-contents-375-light.png) and [desktop dark](screenshots/run-52-contents-1280-dark.png): larger click areas, no clipped labels or page overflow. The eight-link phone box grows from roughly 290px after run 51 to 451.20px; this space is accepted for 44px targets.
- [Run 52 phone keyboard focus](screenshots/run-52-contents-375-dark-focus.png): 375 CSS px at 2× capture density, visible focus outline and background.

Collaborative browser on the `/resume/` simulation confirmed equal first-row positions at 1280, 44px link heights, Tab moving to “System and data”, `:focus-visible`, a 2px outline, and Enter activating the section (settled heading top 84.11px). At 375, a pointer click at x330/y439 in the far-right padded area activated “Results” (heading top 15.91px, no sticky phone header). No page overflow in either layout.

The unchanged full suite includes real Chromium checks at dev-root and simulated Pages-prefix URLs for navigation, search, theme persistence, chart scrolling/tooltips, PDF delivery and nested 404 recovery. Screenshots supplement those assertions; they do not prove every interaction works.

One baseline phone screenshot attempt overlapped rendering and timed out waiting for the contents box. It was rerun successfully after rendering; only successful actual captures are archived.

## Next work and limits

See [the prioritized research plan](project-improvement-plan.md) for project artifact displays, report opening structure, search labels, reproduction panels and chart/table navigation. No candidates were discarded in this batch. Projects chip styling was deferred after measurement showed the old spacing complaint was not sufficient evidence.

Native Linux setup, Firefox/WebKit, physical devices, screen readers, external destinations, live hosting/CDN behavior and an actual merge/deploy were not checked. No live publication or merge was performed.
