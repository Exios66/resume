# Metrics and targets for auto-research on the portfolio

Use this file to choose a goal, measure it, and know when to stop. It adds to the polish hill-climb in
`.claude/skills/portfolio-hillclimb/SKILL.md`; it does not replace it. Roadmap and tasks: issue #117.

## How far the goalposts have moved

| Date | `experience_gaps` | What changed |
| --- | ---: | --- |
| 10 Nov 2026 (post #116) | **125** | Motif system and covers on main |
| 12 Nov 2026 (post #148) | **19** | Image sizing, lazy loading, lead captures (#119) |
| 19 Nov 2026 evening (run 73) | **5** | Per-project social cards (#120 measured) |
| 20 Nov 2026 (design stack) | **5** | Track 2 motion and aesthetic hardening; number cannot fall without #121 owner titles |

`polish_defects` has been **0** for many segments. Equal-score `5 → 5` keeps no longer prove Track 1 progress; they are craft work under the levels below. Do not treat a flat `experience_gaps` chart as failure, and do not invent titles or motifs to force the number down.

## Quality levels (grade the loop here)

Each level assumes every lower level still holds. Agents pick the **lowest incomplete** level as the grading bar for a session.

| Level | Name | Bar | How to pass a keep | Stop / escalate when |
| --- | --- | --- | --- | --- |
| **L0** | Safety net | `polish_defects=0`, checks pass, `pages_over_budget=0` | Regression only: discard any break | A deliberate design finding is recorded, not gamed away |
| **L1** | Measured Track 1 | `experience_gaps` ≤ 5, all KPI parts at target except owner titles | A keep that lowers a gap, or a guard that prevents a regression | Remaining gaps are only `repo_style_titles` (**current**) |
| **L2** | Craft / Track 2–3 | Judged motion and layout feel finished; weight soft limits hold | Screenshots + checks; log as judged keep when the number is flat | Owner says stop, or residual #122 tasks need a design section |
| **L3** | Owner closure | Titles, motif specificity, OG contact sheet signed off | Owner wording / confirmation only | #118, #120 signoff, #121 titles done |
| **L4** | Roadmap complete | `experience_gaps=0` + all judged indicators at target + three-engine scope recorded | Issue #117 acceptance | Close #126 / #117 with evidence |

**Current grade (20 Nov 2026, design branch):** **L1 held; working in L2.** Measured Track 1 is complete except owner-gated titles. Further hill-climb keeps must improve a judged indicator, close a residual #122–#125 task, or harden a regression—not chase a number that cannot move.

### What “good enough” means at L2

- Motion uses the shared `--motion-*` scale and is off under reduced motion, print, and forced colours.
- Small aesthetic slips (spacing rhythm, phone CTA crowding, theme-fade orphans, print chrome) are fair game; inventing content or display titles is not.
- Soft weight: treat **≥90% of a page/asset budget** as yellow and **≥95%** as red before adding CSS/JS or case-study prose.
- Do not open a new KPI part in the same PR that “improves” it.

## How to measure

```
. .autoresearch-tools/env.sh
bash autoresearch.sh                      # renders docs/, prints METRIC polish_defects=...
.venv/bin/python scripts/hillclimb/kpi.py # prints METRIC experience_gaps=... and its parts
bash autoresearch.checks.sh               # correctness gate: must end with "All checks passed."
```

## Gates (every experiment must hold these; a change that breaks one is discarded)

| Gate | Command | Required |
| --- | --- | --- |
| Correctness | `bash autoresearch.checks.sh` | All checks passed |
| Polish audit | `scripts/hillclimb/hc.sh findings` | `polish_defects` stays at 0, or the new finding is a recorded design choice |
| Page weight | `kpi.py` | `pages_over_budget` = 0 for **every** built page type (see budgets below), not only home and projects index |

Never edit the audit, the checks or `kpi.py` to rescue a result. Change them only in a separate pull request that says why.
Page budgets and classification live in `scripts/hillclimb/page_budgets.py` so `kpi.py` and
`tests/python/test_page_budget.py` stay aligned.

## Primary metric for the experience loop: `experience_gaps` (lower is better, target 0)

It is the sum of the counts below. Baseline measured on `main` after pull request #116, 10 November 2026: **125**.
After #148 (image sizing/lazy): **19**. After hill-climb run 73 (per-project social cards, 19 November 2026 evening):
**5**. The KPI expansion (full-site page budgets plus chart-title and figure-alt guards) still reads those new
parts as 0; `pages_over_budget` counts every page type (currently 0).

| Part | Baseline | Now (20 Nov 2026) | Target | Closed by |
| --- | ---: | ---: | --- | --- |
| `cards_without_cover` | 0 | 0 | 0 | done (#116); regression guard |
| `repo_style_titles` | 5 | 5 | 0 | #121; **owner titles only** — L3 |
| `projects_without_own_social_card` | 14 | 0 | 0 | #120 measured (run 73); owner contact-sheet signoff still L3 |
| `projects_without_structured_data` | 0 | 0 | 0 | guard |
| `images_without_size` | 61 | 0 | 0 | #119 |
| `later_images_not_lazy` | 45 | 0 | 0 | #119 |
| `pages_over_budget` | 0 | 0 | 0 | gate; every page type in `page_budgets.py` |
| `charts_without_title` | — | 0 | 0 | guard (#139) |
| `figures_without_alt` | — | 0 | 0 | guard |

At **5**, the metric is **owner-blocked**. Scripts must not invent the five display titles. Grade L2+ work with judged
indicators and gates, not with a fake drop in `experience_gaps`.

Secondary numbers (gzip bytes of the heaviest page of each type, plus shared assets), refreshed 20 Nov 2026 on the
design stack: `gz_home` 15,103; `gz_projects_index` 24,968; `gz_case_study` 19,255; `gz_technical_report` 19,693;
`gz_appendix` 11,997; `gz_other_page` 12,451; `gz_styles_css` 17,850; `gz_site_js` 7,199.
Soft limits: CSS 20,000; JavaScript 9,000. `kpi.py` prints an `INFO heaviest_…` line naming the page behind each
`gz_*` size.

## Page transfer budgets

Refreshed 20 November 2026 against the design-stack build (motion + aesthetic hardening). Sizes are gzipped HTML
bytes at compression level 9; the shared stylesheet and script are measured separately because every page pays for
them. `tests/python/test_page_budget.py` and `kpi.py` both import `scripts/hillclimb/page_budgets.py`.

| Page type | Heaviest page now | Measured | Budget | Headroom | Pressure |
| --- | --- | ---: | ---: | ---: | --- |
| Home | `index.html` | 15,103 | 16,000 | 6% | yellow (≥90%) |
| Projects index | `projects/index.html` | 24,968 | 26,000 | 4% | red (≥95%) |
| Case study | `projects/mapreduce-reloaded.html` | 19,255 | 19,500 | 1% | red |
| Technical report | `projects/natd/report.html` | 19,693 | 22,000 | 10% | ok |
| Appendix | `projects/langtons-ant/appendix.html` | 11,997 | 13,000 | 8% | yellow |
| Other page | `resume.html` | 12,451 | 15,000 | 17% | ok |
| Shared stylesheet | `styles.css` | 17,850 | 20,000 | 11% | ok (watch motion CSS) |
| Shared script | `assets/js/site.js` | 7,199 | 9,000 | 20% | ok |

The case-study budget was raised from 19,000 to 19,500 on 19 November 2026 because the Track 2 theme cross-fade
script lands on every page and MapReduce was already within 20 bytes of the old ceiling. Raising a budget is a
deliberate decision that belongs in the pull request, with the reason and the new measurement. Do not trim
meaningful content only to pass the gate. Prefer cutting decorative CSS/JS before raising budgets again.

## Judged indicators (a person or a reviewing agent scores these; a script cannot)

These are the **L2 / L3 scoreboard** while `experience_gaps` sits at 5.

| Indicator | Now (20 Nov 2026) | Target | How it is scored |
| --- | --- | --- | --- |
| Motifs that pass the specificity test | 8 of 14, not yet owner-confirmed | 14 of 14, owner confirmed | Test in #118: cover the title; the drawing must fit only its project |
| Case studies of visual projects that lead with a real screenshot | **2 of 2** (#148) | 2 of 2 | #119; real captures only — **measured done** |
| Motion scale + hero drift + chart draw-in + theme cross-fade | Shipped on design stack (runs 74–86); matrix test incomplete | Spec items + browser proof | #122; still open: page transitions, per-motif life, stat count-up, full reduced-motion/print/forced-colours test |
| Aesthetic hardening (spacing, phone chrome, print leftovers) | Runs 80–86 kept with evidence | No obvious slips at 375/1280 light+dark | Judged; screenshots required |
| Browsers checked | Chromium suite; targeted Firefox/WebKit chart and video cases | Chromium, Firefox, WebKit with scope recorded | #125; real devices remain unverified |

Do not turn a judged indicator into a number by guessing. Record who judged it and attach the screenshot.
Do not tick #122 complete until its unchecked tasks and the motion matrix test land.

## Rules for the loop

1. One small change per experiment. Measure before and after with the commands above.
2. Keep a change only if all gates hold, **`experience_gaps` does not rise** (L2 inherits L1: once the floor is ≤ 5, a keep may not push it above 5), **and** one of: `experience_gaps` falls; a judged indicator improves with evidence at an equal score; a residual roadmap task closes with evidence; or a clear regression risk is removed (guard/hardening) without making the look worse.
3. At L1 complete / L2 active, a flat `experience_gaps` is expected. Log design keeps as judged changes with screenshots (design-spec rule 8). The ledger may still show metric 5; that is not a reason to discard a good craft keep. **This file governs** equal-score judged keeps; `.claude/skills/portfolio-hillclimb/SKILL.md` defers here when the two conflict.
4. Do not game a metric: no hidden images to satisfy a count, no fake sizes, no title changes without the owner's wording.
5. Report `experience_gaps` after each render. Since the experience-scored tooling landed (#126), `autoresearch.sh` also prints the KPI metrics and the ledger can score `experience_gaps` directly: start such a segment with `hc.sh segment "<name>" --metric experience_gaps --gate polish_defects=0`. Never edit the audit, the checks or `kpi.py` to rescue a result.
6. Prefer weight-neutral or weight-negative CSS when projects index or MapReduce are in the red band.

## How to raise each metric

Measured after run 73 + KPI expansion + design stack through run 86: `experience_gaps` = **5**. The remaining gaps are
repository-style display titles (#121). Chart-title and figure-alt guards are at 0; keep them there. Re-run
`kpi.py` before starting; these counts drift as the portfolio grows.

### 1. `repo_style_titles` (5): owner decision first — L3

- The five cards are Digital-Mailroom, Mailroom-ML, RVL-CDIP-Classifier, Mailroom-Corpus-EDA and MapReduce-Reloaded.
- **Lever (#121):** ask the owner for the display titles. Do not write them yourself (rule 4). Once given, change
  only the card and page titles and keep the repository names in links and code.

### 2. Page-weight headroom (gate; pressure bands above)

| Number | 10 Nov | 19 Nov evening | 20 Nov design | Limit | Note |
| --- | ---: | ---: | ---: | ---: | --- |
| `gz_projects_index` | 23,702 | 24,670 | 24,968 | 26,000 | Red; new cards need shorter copy elsewhere |
| `gz_case_study` | 16,028 | 19,008 | 19,255 | 19,500 | Red; MapReduce is the ceiling |
| `gz_home` | 14,127 | 14,816 | 15,103 | 16,000 | Yellow; Explore tiles added weight |
| `gz_styles_css` | 14,935 | 15,653 | 17,850 | 20,000 | Motion/aesthetic CSS; still under soft limit |
| `gz_site_js` | 5,683 | 6,643 | 7,199 | 9,000 | Watch chart draw-in and page-enter |

### 3. `#120` social cards (measured closed; owner signoff open — L3)

- Run 73 wrote `assets/og/<slug>.png` from cover motifs via `scripts/build/make-og.py` and set absolute `image:` URLs.
- `projects_without_own_social_card=0`. Keep regenerating after #118 motif redraws; owner contact-sheet signoff remains.

### 4. Track 2 residual (#122) — L2

Still open relative to the issue checklist: cross-page view transitions, per-motif hover life (one motif first for
approval), stat count-up with final number in HTML, and a browser test that the motion matrix is off under reduced
motion, print and forced colours. Shipped pieces (tokens, hero drift, chart draw-in, theme cross-fade, nav/card
polish) count toward L2 craft but do not close #122 alone.

## Metrics worth adding next

`experience_gaps` already includes chart-title and figure-alt guards and full-site page budgets. Each new candidate
needs a separate, reviewed change to `kpi.py` (or a test), a fresh baseline recorded here, and a target. Never add
one in the same pull request that improves it. Prefer candidates that score **L2** work the ledger currently
flattens to `5 → 5`.

| Candidate | Why | How to count |
| --- | --- | --- |
| `motion_matrix_gaps` | Track 2 “done when” is still manual | Count of #122 checklist items without a passing browser assertion (reduced motion / print / forced colours) |
| `layout_shift` | `images_without_size` is a proxy; this measures the effect | Playwright `PerformanceObserver('layout-shift')` on the five heaviest pages at 375 px; report the worst page |
| `largest_paint_ms` | Real speed, not only bytes | Playwright LCP on the home and projects index pages, median of 3 runs; report it, do not gate on it, because CI timing is noisy |
| `wip_pages_without_status` | Portfolio expansion adds WIP tracks; stale claims confuse visitors | Project pages whose front matter or body marks WIP but lack a visible status callout the audit already expects |
| `weight_pressure` | Soft yellow/red bands above are easy to ignore | Count of page/asset rows at ≥90% of budget; report beside `pages_over_budget` |

## Making the loop score experience (#126)

Landed 2026-11-12 in the experience-ledger tooling PR:

1. The primary metric name comes from the segment config; `polish_defects` is only the default (`scripts/hillclimb/ledger.py`).
2. `autoresearch.sh` runs `kpi.py` after the polish audit and prints both sets of `METRIC` lines.
3. Start the segment with `hc.sh segment "<name>" --metric experience_gaps --gate polish_defects=0`, then log the baseline on the same commit with `hc.sh baseline`. A run whose gate fails cannot be logged as keep.
4. Regression tests live in `tests/python/test_ledger.py`.

While `experience_gaps` is stuck at 5, keep using that segment for the polish gate, but grade session success by
**level L2/L3 criteria**, not by expecting the ledger best to beat run 73’s metric of 5.

## Success points

- **L1 / Track 1 measured complete:** `experience_gaps` ≤ 5 (only the title decision left) and both lead screenshots in place. **Met** (run 73 + #148).
- **L2 / craft bar:** residual #122 motion items and aesthetic hardening land with evidence; weight stays out of red where possible. **In progress** (design stack runs 74–86).
- **L3 / owner closure:** #121 titles, #118 motif confirmation, #120 OG contact-sheet signoff.
- **L4 / roadmap complete:** `experience_gaps` = 0, all judged indicators at target, all gates green with three-browser scope recorded.
