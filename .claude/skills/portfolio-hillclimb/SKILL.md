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
| `findings.tsv`, `findings.best.tsv`, `checks.ok`, `checks.log`, `run.log` | Latest findings, best kept findings, checks stamp and logs (gitignored) | Written by `hc.sh` |
| `.hillclimb-evidence/run-N.md`, `.hillclimb-shots/` | Evidence records and screenshots, outside the site (gitignored) | Written by `hc.sh` |

In scope for experiments: `styles.css`, `assets/js/site.js`, `scripts/*.lua`, `scripts/post-render.py`,
`partials/**`, `_quarto.yml`, `*.qmd`, and the rendered `docs/` (always via Quarto). Tests may change only
when they pin the exact text or markup an experiment changes on purpose (say so in the log).

## Audit (what the number means)

Every page in `docs/` at 375, 414, 768 and 1280 px in light and dark themes, plus 320 px for layout only.

| Bucket | Finding | Points |
|---|---|---|
| axe | WCAG 2.0–2.2 A/AA + best-practice violation per node | critical 10, serious 5, moderate 2, minor 1 |
| layout | page wider than the screen | 20 |
| layout | table cell crushed (more text lines than words + 1) or code clipped (320, 375 px) | 2 |
| layout | table wider than the screen (320, 375 px) | 1 |
| layout | tap target under 24 px (375 px; a stretched-link overlay counts as its box) | 1 |
| layout | distinct text under 12 px (375 px) | 1 |
| layout | SVG figure with rendered text under 12 px (one point per figure and viewport/theme) | 1 |
| layout | focusable control under 8 px | 5 |
| structure | heading level skipped; not exactly one h1 (1280 light) | 2 |
| type | visible `•`/`·` separator starting a wrapped line / ending one (375, 1280 light) | 2 / 1 |
| type | h1–h3 whose last line is a single word (375, 1280 light) | 1 |
| errors | console error, failed request, broken image | 10 |
| lint | content regressions fixed earlier (404 page, résumé contact, search titles) | 1–10 |

`hc.sh findings` lists each scored finding by viewport, page, kind and element. Read it before choosing
an experiment, and again after one, to see exactly what moved.

## Tools and how to get them

Run `scripts/hillclimb/hc.sh doctor` first. It checks each tool and prints how to install whatever is missing.

| Tool | Used for | How to get it |
|---|---|---|
| Quarto 1.10.x (bundles pandoc and its Lua) | rendering `docs/`; Lua filter tests | quarto.org, or set `QUARTO=/path/to/quarto` |
| Node 18+ with `playwright` | the audit and screenshots | `npm install --no-save playwright` (match the Python version) |
| axe-core 4.10.2 | accessibility rules | installed automatically into `.autoresearch-tools/` (never published) |
| Python venv `.venv` | pytest and the browser suite | `python3 -m venv .venv && .venv/bin/pip install -r requirements-test.txt` |
| Chromium for Playwright | audit, screenshots, browser tests | `npx playwright install chromium`, or `PLAYWRIGHT_BROWSERS_PATH` for a preinstalled set |
| git | one commit per experiment | — |

See `.github/BUILDING.md` for the full build setup.

## Setup (once per clone)

1. **Branch.** Work on the branch you were given, never on `main`.
2. **Tools.** `hc.sh doctor` must end with `All tools present.`
3. **Session state.**
   - Resuming: `hc.sh restore` copies `.autoresearch/` back to the living files. Read `autoresearch.md` and
     `autoresearch.ideas.md` before anything else.
   - Fresh start: `python3 scripts/hillclimb/ledger.py segment "<goal>"`, then write `autoresearch.md` (goal,
     metrics, scope, rules, learnings) and `autoresearch.ideas.md` (backlog).
4. **Baseline.** `hc.sh baseline`, then `hc.sh checks`, then `hc.sh log keep "baseline"`. The first run of a
   segment is its baseline and is the only keep that needs no evidence record.

## The loop, step by step

Repeat until the owner stops you, the status says stop, or a set iteration budget runs out. Do not stop to
ask whether to continue. Every step names its command and what you must see before going on.

| # | Step | Command | Pass condition |
|---|---|---|---|
| 1 | Status | `hc.sh status` | `VERDICT=continue`. `rethink`: change approach and read the backlog. `wall` (more than 8 failures in a row): stop and report. `concluded`: ask the owner. |
| 2 | Choose | `hc.sh findings` (lists every scored finding in `findings.tsv`) | One idea that removes real defects with little code. Write the hypothesis down. |
| 3 | Edit | your editor | Only in-scope source files. Never `docs/` by hand. |
| 4 | Experiment | `hc.sh experiment "<what>" <source paths>` | It prints `run N committed as ...` and the metric line. Note N. |
| 5 | Look | `hc.sh shot <page> <width> <light\|dark> run-N-<page>-<width>-<theme> [--at css --text words]` | For any visible change: 375 and 1280 px, light and dark, at the changed spot. Open every image. |
| 6 | Checks | `hc.sh checks` | `All checks passed.` It stamps the commit in `checks.ok`. |
| 7 | Evidence | `hc.sh evidence "<what you saw in each screenshot>"` | Writes `.hillclimb-evidence/run-N.md`. Read it: the findings delta must match what you meant to change. |
| 8 | Decide | `hc.sh log keep "<what>" '<asi>'`, or `hc.sh log discard\|crash\|checks_failed "<what>" '<asi>'` then `hc.sh discard` | See the decision rules below. |
| 9 | Record | edit `autoresearch.md`, `autoresearch.ideas.md`; `python3 scripts/hillclimb/ledger.py table` | Every few runs. |
| 10 | Publish | `git push -u origin <branch>` | Every few keeps. |

**Decision rules.**
- Keep only if the score is lower, checks pass, the screenshots look right, and nothing nearby got worse.
- Equal or higher score, failed checks, or a worse look: log it with the reason in the ASI, then `hc.sh discard`.
- A side effect you can fix inside the same idea (bigger labels made the pager wrap): fix it,
  `git commit --amend`, re-run steps 4–7, then decide once.
- ASI is a JSON object that survives reverts: `hypothesis`, `result`, `next_action_hint`, plus anything specific.

## Evidence contract

A keep is a claim that one change made the site better. `hc.sh log keep` refuses it unless the claim is backed:

1. **Checks passed on this exact commit.** `checks.ok` holds HEAD's hash. Any later edit or amend voids it.
2. **An evidence record exists** at `.hillclimb-evidence/run-N.md`. It holds the commit and parent, the source
   diffstat, the full metric line, the findings removed and added against the best kept state
   (`findings.best.tsv`), the checks summary, the screenshot paths, your review notes and what was not checked.
3. **Screenshots exist for visible changes.** If the commit touches `.css`, `.qmd`, `.lua`, `.js` or `.html`,
   at least one `.hillclimb-shots/run-N-*.png` must exist, and you must have opened it.
4. **Review notes are written.** `hc.sh evidence` without notes leaves "none given", and the keep is refused.
5. **No session links.** Descriptions and ASI with session URLs, co-author trailers or tool footers are refused.

After a keep, `findings.tsv` becomes `findings.best.tsv`, so the next record shows only that experiment's delta.
Screenshots stay in `.hillclimb-shots/` and records in `.hillclimb-evidence/`, both outside the published site.
`hc.sh snapshot` copies the records (not the images) into `.autoresearch/evidence/` for hand-off. Before
sharing any screenshot, check it for private data.

The gate checks that evidence exists, not that it is true. Never write notes for images you did not open, and
never claim checks, browsers or devices you did not run.

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
   Commit messages, pull requests, issues and comments carry no session links, co-author trailers or tool footers.
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
