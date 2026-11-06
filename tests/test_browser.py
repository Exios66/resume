"""Opt-in, real Chromium checks of the rendered site; serves it under a subpath.

pip install playwright pytest pypdf && playwright install chromium
RUN_BROWSER_TESTS=1 python -m pytest -q tests/test_browser.py
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
from threading import Thread

import pytest

if os.environ.get("RUN_BROWSER_TESTS") != "1":
    pytest.skip("Set RUN_BROWSER_TESTS=1 to run Chromium checks", allow_module_level=True)

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(path.relative_to(ROOT / "docs").as_posix()
               for path in (ROOT / "docs").rglob("*.html") if "site_libs" not in path.parts)


@pytest.fixture(scope="module")
def site():
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=ROOT))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser, f"http://127.0.0.1:{server.server_port}/docs/"
        browser.close()
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.parametrize("width", [320, 375, 768, 1280])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_every_page_layout_and_resources(site, width, theme):
    browser, base = site
    context = browser.new_context(viewport={"width": width, "height": 900},
                                  color_scheme=theme, reduced_motion="reduce")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    page.on("requestfailed", lambda request: errors.append(request.url))
    page.on("response", lambda response: errors.append(f"{response.status}: {response.url}")
            if response.status >= 400 else None)
    try:
        assert len(PAGES) >= 28
        for path in PAGES:
            assert page.goto(base + path).ok, path
            page.evaluate("document.fonts.ready")
            expect(page.locator("main")).to_have_count(1)
            expect(page.get_by_role("heading", level=1)).to_have_count(1)
            expect(page.locator('.site-nav [aria-current="page"]')).to_have_count(1)
            failures = page.evaluate("""() => {
              const failures = [];
              if (document.documentElement.scrollWidth > innerWidth + 1) failures.push('page overflow');
              for (const el of document.querySelectorAll('.nav-link, .theme-toggle, .project-jump a')) {
                if (el.getBoundingClientRect().height < 44) failures.push('small touch target: ' + el.textContent);
              }
              for (const card of document.querySelectorAll('.card')) {
                const paper = card.closest('.page');
                const right = paper.getBoundingClientRect().right - parseFloat(getComputedStyle(paper).paddingRight);
                if (card.getBoundingClientRect().right > right + 1) failures.push('card exceeds content padding');
              }
              for (const link of document.querySelectorAll('a[href^="#"]')) {
                const id = decodeURIComponent(link.getAttribute('href').slice(1));
                if (id && !document.getElementById(id)) failures.push('missing anchor: ' + id);
              }
              return failures;
            }""")
            assert not failures, (path, width, theme, failures)
            for image in page.locator("main img").all():
                image.scroll_into_view_if_needed()
                assert image.evaluate("img => img.decode().then(() => img.naturalWidth > 0)"), path
            assert not errors, (path, errors)
    finally:
        context.close()


def test_project_navigation_theme_and_keyboard(site):
    browser, base = site
    context = browser.new_context(viewport={"width": 375, "height": 812})
    page = context.new_page()
    try:
        page.goto(base)
        page.keyboard.press("Tab")
        expect(page.locator(".skip-link")).to_be_focused()
        page.keyboard.press("Enter")
        expect(page).to_have_url(base + "#main")
        page.get_by_role("link", name="View projects", exact=True).click()
        page.get_by_role("link", name="Neuron Atlas", exact=True).click()
        expect(page.get_by_role("heading", level=1)).to_have_text("Neuron Atlas")
        page.get_by_role("button", name="Switch to dark theme").click()
        page.reload()
        expect(page.locator("html")).to_have_attribute("data-theme", "dark")
        page.get_by_role("link", name="All projects", exact=True).click()
        page.get_by_role("link", name="Document AI", exact=True).click()
        expect(page).to_have_url(base + "projects/index.html#document-intelligence")
        for width in (375, 768, 1280):
            page.set_viewport_size({"width": width, "height": 900})
            page.goto(base + "projects/index.html#document-intelligence")
            page.evaluate("document.fonts.ready")
            assert page.evaluate("""() => {
              const header = document.querySelector('.site-header');
              const target = document.getElementById('document-intelligence').getBoundingClientRect();
              return getComputedStyle(header).position !== 'sticky' || target.top >= header.getBoundingClientRect().bottom;
            }""")
        page.get_by_role("link", name="Simulations", exact=True).click()
        expect(page.locator("#wave-laboratory.card")).to_have_css("opacity", "1")
    finally:
        context.close()


def test_ecosystem_text_padding_and_code_font(site):
    browser, base = site
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    try:
        page.goto(base + "projects/")
        page.evaluate("document.fonts.ready")
        failures = page.evaluate("""() => {
          const failures = [];
          const nodes = document.querySelectorAll('.diagram-ecosystem [data-node]');
          if (nodes.length !== 5) failures.push('expected five labeled nodes');
          for (const node of nodes) {
            const box = node.querySelector('rect').getBBox();
            for (const text of node.querySelectorAll('text')) {
              const b = text.getBBox();
              if (b.x < box.x + 16 || b.x + b.width > box.x + box.width - 16 ||
                  b.y < box.y + 16 || b.y + b.height > box.y + box.height - 16)
                failures.push(node.dataset.node + ': insufficient padding for ' + text.textContent);
            }
          }
          for (const text of document.querySelectorAll('.diagram-ecosystem .d-code')) {
            if (!getComputedStyle(text).fontFamily.includes('JetBrains Mono')) failures.push('missing code font');
          }
          return failures;
        }""")
        assert not failures, failures
        page.set_viewport_size({"width": 375, "height": 812})
        diagram = page.locator(".diagram-ecosystem")
        diagram.focus()
        expect(diagram).to_be_focused()
        assert diagram.evaluate("el => el.scrollWidth > el.clientWidth")
        page.keyboard.press("End")
        page.keyboard.press("ArrowRight")
        page.wait_for_function("document.querySelector('.diagram-ecosystem').scrollLeft > 0")
    finally:
        page.close()


def test_no_script_and_print_from_dark(site, tmp_path):
    browser, base = site
    context = browser.new_context(java_script_enabled=False, viewport={"width": 375, "height": 812})
    page = context.new_page()
    page.goto(base + "projects/")
    expect(page.get_by_role("link", name="Neuron Atlas", exact=True)).to_be_visible()
    expect(page.locator(".theme-toggle")).to_be_hidden()
    context.close()

    page = browser.new_page(color_scheme="dark")
    try:
        page.goto(base + "resume.html")
        page.evaluate("document.fonts.ready")
        page.emulate_media(media="print")
        expect(page.locator("body")).to_have_css("color", "rgb(17, 17, 17)")
        expect(page.locator(".site-header")).to_be_hidden()
        from pypdf import PdfReader
        output = tmp_path / "resume-print.pdf"
        page.pdf(path=output, prefer_css_page_size=True)
        assert len(PdfReader(output).pages) == 2
    finally:
        page.close()


def test_mailroom_accessible_link_names_and_print_action(site):
    browser, base = site
    page = browser.new_page()
    try:
        page.goto(base + "projects/digital-mailroom.html")
        expect(page.get_by_role("link", name="Mailroom-ML case study", exact=True)).to_have_count(2)
        expect(page.get_by_role("link", name="Mailroom-ML case study Mailroom-ML case study",
                                exact=True)).to_have_count(0)
        page.goto(base + "resume.html")
        page.evaluate("window.printCalls = 0; window.print = () => window.printCalls++")
        page.get_by_role("link", name="Print", exact=True).click()
        assert page.evaluate("window.printCalls") >= 1
        assert not page.url.endswith("#")
    finally:
        page.close()
