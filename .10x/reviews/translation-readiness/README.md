# Translation readiness: evidence

The site has one English source. Readers can translate it in their browser (Chrome, Edge, Safari)
or with Google Translate. These screenshots show the built site (`docs/`), served locally, after
**simulated** in-place translation by `tests/browser/pseudo_translate.js` in Chromium. The
simulation does what those translators do: it replaces each text node in place, skips anything
under `translate="no"`, and tags the root element with `lang` and Chrome's
`translated-ltr`/`translated-rtl` class. The navigation, Search and Copy labels use real
translations. Other words are deterministic pseudo-text with each language's shape: German runs
about 35% longer and forms compounds, French and Spanish run 20–25% longer, Chinese is half as
long with no spaces, and Arabic runs right to left. The screenshots contain only public site
content.

| File | What it shows |
| --- | --- |
| `{de,fr,ar}-320-before.png` | `main` before the change, translated at 320 px. The title runs under Search and the theme toggle, the nav row overflows, and the project title (`MapReduce-Reloaded`) is translated. |
| `{de,fr,ar}-320-after.png` | This branch at 320 px. The header keeps 44 px targets with no overlap, the project name stays as written, and Arabic text is right to left and right-aligned. |
| `{de,zh,ar}-375-index.png`, `de-1280-index.png` | This branch: the home page, from the final sweep (`--shots`). |
| `{de,ar}-375-projects_mapreduce-reloaded.png`, `ar-1280-projects_mapreduce-reloaded.png` | This branch: the MapReduce-Reloaded case study, Arabic full page on desktop. |
| `zh-375-projects_mailroom-ml_report.png` | This branch: the Mailroom-ML report in Chinese at phone width. |

The 320 px pairs are the MapReduce-Reloaded page at a 320×640 viewport and device scale 2. The
"before" images come from a build of `main`. The 375 and 1280 images are 1× sweep captures; the
1280 ones are full page.

## Commands and results

```sh
. .autoresearch-tools/env.sh
node scripts/hillclimb/translation-sweep.cjs        # all 43 pages, de/fr/es/zh/ar, 320/375/1280
SWEEP_DOCS=<main build> node scripts/hillclimb/translation-sweep.cjs --engines chromium
bash autoresearch.sh && bash autoresearch.checks.sh
python3 scripts/hillclimb/kpi.py
```

- Sweep on this branch: Chromium 645 views, 0 with problems. Firefox 645/0. WebKit 645/0.
- Sweep on `main` (Chromium only): 504 of 645 views had problems, including 173 with sideways page overflow, 258 where the title overlapped a header control, and 209 where a project title was translated.
- Audit: `polish_defects=0`, with 0 axe, layout and error points, across 43 pages.
- The full gate includes `test_translated_pages_keep_layout_names_and_code`: Chromium, Firefox and WebKit; de/ar/zh; 320 and 1280 px; 4 pages.

## Not checked

- The real Chrome, Edge, Safari and Google Translate translators. Every check used the simulation above.
- `alt` and `aria-label` text, including names inside them. Translators can translate it, and no markup prevents that.
- Chart SVG labels. They are marked `translate="no"` and stay English. Each chart's data table translates.
- The chart tooltip. It is written by script and relies on the translator picking up dynamic text.
- Site search. It still queries the English index.
- Arabic alignment in Firefox and Safari. Their translators may not set the root `lang` or class, so pages can stay left-aligned there.
- Real devices and screen readers.
- Common technical terms in prose, such as "MapReduce" on its own, which can translate. Only the names in `PROTECTED_NAMES` in `scripts/build/post-render.py` are protected, along with code and drawn text.
