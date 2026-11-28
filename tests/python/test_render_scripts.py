"""Unit tests with fake browsers; no Quarto, Playwright, or asset writes required.

Run from the repository root: python3 -B -m unittest discover -s tests -p 'test_*.py'
"""

import contextlib
import io
import os
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, Mock, call, patch


ROOT = Path(__file__).resolve().parents[2]
# run_path loads the hyphenated filename without executing its main entry point.
POST = runpy.run_path(str(ROOT / "scripts/build/post-render.py"))
GLOBALS = POST["publish_pdf"].__globals__


class BrowserTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = MagicMock()
        self.browser = self.factory.return_value.__enter__.return_value.chromium.launch.return_value
        self.page = self.browser.new_page.return_value
        api = types.ModuleType("playwright.sync_api")
        api.sync_playwright = self.factory
        self.enterContextCompat(patch.dict(sys.modules, {
            "playwright": types.ModuleType("playwright"),
            "playwright.sync_api": api,
        }))
        self.stdout = self.enterContextCompat(contextlib.redirect_stdout(io.StringIO()))
        self.stderr = self.enterContextCompat(contextlib.redirect_stderr(io.StringIO()))

    def enterContextCompat(self, manager):
        # unittest.TestCase.enterContext is only available in Python 3.11+.
        value = manager.__enter__()
        self.addCleanup(manager.__exit__, None, None, None)
        return value


class PostRenderTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.docs = self.root / "docs"
        self.source = self.root / "assets" / POST["PDF_NAME"]
        self.output = self.docs / "assets" / POST["PDF_NAME"]
        self.source.parent.mkdir()
        self.source.write_bytes(b"owner's PDF")
        patcher = patch.dict(GLOBALS, {"ROOT": self.root, "DOCS": self.docs})
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_quietly(self, function):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = function()
        return result, out.getvalue(), err.getvalue()

    def test_end_of_document_footnotes_seat_inside_main(self):
        text = ('<body><main id="main"><p>Body cites'
                '<a href="#fn1" class="footnote-ref" role="doc-noteref"><sup>1</sup></a></p></main>'
                '<footer class="site-footer"></footer>'
                '<section id="footnotes" class="footnotes" role="doc-endnotes"><ol><li id="fn1">Levine (2014).</li></ol></section>')
        fixed = POST["seat_footnotes"](text)
        self.assertIn('<section id="footnotes"', fixed)
        self.assertLess(fixed.find('<section id="footnotes"'), fixed.find('</main>'))
        self.assertGreater(fixed.find('<section id="footnotes"'), fixed.find('class="footnote-ref"'))
        # A page whose footnotes are already inside a landmark is untouched.
        plain = '<body><main id="main"></main><footer class="site-footer"></footer></body>'
        self.assertEqual(POST["seat_footnotes"](plain), plain)

    def test_raster_figures_link_to_their_full_size_file_once(self):
        link = POST["link_raster_figures"]
        shot = '<p><img src="figures/app.jpg" class="fig img-fluid" style="width:100.0%" alt="The app."></p>'
        linked = link(shot)
        self.assertEqual(linked, '<p><a class="fig-zoom" href="figures/app.jpg" title="Open full size">'
                         '<img src="figures/app.jpg" class="fig img-fluid" style="width:100.0%" alt="The app."></a></p>')
        self.assertEqual(link(linked), linked)
        vector = '<p><img src="figures/plot.svg" class="fig img-fluid" alt="A plot."></p>'
        self.assertEqual(link(vector), vector)
        self.assertIn('href="a/b.png"', link('<img src="a/b.png" class="fig img-fluid" alt="">'))
        # Attribute order and the class list vary with Quarto and the site filters.
        lead = '<img src="f/lead.jpg" class="fig" loading="eager" decoding="async" alt="x" width="1200" height="750">'
        self.assertEqual(link(lead), '<a class="fig-zoom" href="f/lead.jpg" title="Open full size">' + lead + '</a>')
        self.assertIn('href="f/c.jpg"', link('<img class="fig" alt="" src="f/c.jpg">'))
        self.assertEqual(link('<img src="f/x.jpg" class="figure-img" alt="">'), '<img src="f/x.jpg" class="figure-img" alt="">')

    def test_empty_highlight_placeholder_is_removed_once(self):
        drop = POST["drop_empty_highlight_rule"]
        page = "div.sourceCode { margin: 1em 0; }\npre.numberSource { margin-left: 3em; }\ndiv.sourceCode\n  {   }\n@media screen {\n"
        fixed = drop(page)
        self.assertEqual(fixed, "div.sourceCode { margin: 1em 0; }\npre.numberSource { margin-left: 3em; }\n@media screen {\n")
        self.assertEqual(drop(fixed), fixed)
        self.assertEqual(drop("<p>No highlight.</p>"), "<p>No highlight.</p>")

    def test_sprite_keeps_only_the_icons_a_page_uses(self):
        prune = POST["prune_sprite"]
        page = ('<a><svg class="icon"><use href="#i-mail"></use></svg></a>'
                '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">'
                '<symbol id="i-mail" viewBox="0 0 24 24"><path d="M1"/></symbol>'
                '<symbol id="i-moon" viewBox="0 0 24 24"><path d="M2"/></symbol></svg>')
        pruned = prune(page)
        self.assertIn('<symbol id="i-mail"', pruned)
        self.assertNotIn('i-moon', pruned)
        self.assertEqual(prune(pruned), pruned)
        self.assertEqual(prune("<p>No sprite.</p>"), "<p>No sprite.</p>")

    def test_committed_pdf_is_published_byte_for_byte(self):
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"stale copy")
        result, out, _ = self.run_quietly(POST["publish_pdf"])
        self.assertIs(result, True)
        self.assertEqual(self.output.read_bytes(), b"owner's PDF")
        self.assertEqual(self.source.read_bytes(), b"owner's PDF")
        self.assertIn("published Jack_Burleson_Resume.pdf", out)

    def test_render_never_prints_the_page_to_pdf(self):
        self.assertNotIn("build_pdf", POST)
        self.assertNotIn("sync_playwright", (ROOT / "scripts/build/post-render.py").read_text(encoding="utf-8"))

    def test_missing_source_warns_and_leaves_docs_untouched(self):
        self.source.unlink()
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"existing published PDF")
        result, _, err = self.run_quietly(POST["publish_pdf"])
        self.assertIs(result, False)
        self.assertEqual(self.output.read_bytes(), b"existing published PDF")
        self.assertIn("résumé PDF not published", err)

    def test_output_directory_and_copy_errors_propagate(self):
        for target, error in ((Path, "mkdir"), (None, "copyfile")):
            with self.subTest(error=error):
                patcher = patch.object(Path, "mkdir", side_effect=PermissionError("read only")) \
                    if target else patch("shutil.copyfile", side_effect=PermissionError("read only"))
                with patcher, self.assertRaisesRegex(PermissionError, "read only"):
                    self.run_quietly(POST["publish_pdf"])
                self.assertEqual(self.source.read_bytes(), b"owner's PDF")

    def test_main_creates_pages_marker_and_publishes_the_pdf(self):
        publish = Mock(return_value=False)
        with patch.dict(GLOBALS, {"publish_pdf": publish}):
            self.run_quietly(POST["main"])
            self.assertTrue((self.docs / ".nojekyll").is_file())
            publish.assert_called_once_with()

    def test_main_removes_search_index_and_is_repeatable(self):
        self.docs.mkdir()
        (self.docs / "search.json").write_text("{}")
        unrelated = self.docs / "index.html"
        unrelated.write_text("keep me")

        def publish():
            self.assertTrue((self.docs / ".nojekyll").is_file())
            self.assertFalse((self.docs / "search.json").exists())

        with patch.dict(GLOBALS, {"publish_pdf": Mock(side_effect=publish)}):
            self.run_quietly(POST["main"])
            self.run_quietly(POST["main"])
        self.assertEqual(unrelated.read_text(), "keep me")


class SocialImageTests(BrowserTestCase):
    def load_make_og(self):
        # Load without executing __main__ so tests can call main([...]) with a clean argv.
        return runpy.run_path(str(ROOT / "scripts/build/make-og.py"), run_name="make_og")

    def test_screenshot_dimensions_fonts_destination_and_browser_selection(self):
        """Verify social-image capture uses the expected browser, fonts, and output."""
        make_og = self.load_make_og()
        with tempfile.TemporaryDirectory() as tmp:
            site_og = Path(tmp) / "og-image.png"
            for matches, expected in (([], {}), (["/b/z/chrome", "/b/a/chrome"],
                                                 {"executable_path": "/b/z/chrome"})):
                with self.subTest(matches=matches), \
                        patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": "/b"}, clear=True), \
                        patch.object(make_og["glob"], "glob", return_value=matches) as glob, \
                        patch.dict(make_og["write_site_card"].__globals__, {"SITE_OG": site_og}):
                    self.factory.reset_mock()
                    self.page.method_calls.clear()
                    # Atomic capture writes a temporary .partial.png then renames it.
                    self.page.screenshot.side_effect = (
                        lambda path, **_kwargs: Path(path).write_bytes(b"x" * 2000)
                    )
                    make_og["main"]([])
                    glob.assert_called_once_with("/b/chromium-*/chrome-linux*/chrome")
                    self.factory.return_value.__enter__.return_value.chromium.launch.assert_called_once_with(**expected)
                    self.browser.new_page.assert_called_once_with(viewport={"width": 1200, "height": 630})
                    self.assertEqual(
                        [c for c in self.page.method_calls if c[0] in {"goto", "evaluate"}],
                        [
                            call.goto((ROOT / "scripts/build/og-image.html").as_uri(), wait_until="networkidle"),
                            call.evaluate("document.fonts.ready"),
                        ],
                    )
                    self.assertTrue(any(c[0] == "screenshot" for c in self.page.method_calls))
                    self.assertTrue(site_og.is_file())
                    self.browser.close.assert_called_once_with()
        self.assertIn("wrote assets/og-image.png", self.stdout.getvalue())

    def test_screenshot_failure_is_not_reported_as_success(self):
        make_og = self.load_make_og()
        with tempfile.TemporaryDirectory() as tmp:
            site_og = Path(tmp) / "og-image.png"
            self.page.screenshot.side_effect = RuntimeError("capture failed")
            with patch.object(make_og["glob"], "glob", return_value=[]), \
                    patch.dict(make_og["write_site_card"].__globals__, {"SITE_OG": site_og}):
                with self.assertRaisesRegex(RuntimeError, "capture failed"):
                    make_og["main"]([])
            self.assertFalse(site_og.exists())
        self.assertNotIn("wrote assets/og-image.png", self.stdout.getvalue())
        self.factory.return_value.__exit__.assert_called_once()

    def test_project_card_uses_title_kicker_and_motif(self):
        make_og = self.load_make_og()
        html = make_og["project_card_html"]("wave-laboratory")
        self.assertIn("Wave Laboratory", html)
        self.assertIn("Side project", html)
        self.assertIn("card-cover", html)
        self.assertIn("#fe01b1", html)
        self.assertIn((ROOT / "partials/covers/wave-laboratory.svg").read_text(encoding="utf-8").strip()[:40], html)


class TitleTests(unittest.TestCase):
    dedupe = staticmethod(POST["dedupe_title"])

    def test_drops_suffix_when_page_title_names_site(self):
        page = "<head><title>Wave Laboratory — Jack J. Burleson – Jack J. Burleson</title></head>"
        self.assertEqual(self.dedupe(page, "Jack J. Burleson"),
                         "<head><title>Wave Laboratory — Jack J. Burleson</title></head>")

    def test_keeps_suffix_when_page_title_omits_site(self):
        page = "<title>Résumé – Jack J. Burleson</title>"
        self.assertEqual(self.dedupe(page, "Jack J. Burleson"), page)

    def test_is_idempotent(self):
        once = self.dedupe("<title>A — Jack J. Burleson – Jack J. Burleson</title>", "Jack J. Burleson")
        self.assertEqual(self.dedupe(once, "Jack J. Burleson"), once)

    def test_reads_site_title_from_config(self):
        self.assertEqual(POST["site_title"](), "Jack J. Burleson")

    def test_escapes_site_title(self):
        page = "<title>R&amp;D — A &amp; B – A &amp; B</title>"
        self.assertEqual(self.dedupe(page, "A & B"), "<title>R&amp;D — A &amp; B</title>")

    def test_rewrites_rendered_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_quarto.yml").write_text("website:\n  title: 'Site'\n", encoding="utf-8")
            docs = root / "docs"
            (docs / "sub").mkdir(parents=True)
            page = docs / "sub" / "a.html"
            page.write_text("<title>A — Site – Site</title>", encoding="utf-8")
            with patch.dict(GLOBALS, {"ROOT": root, "DOCS": docs}):
                POST["dedupe_titles"]()
            self.assertEqual(page.read_text(encoding="utf-8"), "<title>A — Site</title>")

    def test_missing_config_skips(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(GLOBALS, {"ROOT": Path(tmp)}):
            self.assertIsNone(POST["site_title"]())


class CacheBustTests(unittest.TestCase):
    bust = staticmethod(POST["cache_bust"])

    def test_versions_links_at_any_depth(self):
        page = '<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="../../styles.css">'
        self.assertEqual(self.bust(page, {"styles.css": "abc123"}),
                         '<link rel="stylesheet" href="styles.css?v=abc123">'
                         '<link rel="stylesheet" href="../../styles.css?v=abc123">')

    def test_versions_absolute_links_under_the_site_path(self):
        page = '<link rel="stylesheet" href="/resume/styles.css"><script src="/resume/assets/js/site.js" defer></script>'
        self.assertEqual(self.bust(page, {"styles.css": "abc", "assets/js/site.js": "f00"}),
                         '<link rel="stylesheet" href="/resume/styles.css?v=abc">'
                         '<script src="/resume/assets/js/site.js?v=f00" defer></script>')

    def test_replaces_an_old_version_and_is_idempotent(self):
        page = '<script src="../assets/js/site.js?v=0aa" defer></script>'
        once = self.bust(page, {"assets/js/site.js": "f00"})
        self.assertEqual(once, '<script src="../assets/js/site.js?v=f00" defer></script>')
        self.assertEqual(self.bust(once, {"assets/js/site.js": "f00"}), once)

    def test_leaves_other_links_alone(self):
        page = '<link href="../site_libs/quarto-html/tippy.css" rel="stylesheet"><a href="mystyles.css">x</a>'
        self.assertEqual(self.bust(page, {"styles.css": "abc"}), page)

    def test_rewrites_rendered_pages_with_content_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp)
            (docs / "styles.css").write_text("body{}", encoding="utf-8")
            (docs / "sub").mkdir()
            page = docs / "sub" / "a.html"
            page.write_text('<link rel="stylesheet" href="../styles.css">', encoding="utf-8")
            with patch.dict(GLOBALS, {"DOCS": docs}):
                POST["cache_bust_pages"]()
            version = POST["hashlib"].sha256(b"body{}").hexdigest()[:10]
            self.assertEqual(page.read_text(encoding="utf-8"),
                             f'<link rel="stylesheet" href="../styles.css?v={version}">')


class StripCommentsTests(unittest.TestCase):
    strip = staticmethod(POST["strip_comments"])

    def test_css_comments_and_blank_lines_go(self):
        css = "/* head */\n.a { color: red; } /* why */\n\n/* two\n   lines */\n.b::after { content: \"\"; }\n"
        self.assertEqual(self.strip(css, "css"), ".a { color: red; }\n.b::after { content: \"\"; }\n")

    def test_js_keeps_strings_regexes_and_urls(self):
        js = ('/* Header. */\n(() => {\n  // a note\n  /** Doc. */\n  const u = "https://x.org/a"; // trailing\n'
              '  const r = /\\/docs\\//;\n})();\n')
        self.assertEqual(self.strip(js, "js"),
                         '(() => {\n  const u = "https://x.org/a"; // trailing\n  const r = /\\/docs\\//;\n})();\n')

    def test_published_copies_are_stripped_before_hashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp)
            (docs / "assets/js").mkdir(parents=True)
            (docs / "styles.css").write_text("/* c */\nbody{}\n", encoding="utf-8")
            (docs / "assets/js/site.js").write_text("// c\nrun();\n", encoding="utf-8")
            with patch.dict(GLOBALS, {"DOCS": docs}):
                POST["strip_published_comments"]()
            self.assertEqual((docs / "styles.css").read_text(encoding="utf-8"), "body{}\n")
            self.assertEqual((docs / "assets/js/site.js").read_text(encoding="utf-8"), "run();\n")
        source = (ROOT / "scripts/build/post-render.py").read_text(encoding="utf-8")
        self.assertLess(source.index("    strip_published_comments()"), source.index("    cache_bust_pages()"))


class TranslationReadyTests(unittest.TestCase):
    prepare = staticmethod(POST["prepare_translation"])
    names = staticmethod(POST["protect_names"])

    def test_code_and_drawn_text_are_kept_as_written(self):
        page = ('<html><head><title>x</title></head><body><main><p>Run <code>uv sync</code></p>'
                '<pre class="sourceCode"><code>make</code></pre><kbd>/</kbd>'
                '<figure class="chart chart-bars"><div class="chart-body"><svg viewbox="0 0 1 1"><text>Sort</text></svg></div>'
                '<template class="chart-narrow"><svg viewbox="0 0 1 1"></svg></template></figure>'
                '<figure class="diagram diagram-x" role="img"><svg aria-hidden="true"></svg><figcaption id="c">How</figcaption></figure>'
                '<svg class="icon"><use href="#i"></use></svg></main></body></html>')
        out = self.prepare(page)
        self.assertIn('<code translate="no">uv sync</code>', out)
        self.assertIn('<pre translate="no" class="sourceCode">', out)
        self.assertIn('<kbd translate="no">', out)
        self.assertEqual(out.count('<svg translate="no"'), 3)
        # Icons are not drawn text; only chart and diagram drawings are marked.
        self.assertIn('<svg class="icon">', out)
        self.assertEqual(self.prepare(out), out)

    def test_names_in_prose_are_wrapped_but_attributes_and_code_are_not(self):
        text = ('<body><h1>Wave Laboratory</h1><p>The Mandalay Bay and Mailroom-ML.</p>'
                '<img alt="Wave Laboratory screenshot"><code>Mailroom-ML</code>'
                '<script>var x = "AeroGlobe";</script><a href="/aeroglobe">AeroGlobe</a>'
                '<p>Mailroom-ML-v2 and RVL-CDIP-Classifier stay whole.</p></body>')
        out = self.names(text)
        self.assertIn('<h1><span translate="no">Wave Laboratory</span></h1>', out)
        self.assertIn('<span translate="no">The Mandalay Bay</span> and <span translate="no">Mailroom-ML</span>.', out)
        self.assertIn('alt="Wave Laboratory screenshot"', out)
        self.assertIn('<code>Mailroom-ML</code>', out)
        self.assertIn('var x = "AeroGlobe";', out)
        self.assertIn('<a href="/aeroglobe"><span translate="no">AeroGlobe</span></a>', out)
        # A longer hyphenated token is not a name; the longest name wins.
        self.assertIn('Mailroom-ML-v2 and <span translate="no">RVL-CDIP-Classifier</span>', out)
        self.assertEqual(self.names(out), out)

    def test_names_inside_a_kept_element_are_not_wrapped_again(self):
        text = '<body><div translate="no"><div>Neuron Atlas</div></div><p>Neuron Atlas</p></body>'
        self.assertEqual(self.names(text),
                         '<body><div translate="no"><div>Neuron Atlas</div></div><p><span translate="no">Neuron Atlas</span></p></body>')

    def test_generated_labels_become_text_once(self):
        page = ('<body><div class="code-copy-outer-scaffold"><button title="Copy to Clipboard" class="code-copy-button"><i class="bi"></i></button></div>'
                '<a class="fig-zoom" href="a.jpg" title="Open full size"><img src="a.jpg" class="fig"></a>'
                '<figure class="diagram"><svg></svg><figcaption>How it fits.</figcaption></figure>'
                '<figure class="chart chart-dots"><p class="chart-tools"></p></figure></body>')
        out = self.prepare(page)
        self.assertIn('<span class="cc-copy">Copy</span><span class="cc-done">Copied</span></button>', out)
        self.assertIn('<img src="a.jpg" class="fig"><span class="zoom-hint">Tap to open full size</span></a>', out)
        self.assertIn('<figcaption><span class="scroll-hint" aria-hidden="true">Scroll sideways to see the whole diagram. </span>How it fits.</figcaption>', out)
        self.assertIn('<p class="chart-tools"></p><p class="scroll-hint">Scroll sideways to see the whole chart.</p></figure>', out)
        self.assertEqual(self.prepare(out), out)

    def test_head_is_left_alone(self):
        page = '<html><head><title>Wave Laboratory</title><style>pre{}</style></head><body></body></html>'
        self.assertEqual(self.prepare(page), page)


if __name__ == "__main__":
    unittest.main()
