// Run from the repository root: node --test tests/theme.test.cjs
// Execute the real inline scripts in isolated contexts with a minimal DOM.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

function script(name) {
  const html = readFileSync(path.join(__dirname, '..', 'partials', name), 'utf8');
  const match = html.match(/<script>([\s\S]*?)<\/script>/);
  assert.ok(match, `Missing executable script in ${name}`);
  return match[1];
}

const bootstrap = script('head.html');
const controls = script('scripts.html');

function element() {
  const attributes = new Map();
  const listeners = new Map();
  return {
    textContent: '',
    getAttribute: (name) => attributes.get(name) ?? null,
    setAttribute: (name, value) => attributes.set(name, value),
    addEventListener(name, callback) {
      const callbacks = listeners.get(name) ?? [];
      callbacks.push(callback);
      listeners.set(name, callbacks);
    },
    click(event = {}) {
      for (const callback of listeners.get('click') ?? []) callback(event);
    },
  };
}

function environment({ saved = null, dark = false, storageFails = false,
                       togglePresent = true, printPresent = true } = {}) {
  const root = element();
  const toggle = element();
  const print = element();
  const writes = [];
  let printCalls = 0;
  const context = vm.createContext({
    document: {
      documentElement: root,
      querySelector(selector) {
        if (selector === '.theme-toggle') return togglePresent ? toggle : null;
        if (selector === '.print-btn') return printPresent ? print : null;
        throw new Error(`Unexpected selector: ${selector}`);
      },
    },
    localStorage: {
      getItem(key) {
        assert.equal(key, 'theme');
        if (storageFails) throw new Error('Storage denied');
        return saved;
      },
      setItem(key, value) {
        if (storageFails) throw new Error('Storage denied');
        writes.push([key, value]);
      },
    },
    window: {
      matchMedia(query) {
        assert.equal(query, '(prefers-color-scheme: dark)');
        return { matches: dark };
      },
      print() { printCalls += 1; },
    },
  });
  return { root, toggle, print, writes, context, printCalls: () => printCalls };
}

function assertTheme(ui, theme) {
  assert.equal(ui.root.getAttribute('data-theme'), theme);
  assert.equal(ui.toggle.getAttribute('aria-label'),
    theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
  assert.equal(ui.toggle.textContent, theme === 'dark' ? '☀' : '☾');
}

for (const saved of ['light', 'dark']) {
  test(`saved ${saved} theme overrides the opposite system preference before paint`, () => {
    const ui = environment({ saved, dark: saved === 'light' });
    vm.runInContext(bootstrap, ui.context);
    assert.equal(ui.root.getAttribute('data-theme'), saved);
    vm.runInContext(controls, ui.context);
    assertTheme(ui, saved);
    assert.deepEqual(ui.writes, []);
    ui.toggle.click();
    const next = saved === 'light' ? 'dark' : 'light';
    assertTheme(ui, next);
    assert.deepEqual(ui.writes, [['theme', next]]);
  });
}

for (const saved of [null, '', 'sepia', 'DARK', ' light ']) {
  for (const dark of [false, true]) {
    test(`invalid or missing saved theme ${JSON.stringify(saved)}, system dark=${dark}`, () => {
      const ui = environment({ saved, dark });
      vm.runInContext(bootstrap, ui.context);
      assert.equal(ui.root.getAttribute('data-theme'), null);
      vm.runInContext(controls, ui.context);
      assert.equal(ui.toggle.getAttribute('aria-label'),
        dark ? 'Switch to light theme' : 'Switch to dark theme');
      assert.equal(ui.toggle.textContent, dark ? '☀' : '☾');
      assert.deepEqual(ui.writes, []);
      ui.toggle.click();
      assertTheme(ui, dark ? 'light' : 'dark');
      ui.toggle.click();
      assertTheme(ui, dark ? 'dark' : 'light');
      assert.deepEqual(ui.writes, [
        ['theme', dark ? 'light' : 'dark'], ['theme', dark ? 'dark' : 'light'],
      ]);
    });
  }
}

for (const dark of [false, true]) {
  test(`storage access errors still allow toggling, system dark=${dark}`, () => {
    const ui = environment({ dark, storageFails: true });
    vm.runInContext(bootstrap, ui.context);
    assert.equal(ui.root.getAttribute('data-theme'), null);
    vm.runInContext(controls, ui.context);
    ui.toggle.click();
    assertTheme(ui, dark ? 'light' : 'dark');
    ui.toggle.click();
    assertTheme(ui, dark ? 'dark' : 'light');
    assert.deepEqual(ui.writes, []);
  });
}

for (const togglePresent of [false, true]) {
  test(`print cancels link navigation and opens one dialog, toggle present=${togglePresent}`, () => {
    const ui = environment({ togglePresent });
    vm.runInContext(controls, ui.context);
    assert.equal(ui.printCalls(), 0);
    let prevented = 0;
    ui.print.click({ preventDefault() { prevented += 1; } });
    assert.equal(prevented, 1);
    assert.equal(ui.printCalls(), 1);
    assert.deepEqual(ui.writes, []);
  });
}

test('theme toggle works on pages without a print button', () => {
  const ui = environment({ printPresent: false });
  vm.runInContext(controls, ui.context);
  ui.toggle.click();
  assertTheme(ui, 'dark');
  assert.equal(ui.printCalls(), 0);
});

test('pages without either control initialize safely', () => {
  const ui = environment({ printPresent: false, togglePresent: false });
  vm.runInContext(controls, ui.context);
  assert.equal(ui.root.getAttribute('data-theme'), null);
  assert.equal(ui.printCalls(), 0);
  assert.deepEqual(ui.writes, []);
});
