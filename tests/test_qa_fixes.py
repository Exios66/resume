"""Regressions for the browser QA audit fixes (print from dark, nav pills, anchors, diagrams, ...).

Run from the repository root: python3 -m pytest -q tests/test_qa_fixes.py
Static checks on styles.css and the committed pages; no browser, render or network needed.
The Playwright counterpart (computed colors, PDF page count) is described in the pull request.
"""

import re
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")
POST = runpy.run_path(str(ROOT / "scripts/post-render.py"))
DOCS = ROOT / "docs"


def block(css, opener):
    """Return the text of the first {...} block that follows `opener`, braces balanced."""
    start = css.index(opener)
    depth, i = 0, css.index("{", start)
    begin = i
    while True:
        depth += {"{": 1, "}": -1}.get(css[i], 0)
        if depth == 0:
            return css[begin + 1:i]
        i += 1


class PrintFromDarkTests(unittest.TestCase):
    def setUp(self):
        self.print_css = block(CSS, "@media print")

    def test_print_tokens_use_selectors_that_out_rank_both_dark_blocks(self):
        # Dark tokens sit at :root:not([data-theme="light"]) and :root[data-theme="dark"] (0,2,0).
        rule = re.search(r"([^{}]*:root:root:root[^{}]*)\{([^{}]*)\}", self.print_css)
        self.assertIsNotNone(rule, "print block needs a :root:root:root token rule")
        selectors, body = rule.group(1), rule.group(2)
        self.assertIn(':root[data-theme="dark"]:root', selectors)
        self.assertIn(':root:not([data-theme="light"]):root', selectors)
        for token, value in {"--bg": "#fff", "--paper": "#fff", "--ink": "#111", "--muted": "#444",
                             "--rule": "#ccc", "--accent": "#0e6f7a", "--accent-soft": "#fff",
                             "--accent-ink": "#fff"}.items():
            self.assertRegex(body, rf"{token}:\s*{re.escape(value)}\b")
        self.assertIn("color-scheme: light", body)

    def test_print_page_and_body_are_forced_light(self):
        self.assertRegex(self.print_css, r"body \{[^}]*background: #fff;[^}]*color: #111")
        self.assertRegex(self.print_css, r"\.page \{ background: #fff;")

    def test_every_token_the_dark_blocks_set_is_reset_for_print(self):
        dark = block(CSS, ':root[data-theme="dark"]')
        reset = re.search(r":root:root:root[^{}]*\{([^{}]*)\}", self.print_css).group(1)
        for token in re.findall(r"(--[\w-]+):", dark):
            self.assertIn(token + ":", reset, f"{token} is set in dark mode but not reset in print")


class SmallCssFixTests(unittest.TestCase):
    def test_project_nav_pills_are_excluded_from_prose_link_underlines(self):
        rules = re.findall(r"\.page :is\(p, li\) a:not\(([^)]*)\)", CSS)
        self.assertTrue(rules)
        for selector in rules:
            self.assertIn(".project-nav a", selector)

    def test_page_with_its_own_id_clears_the_sticky_header(self):
        wide = block(CSS, "@media (min-width: 721px)")
        self.assertRegex(wide, r"\.page\[id\] \{ scroll-margin-top: 84px; \}")

    def test_color_scheme_is_declared_for_light_and_both_dark_blocks(self):
        self.assertRegex(block(CSS, ":root {"), r"color-scheme: light;")
        self.assertRegex(block(CSS, ':root:not([data-theme="light"])'), r"color-scheme: dark;")
        self.assertRegex(block(CSS, ':root[data-theme="dark"]'), r"color-scheme: dark;")

    def test_four_cards_use_two_columns_only_above_phone_width(self):
        self.assertRegex(CSS, r"@media \(min-width: 560px\) \{\s*\.cards:not\(\.cards-wide\):has\(> \.card:nth-child\(4\):last-child\) "
                              r"\{ grid-template-columns: repeat\(2, minmax\(0, 1fr\)\); \}")

    def test_wide_card_groups_keep_their_own_column_rule(self):
        # .cards-wide uses a 300px minimum column; the four-card 2x2 rule must not override it.
        self.assertNotRegex(CSS, r"\.cards:has\(> \.card:nth-child\(4\)")

    def test_published_stylesheet_is_the_source_stylesheet(self):
        published = (DOCS / "styles.css").read_text(encoding="utf-8")
        self.assertEqual(published, CSS)

    def test_resume_action_buttons_tighten_on_phones(self):
        phone = block(CSS, "@media (max-width: 480px)")
        self.assertIn(".actions .btn { flex: 1 1 auto;", phone)

    def test_icons_stay_sized_by_em(self):
        self.assertRegex(CSS, r"\.icon \{ width: 1em; height: 1em;")
        self.assertRegex(CSS, r"\.icon-ext \{ width: \.75em; height: \.75em;")
        self.assertIn("[hidden] { display: none !important; }", CSS)


class DiagramHardeningTests(unittest.TestCase):
    harden = staticmethod(POST["harden_diagrams"])

    def test_styled_shapes_get_fill_and_stroke_defaults(self):
        out = self.harden('<figure class="diagram"><svg><rect class="d-box" x="1"/><path class="d-arrow" d="M0 0"></path>'
                          '<circle class="d-accent" r="2"/></svg></figure>')
        self.assertIn('<rect class="d-box" x="1" fill="none" stroke="currentColor"/>', out)
        self.assertIn('<path class="d-arrow" d="M0 0" fill="none" stroke="currentColor">', out)
        self.assertIn('<circle class="d-accent" r="2" fill="none" stroke="currentColor"/>', out)

    def test_existing_attributes_unstyled_shapes_and_other_markup_are_untouched(self):
        source = ('<figure class="diagram"><svg><marker><path d="M0 0L10 5z"/></marker>'
                  '<rect class="d-muted" fill="none" stroke-dasharray="5 4"/></svg></figure>')
        out = self.harden(source)
        self.assertIn('<path d="M0 0L10 5z"/>', out)
        self.assertIn('<rect class="d-muted" fill="none" stroke-dasharray="5 4" stroke="currentColor"/>', out)
        outside = '<svg class="icon"><use href="#i"/></svg><p><rect class="d-box"/></p>'
        self.assertEqual(self.harden(outside), outside)

    def test_hardening_is_idempotent(self):
        once = self.harden('<figure class="diagram"><svg><rect class="d-box"/></svg></figure>')
        self.assertEqual(self.harden(once), once)

    def test_every_published_diagram_shape_survives_a_missing_stylesheet(self):
        shape = re.compile(r"<(?:rect|circle|ellipse|path|line|polygon|polyline)\b[^<>]*>")
        count = 0
        for page in DOCS.rglob("*.html"):
            for figure in re.findall(r'<figure class="diagram".*?</figure>', page.read_text(encoding="utf-8"), re.S):
                for tag in shape.findall(figure):
                    if 'class="d-' not in tag:
                        continue
                    count += 1
                    self.assertIn(' fill="', tag, f"{page.name}: {tag}")
                    self.assertIn(' stroke="', tag, f"{page.name}: {tag}")
        self.assertGreater(count, 50)


class ThemeToggleTests(unittest.TestCase):
    def test_toggle_item_is_hidden_in_markup_and_revealed_by_the_script(self):
        for page in DOCS.rglob("*.html"):
            if "site_libs" in page.parts:
                continue
            html = page.read_text(encoding="utf-8")
            self.assertRegex(html, r'<li hidden(?:="")?><button type="button" class="theme-toggle" aria-label="Switch theme">',
                             page.name)
        script = (ROOT / "partials/scripts.html").read_text(encoding="utf-8")
        self.assertIn("toggle.parentNode.hidden = false;", script)
        self.assertIn("toggle.hidden = false;", script)
        self.assertIn("<li hidden>", (ROOT / "scripts/site.lua").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
