// Discovery probes: measure weak points the fixed audit does not score, so the loop can find new work.
// node scripts/hillclimb/probes.cjs [--pages a.html,b.html] [--out file.json] [--append autoresearch.probes.jsonl]
//
// Probes are evidence for choosing experiments (scripts/hillclimb/priorities.py), never a keep metric:
// a probe only becomes a scored metric through a new segment (see .10x/metrics.md, "Adaptive priorities").
// Each probe returns a count (lower is better) and up to five examples. Pages are served at /resume/.
//
//   focus_unseen     focusable controls whose keyboard focus changes nothing visible (outline, ring, colour)
//   tap_near_miss    phone (375 px) controls outside running text that pass 24 px but miss the 44 px guideline
//   layout_shift     pages whose cumulative layout shift at 375 px exceeds 0.05 after load and fonts
//   motion_reduced   animations still running under prefers-reduced-motion: reduce
//   centered_prose   centred text blocks of more than three lines (hard to read) at 375 and 1280 px
//   measure          paragraphs in main longer than 90 or shorter than 30 characters per line at 1280 px
//   row_misalign     cards in one grid row whose titles start at different heights (1280 px)
//   cover_empty      card cover drawings that fill under 55% of their panel's width (1280 px)
//   svg_contrast     SVG text below 4.5:1 against the colour behind it (light and dark, 1280 px)
//   type_sprawl      distinct font sizes used for visible text, site-wide (a type scale has about eight)
//   colour_sprawl    distinct text colours, site-wide per theme
const { chromium } = require('playwright');
const fs = require('fs');
const http = require('http');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const DOCS = path.join(ROOT, 'docs');
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2',
  '.pdf': 'application/pdf', '.mp4': 'video/mp4' };

const opt = {};
const args = process.argv.slice(2);
for (let i = 0; i < args.length; i++) opt[args[i].replace(/^--/, '')] = args[++i];

function pages() {
  if (opt.pages) return opt.pages.split(',');
  const out = [];
  (function walk(dir) {
    for (const name of fs.readdirSync(dir)) {
      const full = path.join(dir, name);
      if (fs.statSync(full).isDirectory()) { if (name !== 'site_libs') walk(full); }
      else if (name.endsWith('.html')) out.push(path.relative(DOCS, full).split(path.sep).join('/'));
    }
  })(DOCS);
  return out.sort();
}

function serve() {
  return http.createServer((req, res) => {
    let url = '';
    try { url = decodeURIComponent(req.url.split('?')[0].split('#')[0]); } catch { /* 404 below */ }
    let file = url.startsWith('/resume/') ? path.join(DOCS, url.slice('/resume/'.length)) : '';
    if (file && file !== DOCS && !file.startsWith(DOCS + path.sep)) file = '';
    if (file && fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (!file || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
}

// Runs in the page. Shared helpers for every in-page probe.
const HELPERS = `
  window.__probe = {
    // Lines of text an element shows: distinct tops of its text boxes (images and figures add none).
    // A box starts a new line when its vertical middle is below the bottom of the line so far.
    lines(el) { const boxes = []; const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      while (w.nextNode()) { if (!w.currentNode.data.trim()) continue; const r = document.createRange(); r.selectNodeContents(w.currentNode);
        for (const b of r.getClientRects()) if (b.width > 1) boxes.push(b); }
      boxes.sort((a, b) => a.top - b.top); let n = 0, bottom = -Infinity;
      for (const b of boxes) { if ((b.top + b.bottom) / 2 > bottom) { n++; bottom = b.bottom; } else bottom = Math.max(bottom, b.bottom); }
      return n; },
    shown(el) { const s = getComputedStyle(el); const r = el.getBoundingClientRect();
      return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0; },
    name(el) { const cls = typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.') : '';
      return el.tagName.toLowerCase() + cls + ' "' + (el.textContent || el.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ').slice(0, 32) + '"'; },
    rgb(c) { const m = c.match(/rgba?\\(([^)]+)\\)/); if (!m) return null; const p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number);
      return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; },
    lum({ r, g, b }) { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
      return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); },
    ratio(a, b) { const x = this.lum(a), y = this.lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); },
    // The opaque colour behind an element: the first ancestor with a non-transparent background.
    behind(el) { for (let p = el; p; p = p.parentElement) {
        const c = this.rgb(getComputedStyle(p).backgroundColor); if (c && c.a > 0.5) return c; }
      return this.rgb(getComputedStyle(document.documentElement).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 }; },
  };`;

const PROBES_WIDE = `(() => {
  const P = window.__probe; const out = {};
  // centered_prose
  out.centered_prose = [...document.querySelectorAll('main p, main li, .hero p, .lead')].filter(el => P.shown(el)
      && getComputedStyle(el).textAlign === 'center').filter(el => {
      return P.lines(el) > 3; })
    .map(el => P.name(el));
  // measure (chars per line) for paragraphs in main
  out.measure = [...document.querySelectorAll('main p')].filter(el => P.shown(el) && el.textContent.trim().length > 160).filter(el => {
      const lines = Math.max(1, P.lines(el));
      const cpl = el.textContent.trim().length / lines; return lines > 1 && (cpl > 90 || cpl < 30); })
    .map(el => P.name(el));
  // row_misalign: card titles in one row of a grid
  const misses = [];
  for (const grid of document.querySelectorAll('.cards, .grid, .explore, .listing, [class*="cards"]')) {
    const cards = [...grid.children].filter(P.shown); const rows = new Map();
    for (const c of cards) { const top = Math.round(c.getBoundingClientRect().top); (rows.get(top) || rows.set(top, []).get(top)).push(c); }
    for (const row of rows.values()) {
      if (row.length < 2) continue;
      const titles = row.map(c => c.querySelector('h2, h3, h4, .card-title')).filter(Boolean);
      // The description is the card's longest paragraph (kickers are short).
      const bodies = row.map(c => [...c.querySelectorAll('p')].filter(P.shown).sort((a, b) => b.textContent.length - a.textContent.length)[0]).filter(Boolean);
      const spread = arr => { const t = arr.map(x => x.getBoundingClientRect().top); return Math.max(...t) - Math.min(...t); };
      if (titles.length === row.length && spread(titles) > 2) misses.push('titles ' + titles.map(t => P.name(t)).join(' | '));
      if (bodies.length === row.length && spread(bodies) > 2) misses.push('descriptions ' + bodies.map(t => P.name(t)).join(' | '));
    }
  }
  out.row_misalign = misses;
  // cover_empty: card cover svg drawn content width versus panel width
  out.cover_empty = [...document.querySelectorAll('.card-cover')].filter(P.shown).filter(panel => {
      const svg = panel.querySelector('svg'); if (!svg) return false;
      const a = svg.getBoundingClientRect(); const b = panel.getBoundingClientRect();
      return (a.width * a.height) / (b.width * b.height) < 0.55; }).map(p => P.name(p.closest('.card') || p).replace(/"[^"]*"$/, '"' + ((p.closest('.card') || p).id || '') + '"'));
  // svg_contrast
  out.svg_contrast = [...document.querySelectorAll('svg text')].filter(P.shown).filter(t => {
      const fill = P.rgb(getComputedStyle(t).fill); if (!fill || fill.a < 0.5) return false;
      const op = parseFloat(getComputedStyle(t).opacity || 1) * parseFloat(getComputedStyle(t).fillOpacity || 1);
      const r = t.getBoundingClientRect(); const under = document.elementsFromPoint(r.left + r.width / 2, r.top + r.height / 2)
        .find(e => e !== t && e.closest('svg') === t.closest('svg') && /^(rect|path|circle|polygon|ellipse)$/.test(e.tagName));
      const shape = under && P.rgb(getComputedStyle(under).fill);
      const bg = shape && shape.a > 0.5 && getComputedStyle(under).fillOpacity > 0.5 ? shape : P.behind(t.closest('svg').parentElement); const mix = c => Math.round(c * op);
      const fg = op < 1 ? { r: mix(fill.r) + Math.round(bg.r * (1 - op)), g: mix(fill.g) + Math.round(bg.g * (1 - op)), b: mix(fill.b) + Math.round(bg.b * (1 - op)) } : fill;
      return P.ratio(fg, bg) < 4.5; }).map(t => P.name(t));
  // type and colour sprawl (raw sets; aggregated site-wide by the runner)
  const sizes = new Set(); const colours = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) { const n = walker.currentNode; const el = n.parentElement;
    if (!el || !n.data.trim() || el.closest('svg, script, style, noscript, .visually-hidden, .sr-only') || !P.shown(el)) continue;
    const s = getComputedStyle(el); sizes.add(Math.round(parseFloat(s.fontSize) * 2) / 2); colours.add(s.color); }
  out.__sizes = [...sizes]; out.__colours = [...colours];
  return out;
})()`;

const PROBES_PHONE = `(() => {
  const P = window.__probe; const out = {};
  out.centered_prose = [...document.querySelectorAll('main p, main li, .hero p, .lead')].filter(el => P.shown(el)
      && getComputedStyle(el).textAlign === 'center').filter(el => {
      return P.lines(el) > 3; })
    .map(el => P.name(el));
  // tap_near_miss: controls outside running text between 24 and 44 px on the short side
  // A link inside running text (its block holds other words) is exempt, as in WCAG 2.5.8.
  const inText = el => { if (el.tagName !== 'A' || getComputedStyle(el).display !== 'inline') return false;
    let b = el.parentElement; while (b && getComputedStyle(b).display.startsWith('inline')) b = b.parentElement;
    return !!b && b.textContent.trim().length > el.textContent.trim().length + 2; };
  // A card title link whose ::after covers the card: the card is the target.
  const stretched = el => { const a = getComputedStyle(el, '::after');
    if (a.position !== 'absolute' || a.content === 'none') return false;
    const host = el.closest('.card, li, section'); const r = host && host.getBoundingClientRect();
    return !!r && Math.min(r.width, r.height) >= 44; };
  out.tap_near_miss = [...document.querySelectorAll('a[href], button, select, input:not([type=hidden]), summary, [role=button], [tabindex="0"]')]
    .filter(el => P.shown(el) && !el.closest('.skip-link') && el.getBoundingClientRect().bottom > 0 && el.getBoundingClientRect().right > 0 && !el.closest('p, li p, td, .footnote, .footnotes, figcaption, .caption, svg, .sr-only, .visually-hidden')
      && !inText(el) && !stretched(el))
    .filter(el => { const r = el.getBoundingClientRect(); const s = Math.min(r.width, r.height); return s >= 24 && s < 44; })
    .map(el => { const r = el.getBoundingClientRect(); return P.name(el) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height); });
  return out;
})()`;

async function focusUnseen(p) {
  return p.evaluate(() => {
    const P = window.__probe;
    // Focus can show on the control, its ::before/::after, a child shape (chart marks) or an ancestor (cards).
    const one = (el, pseudo) => { const s = getComputedStyle(el, pseudo || null);
      return [s.outlineStyle, s.outlineWidth, s.outlineColor, s.boxShadow, s.backgroundColor, s.borderColor, s.color,
        s.textDecorationLine, s.stroke, s.strokeWidth, s.fill, s.transform, s.opacity].join('|'); };
    const look = el => { const parts = [one(el), one(el, '::before'), one(el, '::after')];
      [...el.querySelectorAll('*')].slice(0, 30).forEach(d => parts.push(one(d)));
      for (let a = el.parentElement, i = 0; a && i < 3; a = a.parentElement, i++) parts.push(one(a));
      return parts.join('#'); };
    const els = [...document.querySelectorAll('a[href], button, select, input:not([type=hidden]), summary, [tabindex="0"]')].filter(P.shown).slice(0, 400);
    const miss = [];
    // Transitions would report the unfocused value; measure the end state.
    const still = document.head.appendChild(document.createElement('style'));
    still.textContent = '*, *::before, *::after { transition: none !important; animation: none !important; }';
    for (const el of els) {
      if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
      const before = look(el);
      try { el.focus({ focusVisible: true, preventScroll: true }); } catch { el.focus(); }
      if (document.activeElement !== el) continue;
      if (look(el) === before) miss.push(P.name(el));
    }
    still.remove();
    return miss;
  });
}

(async () => {
  const server = serve();
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/resume/`;
  const browser = await chromium.launch();
  const list = pages();
  const found = {}; const add = (k, page, items) => { (found[k] ||= []).push(...items.map(i => page + ': ' + i)); };
  const sizes = new Set(); const colours = { light: new Set(), dark: new Set() };
  const shifts = []; const errors = [];
  try {
    // Reduced motion everywhere: measure the final drawn state, not a chart part-way through its draw-in.
    for (const [width, scheme, motion] of [[1280, 'light', 'reduce'], [1280, 'dark', 'reduce'], [375, 'light', 'reduce']]) {
      const ctx = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: scheme, reducedMotion: motion });
      await ctx.addInitScript(HELPERS);
      await ctx.addInitScript(() => {
        window.__cls = 0;
        try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
          .observe({ type: 'layout-shift', buffered: true }); } catch { /* not supported */ }
      });
      const page = await ctx.newPage();
      for (const rel of list) {
        try {
          const resp = await page.goto(base + rel, { waitUntil: 'networkidle' });
          if (!resp || !resp.ok()) { errors.push(`${rel} HTTP ${resp ? resp.status() : 'none'}`); continue; }
          await page.evaluate(() => document.fonts.ready);
          await page.waitForTimeout(150);
          if (width === 1280) {
            const r = await page.evaluate(PROBES_WIDE);
            for (const k of ['centered_prose', 'measure', 'row_misalign', 'cover_empty', 'svg_contrast']) add(k, `${rel} ${width} ${scheme}`, r[k]);
            r.__colours.forEach(c => colours[scheme].add(c));
            if (scheme === 'light') { r.__sizes.forEach(s => sizes.add(s)); add('focus_unseen', rel, await focusUnseen(page)); }
          } else {
            const r = await page.evaluate(PROBES_PHONE);
            add('centered_prose', `${rel} 375`, r.centered_prose); add('tap_near_miss', rel, r.tap_near_miss);
            const cls = await page.evaluate(() => window.__cls);
            if (cls > 0.05) shifts.push(`${rel}: CLS ${cls.toFixed(3)}`);
            await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 2));
            await page.waitForTimeout(100);
            const running = await page.evaluate(() => document.getAnimations().filter(a => a.playState === 'running'
              && (a.effect && a.effect.getTiming().duration > 10)).map(a => (a.animationName || a.transitionProperty || 'animation')
              + ' on ' + window.__probe.name(a.effect.target || document.body)));
            add('motion_reduced', rel, running);
          }
        } catch (e) { errors.push(`${rel} ${width} ${scheme}: ${e.message.split('\n')[0]}`); }
      }
      await ctx.close();
    }
  } finally { await browser.close(); server.close(); }
  found.layout_shift = shifts;
  // Distinct values above a typical scale count as sprawl: about eight sizes and ten text colours.
  found.type_sprawl = [...sizes].sort((a, b) => a - b).slice(8).map(s => `${s}px`);
  found.colour_sprawl = [...colours.light].slice(10).map(c => 'light ' + c).concat([...colours.dark].slice(10).map(c => 'dark ' + c));
  const probes = {};
  for (const k of ['focus_unseen', 'tap_near_miss', 'layout_shift', 'motion_reduced', 'centered_prose', 'measure',
    'row_misalign', 'cover_empty', 'svg_contrast', 'type_sprawl', 'colour_sprawl']) {
    const items = [...new Set(found[k] || [])];
    probes[k] = { count: items.length, examples: items.slice(0, 5) };
  }
  let commit = ''; try { commit = require('child_process').execSync('git rev-parse --short=7 HEAD', { cwd: ROOT }).toString().trim(); } catch { /* not a repo */ }
  const record = { type: 'probe', commit, timestamp: Math.floor(Date.now() / 1000), pages: list.length, probes, errors };
  for (const [k, v] of Object.entries(probes)) console.log(`PROBE ${k}=${v.count}${v.examples.length ? '  e.g. ' + v.examples[0] : ''}`);
  if (errors.length) console.log('ERRORS', errors.length, errors.slice(0, 3).join('; '));
  if (opt.out) fs.writeFileSync(opt.out, JSON.stringify(record, null, 2));
  if (opt.append) fs.appendFileSync(opt.append, JSON.stringify(record) + '\n');
  process.exitCode = errors.length ? 1 : 0;
})();
