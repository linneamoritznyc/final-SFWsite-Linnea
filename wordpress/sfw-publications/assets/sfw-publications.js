/* SFW Publications: search, collection chips, Topic, Study type, Region and
   Sort, all combined (an entry shows only if it passes every one). Plain
   JavaScript, no library, no server calls: every entry is already on the
   page and this only hides, shows and reorders them.

   The state lives in the address (?topic=compost&region=europe&q=tea), so a
   filtered view can be shared as a link and the back button works. Without
   JavaScript the full list shows and the controls stay hidden. */
(function () {
  "use strict";
  var root = document.querySelector(".sfwp");
  if (!root || !window.URLSearchParams) return;
  var form = root.querySelector("[data-sfwp-form]");
  var controls = root.querySelector("[data-sfwp-controls]");
  var list = root.querySelector("[data-sfwp-list]");
  var flat = root.querySelector("[data-sfwp-flat]");
  var empty = root.querySelector("[data-sfwp-empty]");
  var status = root.querySelector("[data-sfwp-status]");
  var clears = root.querySelectorAll("[data-sfwp-clear]");
  var chips = root.querySelectorAll("[data-sfwp-chip]");
  var groups = list.querySelectorAll("[data-sfwp-group]");
  var items = Array.prototype.slice.call(list.querySelectorAll(".sfwp-entry"));
  var FIELDS = ["q", "collection", "topic", "study", "region", "sort"];
  var FILTERS = ["collection", "topic", "study", "region"];
  var state = {};

  // Accents folded, so "Ostrom" finds "Öström".
  function fold(s) {
    s = String(s).toLowerCase();
    return s.normalize ? s.normalize("NFD").replace(/[̀-ͯ]/g, "") : s;
  }
  // What the search reads: title, authors and citation, summary, useful for,
  // topics and year.
  items.forEach(function (it) {
    var parts = [it.getAttribute("data-year"), it.getAttribute("data-topics-text")];
    Array.prototype.forEach.call(it.querySelectorAll(".sfwp-entry__title, .sfwp-entry__line, [data-s]"),
      function (el) { parts.push(el.textContent); });
    it._text = fold(parts.join(" "));
    it._home = it.parentNode;
  });

  function fromUrl() {
    var p = new URLSearchParams(location.search), s = {};
    FIELDS.forEach(function (k) { s[k] = p.get(k) || ""; });
    return s;
  }
  function show(s) {
    ["q", "topic", "study", "region", "sort"].forEach(function (k) {
      var el = form.elements[k];
      el.value = s[k];
      if (el.value !== s[k]) { el.value = ""; s[k] = ""; }   // an old link with a value that no longer exists
    });
    var known = false;
    Array.prototype.forEach.call(chips, function (c) {
      var on = c.getAttribute("data-sfwp-chip") === s.collection;
      if (on) known = true;
      c.setAttribute("aria-pressed", on ? "true" : "false");
    });
    if (!known) { s.collection = ""; chips[0].setAttribute("aria-pressed", "true"); }
  }
  function save(push) {
    var p = new URLSearchParams(location.search);
    FIELDS.forEach(function (k) { if (state[k].trim()) p.set(k, state[k].trim()); else p.delete(k); });
    var qs = p.toString();
    var url = location.pathname + (qs ? "?" + qs : "") + location.hash;
    if (url !== location.pathname + location.search + location.hash) {
      history[push ? "pushState" : "replaceState"](null, "", url);
    }
  }
  function holds(it, k, v) {
    return (" " + (it.getAttribute("data-" + k) || "") + " ").indexOf(" " + v + " ") > -1;
  }

  function apply() {
    var s = state, words = fold(s.q).split(/\s+/).filter(Boolean), shown = 0;
    items.forEach(function (it) {
      var ok = true;
      FILTERS.forEach(function (k) { if (ok && s[k] && !holds(it, k, s[k])) ok = false; });
      for (var i = 0; ok && i < words.length; i++) if (it._text.indexOf(words[i]) < 0) ok = false;
      it.hidden = !ok;
      if (ok) shown++;
    });
    // Oldest first keeps the collection headings; newest first is one flat list.
    var newest = s.sort === "newest";
    items.slice().sort(function (a, b) {
      var d = newest ? b.getAttribute("data-year") - a.getAttribute("data-year") : 0;
      return d || a.getAttribute("data-i") - b.getAttribute("data-i");
    }).forEach(function (it) { (newest ? flat : it._home).appendChild(it); });
    flat.hidden = !newest || shown === 0;
    Array.prototype.forEach.call(groups, function (g) {
      g.hidden = newest || !g.querySelector(".sfwp-entry:not([hidden])");
    });
    var filtered = !!(s.q.trim() || s.collection || s.topic || s.study || s.region);
    status.textContent = "Showing " + shown + " of " + items.length + " publications";
    Array.prototype.forEach.call(clears, function (b) { b.hidden = !filtered; });
    empty.hidden = shown !== 0;
  }

  function set(k, v, push) { state[k] = v; save(push); apply(); }

  var timer;
  form.elements.q.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { set("q", form.elements.q.value, false); }, 200);
  });
  form.elements.q.addEventListener("change", function () { set("q", form.elements.q.value, true); });
  ["topic", "study", "region", "sort"].forEach(function (k) {
    form.elements[k].addEventListener("change", function () { set(k, form.elements[k].value, true); });
  });
  form.addEventListener("submit", function (e) { e.preventDefault(); });
  Array.prototype.forEach.call(chips, function (c) {
    c.addEventListener("click", function () {
      Array.prototype.forEach.call(chips, function (o) { o.setAttribute("aria-pressed", o === c ? "true" : "false"); });
      set("collection", c.getAttribute("data-sfwp-chip"), true);
    });
  });
  Array.prototype.forEach.call(clears, function (b) {
    b.addEventListener("click", function () {
      FILTERS.concat("q").forEach(function (k) { state[k] = ""; });
      show(state); save(true); apply();
      form.elements.q.focus();
    });
  });
  window.addEventListener("popstate", function () { state = fromUrl(); show(state); apply(); });

  controls.hidden = false;
  state = fromUrl();
  show(state);
  apply();
})();
