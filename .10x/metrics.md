# Metrics and targets for auto-research on the portfolio

Use this file to choose a goal, measure it, and know when to stop. It adds to the polish hill-climb in
`.claude/skills/portfolio-hillclimb/SKILL.md`; it does not replace it. Roadmap and tasks: issue #117.

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
**5**. The 19 November KPI expansion (full-site page budgets plus chart-title and figure-alt guards) still reads
those new parts as 0; `pages_over_budget` counts every page type (currently 0).

| Part | Baseline | Now (19 Nov 2026 evening) | Target | Closed by |
| --- | --- | ---: | --- | --- |
| `cards_without_cover` | 0 | 0 | 0 | done (#116); guards against regressions |
| `repo_style_titles` (card titles that are hyphenated repository names) | 5 | 5 | 0 | #121; needs the owner's titles first |
| `projects_without_own_social_card` | 14 | 0 | 0 | #120; generator + front matter in run 73 (`e128dee`); owner visual signoff still open |
| `projects_without_structured_data` | 0 | 0 | 0 | guard |
| `images_without_size` (no `width` and `height`) | 61 | 0 | 0 | #119 |
| `later_images_not_lazy` (not the first image on a page, and not `loading="lazy"`) | 45 | 0 | 0 | #119 |
| `pages_over_budget` | 0 | 0 | 0 | gate; every page type in `page_budgets.py` |
| `charts_without_title` | — | 0 | 0 | guard (#139); `figure.chart` missing/empty `figcaption.chart-title` |
| `figures_without_alt` | — | 0 | 0 | guard; empty `alt`, or `alt` that only repeats the figcaption |

Secondary numbers, reported but not summed (gzip bytes of the heaviest page of each type, plus shared assets):
`gz_home` 14,816; `gz_projects_index` 24,670; `gz_case_study` 18,989; `gz_technical_report` 19,388;
`gz_appendix` 11,699; `gz_other_page` 12,181; `gz_styles_css` 15,653; `gz_site_js` 6,643.
Soft limits: CSS 20,000; JavaScript 9,000. `kpi.py` prints an `INFO heaviest_…` line naming the page behind each
`gz_*` size.

## Page transfer budgets

Refreshed 19 November 2026 against the current built site. Sizes are gzipped HTML bytes at compression level 9;
the shared stylesheet and script are measured separately because every page pays for them.
`tests/python/test_page_budget.py` and `kpi.py` both import `scripts/hillclimb/page_budgets.py`, so a new project
page or a heavier case study moves both the gate and `pages_over_budget` together.

| Page type | Heaviest page now | Measured | Budget | Headroom |
| --- | --- | ---: | ---: | ---: |
| Home | `index.html` | 14,816 | 16,000 | 7% |
| Projects index | `projects/index.html` | 24,670 | 26,000 | 5% |
| Case study | `projects/mapreduce-reloaded.html` | 18,981 | 19,000 | under 1% |
| Technical report | `projects/natd/report.html` | 19,401 | 22,000 | 12% |
| Appendix | `projects/langtons-ant/appendix.html` | 11,716 | 13,000 | 10% |
| Other page | `resume.html` | 12,181 | 15,000 | 19% |
| Shared stylesheet | `styles.css` | 15,653 | 20,000 | 22% |
| Shared script | `assets/js/site.js` | 6,643 | 9,000 | 26% |

The case-study budget is the tightest: MapReduce sits 11 bytes under 19,000. Raising a budget is a deliberate
decision that belongs in the pull request, with the reason and the new measurement. Do not trim meaningful
content only to pass the gate.

## Judged indicators (a person or a reviewing agent scores these; a script cannot)

| Indicator | Now | Target | How it is scored |
| --- | --- | --- | --- |
| Motifs that pass the specificity test | 8 of 14, not yet confirmed by the owner | 14 of 14, owner confirmed | Test in #118: cover the title; the drawing must fit only its project |
| Case studies of visual projects that lead with a real screenshot | 0 of 2 | 2 of 2 | #119; real captures only |
| Motion that is off under reduced motion, print and forced colours | Live reduced-motion video pause covered; full roadmap matrix remains open | 100%, with a browser test | #122 |
| Browsers checked | Chromium suite; targeted Firefox/WebKit chart and video cases (#133/#129) | Chromium, Firefox, WebKit with scope recorded | #125; real devices remain unverified |

Do not turn a judged indicator into a number by guessing. Record who judged it and attach the screenshot.

## Rules for the loop

1. One small change per experiment. Measure before and after with the commands above.
2. Keep a change only if all gates hold and either `experience_gaps` falls or a judged indicator improves with evidence.
3. Design work that moves no number is allowed (rule 8 of the design spec). Log it as a judged change with screenshots.
4. Do not game a metric: no hidden images to satisfy a count, no fake sizes, no title changes without the owner's wording.
5. Report `experience_gaps` after each render. Since the experience-scored tooling landed (#126), `autoresearch.sh` also prints the KPI metrics and the ledger can score `experience_gaps` directly: start such a segment with `hc.sh segment "<name>" --metric experience_gaps --gate polish_defects=0`. Never edit the audit, the checks or `kpi.py` to rescue a result.

## How to raise each metric

Measured after run 73 + the 19 November 2026 KPI expansion: `experience_gaps` = **5**. The remaining gaps are
repository-style display titles (#121). Chart-title and figure-alt guards are at 0; keep them there. Re-run
`kpi.py` before starting; these counts drift as the portfolio grows.

### 1. `repo_style_titles` (5): owner decision first

- The five cards are Digital-Mailroom, Mailroom-ML, RVL-CDIP-Classifier, Mailroom-Corpus-EDA and MapReduce-Reloaded.
- **Lever (#121):** ask the owner for the display titles. Do not write them yourself (rule 4 below). Once given, change
  only the card and page titles and keep the repository names in links and code.

### 2. Page-weight headroom (gate, not a gap count until a page crosses)

| Number | 10 Nov | 19 Nov evening | Limit | Note |
| --- | ---: | ---: | ---: | --- |
| `gz_projects_index` | 23,702 | 24,670 | 26,000 | 95% used; a new card or longer card text can break it |
| `gz_case_study` | 16,028 | 18,981 | 19,000 | MapReduce is 19 bytes under after the social-card description trim |
| `gz_home` | 14,127 | 14,816 | 16,000 | 93% used |
| `gz_site_js` | 5,683 | 6,643 | 9,000 | Watch phone-chart and motion additions |
| `gz_styles_css` | 14,935 | 15,653 | 20,000 | |

### 3. `#120` social cards (measured closed; owner signoff open)

- Run 73 wrote `assets/og/<slug>.png` from cover motifs via `scripts/build/make-og.py` and set absolute `image:` URLs.
- `projects_without_own_social_card=0`. Keep regenerating after #118 motif redraws; owner contact-sheet signoff remains.

## Metrics worth adding next

`experience_gaps` already includes chart-title and figure-alt guards and full-site page budgets. Each new candidate
needs a separate, reviewed change to `kpi.py` (or a test), a fresh baseline recorded here, and a target. Never add
one in the same pull request that improves it.

| Candidate | Why | How to count |
| --- | --- | --- |
| `layout_shift` | `images_without_size` is a proxy; this measures the effect | Playwright `PerformanceObserver('layout-shift')` on the five heaviest pages at 375 px; report the worst page |
| `largest_paint_ms` | Real speed, not only bytes | Playwright LCP on the home and projects index pages, median of 3 runs; report it, do not gate on it, because CI timing is noisy |
| `wip_pages_without_status` | Portfolio expansion adds WIP tracks; stale claims confuse visitors | Project pages whose front matter or body marks WIP but lack a visible status callout the audit already expects |

## Making the loop score experience (#126)

Landed 2026-11-12 in the experience-ledger tooling PR:

1. The primary metric name comes from the segment config; `polish_defects` is only the default (`scripts/hillclimb/ledger.py`).
2. `autoresearch.sh` runs `kpi.py` after the polish audit and prints both sets of `METRIC` lines.
3. Start the segment with `hc.sh segment "<name>" --metric experience_gaps --gate polish_defects=0`, then log the baseline on the same commit with `hc.sh baseline`. A run whose gate fails cannot be logged as keep.
4. Regression tests live in `tests/python/test_ledger.py`.

## Success points

- **Track 1 complete:** `experience_gaps` ≤ 5 (only the title decision left) and both lead screenshots in place.
- **Roadmap complete:** `experience_gaps` = 0, all judged indicators at target, all gates green on three browsers.
