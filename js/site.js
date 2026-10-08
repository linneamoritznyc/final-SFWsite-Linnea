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
