/* ==========================================================================
   motion.js — sixteen motion studies on one reel of brightfield microscopy.
   Page-scoped to /motion. No library. Delete with motion.html and
   css/motion.css once a direction is picked.

   The one fact that governs everything here: the footage is almost flat.
   Measured over the full frame, luminance runs 152 to 174 out of 255 and
   mean saturation is 3.7. Nothing shows until it is stretched. Every study
   below opens the same window on the signal, LO..HI, and throws the rest
   away. Change those two numbers and all sixteen change together.
   ========================================================================== */
(function () {
  "use strict";

  /* The window, measured off the reel: the bulk of the signal lives
     between 152 and 174. Opening wider than that wastes most of the range
     and everything comes out grey. */
  var LO = 147, HI = 181;
  var LUT = new Uint8Array(256);
  for (var i = 0; i < 256; i++) {
    var v = ((i - LO) * 255) / (HI - LO);
    LUT[i] = v < 0 ? 0 : v > 255 ? 255 : v | 0;
  }
  /* The same window expressed as a CSS filter, for the studies that draw
     pixels straight rather than reading them back. brightness() first pulls
     the mean down to where contrast() can act on it: a mean of 0.64 pushed
     through contrast() alone only ever gets brighter. Studies that apply
     LUT afterwards must NOT use this, or the signal is stretched twice.
     saturate() is BELOW 1 on purpose: contrast() already multiplies chroma
     by the same 7.5, and mean saturation on this reel is 3.7 against a
     membrane peak of 85. Left at 1 the noise goes neon and the membrane,
     the one real colour in the frame, stops being special. */
  var CSS_TONE = "brightness(.78) contrast(7.5) saturate(.38)";

  var SRC_WIDE = "video/sfw-amoeba-lab-640";
  var SRC_SQ   = "video/sfw-amoeba-lab-512";

  /* the six inks, as [r,g,b] */
  var INK = {
    slide:  [176, 181, 172],
    light:  [213, 219, 195],
    green:  [162, 174, 119],
    glow:   [219, 230, 167],
    violet: [158, 143, 194],
    deep:   [60, 56, 65],
    deeper: [42, 39, 47]
  };

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------------------
     Small helpers
     --------------------------------------------------------------------- */
  function el(sel, root) { return (root || document).querySelector(sel); }

  /* WebM first for size, MP4 behind it for browsers without VP9 */
  function video(stem) {
    var v = document.createElement("video");
    [["webm", "video/webm"], ["mp4", "video/mp4"]].forEach(function (f) {
      var s = document.createElement("source");
      s.src = stem + "." + f[0]; s.type = f[1];
      v.appendChild(s);
    });
    v.muted = true; v.loop = true; v.playsInline = true;
    v.setAttribute("muted", ""); v.setAttribute("playsinline", "");
    v.preload = "auto";
    return v;
  }

  function off(w, h, read) {
    var c = document.createElement("canvas");
    c.width = w; c.height = h;
    return { c: c, x: c.getContext("2d", read ? { willReadFrequently: true } : undefined) };
  }

  /* size a canvas to its own box, capped so nothing renders more pixels
     than it can show */
  function fit(canvas, maxW) {
    var r = canvas.getBoundingClientRect();
    if (!r.width) return false;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.min(Math.round(r.width * dpr), maxW || 1400);
    var h = Math.round(w * (r.height / r.width));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    return true;
  }

  function ready(v) { return v.readyState >= 2 && v.videoWidth > 0; }

  /* draw a video "cover" into a canvas, optionally zoomed on a point */
  function cover(ctx, v, W, H, zoom, cx, cy) {
    zoom = zoom || 1; cx = cx == null ? 0.5 : cx; cy = cy == null ? 0.5 : cy;
    var vw = v.videoWidth, vh = v.videoHeight;
    var s = Math.max(W / vw, H / vh) * zoom;
    var dw = vw * s, dh = vh * s;
    ctx.drawImage(v, W / 2 - dw * cx, H / 2 - dh * cy, dw, dh);
  }

  /* ---------------------------------------------------------------------
     The driver. One rAF for the whole page; a study only runs while it is
     on screen, and only while the page is playing.
     --------------------------------------------------------------------- */
  var studies = [];
  var playing = true;

  function add(node, build) {
    if (!node) return;
    var s = { node: node, api: null, build: build, live: false, on: false, vids: [] };
    studies.push(s);
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { s.on = e.isIntersecting; sync(s); });
    }, { rootMargin: "160px 0px" });
    io.observe(node);
  }

  function sync(s) {
    var want = s.on && playing;
    if (want && !s.api) {
      try { s.api = s.build(s.node, s) || {}; }
      catch (err) { s.api = {}; fail(s.node, err); }
    }
    if (!s.api) return;
    if (want === s.live) return;
    s.live = want;
    s.vids.forEach(function (v) { want ? v.play().catch(function () {}) : v.pause(); });
    if (want && s.api.start) s.api.start();
    if (!want && s.api.stop) s.api.stop();
  }

  function fail(node, err) {
    if (window.console) console.error("[motion]", node.id || node.className, err);
    var p = document.createElement("p");
    p.className = "pl__note";
    p.textContent = "This study did not run in this browser.";
    node.appendChild(p);
  }

  function tick(t) {
    for (var i = 0; i < studies.length; i++) {
      var s = studies[i];
      if (s.live && s.api && s.api.frame) {
        try { s.api.frame(t / 1000); } catch (e) { s.live = false; fail(s.node, e); }
      }
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  /* register a video with a study so start/stop handles playback */
  function use(s, v) { s.vids.push(v); if (s.live) v.play().catch(function () {}); return v; }

  /* =====================================================================
     01  FIELD OF VIEW
     The reference point. Everything else is measured against this.
     Markup and animation are in HTML and CSS; this only starts the tape.
     ===================================================================== */
  add(el("#s-fov"), function (node, s) {
    use(s, el("video", node));
    return {};
  });

  /* =====================================================================
     02  ANALYTIC AMOEBA
     Cubism's actual proposition, applied to time instead of space: one
     picture holding many moments of the same body at once. A ring of past
     frames is kept; the plane is broken into irregular facets; each facet
     is filled from a different moment. Standing still it reads as a single
     image. Moving, the facets disagree, and the disagreement is the motion.
     ===================================================================== */
  add(el("#s-cubist"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_WIDE));

    var N = 24, BW = 420, BH = 236;             // ring of 24 past frames
    var ring = [], head = 0, pushEvery = 3, pc = 0, primed = false;
    for (var i = 0; i < N; i++) ring.push(off(BW, BH));

    var facets = null, fw = 0, fh = 0;

    /* An irregular tiling: a jittered lattice, so the facets share every
       edge exactly and the plane is covered with no seams. Half the quads
       are then split on a diagonal, which is what stops it reading as a
       grid. */
    function build(W, H) {
      var CX = 7, CY = 5, out = [];
      var P = [];
      for (var y = 0; y <= CY; y++) {
        P[y] = [];
        for (var x = 0; x <= CX; x++) {
          var jx = (x === 0 || x === CX) ? 0 : (Math.sin(x * 12.9 + y * 78.2) * 0.5) * (W / CX) * 0.44;
          var jy = (y === 0 || y === CY) ? 0 : (Math.sin(x * 39.3 + y * 11.1) * 0.5) * (H / CY) * 0.46;
          P[y][x] = [(x * W) / CX + jx, (y * H) / CY + jy];
        }
      }
      for (var yy = 0; yy < CY; yy++) {
        for (var xx = 0; xx < CX; xx++) {
          var a = P[yy][xx], b = P[yy][xx + 1], c = P[yy + 1][xx + 1], d = P[yy + 1][xx];
          var split = ((xx * 3 + yy * 5) % 7) < 4;
          if (split) { out.push([a, b, c]); out.push([a, c, d]); }
          else       { out.push([a, b, c, d]); }
        }
      }
      /* spread the lags so neighbouring facets are never adjacent in time,
         and give each facet a value shift keyed to its own lag: in analytic
         cubism a facet carries its own tone, and here that tone is a clock */
      out.forEach(function (f, k) {
        f.lag = (k * 7) % N;
        f.tone = (f.lag / N - 0.5) * 0.14;
      });
      return out;
    }

    return {
      frame: function () {
        if (!ready(v) || !fit(cv, 1200)) return;
        var W = cv.width, H = cv.height;
        if (!facets || fw !== W || fh !== H) { facets = build(W, H); fw = W; fh = H; }

        if (!primed) {                            /* fill the whole ring first */
          primed = true;
          for (var pi = 0; pi < N; pi++) {
            ring[pi].x.filter = CSS_TONE;
            cover(ring[pi].x, v, BW, BH, 1.55, 0.5, 0.52);
            ring[pi].x.filter = "none";
          }
        }
        if (++pc >= pushEvery) {
          pc = 0;
          head = (head + 1) % N;
          var b = ring[head];
          b.x.filter = CSS_TONE;
          cover(b.x, v, BW, BH, 1.55, 0.5, 0.52);
          b.x.filter = "none";
        }

        ctx.clearRect(0, 0, W, H);
        for (var i = 0; i < facets.length; i++) {
          var f = facets[i];
          ctx.save();
          ctx.beginPath();
          ctx.moveTo(f[0][0], f[0][1]);
          for (var p = 1; p < f.length; p++) ctx.lineTo(f[p][0], f[p][1]);
          ctx.closePath();
          ctx.clip();
          ctx.drawImage(ring[(head - f.lag + N * 2) % N].c, 0, 0, W, H);
          ctx.restore();

          ctx.beginPath();
          ctx.moveTo(f[0][0], f[0][1]);
          for (var q = 1; q < f.length; q++) ctx.lineTo(f[q][0], f[q][1]);
          ctx.closePath();
          ctx.fillStyle = (f.tone > 0 ? "rgba(219,230,167," : "rgba(60,56,65,")
                          + Math.abs(f.tone).toFixed(3) + ")";
          ctx.fill();
          ctx.strokeStyle = "rgba(158,143,194,.55)";
          ctx.lineWidth = 1.25;
          ctx.stroke();
        }
      }
    };
  });

  /* =====================================================================
     03  CANON IN SIX
     No processing at all. One tape, six times, entered at six points in
     the bar and screened over itself. Six moments of the same organism
     share the frame. The cheapest study here and one of the strangest.
     ===================================================================== */
  add(el("#s-canon"), function (node, s) {
    var vids = node.querySelectorAll("video");
    Array.prototype.forEach.call(vids, function (v, i) {
      use(s, v);
      var seed = function () { try { v.currentTime = (i * 10) / vids.length; } catch (e) {} };
      if (ready(v)) seed(); else v.addEventListener("loadeddata", seed, { once: true });
    });
    return {};
  });

  /* =====================================================================
     04  SLIT-SCAN
     One column of the tape, one pixel wide, written to the right edge of a
     canvas that slides left forever. The horizontal axis stops being space
     and becomes time. What the organism draws as it crosses the slit is a
     graph of its own passage.
     ===================================================================== */
  add(el("#s-slit"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_WIDE));
    var seeded = false;

    return {
      frame: function (t) {
        if (!ready(v) || !fit(cv, 1600)) return;
        var W = cv.width, H = cv.height, step = 3;
        if (!seeded) {
          ctx.fillStyle = "#2A272F"; ctx.fillRect(0, 0, W, H); seeded = true;
        }
        ctx.drawImage(cv, -step, 0);            /* the whole record shifts left */

        /* the slit itself wanders slowly, so the record is never periodic */
        var sx = v.videoWidth * (0.5 + 0.22 * Math.sin(t * 0.07));
        ctx.save();
        ctx.filter = CSS_TONE;
        ctx.drawImage(v, sx, 0, 2, v.videoHeight, W - step, 0, step, H);
        ctx.restore();

        ctx.fillStyle = "rgba(219,230,167,.85)";  /* "now" */
        ctx.fillRect(W - 1, 0, 1, H);
      }
    };
  });

  /* =====================================================================
     05  MEMBRANE
     A raw WebGL fragment shader, no library. The frame is pushed through a
     turbulent lens and the colour channels are pulled apart along the
     direction of the push, so violet and green separate wherever the lens
     bends hardest. It looks like reading the slide through the organism's
     own wall.
     ===================================================================== */
  add(el("#s-membrane"), function (node, s) {
    var cv = el("canvas", node);
    var gl = cv.getContext("webgl", { antialias: false, alpha: false }) ||
             cv.getContext("experimental-webgl");
    if (!gl) throw new Error("no webgl");
    var v = use(s, video(SRC_SQ));

    var VS =
      "attribute vec2 p;varying vec2 uv;" +
      "void main(){uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}";

    var FS = [
      "precision highp float;",
      "varying vec2 uv;",
      "uniform sampler2D tex;uniform float t;uniform vec2 res;uniform vec2 tres;",
      "float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}",
      "float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);",
      " return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+vec2(1.,1.)),f.x),f.y);}",
      "float fbm(vec2 p){float a=.5,s=0.;for(int i=0;i<4;i++){s+=a*n(p);p*=2.03;a*=.5;}return s;}",
      /* cover-fit the texture into the viewport */
      "vec2 coverUV(vec2 u){float ar=res.x/res.y,tr=tres.x/tres.y;vec2 c=u-.5;",
      " if(ar>tr){c.y*=tr/ar;}else{c.x*=ar/tr;}return c*.72+.5;}",
      "vec3 sample1(vec2 u){return texture2D(tex,clamp(u,0.001,0.999)).rgb;}",
      "void main(){",
      " vec2 base=coverUV(uv);",
      " vec2 w=vec2(fbm(uv*3.1+t*.055),fbm(uv*3.1+vec2(7.3,2.1)-t*.048))-.5;",
      " float breathe=.55+.45*sin(t*.28);",
      " vec2 d=w*.075*breathe;",
      " float k=.016*(.4+length(w)*2.2);",   /* split hardest where the lens bends */
      " float r=sample1(base+d+w*k).r;",
      " float g=sample1(base+d).g;",
      " float b=sample1(base+d-w*k).b;",
      " vec3 c=vec3(r,g,b);",
      " float l=dot(c,vec3(.299,.587,.114));",
      " l=clamp((l-.576)/.134,0.,1.);",       /* the same LO..HI window */
      /* ramp the flat signal across the six inks */
      " vec3 deep=vec3(.235,.220,.255),vio=vec3(.620,.561,.761),grn=vec3(.635,.682,.467),glow=vec3(.859,.902,.655);",
      " vec3 col=mix(deep,vio,smoothstep(0.,.45,l));",
      " col=mix(col,grn,smoothstep(.35,.75,l));",
      " col=mix(col,glow,smoothstep(.7,1.,l));",
      /* let the chromatic split itself show as colour, not just fringe */
      " float split=abs(r-b)*3.4;",
      " col=mix(col,vio,clamp(split,0.,.75));",
      " float vig=1.-.85*pow(length(uv-.5)*1.42,3.0);",
      " gl_FragColor=vec4(col*vig,1.);",
      "}"
    ].join("\n");

    function sh(type, src) {
      var o = gl.createShader(type);
      gl.shaderSource(o, src); gl.compileShader(o);
      if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o));
      return o;
    }
    var prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS));
    gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
    gl.useProgram(prog);

    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, "p");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

    var tx = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tx);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);

    var uT = gl.getUniformLocation(prog, "t"),
        uR = gl.getUniformLocation(prog, "res"),
        uTR = gl.getUniformLocation(prog, "tres");

    return {
      frame: function (t) {
        if (!ready(v) || !fit(cv, 1100)) return;
        gl.viewport(0, 0, cv.width, cv.height);
        gl.bindTexture(gl.TEXTURE_2D, tx);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, v);
        gl.uniform1f(uT, reduced ? 4.0 : t);
        gl.uniform2f(uR, cv.width, cv.height);
        gl.uniform2f(uTR, v.videoWidth, v.videoHeight);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      }
    };
  });

  /* =====================================================================
     06  RISO, TWO INKS
     An 8x8 ordered dither, printed in two passes: Living green, then
     Membrane violet two pixels out of register. Continuous tone is thrown
     away entirely. What survives is a printed object, on paper, that a
     risograph could actually produce.
     ===================================================================== */
  add(el("#s-riso"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_WIDE));
    var SW = 300, SH = 169;
    var src = off(SW, SH, true), dst = off(SW, SH);
    var img = dst.x.createImageData(SW, SH);

    var B = [];                                  /* Bayer 8x8, 0..63 */
    (function () {
      var m = [[0,32,8,40,2,34,10,42],[48,16,56,24,50,18,58,26],
               [12,44,4,36,14,46,6,38],[60,28,52,20,62,30,54,22],
               [3,35,11,43,1,33,9,41],[51,19,59,27,49,17,57,25],
               [15,47,7,39,13,45,5,37],[63,31,55,23,61,29,53,21]];
      for (var y = 0; y < 8; y++) for (var x = 0; x < 8; x++) B[y * 8 + x] = (m[y][x] / 64) * 255;
    })();

    return {
      frame: function () {
        if (!ready(v) || !fit(cv, 1200)) return;
        cover(src.x, v, SW, SH, 1.35, 0.5, 0.5);   /* raw: LUT is the only stretch */
        var d = src.x.getImageData(0, 0, SW, SH).data, o = img.data;

        for (var y = 0; y < SH; y++) {
          for (var x = 0; x < SW; x++) {
            var i = (y * SW + x) * 4;
            var l = LUT[(d[i] * 77 + d[i + 1] * 151 + d[i + 2] * 28) >> 8];
            /* second plate reads two pixels away: the misregistration */
            var j = (Math.min(SH - 1, y + 1) * SW + Math.min(SW - 1, x + 2)) * 4;
            var l2 = LUT[(d[j] * 77 + d[j + 1] * 151 + d[j + 2] * 28) >> 8];
            var th = B[(y & 7) * 8 + (x & 7)];

            var r = INK.light[0], g = INK.light[1], b = INK.light[2];
            if (l < th) { r = INK.green[0]; g = INK.green[1]; b = INK.green[2]; }
            if (l2 < th * 0.82) {                 /* violet multiplies over */
              r = (r * INK.violet[0]) / 255; g = (g * INK.violet[1]) / 255; b = (b * INK.violet[2]) / 255;
            }
            o[i] = r; o[i + 1] = g; o[i + 2] = b; o[i + 3] = 255;
          }
        }
        dst.x.putImageData(img, 0, 0);
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(dst.c, 0, 0, cv.width, cv.height);
      }
    };
  });

  /* =====================================================================
     07  BATHYMETRY
     Luminance quantised to seven bands, and only the boundaries between
     bands drawn. The organism stops being a photograph and becomes a
     survey: contour lines, the way a seabed or a soil horizon is drawn.
     ===================================================================== */
  add(el("#s-contour"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_WIDE));
    var SW = 330, SH = 186, BANDS = 6;
    var src = off(SW, SH, true), dst = off(SW, SH);
    var img = dst.x.createImageData(SW, SH);
    var lev = new Uint8Array(SW * SH);

    return {
      frame: function () {
        if (!ready(v) || !fit(cv, 1300)) return;
        src.x.filter = "blur(1.9px)";              /* smooth only; LUT is the only stretch */
        cover(src.x, v, SW, SH, 1.5, 0.5, 0.52);
        src.x.filter = "none";
        var d = src.x.getImageData(0, 0, SW, SH).data;

        var k;
        for (k = 0; k < SW * SH; k++) {
          var i = k * 4;
          var l = LUT[(d[i] * 77 + d[i + 1] * 151 + d[i + 2] * 28) >> 8];
          lev[k] = (l * BANDS) / 256 | 0;
        }
        var o = img.data;
        for (var y = 0; y < SH; y++) {
          for (var x = 0; x < SW; x++) {
            k = y * SW + x;
            var q = lev[k];
            var edge = (x < SW - 1 && lev[k + 1] !== q) || (y < SH - 1 && lev[k + SW] !== q);
            var i2 = k * 4, f = q / (BANDS - 1);
            /* faint banded ground, hard green lines */
            var r = INK.light[0] + (INK.glow[0] - INK.light[0]) * f * 0.55;
            var g = INK.light[1] + (INK.glow[1] - INK.light[1]) * f * 0.55;
            var b = INK.light[2] + (INK.glow[2] - INK.light[2]) * f * 0.55;
            if (edge) {
              var deepness = 1 - f;
              r = INK.green[0] * (1 - deepness * 0.62);
              g = INK.green[1] * (1 - deepness * 0.62);
              b = INK.green[2] * (1 - deepness * 0.62);
            }
            o[i2] = r; o[i2 + 1] = g; o[i2 + 2] = b; o[i2 + 3] = 255;
          }
        }
        dst.x.putImageData(img, 0, 0);
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(dst.c, 0, 0, cv.width, cv.height);
      }
    };
  });

  /* =====================================================================
     08  LIVING TYPE
     The tape poured into a word and nowhere else. Drawn, then cut to the
     letterforms with destination-in, so the type is a window rather than a
     fill. The faint field behind it is the same tape, running free.
     ===================================================================== */
  add(el("#s-type"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_WIDE));
    use(s, el("video", node));                    /* the faint field behind */
    var word = cv.getAttribute("data-word") || "LIVING";

    return {
      frame: function () {
        if (!ready(v) || !fit(cv, 1500)) return;
        var W = cv.width, H = cv.height;
        ctx.globalCompositeOperation = "source-over";
        ctx.clearRect(0, 0, W, H);
        ctx.filter = CSS_TONE;
        cover(ctx, v, W, H, 3.4, 0.47, 0.56);   /* onto the organism itself */
        ctx.filter = "none";

        /* fit the word to the box, then cut everything outside it */
        var size = H * 0.82;
        ctx.font = "700 " + size + "px Montserrat, Helvetica Neue, Arial, sans-serif";
        var w = ctx.measureText(word).width;
        if (w > W * 0.92) {
          size = size * ((W * 0.92) / w);
          ctx.font = "700 " + size + "px Montserrat, Helvetica Neue, Arial, sans-serif";
        }
        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.globalCompositeOperation = "destination-in";
        ctx.fillStyle = "#fff";
        ctx.fillText(word, W / 2, H / 2 + size * 0.03);
        ctx.globalCompositeOperation = "source-over";
      }
    };
  });

  /* =====================================================================
     09  SWARM
     Nothing of the picture is drawn. Two and a half thousand particles
     read the frame for local contrast and climb toward it, leaving trails.
     The organisms are never rendered; they precipitate out of the dust
     because that is where the texture is. Stop the tape and the swarm
     dissolves.
     ===================================================================== */
  add(el("#s-swarm"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_WIDE));
    var GW = 160, GH = 90;
    var src = off(GW, GH, true);
    var E = new Float32Array(GW * GH);
    var T = new Float32Array(GW * GH);
    /* separable 3-tap box blur between two buffers */
    function blur(a, b) {
      var x, y, k;
      for (y = 0; y < GH; y++) for (x = 1; x < GW - 1; x++) {
        k = y * GW + x; b[k] = (a[k - 1] + a[k] + a[k + 1]) / 3;
      }
      for (y = 1; y < GH - 1; y++) for (x = 0; x < GW; x++) {
        k = y * GW + x; a[k] = (b[k - GW] + b[k] + b[k + GW]) / 3;
      }
    }
    var N = 2600, P = new Float32Array(N * 4);
    for (var i = 0; i < N; i++) {
      P[i * 4] = Math.random(); P[i * 4 + 1] = Math.random();
      P[i * 4 + 2] = 0; P[i * 4 + 3] = 0;
    }
    var primed = false;

    return {
      start: function () { primed = false; },
      frame: function () {
        if (!ready(v) || !fit(cv, 1200)) return;
        var W = cv.width, H = cv.height;
        if (!primed) { ctx.fillStyle = "#16141a"; ctx.fillRect(0, 0, W, H); primed = true; }

        cover(src.x, v, GW, GH, 1.5, 0.5, 0.52);   /* raw: LUT is the only stretch */
        var d = src.x.getImageData(0, 0, GW, GH).data;

        /* What the swarm climbs, after two false starts.
           Local contrast alone is useless: this reel is covered edge to edge
           in small round debris, so texture is everywhere. Frame-to-frame
           difference is useless too: over a third of a second the organism
           moves less than one cell of this grid, so the difference is noise.
           What actually separates the living thing from its field is SCALE.
           It is a large textured body among tiny isolated specks. So: measure
           texture, blur it six times until small specks have dissolved and
           only broad regions survive, then subtract the mean so that only
           above-average ground attracts anything at all. Whatever is left is
           the organism. */
        var x, y, k, n2 = GW * GH;
        for (y = 1; y < GH - 1; y++) {
          for (x = 1; x < GW - 1; x++) {
            k = y * GW + x;
            var c = k * 4;
            var l  = LUT[(d[c] * 77 + d[c + 1] * 151 + d[c + 2] * 28) >> 8];
            var lr = LUT[(d[c + 4] * 77 + d[c + 5] * 151 + d[c + 6] * 28) >> 8];
            var lb = LUT[(d[c + GW * 4] * 77 + d[c + GW * 4 + 1] * 151 + d[c + GW * 4 + 2] * 28) >> 8];
            E[k] = Math.abs(l - lr) + Math.abs(l - lb);
          }
        }
        blur(E, T); blur(E, T); blur(E, T); blur(E, T); blur(E, T); blur(E, T);

        var mn = 1e9, mx = -1e9;
        for (k = 0; k < n2; k++) { if (E[k] < mn) mn = E[k]; if (E[k] > mx) mx = E[k]; }
        var inv = 1 / (mx - mn || 1);
        for (k = 0; k < n2; k++) E[k] = (E[k] - mn) * inv;

        ctx.fillStyle = "rgba(22,20,26,.055)";   /* the trail decay */
        ctx.fillRect(0, 0, W, H);

        function e(px, py) {
          var gx = px * GW | 0, gy = py * GH | 0;
          if (gx < 1) gx = 1; if (gx > GW - 2) gx = GW - 2;
          if (gy < 1) gy = 1; if (gy > GH - 2) gy = GH - 2;
          return E[gy * GW + gx];
        }

        for (var i2 = 0; i2 < N; i2++) {
          var o = i2 * 4;
          var px = P[o], py = P[o + 1], vx = P[o + 2], vy = P[o + 3];
          var here = e(px, py);
          var dx = e(px + 0.008, py) - e(px - 0.008, py);
          var dy = e(px, py + 0.013) - e(px, py - 0.013);
          vx += dx * 0.30 + (Math.random() - 0.5) * 0.0022;   /* E is 0..1 now */
          vy += dy * 0.30 + (Math.random() - 0.5) * 0.0022;
          vx *= 0.93; vy *= 0.93;
          px += vx; py += vy;

          if (px < 0 || px > 1 || py < 0 || py > 1 || (here < 0.12 && Math.random() < 0.02)) {
            px = Math.random(); py = Math.random(); vx = vy = 0;
          }
          P[o] = px; P[o + 1] = py; P[o + 2] = vx; P[o + 3] = vy;

          var sp = Math.min(1, (Math.abs(vx) + Math.abs(vy)) * 190);
          /* the field slopes everywhere so particles can find their way in,
             but only the summit is drawn brightly */
          var hh = here < 0 ? 0 : here > 1 ? 1 : here;
          var a = 0.06 + 0.9 * hh * hh;
          ctx.fillStyle = sp > 0.45
            ? "rgba(158,143,194," + a + ")"
            : "rgba(219,230,167," + a + ")";
          ctx.fillRect(px * W, py * H, 1.7, 1.7);
        }
      }
    };
  });

  /* =====================================================================
     10  RADIOLARIAN
     Ten mirrored wedges around one centre. A soft-bodied organism with no
     symmetry at all is forced into the radial symmetry of a diatom. It is
     a lie about the specimen and a true thing about the palette: the
     violet membrane becomes structure.
     ===================================================================== */
  add(el("#s-kaleid"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_SQ));
    var WEDGES = 10;

    return {
      frame: function (t) {
        if (!ready(v) || !fit(cv, 1000)) return;
        var W = cv.width, H = cv.height, cx = W / 2, cy = H / 2;
        var R = Math.hypot(cx, cy);
        ctx.fillStyle = "#2A272F"; ctx.fillRect(0, 0, W, H);

        var spin = reduced ? 0.4 : t * 0.035;
        var step = (Math.PI * 2) / WEDGES;
        var vw = v.videoWidth, vh = v.videoHeight;
        var sc = (R * 2.8) / Math.max(vw, vh);
        /* the sampled patch drifts, so the mandala keeps rebuilding itself */
        var ox = Math.sin(t * 0.05) * R * 0.18, oy = Math.cos(t * 0.041) * R * 0.18;

        for (var i = 0; i < WEDGES; i++) {
          ctx.save();
          ctx.translate(cx, cy);
          ctx.rotate(spin + i * step);
          ctx.beginPath();
          ctx.moveTo(0, 0);
          ctx.arc(0, 0, R, -step / 2, step / 2);
          ctx.closePath();
          ctx.clip();
          if (i % 2) ctx.scale(-1, 1);      /* mirror the image, not the wedge */
          ctx.filter = CSS_TONE;
          ctx.drawImage(v, -vw * sc * 0.5 + ox + R * 0.22, -vh * sc * 0.5 + oy, vw * sc, vh * sc);
          ctx.filter = "none";
          ctx.restore();
        }

        /* the seams, and a rim */
        ctx.save();
        ctx.translate(cx, cy);
        ctx.globalCompositeOperation = "screen";
        for (var j = 0; j < WEDGES; j++) {
          ctx.beginPath();
          ctx.moveTo(0, 0);
          ctx.lineTo(Math.cos(spin + j * step + step / 2) * R, Math.sin(spin + j * step + step / 2) * R);
          ctx.strokeStyle = "rgba(158,143,194,.22)";
          ctx.lineWidth = 1; ctx.stroke();
        }
        ctx.restore();
        var g = ctx.createRadialGradient(cx, cy, R * 0.42, cx, cy, R * 0.98);
        g.addColorStop(0, "rgba(42,39,47,0)");
        g.addColorStop(1, "rgba(42,39,47,.72)");
        ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      }
    };
  });

  /* =====================================================================
     11  READOUT
     The frame quantised to a grid of numerals, one digit per cell, low to
     high. It is not a picture of an organism, it is the measurement that
     produced one, and the eye assembles the organism out of the density of
     the digits anyway. This is what the microscope actually hands over.
     ===================================================================== */
  add(el("#s-readout"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_WIDE));
    var COLS = 78;                                /* columns, not pixels */
    var atlas = null, aw = 0;
    var src = off(2, 2, true), cols = 0, rows = 0;

    /* one pre-rendered strip of glyphs per ink beats 3,000 fillText calls */
    function buildAtlas(w) {
      var h = Math.round(w * 1.05);
      var tones = ["rgba(162,174,119,.22)", "rgba(162,174,119,.60)",
                   "rgba(219,230,167,.98)", "rgba(255,255,255,1)"];
      var a = off(w * 10, h * tones.length);
      a.x.textAlign = "center"; a.x.textBaseline = "middle";
      a.x.font = "600 " + Math.round(w * 0.86) + "px ui-monospace, Menlo, monospace";
      for (var ti = 0; ti < tones.length; ti++) {
        a.x.fillStyle = tones[ti];
        for (var n = 0; n < 10; n++) a.x.fillText(String(n), n * w + w / 2, ti * h + h / 2);
      }
      aw = w; atlas = { c: a.c, w: w, h: h };
    }

    return {
      frame: function (t) {
        if (!ready(v) || !fit(cv, 1500)) return;
        var W = cv.width, H = cv.height;
        var want = Math.max(7, Math.round(W / COLS));
        if (!atlas || aw !== want) buildAtlas(want);
        var cw = atlas.w, ch = atlas.h;
        var nc = Math.ceil(W / cw), nr = Math.ceil(H / ch);
        if (nc !== cols || nr !== rows) {
          cols = nc; rows = nr; src.c.width = cols * 2; src.c.height = rows * 2;
        }
        /* Sampled at twice the grid. A cell's mean alone is useless here:
           at this size the organism's texture averages straight back into
           the field. Its RANGE does not. */
        cover(src.x, v, cols * 2, rows * 2, 1.45, 0.5, 0.52);
        var d = src.x.getImageData(0, 0, cols * 2, rows * 2).data;
        var SW2 = cols * 2;

        ctx.fillStyle = "#2A272F"; ctx.fillRect(0, 0, W, H);
        var scan = reduced ? -9 : (t * 6) % (rows + 8);
        for (var y = 0; y < rows; y++) {
          var near = Math.abs(y - scan) < 1.6;
          for (var x = 0; x < cols; x++) {
            var i = ((y * 2) * SW2 + x * 2) * 4, hi = 0, lo = 255, sum = 0, p2;
            for (p2 = 0; p2 < 4; p2++) {
              var j = i + (p2 & 1) * 4 + (p2 >> 1) * SW2 * 4;
              var lv = LUT[(d[j] * 77 + d[j + 1] * 151 + d[j + 2] * 28) >> 8];
              sum += lv; if (lv > hi) hi = lv; if (lv < lo) lo = lv;
            }
            var l = Math.min(255, sum / 4 * 0.4 + (hi - lo) * 2.6);
            var n = (l * 10) / 256 | 0;
            var tone = near ? 3 : n > 6 ? 2 : n > 3 ? 1 : 0;
            ctx.drawImage(atlas.c, n * cw, tone * ch, cw, ch, x * cw, y * ch, cw, ch);
          }
        }
      }
    };
  });

  /* =====================================================================
     12  HALFTONE
     A screen at fifteen degrees, dot area from luminance, ink in Deep on
     Glow. Print's oldest lie, that tone can be made from countable solids,
     applied to something too small to see with the eye at all.
     ===================================================================== */
  add(el("#s-halftone"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_WIDE));
    var COLS = 92, LEVELS = 10;                   /* dots across, not pixels */
    var sw = 0, cols = 0, rows = 0;
    var src = off(2, 2, true);
    var bucket = [];
    for (var bi = 0; bi < LEVELS; bi++) bucket.push([]);

    return {
      frame: function () {
        if (!ready(v) || !fit(cv, 1400)) return;
        var W = cv.width, H = cv.height;
        var px = Math.max(5, Math.round(W / COLS));
        sw = px;

        /* The screen is rotated, so the grid has to overhang the canvas. Use
           the true rotated bounding box, not a square of the diagonal: the
           square is more than twice the cells for the same picture. */
        var CO = Math.cos(15 * Math.PI / 180), SI = Math.sin(15 * Math.PI / 180);
        var nc = Math.ceil((W * CO + H * SI) / px) + 2;
        var nr = Math.ceil((W * SI + H * CO) / px) + 2;
        if (nc !== cols || nr !== rows) { cols = nc; rows = nr; src.c.width = cols; src.c.height = rows; }

        src.x.save();
        src.x.translate(cols / 2, rows / 2);
        src.x.rotate(-15 * Math.PI / 180);
        src.x.translate(-cols / 2, -rows / 2);
        cover(src.x, v, cols, rows, 1.45, 0.5, 0.52);  /* raw: LUT is the only stretch */
        src.x.restore();
        var d = src.x.getImageData(0, 0, cols, rows).data;

        ctx.fillStyle = "#DBE6A7"; ctx.fillRect(0, 0, W, H);
        for (var bj = 0; bj < LEVELS; bj++) bucket[bj].length = 0;
        for (var y = 0; y < rows; y++) {
          for (var x = 0; x < cols; x++) {
            var i = (y * cols + x) * 4;
            if (d[i + 3] === 0) continue;
            var l = LUT[(d[i] * 77 + d[i + 1] * 151 + d[i + 2] * 28) >> 8];
            var n = ((255 - l) * (LEVELS - 1)) / 255 | 0;   /* dark = big dot */
            if (n <= 0) continue;
            var bk = bucket[n];
            bk.push(x * px + px / 2, y * px + px / 2);
          }
        }
        ctx.save();
        ctx.translate(W / 2, H / 2);
        ctx.rotate(15 * Math.PI / 180);
        ctx.translate(-cols * px / 2, -rows * px / 2);
        ctx.fillStyle = "#3C3841";
        var TAU = Math.PI * 2;
        for (var lv = 1; lv < LEVELS; lv++) {
          var pts = bucket[lv];
          if (!pts.length) continue;
          var r = (px * 0.62) * (lv / (LEVELS - 1));
          ctx.beginPath();
          for (var pi = 0; pi < pts.length; pi += 2) {
            ctx.moveTo(pts[pi] + r, pts[pi + 1]);
            ctx.arc(pts[pi], pts[pi + 1], r, 0, TAU);
          }
          ctx.fill();
        }
        ctx.restore();
      }
    };
  });

  /* =====================================================================
     13  CHANNEL DRIFT
     Three moments, half a second apart, screened together as three inks:
     violet is the past, green the middle, glow the present. Anything that
     holds still stays neutral. Anything that moves smears into colour, and
     the colour tells you which way it went.
     ===================================================================== */
  add(el("#s-drift"), function (node, s) {
    var cv = el("canvas", node), ctx = cv.getContext("2d");
    var v = use(s, video(SRC_WIDE));
    var SW = 330, SH = 186, N = 16;
    var ring = [], head = 0, pc = 0, dirty = true, primed = false;
    for (var i = 0; i < N; i++) ring.push(off(SW, SH, true));
    var dst = off(SW, SH), img = dst.x.createImageData(SW, SH);
    /* TBL[ink][channel][luminance] = that plate's transfer for that channel */
    var TBL = [];
    (function () {
      [INK.glow, INK.green, INK.violet].forEach(function (ink) {
        var per = [];
        for (var ch = 0; ch < 3; ch++) {
          var col = new Float32Array(256), k = 1 - ink[ch] / 255;
          for (var l = 0; l < 256; l++) {
            var dns = 1 - l / 255;
            col[l] = 1 - dns * dns * dns * k;   /* cubed: see the loop below */
          }
          per.push(col);
        }
        TBL.push(per);
      });
    })();
    var L = [new Uint8Array(SW * SH), new Uint8Array(SW * SH), new Uint8Array(SW * SH)];
    var LAG = [0, 7, 15];

    function readInto(buf, target) {
      var d = buf.x.getImageData(0, 0, SW, SH).data;
      for (var k = 0, n = SW * SH; k < n; k++) {
        var i2 = k * 4;
        target[k] = LUT[(d[i2] * 77 + d[i2 + 1] * 151 + d[i2 + 2] * 28) >> 8];
      }
    }

    return {
      start: function () { primed = false; dirty = true; },
      frame: function () {
        if (!ready(v) || !fit(cv, 1300)) return;
        if (!primed) {                   /* fill the whole ring first */
          primed = true;
          for (var pi = 0; pi < N; pi++) cover(ring[pi].x, v, SW, SH, 1.5, 0.5, 0.52);
        }
        if (++pc >= 16) {                /* 16 buffers reaching ~4.3s back */
          pc = 0; dirty = true; head = (head + 1) % N;
          var b = ring[head];
          cover(b.x, v, SW, SH, 1.5, 0.5, 0.52);   /* raw: LUT is the only stretch */
        }
        if (dirty) {                     /* the lag buffers only change on a push */
          dirty = false;
          for (var t = 0; t < 3; t++) readInto(ring[(head - LAG[t] + N * 2) % N], L[t]);
        }

        var o = img.data;
        /* Three plates on one sheet, printed subtractively. Ink density is
           darkness, cubed so that the flat field barely inks and only real
           darks print: at linear density every plate lays 50% everywhere and
           the sheet comes out mud. Where all three plates agree the result is
           neutral; where the subject moved, one plate prints alone and the
           trail takes its colour. Screening them instead only ever gives
           white, because on this reel all three moments sit near the top of
           the range. */
        var G0 = TBL[0], G1 = TBL[1], G2 = TBL[2];
        var l0 = L[0], l1 = L[1], l2 = L[2];
        for (var k = 0, n = SW * SH, i3 = 0; k < n; k++, i3 += 4) {
          var p0 = l0[k], p1 = l1[k], p2 = l2[k];
          o[i3]     = G0[0][p0] * G1[0][p1] * G2[0][p2] * 255;
          o[i3 + 1] = G0[1][p0] * G1[1][p1] * G2[1][p2] * 255;
          o[i3 + 2] = G0[2][p0] * G1[2][p1] * G2[2][p2] * 255;
          o[i3 + 3] = 255;
        }
        dst.x.putImageData(img, 0, 0);
        ctx.drawImage(dst.c, 0, 0, cv.width, cv.height);
      }
    };
  });

  /* =====================================================================
     14  RACK
     The only study with no autonomous motion. Scroll position is bound to
     the tape's playhead and to the focus. The organism moves when the
     reader moves and stops when they stop. Reading the page becomes the
     act of looking down a microscope.
     ===================================================================== */
  add(el("#s-rack"), function (node, s) {
    var box = el(".rack", node);
    var v = el("video", box);
    var meter = el(".rack__meter i", box);
    var dur = 10, last = -1;

    v.addEventListener("loadedmetadata", function () { dur = v.videoDuration || v.duration || 10; });

    function update() {
      var r = box.getBoundingClientRect();
      var span = window.innerHeight + r.height;
      var p = (window.innerHeight - r.top) / span;
      p = p < 0 ? 0 : p > 1 ? 1 : p;
      var d = v.duration || dur;
      if (d && isFinite(d)) {
        try { v.currentTime = p * d * 0.999; } catch (e) {}
      }
      /* sharp in the middle of the pass, soft at both ends */
      var focus = Math.abs(p - 0.5) * 2;
      v.style.filter = "brightness(.8) contrast(6.5) saturate(.42) blur(" + (focus * focus * 7).toFixed(2) + "px)";
      meter.style.width = (p * 100).toFixed(1) + "%";
      if (last >= 0 && Math.abs(p - last) > 0.004) box.setAttribute("data-touched", "1");
      last = p;
    }

    return {
      start: function () { v.pause(); update(); window.addEventListener("scroll", update, { passive: true }); },
      stop:  function () { window.removeEventListener("scroll", update); }
    };
  });

  /* =====================================================================
     15  CONTACT SHEET
     Twelve cells, one moment each, spread across the ten seconds. The tape
     runs once and each cell exposes as the playhead reaches its mark, then
     holds. Motion moves across the sheet rather than inside any frame:
     the archive itself is the moving thing.
     ===================================================================== */
  add(el("#s-sheet"), function (node, s) {
    var cells = node.querySelectorAll(".cell");
    var v = use(s, video(SRC_WIDE));
    var n = cells.length, ctxs = [], marks = [], hot = [];
    Array.prototype.forEach.call(cells, function (c, i) {
      var cv = el("canvas", c);
      cv.width = 320; cv.height = 240;
      ctxs.push(cv.getContext("2d"));
      marks.push((i * 10) / n + 0.12);
      hot.push(0);
      ctxs[i].fillStyle = "#2A272F"; ctxs[i].fillRect(0, 0, 320, 240);
    });
    var prev = 0;

    return {
      frame: function (t) {
        if (!ready(v)) return;
        var now = v.currentTime;
        var wrapped = now < prev;
        for (var i = 0; i < n; i++) {
          var m = marks[i];
          var crossed = wrapped ? (prev < m || now >= m) : (prev < m && now >= m);
          if (crossed) {
            var c = ctxs[i];
            c.filter = CSS_TONE;
            cover(c, v, 320, 240, 2.5, 0.5, 0.53);   /* tight, so the drift between cells reads */
            c.filter = "none";
            cells[i].setAttribute("data-hot", "1");
            hot[i] = t;
          }
          if (hot[i] && t - hot[i] > 0.45) { cells[i].removeAttribute("data-hot"); hot[i] = 0; }
        }
        prev = now;
      }
    };
  });

  /* =====================================================================
     16  WET INK
     No canvas, no shader. An SVG filter graph applied straight to the video
     element: turbulence, displacement, then a four-step posterisation. The
     animation is SMIL inside the filter, so the browser drives it and the
     main thread does nothing at all. Ink spreading in damp paper.
     ===================================================================== */
  add(el("#s-ink"), function (node, s) {
    use(s, el("video", node));
    var defs = document.getElementById("mo-defs");
    var can = defs && typeof defs.pauseAnimations === "function";
    if (can && reduced) { defs.setCurrentTime(6); defs.pauseAnimations(); }
    return {
      start: function () { if (can && !reduced) defs.unpauseAnimations(); },
      stop:  function () { if (can) defs.pauseAnimations(); }
    };
  });

  /* ---------------------------------------------------------------------
     Page controls
     --------------------------------------------------------------------- */
  var toggle = document.getElementById("mo-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      playing = !playing;
      toggle.setAttribute("aria-pressed", String(!playing));
      toggle.textContent = playing ? "Pause everything" : "Play everything";
      studies.forEach(sync);
    });
  }
})();
