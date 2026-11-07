# Interactive charts from report tables — design

Date: 2026-11-07. Status: approved in conversation; awaiting written-spec review.

## Goal

Turn six existing result tables into interactive charts that sit on the
portfolio's teal design system without anything looking out of place. The table
stays on the page as the accessible source of truth; the chart is a view of it.

Success means: each chart is drawn at render time from its table, so its numbers
cannot drift from the page; every value is readable without a mouse, without
JavaScript, and in print; the colors pass the dataviz validator in both themes; the
existing test suite still passes (apart from the known résumé-print failure noted
below).

## Charts

| # | Page | Source table | Kind | Encoding |
|---|---|---|---|---|
| 1 | `projects/natd.qmd` and `projects/natd/report.qmd` | Persona / Type / Sessions / Mean exam change (points) | `bars` | Horizontal bars from a zero baseline (negatives grow left). Series by Type: Helpful = `--chart-1`, Deceitful = `--chart-2`. Legend + value at each bar tip. |
| 2 | `projects/mailroom-ml/report.qmd` | Per-head macro-F1: Head / Arm B / Final | `dumbbell` | Domain 0–1. Arm B = `--chart-1-soft`, Final = `--chart-1`, connector between. Legend; Final value labeled. |
| 3 | `projects/mailroom-corpus-eda/report.qmd` | Context window / Documents that fit | `step` | x on a log2 scale (4,096 → 131,072), y 70–100% with the axis labeled as starting at 70%. One series, no legend. Hover columns snap to each window. |
| 4 | `projects/rvl-cdip-classifier.qmd` | **New** table "Measured before and after" | `dumbbell` | Before = `--chart-1-soft`, After = `--chart-1`. Slice named in each row label. |
| 5 | `projects/mapreduce-reloaded.qmd` | **New** table "Speedup with four workers" | `bars` | One series (`--chart-1`), domain 0–4, reference line "ideal 4×". |
| 6 | `projects/langtons-ant.qmd` | Existing benchmark table | `strip` | Two small-multiple panels (single ant; colony of 25), each with its own 0-based axis. README value = `--chart-2`, re-runs = `--chart-1`. Legend. |

New tables (numbers taken only from the sentences already on each page):

- RVL-CDIP: Escalation to a stronger model, 48-image low-confidence slice 66.7% →
  62.5%; Worked examples, 48-image slice 68.8% → 64.6%; v19 vote preamble, tuning
  slice 97.5% → 96.9%.
- MapReduce: word count 3.8×, sort 2.9×, grep 2.3×.

## Color

Validated with the dataviz skill's `validate_palette.js` (categorical; ordinal for
the soft→full step). Chart marks need OKLCH chroma ≥ 0.10, which the UI teal
`#0e6f7a` (0.082) misses, so charts use a slightly more saturated step of the same
teal.

| Token | Light (surface `#ffffff`) | Dark (surface `#131c20`) |
|---|---|---|
| `--chart-1` (teal) | `#008b9a` | `#2aa3b0` |
| `--chart-2` (indigo) | `#4f5fc4` | `#7c86f0` |
| `--chart-1-soft` (earlier step) | `#6cb2bb` | `#1f6f78` |

Teal + indigo pass every check in both modes (light worst CVD ΔE 13.3, normal 15.7;
dark worst CVD ΔE 10.9, normal 15.7). The soft→full ramp passes the ordinal checks
(light end 2.41:1 light, 2.97:1 dark). Tokens are set in `:root`, in both dark
blocks, and reset in the print block (light values), which the existing
`test_every_token_the_dark_blocks_set_is_reset_for_print` enforces. Text, values,
legends and axes use `--ink`/`--muted`, never a chart color.

## Architecture

### Markup

```markdown
::: {.chart kind="bars" label="Persona" value="Mean exam change (points)" series="Type" title="Exam change by persona" unit=" pts"}
| Persona | Type | Sessions | Mean exam change (points) |
| --- | --- | --- | --- |
...
:::
```

Attributes: `kind` (`bars` | `dumbbell` | `step` | `strip`), `title`, `label`
(category column), `value` (bars, step), `from`/`to` (dumbbell, strip), `series`
(optional series column), `min`/`max` (optional domain), `ref` + `ref-label`
(optional reference line), `unit` (suffix for labels and tooltips), `summary`
(optional screen-reader sentence; a generated one is used otherwise), and for
`strip` `from-mode`/`to-mode` = `first` | `all` (how many numbers to take from a
cell). Column names match header text exactly.

### `scripts/charts.lua`

A Pandoc filter listed before `scripts/site.lua` in `_quarto.yml`. On a `Div` with
class `chart` it finds the first `Table`, stringifies header and body cells, and
replaces the Div with: a raw-HTML `<figure class="chart chart-<kind>">` holding a
`<figcaption>` title, an optional HTML legend, and an inline SVG; then the original
`Table` (unchanged) after the figure.

Pure functions, exported as a module table so tests can load the file without
Pandoc: `parse_numbers(text)` (handles `−`, `+`, `%`, `×`, thousands commas; returns
all numbers in order), `nice_ticks(min, max, count)`, and one renderer per kind that
takes plain Lua rows and returns an SVG string. A missing table or an unknown column
raises an error naming the page and column, so a broken chart fails the render.

SVG rules (from the dataviz skill): fixed `viewBox` width 640, height from row
count; bars ≤ 24px thick with a 4px rounded data end and square baseline end; 2px
lines with round caps; dots r ≥ 4 with a 2px ring in the surface color; gridlines
1px solid `--rule`; tick labels with `tabular-nums`. Every shape carries fallback
`fill`/`stroke` attributes (light values), which the CSS classes override, so a chart
survives a missing stylesheet. The `<svg>` has `role="img"` and an `aria-label`
summary.

### Interaction (`assets/js/site.js`)

Each mark group gets a transparent hit area of at least 24px, `tabindex="0"`, and
`data-tip-value` / `data-tip-label` attributes. One shared tooltip element per page
shows value first, label second, set with `textContent`. Shown on `pointerenter` and
`focus`, hidden on `pointerleave`, `blur` and Escape; positioned inside the viewport.
The step chart uses one invisible column per x position, so the readout snaps to the
nearest window. Without JavaScript the static chart (with direct labels) and the
table carry every value.

### Layout

Charts follow the `.page figure.diagram` card style. Under 720px the chart body
scrolls sideways (`min-width: 520px`) like the diagrams, keyboard-scrollable, with the
same "scroll sideways" hint; text never shrinks below a readable size. Print shows
the chart in light colors and keeps the table.

## Error handling

- Missing table, missing column, or a cell with no number where one is required:
  render error naming file and column (fail loudly, never a blank chart).
- Fewer than two rows: error (a one-bar chart is an anti-pattern).
- Tooltip script failures are caught; the static chart remains.

## Testing

- `tests/test_charts.lua` (run with `lua tests/test_charts.lua`): number parsing,
  tick generation, each kind's SVG (mark count, zero baseline for negatives,
  reference line, log2 positions), error cases.
- `tests/test_charts.py`: for each of the six pages in `docs/`, the chart exists, is
  followed by its table, every `data-tip-value` matches the table cell, all shapes
  have fallback fill/stroke; the two new tables' numbers appear in their page's prose.
- `tests/test_browser.py`: hover and keyboard focus show the right tooltip and
  Escape/blur hide it; charts render with JavaScript off; dark theme uses the dark
  `--chart-*` values; at 375px charts scroll and labels are not clipped. The existing
  all-pages sweep (320/375/768/1280, both themes) and print checks keep running.
- Evidence: screenshots of all six charts, light and dark, desktop and 375px, plus a
  hover state, kept outside `docs/`.

Known baseline: `test_no_script_and_print_from_dark` already fails in this
environment (the pinned Chromium prints the résumé on 3 pages); it is out of scope.

## Out of scope

Restyling the 66 existing PNG/SVG figures copied from project repos; charts for other
tables; filters or time-range controls (no chart here needs them).
