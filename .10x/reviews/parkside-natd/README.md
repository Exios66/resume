# NATD / Parkside related assessment links

Adds the two hosted assessment tools requested by the owner to the Parkside
research context:

- `https://exios66.github.io/dark-triad-assessments/` — Dark Triad personality
  inventories (SDT3, Dirty Dozen, SDT4, MACH IV, HEXACO, OCEAN).
- `https://exios66.github.io/Intro-Knowledge-Quiz/` — a 15-question knowledge
  quiz across subjects.

## Placement

- `research.qmd`: a nested "Related assessment tools" bullet under the NATD
  pilot-study bullet in the Cognitive Neuroscience Lab, UW–Parkside section.
- `projects/natd.qmd`: a short "Related assessment tools" section before
  "Methods and tools".

The copy describes each tool from its published page. It does not claim either
instrument was used in the nine-participant pilot; the owner can add that
provenance if it applies.

## Verification

- Both destinations fetched: titles and descriptions match the copy.
- `tests/python/test_natd.py`, `test_links.py`, `test_site_integrity.py`,
  `test_resume_content.py`: 46 passed, 228 subtests.
- `RUN_BROWSER_TESTS=1 ... -k "research or natd"`: 5 passed.
- `bash autoresearch.checks.sh`: All checks passed, both Lua suites, 28 Node
  tests, 313 Python/browser tests and 691 subtests.
- Page sizes remain within budget: Research 10,125 gzip bytes (15,000 limit);
  NATD 12,679 (19,000 limit).

Screenshots: `research-parkside-1280-light.png`,
`research-parkside-375-dark.png`, and `natd-related-1280-light.png`. No real
device or secondary-engine page pass; browser assertions are Chromium-only for
these pages.
