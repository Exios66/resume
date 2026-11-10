/* Site enhancements: header hairline, reading progress on technical reports and a
   fade-in for project cards. Everything here is optional; the pages are complete
   without it. Decorative motion respects the reduced-motion preference. */
(function () {
  "use strict";
  var doc = document;
  var root = doc.documentElement;
  doc.querySelectorAll('.chart-scroll').forEach(function (chart) {
    chart.addEventListener('keydown', function (event) {
      if (chart.scrollWidth <= chart.clientWidth || (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight')) return;
      event.preventDefault();
      chart.scrollLeft += event.key === 'ArrowRight' ? 40 : -40;
    });
  });
  // Cards: a soft light follows the pointer. Decorative, fine pointers only.
  try {
    if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
      doc.addEventListener("pointermove", function (event) {
        var card = event.target.closest && event.target.closest(".card");
        if (!card) return;
        var box = card.getBoundingClientRect();
        card.style.setProperty("--mx", Math.round(event.clientX - box.left) + "px");
        card.style.setProperty("--my", Math.round(event.clientY - box.top) + "px");
      }, { passive: true });
    }
  } catch (e) {}

  // Coordinated views share a row index emitted by the chart's table renderer.
  // Readout text comes from the authored table, including unplotted context.
  (function () {
    doc.querySelectorAll('figure.chart').forEach(function (figure) {
      var link = figure.querySelector('.chart-tools a');
      var table = link && doc.getElementById(link.hash.slice(1));
      if (!table) return;
      var rows = Array.from(table.querySelectorAll('tbody tr'));
      var marks = Array.from(figure.querySelectorAll('.mark'));
      if (!rows.length || !marks.length || marks.some(function (mark) {
        var index = Number(mark.getAttribute('data-source-row'));
        return !Number.isInteger(index) || index < 1 || index > rows.length;
      })) return;
      var headers = Array.from(table.querySelectorAll('thead tr:last-child th')).map(function (cell) { return cell.textContent.trim(); });
      var readout = doc.createElement('div');
      readout.className = 'chart-readout';
      readout.setAttribute('role', 'group');
      readout.setAttribute('aria-label', 'Selected source row');
      var position = doc.createElement('span');
      position.className = 'chart-readout-position';
      var name = doc.createElement('strong');
      name.className = 'chart-readout-name';
      var values = doc.createElement('dl');
      var hint = doc.createElement('p');
      hint.className = 'chart-readout-hint';
      hint.textContent = 'Focus or point to a mark or data row to connect the evidence.';
      readout.append(position, name, values, hint);
      figure.querySelector('.chart-tools').before(readout);
      function select(index) {
        rows.forEach(function (row, at) { row.classList.toggle('is-linked', at === index); });
        marks.forEach(function (mark) { mark.classList.toggle('is-linked', Number(mark.getAttribute('data-source-row')) === index + 1); });
        position.textContent = 'Source row ' + (index + 1) + ' of ' + rows.length;
        name.textContent = rows[index].cells[0].textContent.trim();
        values.replaceChildren();
        Array.from(rows[index].cells).slice(1).forEach(function (cell, at) {
          var pair = doc.createElement('div');
          var key = doc.createElement('dt');
          var value = doc.createElement('dd');
          key.textContent = headers[at + 1] || 'Value';
          value.textContent = cell.textContent.trim();
          pair.append(key, value);
          values.appendChild(pair);
        });
      }
      marks.forEach(function (mark) {
        var index = Number(mark.getAttribute('data-source-row')) - 1;
        mark.addEventListener('focus', function () { select(index); });
        mark.addEventListener('pointerenter', function () { select(index); });
        mark.addEventListener('click', function () { mark.focus({preventScroll: true}); select(index); });
      });
      rows.forEach(function (row, index) {
        row.tabIndex = 0;
        row.addEventListener('focus', function () { select(index); });
        row.addEventListener('pointerenter', function () { select(index); });
        row.addEventListener('click', function (event) {
          if (!event.target.closest('a, button, input, select, textarea')) row.focus({preventScroll: true});
        });
      });
      select(0);
    });
  })();

  // Charts: one shared tooltip for hover and keyboard focus. Every value it shows is
  // also in the table under the chart, so it only ever adds convenience.
  (function () {
    var marks = doc.querySelectorAll(".chart .mark");
    if (!marks.length) return;
    var tip = doc.createElement("div");
    var value = doc.createElement("strong");
    var label = doc.createElement("span");
    tip.className = "chart-tooltip";
    tip.setAttribute("role", "tooltip");
    tip.hidden = true;
    tip.appendChild(value);
    tip.appendChild(label);
    doc.body.appendChild(tip);
    var current = null;

    /** Show the tooltip for a mark, above its shape and inside the viewport. */
    function show(mark) {
      current = mark;
      value.textContent = mark.getAttribute("data-tip-value") || "";
      label.textContent = mark.getAttribute("data-tip-label") || "";
      tip.hidden = false;
      place();
    }
    /** Re-anchor the tooltip to its mark; hide it once the mark is out of view. */
    function place() {
      if (!current) return;
      var box = (current.querySelector(".bar, .dot") || current).getBoundingClientRect();
      var body = current.closest(".chart-body");
      var view = body ? body.getBoundingClientRect() : { left: 0, right: window.innerWidth };
      // Anchor to the part of the shape that is visible inside its chart.
      var left = Math.max(box.left, view.left), right = Math.min(box.right, view.right);
      var cx = (left + right) / 2;
      if (right <= left || box.bottom < 0 || box.top > window.innerHeight) {
        tip.hidden = true;
        return;
      }
      tip.hidden = false;
      var x = cx - tip.offsetWidth / 2;
      x = Math.max(8, Math.min(x, window.innerWidth - tip.offsetWidth - 8));
      var y = box.top - tip.offsetHeight - 10;
      if (y < 8) y = box.bottom + 10;
      // Never below the viewport; if it is taller than the space, pin it to the top.
      y = Math.max(8, Math.min(y, window.innerHeight - tip.offsetHeight - 8));
      tip.style.left = Math.round(x) + "px";
      tip.style.top = Math.round(y) + "px";
    }
    /** Hide the tooltip, or only if it belongs to the given mark. */
    function hide(mark) {
      if (mark && mark !== current) return;
      tip.hidden = true;
      current = null;
    }
    Array.prototype.forEach.call(marks, function (mark) {
      mark.addEventListener("pointerenter", function () { show(mark); });
      mark.addEventListener("pointerleave", function () { hide(mark); });
      mark.addEventListener("focus", function () { show(mark); });
      mark.addEventListener("blur", function () { hide(mark); });
    });
    doc.addEventListener("keydown", function (event) { if (event.key === "Escape") hide(); });
    // Page or chart scrolling (including the scroll that brings a focused mark into
    // view) moves the mark, so the tooltip follows it, or hides once it is out of view.
    window.addEventListener("scroll", place, { passive: true });
    Array.prototype.forEach.call(doc.querySelectorAll(".chart-body"), function (body) {
      body.addEventListener("scroll", place, { passive: true });
    });
  })();

  var reduce = false;
  try { reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}

  var frame = 0;
  var tasks = [];
  /** Run all registered scroll tasks once per animation frame. */
  function flush() {
    frame = 0;
    for (var i = 0; i < tasks.length; i++) tasks[i]();
  }
  /** Passive, rAF-throttled scroll listener shared by every task. */
  function onScroll(task) {
    if (!tasks.length) {
      window.addEventListener("scroll", function () {
        if (!frame) frame = window.requestAnimationFrame(flush);
      }, { passive: true });
    }
    tasks.push(task);
    task();
  }
  function scrollTop() { return window.pageYOffset || root.scrollTop || 0; }

  // Header: a hairline under the sticky header once the page has scrolled (not motion).
  var header = doc.querySelector(".site-header");
  if (header) {
    onScroll(function () { header.classList.toggle("is-scrolled", scrollTop() > 8); });
  }

  // Wide tables and long code blocks scroll on small screens. Make each one that
  // actually overflows reachable by keyboard (arrow keys then scroll it), and drop the
  // extra tab stop again when it fits. Tables keep their table role and caption name.
  (function () {
    var boxes = doc.querySelectorAll(".page table, .page div.sourceCode, .page pre:not(.sourceCode)");
    if (!boxes.length) return;
    var codes = [].filter.call(boxes, function (box) { return box.tagName !== "TABLE"; });
    function update() {
      boxes.forEach(function (box) {
        var wide = box.scrollWidth > box.clientWidth || box.scrollHeight > box.clientHeight;
        if (wide === box.hasAttribute("data-scrolls")) return;
        if (wide) {
          box.setAttribute("data-scrolls", "");
          box.setAttribute("tabindex", "0");
          if (box.tagName !== "TABLE") {
            box.setAttribute("role", "region");
            box.setAttribute("aria-label", "Code example " + (codes.indexOf(box) + 1) + " of " + codes.length + ", scrollable");
          }
        } else {
          box.removeAttribute("data-scrolls");
          box.removeAttribute("tabindex");
          if (box.tagName !== "TABLE") { box.removeAttribute("role"); box.removeAttribute("aria-label"); }
        }
      });
    }
    update();
    window.addEventListener("load", update); // web fonts can change widths
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(update);
    var timer;
    window.addEventListener("resize", function () { clearTimeout(timer); timer = setTimeout(update, 150); });
  })();

  // Site search: filter the generated page index and render results in place.
  (function () {
    var input = doc.getElementById("site-search-input");
    var list = doc.getElementById("search-results");
    var status = doc.getElementById("search-status");
    if (!input || !list || !status) return;
    var typeControl = doc.getElementById("search-type");
    if (!typeControl) return;
    var pages = null;

    function node(tag, text) {
      var el = doc.createElement(tag);
      if (text) el.textContent = text;
      return el;
    }

    // Derive artifact types from local routes, not claims in project prose.
    function pageType(url) {
      var route = new URL(url, location.href).pathname;
      if (/\/report\.html$/.test(route)) return { key: "report", label: "Technical report" };
      if (/\/appendix\.html$/.test(route)) return { key: "appendix", label: "Appendix" };
      if (/\/projects\/(?!index\.html$)[^/]+\.html$/.test(route)) return { key: "case-study", label: "Case study" };
      return { key: "other", label: "Page" };
    }

    function snippet(page, tokens) {
      var body = page.b || "";
      var at = -1;
      for (var i = 0; i < tokens.length && at < 0; i++) at = body.toLowerCase().indexOf(tokens[i]);
      if (at < 0) return body.slice(0, 150);
      var start = Math.max(0, at - 60);
      return (start ? "…" : "") + body.slice(start, start + 170).trim() + "…";
    }

    function render(query) {
      if (!pages) return;
      var tokens = query.toLowerCase().split(/\s+/).filter(function (t) { return t.length > 1; });
      list.textContent = "";
      if (!tokens.length) { status.textContent = ""; return; }
      var hits = [];
      pages.forEach(function (page) {
        var title = (page.t || "").toLowerCase();
        var headings = (page.h || "").toLowerCase();
        var description = (page.d || "").toLowerCase();
        var body = (page.b || "").toLowerCase();
        var score = 0;
        for (var i = 0; i < tokens.length; i++) {
          var token = tokens[i];
          var found = 0;
          if (title.indexOf(token) >= 0) found += 8;
          if (headings.indexOf(token) >= 0) found += 3;
          if (description.indexOf(token) >= 0) found += 2;
          if (body.indexOf(token) >= 0) found += 1;
          if (!found) return;
          score += found;
        }
        hits.push({ page: page, score: score });
      });
      hits.sort(function (a, b) { return b.score - a.score || a.page.t.localeCompare(b.page.t); });
      var total = hits.length;
      var activeType = typeControl.value;
      if (activeType !== "all") hits = hits.filter(function (hit) { return pageType(hit.page.u).key === activeType; });
      var scope = activeType === "all" ? "" : " in " + typeControl.options[typeControl.selectedIndex].textContent.toLowerCase();
      var across = activeType === "all" ? "" : " (" + total + " across all types)";
      status.textContent = hits.length
        ? hits.length + (hits.length === 1 ? " page matches “" : " pages match “") + query + "”" + scope + across
        : "No pages match “" + query + "”" + scope + "." + across;
      hits.forEach(function (hit) {
        var item = node("li");
        var type = pageType(hit.page.u);
        item.dataset.pageType = type.key;
        var badge = node("span", type.label);
        badge.className = "result-type";
        item.appendChild(badge);
        var link = node("a");
        link.href = hit.page.u;
        link.appendChild(node("span", hit.page.t));
        link.className = "result-title";
        item.appendChild(link);
        item.appendChild(node("span", hit.page.u.replace(/^.*\/docs\//, "").replace(/\.html$/, "").replace(/\//g, " / ")));
        item.appendChild(node("p", snippet(hit.page, tokens)));
        list.appendChild(item);
      });
    }

    function readLocation() {
      var params = new URLSearchParams(location.search);
      input.value = params.get("q") || "";
      var type = params.get("type") || "all";
      typeControl.value = ["all", "case-study", "report", "appendix", "other"].indexOf(type) >= 0 ? type : "all";
    }

    function writeLocation() {
      try {
        var url = new URL(location.href);
        if (input.value) url.searchParams.set("q", input.value); else url.searchParams.delete("q");
        if (typeControl.value !== "all") url.searchParams.set("type", typeControl.value); else url.searchParams.delete("type");
        history.replaceState(null, "", url.pathname + url.search + url.hash);
      } catch (e) { /* Search still works when URL updates are unavailable. */ }
    }

    readLocation();
    fetch("search-index.json").then(function (response) {
      if (!response.ok) throw new Error("no index");
      return response.json();
    }).then(function (data) {
      pages = data;
      typeControl.disabled = false;
      render(input.value);
    }).catch(function () { status.textContent = "Search is unavailable right now."; });

    input.addEventListener("input", function () { writeLocation(); render(input.value); });
    typeControl.addEventListener("change", function () { writeLocation(); render(input.value); });
    window.addEventListener("popstate", function () { readLocation(); render(input.value); });
    input.addEventListener("keydown", function (event) {
      if (event.key === "Escape") { input.value = ""; writeLocation(); render(""); }
    });
    input.form.addEventListener("submit", function (event) {
      event.preventDefault();
      writeLocation();
      render(input.value);
    });

    // A "/" shortcut lands here from another page; focus the field so the visitor can type.
    try {
      if (new URLSearchParams(location.search).get("focus") === "search") input.focus();
    } catch (e) {}
  })();

  // Press "/" anywhere outside a text field to open search. On the search page itself
  // the existing field is focused instead of reloading the page.
  (function () {
    var link = doc.querySelector('.nav-link[data-search-shortcut="/"]');
    if (!link) return;
    // The key cap is rendered hidden so it never advertises a shortcut that cannot work.
    var hint = link.querySelector(".key-hint");
    doc.addEventListener("keydown", function (event) {
      var altGraph = event.getModifierState && event.getModifierState("AltGraph");
      if (event.defaultPrevented || event.key !== "/" || event.metaKey ||
          (!altGraph && (event.ctrlKey || event.altKey))) return;
      var target = event.target;
      if (target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
      event.preventDefault();
      var input = doc.getElementById("site-search-input");
      if (input) { input.focus(); return; }
      var url = new URL(link.href, location.href);
      url.searchParams.set("focus", "search");
      location.href = url.pathname + url.search;
    });
    link.setAttribute("aria-keyshortcuts", "/");
    if (hint) hint.hidden = false;
  })();

  if (reduce) return;

  // Reading progress on technical reports. Scroll-driven CSS animation where supported.
  (function () {
    var active = doc.querySelector('.project-nav a[aria-current="page"]');
    var report = /\/report(\.html)?\/?$/.test(location.pathname) ||
      (active && /technical report/i.test(active.textContent));
    if (!report) return;
    var bar = doc.createElement("div");
    bar.className = "read-progress";
    bar.setAttribute("aria-hidden", "true");
    doc.body.appendChild(bar);
    var native = false;
    try { native = window.CSS && CSS.supports("animation-timeline: scroll()"); } catch (e) {}
    if (native) return;
    onScroll(function () {
      var max = root.scrollHeight - window.innerHeight;
      var ratio = max > 0 ? Math.min(1, Math.max(0, scrollTop() / max)) : 0;
      bar.style.setProperty("--read", ratio.toFixed(4));
    });
  })();

  // Project cards below the fold fade in as they arrive. Skipped on a deep link,
  // a reload or back/forward navigation, where the browser restores a scroll
  // position and revealing would make visible content flash.
  if (!("IntersectionObserver" in window) || location.hash || scrollTop() > 0) return;
  try {
    var nav = performance.getEntriesByType("navigation")[0];
    if (nav && (nav.type === "reload" || nav.type === "back_forward")) return;
  } catch (e) {}

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var el = entry.target;
      observer.unobserve(el);
      el.classList.add("is-in");
      setTimeout(function () { el.classList.remove("rv", "is-in"); el.style.removeProperty("--rv-i"); }, 1000);
    });
  }, { threshold: 0, rootMargin: "0px 0px -8% 0px" });

  var fold = window.innerHeight * 0.92;
  var grids = doc.querySelectorAll(".page .cards");
  Array.prototype.forEach.call(grids, function (grid) {
    var n = 0;
    Array.prototype.forEach.call(grid.children, function (card) {
      if (!card.classList.contains("card") || card.getBoundingClientRect().top < fold) return;
      card.style.setProperty("--rv-i", String(Math.min(n++, 3)));
      card.classList.add("rv");
      observer.observe(card);
    });
  });

  // Never print a card mid-fade.
  window.addEventListener("beforeprint", function () {
    Array.prototype.forEach.call(doc.querySelectorAll(".rv"), function (el) { el.classList.remove("rv", "is-in"); });
  });
})();
