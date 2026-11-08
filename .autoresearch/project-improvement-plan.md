# Project display, interaction and report research plan

This queue combines the saved backlog with ideas from inspecting the Projects index, Mailroom-ML report and RVL-CDIP report. These are hypotheses, not measured improvements. Preserve the source-backed claims, historical run labels and limitations. Define each evaluation before changing the implementation; use a new fixed audit segment when adding scored checks.

## Completed foundation: report navigation

1. Align report contents columns with a responsive grid. Measure column starts in CSS pixels, preserve DOM order and all section destinations, and inspect phone/tablet/desktop layouts in both themes.
2. Expand standalone contents links to at least 44×44 CSS px on touch layouts. Exercise keyboard activation, visible focus, pointer activation, section positioning and overflow. Review the added vertical space before keeping it.

Projects category links already have 44px targets and a 4px row gap. The old “large row gaps” note is not sufficient evidence for a change. Chip styling remains optional pending a demonstrable navigation benefit.

## Prioritized experiments after this batch

| Idea | Visitor benefit | Evaluation to establish first | Scope / risk |
| --- | --- | --- | --- |
| Report opening: finding, evidence, constraint | Readers can distinguish the result from its limits before entering the method | Inventory the existing claims; check each summary against its cited run/split and preserve caveats adjacent to the result; inspect first-screen reading at 375/768/1280 | Start with one report. No new performance or business claims. |
| Project cards with explicit artifact labels | Distinguish live browser demos, recordings, reports and source code | Count correctly labelled destinations; activate each internal route by keyboard; verify text against existing project descriptions | Neuron Atlas already distinguishes live TinyStories from offline Qwen recordings; preserve that distinction. |
| Search result page-type labels | Tell a case study from its technical report or appendix before opening it | Fixed sample queries with expected destination/type pairs, no duplicate site titles, no loss of matching results; mobile wrapping and contrast | Derive types from page metadata or known paths, rather than guessing from prose. |
| Reproducibility panel | Find the snapshot, setup and known limits quickly | Check that each field comes from the current report, anchors work, commands remain selectable/copyable, and historical/current versions are explicit | Restructure existing content first; external repository verification is a separate task. |
| Chart-to-table navigation | Move from a visual finding to precise values with the keyboard | Every eligible chart links to its corresponding existing table; table values and series labels agree; focus and return navigation work | Avoid duplicating figures or inventing data. |
| Optional project category filter | Narrow a long index without losing category context | All cards available without JavaScript; keyboard controls and announced result count; URL/reset/back behavior; no hidden matches after reset | Higher complexity than jump links. Prototype only after measuring the current navigation problem. |
| SVG text and essential-mark contrast | Read chart labels and series in both themes | Establish color-compositing measurements with explicit thresholds and exempt only decorative marks; fix the audit before the site | Existing axe coverage does not establish full SVG contrast. |
| Reduced-motion and forced-colors behavior | Retain meaningful interaction under user preferences | Fixed browser preference cases; no motion-dependent information; visible focus, marks, legends and controls | Do not claim assistive-technology coverage from CSS emulation alone. |

## Prose editing checklist

- Keep result, population/split, run/version and limitation together. Mailroom-ML's historical M9b report must not imply it describes M9c; its routing sweep reused the test split.
- RVL-CDIP's tuning-slice results must remain distinct from its control-slice results. Preserve usable-row denominators and temperature/run differences.
- Replace repeated topic inventories with a short reader-oriented lead only when all destinations and project distinctions remain discoverable.
- Prefer descriptive section headings and short evidence-linked paragraphs. Do not optimize word counts by deleting uncertainty, negative results or reproduction details.
- Date-format unification and the DSHB expansion remain fact-check tasks when the correct wording is not available locally.

## Evidence and delivery

Each progressing candidate needs its own experiment commit, fixed-segment baseline/delta, full correctness gate on that commit, actual inspected screenshots, interaction observations, a keep/discard rationale and durable PR evidence. Archive outside `docs/`. A local root/Pages-prefix simulation is required; native Linux and live deployment remain separate open checks.

## Current follow-on queue
Native chart/source navigation and coordinated source reading are completed in PR110. See [uncovered-aspects-queue.md](uncovered-aspects-queue.md) for the ranked next objectives and required evaluations. A zero score covers only the fixed measured criteria.
