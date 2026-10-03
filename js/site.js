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
