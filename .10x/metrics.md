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
| Page weight | `kpi.py` | `pages_over_budget` = 0 (home HTML ≤ 16,000 gzip bytes; projects index ≤ 26,000) |

Never edit the audit, the checks or `kpi.py` to rescue a result. Change them only in a separate pull request that says why.

## Primary metric for the experience loop: `experience_gaps` (lower is better, target 0)

It is the sum of the counts below. Baseline measured on `main` after pull request #116, 10 November 2026: **125**.

| Part | Baseline | Target | Closed by |
| --- | --- | --- | --- |
| `cards_without_cover` | 0 | 0 | done (#116); guards against regressions |
| `repo_style_titles` (card titles that are hyphenated repository names) | 5 | 0 | #121; needs the owner's titles first |
| `projects_without_own_social_card` | 14 | 0 | #120 |
| `projects_without_structured_data` | 0 | 0 | guard |
| `images_without_size` (no `width` and `height`) | 61 | 0 | #119 |
| `later_images_not_lazy` (not the first image on a page, and not `loading="lazy"`) | 45 | 0 | #119 |
| `pages_over_budget` | 0 | 0 | gate |

Secondary numbers, reported but not summed: `gz_index` 14,127; `gz_projects_index` 23,702; `gz_styles_css` 14,935;
`gz_site_js` 5,683 (gzip bytes). Watch them for sudden growth. Soft limits: CSS 20,000; JavaScript 9,000.

## Page transfer budgets

Recorded on 10 November 2026 against the same render as the baseline above. Sizes are gzipped HTML bytes at
compression level 9; the shared stylesheet and script are measured separately because every page pays for them.
`tests/python/test_page_budget.py` checks every built page, not only the example named here, and fails with the page path,
its size and its budget.

| Page type | Heaviest page at baseline | Measured | Budget |
| --- | --- | ---: | ---: |
| Home | `index.html` | 14,127 | 16,000 |
| Projects index | `projects/index.html` | 23,702 | 26,000 |
| Case study | `projects/mapreduce-reloaded.html` | 16,028 | 19,000 |
| Technical report | `projects/natd/report.html` | 19,345 | 22,000 |
| Appendix | `projects/mailroom-ml/appendix.html` | 11,018 | 13,000 |
| Other page | `resume.html` | 12,099 | 15,000 |
| Shared stylesheet | `styles.css` | 14,935 | 20,000 |
| Shared script | `assets/js/site.js` | 5,683 | 9,000 |

Page budgets leave roughly 10–24 percent headroom over their baselines; shared CSS and JavaScript budgets allow roughly 34 and 58 percent, respectively. Raising one is a deliberate decision that belongs in
the pull request, with the reason and the new measurement.

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
5. Report `experience_gaps` separately after each render. The current `ledger.py` hardcodes `polish_defects`, and `autoresearch.sh` does not append KPI output. Do not change a segment name/config and claim the loop scores experience. Experience-scored logging needs a separately reviewed tooling change and new baseline (#126); meanwhile retain ordinary scoped PR evidence and honest polish records.

## Success points

- **Track 1 complete:** `experience_gaps` ≤ 5 (only the title decision left) and both lead screenshots in place.
- **Roadmap complete:** `experience_gaps` = 0, all judged indicators at target, all gates green on three browsers.
