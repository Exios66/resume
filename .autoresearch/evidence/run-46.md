# Evidence for run 46

- Commit: `6cb67bb experiment: Separate undergraduate credential from concentration and GPA` (parent `6e4102e`)
- Branch: `t3/resume-auto-research-loops`
- Date: 2026-11-08T08:59:21Z

## Source change (docs/ excluded)
```
 about.qmd                       |   4 +++-
 assets/Jack_Burleson_Resume.pdf | Bin 59596 -> 63091 bytes
 resume.qmd                      |   4 +++-
 3 files changed, 6 insertions(+), 2 deletions(-)
```

## Measurement
- Command: `scripts/hillclimb/hc.sh experiment` (runs `AUDIT_LIST=findings.tsv bash autoresearch.sh`)
- Best kept before this run: 4
- This run:
```
METRIC polish_defects=2 METRIC axe_points=0 METRIC layout_points=0 METRIC error_points=0 METRIC structure_points=0 METRIC lint_points=0 METRIC type_points=2 METRIC pages=43 METRIC css_kb=53.6 METRIC audit_s=48.5 METRIC render_s=19
non-zero: {'heading ends with a one-word line': 2}
```

## Findings delta against the best kept state
Removed (       2):
```
414	light	about.html	separator ends line	div.entry>div.degree>p | B.S., Psychology · Concentration: Neuroscience · GPA: 3.93
414	light	resume.html	separator ends line	div.entry>div.degree>p | B.S., Psychology · Concentration: Neuroscience · GPA: 3.93
```
Added (       0):
```
```

## Correctness checks
- Command: `bash autoresearch.checks.sh` on `6cb67bb`
```
chart unit tests passed
197 passed, 2 deselected, 611 subtests passed in 42.33s
All checks passed.
```

## Visual evidence
- [run-46-education-1280-dark.png](../screenshots/run-46-education-1280-dark.png)
- [run-46-education-1280-light.png](../screenshots/run-46-education-1280-light.png)
- [run-46-education-375-dark.png](../screenshots/run-46-education-375-dark.png)
- [run-46-education-375-light.png](../screenshots/run-46-education-375-light.png)
- [run-46-education-414-dark.png](../screenshots/run-46-education-414-dark.png)
- [run-46-education-414-light.png](../screenshots/run-46-education-414-light.png)
- [run-46-resume-1280-dark.png](../screenshots/run-46-resume-1280-dark.png)
- [run-46-resume-414-light.png](../screenshots/run-46-resume-414-light.png)

Reviewer notes: Opened eight screenshots: About at 375, 414, 1280 light/dark; resume at 414 light and 1280 dark. Credential and concentration/GPA form two clean paragraphs, surrounding entries remain readable, and no private data is visible. Browser confirmed both paragraphs at 414 without overflow. Delta removes precisely the two separator findings. Resume PDF regenerated; two-page print correctness passes in the browser suite.

## Not checked
- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);
  external links and live GitHub Pages deployment.
