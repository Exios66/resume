"""Validate generated output at a dev root and a GitHub Pages project prefix."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from threading import Thread
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen

import pytest

import test_links as checks

DOCS = checks.DOCS


def test_no_local_build_dependencies_are_published():
    """The built artifact must exclude local packages, environments and review data."""
    forbidden = {'node_modules', '.venv', '.autoresearch-tools', '.autoresearch'}
    assert not [str(p.relative_to(DOCS)) for p in DOCS.rglob('*')
                if forbidden.intersection(p.relative_to(DOCS).parts)]


@pytest.fixture(scope='module', params=['/', '/resume/'], ids=['dev-root', 'pages-project'])
def deployment(request):
    """Serve the real build, with Pages-style custom 404 responses under /resume/."""
    prefix = request.param

    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self, path):
            if prefix != '/':
                if not urlsplit(path).path.startswith(prefix):
                    return str(DOCS / '__outside_project__')
                path = path[len(prefix) - 1:]
            return super().translate_path(path)

        def send_error(self, code, message=None, explain=None):
            if code != 404 or prefix == '/':
                return super().send_error(code, message, explain)
            body = (DOCS / '404.html').read_bytes()
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=DOCS))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}{prefix}', prefix
    server.shutdown()
    server.server_close()
    thread.join()


def test_local_assets_links_and_directory_indexes_resolve(deployment):
    """HTTP-test every locally referenced resource, including nested-page relatives."""
    base, prefix = deployment
    urls = {base, base + 'projects/', base + 'writing/'}
    for path in checks.site_files(include_libs=False):
        if prefix == '/' and path.name == '404.html':
            # The 404 intentionally uses absolute /resume/ links for unknown depths.
            continue
        page_url = urljoin(base, path.relative_to(DOCS).as_posix())
        urls.add(page_url)
        for tag, attrs, _ in checks.parse(path):
            for key in ('src', 'href'):
                link = checks.attr(attrs, key)
                if not link:
                    continue
                url = urljoin(page_url, link).split('#')[0]
                if urlsplit(url).netloc == urlsplit(base).netloc:
                    urls.add(url)
    for url in sorted(urls):
        with urlopen(url, timeout=10) as response:
            assert response.status == 200, url


@pytest.mark.skipif(os.environ.get('RUN_BROWSER_TESTS') != '1', reason='Opt-in Chromium deployment checks')
@pytest.mark.parametrize('width', [375, 768, 1280])
@pytest.mark.parametrize('theme', ['light', 'dark'])
def test_navigation_search_theme_chart_and_pdf_on_deployment(deployment, width, theme):
    """Exercise critical controls against both deployment layouts with real Chromium."""
    from playwright.sync_api import expect, sync_playwright

    base, prefix = deployment
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width': width, 'height': 900},
                                      color_scheme=theme, reduced_motion='reduce')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('requestfailed', lambda request: errors.append(request.url))
        page.on('response', lambda response: errors.append(response.url)
                if response.status >= 400 and not response.url.endswith('/missing/deep/page.html') else None)
        try:
            page.goto(base)
            assert page.locator('link[rel="canonical"]').get_attribute('href') == 'https://exios66.github.io/resume/'
            page.get_by_role('button', name=f'Switch to {"dark" if theme == "light" else "light"} theme').click()
            chosen = 'dark' if theme == 'light' else 'light'
            expect(page.locator('html')).to_have_attribute('data-theme', chosen)
            page.get_by_role('link', name='Search', exact=True).click()
            expect(page).to_have_url(base + 'search.html')
            expect(page.locator('html')).to_have_attribute('data-theme', chosen)
            page.locator('#site-search-input').fill('calibration')
            expect(page.locator('#search-status')).to_contain_text('pages match')
            assert page.locator('#search-results a').first.get_attribute('href')
            page.goto(base + 'projects/natd.html')
            chart = page.locator('.chart-body').first
            chart.focus()
            if chart.evaluate('el => el.scrollWidth > el.clientWidth'):
                page.keyboard.press('ArrowRight')
                page.wait_for_function('el => el.scrollLeft > 0', arg=chart.element_handle())
            chart.locator('.mark').first.focus()
            expect(page.locator('.chart-tooltip')).to_be_visible()
            page.keyboard.press('Escape')
            expect(page.locator('.chart-tooltip')).to_be_hidden()
            pdf = context.request.get(base + 'assets/Jack_Burleson_Resume.pdf')
            assert pdf.status == 200 and pdf.headers['content-type'].startswith('application/pdf')
            assert pdf.body().startswith(b'%PDF-')
            if prefix != '/':
                response = page.goto(base + 'projects/mailroom-ml/missing/deep/page.html')
                assert response.status == 404
                expect(page.get_by_role('heading', name='Page not found')).to_be_visible()
                for link in page.locator('main a').all():
                    assert link.evaluate('el => el.href').startswith(base)
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
            assert errors == []
        finally:
            context.close()
            browser.close()
