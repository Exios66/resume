# Building the site

Notes for working on the source of this portfolio. For the human side, see the [README](../README.md).

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
| `writing/index.qmd` | Blog stub ("coming soon") |
| `resume.qmd` | Two-page résumé, also the source of the PDF |

## How it fits together

- `_quarto.yml` holds site settings: URL, descriptions, Open Graph/Twitter cards, canonical links, sitemap.
- `scripts/site.lua` adds the header, `<main>` landmark, and footer to every page, with links that work from any folder depth. It also adds icons from an inline SVG sprite (shapes follow [Lucide](https://lucide.dev/), ISC license); every icon carries `width`/`height="1em"` so it stays small even if `styles.css` fails to load. (Quarto's own navbar needs a Bootstrap theme, which this site doesn't use.)
- `styles.css` holds the whole design: light/dark themes, mobile layout, print layout. Fonts (Newsreader for the display headings, Inter for text and UI, JetBrains Mono for code) are self-hosted in `assets/fonts/`.
- `partials/` holds the head metadata (JSON-LD `Person` schema, theme bootstrapping), skip link, and the small theme-toggle script.
- `scripts/post-render.py` runs after every render. It recreates `docs/.nojekyll`, removes the repeated site name from page titles, adds a `?v=<hash>` to the `styles.css` links, and prints `resume.html` to `assets/Jack_Burleson_Resume.pdf`. The PDF is refreshed only when that step succeeds; without Playwright or Chromium the committed PDF is kept, so re-check it after editing the résumé.
- `scripts/og-image.html` + `scripts/make-og.py` regenerate the social preview image `assets/og-image.png`.
- `partials/diagrams/_*.qmd` are inline SVG architecture diagrams. Pages pull them in with `{{< include >}}`. They draw with `currentColor` and CSS classes, so they follow the light/dark theme. The leading underscore stops Quarto from rendering them as pages.
- `docs/` holds the built site. Do not edit it by hand.

## Adding a project

1. Write `projects/<slug>.qmd` (case study) and, if there is enough material, `projects/<slug>/report.qmd`. Copy the structure of an existing project: back link, `.project-nav`, `.stats` tiles, figures with `fig-alt`.
2. Copy figures into `projects/<slug>/figures/` and add a line to its `MANIFEST.txt` naming the source file.
3. Check every number against the source repo before publishing. HTML comments are removed from the rendered pages, but they stay visible in this public source, so don't use them for private notes.
4. Add a card to `projects/index.qmd`, and to `index.qmd` if the project should be featured.

## Update the site

One-time setup for the PDF step (skip it and the render still works; the existing PDF is kept):

```sh
pip install playwright
playwright install chromium
```

Then:

1. Edit the `.qmd` files.
2. Run `quarto render`. This rebuilds `docs/` and the PDF.
3. Commit and push, including `docs/` and the refreshed `assets/Jack_Burleson_Resume.pdf`.

Use `quarto preview` while writing. The header and footer appear there too, but the PDF is only rebuilt by `quarto render`.

Run the checks with `lua tests/test_site.lua`, `node --test tests/theme.test.cjs tests/icons.test.cjs`, and `python -m pytest tests`. `tests/icons.test.cjs` reads the rendered `docs/` and checks that every icon sizes itself and the stylesheet link is cache-busted. `tests/test_links.py` checks the rendered `docs/` for broken internal links, images without alt text, and strings that must never be published.

To refresh the social image after changing the tagline, run `python scripts/make-og.py`.

## Things to fill in

Some pages have TODO comments (invisible on the site) marking missing results, figures, and repo links. Search with `grep -rn TODO projects research.qmd`.

## Publish

Do this once: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs`**.

If you move to a custom domain, change `site-url` in `_quarto.yml`, the URL in `partials/head.html`, and the text in `scripts/og-image.html`.
