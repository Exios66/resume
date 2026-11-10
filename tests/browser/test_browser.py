"""Opt-in, real-browser checks of the rendered site; serves it under a subpath.

pip install playwright pytest pypdf && playwright install chromium firefox webkit
RUN_BROWSER_TESTS=1 python -m pytest -q tests/browser/test_browser.py
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import re
from threading import Thread

import pytest

if os.environ.get("RUN_BROWSER_TESTS") != "1":
    pytest.skip("Set RUN_BROWSER_TESTS=1 to run Chromium checks", allow_module_level=True)

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PAGES = sorted(path.relative_to(ROOT / "docs").as_posix()
               for path in (ROOT / "docs").rglob("*.html") if "site_libs" not in path.parts)


@pytest.fixture(scope="module")
def playwright():
    with sync_playwright() as instance:
        yield instance


@pytest.fixture(scope="module")
def site(playwright):
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def translate_path(self, path):
            # GitHub Pages serves docs/ at /resume/; 404.html links there absolutely
            # because it is shown at whatever depth the missing address had.
            if path.startswith("/resume/"):
                path = "/docs/" + path[len("/resume/"):]
            return super().translate_path(path)

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=ROOT))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
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
            # The 404 page is not a section of the site, so no nav item is current there.
            expect(page.locator('.site-nav [aria-current="page"]')).to_have_count(0 if path == "404.html" else 1)
            failures = page.evaluate("""() => {
              const failures = [];
              if (document.documentElement.scrollWidth > innerWidth + 1) failures.push('page overflow');
              for (const el of document.querySelectorAll('.nav-link, .theme-toggle, .project-jump a, .btn')) {
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


def diagram_pages():
    """Return built pages that carry an inline diagram."""
    return sorted(path.relative_to(ROOT / "docs").as_posix()
                  for path in (ROOT / "docs").rglob("*.html")
                  if 'class="diagram' in path.read_text(encoding="utf-8"))


def test_diagram_text_clears_arrows_and_box_borders(site):
    browser, base = site
    page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
    try:
        pages = diagram_pages()
        assert len(pages) >= 14, pages
        for path in pages:
            page.goto(base + path)
            page.evaluate("document.fonts.ready")
            failures = page.evaluate("""() => {
              const failures = [];
              const svg = document.querySelector('figure.diagram svg');
              if (!svg) return ['missing diagram svg'];
              const name = (text) => text.textContent.trim().replace(/\\s+/g, ' ');
              const texts = [...svg.querySelectorAll('text')].filter((text) => name(text));
              const boxes = [...svg.querySelectorAll('rect.d-box')];
              const points = [];
              for (const path of svg.querySelectorAll('path.d-arrow')) {
                const length = path.getTotalLength();
                for (let at = 0; at <= length; at += 2) points.push(path.getPointAtLength(at));
              }
              for (const text of texts) {
                const b = text.getBBox();
                if (b.width <= 0 || b.height <= 0) continue;
                for (const box of boxes) {
                  const x = +box.getAttribute('x'), y = +box.getAttribute('y');
                  const w = +box.getAttribute('width'), h = +box.getAttribute('height');
                  const inside = b.x >= x && b.x + b.width <= x + w && b.y >= y && b.y + b.height <= y + h;
                  const outside = b.x + b.width <= x || b.x >= x + w || b.y + b.height <= y || b.y >= y + h;
                  if (!inside && !outside) failures.push('text crosses a box border: ' + name(text));
                }
                const pad = 1.5;
                for (const p of points) {
                  if (p.x >= b.x - pad && p.x <= b.x + b.width + pad &&
                      p.y >= b.y - pad && p.y <= b.y + b.height + pad) {
                    failures.push('text touches an arrow: ' + name(text));
                    break;
                  }
                }
              }
              return failures;
            }""")
            assert not failures, (path, failures)
    finally:
        page.close()


def test_site_search_contents_list_and_pager(site):
    browser, base = site
    page = browser.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
    try:
        page.goto(base + "search.html")
        page.get_by_label("Search this site").fill("mailroom")
        expect(page.locator("#search-status")).to_contain_text('pages match')
        matches = int(page.locator("#search-status").inner_text().split()[0])
        assert matches > 10
        expect(page.locator("#search-results li")).to_have_count(matches)
        snippet = page.locator('#search-results a[href$="projects/digital-mailroom/appendix.html"] + span + p')
        expect(snippet).not_to_contain_text("Case study Case study")
        appendix = page.locator('#search-results a[href$="projects/digital-mailroom/appendix.html"]')
        expect(appendix.locator("..").locator(".result-type")).to_have_text("Appendix")
        report = page.locator('#search-results a[href$="projects/mailroom-ml/report.html"]')
        expect(report.locator("..").locator(".result-type")).to_have_text("Technical report")

        # Whole pages are indexed, not an opening excerpt: "shipment" is only deep in the résumé.
        page.get_by_label("Search this site").fill("shipment")
        expect(page.locator('#search-results a[href$="resume.html"]')).to_be_visible()

        page.get_by_label("Search this site").fill("M9c")
        expect(page.locator("#search-results a").first).to_be_visible()
        case_study = page.locator('#search-results a[href$="projects/mailroom-ml.html"]')
        expect(case_study).to_have_count(1)
        expect(case_study.locator("..").locator(".result-type")).to_have_text("Case study")
        case_study.click()
        expect(page.get_by_role("heading", level=1)).to_have_text("Mailroom-ML")

        page.goto(base + "search.html?q=corpus")
        expect(page.get_by_label("Search this site")).to_have_value("corpus")
        expect(page.locator("#search-results a").first).to_be_visible()

        page.goto(base + "search.html")
        page.get_by_label("Search this site").fill("zzzznothing")
        expect(page.locator("#search-status")).to_contain_text("No pages match")

        page.goto(base + "projects/mailroom-ml/report.html")
        toc = page.locator("nav.page-toc")
        expect(toc).to_be_visible()
        links = toc.get_by_role("link")
        assert links.count() >= 3
        target = links.nth(2).get_attribute("href")
        links.nth(2).click()
        expect(page).to_have_url(re.compile(re.escape(target) + "$"))
        assert page.evaluate("""(id) => {
          const heading = document.getElementById(id);
          const box = heading.getBoundingClientRect();
          return box.top >= 0 && box.top < innerHeight / 2;
        }""", target[1:])

        page.goto(base + "projects/mailroom-ml.html")
        page.locator(".project-pager a", has_text="Next project").click()
        expect(page.get_by_role("heading", level=1)).to_have_text("Mailroom Reloaded")
    finally:
        page.close()


def test_slash_opens_search_without_hijacking_typing(site):
    """Verify shortcut focus, modifier handling, typing, and responsive hints."""
    browser, base = site
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    try:
        page.goto(base + "index.html")
        link = page.get_by_role("link", name="Search", exact=True)
        expect(link).to_have_attribute("aria-keyshortcuts", "/")
        expect(link.locator(".key-hint")).to_have_text("/")
        expect(link.locator(".key-hint")).to_be_visible()

        # The hint inherits the hovered link's accent color in both themes.
        link.hover()
        assert link.locator('.key-hint').evaluate("el => getComputedStyle(el).color") == link.evaluate("el => getComputedStyle(el).color")

        # Browser/OS shortcuts must remain untouched.
        for modifiers in ({'ctrlKey': True}, {'altKey': True}, {'metaKey': True}):
            assert page.evaluate("""modifiers => document.dispatchEvent(new KeyboardEvent(
                'keydown', {key: '/', bubbles: true, cancelable: true, ...modifiers}))""", modifiers)
        assert page.url.endswith('index.html')

        page.keyboard.press("/")
        expect(page).to_have_url(re.compile(r"search\.html\?focus=search$"))
        search = page.get_by_label("Search this site")
        expect(search).to_be_focused()
        page.keyboard.type("mailroom/")
        expect(search).to_have_value("mailroom/")
        assert page.url.split("?")[0].endswith("search.html")

        # The shortcut resolves the relative nav link from a nested page.
        page.goto(base + "projects/digital-mailroom.html")
        page.keyboard.press("/")
        expect(page).to_have_url(re.compile(r"search\.html\?focus=search$"))
        expect(page.get_by_label("Search this site")).to_be_focused()

        # Model an AltGr slash from an international keyboard layout. Playwright's
        # US keyboard mapping cannot generate this OS-specific modifier state.
        page.goto(base + "index.html")
        page.evaluate("""() => {
            const event = new KeyboardEvent('keydown', {key: '/', ctrlKey: true,
                altKey: true, bubbles: true, cancelable: true});
            Object.defineProperty(event, 'getModifierState', {value: key => key === 'AltGraph'});
            document.dispatchEvent(event);
        }""")
        expect(page).to_have_url(re.compile(r"search\.html\?focus=search$"))
        expect(page.get_by_label("Search this site")).to_be_focused()

        # The phone header hides the key cap but keeps the semantic shortcut.
        page.set_viewport_size({"width": 375, "height": 812})
        page.goto(base + "index.html")
        expect(page.get_by_role("link", name="Search", exact=True)).to_have_attribute("aria-keyshortcuts", "/")
        expect(page.locator(".nav-link .key-hint")).to_be_hidden()
    finally:
        page.close()


def test_search_before_index_load_and_after_failure(site):
    browser, base = site
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.add_init_script("""(() => {
      const originalFetch = window.fetch;
      window.fetch = (...args) => new Promise((resolve, reject) => {
        window.releaseIndex = () => resolve(originalFetch(...args));
        window.rejectIndex = () => reject(new Error('index unavailable'));
      });
    })()""")
    try:
        page.goto(base + "search.html")
        search = page.get_by_label("Search this site")
        expect(page.get_by_label("Page type", exact=True)).to_be_disabled()
        search.fill("M9c")
        search.press("Enter")
        assert not errors
        page.evaluate("window.releaseIndex()")
        expect(page.locator('#search-results a[href$="projects/mailroom-ml.html"]')).to_have_count(1)
        expect(page.get_by_label("Page type", exact=True)).to_be_enabled()

        page.goto(base + "search.html")
        page.evaluate("window.rejectIndex()")
        expect(page.get_by_label("Page type", exact=True)).to_be_disabled()
        expect(page.locator("#search-status")).to_have_text("Search is unavailable right now.")
        search.fill("M9c")
        search.press("Escape")
        assert not errors
        expect(page.locator("#search-status")).to_have_text("Search is unavailable right now.")
    finally:
        page.close()


def test_mobile_report_charts_are_scrollable_by_keyboard(site):
    browser, base = site
    page = browser.new_page(viewport={"width": 375, "height": 812}, reduced_motion="reduce")
    try:
        page.goto(base + "projects/mailroom-ml/report.html")
        charts = page.locator(".chart-scroll")
        expect(charts).to_have_count(6)
        for chart in charts.all():
            assert chart.get_attribute("aria-label")
            assert chart.evaluate("el => el.scrollWidth > el.clientWidth")
            expect(chart.locator("img")).to_have_css("width", "700px")
            chart.focus()
            expect(chart).to_be_focused()
            page.keyboard.press("ArrowRight")
            page.wait_for_function("el => el.scrollLeft > 0", arg=chart.element_handle())
    finally:
        page.close()


def test_report_charts_fit_print_from_mobile(site):
    browser, base = site
    page = browser.new_page(viewport={"width": 375, "height": 812})
    try:
        page.goto(base + "projects/mailroom-ml/report.html")
        page.emulate_media(media="print")
        for chart in page.locator(".chart-scroll").all():
            assert chart.evaluate("el => el.scrollWidth <= el.clientWidth + 1")
            expect(chart).to_have_css("overflow-x", "visible")
    finally:
        page.close()


@pytest.mark.parametrize("engine", ["firefox", "webkit"])
def test_mobile_report_charts_in_other_engines(site, playwright, engine):
    _, base = site
    browser = getattr(playwright, engine).launch()
    page = browser.new_page(viewport={"width": 375, "height": 812}, reduced_motion="reduce")
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(base + "projects/mailroom-ml/report.html")
        charts = page.locator(".chart-scroll")
        expect(charts).to_have_count(6)
        for chart in charts.all():
            image = chart.locator("img")
            image.scroll_into_view_if_needed()
            assert image.evaluate("img => img.decode().then(() => img.naturalWidth > 0)")
            assert chart.evaluate("el => el.scrollWidth > el.clientWidth")
            chart.focus()
            page.keyboard.press("ArrowRight")
            page.wait_for_function("el => el.scrollLeft > 0", arg=chart.element_handle())
        assert not errors
    finally:
        browser.close()


def test_no_script_and_print_from_dark(site, tmp_path):
    """Keep navigation usable without scripts and print the dark résumé legibly."""
    browser, base = site
    context = browser.new_context(java_script_enabled=False, viewport={"width": 375, "height": 812})
    page = context.new_page()
    page.goto(base + "projects/")
    expect(page.get_by_role("link", name="Neuron Atlas", exact=True)).to_be_visible()
    expect(page.locator(".theme-toggle")).to_be_hidden()
    expect(page.locator(".nav-link .key-hint")).to_be_hidden()
    expect(page.get_by_role("link", name="Search", exact=True)).not_to_have_attribute("aria-keyshortcuts")
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


CHART_PAGES = [
    "projects/natd.html", "projects/natd/report.html", "projects/mailroom-ml/report.html",
    "projects/mailroom-corpus-eda/report.html", "projects/rvl-cdip-classifier.html",
    "projects/mapreduce-reloaded.html", "projects/langtons-ant.html",
]


def test_chart_tooltip_hover_and_keyboard(site):
    browser, base = site
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    try:
        page.goto(base + "projects/natd.html")
        tip = page.locator(".chart-tooltip")
        first = page.locator(".chart .mark").first
        first.scroll_into_view_if_needed()
        first.hover()
        expect(tip).to_be_visible()
        expect(tip).to_contain_text("+14.5 pts")
        expect(tip).to_contain_text("Athena")
        page.mouse.move(0, 0)
        expect(tip).to_be_hidden()
        last = page.locator(".chart .mark").last
        last.focus()
        expect(tip).to_be_visible()
        expect(tip).to_contain_text("−3.6 pts")
        box, tip_box = last.bounding_box(), tip.bounding_box()
        assert 0 <= tip_box["x"] and tip_box["x"] + tip_box["width"] <= 1280
        page.keyboard.press("Escape")
        expect(tip).to_be_hidden()
        assert box["height"] >= 24
    finally:
        page.close()


def test_charts_dark_theme_and_no_script(site):
    browser, base = site
    page = browser.new_page(color_scheme="dark")
    try:
        page.goto(base + "projects/mapreduce-reloaded.html")
        expect(page.locator(".chart .bar.c1").first).to_have_css("fill", "rgb(42, 163, 176)")
        expect(page.locator(".chart text.cat").first).to_have_css("fill", "rgb(230, 237, 239)")
        # Value labels carry a halo in the surface color, so the reference line cannot cut through them.
        label = page.locator(".chart text.val").first
        expect(label).to_have_css("paint-order", "stroke")
        expect(label).to_have_css("stroke", "rgb(19, 28, 32)")
    finally:
        page.close()
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    try:
        for path in CHART_PAGES:
            page.goto(base + path)
            charts = page.locator("figure.chart svg")
            assert charts.count() >= 1, f"{path}: no chart without JavaScript"
            for chart in charts.all():
                expect(chart).to_be_visible()
                assert chart.bounding_box()["height"] > 60, path
            expect(page.locator(".chart-tooltip")).to_have_count(0)
    finally:
        context.close()


def test_charts_scroll_on_phone(site):
    browser, base = site
    page = browser.new_page(viewport={"width": 375, "height": 812}, reduced_motion="reduce")
    try:
        for path in CHART_PAGES:
            page.goto(base + path)
            for body in page.locator(".chart-body").all():
                compact = body.evaluate("el => el.querySelector('svg').viewBox.baseVal.width === 320")
                if compact:
                    assert body.evaluate("el => el.scrollWidth <= el.clientWidth + 1"), path
                else:
                    assert body.evaluate("el => el.scrollWidth > el.clientWidth"), path
                    body.focus()
                    page.keyboard.press("ArrowRight")
                    page.wait_for_function("el => el.scrollLeft > 0", arg=body.element_handle())
                outside = body.evaluate("""el => {
                    const svg = el.querySelector('svg').getBoundingClientRect();
                    return [...el.querySelectorAll('svg text')].filter(t => {
                        const b = t.getBoundingClientRect();
                        return b.left < svg.left - 1 || b.right > svg.right + 1 || b.top < svg.top - 1 || b.bottom > svg.bottom + 1;
                    }).map(t => t.textContent);
                }""")
                assert outside == [], f"{path}: text outside the chart: {outside}"
    finally:
        page.close()


def test_chart_tooltip_hides_on_sideways_scroll_and_stays_on_screen(site):
    browser, base = site
    page = browser.new_page(viewport={"width": 375, "height": 812}, reduced_motion="reduce")
    try:
        page.goto(base + "projects/natd.html")
        mark = page.locator("figure.chart g.mark").first
        mark.focus()
        tip = page.locator(".chart-tooltip")
        expect(tip).to_be_visible()
        box = tip.bounding_box()
        assert 0 <= box["y"] and box["y"] + box["height"] <= 812, box
        def follows_mark():
            if tip.is_hidden():
                return True
            t, m = tip.bounding_box(), mark.locator(".bar, .dot").first.bounding_box()
            return t["x"] < m["x"] + m["width"] and m["x"] < t["x"] + t["width"]
        body = page.locator(".chart-body").first
        body.evaluate("el => { el.scrollLeft = 80; }")
        page.wait_for_timeout(100)
        assert follows_mark(), "tooltip stays over its mark after a sideways scroll"
        body.evaluate("el => { el.scrollLeft = el.scrollWidth; }")
        page.wait_for_timeout(100)
        assert follows_mark(), "tooltip follows or hides when its mark scrolls away"
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(200)
        assert follows_mark(), "tooltip follows its mark on page scroll"
    finally:
        page.close()


@pytest.mark.parametrize("width", [375, 1280])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_search_type_filter_url_and_restoration(site, width, theme):
    """The new native filter preserves exact route subsets and shareable state."""
    browser, base = site
    page = browser.new_page(viewport={"width": width, "height": 900}, color_scheme=theme)
    try:
        page.goto(base + "search.html?q=calibration&type=report")
        control = page.get_by_label("Page type", exact=True)
        results = page.locator("#search-results a.result-title")
        expect(control).to_be_enabled()
        expect(control).to_have_value("report")
        expect(results).to_have_count(3)
        assert all(a.get_attribute("href").endswith("/report.html") for a in results.all())
        control.select_option("all")
        expect(results).to_have_count(11)
        original = [a.get_attribute("href") for a in results.all()]
        for kind, expected in (
            ("case-study", [u for u in original if re.fullmatch(r"projects/(?!index\.html)[^/]+\.html", u)]),
            ("appendix", [u for u in original if u.endswith("/appendix.html")]),
            ("report", [u for u in original if u.endswith("/report.html")]),
            ("other", [u for u in original if not u.startswith("projects/") or u == "projects/index.html"]),
        ):
            control.select_option(kind)
            expect(results).to_have_count(len(expected))
            assert [a.get_attribute("href") for a in results.all()] == expected
            assert page.evaluate("new URLSearchParams(location.search).get('type')") == kind
            expect(page.get_by_label("Search this site")).to_have_value("calibration")
        control.select_option("all")
        assert [a.get_attribute("href") for a in results.all()] == original
        assert page.evaluate("new URLSearchParams(location.search).has('type')") is False
        control.select_option("appendix")
        page.reload()
        expect(control).to_be_enabled()
        expect(control).to_have_value("appendix")
        expect(results).to_have_count(2)
        search = page.get_by_label("Search this site")
        search.fill("zzzznothing")
        expect(results).to_have_count(0)
        expect(page.locator("#search-status")).to_contain_text("in appendices")
        search.press("Escape")
        expect(search).to_have_value("")
        assert page.evaluate("new URLSearchParams(location.search).has('q')") is False
        page.goto(base + "search.html?q=calibration&type=unknown")
        expect(control).to_be_enabled()
        expect(control).to_have_value("all")
        expect(results).to_have_count(11)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.emulate_media(media="print")
        expect(page.locator("form.site-search")).to_be_hidden()
    finally:
        page.close()


def test_search_without_javascript_keeps_browse_fallback(site):
    """The disabled filter must not block the existing non-JavaScript browse path."""
    browser, base = site
    page = browser.new_page(java_script_enabled=False)
    try:
        page.goto(base + "search.html")
        expect(page.get_by_label("Page type", exact=True)).to_be_disabled()
        expect(page.locator("noscript p")).to_contain_text("Search needs JavaScript")
        page.get_by_role("link", name="projects index", exact=True).click()
        expect(page.get_by_role("heading", level=1)).to_have_text("Projects")
    finally:
        page.close()


@pytest.mark.parametrize("width", [375, 1280])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_numbered_research_sources_and_return_links(site, width, theme):
    """Native numbered notes retain sources and return navigation without overlays."""
    browser, base = site
    page = browser.new_page(viewport={"width": width, "height": 900}, color_scheme=theme, reduced_motion="reduce")
    try:
        page.goto(base + "projects/natd/report.html")
        refs = page.locator('a[role="doc-noteref"]')
        expect(refs).to_have_count(17)
        for i, ref in enumerate(refs.all(), 1):
            assert ref.inner_text() == str(i)
            note = page.locator(ref.get_attribute("href"))
            expect(note).to_have_count(1)
            assert note.locator('a[href^="https://"]').count() == 1
            expect(note.locator('a[href="#' + ref.get_attribute("id") + '"]')).to_have_count(1)
        first = refs.first
        first.focus()
        page.keyboard.press("Enter")
        expect(page).to_have_url(re.compile(r"#fn1$"))
        note = page.locator("#fn1")
        expect(note).to_be_in_viewport()
        note.locator('a[role="doc-backlink"]').click()
        expect(page).to_have_url(re.compile(r"#fnref1$"))
        expect(first).to_be_in_viewport()
        first.hover()
        expect(page.locator(".tippy-box")).to_have_count(0)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.emulate_media(media="print")
        expect(page.locator("#footnotes")).to_be_visible()
    finally:
        page.close()


def test_numbered_research_notes_work_without_javascript(site):
    browser, base = site
    page = browser.new_page(java_script_enabled=False)
    try:
        page.goto(base + "projects/natd/report.html")
        page.locator("#fnref17").click()
        expect(page).to_have_url(re.compile(r"#fn17$"))
        page.locator('#fn17 a[role="doc-backlink"]').click()
        expect(page).to_have_url(re.compile(r"#fnref17$"))
    finally:
        page.close()


@pytest.mark.parametrize("width,theme", [(375, "light"), (375, "dark"), (1280, "light"), (1280, "dark")])
def test_chart_source_round_trip_without_script(site, width, theme):
    """Evidence links must move keyboard focus and work without enhancement JS."""
    browser, base = site
    context = browser.new_context(viewport={"width": width, "height": 900}, color_scheme=theme, java_script_enabled=False)
    page = context.new_page()
    try:
        for path in CHART_PAGES:
            page.goto(base + path)
            for figure in page.locator("figure.chart").all():
                forward = figure.locator(".chart-tools a")
                table = page.locator(forward.get_attribute("href"))
                assert table.evaluate("el => el.tagName === 'TABLE'")
                forward.focus()
                page.keyboard.press("Enter")
                expect(table).to_be_focused()
                assert page.url.endswith(forward.get_attribute("href"))
                back = table.locator("xpath=following-sibling::p[1]").locator("a")
                caption = page.locator(back.get_attribute("href"))
                back.focus()
                page.keyboard.press("Enter")
                expect(caption).to_be_focused()
                expect(caption).to_have_text(figure.locator("figcaption").inner_text())
    finally:
        context.close()


@pytest.mark.parametrize("width,theme", [(375, "light"), (375, "dark"), (1280, "light"), (1280, "dark")])
def test_chart_evidence_linking_uses_every_source_row(site, width, theme):
    browser, base = site
    page = browser.new_page(viewport={"width": width, "height": 1000}, color_scheme=theme, reduced_motion="reduce")
    try:
        for path in CHART_PAGES:
            page.goto(base + path)
            for figure in page.locator("figure.chart").all():
                table = page.locator(figure.locator(".chart-tools a").get_attribute("href"))
                rows = table.locator("tbody tr")
                readout = figure.locator(".chart-readout")
                expect(readout).to_be_visible()
                for mark in figure.locator(".mark").all():
                    index = int(mark.get_attribute("data-source-row")) - 1
                    row = rows.nth(index)
                    cells = [" ".join(text.split()) for text in row.locator("td").all_text_contents()]
                    assert mark.get_attribute("data-tip-label").startswith(cells[0])
                    mark.focus()
                    expect(row).to_have_class(re.compile(r"\bis-linked\b"))
                    for text in cells:
                        expect(readout).to_contain_text(text)
                    assert row.evaluate("el => getComputedStyle(el).outlineWidth") == "2px"
                # Reverse direction: keyboard focus in the table selects all its marks,
                # including every replicate in a benchmark-strip panel.
                for index in range(rows.count()):
                    rows.nth(index).focus()
                    selected = figure.locator(".mark.is-linked")
                    assert selected.count() > 0
                    assert all(int(m.get_attribute("data-source-row")) == index + 1 for m in selected.all())
                page.emulate_media(media="print")
                expect(readout).to_be_hidden()
                expect(table).to_be_visible()
                expect(figure.locator("svg")).to_be_visible()
                page.emulate_media(media="screen")
    finally:
        page.close()


@pytest.mark.parametrize("width", [375, 414, 768, 1280])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_stacked_benchmark_caption_preserves_reading_width(site, width, theme):
    browser, base = site
    page = browser.new_page(viewport={"width": width, "height": 1000}, color_scheme=theme)
    try:
        page.goto(base + "projects/langtons-ant.html")
        table = page.locator("table.chart-source")
        caption = table.locator("caption")
        expect(caption).to_contain_text("These are not browser frame rates")
        assert caption.bounding_box()["width"] >= table.bounding_box()["width"] * .9
        if width <= 768:
            assert caption.bounding_box()["height"] < 180
        else:
            expect(caption).to_have_css("display", "table-caption")
        assert table.locator("tbody tr").count() == 2
    finally:
        page.close()


@pytest.mark.parametrize("width,theme", [(375, "light"), (375, "dark"), (1280, "light"), (1280, "dark")])
def test_mapreduce_duration_keeps_condition_and_source_context(site, width, theme):
    browser, base = site
    page = browser.new_page(viewport={"width": width, "height": 1100}, color_scheme=theme, reduced_motion="reduce")
    try:
        page.goto(base + "projects/mapreduce-reloaded.html")
        panel = page.locator("#mr-backup-duration")
        expect(panel).to_contain_text("three runs")
        expect(panel).to_contain_text("fixed setting order")
        expect(panel).to_contain_text("not drift-controlled")
        marks = panel.locator(".mark")
        expect(marks).to_have_count(2)
        assert [m.get_attribute("data-tip-value") for m in marks.all()] == ["17.58 s", "11.24 s"]
        if width == 375:
            for label in panel.locator('.chart text.val').all():
                box = label.bounding_box()
                assert box["x"] >= 0 and box["x"] + box["width"] <= width
            assert panel.locator('.chart-body').evaluate("el => el.scrollWidth <= el.clientWidth + 1")
        marks.last.focus()
        expect(panel.locator(".chart-readout")).to_contain_text("Backups on")
        expect(panel.locator(".chart-readout")).to_contain_text("11.24")
        expect(panel.locator(".chart-readout")).to_contain_text("Runs")
        citation = panel.locator('a[role="doc-noteref"]')
        citation.click()
        expect(page.locator("#fn1")).to_contain_text("4dd1ca4")
        assert page.locator('#fn1 a[href*="4dd1ca4045b2b9f49a63a8f6e757b20b6fb32387"]').count() == 2
    finally:
        page.close()


@pytest.mark.parametrize("width,theme", [(375, "light"), (375, "dark"), (1280, "light"), (1280, "dark")])
def test_mapreduce_interval_distinguishes_mean_bounds_and_zero(site, width, theme):
    browser, base = site
    page = browser.new_page(viewport={"width": width, "height": 1100}, color_scheme=theme, reduced_motion="reduce")
    try:
        page.goto(base + "projects/mapreduce-reloaded.html")
        panel = page.locator("#mr-backup-uncertainty")
        expect(panel).to_contain_text("ten interleaved pairs")
        expect(panel).to_contain_text("backups on minus off")
        expect(panel).to_contain_text("does not prove zero cost")
        plot = panel.locator("figure.chart")
        mark = plot.locator(".mark")
        expect(mark).to_have_count(1)
        assert mark.get_attribute("data-tip-value") == "−0.11 s; −0.38 s to +0.16 s"
        geometry = plot.evaluate("""el => {
            const line = el.querySelector('.interval-range'), dot = el.querySelector('.dot'), zero = el.querySelector('line.ref');
            return [Number(line.getAttribute('x1')), Number(dot.getAttribute('cx')), Number(zero.getAttribute('x1')), Number(line.getAttribute('x2'))];
        }""")
        assert geometry == sorted(geometry)
        mark.focus()
        for value in ("−0.11", "−0.38", "+0.16", "10"):
            expect(plot.locator(".chart-readout")).to_contain_text(value)
        page.emulate_media(media="print")
        expect(plot.locator("svg")).to_be_visible()
        expect(panel.locator("table")).to_be_visible()
        expect(plot.locator(".chart-readout")).to_be_hidden()
        page.emulate_media(media="screen", forced_colors="active")
        expect(plot.locator(".interval-range")).to_have_css("stroke-width", "2px")
    finally:
        page.close()


def test_mapreduce_evidence_audit_rejects_wrong_cpu_and_missing_measurement(site):
    """Review regression: apparently plausible plots cannot hide misstated context."""
    browser, base = site
    page = browser.new_page()
    audit = (ROOT / "autoresearch.audit.cjs").read_text()
    start = audit.index("function inspectMapReduceEvidence()")
    end = audit.index("// Exercise discovery", start)
    inspect = "() => { " + audit[start:end] + "; return inspectMapReduceEvidence(); }"
    try:
        page.goto(base + "projects/mapreduce-reloaded.html")
        assert page.evaluate(inspect) == []
        page.locator('#mr-backup-duration > p').first.evaluate("el => el.textContent = el.textContent.replace('0.2 CPU', '0.5 CPU')")
        assert "slow-worker duration with experiment limits" in page.evaluate(inspect)
        page.reload()
        page.locator('#mr-backup-uncertainty table tbody td').nth(1).evaluate("el => el.textContent = '--'")
        assert "paired effect interval across no change, with limits" in page.evaluate(inspect)
    finally:
        page.close()


def test_unavailable_script_does_not_advertise_search_shortcut(site):
    """A failed script download leaves an ordinary usable search link."""
    browser, base = site
    page = browser.new_page()
    try:
        page.route('**/assets/js/site.js*', lambda route: route.abort())
        page.goto(base + 'index.html')
        link = page.get_by_role('link', name='Search', exact=True)
        expect(link).not_to_have_attribute('aria-keyshortcuts')
        expect(link.locator('.key-hint')).to_be_hidden()
        link.click()
        expect(page).to_have_url(re.compile(r'search\.html$'))
    finally:
        page.close()
