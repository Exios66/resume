# Autoresearch: polish the portfolio site

## Objective
Hill-climb toward a fully polished, professional, beautiful portfolio that builds on the existing design
(Newsreader/Inter/JetBrains Mono, teal accent, light/dark themes, cards, inline SVG charts and diagrams).
Fix what visitors, keyboard users and screen-reader users actually meet; never trade looks for a lower count.

## Metrics
- **Primary:** `polish_defects` (weighted defect points, lower is better), from `autoresearch.audit.cjs` on a fresh render.
  - axe-core violations x impact (critical 10, serious 5, moderate 2, minor 1), 375 and 1280 px, light and dark
  - layout: page overflow 20; crushed or clipped table cells 2 each (320 and 375 px); tables wider than the screen 1;
    tap targets < 24 px 1; unique text < 12 px 1 (375 px); invisible focusable controls 5 (per combo)
  - structure: heading skips 2, pages without exactly one h1 2
  - errors: console, network, broken images 10 each
  - lint: no 404 page 10; résumé "Portfolio" text 3; résumé lacks GitHub profile 3; search titles repeat site name 3;
    `mailroom-ml` spelling 1; "Open to Relocation" 1
- **Secondary:** axe_points, layout_points, error_points, structure_points, lint_points, pages, css_kb, audit_s, render_s

## How to run
`bash autoresearch.sh > run.log 2>&1` (renders with Quarto 1.10.19 at /opt/quarto, ~70 s); breakdown in `audit.details.json`.
Checks: `bash autoresearch.checks.sh` (Lua via bundled pandoc, Node, pytest + Chromium; ~70 s).

## Files in scope
`styles.css`, `assets/js/site.js`, `scripts/*.lua`, `scripts/post-render.py`, `partials/**`, `_quarto.yml`, every `.qmd`,
new `404.qmd`, `docs/` (rendered output only, always via `quarto render`), `assets/Jack_Burleson_Resume.pdf`
(regenerate with `scripts/make-resume-pdf.py` whenever `resume.qmd` changes), tests that encode the exact content changed.

## Off limits
`autoresearch.sh`, `autoresearch.checks.sh`, `autoresearch.audit.cjs` (immutable harness). Hand edits to `docs/`.
Project numbers and claims (must match source repos). Removing or hiding content to dodge a check.

## Constraints and anti-cheating rules
- All checks pass. Do not delete or weaken a test; update a test only when it pins the exact text being changed on purpose.
- Visual review of screenshots for every kept change (SHOT_DIR=... node autoresearch.audit.cjs). A lower count that looks worse is a discard.
- No `display:none`/`aria-hidden` tricks to hide defects; no shrinking content to avoid overflow checks.
- Commit sources + rendered `docs/` together per experiment; restore `docs/sitemap.xml` churn on discards via revert.
- Branch: `claude/serene-fermat-yr920i` (required by the session; not a separate autoresearch/* branch).

## Segments
- 0: original audit (served at /docs/). 1: audit serves docs/ at /resume/ like GitHub Pages.
- 2: adds typography (separator that starts a line 2, ends a line 1; heading ending on a one-word line 1, at 375 and 1280 light);
  stretched card links measured by the overlay box; table-cell lines counted from text nodes, not padded code boxes.
- 3: characters clipped by an overflow ancestor are not counted (they are not seen).

## What's been tried
| # | Seg | Description | polish_defects | Status |
|---|---|---|---|---|
| 0 | 0 | Baseline (620 axe scrollable-region-focusable, 280 invisible copy buttons, 152 table issues) | 1282 | keep |
| 1 | 0 | Visible text-labelled code copy button | 988 | keep |
| 2 | 0 | Keyboard access (tabindex/role/label) for scrolling tables, code blocks, diagrams | 368 | keep |
| 3 | 0 | Inline code pre-wrap + overflow-wrap anywhere | 657 | discard |
| 4 | 0 | Inline code pre-wrap + break-word | 388 | discard |
| 5 | 0 | Stack text-heavy tables into labelled rows on phones | 311 | keep |
| 6 | 0 | Column-aware table classification; stacked figures label-left value-right | 291 | keep |
| 7 | 0 | Résumé contact shows addresses, adds GitHub, Mailroom-ML spelling, PDF regenerated | 283 | keep |
| 8 | 0 | Custom 404 page (scored badly only because audit served /docs/) | 1105 | discard |
| 9 | 1 | Segment 1 baseline | 283 | keep |
| 10 | 1 | Custom 404 page with site chrome and ways back | 274 | keep |
| 11 | 1 | Search results drop the repeated site name | 271 | keep |
| 12 | 1 | 24 px tap targets: site title, back links | 193 | keep |
| 13 | 1 | Labels and caption code at 12 px minimum; project pager stacks under 480 px | 101 | keep |
| 14 | 1 | Tighter number grids on phones | 87 | keep |
| 15 | 1 | Psychometric band row split into three rows (metric-blind, still worth doing) | 87 | discard |
| 16 | 1 | Tables whose cells hold links now stack (table filter moved to post-render) | 85 | keep |
| 17 | 1 | Hyphenate grid headers on phones | 97 | discard |
| 18 | 2 | Segment 2 baseline | 63 | keep |
| 19 | 2 | Separator splitting (scored badly: audit counted clipped separators) | 162 | discard |
| 20 | 3 | Segment 3 baseline | 63 | keep |
| 21 | 3 | Separators never start or end a wrapped label | 42 | keep |
| 22 | 3 | Balanced heading lines (text-wrap: balance on h1-h3) | 22 | keep |

## Remaining at 22 points
- Tables wider than the screen: 13 (5-6 column number grids in psychometric-digital-twin, mailroom-ml appendix, natd at 320 px). They scroll and are keyboard reachable.
- Crushed table cells: 4 cells (8 pts), long code paths and model names in narrow columns.
- Heading widow: 1 ("Graduate research, UW–Madison" at 375 px; UW–Madison is one unit, acceptable).

## Learnings
- Quarto base CSS sets `code { white-space: pre }` and relaxes it only for `p code`/`dd code`; table-cell code can't wrap.
- Quarto's copy button needs Bootstrap Icons, which `theme: none` never loads, so it renders 12x2 px.
- `quarto render` rewrites every `lastmod` in `docs/sitemap.xml`; that churn is expected (restore it on discards).
- Quarto's project link resolver rebuilds any table whose cells hold a link and drops attributes a filter added; table
  stacking therefore runs in `scripts/tables.lua` registered `at: post-render`.
- Lua patterns are byte-based: compare multi-byte prefixes (≥ ≤ − ≈ ±) as whole strings.
- `content: attr(data-label) / ""` keeps stacked-table labels from being read twice by screen readers.
- Tests that match `class="kicker"` exactly break when a filter adds classes; match by class membership.
- Hyphenating headers or wrapping inline code anywhere both made layout worse.
