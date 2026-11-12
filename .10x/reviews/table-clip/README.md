# Mailroom-ML appendix table clipping

The polish audit reported `polish_defects=8`, including four `crushed cell`
findings on `projects/mailroom-ml/appendix.html` at 375 and 414 px in both
themes: "clipped 2 lines | training/eval/eval_modernbert.py, --subset test
--sample 0".

## Cause

`scripts/filters/tables.lua` split long inline code at `/`, `-`, `_` and `.`.
The flags `--subset test --sample 0` became separate code fragments, and one
fragment ended in a preserved space. When that fragment started late on a
line, the chip's padding extended about 4 px past the table cell.

## Fix

- Skip splitting inline code that already contains spaces; spaces are natural
  break points, and fragmenting flags produced the overflow.
- Put the script path and flags in separate settings rows (`Reported by` and
  `Flags`) so each code span starts at the cell edge.

## Verification

- Audit before: `polish_defects=8`, four appendix `crushed cell` rows.
- Audit after: `polish_defects=0`, no appendix findings.
- `tests/python/test_tables.py` pins that code containing spaces stays one
  fragment; `tests/python/test_appendices.py` pins the separate rows.
- `bash autoresearch.checks.sh`: All checks passed, both Lua suites, 28 Node
  tests, 311 Python/browser tests and 691 subtests.
- Screenshots: `before-375-light.png`, `before-414-dark.png` from the failing
  build; `after-375-light.png`, `after-414-dark.png` from the fixed build.

No real-device or secondary-engine pass; the audit ran in Chromium at the
listed widths.
