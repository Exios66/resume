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
GLOBALS = POST["build_pdf"].__globals__


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


class ChromiumDiscoveryTests(unittest.TestCase):
    def test_existing_explicit_browser_takes_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "chrome"
            executable.touch()
            with patch.dict(os.environ, {"CHROMIUM_PATH": str(executable)}, clear=True), \
                    patch("glob.glob") as glob:
                self.assertEqual(POST["find_chromium"](), str(executable))
                glob.assert_not_called()

    def test_missing_override_uses_last_sorted_versioned_match(self):
        with patch.dict(os.environ, {
            "CHROMIUM_PATH": "/missing/chrome",
            "PLAYWRIGHT_BROWSERS_PATH": "/browsers",
        }, clear=True), patch.object(Path, "exists", return_value=False), \
                patch("glob.glob", return_value=["/browsers/120/chrome", "/browsers/110/chrome"]) as glob:
            self.assertEqual(POST["find_chromium"](), "/browsers/120/chrome")
            glob.assert_called_once_with("/browsers/chromium-*/chrome-linux*/chrome")

    def test_unversioned_layout_is_a_fallback(self):
        with patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": "/browsers"}, clear=True), \
                patch("glob.glob", side_effect=[[], ["/browsers/chromium/chrome-linux/chrome"]]) as glob:
            self.assertEqual(POST["find_chromium"](), "/browsers/chromium/chrome-linux/chrome")
            self.assertEqual(glob.call_args_list, [
                call("/browsers/chromium-*/chrome-linux*/chrome"),
                call("/browsers/chromium/chrome-linux*/chrome"),
            ])

    def test_no_matches_delegates_to_playwright(self):
        for environment in ({}, {"PLAYWRIGHT_BROWSERS_PATH": "/empty"}):
            with self.subTest(environment=environment), \
                    patch.dict(os.environ, environment, clear=True), patch("glob.glob", return_value=[]):
                self.assertIsNone(POST["find_chromium"]())


class PostRenderTests(BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.root = Path(self.enterContextCompat(tempfile.TemporaryDirectory()))
        self.docs = self.root / "docs"
        self.source = self.root / "assets" / POST["PDF_NAME"]
        self.output = self.docs / "assets" / POST["PDF_NAME"]
        self.source.parent.mkdir()
        self.source.write_bytes(b"existing source PDF")
        self.enterContextCompat(patch.dict(GLOBALS, {"ROOT": self.root, "DOCS": self.docs}))
        self.find_browser = Mock(return_value=None)
        self.enterContextCompat(patch.dict(GLOBALS, {"find_chromium": self.find_browser}))

    def test_pdf_uses_print_styles_waits_for_fonts_and_copies_result(self):
        for executable in (None, "/custom/chrome"):
            with self.subTest(executable=executable):
                self.factory.reset_mock()
                self.find_browser.return_value = executable
                self.page.pdf.side_effect = lambda **options: Path(options["path"]).write_bytes(b"new PDF")
                self.assertIs(POST["build_pdf"](), True)
                launch = self.factory.return_value.__enter__.return_value.chromium.launch
                launch.assert_called_once_with(**({"executable_path": executable} if executable else {}))
                self.assertEqual(self.page.method_calls, [
                    call.goto((self.docs / "resume.html").as_uri(), wait_until="networkidle"),
                    call.emulate_media(media="print"),
                    call.evaluate("document.fonts.ready"),
                    call.pdf(path=str(self.output), format="Letter", print_background=True,
                             prefer_css_page_size=True, display_header_footer=False,
                             tagged=True, outline=True),
                ])
                self.browser.close.assert_called_once_with()
                self.assertEqual(self.source.read_bytes(), b"new PDF")
                self.assertEqual(self.output.read_bytes(), b"new PDF")
        self.assertIn("wrote Jack_Burleson_Resume.pdf", self.stdout.getvalue())

    def test_missing_playwright_preserves_existing_pdfs(self):
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"existing published PDF")
        with patch.dict(sys.modules, {"playwright.sync_api": None}):
            self.assertIs(POST["build_pdf"](), False)
        self.assertEqual(self.source.read_bytes(), b"existing source PDF")
        self.assertEqual(self.output.read_bytes(), b"existing published PDF")
        self.factory.assert_not_called()
        self.assertIn("playwright not installed", self.stderr.getvalue())

    def test_browser_failures_warn_and_preserve_pdfs(self):
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"existing published PDF")
        launch = self.factory.return_value.__enter__.return_value.chromium.launch
        for operation in (launch, self.browser.new_page, self.page.goto,
                          self.page.emulate_media, self.page.evaluate, self.page.pdf):
            with self.subTest(operation=operation._mock_name):
                operation.side_effect = RuntimeError("browser unavailable")
                try:
                    self.assertIs(POST["build_pdf"](), False)
                    self.assertEqual(self.source.read_bytes(), b"existing source PDF")
                    self.assertEqual(self.output.read_bytes(), b"existing published PDF")
                finally:
                    operation.side_effect = None
        self.assertIn("PDF build failed (browser unavailable)", self.stderr.getvalue())

    def test_output_directory_errors_propagate(self):
        with patch.object(Path, "mkdir", side_effect=PermissionError("read only")):
            with self.assertRaisesRegex(PermissionError, "read only"):
                POST["build_pdf"]()
        self.factory.assert_not_called()
        self.assertEqual(self.source.read_bytes(), b"existing source PDF")

    def test_copy_errors_propagate_without_overwriting_source(self):
        self.page.pdf.side_effect = lambda **options: Path(options["path"]).write_bytes(b"new PDF")
        with patch("shutil.copyfile", side_effect=PermissionError("cannot copy")):
            with self.assertRaisesRegex(PermissionError, "cannot copy"):
                POST["build_pdf"]()
        self.assertEqual(self.source.read_bytes(), b"existing source PDF")
        self.assertNotIn("post-render: wrote", self.stdout.getvalue())

    def test_main_creates_pages_marker_even_when_pdf_is_skipped(self):
        build = Mock(return_value=False)
        with patch.dict(GLOBALS, {"build_pdf": build}):
            POST["main"]()
            self.assertTrue((self.docs / ".nojekyll").is_file())
            build.assert_called_once_with()

    def test_main_removes_search_index_and_is_repeatable(self):
        self.docs.mkdir()
        (self.docs / "search.json").write_text("{}")
        unrelated = self.docs / "index.html"
        unrelated.write_text("keep me")

        def build():
            self.assertTrue((self.docs / ".nojekyll").is_file())
            self.assertFalse((self.docs / "search.json").exists())

        with patch.dict(GLOBALS, {"build_pdf": Mock(side_effect=build)}):
            POST["main"]()
            POST["main"]()
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


if __name__ == "__main__":
    unittest.main()
