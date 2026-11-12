# RVL-CDIP hosted study

The case study and technical report now link directly to the hosted research site and describe its role in prompting the Digital-Mailroom capstone, as confirmed by the owner. The URL comes from the source repository's homepage metadata.

Verification:

- `. .autoresearch-tools/env.sh && "$QUARTO" render --quiet` (then focused case-study render): succeeded.
- `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/python/test_portfolio_additions.py tests/python/test_links.py tests/browser/test_browser.py -k 'rvl or project_pager'`: 3 passed, 100 deselected, 11 subtests passed. This selection did not include browser cases.
- `RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/browser/test_browser.py -k every_page_layout_and_resources`: 8 passed, 67 deselected; all built pages at 320/375/768/1280, light/dark, Chromium.
- In the collaborative Chromium browser, clicked the case study's Live site control; it reached “RVL-CDIP Document Classifier” at the expected Posit URL. A read-only HTTP request returned 200. Inspected the hosted heading and manuscript/tools links.
- Four screenshots in this folder: both portfolio pages at 375 dark and 1280 light, opened and reviewed. `git diff --check`: clean.

The local Firecrawl service was unavailable and the web reader could not open this URL; direct HTTP and the collaborative browser verified it. No hosted forms or tools submitted; no real devices or secondary-engine page pass.
