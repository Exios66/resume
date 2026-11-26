// Check that every built page survives in-place browser translation.
// node scripts/hillclimb/translation-sweep.cjs [--engines chromium,firefox,webkit] [--widths 320,375,1280]
//   [--langs de,fr,es,zh,ar] [--pages a.html,b.html] [--shots page,page]
// Each page is loaded, translated with tests/browser/pseudo_translate.js (simulated: the same
// in-place text replacement real translators do, with language-shaped pseudo-text), then checked:
//   overflow   the page scrolls sideways
//   escape     an element sticks out of the viewport outside a sideways scroller
//   clipped    a control's or label's text is wider than its box
//   header     a header control is under 44px, or the title runs under Search or the toggle
//   copy       a code block's Copy button covers its first line
//   align      (Arabic) a paragraph's text does not start at its right edge
//   names      a project page's title changed, so a translate="no" name was translated
// Screenshots of the --shots pages (default: home, projects, a case study and a report) go to
// .hillclimb-shots/translation/ (gitignored) unless SHOT_OUT is set. SWEEP_DOCS checks another build, such as
// one extracted from main for a before/after comparison. Exit status 1 if any check fails.
const { chromium, firefox, webkit } = require('playwright');
const fs = require('fs');
const http = require('http');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const DOCS = process.env.SWEEP_DOCS ? path.resolve(process.env.SWEEP_DOCS) : path.join(ROOT, 'docs');
const OUT = process.env.SHOT_OUT || path.join(ROOT, '.hillclimb-shots', 'translation');
const SCRIPT = fs.readFileSync(path.join(ROOT, 'tests', 'browser', 'pseudo_translate.js'), 'utf8');
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2',
  '.mp4': 'video/mp4', '.webm': 'video/webm' };
const ENGINES = { chromium, firefox, webkit };

const opt = { engines: 'chromium,firefox,webkit', widths: '320,375,1280', langs: 'de,fr,es,zh,ar',
  shots: 'index.html,projects/index.html,projects/mapreduce-reloaded.html,projects/mailroom-ml/report.html' };
const args = process.argv.slice(2);
for (let i = 0; i < args.length; i++) opt[args[i].replace(/^--/, '')] = args[++i];
const list = value => value.split(',').map(s => s.trim()).filter(Boolean);
const pages = opt.pages ? list(opt.pages) : walk(DOCS).sort();
const shots = new Set(list(opt.shots));

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return entry.name === 'site_libs' ? [] : walk(full);
    return entry.name.endsWith('.html') ? [path.relative(DOCS, full).split(path.sep).join('/')] : [];
  });
}

const server = http.createServer((req, res) => {
  let url = '';
  try { url = decodeURIComponent(req.url.split('?')[0].split('#')[0]); } catch { /* malformed: answer 404 below */ }
  let file = url.startsWith('/resume/') ? path.join(DOCS, url.slice('/resume/'.length)) : '';
  if (file && file !== DOCS && !file.startsWith(DOCS + path.sep)) file = '';
  if (file && fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!file || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

/** Runs in the page after translation; returns a list of problems. */
function inspect(before) {
  const problems = [];
  const vw = document.documentElement.clientWidth;
  const visible = el => { const s = getComputedStyle(el); const r = el.getBoundingClientRect(); return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0; };
  const name = el => el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '') + ' "' + (el.textContent || '').trim().slice(0, 40) + '"';
  const scroller = el => { for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) { const o = getComputedStyle(p).overflowX; if (o !== 'visible') return p; } return null; };

  const over = document.documentElement.scrollWidth - vw;
  if (over > 0) problems.push(`overflow: page is ${over}px wider than the viewport`);

  let escapes = 0;
  for (const el of document.body.querySelectorAll('*')) {
    if (el.closest('svg, .visually-hidden, .sr-only, .skip-link, [hidden]') || !visible(el) || scroller(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.right > vw + 1 || r.left < -1) { if (escapes++ < 3) problems.push(`escape: ${name(el)} spans ${Math.round(r.left)}..${Math.round(r.right)} of ${vw}`); }
  }

  for (const el of document.querySelectorAll('.nav-link, .btn, .chip, .code-copy-button, .site-title, .pager-name, .project-jump a, .footer-links a, .kicker, h1, h2')) {
    if (!visible(el)) continue;
    if (el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).overflowX === 'visible' && !scroller(el)) {
      const text = document.createRange(); text.selectNodeContents(el);
      const t = text.getBoundingClientRect(); const r = el.getBoundingClientRect();
      if (t.right > r.right + 1 || t.left < r.left - 1) problems.push(`clipped: ${name(el)} text ${Math.round(t.width)}px in a ${Math.round(r.width)}px box`);
    }
  }

  const header = document.querySelector('.site-header');
  if (header) {
    const controls = [...header.querySelectorAll('.nav-list li')].filter(li => visible(li) && getComputedStyle(li).visibility !== 'hidden').map(li => li.querySelector('a, button')).filter(Boolean);
    for (const c of controls) { const r = c.getBoundingClientRect(); if (r.height < 44 || r.width < 40) problems.push(`header: ${name(c)} is ${Math.round(r.width)}x${Math.round(r.height)}`); }
    const title = document.querySelector('.site-title');
    const range = document.createRange(); range.selectNodeContents(title);
    for (const t of range.getClientRects()) {
      for (const c of controls) {
        const r = c.getBoundingClientRect();
        if (t.right > r.left + 1 && t.left < r.right - 1 && t.bottom > r.top + 1 && t.top < r.bottom - 1) problems.push(`header: title text overlaps ${name(c)}`);
      }
    }
  }

  for (const block of document.querySelectorAll('div.code-copy-outer-scaffold')) {
    const button = block.querySelector('.code-copy-button'); const code = block.querySelector('code');
    if (!button || !code || !visible(button)) continue;
    const b = button.getBoundingClientRect();
    const walker = document.createTreeWalker(code, NodeFilter.SHOW_TEXT);
    let hit = false;
    while (walker.nextNode() && !hit) {
      const r = document.createRange(); r.selectNodeContents(walker.currentNode);
      for (const line of r.getClientRects()) if (line.width && line.right > b.left && line.left < b.right && line.bottom > b.top && line.top < b.bottom) hit = true;
    }
    if (hit) problems.push(`copy: the Copy button (${Math.round(b.width)}px) covers code text`);
  }

  if (document.documentElement.lang === 'ar') {
    let off = 0;
    for (const p of document.querySelectorAll('main p')) {
      if (!visible(p) || p.closest('[translate="no"], .chart-tools, .contact, .actions') || !/[؀-ۿ]/.test(p.textContent.trim().charAt(0) + p.textContent.trim().slice(0, 12))) continue;
      const s = getComputedStyle(p); if (s.textAlign === 'center' || s.display !== 'block') continue;
      // Rows of tags, buttons or arrow links start with a box, which gives no direction; the layout is not mirrored.
      const lead = [...p.childNodes].find(n => n.nodeType === 1 || n.data.trim());
      if (lead && lead.nodeType === 1 && getComputedStyle(lead).display !== 'inline') continue;
      const range = document.createRange(); range.selectNodeContents(p);
      // Right-to-left text boxes come in logical order, so the first line is every box at the first box's height.
      const boxes = [...range.getClientRects()].filter(x => x.width); const r = p.getBoundingClientRect();
      if (!boxes.length) continue;
      const lineRight = Math.max(...boxes.filter(x => Math.abs(x.top - boxes[0].top) < 2).map(x => x.right));
      if (Math.abs(r.right - parseFloat(s.paddingRight) - parseFloat(s.borderRightWidth) - lineRight) > 3) { if (off++ < 2) problems.push(`align: ${name(p)} does not start at its right edge`); }
    }
  }

  const h1 = document.querySelector('h1.page-title');
  if (before && h1 && h1.textContent.trim() !== before) problems.push(`names: title "${before}" became "${h1.textContent.trim()}"`);
  return problems;
}

server.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${server.address().port}/resume/`;
  let failures = 0, loads = 0;
  try {
    for (const engine of list(opt.engines)) {
      const browser = await ENGINES[engine].launch();
      for (const width of list(opt.widths).map(Number)) {
        const ctx = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
        await ctx.addInitScript(SCRIPT);
        const page = await ctx.newPage();
        for (const lang of list(opt.langs)) {
          for (const rel of pages) {
            await page.goto(base + rel, { waitUntil: 'load' });
            await page.evaluate(() => document.fonts.ready);
            // A thesis title and Langton's Ant have names in other languages, so they translate.
            const project = /^projects\/[^/]+\.html$/.test(rel) && !/\/(index|natd|langtons-ant)\.html$/.test(rel);
            const before = project ? await page.evaluate(() => (document.querySelector('h1.page-title') || {}).textContent?.trim() || null) : null;
            await page.evaluate(l => window.pseudoTranslate(l), lang);
            await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
            const problems = await page.evaluate(inspect, before);
            loads++;
            if (problems.length) { failures++; console.log(`FAIL ${engine} ${width} ${lang} ${rel}\n  ${problems.join('\n  ')}`); }
            if ((problems.length || shots.has(rel)) && engine === 'chromium' && width !== 320) {
              fs.mkdirSync(OUT, { recursive: true });
              await page.screenshot({ path: path.join(OUT, `${lang}-${width}-${rel.replace(/\//g, '_').replace(/\.html$/, '')}.png`), fullPage: !problems.length && width === 375 ? false : true });
            }
          }
        }
        await ctx.close();
      }
      await browser.close();
    }
  } finally {
    server.close();
  }
  console.log(`${loads} translated page views, ${failures} with problems`);
  process.exitCode = failures ? 1 : 0;
});
