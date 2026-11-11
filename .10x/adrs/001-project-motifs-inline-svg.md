# ADR-001: Project motifs as inline SVG injected by the site filter

**Status:** Accepted
**Date:** 2026-11-10
**Feature:** portfolio-experience-v2
**Author:** 10x-Team (Architect + Staff Engineer)

## Context
Project cards are text only. Only 2 of 14 projects have a product screenshot. The site has two themes, a print
layout and no build step beyond Quarto.

## Decision
Each project gets a hand-drawn SVG motif in `partials/covers/<slug>.svg`. A card opts in with a `cover` attribute and
`scripts/filters/site.lua` inlines the SVG, marked decorative, as the first block of the card. Motifs draw with
`currentColor` and shared classes so the stylesheet controls their colour in both themes.

## Alternatives Considered
| Alternative | Pros | Cons | Why Not |
|-------------|------|------|---------|
| Screenshot thumbnails | Shows the real product | Most projects have none; adds requests and weight; needs light and dark variants | Inconsistent and heavy |
| `<img src="cover.svg">` | Cacheable, simple markup | Cannot inherit theme colours; one request per card | Breaks dark mode |
| Quarto include shortcode in each card | No filter change | Verbose in every card; no validation of the slug | Easy to get wrong silently |

## Consequences
### Positive
- Consistent cards, theme-aware, no extra requests, works without JavaScript.
### Negative
- Inline SVG repeats in the HTML of each page that shows the card (about 1 KB each after compression).
- Motifs must be drawn and kept in one style by hand.
### Risks
- A motif could be read as data. Mitigation: motifs picture the subject, carry no numbers or axes, and are hidden from assistive technology.

## Dependencies
- Depends on the `Div` handler in `scripts/filters/site.lua`. Social cards (later) will reuse the same files.
