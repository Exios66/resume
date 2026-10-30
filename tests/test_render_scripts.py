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


ROOT = Path(__file__).resolve().parents[1]
# run_path loads the hyphenated filename without executing its main entry point.
POST = runpy.run_path(str(ROOT / "scripts/post-render.py"))
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

    def test_committed_pdf_is_published_byte_for_byte(self):
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"stale copy")
        result, out, _ = self.run_quietly(POST["publish_pdf"])
        self.assertIs(result, True)
        self.assertEqual(self.output.read_bytes(), b"owner's PDF")
        self.assertEqual(self.source.read_bytes(), b"owner's PDF")
        self.assertIn("published Jack_Burleson_Resume.pdf", out)

    def test_long_reports_get_a_contents_nav(self):
        html = (
            '<h1 id="title">Report</h1>\n'
            '<h2 id="one">One</h2><p>a</p>\n'
            '<h2 id="two">Two</h2><p>b</p>\n'
            '<h2 id="three">Three</h2><p>c</p>\n'
        )
        fixed = POST["add_report_toc"](html)
        self.assertIn('id="TOC"', fixed)
        self.assertIn('href="#two"', fixed)
        self.assertLess(fixed.index('id="TOC"'), fixed.index('id="one"'))
        self.assertEqual(POST["add_report_toc"](fixed), fixed)

    def test_render_never_prints_the_page_to_pdf(self):
        self.assertNotIn("build_pdf", POST)
        self.assertNotIn("sync_playwright", (ROOT / "scripts/post-render.py").read_text(encoding="utf-8"))

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
    def test_screenshot_dimensions_fonts_destination_and_browser_selection(self):
        for matches, expected in (([], {}), (["/b/z/chrome", "/b/a/chrome"],
                                             {"executable_path": "/b/z/chrome"})):
            with self.subTest(matches=matches), \
                    patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": "/b"}, clear=True), \
                    patch("glob.glob", return_value=matches) as glob:
                self.factory.reset_mock()
                runpy.run_path(str(ROOT / "scripts/make-og.py"), run_name="__main__")
                glob.assert_called_once_with("/b/chromium-*/chrome-linux*/chrome")
                self.factory.return_value.__enter__.return_value.chromium.launch.assert_called_once_with(**expected)
                self.browser.new_page.assert_called_once_with(viewport={"width": 1200, "height": 630})
                self.assertEqual(self.page.method_calls, [
                    call.goto((ROOT / "scripts/og-image.html").as_uri(), wait_until="networkidle"),
                    call.evaluate("document.fonts.ready"),
                    call.screenshot(path=str(ROOT / "assets/og-image.png")),
                ])
                self.browser.close.assert_called_once_with()
        self.assertIn("wrote assets/og-image.png", self.stdout.getvalue())

    def test_screenshot_failure_is_not_reported_as_success(self):
        self.page.screenshot.side_effect = RuntimeError("capture failed")
        with patch("glob.glob", return_value=[]):
            with self.assertRaisesRegex(RuntimeError, "capture failed"):
                runpy.run_path(str(ROOT / "scripts/make-og.py"), run_name="__main__")
        self.assertNotIn("wrote assets/og-image.png", self.stdout.getvalue())
        self.factory.return_value.__exit__.assert_called_once()


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


if __name__ == "__main__":
    unittest.main()
