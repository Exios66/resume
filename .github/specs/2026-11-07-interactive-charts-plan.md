# Interactive Report Charts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render six existing result tables as interactive, theme-aware SVG charts at Quarto render time, keeping each table as the accessible source of truth.

**Architecture:** A new Pandoc filter `scripts/charts.lua` replaces each `::: {.chart}` Div with a `<figure class="chart">` (title, optional legend, inline SVG) followed by the untouched table. Styling comes from new `--chart-*` tokens in `styles.css`; `assets/js/site.js` adds one shared hover/focus tooltip.

**Tech Stack:** Quarto 1.10.19 / Pandoc Lua filters, Lua 5.4, plain CSS, vanilla JS, pytest + Playwright 1.64.1.

**Spec:** `.github/specs/2026-11-07-interactive-charts-design.md`

## Global Constraints

- Plans and specs live in `.github/specs/`; `docs/` is generated output — never hand-edit it, always `quarto render`.
- Tokens, exact values: `--chart-1` `#008b9a` / dark `#2aa3b0`; `--chart-2` `#4f5fc4` / dark `#7c86f0`; `--chart-1-soft` `#6cb2bb` / dark `#1f6f78`. Print block resets them to the light values.
- Text, values, legends, axes use `--ink` / `--muted`, never a chart token.
- SVG: `viewBox` width 640; bars ≤ 24px with 4px rounded data end, square baseline end; 2px lines, round caps; dots r ≥ 4 with 2px `--paper` ring; gridlines 1px solid `--rule`; hit areas ≥ 24px.
- Every SVG shape carries fallback `fill`/`stroke` attributes (light values).
- Tooltip text is set with `textContent` only; value first, label second.
- No chart without its table; fewer than two rows or a missing column is a render error.
- Commit messages carry no session links, co-author trailers or tool footers.

## Review Focus

- Unicode minus (`−2.3`) and leading `+` in table cells must parse as signed numbers, or bars point the wrong way. (Task 1)
- Long row labels (RVL-CDIP "Escalation to a stronger model, 48-image low-confidence slice") must wrap to at most two lines inside the label gutter, never overlap the plot. (Task 2)
- Cells with markup (`**925/1,120 (82.6%)**`) or no number (`—`) where a number is required: markup is ignored; no number raises an error naming file and column. (Tasks 1–2)
- Dark theme must repaint marks via CSS even though shapes carry light fallback attributes. (Task 5)
- At 375px a chart must scroll sideways with no clipped labels, and be keyboard-scrollable. (Task 5)

---

### Task 1: Number parsing and tick generation

**Files:**
- Create: `scripts/charts.lua`
- Test: `tests/test_charts.lua`

**Interfaces:**
- Produces (global table `CHARTS`, set when the file is loaded with `dofile`):
  - `CHARTS.parse_numbers(text: string) -> {number...}` — every number in order; handles `−` (U+2212) and `-`, leading `+`, thousands commas, decimals; ignores `%`, `×`, `$`, words, markup already stringified away.
  - `CHARTS.nice_ticks(lo: number, hi: number, count: integer) -> {number...}` — clean steps (1, 2, 2.5, 5 × 10^k) covering `[lo, hi]`, including both ends' nice bounds.
  - `CHARTS.fmt(n: number, unit: string|nil, signed: boolean|nil) -> string` — trims trailing zeros, uses `−` for negatives, `+` when `signed`, appends `unit`.

- [ ] **Step 1: Write failing tests** in `tests/test_charts.lua` (header comment: `-- Run from the repository root: lua tests/test_charts.lua`; define a minimal `pandoc` double like `tests/test_site.lua` before `dofile("scripts/charts.lua")`):

```lua
local P = CHARTS.parse_numbers
assert_eq(P("−2.3"), {-2.3}); assert_eq(P("+14.5"), {14.5})
assert_eq(P("4,096"), {4096}); assert_eq(P("83.1% (665/800)"), {83.1, 665, 800})
assert_eq(P("0.19, 0.29 and 0.31 million in three re-runs"), {0.19, 0.29, 0.31})
assert_eq(P("3.8×"), {3.8}); assert_eq(P("—"), {})
assert_eq(CHARTS.nice_ticks(0, 1, 5), {0, 0.2, 0.4, 0.6, 0.8, 1})
assert_eq(CHARTS.nice_ticks(-3.6, 14.5, 5), {-5, 0, 5, 10, 15})
assert(CHARTS.fmt(-3.6, " pts", true) == "−3.6 pts"); assert(CHARTS.fmt(14.5, " pts", true) == "+14.5 pts")
assert(CHARTS.fmt(0.9505) == "0.9505"); assert(CHARTS.fmt(4.0, "×") == "4×")
```

- [ ] **Step 2: Run** `lua tests/test_charts.lua` — Expected: error, `CHARTS` is nil.
- [ ] **Step 3: Implement** the three functions in `scripts/charts.lua` (Lua patterns on the UTF-8 string; replace `−` with `-` before matching; strip commas only between digits).
- [ ] **Step 4: Run** `lua tests/test_charts.lua` — Expected: prints `chart unit tests passed`.
- [ ] **Step 5: Commit** `Add chart number parsing and tick helpers`.

### Task 2: SVG renderers and the filter

**Files:**
- Modify: `scripts/charts.lua`, `_quarto.yml` (filters: `scripts/charts.lua` before `scripts/site.lua`)
- Test: `tests/test_charts.lua`

**Interfaces:**
- Consumes: Task 1 functions.
- Produces:
  - `CHARTS.wrap_label(text: string, max_chars: integer) -> {string, string?}` — at most two lines, break at spaces, second line ellipsised with `…` if still too long.
  - `CHARTS.render(spec: table, rows: table) -> string` — returns the full `<figure class="chart chart-<kind>">…</figure>` HTML. `spec` = Div attributes (`kind`, `title`, `label`, `value`, `from`, `to`, `series`, `min`, `max`, `ref`, `ref-label`, `unit`, `summary`, `from-mode`, `to-mode`, `signed`); `rows` = list of `{[header]=cell_text}`.
  - Global `Div(el)` filter: on class `chart`, stringify the first Table's header and body cells, call `CHARTS.render`, return `{pandoc.RawBlock("html", figure), table}`; non-chart Divs untouched.
  - Mark markup contract (consumed by Tasks 3–5): each datum is `<g class="mark" tabindex="0" data-tip-value="…" data-tip-label="…">` containing a transparent `rect.hit` (≥ 24px) and the visible shape(s) with classes `c1`, `c2` or `c1s` (→ `--chart-1`, `--chart-2`, `--chart-1-soft`). Grid lines `class="grid"`, axis text `class="tick"`, direct labels `class="val"`, row labels `class="cat"`, reference line `class="ref"`. Step chart hover columns are `g.mark` with a full-height `rect.hit`. SVG root: `role="img" aria-label="<summary>"`. Legend: `<ul class="chart-legend">` with `<li><span class="key c1"></span>Helpful</li>`; omitted for one series.
  - Errors: `error("chart: <file>: column '<name>' not found")`, `"…needs a table"`, `"…needs at least two rows"`, `"…no number in column '<name>', row <n>"`.

- [ ] **Step 1: Write failing tests** (one per kind plus errors):
  - `bars` with NATD rows (Athena Helpful +14.5 … Scarlet Deceitful −3.6): 5 `g.mark`; Scarlet's bar `x` ≥ zero-line's `x` is false (it starts left of zero), Athena's starts at zero; legend has `Helpful` and `Deceitful`; `data-tip-value="−3.6 pts"`.
  - `bars` with MapReduce rows and `ref="4"`: one `class="ref"` line; no legend.
  - `dumbbell` with Mailroom heads: 5 marks, each with one `c1s` circle and one `c1` circle; `merger_agreement` Final circle `cx` < Arm B circle `cx`.
  - `step` with the context-window rows: 5 marks; 4,096 → 131,072 x positions equally spaced (log2); one `path` of class `line c1`.
  - `strip` with Langton rows, `from-mode="first"`, `to-mode="all"`: 2 panels; README markers `c2` = 2; re-run markers `c1` = 6.
  - `wrap_label("Escalation to a stronger model, 48-image low-confidence slice", 26)` returns two lines, each ≤ 26 chars.
  - Errors: missing column, one row, `—` in a value column each raise with the messages above.
- [ ] **Step 2: Run** `lua tests/test_charts.lua` — Expected: FAIL on `CHARTS.render` nil.
- [ ] **Step 3: Implement** renderers per the Global Constraints (left label gutter 190px, right padding 56px for tip labels, row band 40px; `strip` panels stacked, each with its own `nice_ticks(0, max)`; `step` y domain from `min`/`max` attrs). Escape all text with an `esc()` helper (`& < > "`).
- [ ] **Step 4: Run** `lua tests/test_charts.lua` and `lua tests/test_site.lua` — Expected: both pass.
- [ ] **Step 5: Commit** `Render report tables as SVG charts at build time`.

### Task 3: Tokens, chart styles and tooltip

**Files:**
- Modify: `styles.css` (tokens in `:root`, both dark blocks, print reset; a "Charts" section after the diagram rules), `assets/js/site.js` (tooltip before the `if (reduce) return;` line)
- Test: `tests/test_qa_fixes.py` (existing token-reset test covers the new tokens), new assertions in `tests/test_charts.py`

**Interfaces:**
- Consumes: Task 2 markup contract.
- Produces: `.chart` card styled like `.page figure.diagram`; `.chart-tooltip` element (one per page, `role="tooltip"`, `hidden` when idle) created by site.js; CSS: `.chart .c1 { fill/stroke: var(--chart-1) }` etc., `.mark:is(:hover,:focus-visible) .hit { fill: color-mix(in srgb, var(--accent) 8%, transparent) }`; under 720px `.chart-body { overflow-x: auto }` with `svg { min-width: 520px }` and the diagram "Scroll sideways" hint.

- [ ] **Step 1: Write failing test** `tests/test_charts.py::test_chart_tokens_in_every_theme_block` — asserts each `--chart-1|2|1-soft` value above appears in `:root {`, `:root:not([data-theme="light"])`, `:root[data-theme="dark"]`, and the print `:root:root:root` block with light values.
- [ ] **Step 2: Run** `.venv/bin/python -m pytest -q tests/test_charts.py tests/test_qa_fixes.py` — Expected: FAIL.
- [ ] **Step 3: Implement** tokens, styles, tooltip (pointerenter/focusin show, pointerleave/focusout/Escape hide; position above the mark, clamped to the viewport; `strong` for value, `span` for label, both via `textContent`).
- [ ] **Step 4: Run** the same command — Expected: PASS.
- [ ] **Step 5: Commit** `Style charts with shared tokens and add hover tooltips`.

### Task 4: Wrap the six tables, add two tables, render

**Files:**
- Modify: `projects/natd.qmd`, `projects/natd/report.qmd`, `projects/mailroom-ml/report.qmd`, `projects/mailroom-corpus-eda/report.qmd`, `projects/rvl-cdip-classifier.qmd`, `projects/mapreduce-reloaded.qmd`, `projects/langtons-ant.qmd`; regenerate `docs/`
- Test: `tests/test_charts.py`

**Interfaces:**
- Consumes: Task 2 attributes; spec table of charts (titles, columns, encodings).
- New tables (numbers verbatim from the page prose): RVL-CDIP "Measured before and after" (`Change | Before | After`: Escalation to a stronger model, 48-image low-confidence slice | 66.7% | 62.5%; Worked examples, 48-image slice | 68.8% | 64.6%; Escalation of v19, tuning slice | 97.5% | 96.9%); MapReduce "Speedup with four workers" (`Job | Speedup`: word count 3.8×; sort 2.9×; grep 2.3×).

- [ ] **Step 1: Write failing tests** in `tests/test_charts.py`:
  - `test_each_page_has_its_chart` — for the 7 built pages, exactly the expected count of `figure.chart` (NATD case study 1, NATD report 1, others 1 each) and each figure's next element sibling is a `table`.
  - `test_tip_values_match_table_cells` — for every `g.mark`, the numbers parsed from `data-tip-value` appear among the numbers of the following table.
  - `test_new_tables_come_from_prose` — every number in the two new tables appears in that page's prose outside the table.
  - `test_chart_shapes_have_fallback_paint` — every `rect|circle|line|path` inside `figure.chart svg` has `fill` and `stroke` attributes.
- [ ] **Step 2: Run** `.venv/bin/python -m pytest -q tests/test_charts.py` — Expected: FAIL (no charts yet).
- [ ] **Step 3: Wrap** the tables and add the two new tables; run `quarto render`.
- [ ] **Step 4: Run** `.venv/bin/python -m pytest -q tests/test_charts.py tests/test_links.py tests/test_site_integrity.py tests/test_qa_fixes.py` — Expected: PASS.
- [ ] **Step 5: Commit** `Chart six report tables` (source and `docs/`).

### Task 5: Browser tests, evidence and docs

**Files:**
- Modify: `tests/test_browser.py`, `.github/BUILDING.md` (charts paragraph in "How it fits together"; how to add a chart)
- Evidence (not committed): screenshots and a hover recording in the session scratchpad

**Interfaces:**
- Consumes: Tasks 2–4 markup and styles.

- [ ] **Step 1: Write failing tests** in `tests/test_browser.py`:
  - `test_chart_tooltip_hover_and_keyboard` — NATD case study: hover first `g.mark` → `.chart-tooltip` visible with text containing `+14.5`; Tab focus on a mark shows its value; Escape hides it.
  - `test_charts_dark_theme_and_no_script` — dark theme: computed `fill` of a `.c1` bar is `rgb(42, 163, 176)`; with JavaScript disabled, each chart page shows a visible `figure.chart svg`.
  - `test_charts_scroll_on_phone` — 375px: `.chart-body` has `scrollWidth > clientWidth`, accepts ArrowRight scrolling, and every `text` box in the SVG lies within the SVG's box.
- [ ] **Step 2: Run** `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/test_browser.py -k chart` — Expected: FAIL before fixes, then PASS after any needed CSS/JS fixes.
- [ ] **Step 3: Run the full suite:** `lua tests/test_site.lua`, `lua tests/test_charts.lua`, `node --test tests/theme.test.cjs tests/icons.test.cjs`, `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests` — Expected: all pass except the known `test_no_script_and_print_from_dark` (3-page résumé print, pre-existing).
- [ ] **Step 4: Capture evidence** — all six charts, light/dark, 1280 and 375px, plus a hover state; review each image for collisions and clipping.
- [ ] **Step 5: Commit** `Test charts in real browsers and document them`.

### Task 6: Preview and pull request

- [ ] **Step 1:** Publish the rendered chart pages as a private preview artifact so the owner can click through them in any browser (the built-in browser cannot reach this container).
- [ ] **Step 2:** Push `claude/sweet-shannon-wcsgcl`; open a PR against `main` covering both the visual refresh and the charts, with commands, results, evidence and what was not checked.
