/* Site enhancements: header hairline, reading progress on technical reports and a
   fade-in for project cards. Everything here is optional; the pages are complete
   without it. Nothing runs when the visitor asks for reduced motion. */
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

  // Site search: filter the generated page index and render results in place.
  (function () {
    var input = doc.getElementById("site-search-input");
    var list = doc.getElementById("search-results");
    var status = doc.getElementById("search-status");
    if (!input || !list || !status) return;
    var pages = null;

    function node(tag, text) {
      var el = doc.createElement(tag);
      if (text) el.textContent = text;
      return el;
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
      status.textContent = hits.length
        ? hits.length + (hits.length === 1 ? " page matches “" : " pages match “") + query + "”"
        : "No pages match “" + query + "”.";
      hits.forEach(function (hit) {
        var item = node("li");
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

    var params = new URLSearchParams(location.search);
    var initial = params.get("q") || "";
    input.value = initial;
    fetch("search-index.json").then(function (response) {
      if (!response.ok) throw new Error("no index");
      return response.json();
    }).then(function (data) {
      pages = data;
      render(input.value);
    }).catch(function () { status.textContent = "Search is unavailable right now."; });

    input.addEventListener("input", function () { render(input.value); });
    input.addEventListener("keydown", function (event) {
      if (event.key === "Escape") { input.value = ""; render(""); }
    });
    input.form.addEventListener("submit", function (event) {
      event.preventDefault();
      try { history.replaceState(null, "", "?q=" + encodeURIComponent(input.value)); } catch (e) {}
      render(input.value);
    });
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
