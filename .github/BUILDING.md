# Building the site

Notes for working on the source of this portfolio. For the human side, see the [README](../README.md).

## Agent / fresh-clone setup

`bash scripts/setup-agent.sh` synchronizes the pinned Python dependencies in `.venv`, installs the same Node Playwright version in the ignored root `node_modules/`, verifies Chromium, Firefox and WebKit launches for both clients, installs Quarto 1.10.19 in `.autoresearch-tools/` when needed, and writes `.autoresearch-tools/env.sh`. Playwright browsers use the user cache by default (`~/Library/Caches/ms-playwright` on macOS, `~/.cache/ms-playwright` on Linux), outside the worktree; set `PLAYWRIGHT_BROWSERS_PATH` before setup and validation to use another cache. Local dependencies are excluded from Quarto rendering and published resources.

Source `. .autoresearch-tools/env.sh` before rendering or auditing, then run `scripts/hillclimb/hc.sh doctor` (`All tools present.`). Setup is idempotent, probes the default locale, and sets `LC_ALL=C` for deterministic byte-based Lua pattern matching. An explicit `QUARTO` override must also be version 1.10.19.

An interim portfolio site built with [Quarto](https://quarto.org/). GitHub Pages serves it straight from `docs/`, with no GitHub Actions. Live at <https://exios66.github.io/resume/>.

## Pages

| Source | Page |
| --- | --- |
| `index.qmd` | Home: intro, current work, featured projects |
| `about.qmd` | Background, skills, education, research training |
| `projects/index.qmd` | Project list, grouped by theme, with a diagram showing how the projects connect |
| `projects/<slug>.qmd` | One case study per project |
| `projects/<slug>/report.qmd` | Technical report: iteration history, metrics tables, figures, reproduction steps |
| `projects/<slug>/figures/` | Figures copied from each project repo; `MANIFEST.txt` records where each one came from |
| `research.qmd` | Cognitive neuroscience and graduate research |
| `writing/index.qmd` | Writing by the Hermes agent (Owlcot entries) |
| `resume.qmd` | Web résumé and print view; the downloadable PDF is a separately maintained owner export |

## How it fits together

- `_quarto.yml` holds site settings: URL, descriptions, Open Graph/Twitter cards, canonical links, sitemap.
- `scripts/site.lua` adds the header, `<main>` landmark, and footer to every page, with links that work from any folder depth. Each case study also gets schema.org `CreativeWork` data built from its own title, description and social image, so the markup cannot drift from the page. It also adds icons from an inline SVG sprite (shapes follow [Lucide](https://lucide.dev/), ISC license); every icon carries `width`/`height="1em"` so it stays small even if `styles.css` fails to load. (Quarto's own navbar needs a Bootstrap theme, which this site doesn't use.)
- `styles.css` holds the whole design: light/dark themes, mobile layout, print layout. The design layer at its end adds the background glow and dot grid, the hero constellation, gradient accents (`--accent` with `--accent-2`) and card hover effects; all of it is decorative and switched off in print and forced-colors mode. Fonts (Newsreader for the display headings, Inter for text and UI, JetBrains Mono for code) are self-hosted in `assets/fonts/`.
- `partials/` holds the head metadata (JSON-LD `Person` schema, theme bootstrapping), skip link, and the small theme-toggle script.
- `assets/js/site.js` is the only site script file: a hairline under the sticky header (wide screens only), a soft light that follows the pointer over cards (fine pointers only, decorative), a reading-progress bar on technical reports, and a fade-in for project cards below the fold. The fade is skipped on deep links, reloads and back/forward navigation, and all motion is off under `prefers-reduced-motion` and in print.
- `scripts/post-render.py` runs after every render. It recreates `docs/.nojekyll`, removes the repeated site name from page titles, adds a `?v=<hash>` to the `styles.css` and `site.js` links, and copies `assets/Jack_Burleson_Resume.pdf` to `docs/assets/` unchanged. That PDF is generated from `resume.html` by `scripts/make-resume-pdf.py` (Chromium print, two pages), so the web résumé and the download stay in step.
- `scripts/og-image.html` + `scripts/make-og.py` regenerate the social preview image `assets/og-image.png`.
- `scripts/charts.lua` turns a table wrapped in a `::: {.chart}` block into an inline SVG chart at render time, and keeps the table directly below it as the accessible source of every value. Kinds: `bars` (negative values and an optional `ref` line), `dumbbell` (`from` to `to`), `step` (log2 x-axis) and `strip` (one panel per row). Colors come from the `--chart-1`, `--chart-2` and `--chart-1-soft` tokens in `styles.css`, validated for colour-blind separation and contrast in both themes; `site.js` adds one hover and keyboard tooltip. Write units without a leading space (`unit="pts"`): Pandoc stops parsing a fenced div whose attribute starts with a space. Design and plan: `.github/specs/2026-11-07-interactive-charts-*.md`.
- `partials/diagrams/_*.qmd` are inline SVG architecture diagrams. Pages pull them in with `{{< include >}}`. They draw with `currentColor` and CSS classes, so they follow the light/dark theme. The leading underscore stops Quarto from rendering them as pages.
- `docs/` holds the built site. Do not edit it by hand.

## Adding a project

1. Write `projects/<slug>.qmd` (case study) and, if there is enough material, `projects/<slug>/report.qmd`. Copy the structure of an existing project: back link, `.project-nav`, `.stats` tiles, figures with `fig-alt`.
2. Copy figures into `projects/<slug>/figures/` and add a line to its `MANIFEST.txt` naming the source file.
3. Check every number against the source repo before publishing. HTML comments are removed from the rendered pages, but they stay visible in this public source, so don't use them for private notes.
4. Add a card to `projects/index.qmd`, and to `index.qmd` if the project should be featured.
5. To chart a table, wrap it: `::: {.chart kind="bars" title="…" label="<category column>" value="<number column>"}` … `:::`. Column names match the header text exactly; a missing column, a cell without a number or a one-row table stops the render with an error naming the page. `lua tests/test_charts.lua` and `tests/test_charts.py` cover the renderer and the published charts.

## Update the site

Set up the test environment (Python 3.13 is known to work):

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m playwright install chromium firefox webkit
```

Then:

1. Edit the `.qmd` files.
2. To change the downloadable résumé, edit `resume.qmd`, run `quarto render resume.qmd`, then `python scripts/make-resume-pdf.py` to rewrite `assets/Jack_Burleson_Resume.pdf`.
3. Run `quarto render`. This rebuilds `docs/` and copies the PDF into it.
4. Commit and push, including `docs/`.

Use `quarto preview` while writing. The header and footer appear there too.

Run the checks with `lua tests/test_site.lua`, `lua tests/test_charts.lua`, `node --test tests/theme.test.cjs tests/icons.test.cjs`, and `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests`. `tests/icons.test.cjs` reads the rendered `docs/` and checks that every icon sizes itself and the stylesheet and script links are cache-busted. `tests/test_links.py` checks the rendered `docs/` for broken internal links, images without alt text, and strings that must never be published. `tests/test_structured_data.py` parses the JSON-LD on every page. `tests/test_page_budget.py` fails when a page type or a shared asset grows past its recorded budget in `.10x/metrics.md`.

For real-browser regression checks alone, run `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/test_browser.py`. The test serves `docs/` under a subpath and checks every page in both themes at 320, 375, 768 and 1280 px, plus project navigation, keyboard access, diagram text bounds, image loading, no-JavaScript access and two-page résumé printing. The same suite runs the mobile chart checks in Chromium, Firefox and WebKit. Without the environment flag, these browser checks are explicitly skipped. Capture screenshots or a recording for visual changes and report coverage limits as described in `AGENTS.md`.

Project navigation links only to resources that actually exist: a local case study, a local report when available, a public Code repository, and a verified Live link. An upstream report can be linked directly (MapReduce); no placeholder reports or private repository links are added. Search remains off in this pass: category shortcuts improve the current index without adding another script or generated search index. Search, report TOCs and prev/next navigation remain separate backlog work, not completed features.

To refresh the social image after changing the tagline, run `python scripts/make-og.py` (needs `pip install playwright` and `playwright install chromium`).

## Things to fill in

Some pages have TODO comments (invisible on the site) marking missing results, figures, and repo links. Search with `grep -rn TODO projects research.qmd`.

## Publish

Do this once: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs`**.

If you move to a custom domain, change `site-url` in `_quarto.yml`, the URL in `partials/head.html`, and the text in `scripts/og-image.html`.
