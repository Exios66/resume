// Screenshot a built page for visual review of an experiment.
// node scripts/hillclimb/shot.cjs <docs page> <width> <light|dark> <name> [--at css] [--text words] [--height px] [--full]
//   --at css      scroll the first element matching the selector to the top of the view
//   --text words  with --at, pick the first match that contains these words
// Pages are served at /resume/ as GitHub Pages does, so absolute links (404.html) resolve.
// Images go to .hillclimb-shots/ (gitignored, outside the published site) unless SHOT_OUT is set.
const { chromium } = require('playwright');
const fs = require('fs');
const http = require('http');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const DOCS = path.join(ROOT, 'docs');
const OUT = process.env.SHOT_OUT || path.join(ROOT, '.hillclimb-shots');
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2' };

const [page, width, theme, name, ...rest] = process.argv.slice(2);
if (!page || !width || !theme || !name) {
  console.error('usage: shot.cjs <page> <width> <light|dark> <name> [--at css] [--text words] [--height px] [--full]');
  process.exit(2);
}
const opt = {};
for (let i = 0; i < rest.length; i++) {
  if (rest[i] === '--full') opt.full = true;
  else opt[rest[i].replace(/^--/, '')] = rest[++i];
}

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0].split('#')[0]);
  let file = url.startsWith('/resume/') ? path.join(DOCS, url.slice('/resume/'.length)) : '';
  if (file && fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!file || !file.startsWith(DOCS) || !fs.existsSync(file)) {
    res.writeHead(404, { 'Content-Type': 'text/html' });
    return fs.existsSync(path.join(DOCS, '404.html')) ? fs.createReadStream(path.join(DOCS, '404.html')).pipe(res) : res.end();
  }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

server.listen(0, '127.0.0.1', async () => {
  const browser = await chromium.launch();
  try {
    const ctx = await browser.newContext({ viewport: { width: +width, height: +(opt.height || 760) },
      colorScheme: theme, reducedMotion: 'reduce' });
    const p = await ctx.newPage();
    p.on('pageerror', e => console.error('pageerror:', e.message));
    await p.goto(`http://127.0.0.1:${server.address().port}/resume/${page}`, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    if (opt.at) {
      let target = p.locator(opt.at);
      if (opt.text) target = target.filter({ hasText: opt.text });
      await target.first().evaluate(el => el.scrollIntoView({ block: 'start' }));
      await p.evaluate(() => window.scrollBy(0, -90)); // clear the sticky header
    }
    await p.waitForTimeout(250);
    fs.mkdirSync(OUT, { recursive: true });
    const file = path.join(OUT, name.endsWith('.png') ? name : name + '.png');
    await p.screenshot({ path: file, fullPage: !!opt.full });
    console.log(file);
  } finally {
    await browser.close();
    server.close();
  }
});
