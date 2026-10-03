/* Soil Food Web Foundation — site.js
   Vanilla JS, no dependencies. Three jobs:
   1. Overlay menu: open, close, focus trap, Escape, body scroll lock.
   2. Accordion inside the overlay: one section open at a time.
   3. Root line: one hairline path drawn by scroll position (reversible).
   Everything degrades: without JS the header links still work, the overlay
   markup is hidden, and reduced-motion users get static states. */

(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 1. Overlay ---------- */
  var overlay = document.getElementById("overlay");
  var openBtn = document.querySelector("[data-menu-open]");
  var closeBtn = overlay && overlay.querySelector("[data-menu-close]");
  var lastFocus = null;

  function focusables(root) {
    return Array.prototype.slice.call(
      root.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])')
    ).filter(function (el) { return el.offsetParent !== null; });
  }

  function openMenu() {
    if (!overlay) return;
    lastFocus = document.activeElement;
    overlay.setAttribute("data-open", "true");
    overlay.removeAttribute("aria-hidden");
    openBtn.setAttribute("aria-expanded", "true");
    document.body.classList.add("is-locked");
    window.setTimeout(function () { closeBtn.focus(); }, reduceMotion ? 0 : 60);
  }

  function closeMenu() {
    if (!overlay) return;
    overlay.setAttribute("data-open", "false");
    overlay.setAttribute("aria-hidden", "true");
    openBtn.setAttribute("aria-expanded", "false");
    document.body.classList.remove("is-locked");
    if (lastFocus) lastFocus.focus();
  }

  if (overlay && openBtn && closeBtn) {
    overlay.setAttribute("aria-hidden", "true");
    openBtn.addEventListener("click", openMenu);
    closeBtn.addEventListener("click", closeMenu);

    // Close on any link click inside the overlay.
    overlay.addEventListener("click", function (e) {
      var a = e.target.closest("a[href]");
      if (a) closeMenu();
    });

    document.addEventListener("keydown", function (e) {
      if (overlay.getAttribute("data-open") !== "true") return;
      if (e.key === "Escape") { e.preventDefault(); closeMenu(); return; }
      if (e.key === "Tab") {
        var items = focusables(overlay);
        if (!items.length) return;
        var first = items[0], last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }

  /* ---------- 2. Accordion ---------- */
  var accordions = document.querySelectorAll("[data-accordion]");
  Array.prototype.forEach.call(accordions, function (acc) {
    var items = acc.querySelectorAll("[data-acc-item]");
    Array.prototype.forEach.call(items, function (item) {
      var btn = item.querySelector("[data-acc-btn]");
      var panel = item.querySelector("[data-acc-panel]");
      if (!btn || !panel) return;
      btn.setAttribute("aria-expanded", item.getAttribute("data-open") === "true" ? "true" : "false");
      btn.addEventListener("click", function () {
        var isOpen = item.getAttribute("data-open") === "true";
        Array.prototype.forEach.call(items, function (other) {
          other.setAttribute("data-open", "false");
          var ob = other.querySelector("[data-acc-btn]");
          if (ob) ob.setAttribute("aria-expanded", "false");
        });
        if (!isOpen) { item.setAttribute("data-open", "true"); btn.setAttribute("aria-expanded", "true"); }
      });
    });
  });

  /* ---------- 3. Root line drawn by scroll ---------- */
  // Markup: <svg class="root-line" data-root-line><path pathLength="1" d="..."/></svg>
  // inside a position:relative container. The path draws from 0 to 1 as the
  // container scrolls through the viewport, and un-draws on the way back up.
  var lines = document.querySelectorAll("[data-root-line]");
  if (lines.length && !reduceMotion) {
    var ticking = false;
    function update() {
      var vh = window.innerHeight;
      Array.prototype.forEach.call(lines, function (svg) {
        var box = svg.parentElement.getBoundingClientRect();
        var total = box.height + vh * 0.5;
        var passed = vh * 0.85 - box.top;
        var t = Math.max(0, Math.min(1, passed / total));
        svg.style.setProperty("--draw", t.toFixed(3));
      });
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    window.addEventListener("resize", update);
    update();
  }

  /* ---------- 4. Filter chips (index pages) ---------- */
  // <ul class="chips" data-filter-for="#list"> with <button class="chip" data-filter="all|kind">
  // Items in the list carry data-kind. "all" shows everything. No pagination anywhere.
  // More than one group may point at the same list: an item shows only when
  // every group agrees. A group tests data-kind unless data-filter-attr names
  // another attribute, so Publications filters by collection and by decade.
  // Children carrying none of those attributes (the column header row) are
  // chrome: never hidden, never counted.
  // An attribute may hold several space-separated values, and the item shows
  // if any one of them is the pressed key. That is what lets the community
  // log carry data-when="year month" on a post from this month and answer to
  // both "This year" and "This month". A single value is one token, so every
  // list that had one keeps behaving exactly as it did.
  function holds(item, attr, key) {
    var v = item.getAttribute(attr);
    return (" " + (v || "") + " ").indexOf(" " + key + " ") > -1;
  }
  var byList = [];
  Array.prototype.forEach.call(document.querySelectorAll("[data-filter-for]"), function (group) {
    var sel = group.getAttribute("data-filter-for");
    var found = null;
    byList.forEach(function (b) { if (b.sel === sel) found = b; });
    if (!found) {
      var list = document.querySelector(sel);
      if (!list) return;
      found = { sel: sel, list: list, groups: [] };
      byList.push(found);
    }
    found.groups.push(group);
  });

  byList.forEach(function (b) {
    var attrs = b.groups.map(function (g) { return g.getAttribute("data-filter-attr") || "data-kind"; });
    var items = Array.prototype.filter.call(b.list.children, function (item) {
      for (var i = 0; i < attrs.length; i++) { if (item.hasAttribute(attrs[i])) return true; }
      return false;
    });

    function apply() {
      var shown = 0;
      items.forEach(function (item) {
        var show = true;
        b.groups.forEach(function (group, i) {
          if (!show) return;
          var on = group.querySelector('[data-filter][aria-pressed="true"]');
          var key = on ? on.getAttribute("data-filter") : "all";
          // "all" on the ITEM, not just on the chip: a row that answers every
          // filter rather than one of them. The volunteer page's "Something
          // else" card is one, because no amount of time rules it out.
          if (key !== "all" && !holds(item, attrs[i], "all")
              && !holds(item, attrs[i], key)) show = false;
        });
        item.hidden = !show;
        if (show) shown++;
      });
      b.groups.forEach(function (group) {
        var status = group.querySelector("[data-filter-status]");
        if (status) status.textContent = shown + " shown";
      });
      // A filter that matches nothing says so, and says what to do about it,
      // rather than leaving a blank page under the chips.
      var empty = b.list.querySelector("[data-filter-empty]");
      if (empty) empty.hidden = shown !== 0;
    }

    b.groups.forEach(function (group) {
      var chips = group.querySelectorAll("[data-filter]");
      Array.prototype.forEach.call(chips, function (chip) {
        chip.addEventListener("click", function () {
          Array.prototype.forEach.call(chips, function (c) {
            c.setAttribute("aria-pressed", c === chip ? "true" : "false");
          });
          apply();
        });
      });
    });

    apply();
  });
})();

/* ---------- 5. Pathway diagram (Learn) ---------- */
// <div data-pathway> with <button data-pathway-btn aria-controls="id"> and a
// panel by that id. One panel open at a time; hover opens too, tap toggles.
(function () {
  var roots = document.querySelectorAll("[data-pathway]");
  Array.prototype.forEach.call(roots, function (root) {
    var btns = root.querySelectorAll("[data-pathway-btn]");
    function closeAll() {
      Array.prototype.forEach.call(btns, function (b) {
        b.setAttribute("aria-expanded", "false");
        var p = document.getElementById(b.getAttribute("aria-controls"));
        if (p) p.hidden = true;
      });
    }
    Array.prototype.forEach.call(btns, function (b) {
      var panel = document.getElementById(b.getAttribute("aria-controls"));
      if (!panel) return;
      function open() { closeAll(); b.setAttribute("aria-expanded", "true"); panel.hidden = false; }
      b.addEventListener("click", function () {
        var isOpen = b.getAttribute("aria-expanded") === "true";
        closeAll();
        if (!isOpen) { b.setAttribute("aria-expanded", "true"); panel.hidden = false; }
      });
      b.addEventListener("mouseenter", open);
      b.addEventListener("focus", open);
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeAll(); });
  });
})();

/* ---------- 5b. Role picker (Learn) ---------- */
(function () {
  var picker = document.querySelector("[data-role-picker]");
  if (!picker) return;
  var items = picker.querySelectorAll("[data-role]");
  var allCourses = document.querySelectorAll("[data-role-courses]");

  function show(role) {
    Array.prototype.forEach.call(items, function (el) {
      el.classList.toggle("is-active", el.getAttribute("data-role") === role);
    });
    Array.prototype.forEach.call(allCourses, function (el) {
      el.classList.toggle("is-visible", el.getAttribute("data-role-courses") === role);
    });
  }
  function hideAll() {
    Array.prototype.forEach.call(items, function (el) { el.classList.remove("is-active"); });
    Array.prototype.forEach.call(allCourses, function (el) { el.classList.remove("is-visible"); });
  }

  Array.prototype.forEach.call(items, function (item) {
    var role = item.getAttribute("data-role");
    var btn = item.querySelector("button");
    btn.addEventListener("mouseenter", function () { show(role); });
    btn.addEventListener("focus", function () { show(role); });
    btn.addEventListener("click", function () {
      var wasActive = item.classList.contains("is-active");
      if (wasActive) { hideAll(); } else { show(role); }
    });
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") hideAll(); });
})();

/* ---------- 6. Calendar today marker ---------- */
// The site is static, so "today" cannot be baked into the HTML or it goes stale.
// <div data-cal data-cal-start="YYYY-MM-DD" data-cal-end="YYYY-MM-DD"> with a
// [data-cal-today] span inside .cal__grid. Hidden when today is out of range.
(function () {
  var cals = document.querySelectorAll("[data-cal]");
  Array.prototype.forEach.call(cals, function (cal) {
    var marker = cal.querySelector("[data-cal-today]");
    if (!marker) return;
    var start = new Date(cal.getAttribute("data-cal-start") + "T00:00:00");
    var end = new Date(cal.getAttribute("data-cal-end") + "T00:00:00");
    var now = new Date(); now.setHours(0, 0, 0, 0);
    if (isNaN(start) || isNaN(end) || now < start || now > end) return;
    var span = (end - start) + 86400000;
    marker.style.left = ((now - start) / span * 100).toFixed(3) + "%";
    marker.hidden = false;
    var sr = document.createElement("span");
    sr.className = "visually-hidden";
    sr.textContent = "Today, " + now.toDateString() + ".";
    marker.appendChild(sr);
  });
})();

/* ---------- 7. Production notes ---------- */
// .todo blocks are hidden from visitors by CSS. ?notes=1 on any URL sets
// data-notes on <html>, which reveals every placeholder and prints the
// instruction held on each empty image slot's data-empty attribute.
(function () {
  try {
    var p = new URLSearchParams(window.location.search).get("notes");
    if (p === "1" || p === "true") document.documentElement.setAttribute("data-notes", "");
  } catch (e) { /* no URLSearchParams: notes stay hidden, which is the safe default */ }
})();

/* ---------- 8. Microscopy loops ---------- */
// Every <video data-loop> on the site is the Foundation's own brightfield
// footage. Three rules, in this order:
//   1. Nothing downloads until it is near the viewport. The markup carries
//      data-src rather than src, so a page with a clip below the fold costs
//      nothing until the reader goes there.
//   2. A clip plays only while it is on screen. Off screen it pauses, so a
//      long page never has more than one or two decoding at once.
//   3. Reduced motion means reduced motion. The clip loads and shows its
//      first frame, and never runs.
(function () {
  var vids = document.querySelectorAll("video[data-loop]");
  if (!vids.length) return;
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function load(v) {
    if (v.dataset.loaded) return;
    v.dataset.loaded = "1";
    (v.dataset.src || "").split(",").forEach(function (src) {
      src = src.trim();
      if (!src) return;
      var s = document.createElement("source");
      s.src = src;
      s.type = src.slice(-5) === ".webm" ? "video/webm" : "video/mp4";
      v.appendChild(s);
    });
    // data-start seeds the playhead, so several clips of the same reel on one
    // page are several moments rather than several copies of one.
    if (v.dataset.start) {
      v.addEventListener("loadedmetadata", function () {
        try { v.currentTime = parseFloat(v.dataset.start) || 0; } catch (e) { /* not seekable */ }
      }, { once: true });
    }
    v.load();
  }

  if (!("IntersectionObserver" in window)) {
    // No observer: load everything and let the browser decide. Correctness
    // over thrift on browsers this old.
    Array.prototype.forEach.call(vids, function (v) { load(v); if (!still) v.play().catch(function () {}); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      var v = en.target;
      if (!en.isIntersecting) { v.pause(); return; }
      load(v);
      if (!still && !v.hasAttribute("data-scrub")) v.play().catch(function () {});
    });
  }, { rootMargin: "200px 0px" });

  Array.prototype.forEach.call(vids, function (v) { io.observe(v); });
})();

/* ---------- 9. The rack ---------- */
// <div class="rack"> holding a <video data-loop data-scrub>. Scroll position
// through the block drives the playhead and the focus together: sharp as the
// block passes the middle of the window, soft at either end. The organism
// moves when the reader moves. Study 14 from /motion.
//
// Reduced motion turns it into an ordinary still frame, because the whole
// point of it is motion tied to scrolling.
(function () {
  var racks = document.querySelectorAll(".rack video[data-scrub]");
  if (!racks.length) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var ticking = false;
  function update() {
    ticking = false;
    Array.prototype.forEach.call(racks, function (v) {
      var box = v.closest(".rack");
      var r = box.getBoundingClientRect();
      if (r.bottom < -200 || r.top > window.innerHeight + 200) return;
      var p = (window.innerHeight - r.top) / (window.innerHeight + r.height);
      p = p < 0 ? 0 : p > 1 ? 1 : p;
      var d = v.duration;
      if (d && isFinite(d)) { try { v.currentTime = p * d * 0.999; } catch (e) { /* not seekable yet */ } }
      // sharp across the middle half of the pass, soft only at the extremes
      var focus = Math.max(0, (Math.abs(p - 0.5) * 2 - 0.45) / 0.55);
      v.style.filter = "brightness(.8) contrast(6.5) saturate(.42) blur(" + (focus * focus * 3.2).toFixed(2) + "px)";
      var m = box.querySelector(".rack__meter i");
      if (m) m.style.width = (p * 100).toFixed(1) + "%";
    });
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  Array.prototype.forEach.call(racks, function (v) {
    v.addEventListener("loadedmetadata", update, { once: true });
  });
  update();
})();

/* ---------- 10. The reveal ---------- */
// Photographs and plates rise a little and fade as they arrive, once.
//
// The stylesheet hides nothing. This hides only what is ALREADY BELOW THE
// FOLD, so a page with no JavaScript shows everything, and so does a
// screenshot, a thumbnail and a print. Anything on screen at load is left
// exactly as it is, which is why there is no flash.
//
// Reduced motion skips the whole thing rather than shortening it.
(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;

  var SEL = ".shot, .slides > li, .ledger > li, .doors > li, .cards > .card," +
            " .step, .banner, .filmstrip, .scope, .plate";
  // A page, or a region of one, may ask to be left still. The Wild Ken Hill
  // story does: the looping clips are the only motion wanted on it, and a
  // photograph fading up on the way past would be a second kind.
  var els = Array.prototype.filter.call(document.querySelectorAll(SEL), function (el) {
    return !el.closest("[data-still]");
  });
  if (!els.length) return;

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add("rise-in");
      en.target.classList.remove("rise");
      io.unobserve(en.target);            // once, then never again
    });
  }, { rootMargin: "0px 0px -8% 0px" });

  els.forEach(function (el) {
    // only pre-hide what the reader cannot see yet
    if (el.getBoundingClientRect().top > window.innerHeight) {
      el.classList.add("rise");
      io.observe(el);
    }
  });
})();

/* ---------- 11. The theatre ---------- */
// One player that stays on the page.
//
// The old playlist reloaded the whole of WordPress for every video and then
// booted a new Vimeo player from zero, which is why it felt slow and why
// autoplay into the next video was impossible. Here the player is created
// once, on the first click, and every video after that is a loadVideo() call
// on the player that is already running. The URL changes with pushState, so
// links and the back button still work, and nothing reloads.
//
// Nothing third-party loads until someone presses play. Until then the stage
// is a poster and a button, so the page costs nothing to arrive at. This is
// the facade pattern, and it is the single biggest speed difference between
// this and either a Vimeo or a YouTube embed dropped straight into a page:
// the platform's script is the weight, not the platform.
//
// The private hash travels in the data, never in the URL. Unlisted videos
// need it to play, and every way the old page had of losing it, dropping it
// from a link, pasting it inside the id, arriving with no query string at
// all, is a way of breaking the player. content/videos.json holds it and
// tools/playlist.py checks it against Vimeo before it is committed.
//
// If the platform script does not load, the stage becomes a plain link to
// the video. The content stays reachable.
(function () {
  "use strict";

  var root = document.querySelector("[data-theatre]");
  if (!root) return;
  var holder = root.querySelector("[data-theatre-data]");
  var list = [];
  try { list = JSON.parse(holder.textContent); } catch (err) { return; }
  if (!list.length) return;

  var frame  = root.querySelector("[data-frame]");
  var poster = root.querySelector("[data-poster]");
  var nowT   = root.querySelector("[data-now-title]");
  var nowS   = root.querySelector("[data-now-sub]");
  var live   = root.querySelector("[data-live]");
  var next   = root.querySelector("[data-next]");
  var nextT  = root.querySelector("[data-next-title]");
  var nextN  = root.querySelector("[data-next-count]");
  var check  = root.querySelector("[data-check]");
  var buttons = Array.prototype.slice.call(root.querySelectorAll("[data-i]"));

  var COUNTDOWN = 8;        // seconds before the next video starts
  var STREAK_LIMIT = 3;     // videos in a row unattended before we ask
  var player = null, loading = null, timer = null, i = 0, streak = 0;

  function slugIndex(slug) {
    for (var n = 0; n < list.length; n++) { if (list[n].slug === slug) return n; }
    return -1;
  }

  /* -- the platform script, fetched once and only on demand -- */
  function api() {
    if (window.Vimeo && window.Vimeo.Player) return Promise.resolve();
    if (loading) return loading;
    loading = new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = "https://player.vimeo.com/api/player.js";
      s.async = true;
      s.onload = resolve;
      s.onerror = function () { loading = null; reject(new Error("player.js")); };
      document.head.appendChild(s);
    });
    return loading;
  }

  // If Vimeo's control script will not load, the video still plays here, in
  // an ordinary iframe that needs no script at all. What is lost is the
  // autoplay chain and the still-watching check, not the video. Nothing ever
  // sends the visitor off to vimeo.com.
  function fallback() {
    var v = list[i];
    player = null;
    root.setAttribute("data-fallback", "true");
    frame.hidden = false;
    frame.innerHTML = "";
    var f = document.createElement("iframe");
    f.src = "https://player.vimeo.com/video/" + encodeURIComponent(v.id) +
            "?h=" + encodeURIComponent(v.hash) +
            "&autoplay=1&dnt=1&title=0&byline=0&portrait=0";
    f.title = v.title;
    f.allow = "autoplay; fullscreen; picture-in-picture";
    f.setAttribute("allowfullscreen", "");
    f.setAttribute("frameborder", "0");
    frame.appendChild(f);
    if (poster) poster.hidden = true;
    if (live) live.textContent = "Now playing: " + v.title;
  }

  function boot() {
    var v = list[i];
    return api().then(function () {
      frame.hidden = false;
      player = new window.Vimeo.Player(frame, {
        id: Number(v.id),
        h: v.hash,              // the private hash, from the data file
        autoplay: true,         // allowed: we are inside the click that asked
        dnt: true,              // no Vimeo tracking cookies
        title: false, byline: false, portrait: false,
        responsive: true
      });
      // The poster's job is over the moment the player exists. Waiting for
      // the play event would leave the poster sitting on top of a video that
      // has already started when autoplay is allowed, and on top of Vimeo's
      // own play button when it is not.
      if (poster) poster.hidden = true;
      player.on("ended", ended);
      // A pause or a scrub is a person, so the unattended count starts over.
      player.on("pause", awake);
      player.on("seeked", awake);
    })["catch"](fallback);
  }

  /* -- selecting, with or without playing -- */
  function select(n, opts) {
    opts = opts || {};
    i = ((n % list.length) + list.length) % list.length;
    var v = list[i];

    buttons.forEach(function (b, n2) {
      var on = n2 === i;
      b.setAttribute("aria-current", on ? "true" : "false");
      b.parentNode.setAttribute("data-active", on ? "true" : "false");
    });
    if (nowT) nowT.textContent = v.title;
    if (nowS) nowS.textContent = v.subtitle || "";
    if (poster) {
      var im = poster.querySelector("img");
      if (im && v.thumb) im.src = v.thumb;
    }
    if (!opts.silent) {
      history.pushState({ v: v.slug }, "", "?v=" + encodeURIComponent(v.slug));
    }

    if (!opts.play) return;
    if (live) live.textContent = "Now playing: " + v.title;
    if (player) {
      player.loadVideo({ id: Number(v.id), h: v.hash })
        .then(function () { return player.play(); })["catch"](fallback);
      if (poster) poster.hidden = true;
    } else {
      boot();
    }
  }

  /* -- what happens when one finishes -- */
  function ended() {
    if (i + 1 >= list.length) { stop(); if (poster) poster.hidden = false; return; }
    streak += 1;
    if (streak >= STREAK_LIMIT) { ask(); return; }
    countdown();
  }

  function countdown() {
    var left = COUNTDOWN;
    nextT.textContent = list[i + 1].title;
    nextN.textContent = left;
    next.hidden = false;
    var go = next.querySelector("[data-next-go]");
    if (go) go.focus();
    clearInterval(timer);
    timer = setInterval(function () {
      left -= 1;
      nextN.textContent = left;
      if (left <= 0) { stop(); select(i + 1, { play: true }); }
    }, 1000);
  }

  // Three in a row with nobody touching anything: stop and ask, the way a
  // streaming service does, rather than playing to an empty room.
  function ask() {
    stop();
    check.hidden = false;
    var go = check.querySelector("[data-check-go]");
    if (go) go.focus();
  }

  function stop() {
    clearInterval(timer);
    timer = null;
    if (next) next.hidden = true;
    if (check) check.hidden = true;
  }

  function awake() { streak = 0; }

  /* -- wiring -- */
  buttons.forEach(function (b, n) {
    b.addEventListener("click", function () { awake(); stop(); select(n, { play: true }); });
  });
  if (poster) poster.addEventListener("click", function () { awake(); select(i, { play: true }); });

  root.addEventListener("click", function (ev) {
    var t = ev.target.closest ? ev.target.closest("[data-next-go],[data-next-cancel],[data-check-go]") : null;
    if (!t) return;
    if (t.hasAttribute("data-next-cancel")) { stop(); return; }
    awake();
    stop();
    select(i + 1, { play: true });
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape" && timer) stop();
  });
  document.addEventListener("pointerdown", awake, { passive: true });

  window.addEventListener("popstate", function () {
    var want = slugIndex(new URLSearchParams(location.search).get("v") || "");
    if (want < 0 || want === i) return;
    stop();
    select(want, { silent: true, play: !!player });
  });

  // Arriving with ?v=slug selects that video and shows its poster. It does
  // not start playing: browsers block autoplay with sound before a click,
  // and a muted autostart is worse than a poster.
  var start = slugIndex(new URLSearchParams(location.search).get("v") || "");
  select(start < 0 ? 0 : start, { silent: true });
})();

/* ---------- 12. Films from the field ----------
   Every case-study still is a facade. Nothing is fetched from Vimeo until a
   visitor presses play; then the button is swapped for the player, in place,
   and focus moves into it so a keyboard user lands where the video is. The
   privacy hash rides on the button, because these videos are unlisted and
   the player refuses them without it. */
(function () {
  var strip = document.querySelectorAll("[data-film]");
  if (!strip.length) return;
  Array.prototype.forEach.call(strip, function (btn) {
    btn.addEventListener("click", function () {
      var frame = document.createElement("iframe");
      frame.src = btn.getAttribute("data-film") + "&autoplay=1";
      frame.title = btn.getAttribute("aria-label") || "Video";
      frame.allow = "autoplay; fullscreen; picture-in-picture";
      frame.setAttribute("allowfullscreen", "");
      btn.parentNode.replaceChild(frame, btn);
      frame.focus();
    });
  });
})();

/* ---------- 13. Toggle chips (the volunteer form) ----------
   The filter chips in job 4 are a radio group: one on at a time, and they
   hide things. These are the other kind: a handful of chips where any number
   can be on at once, and they answer a question rather than filtering a list.

   Two extras, both of them things a plain toggle cannot do on its own:

   1. A chip with data-reveals="#id" shows that element while it is pressed,
      and moves focus into the field inside it, so "Other" opens a box and
      the caret is already in it.
   2. The group writes its pressed labels into the hidden input named by
      data-chip-out. Without that the answer never leaves the page: a button
      is not a form control, and the form here is a plain submission with no
      script behind it.  */
(function () {
  "use strict";
  var groups = document.querySelectorAll("[data-chips]");
  Array.prototype.forEach.call(groups, function (group) {
    var chips = group.querySelectorAll('[aria-pressed]');
    var out = group.getAttribute("data-chip-out");
    var field = out ? document.querySelector(out) : null;

    function collect() {
      if (!field) return;
      var on = [];
      Array.prototype.forEach.call(chips, function (c) {
        if (c.getAttribute("aria-pressed") === "true") on.push(c.textContent.trim());
      });
      field.value = on.join(", ");
    }

    Array.prototype.forEach.call(chips, function (chip) {
      chip.addEventListener("click", function () {
        var on = chip.getAttribute("aria-pressed") !== "true";
        chip.setAttribute("aria-pressed", on ? "true" : "false");
        var sel = chip.getAttribute("data-reveals");
        if (sel) {
          var panel = document.querySelector(sel);
          if (panel) {
            panel.hidden = !on;
            if (on) {
              var f = panel.querySelector("input, textarea, select");
              if (f) f.focus();
            }
          }
        }
        collect();
      });
    });
    collect();
  });
})();

/* ---------- 14. The background loop ----------
   A silent clip running under a band of type, with the poster image showing
   until it is worth fetching one and instead of it when it is not.

   Three rules, and the order matters:
   1. Reduced motion means the poster and nothing else. The video element is
      removed rather than paused, so nothing is fetched and nothing can start.
   2. Nothing downloads until the band is near the viewport, and the clip
      pauses again the moment it leaves. data-src rather than src, the same
      way job 8 does it.
   3. It can be stopped. Motion that starts by itself and runs for more than
      five seconds needs a control (WCAG 2.2.2), so the pause button is
      written in here, beside the clip it controls, rather than sitting in
      the markup over a poster on a machine that will never play anything. */
(function () {
  "use strict";
  var holders = document.querySelectorAll("[data-loopbg]");
  if (!holders.length) return;
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  Array.prototype.forEach.call(holders, function (holder) {
    var v = holder.querySelector("video");
    if (!v) return;
    if (still || !("IntersectionObserver" in window)) { v.parentNode.removeChild(v); return; }

    var band = holder.closest(".loopbg") || holder.parentNode;
    var loaded = false, wanted = true;

    function load() {
      if (loaded) return;
      loaded = true;
      (v.getAttribute("data-src") || "").split(",").forEach(function (src) {
        src = src.trim();
        if (!src) return;
        var s = document.createElement("source");
        s.src = src;
        s.type = src.slice(-5) === ".webm" ? "video/webm" : "video/mp4";
        v.appendChild(s);
      });
      v.load();
    }

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "loopbg__pause";
    btn.hidden = true;
    btn.textContent = "Pause the background clip";
    btn.addEventListener("click", function () {
      wanted = !wanted;
      btn.textContent = wanted ? "Pause the background clip" : "Play the background clip";
      if (wanted) { v.play().catch(function () {}); } else { v.pause(); }
    });
    band.appendChild(btn);

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) { v.pause(); return; }
        load();
        if (wanted) {
          v.play().then(function () { btn.hidden = false; }).catch(function () {});
        }
      });
    }, { rootMargin: "200px 0px" });
    io.observe(band);
  });
})();

/* ---------- 15. Before and after ----------
   Two photographs of the same ground on two dates, one on top of the other,
   and a handle that decides how much of the top one you see.

   The handle is a range input rather than a draggable div, because a div
   cannot be reached with a keyboard, cannot be read by a screen reader, and
   has no value to announce. A range has all three for free, and pointer
   dragging is what a range already does. The slider only moves the clip: if
   the script never runs, the "after" photograph is simply shown whole, which
   is the more useful of the two to be left with. */
(function () {
  "use strict";
  var figs = document.querySelectorAll("[data-compare]");
  Array.prototype.forEach.call(figs, function (fig) {
    var range = fig.querySelector('input[type="range"]');
    if (!range) return;
    function draw() { fig.style.setProperty("--split", range.value + "%"); }
    range.addEventListener("input", draw);
    range.addEventListener("change", draw);
    draw();
  });
})();

/* ---------- 16. A file that has not arrived yet ----------
   The Wild Ken Hill photographs and clips are referenced at their final paths
   before the real files are uploaded to public/assets/community/. Until they
   land, a missing one has to fail quietly: no broken-image icon, no shift in
   the layout, and the slot still saying what belongs in it. The image is
   replaced in place by a toned box carrying its own alt text, which is the
   description that was written for it, so a sighted visitor reads what a
   screen-reader user would have heard. Capture phase, because the error event
   on an image does not bubble. */
(function () {
  // On a live page an empty slot goes away rather than standing there as a
  // dashed box: a visitor should see a finished page, not the production
  // schedule. Add ?notes=1, the way every other placeholder on this site is
  // read, and the box comes back with the description of what belongs in it.
  var notes = document.documentElement.hasAttribute("data-notes");

  function box(text) {
    var p = document.createElement("p");
    p.className = "media-missing";
    p.textContent = text;
    return p;
  }

  function retire(el, text) {
    if (!el.parentNode) return;
    if (notes) { el.parentNode.replaceChild(box(text), el); return; }
    // The feature block is the exception. Its photograph is one half of a
    // two-part object, and the empty half is a cream field beside the green
    // panel, which still reads as a design rather than as a hole.
    if (el.closest(".latest__img")) { el.parentNode.removeChild(el); return; }
    // The list item first, then the figure. Asking closest() for both at once
    // returns the figure every time, because the figure is the nearer ancestor,
    // and an empty list item would be left holding a gap in the grid.
    var slot = el.closest(".reel > li, .pair > li, .post__pics > li") || el.closest("figure") || el;
    slot.hidden = true;
  }

  // A list of photographs with every photograph gone is an empty list with
  // spacing around it. Take the list with them.
  function tidy() {
    Array.prototype.forEach.call(document.querySelectorAll(".post__pics, .pair, .reel"), function (ul) {
      var kids = Array.prototype.slice.call(ul.children);
      if (kids.length && kids.every(function (li) { return li.hidden; })) ul.hidden = true;
    });
  }

  function dropImage(el) {
    if (el.getAttribute("data-failed") === "true" || !el.parentNode) return;
    el.setAttribute("data-failed", "true");
    retire(el, el.alt || "Photograph to come");
    // Here rather than only in the sweep: a lazy photograph below the fold
    // does not try to load until it is scrolled to, long after load fired.
    tidy();
  }

  document.addEventListener("error", function (e) {
    var el = e.target;
    if (!el || !el.hasAttribute || !el.hasAttribute("data-optional")) return;

    if (el.tagName === "IMG") { dropImage(el); return; }

    var v = null;
    if (el.tagName === "VIDEO") v = el;
    else if (el.tagName === "SOURCE" && el.parentNode && el.parentNode.tagName === "VIDEO") v = el.parentNode;
    if (!v) return;

    // One <source> failing only means that codec is missing; the browser
    // moves on to the next. Wait until the element has run out of sources,
    // and check on the next tick, because networkState is not settled at the
    // moment the last source's error fires.
    window.setTimeout(function () {
      if (v.getAttribute("data-failed") === "true") return;
      if (v.networkState !== v.NETWORK_NO_SOURCE) return;
      v.setAttribute("data-failed", "true");
      var text = v.getAttribute("aria-label") || "Clip to come";
      function drop() {
        if (!v.parentNode) return;
        // The play button belongs to a clip. With no clip behind it there is
        // nothing to press, so it goes with the video rather than sitting on
        // the box that says the file has not arrived.
        var go = v.parentNode.querySelector(".clip__go");
        if (go) go.parentNode.removeChild(go);
        retire(v, text);
        tidy();
      }
      // A poster that does load is a perfectly good still, so keep it and
      // only fall back to text when there is nothing at all to show.
      if (v.poster) {
        var probe = new Image();
        probe.onerror = drop;
        probe.src = v.poster;
      } else {
        drop();
      }
    }, 0);
  }, true);

  // site.js is the last thing on the page, so an image that failed while the
  // document was still parsing fired its error before this listener existed.
  // Sweep for those once: complete with no intrinsic width is a broken image.
  function sweep() {
    Array.prototype.forEach.call(document.querySelectorAll("img[data-optional]"), function (im) {
      if (im.complete && im.naturalWidth === 0) dropImage(im);
    });
    tidy();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", sweep);
  else sweep();
  window.addEventListener("load", sweep);
})();

/* ---------- 17. The reel: short silent clips cut to circles ----------
   The one piece of motion on the site. Autoplay is never written into the
   markup, so with JavaScript off every clip sits on its poster behind a play
   button and nothing moves on its own.

   With JavaScript on and motion allowed, an IntersectionObserver plays a clip
   while it is on screen and pauses it the moment it leaves, which is what
   keeps a page of four of them cheap on a phone. Pressing a clip pauses or
   resumes it by hand, and a hand-paused clip is left alone by the observer.

   Where the visitor has asked for reduced motion, nothing autoplays: the
   poster and the play button stay, and pressing one plays that clip and only
   that clip. The preference is watched, so turning it on mid-visit stops
   every clip without a reload. */
(function () {
  var clips = document.querySelectorAll("[data-clip]");
  if (!clips.length) return;

  var mq = window.matchMedia("(prefers-reduced-motion: reduce)");
  var list = Array.prototype.slice.call(clips).map(function (v) {
    return { v: v, go: v.parentNode.querySelector(".clip__go"), onScreen: false, byHand: false };
  });

  // The button is never taken away while a clip is playing. Content that moves
  // on its own has to be stoppable, so the control stays in the page and stays
  // in the tab order; it just fades out of the way, and comes back on hover or
  // focus, carrying a pause mark instead of a play mark.
  function mark(c, playing) {
    if (!c.go) return;
    var name = c.v.getAttribute("aria-label") || "clip";
    c.go.setAttribute("aria-label", (playing ? "Pause the clip, " : "Play the clip, ") + name);
    c.go.setAttribute("data-state", playing ? "playing" : "paused");
  }

  function play(c) {
    var p = c.v.play();
    // Autoplay can still be refused (a phone on low power, a browser policy).
    // A refusal is not an error to report: leave the poster and the button.
    if (p && p.catch) p.catch(function () { mark(c, false); });
    mark(c, true);
  }

  function pause(c) {
    c.v.pause();
    mark(c, false);
  }

  function sync() {
    list.forEach(function (c) {
      if (mq.matches) { pause(c); c.byHand = false; return; }
      if (c.byHand) return;
      if (c.onScreen) play(c); else pause(c);
    });
  }

  list.forEach(function (c) {
    if (!c.go) return;
    c.go.hidden = false;
    mark(c, false);
    c.go.addEventListener("click", function () {
      if (c.v.paused) { c.byHand = true; play(c); }
      else { c.byHand = true; pause(c); }
    });
  });

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var c = null;
        list.forEach(function (x) { if (x.v === entry.target) c = x; });
        if (!c) return;
        c.onScreen = entry.isIntersecting;
        if (!entry.isIntersecting) c.byHand = false;   // off screen, start clean
      });
      sync();
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.25 });
    list.forEach(function (c) { io.observe(c.v); });
  } else {
    list.forEach(function (c) { c.onScreen = true; });
    sync();
  }

  if (mq.addEventListener) mq.addEventListener("change", sync);
  else if (mq.addListener) mq.addListener(sync);

  sync();
})();

/* ---------- 15. Rotating images [data-rotate] ---------- */
(function () {
  "use strict";
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var imgs = document.querySelectorAll("[data-rotate]");
  if (!imgs.length) return;
  imgs.forEach(function (img) {
    var srcs = img.getAttribute("data-rotate").split(",");
    if (srcs.length < 2) return;
    var idx = 0;
    img.style.transition = "opacity .6s ease";
    setInterval(function () {
      img.style.opacity = "0";
      setTimeout(function () {
        idx = (idx + 1) % srcs.length;
        img.src = srcs[idx];
        img.style.opacity = "1";
      }, 600);
    }, 4000);
  });
})();

/* ---------- 18. Newsletter submission ---------- */
(function () {
  "use strict";
  var forms = document.querySelectorAll("[data-newsletter]");
  if (!forms.length) return;

  function handle(form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type="email"]');
      if (!input || !input.value) return;
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.textContent = "Subscribed"; }
      input.disabled = true;
      try { sessionStorage.setItem("sfw-subscribed", "1"); } catch (ex) {}
    });
  }
  Array.prototype.forEach.call(forms, handle);
})();

/* ---------- 19. Newsletter nudge (slide-in) ---------- */
(function () {
  "use strict";
  var nudge = document.getElementById("nudge");
  if (!nudge) return;

  try { if (sessionStorage.getItem("sfw-nudge-dismissed") || sessionStorage.getItem("sfw-subscribed")) return; }
  catch (e) {}

  var closeBtn = nudge.querySelector(".nudge__close");
  var shown = false;

  function dismiss() {
    nudge.setAttribute("data-visible", "false");
    try { sessionStorage.setItem("sfw-nudge-dismissed", "1"); } catch (ex) {}
  }

  closeBtn.addEventListener("click", dismiss);

  nudge.querySelector("[data-newsletter]").addEventListener("submit", function () {
    setTimeout(dismiss, 800);
  });

  function check() {
    if (shown) return;
    var scrolled = window.scrollY || window.pageYOffset || 0;
    var total = document.documentElement.scrollHeight - window.innerHeight;
    if (total > 0 && scrolled / total >= 0.6) {
      shown = true;
      nudge.setAttribute("data-visible", "true");
    }
  }

  window.addEventListener("scroll", check, { passive: true });
})();
