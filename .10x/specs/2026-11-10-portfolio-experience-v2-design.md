# Portfolio experience v2: design

Date: 2026-11-10. Baseline: `main` at `5d622fe`. Status: approved by the owner on 2026-11-10, with the instruction that the work is design-led and not limited to the measured polish loop.

## Goal

Make the portfolio look and feel like finished professional work in every area: display, motion, navigation,
features, visualisations and content. Build on what exists. Do not replace the stack, the palette or the type.

## Approach chosen by the owner

A tracked roadmap. Five tracks, each shipped as one or more small pull requests. Track 1 goes first.

| Track | Subject | Order |
| --- | --- | --- |
| 1 | Visual identity and imagery | first (specified in full below) |
| 2 | Motion | second |
| 3 | Navigation and features | third |
| 4 | Visualisations | fourth |
| 5 | Content and reach | runs alongside, when the owner supplies facts |

## Rules for every track

1. The site stays static: Quarto, one stylesheet, one script, no framework, no build step beyond the render.
2. Every page works with JavaScript off. Scripts only enhance.
3. All motion is off under `prefers-reduced-motion`, in print and in forced-colors mode.
4. Decoration never carries information. Decorative images are hidden from assistive technology.
5. No new claims or numbers. Images of results come only from figures already in the repository.
6. `docs/` is rendered, never edited by hand.
7. Each pull request includes: the commands run and their results, screenshots at 375, 768 and 1280 px in light and
   dark, and a list of what was not checked. Screenshots stay outside `docs/`.
8. The work is design-led. The polish audit is a safety net, not the driver: new features, imagery and motion do
   not need to move its score, and a finding caused by a deliberate design choice is recorded and judged, not
   automatically reverted. `bash autoresearch.checks.sh` must still pass, with tests updated where behaviour
   changes on purpose.
9. Commits, pull requests and issues use the owner's git identity and carry no tool footers or session links.

## Track 1: visual identity and imagery

### Problem

The home page and the projects index show text only. Fourteen projects look alike at a glance. Every shared link
shows the same preview image. Case-study images load eagerly. Some layout details are uneven.

### Options considered

| Option | For | Against |
| --- | --- | --- |
| A. Screenshots on every card | Shows the real product | Only 2 of 14 projects have a product screenshot; the rest would be chart crops that read badly at card size. Adds image weight to the two busiest pages. |
| B. A drawn motif per project (inline SVG) | One consistent look. Follows light and dark themes. No image requests. Works for back-end projects that have nothing to photograph. | Abstract; does not show the real interface. |
| C. Motifs on all cards, plus real screenshots where they exist (chosen) | Consistent cards, and the two visual projects still show the real thing where there is room for it | Two systems to maintain |

### What gets built

**1. Project motifs.** One small inline SVG per project in `partials/covers/<slug>.svg`, drawn with `currentColor`
and the existing accent tokens so it follows the theme. Each motif pictures the project's subject, not a result:
a wave spectrum for Wave Laboratory, a neuron grid for Neuron Atlas, an ant trail for Langton's Ant, a fan-out and
fan-in for MapReduce-Reloaded, a page with a routing fork for the mailroom projects, and so on. All 14 share one
grid, stroke width and corner radius.

**2. Cards with covers.** A card opts in with an attribute: `::: {.card cover="wave-laboratory"}`. `scripts/site.lua`
reads the SVG and places it at the top of the card with `aria-hidden="true"`. A missing file fails the render with
a clear message. On the projects index the motif sits beside the text on wide screens and above it on phones. On
the home page the four featured cards show it as a band across the top.

**3. Real media where it exists.** The Wave Laboratory and Neuron Atlas case studies get a lead image under the
title, taken from the screenshots already in `projects/<slug>/figures/`. No new captures are invented; if a better
capture is wanted, the owner supplies it.

**4. A social card per project.** `scripts/make-og.py` gains a mode that renders `assets/og/<slug>.png`
(1200 × 630) from the project title, its kicker line and its motif, using the existing `og-image.html` layout.
Each case study, report and appendix sets `image:` in its front matter. Other pages keep the site card.

**5. Image loading.** `scripts/site.lua` adds `loading="lazy"`, `decoding="async"` and intrinsic `width` and
`height` to content images, except the first image on a page. This removes layout shift and defers about 370 KB on
the Wave Laboratory page.

**6. Layout corrections.**
- At-a-glance tiles: values align on one baseline row and labels start on a common line, so tiles of unequal text
  length no longer look ragged.
- The "Launch the lab" and "Open the atlas" buttons align left with the rest of the page.
- The home "Explore" list becomes four link tiles with the existing icons.
- The footer grows from one line to three short groups: pages, contact, and "last updated" with the build note.

**7. Portrait (optional).** If the owner supplies a photo, the About page shows it beside the opening paragraph.
Nothing is added without one.

### Data flow

```
partials/covers/<slug>.svg --+--> site.lua (card cover, inline)      --> docs/*.html
                             +--> make-og.py (Chromium screenshot)   --> assets/og/<slug>.png --> front matter image:
projects/<slug>/figures/*  ----> site.lua (lazy, sized)              --> docs/projects/...
```

### Failure handling

- Unknown `cover` slug: the render stops and names the card and the missing file.
- A motif with fixed colours instead of tokens: a unit test rejects it, because it would break one theme.
- Social card generation needs Chromium. If it is absent the script says so and exits non-zero; it never writes a
  blank image.
- No JavaScript, print, forced colors: motifs are static SVG and need none of these. In print they are hidden to
  save ink.

### Tests

- Lua unit tests for cover injection, the missing-file error, and the image attributes.
- A Python test that every project page has a motif file, a social card of 1200 × 630, and an `og:image` pointing
  at it.
- Browser tests: no layout shift from images on the two media pages; cards keep one link per card and their focus
  ring; no horizontal scroll at 375 px.
- The fixed audit and the full check suite, before and after.

### Budget and acceptance

- Home page transfer grows by no more than 30 KB; projects index by no more than 40 KB.
- No new console errors and no loss of text contrast. Any new audit finding is listed in the pull request with
  the reason it was accepted or fixed.
- The owner approves the motif style on three samples before the other eleven are drawn.

### Delivery

Three pull requests: (a) motif system and three sample motifs on the home page, for style approval; (b) the
remaining motifs, index layout and layout corrections; (c) social cards and image loading.

## Later tracks (outline; each gets its own design section before work starts)

**Track 2, motion.** Cross-page view transitions with a shared title element. A slow drift on the hero
constellation. Charts draw in when they enter the view. Stat values count up once. Theme change cross-fades.
One motion scale (durations and easing) as tokens.

**Track 3, navigation and features.** A single-row phone header. An "on this page" rail on long case studies.
Category chips and an optional project filter that works without JavaScript. A keyboard shortcut for search.
Previous and next links with motifs.

**Track 4, visualisations.** An interactive version of the project-connection diagram. A skills view tied to the
projects that use each skill. Chart legends that toggle series. Contrast checks for SVG text in both themes.

**Track 5, content and reach.** Issues 71, 76, 84 and 112 to 115. Fuller Research and Writing pages. Structured
data for each project. A performance budget, and checks in Firefox and WebKit once they are installed.

## Out of scope

A new framework, a new palette or typeface, analytics, a contact form, and any content the owner has not supplied.
