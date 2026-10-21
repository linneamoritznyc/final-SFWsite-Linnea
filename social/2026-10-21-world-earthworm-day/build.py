"""World Earthworm Day (21 October 2026): three Instagram Story frames, 1080 x 1920.

Run:  python3 social/2026-10-21-world-earthworm-day/build.py
      node  social/2026-10-21-world-earthworm-day/render.js

build.py draws the cut-paper art as SVG (art/) and writes one HTML page per frame
(frame-1.html ...) with the text as live, editable HTML over the art. render.js
screenshots each page to png/frame-N.png (with text) and png/frame-N-art.png
(art only, for adding the text in Canva).

Frames 1 and 2 are cut from one tall drawing (1080 x 3840), so the anecic burrow
is at the same x on both and reads as one burrow when you tap through.
Edit text in TEXT below (or straight in the HTML), colours in C, then rebuild.
"""
import math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920

C = {  # brand colours, plus the few shades the soil and worms need
    "soil": "#4F3433", "green": "#156826", "deep": "#22371F", "cream": "#F4F1EA",
    "tan": "#C89B7B", "light": "#59A66C", "purple": "#6B4C7A", "ink": "#333130",
    "tan_dark": "#B3876A", "tan_light": "#D9B597", "soil_dark": "#3A2625", "burrow": "#2B1C1B",
    "soil_light": "#654544",
    # worms
    "epi": "#B23A2C", "epi_ring": "#7A2219", "epi_clit": "#E07E66",
    "endo": "#EDB9AD", "endo_ring": "#C7877B", "endo_clit": "#F8DED6",
    "ane": "#6E2846", "ane_ring": "#431528", "ane_clit": "#A35D7A",
}

TEXT = {
    1: "Is World Earthworm Day even a thing?",
    "2h": "Yes, it's real.",
    "2b": "In 2016 the Earthworm Society of Britain nominated 21 October as World Earthworm Day, "
          "and they chose October to honor Charles Darwin, since his book on worms was published that month.",
    3: "Which earthworm are you today?",
    "opts": [("1", "Epigeic.", "Lives in the leaf litter and eats fast."),
             ("2", "Endogeic.", "Stays in the topsoil and eats its way through it."),
             ("3", "Anecic.", "Digs deep vertical burrows and comes up at night.")],
}

BURROW_X = 905  # centre of the anecic burrow on frames 1 and 2


# ---------------------------------------------------------------- geometry helpers
def catmull(pts, n=24):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def pts_attr(pts):
    return " ".join("%.1f,%.1f" % p for p in pts)


def poly(pts, fill, extra=""):
    return '<polygon points="%s" fill="%s"%s/>' % (pts_attr(pts), fill, extra)


def ragged_band(y_top, y_bot, rng, amp=14, step=36, x0=-20, x1=W + 20):
    """Polygon from a ragged top edge down to y_bot (a cut-paper soil layer)."""
    top = []
    x = x0
    y = y_top
    while x <= x1:
        top.append((x, y_top + rng.uniform(-amp, amp)))
        x += step * rng.uniform(.6, 1.4)
    top.append((x1, y_top + rng.uniform(-amp, amp)))
    return top + [(x1, y_bot), (x0, y_bot)]


def blob(cx, cy, r, rng, n=None, squash=1.0, rot=0.0):
    """An irregular cut-paper pebble."""
    n = n or rng.randint(6, 9)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-.25, .25)
        rr = r * rng.uniform(.7, 1.1)
        x, y = math.cos(a) * rr, math.sin(a) * rr * squash
        ca, sa = math.cos(rot), math.sin(rot)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


def leaf(cx, cy, length, width, angle, fill, vein, stem=True):
    """A pointed cut-paper leaf with a midrib, centred on (cx, cy), pointing along angle (radians)."""
    ca, sa = math.cos(angle), math.sin(angle)
    def T(u, v):
        return (cx + u * ca - v * sa, cy + u * sa + v * ca)
    half = length / 2
    upper, lower = [], []
    for k in range(13):
        t = k / 12
        u = -half + t * length
        w = width / 2 * math.sin(math.pi * t) ** 0.8
        upper.append(T(u, -w))
        lower.append(T(u, w))
    shape = upper + lower[::-1][1:-1]
    s = poly(shape, fill)
    s += '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="butt"/>' % (
        pts_attr([T(-half * 1.12 if stem else -half * .9, 0), T(half * .8, 0)]), vein, max(2.5, width * .07))
    for t in (.3, .5, .7):
        u = -half + t * length
        w = width / 2 * math.sin(math.pi * t) ** 0.8 * .75
        s += '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (
            pts_attr([T(u - length * .02, 0), T(u + length * .1, -w)]), vein, max(1.8, width * .045))
        s += '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (
            pts_attr([T(u - length * .02, 0), T(u + length * .1, w)]), vein, max(1.8, width * .045))
    return s


def worm(ctrl, width, body, ring, clit, edge="#F4F1EA", ring_gap=None, head_first=True, edge_w=7):
    """A cut-paper earthworm along the control points (head first): a paper edge, the body,
    segment rings across it, and a lighter clitellum band about a fifth of the way back."""
    c = catmull(ctrl, 30)
    if not head_first:
        c = c[::-1]
    # arc length
    L = [0.0]
    for i in range(1, len(c)):
        L.append(L[-1] + math.dist(c[i], c[i - 1]))
    total = L[-1]

    def prof(s):  # half width along the body: rounder head, longer tapering tail
        t = s / total
        if t < .06:
            f = .62 + .38 * (t / .06) ** .5
        elif t > .7:
            f = 1 - .58 * ((t - .7) / .3) ** 1.3
        else:
            f = 1.0
        return width / 2 * f

    def normal(i):
        a = c[max(i - 1, 0)]
        b = c[min(i + 1, len(c) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        return (-dy / d, dx / d), (dx / d, dy / d)

    def outline(grow=0.0, s0=0.0, s1=None, caps=True):
        s1 = total if s1 is None else s1
        left, right = [], []
        idx = [i for i in range(len(c)) if s0 <= L[i] <= s1]
        for i in idx:
            (nx, ny), _ = normal(i)
            r = prof(L[i]) + grow
            left.append((c[i][0] + nx * r, c[i][1] + ny * r))
            right.append((c[i][0] - nx * r, c[i][1] - ny * r))
        pts = left[:]
        if caps:  # round cap at the tail end
            i = idx[-1]
            (nx, ny), (tx, ty) = normal(i)
            r = prof(L[i]) + grow
            for k in range(1, 8):
                a = math.pi * k / 8
                pts.append((c[i][0] + (nx * math.cos(a) + tx * math.sin(a)) * r,
                            c[i][1] + (ny * math.cos(a) + ty * math.sin(a)) * r))
        pts += right[::-1]
        if caps:  # round head
            i = idx[0]
            (nx, ny), (tx, ty) = normal(i)
            r = prof(L[i]) + grow
            for k in range(1, 8):
                a = math.pi * k / 8
                pts.append((c[i][0] + (-nx * math.cos(a) - tx * math.sin(a)) * r,
                            c[i][1] + (-ny * math.cos(a) - ty * math.sin(a)) * r))
        return pts

    g = poly(outline(edge_w), edge) + poly(outline(), body)
    # clitellum: lighter, slightly swollen band behind the head
    cs0, cs1 = total * .16, total * .27
    g += poly(outline(width * .06, cs0, cs1, caps=False), clit)
    # segment rings
    gap = ring_gap or max(9.0, width * .32)
    s = gap * .8
    while s < total * .97:
        i = min(range(len(c)), key=lambda k: abs(L[k] - s))
        (nx, ny), _ = normal(i)
        r = prof(L[i]) * .92 + (width * .06 if cs0 <= s <= cs1 else 0)
        col = ring if not (cs0 <= s <= cs1) else body
        sw = max(2.2, width * .07)
        g += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"/>' % (
            c[i][0] + nx * r, c[i][1] + ny * r, c[i][0] - nx * r, c[i][1] - ny * r, col, sw)
        s += gap
    return '<g class="worm">%s</g>' % g, c[0]


def svg(w, h, body, title):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
            '<title>%s</title>%s</svg>') % (w, h, w, h, title, body)


# ---------------------------------------------------------------- frames 1 and 2: one tall cross-section
def tall_section():
    rng = random.Random(21)
    TH = H * 2
    s = []
    # topsoil fills everything; litter on top, subsoil at the bottom
    s.append('<rect width="%d" height="%d" fill="%s"/>' % (W, TH, C["tan"]))
    sub_y = 1920 + 1600
    s.append(poly(ragged_band(sub_y, TH + 20, rng, amp=18), C["soil"]))
    s.append(poly(ragged_band(sub_y + 70, TH + 20, rng, amp=12, step=60), C["soil_dark"]))
    # pebbles and crumbs in the topsoil
    for _ in range(170):
        x, y = rng.uniform(0, W), rng.uniform(560, sub_y - 30)
        r = rng.choice([5, 7, 9, 12, 16, 22])
        col = rng.choice([C["tan_dark"], C["tan_dark"], C["tan_light"], C["soil_light"]])
        s.append(poly(blob(x, y, r, rng, squash=rng.uniform(.6, 1), rot=rng.uniform(0, 3.1)), col))
    for _ in range(60):
        x, y = rng.uniform(0, W), rng.uniform(sub_y + 40, TH)
        s.append(poly(blob(x, y, rng.choice([6, 9, 13, 18]), rng, squash=.75, rot=rng.uniform(0, 3.1)),
                      rng.choice([C["soil_light"], C["burrow"]])))
    # a few fine roots hanging from the litter
    for x0 in (120, 330, 560):
        pts = [(x0, 520)]
        x, y = x0, 520
        for _ in range(7):
            x += rng.uniform(-30, 30)
            y += rng.uniform(80, 130)
            pts.append((x, y))
        s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="7" stroke-linejoin="round"/>' % (
            pts_attr(catmull(pts, 10)), C["tan_light"]))
    # the anecic burrow: one ragged vertical channel through both frames
    left, right = [], []
    y = 470
    while y <= TH + 40:
        wob = math.sin(y / 260) * 14
        left.append((BURROW_X - 66 + wob + rng.uniform(-6, 6), y))
        right.append((BURROW_X + 66 + wob + rng.uniform(-6, 6), y))
        y += 40
    s.append(poly(left + right[::-1], C["burrow"]))
    # midden: a small heap of cast soil round the burrow mouth
    s.append(poly([(BURROW_X - 150, 545), (BURROW_X - 90, 470), (BURROW_X - 60, 455), (BURROW_X + 60, 455),
                   (BURROW_X + 95, 468), (BURROW_X + 150, 545)], C["soil"]))
    # leaf litter band
    edge = [(x, 525 + rng.uniform(-16, 16)) for x in range(W + 20, -40, -40)]
    s.append(poly([(-20, -20), (W + 20, -20)] + edge, C["soil"]))
    lrng = random.Random(7)
    cols = [(C["green"], C["deep"]), (C["light"], C["green"]), (C["tan"], C["soil"]), (C["deep"], C["light"]),
            (C["tan_light"], C["tan_dark"]), (C["purple"], C["cream"]), (C["soil_light"], C["tan"])]
    for _ in range(95):
        x, y = lrng.uniform(-40, W + 40), lrng.uniform(-30, 520)
        if abs(x - BURROW_X) < 130 and y > 330:
            continue  # keep the burrow mouth open
        f, v = lrng.choice(cols)
        s.append(leaf(x, y, lrng.uniform(120, 210), lrng.uniform(55, 90), lrng.uniform(0, 6.28), f, v))
    # the anecic worm comes up the burrow and pulls a leaf down into it
    ctrl = [(BURROW_X + 4, 560), (BURROW_X - 14, 760), (BURROW_X + 16, 1050), (BURROW_X - 12, 1400),
            (BURROW_X + 14, 1780), (BURROW_X - 10, 2120), (BURROW_X + 6, 2440)]
    w, head = worm(ctrl, 92, C["ane"], C["ane_ring"], C["ane_clit"], ring_gap=26)
    s.append(leaf(BURROW_X - 14, 430, 240, 115, -1.45, C["green"], C["deep"]))  # under the head: the worm holds its stem
    s.append(w)
    # endogeic worm crossing frame 2 sideways through the topsoil
    yy = 1920 + 1420
    ctrl = [(1130, yy - 20), (930, yy + 40), (720, yy - 30), (520, yy + 35), (330, yy - 25), (150, yy + 20), (-60, yy - 10)]
    w2, _ = worm(ctrl, 58, C["endo"], C["endo_ring"], C["endo_clit"], edge=C["soil"], ring_gap=17, edge_w=6)
    s.append(w2)
    return "".join(s), TH


# ---------------------------------------------------------------- frame 3: three bands, one worm in each
def frame3():
    rng = random.Random(3)
    s = []
    B1, B2, B3 = 400, 790, 1185  # band tops: litter, topsoil, deep
    s.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, C["cream"]))
    s.append(poly(ragged_band(B1, H + 20, rng, amp=10), C["soil"]))   # litter ground
    s.append(poly(ragged_band(B2, H + 20, rng, amp=14), C["tan"]))   # topsoil
    s.append(poly(ragged_band(B3, H + 20, rng, amp=16), C["soil"]))  # deep
    s.append(poly(ragged_band(B3 + 60, H + 20, rng, amp=10, step=60), C["soil_dark"]))
    # litter leaves
    lrng = random.Random(11)
    cols = [(C["green"], C["deep"]), (C["light"], C["green"]), (C["tan"], C["soil"]), (C["deep"], C["light"]),
            (C["tan_light"], C["tan_dark"]), (C["purple"], C["cream"])]
    for _ in range(40):
        x, y = lrng.uniform(-30, 520), lrng.uniform(B1 + 10, B2 - 10)
        f, v = lrng.choice(cols)
        s.append(leaf(x, y, lrng.uniform(100, 170), lrng.uniform(45, 70), lrng.uniform(0, 6.28), f, v))
    # topsoil crumbs
    for _ in range(70):
        x, y = rng.uniform(0, 520), rng.uniform(B2 + 25, B3 - 25)
        s.append(poly(blob(x, y, rng.choice([5, 8, 11, 15]), rng, squash=.7, rot=rng.uniform(0, 3.1)),
                      rng.choice([C["tan_dark"], C["tan_light"], C["soil_light"]])))
    # deep crumbs (kept out of the bottom 350 px for the poll sticker)
    for _ in range(40):
        x, y = rng.uniform(0, 520), rng.uniform(B3 + 30, H - 380)
        s.append(poly(blob(x, y, rng.choice([6, 9, 13]), rng, squash=.75, rot=rng.uniform(0, 3.1)),
                      rng.choice([C["soil_light"], C["burrow"]])))
    # 1 epigeic: small, red, curled in the litter
    ctrl = [(330, 560), (260, 520), (185, 560), (175, 640), (250, 690), (350, 670), (395, 600), (370, 520)]
    # put a few leaves over and under it: draw a couple more leaves after it
    w, _ = worm(ctrl, 46, C["epi"], C["epi_ring"], C["epi_clit"], ring_gap=13, edge_w=6)
    s.append(w)
    s.append(leaf(110, 735, 150, 64, .4, C["green"], C["deep"]))
    s.append(leaf(440, 720, 130, 56, 2.6, C["tan"], C["soil"]))
    # 2 endogeic: pale, sideways through the topsoil
    yy = 990
    ctrl = [(500, yy - 10), (400, yy + 35), (290, yy - 30), (180, yy + 30), (70, yy - 15), (-40, yy + 10)]
    w, _ = worm(ctrl, 54, C["endo"], C["endo_ring"], C["endo_clit"], edge=C["soil"], ring_gap=16, edge_w=6)
    s.append(w)
    # 3 anecic: a vertical burrow in the deep band, pulling a leaf down
    bx = 270
    left, right = [], []
    for y in range(B3 - 30, H - 360, 30):
        left.append((bx - 58 + rng.uniform(-5, 5), y))
        right.append((bx + 58 + rng.uniform(-5, 5), y))
    s.append(poly(left + right[::-1], C["burrow"]))
    ctrl = [(bx + 2, B3 + 40), (bx - 12, B3 + 150), (bx + 12, B3 + 260), (bx - 8, B3 + 340)]
    w, _ = worm(ctrl, 74, C["ane"], C["ane_ring"], C["ane_clit"], ring_gap=22)
    s.append(leaf(bx - 6, B3 - 62, 190, 92, -1.5, C["green"], C["deep"]))
    s.append(w)
    # plain deep soil for the poll sticker (bottom 350 px): one flat colour, nothing on it
    s.append('<rect x="0" y="%d" width="%d" height="%d" fill="%s"/>' % (H - 350, W, 350, C["soil_dark"]))
    return "".join(s)


# ---------------------------------------------------------------- HTML frames (live text over the art)
CSS = """
@font-face { font-family: Montserrat; font-weight: 100 900; src: url("../../fonts/montserrat-latin-variable.woff2") format("woff2"); }
@font-face { font-family: "Source Sans 3"; font-weight: 400; src: url("../../fonts/source-sans-3-latin-400-normal.woff2") format("woff2"); }
@font-face { font-family: "Source Sans 3"; font-weight: 600 700; src: url("../../fonts/source-sans-3-latin-600-normal.woff2") format("woff2"); }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #F4F1EA; }
.frame { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
.art { position: absolute; left: 0; display: block; }
.box { position: absolute; }
.box::before { content: ""; position: absolute; inset: 0; transform: translate(14px, 14px); z-index: -1; }
.h { font-family: Montserrat, sans-serif; font-weight: 800; letter-spacing: -.01em; }
.b { font-family: "Source Sans 3", sans-serif; font-weight: 600; }
body.art-only .box { display: none; }
"""


def page(n, art_src, art_top, boxes):
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>World Earthworm Day, frame %d</title>
<style>%s</style></head><body><div class="frame">
<img class="art" src="%s" style="top:%dpx" width="1080" alt="">
%s
</div></body></html>""" % (n, CSS, art_src, art_top, boxes)


def main():
    os.makedirs(os.path.join(HERE, "art"), exist_ok=True)
    tall, TH = tall_section()
    open(os.path.join(HERE, "art", "frames-1-2-cross-section.svg"), "w").write(
        svg(W, TH, tall, "World Earthworm Day, frames 1 and 2: one soil cross-section"))
    open(os.path.join(HERE, "art", "frame-3.svg"), "w").write(svg(W, H, frame3(), "World Earthworm Day, frame 3"))

    f1 = ('<div class="box" style="left:60px;top:760px;width:760px;padding:58px 56px 64px;background:%s">'
          '<style>.f1::before{background:%s}</style>'
          '<p class="h" style="font-size:104px;line-height:1.02;color:%s">%s</p></div>') % (
        C["green"], C["deep"], C["cream"], TEXT[1])
    f1 = f1.replace('class="box"', 'class="box f1"')
    f2 = ('<div class="box f2" style="left:60px;top:150px;width:770px;padding:56px 56px 62px;background:%s">'
          '<style>.f2::before{background:%s}</style>'
          '<p class="h" style="font-size:86px;line-height:1.05;color:%s;margin-bottom:30px">%s</p>'
          '<p class="b" style="font-size:52px;line-height:1.28;color:%s">%s</p></div>') % (
        C["cream"], C["soil"], C["green"], TEXT["2h"], C["ink"], TEXT["2b"])
    f3 = ('<div class="box f3h" style="left:60px;top:96px;width:960px;padding:44px 52px 50px;background:%s">'
          '<style>.f3h::before{background:%s}.opt::before{background:%s}</style>'
          '<p class="h" style="font-size:86px;line-height:1.04;color:%s">%s</p></div>') % (
        C["green"], C["deep"], C["deep"], C["cream"], TEXT[3])
    tops = [450, 845, 1240]
    nums = [C["green"], C["purple"], C["soil"]]
    for (num, name, desc), top, nc in zip(TEXT["opts"], tops, nums):
        f3 += ('<div class="box opt" style="left:520px;top:%dpx;width:500px;padding:34px 38px 38px;background:%s">'
               '<p class="h" style="font-size:62px;line-height:1;color:%s;display:flex;align-items:center;gap:22px;margin-bottom:16px">'
               '<span style="display:inline-flex;align-items:center;justify-content:center;width:84px;height:84px;background:%s;color:%s">%s</span>%s</p>'
               '<p class="b" style="font-size:44px;line-height:1.22;color:%s">%s</p></div>') % (
            top, C["cream"], C["soil"], nc, C["cream"], num, name, C["ink"], desc)
    open(os.path.join(HERE, "frame-1.html"), "w").write(page(1, "art/frames-1-2-cross-section.svg", 0, f1))
    open(os.path.join(HERE, "frame-2.html"), "w").write(page(2, "art/frames-1-2-cross-section.svg", -1920, f2))
    open(os.path.join(HERE, "frame-3.html"), "w").write(page(3, "art/frame-3.svg", 0, f3))
    print("built art/ and frame-1..3.html")


if __name__ == "__main__":
    main()
