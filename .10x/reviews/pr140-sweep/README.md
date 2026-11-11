# Sweep of the site at PR 140 (11 November 2026)

Method: every built page (43) was probed and screenshotted at 375 px and 1280 px in Chromium, with probe passes at 320 and 768 px, WebKit at 390 px and Firefox at 1280 px. The fixed audit scored 0 before and after.

## Fixed

| Defect | Where | Fix (all in `styles.css`) | Evidence |
| --- | --- | --- | --- |
| File paths in table cells read as separate words (`src/ mailroom_ ml/ config. py`) | every table with long code, all widths | split pieces join into one chip | `before-code-375-light.png`, `a-code-375-light.png`, `a-code-1280-dark.png` |
| Values touched or sat under the linked-row outline; the row label was not tinted | chart source tables on phones | even cell padding; label cell stays in flow unless the table scrolls | `before-src-375-light.png`, `a-src-375-light.png`, `a-src2-375-dark.png` |
| Chart labels drawn at twice body size | the two compact MapReduce charts on desktop | width capped at 400 px | `a-chart-1280-light.png` |
| Copy button covered the first line of code; its padding rule never applied | code blocks, mainly phones | selector now outranks the base rule; the button has its own row on phones | `a-copy-375-light.png` |
| Wrapped location and year lines were indented | About, Résumé and Research on phones | margin removed on phones | `a-about-375-light.png` |
| White frame around dark screenshots | JPEG figures in the dark theme | the light plate applies to non-JPEG figures only | `a-fig-375-dark.png` |

## Checks

- `bash autoresearch.sh`: `polish_defects=0`.
- `bash autoresearch.checks.sh`: 294 passed, 634 subtests passed. Four new browser tests cover the fixes; the first three failed against the previous stylesheet.

## Found, not changed

- Generated charts are 640 px wide, so on phones they open showing mostly the label column until scrolled (clearest on Langton's Ant). Chart changes need the owner's review (#124).
- Raster screenshots of desktop apps are hard to read at phone width (#119).
- The phone header takes three rows (#123).
- Wave Laboratory report writes subscripts as `H_s`, `ω_p`, `K_d`.

## Not checked

Real devices, screen readers, the live deployment and external links. Firefox and WebKit ran the probe passes and the gate's targeted cases only. The probes do not test interactions; those are covered by the gate's Chromium tests.
