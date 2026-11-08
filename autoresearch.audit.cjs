// Polish audit for the rendered site in docs/. Prints METRIC lines; lower polish_defects is better.
// Usage: node autoresearch.audit.cjs   (AXE_PATH, SHOT_DIR and AUDIT_LIST are optional env vars)
// AUDIT_LIST=<file> writes one line per scored finding (width, theme, page, kind, where); scores are unchanged.
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
const LIST = process.env.AUDIT_LIST || '';
const listed = [];
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
    let url;
    try { url = decodeURIComponent(req.url.split('?')[0].split('#')[0]); } catch { res.writeHead(400); return res.end(); }
    let file = url.startsWith('/resume/') ? path.join(DOCS, url.slice('/resume/'.length)) : '';
    if (!file || (file !== DOCS && !file.startsWith(DOCS + path.sep))) { res.writeHead(404); return res.end(); }
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
    tableOverflow: 0, invisibleFocusable: [], headingSkips: 0, h1: 0, brokenImages: 0,
    sepStart: 0, sepEnd: 0, headingWidows: 0, where: { crushed: [], tables: [], sepStart: [], sepEnd: [], widows: [] } };
  const visible = el => { const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0; };
  const sig = el => { const parts = []; while (el && el.nodeType === 1 && parts.length < 3) {
    parts.unshift(el.tagName.toLowerCase() + (el.classList.length ? '.' + [...el.classList].slice(0, 2).join('.') : ''));
    el = el.parentElement; } return parts.join('>'); };
  // Line boxes of an element's own text: element boxes (padded inline code, icons) are ignored, and
  // fragments whose vertical centres are within 6px share a line even when their fonts differ.
  const lineCount = el => {
    const mids = []; const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let n = tw.nextNode(); n; n = tw.nextNode()) {
      if (!n.textContent.trim()) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const q of rg.getClientRects()) if (q.width > 0) mids.push(q.top + q.height / 2);
    }
    mids.sort((a, b) => a - b); let lines = 0, last = -1e9;
    for (const m of mids) { if (m - last > 6) lines++; last = m; }
    return lines;
  };
  const focusables = 'a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"])';
  for (const el of document.querySelectorAll(focusables)) {
    const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (s.display === 'none' || s.visibility === 'hidden' || el.closest('[hidden], [aria-hidden="true"]')) continue;
    if (el.matches('.skip-link, .visually-hidden, .sr-only, a[href="#main"]')) continue;
    if (r.width > 0 && r.height > 0 && (r.width < 8 || r.height < 8)) out.invisibleFocusable.push(sig(el));
    if (!mobile || r.width === 0) continue;
    const inline = el.tagName === 'A' && s.display === 'inline' && el.closest('p, li, td, th, figcaption, dd, dt, blockquote');
    // A link whose ::after is an absolute overlay (a stretched card link) is as big as the box it covers.
    const after = getComputedStyle(el, '::after');
    const hit = after.content !== 'none' && after.position === 'absolute' && el.offsetParent
      ? el.offsetParent.getBoundingClientRect() : r;
    if (!inline && (hit.width < 24 || hit.height < 24) && el.closest('svg') === null) out.tap.push(sig(el));
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
      if (t.scrollWidth > t.clientWidth + 1 || t.getBoundingClientRect().right > vw + 1) { out.tableOverflow++; out.where.tables.push(sig(t) + ' | ' + [...(t.rows[0] || { cells: [] }).cells].map(c => c.textContent.trim()).join(' | ').slice(0, 100)); }
      for (const cell of t.querySelectorAll('td, th')) {
        const text = cell.textContent.trim(); if (!text) continue;
        // Count the text's own line boxes, not the row height that a taller neighbour sets.
        const lines = lineCount(cell);
        const words = text.split(/\s+/).length;
        const clipped = [...cell.querySelectorAll('code')].some(c => c.getBoundingClientRect().right > cell.getBoundingClientRect().right + 1);
        if (lines > words + 1 || clipped) { out.crushed++; out.where.crushed.push((clipped ? 'clipped ' : '') + lines + ' lines | ' + text.slice(0, 80)); }
      }
    }
  }
  // Typography. Separators (• ·) that start or end a wrapped line, and headings whose last line is one word.
  const charRect = (node, i) => { const rg = document.createRange(); rg.setStart(node, i); rg.setEnd(node, i + 1);
    return rg.getClientRects()[0]; };
  // A character outside the box of an ancestor that clips its overflow is not seen.
  const clipped = (el, q) => { for (let a = el; a && a !== document.body; a = a.parentElement) {
    if (getComputedStyle(a).overflowX === 'visible') continue; const b = a.getBoundingClientRect();
    if (q.right <= b.left + 0.5 || q.left >= b.right - 0.5) return true; } return false; };
  const sameLine = (a, b) => a && b && Math.abs((a.top + a.height / 2) - (b.top + b.height / 2)) <= 6;
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const chars = [];
  for (let n = tw.nextNode(); n; n = tw.nextNode()) {
    const el = n.parentElement; if (!el || el.closest('svg, script, style, pre, .visually-hidden, .sr-only') || !visible(el)) continue;
    if (/[•·]/.test(n.textContent)) chars.push(n);
  }
  for (const n of chars) {
    const block = n.parentElement.closest('p, li, h1, h2, h3, h4, dd, dt, figcaption, td, th, div, span.role, nav') || n.parentElement;
    // Every visible character of the block in order, so neighbours across inline elements are found.
    const seq = []; const bw = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
    for (let m = bw.nextNode(); m; m = bw.nextNode()) for (let i = 0; i < m.textContent.length; i++)
      if (m.textContent[i].trim()) seq.push([m, i]);
    seq.forEach(([m, i], k) => {
      if (m !== n || !/[•·]/.test(m.textContent[i])) return;
      const here = charRect(m, i); if (!here || !here.width || clipped(m.parentElement, here)) return;
      const before = k > 0 ? charRect(...seq[k - 1]) : null;
      const after = k < seq.length - 1 ? charRect(...seq[k + 1]) : null;
      if (before && !sameLine(before, here)) { out.sepStart++; out.where.sepStart.push(sig(block) + ' | ' + block.textContent.trim().slice(0, 80)); }
      else if (after && !sameLine(after, here)) { out.sepEnd++; out.where.sepEnd.push(sig(block) + ' | ' + block.textContent.trim().slice(0, 80)); }
    });
  }
  for (const h of document.querySelectorAll('h1, h2, h3')) {
    if (!visible(h)) continue;
    const words = []; const hw = document.createTreeWalker(h, NodeFilter.SHOW_TEXT);
    for (let m = hw.nextNode(); m; m = hw.nextNode()) {
      if (m.parentElement.closest('svg, .visually-hidden')) continue;
      const re = /\S+/g; let w; while ((w = re.exec(m.textContent))) {
        const rg = document.createRange(); rg.setStart(m, w.index); rg.setEnd(m, w.index + w[0].length);
        const q = [...rg.getClientRects()].pop(); if (q && q.width) words.push(q);
      }
    }
    if (words.length >= 3 && !sameLine(words[words.length - 1], words[words.length - 2])) { out.headingWidows++; out.where.widows.push(h.tagName.toLowerCase() + ' | ' + h.textContent.trim().slice(0, 80)); }
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
  const combos = [{ w: 375, theme: 'light', mobile: true }, { w: 375, theme: 'dark', mobile: true },
    { w: 1280, theme: 'light' }, { w: 1280, theme: 'dark' }, { w: 320, theme: 'light', mobile: true, layoutOnly: true }];
  const totals = { axe: 0, layout: 0, errors: 0, structure: 0, type: 0, axeIds: {}, details: {} };
  const add = (bucket, key, pts) => { totals[bucket] += pts; totals.details[key] = (totals.details[key] || 0) + pts; };
  const note = (c, p, kind, items) => { if (LIST) for (const i of items) listed.push([c.w, c.theme, p, kind, i].join('\t')); };
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
        for (const v of violations) { const pts = v.n * (IMPACT[v.impact] || 1); add('axe', 'axe:' + v.id, pts); note(c, p, 'axe', [v.id + ' x' + v.n]);
          totals.axeIds[v.id] = (totals.axeIds[v.id] || 0) + v.n; }
      }
      const r = await page.evaluate(inspect, !!c.mobile);
      if (r.pageOverflow) { add('layout', 'page overflow', 20); note(c, p, 'page overflow', ['']); }
      if (c.mobile) {
        add('layout', 'crushed table cells', 2 * r.crushed);
        add('layout', 'tables wider than screen', r.tableOverflow);
        note(c, p, 'crushed cell', r.where.crushed); note(c, p, 'wide table', r.where.tables);
        if (!c.layoutOnly) { add('layout', 'tap targets < 24px', r.tap.length); add('layout', 'text < 12px', r.tiny.length);
          note(c, p, 'small tap target', r.tap); note(c, p, 'text < 12px', r.tiny); }
      }
      if (!c.layoutOnly) { add('layout', 'invisible focusable controls', 5 * r.invisibleFocusable.length);
        note(c, p, 'invisible focusable', r.invisibleFocusable); }
      if (c.w === 1280 && c.theme === 'light') {
        add('structure', 'heading level skips', 2 * r.headingSkips);
        if (r.h1 !== 1) { add('structure', 'pages without exactly one h1', 2); note(c, p, 'h1 count', [String(r.h1)]); }
        if (r.headingSkips) note(c, p, 'heading skip', [String(r.headingSkips)]);
      }
      if (c.theme === 'light' && !c.layoutOnly) {
        add('type', 'separator starts a line', 2 * r.sepStart);
        add('type', 'separator ends a line', r.sepEnd);
        add('type', 'heading ends with a one-word line', r.headingWidows);
        note(c, p, 'separator starts line', r.where.sepStart); note(c, p, 'separator ends line', r.where.sepEnd);
        note(c, p, 'heading widow', r.where.widows);
      }
      add('errors', 'broken images', 10 * r.brokenImages);
      add('errors', 'console or network errors', 10 * errs.size);
      if (r.brokenImages) note(c, p, 'broken image', [String(r.brokenImages)]); note(c, p, 'error', [...errs]);
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
  for (const [k, w] of lintFound) { totals.details['lint: ' + k] = w; if (LIST) listed.push(['-', '-', '-', 'lint', k].join('\t')); }
  if (LIST) fs.writeFileSync(LIST, listed.sort().join('\n') + (listed.length ? '\n' : ''));
  const total = totals.axe + totals.layout + totals.errors + totals.structure + totals.type + lintPts;
  console.error(JSON.stringify({ details: totals.details, axeIds: totals.axeIds }, null, 1));
  const css = fs.statSync(path.join(DOCS, 'styles.css')).size;
  console.log(`METRIC polish_defects=${total}`);
  console.log(`METRIC axe_points=${totals.axe}`);
  console.log(`METRIC layout_points=${totals.layout}`);
  console.log(`METRIC error_points=${totals.errors}`);
  console.log(`METRIC structure_points=${totals.structure}`);
  console.log(`METRIC lint_points=${lintPts}`);
  console.log(`METRIC type_points=${totals.type}`);
  console.log(`METRIC pages=${PAGES.length}`);
  console.log(`METRIC css_kb=${(css / 1024).toFixed(1)}`);
  console.log(`METRIC audit_s=${((Date.now() - t0) / 1000).toFixed(1)}`);
})().catch(e => { console.error(e); process.exit(1); });
