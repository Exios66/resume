# Architect index
[DISCOVERED]
- Pandoc Lua filters build the chrome and visuals at render time: `scripts/filters/site.lua` (header, main, footer, icons), `scripts/filters/charts.lua` (table to inline SVG chart; table kept as source), `scripts/filters/tables.lua` (post-render table handling).
- `scripts/build/post-render.py`: cache-busting, title cleanup, PDF copy. `partials/`: head metadata, JSON-LD Person, theme bootstrap, inline SVG diagrams.
- Page types: home, about, research, writing, resume, search, projects index, 14 case studies, technical reports and appendices (43+ built pages).
- Motion today: card reveal on scroll, pointer light on cards, reading-progress bar on reports, button and icon hovers. All gated on `prefers-reduced-motion`, off in print and forced colors.
- One site-wide Open Graph image; no per-page cards. No images on the home or projects index.
Active features: portfolio-experience-v2.
