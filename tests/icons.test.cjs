// Run from the repository root after a render: node --test tests/icons.test.cjs
// Guards the built pages against the PR #12 failure: icons sized only by styles.css,
// which balloon to the 300x150 SVG default when a stale or missing stylesheet is served.
const assert = require('node:assert/strict');
const { readdirSync, readFileSync, statSync } = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');

const docs = path.join(__dirname, '..', 'docs');
function pages(dir) {
  return readdirSync(dir).flatMap((entry) => {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) return entry === 'site_libs' ? [] : pages(full);
    return full.endsWith('.html') ? [full] : [];
  });
}
const built = pages(docs).map((file) => ({ file: path.relative(docs, file), html: readFileSync(file, 'utf8') }));

test('the site has been built', () => {
  assert.ok(built.length > 10, 'render the site first: quarto render');
});

test('every icon svg carries its own 1em size', () => {
  let icons = 0;
  for (const { file, html } of built) {
    for (const tag of html.match(/<svg class="icon[^"]*"[^>]*>/g) ?? []) {
      icons++;
      assert.match(tag, / width="1em" height="1em"/, `${file}: unsized icon ${tag}`);
    }
  }
  assert.ok(icons > 0, 'no icons found');
});

test('each page has one sprite, after the footer', () => {
  for (const { file, html } of built) {
    const sprites = html.match(/<svg width="0" height="0"/g) ?? [];
    assert.equal(sprites.length, 1, file);
    assert.ok(html.indexOf('</footer>') < html.indexOf('<symbol id="i-'), `${file}: sprite before footer`);
  }
});

test('only one theme-toggle icon is visible before scripts or styles load', () => {
  for (const { file, html } of built) {
    assert.match(html, /<span class="i-sun" hidden(?:="")?><svg/, file);
    assert.match(html, /<span class="i-moon"><svg/, file);
  }
});

test('the site stylesheet link is cache-busted', () => {
  for (const { file, html } of built) {
    assert.match(html, /href="(?:\.\.\/)*styles\.css\?v=[0-9a-f]{10}"/, file);
    assert.doesNotMatch(html, /href="(?:\.\.\/)*styles\.css"/, file);
  }
});
