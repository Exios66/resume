---
name: portfolio-hillclimb
description: Autonomous polish loop for this Quarto portfolio. Edit, render, audit, then keep or revert, one small change at a time, scored by an accessibility, layout and typography audit of every built page. Use when asked to polish, sweep, hill-climb, audit or improve the site's quality, accessibility, mobile layout or typography, or to resume a hill-climb from .autoresearch/.
---

# Portfolio polish hill-climb

A measured loop for making the site better without making it worse: **edit → render → audit → checks →
keep or revert → log → repeat**. Every experiment is one small, reviewable commit. The audit turns what
visitors, keyboard users and screen-reader users meet into one number, `polish_defects` (lower is better).
The number is a guide, not the goal. The goal is a polished, professional, beautiful portfolio that
builds on the existing design.

`AGENTS.md` applies throughout: `docs/` is generated (render, never hand-edit), run the real-browser
suite, review screenshots for visual changes, and report exact commands, results and what was not checked.

## Files

| File | Role | Change it? |
|---|---|---|
| `autoresearch.sh` | Benchmark: Quarto render, then the audit. Prints `METRIC` lines. | Only by starting a new segment |
| `autoresearch.audit.cjs` | The audit (axe-core, layout, structure, typography, errors, lints) | Only by starting a new segment |
| `autoresearch.checks.sh` | Correctness gate: Lua filter tests, Node tests, pytest + Chromium | No |
| `scripts/hillclimb/hc.sh` | Helper for every step below | Fix bugs only |
| `scripts/hillclimb/ledger.py` | Append-only run log, status, segments | Fix bugs only |
| `scripts/hillclimb/shot.cjs` | Screenshots into `.hillclimb-shots/` (outside the site) | Fix bugs only |
| `autoresearch.jsonl`, `autoresearch.md`, `autoresearch.ideas.md` | Living session state: run log, notes, ideas. **Gitignored** so a revert can never erase them | Every iteration |
| `.autoresearch/` | Committed snapshot of the living files, for hand-off and fresh clones | At hand-off points |

In scope for experiments: `styles.css`, `assets/js/site.js`, `scripts/*.lua`, `scripts/post-render.py`,
`partials/**`, `_quarto.yml`, `*.qmd`, and the rendered `docs/` (always via Quarto). Tests may change only
when they pin the exact text or markup an experiment changes on purpose (say so in the log).

## Audit (what the number means)

Every page in `docs/` at 375 px and 1280 px in light and dark themes, plus 320 px for layout only.

| Bucket | Finding | Points |
|---|---|---|
| axe | WCAG 2.0–2.2 A/AA + best-practice violation per node | critical 10, serious 5, moderate 2, minor 1 |
| layout | page wider than the screen | 20 |
| layout | table cell crushed (more text lines than words + 1) or code clipped (320, 375 px) | 2 |
| layout | table wider than the screen (320, 375 px) | 1 |
| layout | tap target under 24 px (375 px; a stretched-link overlay counts as its box) | 1 |
| layout | distinct text under 12 px (375 px) | 1 |
| layout | focusable control under 8 px | 5 |
| structure | heading level skipped; not exactly one h1 (1280 light) | 2 |
| type | visible `•`/`·` separator starting a wrapped line / ending one (375, 1280 light) | 2 / 1 |
| type | h1–h3 whose last line is a single word (375, 1280 light) | 1 |
| errors | console error, failed request, broken image | 10 |
| lint | content regressions fixed earlier (404 page, résumé contact, search titles) | 1–10 |

`hc.sh findings` lists each scored finding by viewport, page, kind and element. Read it before choosing
an experiment, and again after one, to see exactly what moved.

## Setup (once per clone)

1. Tools: Quarto 1.10.x (`QUARTO=` if not on PATH), Node 18+, Python venv at `.venv` with
   `requirements-test.txt`, Playwright Chromium (`PLAYWRIGHT_BROWSERS_PATH` if preinstalled elsewhere). See `.github/BUILDING.md`.
2. Branch: work on the branch you were given. Never on `main`.
3. Session state:
   - Resuming: `scripts/hillclimb/hc.sh restore` copies `.autoresearch/` back to the living files. Read
     `autoresearch.md` (learnings, history) and `autoresearch.ideas.md` (backlog) before anything else.
   - Fresh start: `scripts/hillclimb/ledger.py segment "<goal>"`, write `autoresearch.md` (goal, metrics,
     scope, rules, learnings) and `autoresearch.ideas.md`.
4. Baseline: `hc.sh baseline`, `hc.sh checks`, then `hc.sh log keep "baseline"`.

## The loop

Repeat until the owner stops you, the status says stop, or a set iteration budget runs out. Do not
stop to ask whether to continue.

1. **Status.** `hc.sh status`. Act on `VERDICT`: `continue`; `rethink` (3+ failures in a row: change
   approach, re-read sources, use the backlog); `wall` (more than 8: stop and report); `concluded` (ask).
2. **Choose one change.** Use `hc.sh findings`, screenshots and the backlog. Prefer the change that
   removes the most real defects with the least code. One idea per experiment.
3. **Edit** source files only.
4. **Experiment.** `hc.sh experiment "<what changed>" <source paths>` renders, audits, and commits the
   sources with `docs/`. Read the metric line and the non-zero breakdown.
5. **Look.** For anything visible, `hc.sh shot <page> 375 light <name> [--at sel --text words]` and the
   same at 1280 and in dark mode. Open the images. Check the changed spot and its neighbours.
6. **Checks.** `hc.sh checks`. All must pass to keep.
7. **Decide.**
   - Lower metric, checks pass, looks right → `hc.sh log keep "<what>" '<asi>'`.
   - Equal or higher, checks fail, or it looks worse → `hc.sh log discard|checks_failed "<what>" '<asi>'`,
     then `hc.sh discard`.
   - A side effect you can fix inside the same idea (e.g. bigger labels made the pager wrap): fix it,
     `git commit --amend`, re-run steps 4–6, then decide once.
8. **Record.** ASI is a JSON object that survives reverts: `hypothesis`, `result`, `next_action_hint`,
   plus anything specific. Every few runs, update `autoresearch.md` (learnings, history table via
   `ledger.py table`) and the backlog.
9. **Publish progress** every few keeps: `git push -u origin <branch>`.

## Rules that keep the number honest

- Never game the audit. No `display:none`, `aria-hidden`, shrinking or removing content to dodge a check.
  A lower number that looks worse or reads worse is a discard.
- The audit and checks are fixed within a segment. If the audit **mis-measures** (counts something a
  visitor cannot see, misses a real defect, or scores an artefact), log the affected run honestly, fix the
  audit in its own commit, `hc.sh segment "<why>"`, re-run the baseline, then reapply the experiment.
  Never change the audit to rescue a single experiment's score.
- Metric-blind improvements (real, but the audit cannot see them) are discarded at equal score. Add them to
  the backlog as "metric-blind" and raise them with the owner, or extend the audit in a new segment.
- Do not weaken or delete a test. Update one only when it pins exactly the text or markup you changed on
  purpose (for example, a test matching `class="kicker"` exactly once a filter adds a class).
- Project facts and numbers must match their source repositories. Do not invent results.
- Commit only files in scope. The living session files are gitignored for a reason.

## Hand-off

When stopping (owner request, wall, budget):
1. `ledger.py pause "<why>"` (or let the final status stand), update `autoresearch.md`.
2. `hc.sh snapshot`, commit `.autoresearch/`, push.
3. Open or update the pull request and an issue that lists: score history, what each kept change does,
   what was discarded and why, the remaining findings, the backlog, and what was not checked (other
   browsers, real devices, screen readers). Link evidence; do not paste screenshots of private data.

## Lessons from the first run (1282 → 22 points)

- Quarto's code-copy button needs Bootstrap Icons, which `theme: none` never loads; style it as a text
  "Copy" button instead.
- Overflowing tables, code blocks and diagrams need `tabindex="0"`, and code regions a `role="region"`
  with a unique label, or axe flags every one (site.js decides from measured overflow, rechecked after fonts load).
- Quarto's base CSS sets `code { white-space: pre }`. Wrapping inline code anywhere made layouts worse
  twice; stacking text tables into labelled rows on phones worked.
- Quarto's project link resolver rebuilds any table whose cells hold a link and drops attributes a filter
  added. Table stacking therefore lives in `scripts/tables.lua`, registered `at: post-render`.
- Lua patterns are byte-based; compare multi-byte prefixes (≥ ≤ − ≈ ±) as whole strings.
- `content: attr(data-label) / ""` keeps stacked-table labels from being read twice by screen readers.
- Separators in "A · B · C" labels: lead each later part with its separator and clip a line-start one in a
  hidden gutter; a centred line cannot clip, so its parts stack on phones.
- `text-wrap: balance` on h1–h3 removed nearly every one-word last line.
- Hyphenating table headers to narrow grids made cells "crushed"; discarded.
- Quarto rewrites every `lastmod` in `docs/sitemap.xml` on each render; `hc.sh` drops that churn unless pages changed.
