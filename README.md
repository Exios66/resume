# Jack J. Burleson — Resume

A one-page resume site built with [Quarto](https://quarto.org/). GitHub Pages serves it straight from `docs/`, with no GitHub Actions.

## Files

- `index.qmd` holds the resume text.
- `styles.css` holds the look: light and dark themes, phone layout, print layout.
- `assets/Jack_Burleson_Resume.pdf` is the file behind the "Download PDF" button.
- `docs/` holds the built site. Do not edit it by hand.

## Update the site

1. Edit `index.qmd`.
2. Run `quarto render`. This rebuilds `docs/`.
3. Commit and push, including `docs/`.

If you change the resume text, also replace the PDF in `assets/` so the download matches the page.

## Publish

Do this once: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs`**.
