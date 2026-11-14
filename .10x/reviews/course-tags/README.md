# Course tags and research wording

Updates PR #146 with three existing project-page tags, the concise scholarship wording on Research/About/Résumé, and Research-only entries for AI Terrarium and Alignment-Gym. Neither private repository URL is published. Alignment-Gym's brief description was checked against its README; no private evaluation results or implementation details were added.

Verification:

- `. .autoresearch-tools/env.sh && scripts/hillclimb/hc.sh doctor`: All tools present (after rendering; an earlier invocation overlapped the render's temporary output cleanup).
- `"$QUARTO" render --quiet`, followed by individual Research and Résumé renders; `.venv/bin/python scripts/build/make-resume-pdf.py` regenerated the PDF.
- `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/python/test_resume_pdf.py tests/python/test_links.py tests/browser/test_browser.py -k 'resume or research or about or print'`: 21 passed, 76 deselected, 41 subtests passed.
- Direct generated-page checks: correct Research/About/Résumé titles, removed scholarship elaboration and private repository URL; source and published PDFs both exactly two pages.
- Chromium screenshots in this directory show the three tags and Research at desktop/phone widths. Inspected for layout and publication privacy.

No real devices, screen readers, or full secondary-engine page matrix checked in this change. Prior CodeAnt duplicate-page/title findings were fixed by 861ef38; the present renders and browser checks verify the corrected pages.

## Page-budget fix

The new MapReduce course tag pushed the case-study page 2 compressed bytes over
its 19,000-byte transfer budget. The kicker now reads "In active development ·
distributed systems · Go + Python" and the caveat ends "not rerun here."; the
page is 18,997 compressed bytes. `tests/python/test_page_budget.py` and
`tests/python/test_mapreduce_reloaded.py` pass.
