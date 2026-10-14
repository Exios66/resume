/* Site enhancements: header state, scroll reveal, stat count-up, diagram drawing,
   reading progress and live repository metadata. Everything here is optional;
   the pages are complete without it. Motion is skipped when the visitor asks
   for reduced motion. */
(function () {
  "use strict";
  var doc = document;
  var root = doc.documentElement;
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

  // Header: translucent with a hairline once the page has scrolled.
  var header = doc.querySelector(".site-header");
  if (header) {
    onScroll(function () {
      header.classList.toggle("is-scrolled", (window.pageYOffset || root.scrollTop) > 8);
    });
  }

  // Live repository metadata under the project tabs (not motion, so it runs either way).
  (function () {
    var nav = doc.querySelector(".project-nav");
    var code = nav && nav.querySelector('a[href*="github.com/Exios66/"]');
    if (!code || typeof fetch !== "function" || typeof AbortController !== "function") return;
    var match = /github\.com\/Exios66\/([A-Za-z0-9._-]+)/.exec(code.getAttribute("href") || "");
    if (!match) return;
    var repo = match[1].replace(/\.git$/, "");
    var key = "repo-meta:" + repo;
    var HOUR = 3600000, RETRY = 600000;

    /** Cached result for the repo, or null when absent, stale or storage is unavailable. */
    function cached() {
      try {
        var hit = JSON.parse(sessionStorage.getItem(key));
        if (hit && Date.now() - hit.t < (hit.ok ? HOUR : RETRY)) return hit;
      } catch (e) {}
      return null;
    }
    function store(value) {
      try { sessionStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
    }
    /** "3 days ago" style text for an ISO timestamp, or "" when it cannot be formed. */
    function ago(iso) {
      var then = Date.parse(iso);
      if (isNaN(then) || typeof Intl === "undefined" || !Intl.RelativeTimeFormat) return "";
      var seconds = Math.min(0, Math.round((then - Date.now()) / 1000));
      var units = [["year", 31536000], ["month", 2592000], ["week", 604800], ["day", 86400], ["hour", 3600], ["minute", 60]];
      var rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
      for (var i = 0; i < units.length; i++) {
        if (-seconds >= units[i][1]) return rtf.format(Math.round(seconds / units[i][1]), units[i][0]);
      }
      return rtf.format(0, "day");
    }
    var slot = null;
    /** The line's element, created once. Added up front so its row is reserved before data arrives. */
    function lineSlot() {
      if (!slot) {
        slot = doc.createElement("span");
        slot.className = "repo-meta";
        nav.appendChild(slot);
      }
      return slot;
    }
    function render(data) {
      var when = ago(data.pushed);
      if (!when) return;
      var line = lineSlot();
      var svg = doc.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("class", "icon");
      svg.setAttribute("aria-hidden", "true");
      svg.setAttribute("focusable", "false");
      var use = doc.createElementNS("http://www.w3.org/2000/svg", "use");
      use.setAttribute("href", "#i-clock");
      svg.appendChild(use);
      line.appendChild(svg);
      var text = "Updated " + when;
      if (data.stars > 0) text += " · ★ " + data.stars;
      line.appendChild(doc.createTextNode(text));
    }

    var hit = cached();
    if (hit) { if (hit.ok) render(hit); return; }
    lineSlot();
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, 4000);
    fetch("https://api.github.com/repos/Exios66/" + encodeURIComponent(repo), {
      signal: controller.signal,
      headers: { Accept: "application/vnd.github+json" }
    }).then(function (response) {
      if (!response.ok) throw new Error("status " + response.status);
      return response.json();
    }).then(function (json) {
      var data = { ok: true, t: Date.now(), pushed: json.pushed_at, stars: json.stargazers_count || 0 };
      store(data);
      render(data);
    }).catch(function () {
      store({ ok: false, t: Date.now() });
    }).then(function () { clearTimeout(timer); });
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
      var ratio = max > 0 ? Math.min(1, Math.max(0, (window.pageYOffset || root.scrollTop) / max)) : 0;
      bar.style.setProperty("--read", ratio.toFixed(4));
    });
  })();

  if (!("IntersectionObserver" in window)) return;

  // Scroll reveal, stat count-up and diagram drawing share one observer.
  var running = [];

  /** Parse "$0.004", "1,280", "89%" ... into pieces, or null for anything else. */
  function parseStat(text) {
    var m = /^([^0-9A-Za-z]*)(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?([^0-9]*)$/.exec(text.trim());
    if (!m || text !== text.trim()) return null;
    return {
      prefix: m[1], suffix: m[4], decimals: m[3] ? m[3].length : 0,
      grouped: m[2].indexOf(",") > -1, value: parseFloat(m[2].replace(/,/g, "") + (m[3] ? "." + m[3] : ""))
    };
  }
  function format(spec, n) {
    var parts = n.toFixed(spec.decimals).split(".");
    if (spec.grouped) parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return spec.prefix + parts.join(".") + spec.suffix;
  }
  function countUp(el) {
    var original = el.textContent;
    var spec = parseStat(original);
    if (!spec || !isFinite(spec.value)) return;
    var start = null;
    var job = { finish: function () { el.textContent = original; job.done = true; } };
    running.push(job);
    el.textContent = format(spec, 0);
    function step(now) {
      if (job.done) return;
      if (start === null) start = now;
      var t = Math.min(1, (now - start) / 900);
      if (t >= 1) { job.finish(); return; }
      el.textContent = format(spec, spec.value * (1 - Math.pow(1 - t, 3)));
      window.requestAnimationFrame(step);
    }
    window.requestAnimationFrame(step);
  }

  /** Prepare a diagram so its arrows can draw in. */
  function prepDiagram(fig) {
    var arrows = fig.querySelectorAll(".d-arrow");
    for (var i = 0; i < arrows.length; i++) {
      arrows[i].setAttribute("pathLength", "1");
      arrows[i].style.setProperty("--d", String(Math.min(i, 12)));
    }
    fig.classList.add("dg");
  }

  /** Trigger the effects for an element that has come into view. */
  function show(el) {
    el.classList.add("is-in");
    if (el.classList.contains("stat")) {
      var value = el.querySelector(".stat-value");
      if (value) countUp(value);
    }
    if (el.classList.contains("rv")) {
      var done = function () {
        // Diagrams keep "is-in" until their own cleanup, or the drawn state would blank.
        el.classList.remove("rv");
        if (!el.classList.contains("dg")) el.classList.remove("is-in");
        el.removeEventListener("transitionend", onEnd);
      };
      var onEnd = function (e) { if (e.target === el && e.propertyName === "opacity") done(); };
      el.addEventListener("transitionend", onEnd);
      setTimeout(done, 1400);
    }
    if (el.classList.contains("dg")) setTimeout(function () { el.classList.remove("dg", "is-in"); }, 1600);
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      show(entry.target);
    });
  }, { threshold: 0, rootMargin: "0px 0px -8% 0px" });

  var SELECTOR = ".page h2, .page .card, .page .stat, .page figure, .page table, .page .sample-doc, .page .caveat";
  var targets = doc.querySelectorAll(SELECTOR);
  var fold = window.innerHeight * 0.92;
  var index = new Map();
  Array.prototype.forEach.call(targets, function (el) {
    // Skip the hero and anything nested inside another revealed block.
    if (el.closest(".hero") || (el.parentElement && el.parentElement.closest(SELECTOR))) return;
    var parent = el.parentNode;
    var grid = parent && parent.classList && (parent.classList.contains("cards") || parent.classList.contains("stats"));
    if (grid) {
      var n = index.get(parent) || 0;
      index.set(parent, n + 1);
      el.style.setProperty("--rv-i", String(Math.min(n, 6)));
    }
    var isDiagram = el.classList.contains("diagram");
    if (isDiagram) prepDiagram(el);
    var top = el.getBoundingClientRect().top;
    if (top < fold) {
      // Already on screen: never hidden. Play the effects straight away.
      if (isDiagram || el.classList.contains("stat")) {
        void el.offsetWidth;
        window.requestAnimationFrame(function () { show(el); });
      }
      return;
    }
    el.classList.add("rv");
    observer.observe(el);
  });

  window.addEventListener("beforeprint", function () {
    running.forEach(function (job) { if (!job.done) job.finish(); });
  });
})();
