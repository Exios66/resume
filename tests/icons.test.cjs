// Sanity check: every decorative icon <svg> in the built pages self-sizes,
// so a missing stylesheet can never balloon them to the 300x150 default.
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "..");
const pages = [];
function walk(dir) {
  const { readdirSync, statSync } = require("node:fs");
  for (const entry of readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) walk(full);
    else pages.push(full);
  }
}
walk(path.join(root, "docs"));

let svgs = 0;
for (const file of pages.filter((f) => f.endsWith(".html"))) {
  const html = readFileSync(file, "utf8");
  const icons = html.match(/<svg class="icon[^"]*"[^>]*>/g) ?? [];
  for (const tag of icons) {
    svgs++;
    assert.ok(/width="1em"/.test(tag) && /height="1em"/.test(tag),
      `${file}: unsized icon ${tag}`);
  }
  assert.ok(!/icon-ext/.test(html) || /<svg class="icon icon-ext" width="1em" height="1em"/.test(html),
    `${file}: icon-ext must be sized`);
}
assert.ok(svgs > 0, "no icon SVGs found — did the build run?");
console.log(`all ${svgs} icon svgs are 1em-sized`);
