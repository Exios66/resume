# Print navigation verification — PR109

Candidate ab26129 on main merge 8d430f2. One source selector in styles.css extends the later print rule to .project-pager and .search-suggest; Quarto generated docs/styles.css. Later display:flex declarations had overridden the earlier print-hide policy. Screen rendering and content are unchanged.

## Fixed evaluation and results

The audit extension f7d8498 initially miscounted two valid semantic headings: segment 11/run 60 scored 38. Before any product edit, d3305c3 recognized role=heading/aria-level=1 and started segment 12. Baseline run 61 scored 36, with 233 tests/611 subtests passing in 75.10s. These two false positives were not site defects or claimed improvements.

With the audit then fixed, run 62 scores 0:35 project pagers and 1 search-suggestion container removed from print; no added findings. All 43 primary titles remain visible. Other buckets remain 0. Audit 49.1s, render 21s. Full correctness gate on ab26129: 233 passed, 2 deselected, 611 subtests in 78.44s; All checks passed.

## Commands

Environment prepared with bash scripts/setup-agent.sh; source .autoresearch-tools/env.sh before render/audit; scripts/hillclimb/hc.sh doctor ended All tools present.

```sh
. .autoresearch-tools/env.sh
scripts/hillclimb/hc.sh baseline
scripts/hillclimb/hc.sh checks
scripts/hillclimb/hc.sh experiment 'Keep screen navigation out of printed reading surfaces' styles.css
scripts/hillclimb/hc.sh checks
python3 -m http.server 8769 --bind 127.0.0.1 --directory docs
.venv/bin/python .autoresearch/print-capture-workflow.py before
.venv/bin/python .autoresearch/print-capture-workflow.py after
```

Capture phases were run against the corresponding baseline/candidate builds, not sequentially against the same build. The scratch capture script was archived after use. It asserts navigation visibility/primary heading visibility, applies Chromium CSS print media and saves actual viewport images. Raw results: print-before-observations.json and print-after-observations.json. All 16 images in screenshots/segment-12-before-* and screenshots/run-62-print-* were opened and checked for private data. Project figures, captions, lessons and stack remain; navigation boxes disappear. Search title and description remain while screen-only suggestions disappear. Both theme preferences use the intended white print surface. These viewport images do not establish paginated PDF layout.

Collaborative browser screen checks: at 1280px, Mailroom ML pager computed display:flex and Next reached Mailroom Reloaded; at 375px Search suggestions computed display:flex and calibration produced 11 matches without page overflow.

## Limits

CSS print media was tested, not native printer dialogs, physical printing or full PDF pagination. No Firefox/WebKit, physical devices, screen readers or native Linux. External destinations were not exercised. PR108 live deployment is a separate revision and bounded smoke record in pr108-live-smoke.md. A zero audit score describes these measured criteria, not every aspect of site quality.
