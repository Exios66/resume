// In-page checks for translation-sweep.cjs, run after simulated translation.
// Loaded as an init script; window.translationChecks(title) returns a list of problems.
(() => {
  const visible = (el) => {
    const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0;
  };
  const name = (el) => {
    const cls = typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).join('.') : '';
    return el.tagName.toLowerCase() + cls + ' "' + (el.textContent || '').trim().slice(0, 40) + '"';
  };
  const scroller = (el) => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      if (getComputedStyle(p).overflowX !== 'visible') return p;
    }
    return null;
  };
  const textBox = (el) => { const range = document.createRange(); range.selectNodeContents(el); return range; };
  const overlaps = (a, b, slack = 1) => a.right > b.left + slack && a.left < b.right - slack && a.bottom > b.top + slack && a.top < b.bottom - slack;
  const width = () => document.documentElement.clientWidth;

  /** overflow: the page scrolls sideways. */
  function overflow() {
    const over = document.documentElement.scrollWidth - width();
    return over > 0 ? [`overflow: page is ${over}px wider than the viewport`] : [];
  }

  /** escape: an element sticks out of the viewport outside a sideways scroller (first three). */
  function escape() {
    const vw = width();
    const out = [...document.body.querySelectorAll('*')].filter((el) => {
      if (el.closest('svg, .visually-hidden, .sr-only, .skip-link, [hidden]') || !visible(el) || scroller(el)) return false;
      const r = el.getBoundingClientRect();
      return r.right > vw + 1 || r.left < -1;
    });
    return out.slice(0, 3).map((el) => {
      const r = el.getBoundingClientRect();
      return `escape: ${name(el)} spans ${Math.round(r.left)}..${Math.round(r.right)} of ${vw}`;
    });
  }

  /** clipped: a control's or label's text is wider than its box. */
  function clipped() {
    const labels = '.nav-link, .btn, .chip, .code-copy-button, .site-title, .pager-name, .project-jump a, .footer-links a, .kicker, h1, h2';
    return [...document.querySelectorAll(labels)].filter((el) => visible(el) && !scroller(el)
      && el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).overflowX === 'visible').flatMap((el) => {
      const t = textBox(el).getBoundingClientRect(); const r = el.getBoundingClientRect();
      return t.right > r.right + 1 || t.left < r.left - 1 ? [`clipped: ${name(el)} text ${Math.round(t.width)}px in a ${Math.round(r.width)}px box`] : [];
    });
  }

  /** header: a header control is under 44px, or the title runs under Search or the toggle. */
  function header() {
    const bar = document.querySelector('.site-header'); const title = document.querySelector('.site-title');
    if (!bar || !title) return [];
    const controls = [...bar.querySelectorAll('.nav-list li')].filter(visible).map((li) => li.querySelector('a, button')).filter(Boolean);
    const small = controls.filter((c) => { const r = c.getBoundingClientRect(); return r.height < 44 || r.width < 40; })
      .map((c) => { const r = c.getBoundingClientRect(); return `header: ${name(c)} is ${Math.round(r.width)}x${Math.round(r.height)}`; });
    const lines = [...textBox(title).getClientRects()];
    const covered = controls.filter((c) => lines.some((t) => overlaps(t, c.getBoundingClientRect())))
      .map((c) => `header: title text overlaps ${name(c)}`);
    return small.concat(covered);
  }

  /** copy: a code block's Copy button covers its code text. */
  function copy() {
    return [...document.querySelectorAll('div.code-copy-outer-scaffold')].flatMap((block) => {
      const button = block.querySelector('.code-copy-button'); const code = block.querySelector('code');
      if (!button || !code || !visible(button)) return [];
      const b = button.getBoundingClientRect();
      // Text nodes only: a range over the whole block would add the taller boxes of its highlight spans.
      const walker = document.createTreeWalker(code, NodeFilter.SHOW_TEXT);
      let hit = false;
      while (!hit && walker.nextNode()) hit = [...textBox(walker.currentNode).getClientRects()].some((line) => line.width && overlaps(line, b, 0));
      return hit ? [`copy: the Copy button (${Math.round(b.width)}px) covers code text`] : [];
    });
  }

  /** Whether a paragraph is Arabic prose that should start at its right edge. */
  function arabicProse(p) {
    const text = p.textContent.trim();
    if (!visible(p) || p.closest('[translate="no"], .chart-tools, .contact, .actions') || !/[؀-ۿ]/.test(text.slice(0, 12))) return false;
    const s = getComputedStyle(p);
    if (s.textAlign === 'center' || s.display !== 'block') return false;
    // Rows of tags, buttons or arrow links start with a box, which gives no direction; the layout is not mirrored.
    const lead = [...p.childNodes].find((n) => n.nodeType === 1 || n.data.trim());
    return !(lead && lead.nodeType === 1 && getComputedStyle(lead).display !== 'inline');
  }

  /** How far a paragraph's first line stops short of its right edge. */
  function rightGap(p) {
    // Right-to-left text boxes come in logical order, so the first line is every box at the first box's height.
    const boxes = [...textBox(p).getClientRects()].filter((x) => x.width);
    if (!boxes.length) return 0;
    const lineRight = Math.max(...boxes.filter((x) => Math.abs(x.top - boxes[0].top) < 2).map((x) => x.right));
    const s = getComputedStyle(p);
    return p.getBoundingClientRect().right - parseFloat(s.paddingRight) - parseFloat(s.borderRightWidth) - lineRight;
  }

  /** align: (Arabic) a paragraph's text does not start at its right edge (first two). */
  function align() {
    if (document.documentElement.lang !== 'ar') return [];
    // One-sided: Firefox measures a trailing space a few pixels past the edge of a right-aligned line.
    return [...document.querySelectorAll('main p')].filter((p) => arabicProse(p) && rightGap(p) > 3)
      .slice(0, 2).map((p) => `align: ${name(p)} does not start at its right edge`);
  }

  /** names: a project page's title changed, so a translate="no" name was translated. */
  function names(before) {
    const h1 = document.querySelector('h1.page-title');
    const after = h1 && h1.textContent.trim();
    return before && h1 && after !== before ? [`names: title "${before}" became "${after}"`] : [];
  }

  window.translationChecks = (before) => [overflow, escape, clipped, header, copy, align].flatMap((check) => check()).concat(names(before));
})();
