// Check that every built page survives in-place browser translation.
// node scripts/hillclimb/translation-sweep.cjs [--engines chromium,firefox,webkit] [--widths 320,375,1280]
//   [--langs de,fr,es,zh,ar] [--pages a.html,b.html] [--shots page,page]
// Each page is loaded, translated with tests/browser/pseudo_translate.js (simulated: the same
// in-place text replacement real translators do, with language-shaped pseudo-text), then checked by translation-checks.js:
//   overflow   the page scrolls sideways
//   escape     an element sticks out of the viewport outside a sideways scroller
//   clipped    a control's or label's text is wider than its box
//   header     a header control is under 44px, or the title runs under Search or the toggle
//   copy       a code block's Copy button covers its code text
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
const CHECKS = fs.readFileSync(path.join(__dirname, 'translation-checks.js'), 'utf8');
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

/** The file under DOCS that a /resume/ URL names, or '' when there is none. */
function resolve(rawUrl) {
  let url = '';
  try { url = decodeURIComponent(rawUrl.split('?')[0].split('#')[0]); } catch { return ''; }
  if (!url.startsWith('/resume/')) return '';
  let file = path.join(DOCS, url.slice('/resume/'.length));
  if (file !== DOCS && !file.startsWith(DOCS + path.sep)) return '';
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  return fs.existsSync(file) ? file : '';
}

const server = http.createServer((req, res) => {
  const file = resolve(req.url);
  if (!file) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

/** Load one page, translate it and return its problems. */
async function check(page, url, rel, lang) {
  await page.goto(url, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  // A thesis title and Langton's Ant have names in other languages, so they translate.
  const project = /^projects\/[^/]+\.html$/.test(rel) && !/\/(index|natd|langtons-ant)\.html$/.test(rel);
  const before = project ? await page.evaluate(() => (document.querySelector('h1.page-title') || {}).textContent?.trim() || null) : null;
  try {
    await page.evaluate(l => window.pseudoTranslate(l), lang);
    await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
    return await page.evaluate(title => window.translationChecks(title), before);
  } catch (error) {
    return [`error: ${error.message.split('\n')[0]}`];
  }
}

/** Sweep every language and page at one width; returns [views, views with problems]. */
async function sweepWidth(browser, engine, width, base) {
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
  await ctx.addInitScript(SCRIPT);
  await ctx.addInitScript(CHECKS);
  const page = await ctx.newPage();
  let loads = 0, failures = 0;
  for (const lang of list(opt.langs)) {
    for (const rel of pages) {
      const problems = await check(page, base + rel, rel, lang);
      loads++;
      if (problems.length) { failures++; console.log(`FAIL ${engine} ${width} ${lang} ${rel}\n  ${problems.join('\n  ')}`); }
      if ((problems.length || shots.has(rel)) && engine === 'chromium' && width !== 320) {
        fs.mkdirSync(OUT, { recursive: true });
        const shot = path.join(OUT, `${lang}-${width}-${rel.replace(/\//g, '_').replace(/\.html$/, '')}.png`);
        await page.screenshot({ path: shot, fullPage: !(width === 375 && !problems.length) });
      }
    }
  }
  await ctx.close();
  return [loads, failures];
}

server.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${server.address().port}/resume/`;
  let failures = 0, loads = 0;
  try {
    for (const engine of list(opt.engines)) {
      const browser = await ENGINES[engine].launch();
      for (const width of list(opt.widths).map(Number)) {
        const [views, failed] = await sweepWidth(browser, engine, width, base);
        loads += views; failures += failed;
      }
      await browser.close();
    }
  } finally {
    server.close();
  }
  console.log(`${loads} translated page views, ${failures} with problems`);
  process.exitCode = failures ? 1 : 0;
});
