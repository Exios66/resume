"""Opt-in, real Chromium checks of the rendered site; serves it under a subpath.

pip install playwright pytest pypdf && playwright install chromium
RUN_BROWSER_TESTS=1 python -m pytest -q tests/test_browser.py
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

ROOT = Path(__file__).resolve().parents[1]
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
