# PR108 merge and live smoke check

PR108 merged into main as `8d430f2bb18c2111bbe4830e56c5d1069890ac74`. `gh run list --limit 3 --json name,status,conclusion,headSha` reports its Pages build/deployment completed successfully.

The collaborative browser opened the actual portfolio (1280px viewport), using read-only navigation and local theme/citation controls:

- `https://exios66.github.io/resume/`: home page loads with the portfolio title.
- `search.html?q=calibration&type=report`: native filter value `report`, three report results from eleven matching pages, no page overflow.
- `projects/natd/report.html`: seventeen note references and seventeen full source notes; notes are within main. Citation 1 reaches `#fn1`; its return arrow reaches `#fnref1`. Source URL retained as `https://doi.org/10.1177/0261927X14535916` (publisher page not opened).
- `research.html`: heading reads “Graduate research at UW–Madison”. Theme toggle changes to dark and the preference persists when navigating back to Search.
- Browser GET of `assets/Jack_Burleson_Resume.pdf`: HTTP 200, `application/pdf`, leading bytes `%PDF-`.
- Browser GET of `smoke-check/missing-page`: HTTP 404, custom “Page not found” content and site-prefix recovery links present.

This is a bounded live smoke check, not a byte-for-byte comparison of all pages/assets or proof of every interaction. It covers the deployed PR108 revision, before the print follow-up. Native Linux, other browser engines, real devices, screen readers, publisher-source verification, native print dialogs, physical printing and complete PDF pagination remain unchecked.
