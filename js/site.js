/* Soil Food Web Foundation: site.js
   One small script, no libraries. Each block checks for its own markup and
   does nothing when the page does not have it. */

/* 1. Review mode: ?review highlights draft text ---------------------------- */
(function () {
  "use strict";
  if (/[?&]review\b/.test(location.search)) document.documentElement.classList.add("is-review");
})();

/* 2. Off-canvas menu ---------------------------------------------------------- */
(function () {
  "use strict";
  var btn = document.querySelector("[data-menu-open]");
  var ocm = document.getElementById("ocm");
  if (!btn || !ocm) return;
  var last = null;
  function open() {
    last = document.activeElement;
    ocm.hidden = false;
    requestAnimationFrame(function () { ocm.classList.add("is-open"); });
    document.body.classList.add("menu-open");
    btn.setAttribute("aria-expanded", "true");
    var c = ocm.querySelector("[data-menu-close]");
    if (c) c.focus();
  }
  function close() {
    ocm.classList.remove("is-open");
    document.body.classList.remove("menu-open");
    btn.setAttribute("aria-expanded", "false");
    setTimeout(function () { ocm.hidden = true; }, 320);
    if (last) last.focus();
  }
  btn.addEventListener("click", open);
  ocm.addEventListener("click", function (e) {
    if (e.target.closest("[data-menu-close]") || e.target.classList.contains("ocm__scrim")) close();
    else if (e.target.closest("a")) close();
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && ocm.classList.contains("is-open")) close(); });
})();

/* 3. Desktop dropdowns: click and keyboard as well as hover ------------------ */
(function () {
  "use strict";
  var tops = document.querySelectorAll(".nav__top");
  Array.prototype.forEach.call(tops, function (b) {
    b.addEventListener("click", function () {
      var li = b.parentNode, isOpen = li.classList.toggle("open");
      b.setAttribute("aria-expanded", String(isOpen));
      Array.prototype.forEach.call(tops, function (o) {
        if (o !== b) { o.parentNode.classList.remove("open"); o.setAttribute("aria-expanded", "false"); }
      });
    });
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".nav")) Array.prototype.forEach.call(tops, function (o) { o.parentNode.classList.remove("open"); o.setAttribute("aria-expanded", "false"); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") Array.prototype.forEach.call(tops, function (o) { o.parentNode.classList.remove("open"); o.setAttribute("aria-expanded", "false"); });
  });
})();

/* 4. Course scroller arrows ------------------------------------------------------ */
(function () {
  "use strict";
  Array.prototype.forEach.call(document.querySelectorAll("[data-scroller]"), function (wrap) {
    var list = wrap.querySelector(".scroller");
    Array.prototype.forEach.call(wrap.querySelectorAll("[data-scroll]"), function (b) {
      b.addEventListener("click", function () {
        list.scrollBy({ left: Number(b.getAttribute("data-scroll")) * list.clientWidth * 0.8, behavior: "smooth" });
      });
    });
  });
})();

/* 5. Filterable lists: chips, search box, topic select ----------------------------
   Container [data-filter]; items [data-item] carry data-group (chip key),
   data-topics (space separated) and data-text (lowercase search text). */
(function () {
  "use strict";
  Array.prototype.forEach.call(document.querySelectorAll("[data-filter]"), function (root) {
    var items = root.querySelectorAll("[data-item]");
    var chips = root.querySelectorAll("[data-chip]");
    var q = root.querySelector("[data-q]");
    var topic = root.querySelector("[data-topic]");
    var count = root.querySelector("[data-count]");
    var empty = root.querySelector("[data-empty]");
    var groups = root.querySelectorAll("[data-group-block]");
    var state = { chip: "", q: "", topic: "" };
    function apply() {
      var n = 0;
      Array.prototype.forEach.call(items, function (it) {
        var ok = (!state.chip || (" " + it.getAttribute("data-group") + " ").indexOf(" " + state.chip + " ") > -1) &&
                 (!state.topic || (" " + (it.getAttribute("data-topics") || "") + " ").indexOf(" " + state.topic + " ") > -1) &&
                 (!state.q || (it.getAttribute("data-text") || it.textContent.toLowerCase()).indexOf(state.q) > -1);
        it.hidden = !ok;
        if (ok) n++;
      });
      Array.prototype.forEach.call(groups, function (g) { g.hidden = !g.querySelector("[data-item]:not([hidden])"); });
      if (count) count.textContent = n + (n === 1 ? " " + (count.getAttribute("data-one") || "result") : " " + (count.getAttribute("data-many") || "results"));
      if (empty) empty.hidden = n > 0;
    }
    Array.prototype.forEach.call(chips, function (c) {
      c.addEventListener("click", function () {
        state.chip = c.getAttribute("data-chip");
        Array.prototype.forEach.call(chips, function (o) { o.setAttribute("aria-pressed", String(o === c)); });
        apply();
      });
    });
    // Hover or focus a path chip: the matching programs lift, the rest step back.
    function preview(key) {
      root.classList.toggle("is-previewing", !!key);
      Array.prototype.forEach.call(items, function (it) {
        it.classList.toggle("is-match", !!key && (" " + it.getAttribute("data-group") + " ").indexOf(" " + key + " ") > -1);
      });
    }
    Array.prototype.forEach.call(chips, function (c) {
      var key = c.getAttribute("data-chip");
      if (key === "all") return;
      function on() { if (c.getAttribute("aria-pressed") !== "true") preview(key); }
      function off() { preview(""); }
      c.addEventListener("mouseenter", on); c.addEventListener("focus", on);
      c.addEventListener("mouseleave", off); c.addEventListener("blur", off); c.addEventListener("click", off);
    });
    if (q) q.addEventListener("input", function () { state.q = q.value.trim().toLowerCase(); apply(); });
    if (topic) topic.addEventListener("change", function () { state.topic = topic.value; apply(); });
    var form = root.querySelector("form");
    if (form) form.addEventListener("submit", function (e) { e.preventDefault(); });
    var hash = location.hash.replace("#", "");
    Array.prototype.forEach.call(chips, function (c) { if (hash && c.getAttribute("data-chip") === hash) c.click(); });
    apply();
  });
})();

/* 5b. Publications: search, four dropdowns and a sort, combined with AND -----------
   State lives in the query string (?topic=compost&region=europe&q=tea), so a
   filtered view can be shared as a link and the back button steps through it.
   The page renders the full list grouped by collection, oldest first; without
   this script that is what a reader gets, and the filter bar stays hidden. */
(function () {
  "use strict";
  var form = document.querySelector("[data-pubs-filter]");
  var root = document.querySelector("[data-pubs]");
  if (!form || !root || !window.URLSearchParams) return;
  var FIELDS = ["q", "collection", "topic", "study", "region", "sort"];
  var FILTERS = ["collection", "topic", "study", "region"];
  var items = Array.prototype.slice.call(root.querySelectorAll(".pub"));
  var groups = Array.prototype.slice.call(root.querySelectorAll("[data-pubs-group]"));
  var flat = root.querySelector("[data-pubs-flat]");
  var empty = root.querySelector("[data-pubs-empty]");
  var bar = document.querySelector("[data-pubs-bar]");
  var status = document.querySelector("[data-pubs-status]");
  var clears = document.querySelectorAll("[data-pubs-clear]");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Accents folded, so "Ostrom" finds "Öström" and the other way round.
  function fold(s) {
    s = String(s).toLowerCase();
    return s.normalize ? s.normalize("NFD").replace(/[̀-ͯ]/g, "") : s;
  }
  // What the search reads: title, authors and citation, summary, useful for,
  // topics and year. Not the labels, so "summary" does not match everything.
  items.forEach(function (it) {
    var parts = [it.getAttribute("data-year")];
    Array.prototype.forEach.call(it.querySelectorAll(".pub__title, .entry__line, [data-s], .chip--tag"),
      function (el) { parts.push(el.textContent); });
    it._text = fold(parts.join(" "));
    it._home = it.parentNode;
  });

  function read() {
    var p = new URLSearchParams(location.search), s = {};
    FIELDS.forEach(function (k) { s[k] = p.get(k) || ""; });
    return s;
  }
  function toControls(s) {
    FIELDS.forEach(function (k) {
      var el = form.elements[k];
      el.value = s[k];
      if (el.value !== s[k]) { el.value = ""; s[k] = ""; }   // a value from an old link that no longer exists
    });
  }
  function fromControls() {
    var s = {};
    FIELDS.forEach(function (k) { s[k] = form.elements[k].value; });
    return s;
  }
  function write(s, push) {
    var p = new URLSearchParams();
    FIELDS.forEach(function (k) { if (s[k].trim()) p.set(k, s[k].trim()); });
    var qs = p.toString();
    var url = location.pathname + (qs ? "?" + qs : "") + location.hash;
    if (url === location.pathname + location.search + location.hash) return;
    history[push ? "pushState" : "replaceState"](null, "", url);
  }
  function holds(it, k, v) {
    return (" " + (it.getAttribute("data-p-" + k) || "") + " ").indexOf(" " + v + " ") > -1;
  }

  function apply(s) {
    var words = fold(s.q).split(/\s+/).filter(Boolean);
    var shown = 0;
    items.forEach(function (it) {
      var ok = true;
      FILTERS.forEach(function (k) { if (ok && s[k] && !holds(it, k, s[k])) ok = false; });
      for (var i = 0; ok && i < words.length; i++) if (it._text.indexOf(words[i]) < 0) ok = false;
      it.hidden = !ok;
      if (ok) shown++;
    });
    // Oldest first keeps the collection headings; newest first is one flat
    // list. data-i is each card's place in the default order.
    var newest = s.sort === "newest";
    items.slice().sort(function (a, b) {
      var d = newest ? b.getAttribute("data-year") - a.getAttribute("data-year") : 0;
      return d || a.getAttribute("data-i") - b.getAttribute("data-i");
    }).forEach(function (it) { (newest ? flat : it._home).appendChild(it); });
    flat.hidden = !newest || shown === 0;
    groups.forEach(function (ul) {
      var head = root.querySelector('[data-pubs-head="' + ul.getAttribute("data-pubs-group") + '"]');
      var any = !newest && !!ul.querySelector(".pub:not([hidden])");
      ul.hidden = !any; head.hidden = !any;
    });
    var filtered = !!(s.q.trim() || s.collection || s.topic || s.study || s.region);
    status.textContent = "Showing " + shown + " of " + items.length + " publications";
    Array.prototype.forEach.call(clears, function (b) { b.hidden = !filtered; });
    empty.hidden = shown !== 0;
  }

  function update(push) { var s = fromControls(); write(s, push); apply(s); }

  var timer;
  form.elements.q.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { update(false); }, 200);
  });
  // One history step per search, not per keystroke.
  form.elements.q.addEventListener("change", function () { update(true); });
  FIELDS.slice(1).forEach(function (k) {
    form.elements[k].addEventListener("change", function () { update(true); });
  });
  form.addEventListener("submit", function (e) { e.preventDefault(); update(true); });

  Array.prototype.forEach.call(clears, function (b) {
    b.addEventListener("click", function () {
      ["q"].concat(FILTERS).forEach(function (k) { form.elements[k].value = ""; });
      update(true);
      form.elements.q.focus();
    });
  });

  // A topic chip on a card sets the Topic filter to that tag.
  root.addEventListener("click", function (e) {
    var chip = e.target.closest ? e.target.closest("a[data-tag]") : null;
    if (!chip || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    e.preventDefault();
    form.elements.topic.value = chip.getAttribute("data-tag");
    update(true);
    form.scrollIntoView({ block: "start", behavior: reduce ? "auto" : "smooth" });
    form.elements.topic.focus({ preventScroll: true });
  });

  window.addEventListener("popstate", function () { var s = read(); toControls(s); apply(s); });

  form.hidden = false;
  bar.hidden = false;
  var start = read();
  toControls(start);
  apply(start);
})();

/* 6. Contact form (mockup): required fields, then a thank-you ---------------------- */
(function () {
  "use strict";
  var form = document.querySelector("[data-contact-form]");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var first = null;
    Array.prototype.forEach.call(form.querySelectorAll("[required]"), function (f) {
      var field = f.closest(".field"), err = field.querySelector(".field__error");
      var bad = !f.value.trim() || (f.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value.trim()));
      field.classList.toggle("has-error", bad);
      f.setAttribute("aria-invalid", String(bad));
      if (err) err.hidden = !bad;
      if (bad && !first) first = f;
    });
    if (first) { first.focus(); return; }
    var done = document.querySelector("[data-contact-done]");
    form.hidden = true;
    done.hidden = false;
    done.focus();
  });
})();

/* 7. Copy email button ----------------------------------------------------------- */
(function () {
  "use strict";
  Array.prototype.forEach.call(document.querySelectorAll("[data-copy]"), function (b) {
    var label = b.textContent;
    b.addEventListener("click", function () {
      var text = b.getAttribute("data-copy");
      var done = function () { b.textContent = "Copied"; setTimeout(function () { b.textContent = label; }, 2000); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, done);
      else done();
    });
  });
})();

/* 8. Newsletter (mockup): marks the form subscribed ------------------------------- */
(function () {
  "use strict";
  Array.prototype.forEach.call(document.querySelectorAll("[data-newsletter]"), function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type="email"]');
      if (!input || !input.value) { if (input) input.focus(); return; }
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.textContent = "Subscribed"; }
      input.disabled = true;
    });
  });
})();

/* 9. Header "Subscribe" link: focus the footer newsletter field -------------------- */
(function () {
  "use strict";
  Array.prototype.forEach.call(document.querySelectorAll('a[href="#newsletter"]'), function (a) {
    a.addEventListener("click", function () {
      var i = document.getElementById("newsletter-email");
      if (i) setTimeout(function () { i.focus({ preventScroll: true }); }, 400);
    });
  });
})();

/* 10. Video facade: swap the thumbnail for the player on click ------------------ */
(function () {
  "use strict";
  Array.prototype.forEach.call(document.querySelectorAll("[data-embed]"), function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var f = document.createElement("iframe");
      f.src = a.getAttribute("data-embed") + (a.getAttribute("data-embed").indexOf("?") > -1 ? "&" : "?") + "autoplay=1";
      f.title = a.getAttribute("data-title") || "Video";
      f.allow = "autoplay; fullscreen; picture-in-picture";
      f.setAttribute("allowfullscreen", "");
      var wrap = document.createElement("div");
      wrap.className = "embed";
      wrap.appendChild(f);
      a.parentNode.replaceChild(wrap, a);
      f.focus();
    });
  });
})();

// Workshops: country and year filters (same behaviour as the staging plugin).
(function () {
  var root = document.querySelector("[data-sfw-workshops]");
  if (!root) return;
  var country = "", year = "", chips = root.querySelectorAll("[data-sfw-country]"), sel = root.querySelector("[data-sfw-year]");
  function apply() {
    var n = { upcoming: 0, past: 0 };
    root.querySelectorAll("[data-sfw-workshop-card]").forEach(function (c) {
      var show = (!country || c.dataset.country === country) && (!year || c.dataset.year === year);
      c.classList.toggle("is-hidden", !show);
      if (show) n[c.dataset.bucket]++;
    });
    ["upcoming", "past"].forEach(function (b) {
      var m = root.querySelector("[data-sfw-empty-" + b + "]");
      if (m) { m.hidden = n[b] > 0; m.classList.toggle("is-hidden", n[b] > 0); }
    });
  }
  chips.forEach(function (b) {
    b.setAttribute("aria-pressed", b.classList.contains("is-active"));
    b.addEventListener("click", function () {
      country = b.dataset.sfwCountry;
      chips.forEach(function (x) { x.classList.toggle("is-active", x === b); x.setAttribute("aria-pressed", x === b); });
      apply();
    });
  });
  if (sel) sel.addEventListener("change", function () { year = sel.value; apply(); });
  // map pins: pick that country's chip, then scroll to the list
  root.querySelectorAll("[data-sfw-pin]").forEach(function (p) {
    p.addEventListener("click", function (ev) {
      ev.preventDefault();
      var c = root.querySelector('[data-sfw-country="' + p.dataset.sfwPin + '"]');
      if (c) c.click();
      root.querySelectorAll("[data-sfw-pin]").forEach(function (x) { x.classList.toggle("is-on", x === p); });
      var t = document.getElementById("workshop-list"); if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
  chips.forEach(function (b) { b.addEventListener("click", function () { root.querySelectorAll("[data-sfw-pin]").forEach(function (x) { x.classList.toggle("is-on", x.dataset.sfwPin === b.dataset.sfwCountry); }); }); });
})();

// Workshop photo galleries: open a photo larger, arrows move, Escape closes.
(function () {
  var g = document.querySelector("[data-ws-gallery]");
  if (!g || !window.HTMLDialogElement) return;
  var imgs = Array.prototype.slice.call(g.querySelectorAll("img")), i = 0;
  var d = document.createElement("dialog");
  d.className = "ws-lightbox";
  d.innerHTML = '<img alt=""><p></p><button type="button" data-prev aria-label="Previous photo">&#8249;</button><button type="button" data-next aria-label="Next photo">&#8250;</button><button type="button" data-close aria-label="Close">&times;</button>';
  document.body.appendChild(d);
  var big = d.querySelector("img"), cap = d.querySelector("p");
  function largest(im) {
    var s = (im.getAttribute("srcset") || "").split(",").map(function (x) { return x.trim().split(" "); });
    s.sort(function (a, b) { return parseInt(b[1] || 0, 10) - parseInt(a[1] || 0, 10); });
    return s.length && s[0][0] ? s[0][0] : im.currentSrc || im.src;
  }
  function show(k) { i = (k + imgs.length) % imgs.length; big.src = largest(imgs[i]); big.alt = imgs[i].alt; var li = imgs[i].closest("li"); cap.textContent = (li && li.dataset.caption) || imgs[i].alt; }
  imgs.forEach(function (im, k) {
    im.tabIndex = 0;
    im.setAttribute("role", "button");
    im.addEventListener("click", function () { show(k); d.showModal(); });
    im.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); show(k); d.showModal(); } });
  });
  d.querySelector("[data-prev]").addEventListener("click", function () { show(i - 1); });
  d.querySelector("[data-next]").addEventListener("click", function () { show(i + 1); });
  d.querySelector("[data-close]").addEventListener("click", function () { d.close(); });
  d.addEventListener("click", function (ev) { if (ev.target === d) d.close(); });
  d.addEventListener("keydown", function (ev) { if (ev.key === "ArrowLeft") show(i - 1); else if (ev.key === "ArrowRight") show(i + 1); });
})();

/* Programme plate: hovering or focusing a circle shows its course in the panel and dims the rest. */
(function () {
  document.querySelectorAll("[data-pp]").forEach(function (w) {
    var svg = w.querySelector("svg"), k = w.querySelector(".pp-detail__k"), n = w.querySelector(".pp-detail__n"), l = w.querySelector(".pp-detail__l");
    var d0 = [k.textContent, n.textContent, l.textContent];
    function on(a) {
      svg.querySelectorAll("a.is-on").forEach(function (x) { x.classList.remove("is-on"); });
      if (!a) { svg.classList.remove("is-dim"); k.textContent = d0[0]; n.textContent = d0[1]; l.textContent = d0[2]; return; }
      a.classList.add("is-on"); svg.classList.add("is-dim");
      k.textContent = a.dataset.ppKicker || ""; n.textContent = a.dataset.ppName || ""; l.textContent = a.dataset.ppLine || "";
    }
    svg.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("mouseenter", function () { on(a); });
      a.addEventListener("focus", function () { on(a); });
    });
    svg.addEventListener("mouseleave", function () { on(null); });
  });
})();

/* About timeline: grow the hypha line and mark each year as the reader reaches it. */
(function () {
  "use strict";
  var lines = document.querySelectorAll(".timeline");
  if (!lines.length || (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches)) return;
  document.documentElement.classList.add("js-grow");
  function draw() {
    var mark = window.innerHeight * 0.62;
    Array.prototype.forEach.call(lines, function (tl) {
      var r = tl.getBoundingClientRect();
      tl.style.setProperty("--grow", String(Math.max(0, Math.min(1, (mark - r.top) / r.height))));
      Array.prototype.forEach.call(tl.children, function (li) {
        li.classList.toggle("is-reached", li.getBoundingClientRect().top + 12 < mark);
      });
    });
  }
  var ticking = false;
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; draw(); }); } }, { passive: true });
  window.addEventListener("resize", draw);
  draw();
})();

/* Things that rise into place once, when they first come into view. */
(function () {
  "use strict";
  var els = document.querySelectorAll("[data-rise]");
  if (!els.length || !("IntersectionObserver" in window)) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  document.documentElement.classList.add("js-rise");
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
  }, { threshold: 0.25 });
  Array.prototype.forEach.call(els, function (el) { io.observe(el); });
})();

/* Publications, research map: papers joined to their topics and co-authors, laid out by a small force simulation. */
(function () {
  "use strict";
  var root = document.querySelector("[data-research-map]");
  if (!root) return;
  var D = JSON.parse(root.querySelector("[data-rm-data]").textContent);
  var svg = root.querySelector("[data-rm-svg]"), panel = root.querySelector("[data-rm-panel]"), NS = "http://www.w3.org/2000/svg";
  var FC = {}; D.facets.forEach(function (f, i) { FC[f] = "var(--f" + i + ")"; });
  var state = { set: "elaine", people: true, facets: {}, q: "", sel: null };
  D.facets.forEach(function (f) { state.facets[f] = true; });
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var W = 1000, H = 760, view = { x: 0, y: 0, k: 1 }, nodes = [], links = [], byId = {}, g, gl, gn, alpha = 1, raf = 0;
  var pos = {}; // keep positions between rebuilds
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function el(n, a) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); return e; }

  function build() {
    var facetOf = {}; D.topics.forEach(function (t) { facetOf[t.name] = t.facet; });
    var papers = D.papers.filter(function (p) { return (state.set === "all" || p.c === "elaine") && p.topics.some(function (t) { return state.facets[facetOf[t]]; }); });
    var used = {}, deg = {};
    nodes = []; links = []; byId = {};
    papers.forEach(function (p) {
      var n = { id: p.id, kind: "paper", p: p, r: 4 };
      nodes.push(n);
      p.topics.forEach(function (t) { if (!state.facets[facetOf[t]]) return; links.push({ s: p.id, t: "t:" + t }); used["t:" + t] = 1; deg["t:" + t] = (deg["t:" + t] || 0) + 1; });
      if (state.people) p.names.forEach(function (a) { if (D.people.some(function (x) { return x.name === a; })) { links.push({ s: p.id, t: "a:" + a }); used["a:" + a] = 1; deg["a:" + a] = (deg["a:" + a] || 0) + 1; } });
    });
    D.topics.forEach(function (t) { if (used[t.id]) nodes.push({ id: t.id, kind: "topic", t: t, r: 8 + Math.sqrt(deg[t.id]) * 3.2 }); });
    if (state.people) D.people.forEach(function (a) { if (used[a.id]) nodes.push({ id: a.id, kind: "person", a: a, r: 6 + Math.sqrt(deg[a.id]) * 2 }); });
    nodes.forEach(function (n) {
      byId[n.id] = n; var o = pos[n.id], ang = Math.random() * 6.283, rad = n.kind === "paper" ? 120 : 300;
      if (n.kind === "topic") { ang = (D.facets.indexOf(n.t.facet) + Math.random() * .8) / D.facets.length * 6.283; }
      n.x = o ? o.x : W / 2 + Math.cos(ang) * rad * 1.5 * (0.6 + Math.random() * .5); n.y = o ? o.y : H / 2 + Math.sin(ang) * rad * .55 * (0.6 + Math.random() * .5); n.vx = 0; n.vy = 0;
      n.nb = [];
    });
    links = links.filter(function (l) { return byId[l.s] && byId[l.t]; });
    links.forEach(function (l) { l.a = byId[l.s]; l.b = byId[l.t]; l.a.nb.push(l.b); l.b.nb.push(l.a); });
    state.sel = null; svg.classList.remove("is-focus"); panel.innerHTML = panel.dataset.intro || panel.innerHTML; draw(); alpha = 1; fitted = false; if (reduce) { for (var i = 0; i < 300; i++) tick(); paint(); fitted = true; fit(); } else kick();
    list();
  }

  function draw() {
    var bx = svg.getBoundingClientRect(); if (bx.width) H = Math.round(W * bx.height / bx.width);
    svg.innerHTML = ""; svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    g = el("g", {}); gl = el("g", {}); gn = el("g", {}); g.appendChild(gl); g.appendChild(gn); svg.appendChild(g);
    links.forEach(function (l) { l.el = el("line", {}); gl.appendChild(l.el); });
    nodes.sort(function (a, b) { return (a.kind === "paper") - (b.kind === "paper"); }).reverse();
    nodes.forEach(function (n) {
      var e = el("g", { "class": "n n--" + n.kind + (n.kind === "paper" && n.p.c !== "elaine" ? " is-field" : "") });
      if (n.kind === "paper") e.appendChild(el("circle", { r: 9, "class": "hit" }));
      var c = el("circle", { r: n.r });
      if (n.kind === "topic") c.setAttribute("style", "fill:" + FC[n.t.facet]);
      e.appendChild(c);
      if (n.kind !== "paper") {
        e.setAttribute("tabindex", "0"); e.setAttribute("role", "button");
        e.setAttribute("aria-label", n.kind === "topic" ? n.t.name + ", topic" : n.a.name + ", colleague");
        var tx = el("text", { y: n.r + 13, "text-anchor": "middle" }); tx.textContent = n.kind === "topic" ? n.t.name : n.a.name; e.appendChild(tx);
      } else { var ti = el("title", {}); ti.textContent = n.p.t + " (" + n.p.y + ")"; e.appendChild(ti); }
      n.el = e; gn.appendChild(e);
      e.addEventListener("mouseenter", function () { hot(n); tipShow(n); });
      e.addEventListener("mousemove", tipMove);
      e.addEventListener("mouseleave", function () { hot(state.sel ? byId[state.sel] : null); tip.hidden = true; });
      e.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); select(n); } });
      e.addEventListener("focus", function () { hot(n); });
      e.addEventListener("pointerdown", function (ev) { dragN = n; ev.stopPropagation(); start(ev); });
    });
    applyView(); paint(); search();
  }

  function tick() {
    var i, j, a, b, dx, dy, d2, d, f, k = alpha;
    for (i = 0; i < nodes.length; i++) for (j = i + 1; j < nodes.length; j++) {
      a = nodes[i]; b = nodes[j]; dx = b.x - a.x; dy = b.y - a.y; d2 = dx * dx + dy * dy || .01;
      if (d2 > 160000) continue;
      f = (a.kind === "paper" && b.kind === "paper" ? 140 : a.kind !== "paper" && b.kind !== "paper" ? 5200 : 700) * k / d2; d = Math.sqrt(d2);
      a.vx -= dx / d * f; a.vy -= dy / d * f; b.vx += dx / d * f; b.vy += dy / d * f;
      var m = a.r + b.r + 3; if (d < m) { var o = (m - d) / d * .5; a.x -= dx * o; a.y -= dy * o; b.x += dx * o; b.y += dy * o; }
    }
    links.forEach(function (l) {
      a = l.a; b = l.b; dx = b.x - a.x; dy = b.y - a.y; d = Math.sqrt(dx * dx + dy * dy) || 1;
      var len = l.b.kind === "person" ? 95 : 80, s = (d - len) / d * .03 * k;
      a.vx += dx * s; a.vy += dy * s; b.vx -= dx * s * .35; b.vy -= dy * s * .35;
    });
    nodes.forEach(function (n) {
      var gr = n.nb.length < 2 ? 4 : 1; n.vx += (W / 2 - n.x) * .0006 * k * gr; n.vy += (H / 2 - n.y) * .0032 * k * gr;
      if (n === dragN) { n.vx = n.vy = 0; return; }
      n.vx *= .82; n.vy *= .82; n.x += n.vx; n.y += n.vy;
    });
    alpha *= .985;
  }
  function paint() {
    links.forEach(function (l) { l.el.setAttribute("x1", l.a.x.toFixed(1)); l.el.setAttribute("y1", l.a.y.toFixed(1)); l.el.setAttribute("x2", l.b.x.toFixed(1)); l.el.setAttribute("y2", l.b.y.toFixed(1)); });
    nodes.forEach(function (n) { n.el.setAttribute("transform", "translate(" + n.x.toFixed(1) + "," + n.y.toFixed(1) + ")"); pos[n.id] = { x: n.x, y: n.y }; });
  }
  function fit() {
    if (!nodes.length) return;
    var xs = nodes.map(function (n) { return n.x; }).sort(function (a, b) { return a - b; }), ys = nodes.map(function (n) { return n.y; }).sort(function (a, b) { return a - b; });
    var q = function (a, f) { return a[Math.max(0, Math.min(a.length - 1, Math.round(f * (a.length - 1))))]; };
    var x0 = q(xs, .02) - 40, x1 = q(xs, .98) + 40, y0 = q(ys, .02) - 30, y1 = q(ys, .98) + 40;
    var k = Math.min(2.2, Math.min((W - 60) / (x1 - x0), (H - 60) / (y1 - y0)));
    view = { k: k, x: W / 2 - (x0 + x1) / 2 * k, y: H / 2 - (y0 + y1) / 2 * k }; applyView();
  }
  var fitted = false;
  function loop() { tick(); paint(); if (!fitted && alpha < .25) { fitted = true; fit(); } if (alpha > .02) raf = requestAnimationFrame(loop); else { raf = 0; if (fitted === true) { fitted = 2; fit(); } } }
  function kick() { alpha = Math.max(alpha, .3); if (!raf) raf = requestAnimationFrame(loop); }

  function hot(n) {
    svg.classList.toggle("is-focus", !!n);
    nodes.forEach(function (m) { m.el.classList.remove("is-hot"); });
    links.forEach(function (l) { l.el.classList.remove("is-hot"); });
    if (!n) return;
    n.el.classList.add("is-hot");
    links.forEach(function (l) { if (l.a === n || l.b === n) { l.el.classList.add("is-hot"); l.a.el.classList.add("is-hot"); l.b.el.classList.add("is-hot"); } });
  }

  function papersOf(n) { return n.nb.filter(function (m) { return m.kind === "paper"; }).map(function (m) { return m.p; }).sort(function (a, b) { return a.y - b.y; }); }
  function plist(ps) { return "<ul>" + ps.map(function (p) { return '<li><a href="' + esc(p.href) + '">' + esc(p.t) + "</a> <span>" + p.y + "</span></li>"; }).join("") + "</ul>"; }
  function related(n, kind) {
    var c = {}; n.nb.forEach(function (p) { p.nb.forEach(function (m) { if (m !== n && m.kind === kind) c[m.id] = (c[m.id] || 0) + 1; }); });
    return Object.keys(c).sort(function (a, b) { return c[b] - c[a]; }).slice(0, 6).map(function (id) { return '<button type="button" class="linkish" data-rm-go="' + esc(id) + '">' + esc(byId[id].kind === "topic" ? byId[id].t.name : byId[id].a.name) + "</button> <span>(" + c[id] + ")</span>"; }).join(", ");
  }
  function select(n) {
    if (state.sel && byId[state.sel]) byId[state.sel].el.classList.remove("is-sel");
    state.sel = n ? n.id : null; hot(n);
    if (!n) return;
    n.el.classList.add("is-sel");
    var h;
    if (n.kind === "topic") {
      var ps = papersOf(n);
      h = '<p class="rm-panel__k">' + esc(n.t.facet) + '</p><h3 class="rm-panel__h">' + esc(n.t.name) + "</h3>" + (n.t.def ? "<p>" + esc(n.t.def.charAt(0).toUpperCase() + n.t.def.slice(1)) + "</p>" : "") +
        '<p class="meta">' + ps.length + " paper" + (ps.length === 1 ? "" : "s") + (ps.length ? ", " + ps[0].y + " to " + ps[ps.length - 1].y : "") + "</p>" +
        "<p><strong>Often studied with:</strong> " + related(n, "topic") + "</p>" + plist(ps);
    } else if (n.kind === "person") {
      var qs = papersOf(n);
      h = '<p class="rm-panel__k">Colleague</p><h3 class="rm-panel__h">' + esc(n.a.name) + "</h3>" +
        '<p class="meta">' + n.a.n + " papers with Dr. Ingham" + (qs.length ? ", " + qs[0].y + " to " + qs[qs.length - 1].y : "") + "</p>" +
        "<p><strong>Topics together:</strong> " + related(n, "topic") + "</p>" + plist(qs);
    } else {
      var p = n.p;
      h = '<p class="rm-panel__k">' + esc(p.type) + " &middot; " + p.y + '</p><h3 class="rm-panel__h"><a href="' + esc(p.href) + '">' + esc(p.t) + "</a></h3>" +
        '<p class="meta">' + esc(p.authors) + (p.cite ? ". " + esc(p.cite) : "") + "</p><p>" + esc(p.s) + "</p>" +
        (p.u ? "<p><strong>Useful for:</strong> " + esc(p.u) + "</p>" : "") +
        "<p><strong>Threads:</strong> " + n.nb.map(function (m) { return '<button type="button" class="linkish" data-rm-go="' + esc(m.id) + '">' + esc(m.kind === "topic" ? m.t.name : m.a.name) + "</button>"; }).join(", ") + "</p>";
    }
    panel.innerHTML = h;
  }
  panel.addEventListener("click", function (ev) { var b = ev.target.closest("[data-rm-go]"); if (b && byId[b.dataset.rmGo]) { select(byId[b.dataset.rmGo]); centre(byId[b.dataset.rmGo]); } });

  var tip = root.querySelector("[data-rm-tip]"), stage = root.querySelector(".rm-stage");
  function tipShow(n) {
    var h;
    if (n.kind === "paper") h = "<b>" + esc(n.p.t) + "</b><span>" + n.p.y + " &middot; " + esc(n.p.type) + " &middot; " + n.nb.filter(function (m) { return m.kind === "topic"; }).map(function (m) { return esc(m.t.name); }).join(", ") + "</span>";
    else if (n.kind === "topic") h = "<b>" + esc(n.t.name) + "</b><span>" + esc(n.t.facet) + " &middot; " + papersOf(n).length + " papers</span>";
    else h = "<b>" + esc(n.a.name) + "</b><span>" + n.a.n + " papers with Dr. Ingham</span>";
    tip.innerHTML = h; tip.hidden = false;
  }
  function tipMove(ev) { var r = stage.getBoundingClientRect(), x = ev.clientX - r.left + 14, y = ev.clientY - r.top + 14; var sw = svg.getBoundingClientRect().width; if (x > sw - 290) x -= 300; if (x < 4) x = 4; tip.style.left = x + "px"; tip.style.top = y + "px"; }
  function centre(n) { view.x = W / 2 - n.x * view.k; view.y = H / 2 - n.y * view.k; applyView(); }
  function applyView() { if (g) g.setAttribute("transform", "translate(" + view.x + "," + view.y + ") scale(" + view.k + ")"); }
  root.querySelectorAll("[data-rm-zoom]").forEach(function (b) {
    b.addEventListener("click", function () {
      var z = parseFloat(b.dataset.rmZoom);
      if (!z) { fit(); return; } else { var k2 = Math.max(.5, Math.min(4, view.k * z)); view.x = W / 2 - (W / 2 - view.x) * k2 / view.k; view.y = H / 2 - (H / 2 - view.y) * k2 / view.k; view.k = k2; }
      applyView();
    });
  });

  // drag nodes, pan the background
  var dragN = null, panning = false, moved = false, last = null;
  function pt(ev) { var r = svg.getBoundingClientRect(); return { x: (ev.clientX - r.left) / r.width * W, y: (ev.clientY - r.top) / r.height * H }; }
  function start(ev) { last = pt(ev); moved = false; svg.setPointerCapture && svg.setPointerCapture(ev.pointerId); svg.classList.add("is-dragging"); }
  svg.addEventListener("pointerdown", function (ev) { if (dragN) return; panning = true; start(ev); });
  svg.addEventListener("pointermove", function (ev) {
    if (!last) return; var p = pt(ev), dx = p.x - last.x, dy = p.y - last.y; if (Math.abs(dx) + Math.abs(dy) > 2) moved = true; last = p;
    if (dragN) { dragN.x += dx / view.k; dragN.y += dy / view.k; kick(); if (reduce) paint(); }
    else if (panning) { view.x += dx; view.y += dy; applyView(); }
  });
  function end() { if (dragN && !moved) select(dragN); if (!dragN && panning && !moved) { select(null); panel.innerHTML = panel.dataset.intro; } dragN = null; panning = false; last = null; svg.classList.remove("is-dragging"); setTimeout(function () { moved = false; }, 0); }
  svg.addEventListener("pointerup", end); svg.addEventListener("pointercancel", end);
  svg.addEventListener("wheel", function (ev) { if (!ev.ctrlKey && !ev.metaKey) return; ev.preventDefault(); var p = pt(ev), k2 = Math.max(.5, Math.min(4, view.k * (ev.deltaY < 0 ? 1.12 : .89))); view.x = p.x - (p.x - view.x) * k2 / view.k; view.y = p.y - (p.y - view.y) * k2 / view.k; view.k = k2; applyView(); }, { passive: false });
  panel.dataset.intro = panel.innerHTML;

  // controls
  root.querySelectorAll('[data-rm-set="all"]').forEach(function (b) { b.addEventListener("click", function () { state.set = state.set === "all" ? "elaine" : "all"; b.classList.toggle("is-active", state.set === "all"); b.setAttribute("aria-pressed", state.set === "all"); build(); }); });
  root.querySelectorAll("[data-rm-layer]").forEach(function (b) { b.addEventListener("click", function () { state.people = !state.people; b.classList.toggle("is-active", state.people); b.setAttribute("aria-pressed", state.people); build(); }); });
  root.querySelectorAll("[data-rm-facet]").forEach(function (b) { b.addEventListener("click", function () { var on = !b.classList.contains("is-active"); b.classList.toggle("is-active", on); b.setAttribute("aria-pressed", on); state.facets[b.dataset.rmFacet] = on; build(); }); });
  root.querySelector("[data-rm-jump]").addEventListener("click", function (ev) { var b = ev.target.closest("[data-rm-go]"); if (!b) return; var n = byId[b.dataset.rmGo]; if (!n) return; select(n); centre(n); root.querySelectorAll("[data-rm-jump] .chip").forEach(function (x) { x.classList.toggle("is-active", x === b); }); });
  var q = root.querySelector("[data-rm-q]");
  function search() {
    var s = (q.value || "").trim().toLowerCase(); state.q = s;
    if (!s) { if (!state.sel) hot(null); return; }
    svg.classList.add("is-focus");
    nodes.forEach(function (n) { var txt = n.kind === "topic" ? n.t.name : n.kind === "person" ? n.a.name : n.p.t + " " + n.p.authors; n.el.classList.toggle("is-hot", txt.toLowerCase().indexOf(s) > -1); });
    links.forEach(function (l) { l.el.classList.toggle("is-hot", l.a.el.classList.contains("is-hot") || l.b.el.classList.contains("is-hot")); });
  }
  q.addEventListener("input", search);
  q.addEventListener("keydown", function (ev) { if (ev.key === "Enter") { var n = nodes.filter(function (m) { return m.el.classList.contains("is-hot"); }).sort(function (a, b) { return (a.kind === "paper") - (b.kind === "paper"); })[0]; if (n) { select(n); centre(n); } } });

  function list() {
    var box = root.querySelector("[data-rm-list]"), h = "";
    D.facets.forEach(function (f) {
      var ts = nodes.filter(function (n) { return n.kind === "topic" && n.t.facet === f; });
      if (!ts.length) return;
      h += "<h3>" + esc(f) + "</h3><ul>" + ts.map(function (n) { return '<li><button type="button" class="linkish" data-rm-go="' + esc(n.id) + '">' + esc(n.t.name) + "</button> (" + papersOf(n).length + ")</li>"; }).join("") + "</ul>";
    });
    var ps = nodes.filter(function (n) { return n.kind === "person"; });
    if (ps.length) h += "<h3>Colleagues</h3><ul>" + ps.map(function (n) { return '<li><button type="button" class="linkish" data-rm-go="' + esc(n.id) + '">' + esc(n.a.name) + "</button> (" + n.a.n + ")</li>"; }).join("") + "</ul>";
    box.innerHTML = h;
  }
  root.querySelector("[data-rm-list]").addEventListener("click", function (ev) { var b = ev.target.closest("[data-rm-go]"); if (b && byId[b.dataset.rmGo]) { select(byId[b.dataset.rmGo]); centre(byId[b.dataset.rmGo]); panel.scrollIntoView({ block: "nearest", behavior: "smooth" }); } });
  build();
})();

/* Practitioner map: a bubble per country. Choosing one filters the directory list below;
   hovering a practitioner's card lights up their country. */
(function () {
  "use strict";
  var map = document.querySelector("[data-pmap]");
  if (!map) return;
  var root = map.closest("[data-filter]");
  var select = root && root.querySelector("[data-topic]");
  if (!select) return;
  var dots = map.querySelectorAll("[data-country]");
  function mark() {
    Array.prototype.forEach.call(dots, function (d) { d.setAttribute("aria-pressed", String(d.getAttribute("data-country") === select.value)); });
    map.classList.toggle("has-pick", !!select.value);
  }
  function pick(d) {
    var c = d.getAttribute("data-country");
    select.value = select.value === c ? "" : c;
    select.dispatchEvent(new Event("change"));
    mark();
  }
  Array.prototype.forEach.call(dots, function (d) {
    d.addEventListener("click", function () { pick(d); });
    d.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(d); } });
  });
  select.addEventListener("change", mark);
  root.addEventListener("mouseover", function (e) {
    var li = e.target.closest && e.target.closest("[data-item]");
    var c = li ? li.getAttribute("data-topics") : "";
    Array.prototype.forEach.call(dots, function (d) { d.classList.toggle("is-hot", !!c && d.getAttribute("data-country") === c); });
  });
  mark();
})();
