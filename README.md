# Jack J. Burleson — Portfolio & Résumé

An interim portfolio site built with [Quarto](https://quarto.org/). GitHub Pages serves it straight from `docs/`, with no GitHub Actions. Live at <https://exios66.github.io/resume/>.

## Pages

| Source | Page |
| --- | --- |
| `index.qmd` | Home: intro, current work, featured projects |
| `about.qmd` | Background, skills, education, research training |
| `projects/index.qmd` + `projects/*.qmd` | Project list and one case study per project |
| `research.qmd` | Cognitive neuroscience and graduate research |
| `writing/index.qmd` | Blog stub ("coming soon") |
| `resume.qmd` | Two-page résumé, also the source of the PDF |

## How it fits together

- `_quarto.yml` holds site settings: URL, descriptions, Open Graph/Twitter cards, canonical links, sitemap.
- `scripts/site.lua` adds the header, `<main>` landmark, and footer to every page, with links that work from any folder depth. (Quarto's own navbar needs a Bootstrap theme, which this site doesn't use.)
- `styles.css` holds the whole design: light/dark themes, mobile layout, print layout. Fonts (Inter, Source Serif 4) are self-hosted in `assets/fonts/`.
- `partials/` holds the head metadata (JSON-LD `Person` schema, theme bootstrapping), skip link, and the small theme-toggle script.
- `scripts/post-render.py` runs after every render. It recreates `docs/.nojekyll` and prints `resume.html` to `assets/Jack_Burleson_Resume.pdf`, so the download always matches the page.
- `scripts/og-image.html` + `scripts/make-og.py` regenerate the social preview image `assets/og-image.png`.
- `docs/` holds the built site. Do not edit it by hand.

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

To refresh the social image after changing the tagline, run `python scripts/make-og.py`.

## Things to fill in

Each case study has `<!-- TODO: ... -->` comments (invisible on the site) marking missing results, figures, and repo links. Search with `grep -rn TODO projects research.qmd`.

## Publish

Do this once: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs`**.

If you move to a custom domain, change `site-url` in `_quarto.yml`, the URL in `partials/head.html`, and the text in `scripts/og-image.html`.
