/* Site enhancements: header hairline, reading progress on technical reports and a
   fade-in for project cards. Everything here is optional; the pages are complete
   without it. Nothing runs when the visitor asks for reduced motion. */
(function () {
  "use strict";
  var doc = document;
  var root = doc.documentElement;
  var reduce = false;
  try { reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}

  // Site search. The index is built at render time; without it the field stays a quiet input.
  (function () {
    var form = doc.querySelector(".site-search");
    var input = form && form.querySelector("input");
    var list = form && form.querySelector(".search-results");
    if (!form || !input || !list) return;
    var script = doc.querySelector('script[src*="assets/js/site.js"]');
    var src = script ? script.getAttribute("src").split("?")[0] : "assets/js/site.js";
    var indexUrl = src.replace(/assets\/js\/site\.js$/, "assets/search-index.json");
    var pages = null;
    function hide() { list.hidden = true; list.innerHTML = ""; }
    function show(items) {
      list.innerHTML = "";
      items.forEach(function (item) {
        var li = doc.createElement("li");
        var a = doc.createElement("a");
        a.href = item.url;
        var title = doc.createElement("span");
        title.className = "hit-title";
        title.textContent = item.title;
        a.appendChild(title);
        if (item.text) {
          var blurb = doc.createElement("span");
          blurb.className = "hit-text";
          blurb.textContent = item.text;
          a.appendChild(blurb);
        }
        li.appendChild(a);
        list.appendChild(li);
      });
      list.hidden = items.length === 0;
    }
    function ready(run) {
      if (pages) { run(); return; }
      fetch(indexUrl).then(function (res) { return res.ok ? res.json() : []; }).then(function (data) {
        pages = data || [];
        run();
      }).catch(function () { pages = []; });
    }
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      if (q.length < 2) { hide(); return; }
      ready(function () {
        var hits = [];
        for (var i = 0; i < pages.length && hits.length < 8; i++) {
          var page = pages[i];
          var hay = (page.title + " " + page.text).toLowerCase();
          if (hay.indexOf(q) !== -1) hits.push(page);
        }
        show(hits);
      });
    });
    doc.addEventListener("click", function (event) {
      if (!form.contains(event.target)) hide();
    });
    input.addEventListener("keydown", function (event) {
      if (event.key === "Escape") hide();
    });
    form.addEventListener("submit", function (event) { event.preventDefault(); });
  })();

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
