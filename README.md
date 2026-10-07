# Jack J. Burleson — Resume

A single-page resume site built with [Quarto](https://quarto.org/) and served by GitHub Pages straight from `docs/` (no GitHub Actions).

## Edit

- `index.qmd` — resume content
- `styles.css` — look and feel (light/dark aware, print friendly)
- `assets/Jack_Burleson_Resume.pdf` — the PDF behind the "Download PDF" button

## Render and publish

```bash
quarto render        # writes the site to docs/
git add -A && git commit -m "Update resume" && git push
```

Rendered output in `docs/` is committed on purpose, because Pages serves it directly.

One-time setup: **Settings → Pages → Build and deployment → Source: Deploy from a branch → `main` / `/docs`**.
