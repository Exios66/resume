# Architect: portfolio-experience-v2
See ADR-001. Motifs are files in `partials/covers/<slug>.svg`. A card opts in with `cover="<slug>"`. `scripts/filters/site.lua` inlines the file as the card's first block inside `<div class="card-cover" aria-hidden="true">`. Styling lives in `styles.css` under a 'Project covers' section. Failure: unknown slug stops the render.
