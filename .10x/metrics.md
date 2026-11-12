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
| Case study | `projects/mapreduce-reloaded.html` | 19,433 | 20,000 |
| Technical report | `projects/natd/report.html` | 19,345 | 22,000 |
| Appendix | `projects/mailroom-ml/appendix.html` | 11,018 | 13,000 |
| Other page | `resume.html` | 12,099 | 15,000 |
| Shared stylesheet | `styles.css` | 14,935 | 20,000 |
| Shared script | `assets/js/site.js` | 5,683 | 9,000 |

The case-study budget was raised from 19,000 on 12 November 2026. The update to its heaviest page (#142) had
brought it to 18,988 bytes. Phone-width chart drawings then added 1,407 bytes, and pruning unused icons from each page's
sprite saved 948, for 19,433. The other budgets are unchanged; every page type got lighter from the sprite pruning.

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

## How to raise each metric

Measured on `main` at d11a820 (11 November 2026): `experience_gaps` = **125**, unchanged since the baseline.
The levers below are ordered by gaps closed per pull request. Re-run `kpi.py` before starting; these counts drift.

### 1. `images_without_size` (61) and `later_images_not_lazy` (45): one filter change, up to 106 gaps

- **Where they come from.** All 61 unsized images are project figures written as
  `![…](figures/x.jpg){.fig fig-alt="…" width="100%"}` (39 JPEG, 21 SVG, 1 PNG). Quarto turns `width="100%"` into
  `style="width:100.0%"`, so no `width`/`height` attributes reach the HTML. Check the count with
  `grep -rn 'width="100%"' projects --include=*.qmd | wc -l`. It should match `images_without_size`.
- **Heaviest pages:** `projects/rvl-cdip-classifier/report.html` (9 images), `projects/wave-laboratory/report.html` (9),
  `projects/wave-laboratory.html` (6), `projects/mailroom-ml/report.html` (6),
  `projects/psychometric-digital-twin/report.html` (5).
- **Lever (#119):** add an `Image` handler to `scripts/filters/site.lua`. It reads each file's intrinsic size: the JPEG
  SOF marker, the PNG IHDR chunk, or the SVG `viewBox`/`width`/`height`. It replaces the percentage width with
  `width` and `height` attributes, and sets `loading="lazy" decoding="async"` on every image after the first in `<main>`.
  `styles.css` already forces `width: 100%; height: auto` on `.page img.fig`, so the attributes reserve the aspect
  ratio without changing the layout. Check that claim with before and after screenshots at 375 and 1280 px.
- **Do not game it.** The sizes must be the file's real pixels or viewBox, never constants. Keep the first figure of each
  page eager, because it is often the largest paint. Add a Lua test in `tests/lua/test_site.lua` for each format, and
  a case for a missing or unreadable file, which must leave the image unchanged rather than fail the render.

### 2. `projects_without_own_social_card` (14): one card per project

- **Where they come from.** Every project page inherits the site-wide `open-graph.image` in `_quarto.yml`
  (`assets/og-image.png`). `kpi.py` counts a project as covered only when its slug appears in its own `og:image` URL.
- **Lever (#120):** make a 1200 × 630 PNG per project from the project's existing cover motif in `partials/covers/`.
  Use the real title and no invented imagery. Name it after the slug, for example
  `assets/social/wave-laboratory.png`, and set `image:` in that project's front matter to the absolute URL
  (`https://exios66.github.io/resume/assets/social/wave-laboratory.png`). `project_schema` in `site.lua` accepts only
  `http(s)` images and falls back to the site-wide image for a relative path, so a relative value would leave the
  JSON-LD on the generic card. Script the generator so that a new project gets a card from the same command. Check one page's `og:image` and `twitter:image` in the built HTML.

### 3. `repo_style_titles` (5): owner decision first

- The five cards are Digital-Mailroom, Mailroom-ML, RVL-CDIP-Classifier, Mailroom-Corpus-EDA and MapReduce-Reloaded.
- **Lever (#121):** ask the owner for the display titles. Do not write them yourself (rule 4 below). Once given, change
  only the card and page titles and keep the repository names in links and code.

### Headroom to protect while doing the above

| Number | 10 Nov | 11 Nov | Limit | Note |
| --- | ---: | ---: | ---: | --- |
| `gz_projects_index` | 23,702 | 24,520 | 26,000 | 94% used; the tightest budget. A new card or longer card text can break it |
| `gz_index` | 14,127 | 14,815 | 16,000 | 93% used |
| `gz_site_js` | 5,683 | 6,643 | 9,000 | Up 17% in a day; check that new script code earns its weight |
| `gz_styles_css` | 14,935 | 15,152 | 20,000 | |

## Metrics worth adding next

`experience_gaps` does not yet measure these. Each needs a separate, reviewed change to `kpi.py`
(or a test), a fresh baseline recorded here, and a target. Never add one in the same pull request that improves it.

| Candidate | Why | How to count |
| --- | --- | --- |
| `charts_without_title` | #139 gave every chart a title; a guard keeps it that way | In built HTML, `figure.chart` elements whose `figcaption.chart-title` is missing or empty (the source `title` attribute becomes that caption), plus hand-drawn figure SVGs with no visible title |
| `figures_without_alt` | Alt text is part of the experience, and the polish audit checks presence, not substance | `<img>` in `<main>` with an empty `alt` or one that repeats the caption |
| `layout_shift` | `images_without_size` is a proxy; this measures the effect | Playwright `PerformanceObserver('layout-shift')` on the five heaviest pages at 375 px; report the worst page |
| `largest_paint_ms` | Real speed, not only bytes | Playwright LCP on the home and projects index pages, median of 3 runs; report it, do not gate on it, because CI timing is noisy |

## Making the loop score experience (#126)

The ledger still scores only `polish_defects`. To let a hill-climb keep a change because `experience_gaps` fell:

1. Take the primary metric name from the segment config in `scripts/hillclimb/ledger.py`. Do not hard-code it.
2. Have `autoresearch.sh` (or `hc.sh experiment`) run `kpi.py` after the polish audit and print both sets of `METRIC` lines.
3. Start a new segment with `experience_gaps` as primary, `polish_defects` = 0 as a gate, and a baseline measured on the same commit.
4. Do this in its own pull request, with tests for the ledger change, before any experiment uses it.

## Success points

- **Track 1 complete:** `experience_gaps` ≤ 5 (only the title decision left) and both lead screenshots in place.
- **Roadmap complete:** `experience_gaps` = 0, all judged indicators at target, all gates green on three browsers.
