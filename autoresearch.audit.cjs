// Polish audit for the rendered site in docs/. Prints METRIC lines; lower polish_defects is better.
// Usage: node autoresearch.audit.cjs   (AXE_PATH and SHOT_DIR are optional env vars)
// Every check measures something a visitor sees or a keyboard or screen-reader user meets.
// Weights favour defects that block reading or access over cosmetic ones.
const { chromium } = require('playwright');
const fs = require('fs');
const http = require('http');
const path = require('path');

const ROOT = __dirname;
const DOCS = path.join(ROOT, 'docs');
const AXE = fs.readFileSync(process.env.AXE_PATH || require.resolve('axe-core/axe.min.js'), 'utf8');
const SHOT_DIR = process.env.SHOT_DIR || '';
const IMPACT = { critical: 10, serious: 5, moderate: 2, minor: 1 };

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) return e.name === 'site_libs' ? [] : walk(p);
    return e.name.endsWith('.html') ? [path.relative(DOCS, p).split(path.sep).join('/')] : [];
  });
}
const PAGES = walk(DOCS).sort();

const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2',
  '.pdf': 'application/pdf', '.txt': 'text/plain', '.xml': 'application/xml' };
function serve() {
  const server = http.createServer((req, res) => {
    // Serve docs/ at /resume/, the path GitHub Pages publishes it under, so pages that
    // link absolutely to the site path (404.html must) load as they do in production.
    const url = decodeURIComponent(req.url.split('?')[0].split('#')[0]);
    let file = url.startsWith('/resume/') ? path.join(DOCS, url.slice('/resume/'.length)) : '';
    if (!file || !file.startsWith(DOCS)) { res.writeHead(404); return res.end(); }
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (!fs.existsSync(file)) { res.writeHead(404); return res.end('not found'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(r => server.listen(0, '127.0.0.1', () => r(server)));
}

// Runs inside the page. Returns layout and interaction findings for one viewport.
function inspect(mobile) {
  const vw = document.documentElement.clientWidth;
  const out = { pageOverflow: document.documentElement.scrollWidth > vw + 1, tap: [], tiny: [], crushed: 0,
    tableOverflow: 0, invisibleFocusable: [], headingSkips: 0, h1: 0, brokenImages: 0 };
  const visible = el => { const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0; };
  const sig = el => { const parts = []; while (el && el.nodeType === 1 && parts.length < 3) {
    parts.unshift(el.tagName.toLowerCase() + (el.classList.length ? '.' + [...el.classList].slice(0, 2).join('.') : ''));
    el = el.parentElement; } return parts.join('>'); };
  const focusables = 'a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"])';
  for (const el of document.querySelectorAll(focusables)) {
    const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (s.display === 'none' || s.visibility === 'hidden' || el.closest('[hidden], [aria-hidden="true"]')) continue;
    if (el.matches('.skip-link, .visually-hidden, .sr-only, a[href="#main"]')) continue;
    if (r.width > 0 && r.height > 0 && (r.width < 8 || r.height < 8)) out.invisibleFocusable.push(sig(el));
    if (!mobile || r.width === 0) continue;
    const inline = el.tagName === 'A' && s.display === 'inline' && el.closest('p, li, td, th, figcaption, dd, dt, blockquote');
    if (!inline && (r.width < 24 || r.height < 24) && el.closest('svg') === null) out.tap.push(sig(el));
  }
  if (mobile) {
    const seen = new Set();
    for (const el of document.querySelectorAll('body *')) {
      if (el.closest('svg, .visually-hidden, .sr-only')) continue;
      const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
      if (!own || !visible(el)) continue;
      const fs_ = parseFloat(getComputedStyle(el).fontSize);
      const key = sig(el) + '@' + fs_;
      if (fs_ < 12 && !seen.has(key)) { seen.add(key); out.tiny.push(key); }
    }
    for (const t of document.querySelectorAll('main table')) {
      if (!visible(t)) continue;
      if (t.scrollWidth > t.clientWidth + 1 || t.getBoundingClientRect().right > vw + 1) out.tableOverflow++;
      for (const cell of t.querySelectorAll('td, th')) {
        const text = cell.textContent.trim(); if (!text) continue;
        // Count the text's own line boxes, not the row height that a taller neighbour sets.
        const range = document.createRange(); range.selectNodeContents(cell);
        const lines = new Set([...range.getClientRects()].filter(q => q.width > 0).map(q => Math.round(q.bottom))).size;
        const words = text.split(/\s+/).length;
        const clipped = [...cell.querySelectorAll('code')].some(c => c.getBoundingClientRect().right > cell.getBoundingClientRect().right + 1);
        if (lines > words + 1 || clipped) out.crushed++;
      }
    }
  }
  let prev = 0;
  for (const h of document.querySelectorAll('h1, h2, h3, h4, h5, h6')) {
    const l = +h.tagName[1]; if (prev && l > prev + 1) out.headingSkips++; prev = l; }
  out.h1 = document.querySelectorAll('h1, [role="heading"][aria-level="1"]').length;
  for (const img of document.images) if (img.complete && img.naturalWidth === 0) out.brokenImages++;
  return out;
}

function lints() {
  const found = [];
  const read = p => fs.existsSync(path.join(DOCS, p)) ? fs.readFileSync(path.join(DOCS, p), 'utf8') : '';
  if (!fs.existsSync(path.join(DOCS, '404.html'))) found.push(['no custom 404 page', 10]);
  const resume = read('resume.html');
  const contact = (resume.match(/<div class="contact"[\s\S]*?<\/div>/) || [''])[0];
  if (/>\s*Portfolio\s*</.test(contact)) found.push(['résumé contact link text hides its URL', 3]);
  if (!/href="https:\/\/github\.com\/Exios66\/?"/.test(contact)) found.push(['résumé contact lacks GitHub profile', 3]);
  if (/>mailroom-ml(\u2060|<)/.test(resume)) found.push(['résumé spells Mailroom-ML in lower case', 1]);
  if (/Open to Relocation/.test(resume)) found.push(['inconsistent "Open to Relocation" capitalisation', 1]);
  const index = read('search-index.json');
  if (/ — Jack J\. Burleson"/.test(index)) found.push(['search results repeat the site name', 3]);
  return found;
}

(async () => {
  const t0 = Date.now();
  const server = await serve();
  const base = `http://127.0.0.1:${server.address().port}/resume/`;
  const browser = await chromium.launch();
  const combos = [{ w: 375, theme: 'light', mobile: true }, { w: 375, theme: 'dark' },
    { w: 1280, theme: 'light' }, { w: 1280, theme: 'dark' }, { w: 320, theme: 'light', mobile: true, layoutOnly: true }];
  const totals = { axe: 0, layout: 0, errors: 0, structure: 0, axeIds: {}, details: {} };
  const add = (bucket, key, pts) => { totals[bucket] += pts; totals.details[key] = (totals.details[key] || 0) + pts; };
  await Promise.all(combos.map(async c => {
    const ctx = await browser.newContext({ viewport: { width: c.w, height: 900 }, colorScheme: c.theme, reducedMotion: 'reduce' });
    for (const p of PAGES) {
      const page = await ctx.newPage();
      const errs = new Set();
      page.on('pageerror', e => errs.add('pageerror ' + e.message));
      page.on('console', m => { if (m.type() === 'error') errs.add('console ' + m.text()); });
      page.on('requestfailed', r => errs.add('failed ' + r.url()));
      page.on('response', r => { if (r.status() >= 400 && !p.startsWith('404')) errs.add(r.status() + ' ' + r.url()); });
      await page.goto(base + p, { waitUntil: 'load' });
      await page.waitForTimeout(150);
      if (!c.layoutOnly) {
        await page.addScriptTag({ content: AXE });
        const violations = await page.evaluate(async () => (await axe.run(document, { runOnly: { type: 'tag',
          values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } })).violations
          .map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length })));
        for (const v of violations) { const pts = v.n * (IMPACT[v.impact] || 1); add('axe', 'axe:' + v.id, pts);
          totals.axeIds[v.id] = (totals.axeIds[v.id] || 0) + v.n; }
      }
      const r = await page.evaluate(inspect, !!c.mobile);
      if (r.pageOverflow) add('layout', 'page overflow', 20);
      if (c.mobile) {
        add('layout', 'crushed table cells', 2 * r.crushed);
        add('layout', 'tables wider than screen', r.tableOverflow);
        if (!c.layoutOnly) { add('layout', 'tap targets < 24px', r.tap.length); add('layout', 'text < 12px', r.tiny.length); }
      }
      if (!c.layoutOnly) add('layout', 'invisible focusable controls', 5 * r.invisibleFocusable.length);
      if (c.w === 1280 && c.theme === 'light') {
        add('structure', 'heading level skips', 2 * r.headingSkips);
        if (r.h1 !== 1) add('structure', 'pages without exactly one h1', 2);
      }
      add('errors', 'broken images', 10 * r.brokenImages);
      add('errors', 'console or network errors', 10 * errs.size);
      if (SHOT_DIR && !c.layoutOnly && c.theme === 'light') {
        fs.mkdirSync(SHOT_DIR, { recursive: true });
        await page.screenshot({ path: path.join(SHOT_DIR, `${p.replace(/\//g, '__').replace('.html', '')}_${c.w}.png`), fullPage: true });
      }
      await page.close();
    }
    await ctx.close();
  }));
  await browser.close();
  server.close();
  const lintFound = lints();
  const lintPts = lintFound.reduce((s, [, w]) => s + w, 0);
  for (const [k, w] of lintFound) totals.details['lint: ' + k] = w;
  const total = totals.axe + totals.layout + totals.errors + totals.structure + lintPts;
  console.error(JSON.stringify({ details: totals.details, axeIds: totals.axeIds }, null, 1));
  const css = fs.statSync(path.join(DOCS, 'styles.css')).size;
  console.log(`METRIC polish_defects=${total}`);
  console.log(`METRIC axe_points=${totals.axe}`);
  console.log(`METRIC layout_points=${totals.layout}`);
  console.log(`METRIC error_points=${totals.errors}`);
  console.log(`METRIC structure_points=${totals.structure}`);
  console.log(`METRIC lint_points=${lintPts}`);
  console.log(`METRIC pages=${PAGES.length}`);
  console.log(`METRIC css_kb=${(css / 1024).toFixed(1)}`);
  console.log(`METRIC audit_s=${((Date.now() - t0) / 1000).toFixed(1)}`);
})().catch(e => { console.error(e); process.exit(1); });
