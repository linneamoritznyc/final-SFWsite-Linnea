#!/usr/bin/env python3
"""How It Works thumbnails as hand-built vector science illustrations.

    python3 tools/hiw_v3/vector.py [slug ...]

Same drawing language as the approved Presentation 2 diagrams (India decks):
flat fills, thin dark outlines, a speckled soil field, cream roots, green rod
bacteria, white fungal hyphae, glowing nutrient dots, gold flow arrows, and the
ciliate and plant icons reused from those diagrams (tools/hiw_v3/icons/).
No AI image generation is involved.

Writes docs/vector-thumbnails/<slug>-<option>.svg and .png (1920x1080, art
only, no title); compose_vector.py adds title and logo.
"""
import math, os, random, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs", "vector-thumbnails")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
W, H = 1920, 1080

INK = "#2B1D14"
SOIL, SPECK, SPECK2 = "#7A5C45", "#6B4A32", "#8A6446"
DEEP = "#3E2C22"
ROOT_FILL, ROOT_LINE = "#F4EBD3", "#C9B48F"
HYPHA = "#F8F3E6"
BAC, BAC_LINE = "#7DB05F", "#4F7C3F"
GOLD = "#D9A23A"
CREAM = "#F4F1EA"
SKY = "#E4EEDC"


def icon(name):
    with open(os.path.join(HERE, "icons", name + ".svgfrag"), encoding="utf-8") as f:
        return f.read()


DEFS = """<defs>
<radialGradient id="nglow"><stop offset="0" stop-color="#F4FF8A"/><stop offset=".5" stop-color="#C9F23A" stop-opacity=".8"/><stop offset="1" stop-color="#C9F23A" stop-opacity="0"/></radialGradient>
<radialGradient id="sglow"><stop offset="0" stop-color="#FFE08A"/><stop offset=".5" stop-color="#F5C04D" stop-opacity=".7"/><stop offset="1" stop-color="#F5C04D" stop-opacity="0"/></radialGradient>
<marker id="ahg" markerUnits="userSpaceOnUse" markerWidth="60" markerHeight="60" refX="34" refY="30" orient="auto"><path d="M0 4 L58 30 L0 56 z" fill="%s"/></marker>
<marker id="ahk" markerUnits="userSpaceOnUse" markerWidth="44" markerHeight="44" refX="26" refY="22" orient="auto"><path d="M0 2 L44 22 L0 42 z" fill="%s"/></marker>
</defs>""" % (GOLD, INK)


# ---------- geometry ----------

def bez(p0, p1, p2, p3, n=80):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def curve(pts, n=40):
    """Catmull-Rom through pts, sampled."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        seg = bez(p1, c1, c2, p2, n)
        out += seg if not out else seg[1:]
    return out


def normals(pl):
    ns = []
    for i in range(len(pl)):
        a, b = pl[max(i - 1, 0)], pl[min(i + 1, len(pl) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        ns.append((-dy / L, dx / L))
    return ns


def d_poly(pts, close=True):
    s = "M" + " L".join("%.1f %.1f" % p for p in pts)
    return s + (" Z" if close else "")


def d_smooth_closed(pts):
    """Smooth closed path through pts (Catmull-Rom as cubic beziers)."""
    n = len(pts)
    s = "M%.1f %.1f" % pts[0]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += " C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1 + c2 + p2)
    return s + " Z"


def blob(cx, cy, rx, ry, rnd, seed, k=11, rot=0):
    r = random.Random(seed)
    pts = []
    for i in range(k):
        a = 2 * math.pi * i / k + rot
        f = 1 + r.uniform(-rnd, rnd)
        pts.append((cx + math.cos(a) * rx * f, cy + math.sin(a) * ry * f))
    return d_smooth_closed(pts)


# ---------- drawing pieces ----------

def speckles(x0, y0, w, h, n, seed, cols=(SPECK, SPECK2)):
    r = random.Random(seed)
    return "".join('<circle cx="%d" cy="%d" r="%d" fill="%s" opacity=".55"/>'
                   % (x0 + r.random() * w, y0 + r.random() * h, r.randint(3, 10), r.choice(cols)) for _ in range(n))


def tube(pl, w0, w1, fill=ROOT_FILL, line=ROOT_LINE, lw=8, cap=True):
    """A tapered tube along polyline pl, width w0 -> w1, rounded tip."""
    ns = normals(pl)
    n = len(pl)
    left, right = [], []
    for i, (p, nn) in enumerate(zip(pl, ns)):
        w = (w0 + (w1 - w0) * (i / (n - 1))) / 2
        left.append((p[0] + nn[0] * w, p[1] + nn[1] * w))
        right.append((p[0] - nn[0] * w, p[1] - nn[1] * w))
    tip = []
    if cap:
        (x, y), (dx, dy) = pl[-1], (pl[-1][0] - pl[-2][0], pl[-1][1] - pl[-2][1])
        L = math.hypot(dx, dy) or 1
        a0 = math.atan2(ns[-1][1], ns[-1][0])
        for k in range(1, 12):
            a = a0 - math.pi * k / 12
            tip.append((x + math.cos(a) * w1 / 2, y + math.sin(a) * w1 / 2))
    pts = left + tip + right[::-1]
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%d" stroke-linejoin="round"/>' % (d_poly(pts), fill, line, lw)


def hairs(pl, w0, w1, every, length, seed, col=ROOT_LINE, sw=4):
    r = random.Random(seed)
    ns = normals(pl)
    out = []
    n = len(pl)
    for i in range(every // 2, n - 4, every):
        for side in (1, -1):
            if r.random() < .25:
                continue
            w = (w0 + (w1 - w0) * i / (n - 1)) / 2
            p, nn = pl[i], ns[i]
            L = length * r.uniform(.6, 1.1)
            x0, y0 = p[0] + nn[0] * w * side, p[1] + nn[1] * w * side
            x1, y1 = x0 + nn[0] * L * side, y0 + nn[1] * L * side
            bend = r.uniform(-.3, .3) * L
            out.append('<path d="M%.0f %.0f Q%.0f %.0f %.0f %.0f" stroke="%s" stroke-width="%d" fill="none" stroke-linecap="round"/>'
                       % (x0, y0, (x0 + x1) / 2 - nn[1] * bend, (y0 + y1) / 2 + nn[0] * bend, x1, y1, col, sw))
    return "".join(out)


def bacterium(x, y, ang, s=1.0, fill=BAC, line=BAC_LINE):
    w, h = 54 * s, 22 * s
    return ('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="%.0f" fill="%s" stroke="%s" stroke-width="%.1f" transform="rotate(%d %.0f %.0f)"/>'
            % (x - w / 2, y - h / 2, w, h, h / 2, fill, line, 3.5 * s, ang, x, y))


def bacteria_cloud(cx, cy, rx, ry, n, seed, s=1.0, avoid=None):
    r = random.Random(seed)
    out = []
    while len(out) < n:
        a, d = r.random() * 2 * math.pi, math.sqrt(r.random())
        x, y = cx + math.cos(a) * rx * d, cy + math.sin(a) * ry * d
        if avoid and avoid(x, y):
            continue
        out.append(bacterium(x, y, r.randint(0, 179), s * r.uniform(.85, 1.15)))
    return "".join(out)


def bacteria_along(pl, w, n, seed, s=1.0, spread=26):
    """Rods lying on a root surface, both sides."""
    r = random.Random(seed)
    ns = normals(pl)
    out = []
    for _ in range(n):
        i = r.randint(2, len(pl) - 3)
        side = r.choice((1, -1))
        p, nn = pl[i], ns[i]
        off = w / 2 + r.uniform(4, spread)
        x, y = p[0] + nn[0] * off * side, p[1] + nn[1] * off * side
        tang = math.degrees(math.atan2(nn[0], -nn[1])) + r.uniform(-35, 35)
        out.append(bacterium(x, y, tang, s * r.uniform(.85, 1.1)))
    return "".join(out)


def hypha(pts, seed, w=7, branches=6, blen=110, col=HYPHA, depth=2):
    pl = curve(pts, 30)
    r = random.Random(seed)
    out = ['<path d="%s" stroke="%s" stroke-width="%d" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
           % (d_poly(pl, False), col, w)]
    if depth == 0:
        return "".join(out)
    ns = normals(pl)
    for _ in range(branches):
        i = r.randint(len(pl) // 8, len(pl) - 4)
        p, nn = pl[i], ns[i]
        side = r.choice((1, -1))
        t = (pl[i + 2][0] - pl[i][0], pl[i + 2][1] - pl[i][1])
        L = math.hypot(*t) or 1
        t = (t[0] / L, t[1] / L)
        bl = blen * r.uniform(.6, 1.2)
        q1 = (p[0] + (t[0] * .5 + nn[0] * side * .7) * bl * .5, p[1] + (t[1] * .5 + nn[1] * side * .7) * bl * .5)
        q2 = (p[0] + (t[0] * .7 + nn[0] * side * .7) * bl, p[1] + (t[1] * .7 + nn[1] * side * .7) * bl)
        out.append(hypha([p, q1, q2], r.randint(0, 9999), max(w - 2, 3), branches // 2, blen * .55, col, depth - 1))
    return "".join(out)


def glow_dot(x, y, r=15):
    return ('<circle cx="%.0f" cy="%.0f" r="%.0f" fill="url(#nglow)"/><circle cx="%.0f" cy="%.0f" r="%.0f" fill="#E9FF6B" stroke="#9BC21B" stroke-width="2.5"/>'
            % (x, y, r * 2.4, x, y, r))


def sugar_dot(x, y, r=13):
    return ('<circle cx="%.0f" cy="%.0f" r="%.0f" fill="url(#sglow)"/><circle cx="%.0f" cy="%.0f" r="%.0f" fill="#F7C548" stroke="#B9821C" stroke-width="2.5"/>'
            % (x, y, r * 2.2, x, y, r))


def arrow(pts, col=GOLD, w=16, marker="ahg"):
    return ('<path d="%s" stroke="%s" stroke-width="%d" fill="none" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#%s)"/>'
            % (d_poly(curve(pts, 30), False), col, w, marker))


def ciliate(x, y, size, rot=0):
    """The ciliate icon from the Presentation 2 diagrams; size = drawn width in px (native ~2048)."""
    s = size / 2048
    return '<g transform="translate(%.0f %.0f) rotate(%d) scale(%.4f) translate(-1024 -1024)">%s</g>' % (x, y, rot, s, icon("ciliate"))


def plant(x, y, size, rot=0, wilt=False):
    """The line-drawn plant icon; (x, y) is where the stem meets the soil."""
    s = size / 2048
    body = icon("plant")
    if wilt:   # ochre, struggling version
        body = (body.replace("rgb(162,184,172)", "rgb(214,178,92)").replace("rgb(98,113,111)", "rgb(150,112,48)")
                .replace("rgb(227,227,226)", "rgb(240,226,190)"))
    # stem base of the icon sits near (1024, 1880) in its own units
    return '<g transform="translate(%.0f %.0f) rotate(%d) scale(%.4f) translate(-1010 -1830)">%s</g>' % (x, y, rot, s, body)


def nematode(pts, w, seed, fill="#E9D8BC", line="#8A6E4E"):
    pl = curve(pts, 40)
    n = len(pl)
    ns = normals(pl)
    left, right = [], []
    for i, (p, nn) in enumerate(zip(pl, ns)):
        t = i / (n - 1)
        ww = w / 2 * min(1, t * 7 + .25) * min(1, (1 - t) * 3.2 + .08)
        left.append((p[0] + nn[0] * ww, p[1] + nn[1] * ww))
        right.append((p[0] - nn[0] * ww, p[1] - nn[1] * ww))
    body = '<path d="%s" fill="%s" stroke="%s" stroke-width="5" stroke-linejoin="round"/>' % (d_poly(left + right[::-1]), fill, line)
    gut = '<path d="%s" stroke="#C9A97E" stroke-width="%d" fill="none" stroke-linecap="round" opacity=".8"/>' % (
        d_poly(pl[int(n * .12):int(n * .85)], False), max(3, w // 6))
    r = random.Random(seed)
    dots = "".join('<circle cx="%.0f" cy="%.0f" r="%d" fill="#B79468" opacity=".7"/>' % (
        pl[i][0] + ns[i][0] * r.uniform(-w * .2, w * .2), pl[i][1] + ns[i][1] * r.uniform(-w * .2, w * .2), r.randint(3, 5))
        for i in range(int(n * .18), int(n * .8), 7))
    head = pl[2]
    return body + gut + dots + '<circle cx="%.0f" cy="%.0f" r="%d" fill="%s"/>' % (head[0], head[1], max(3, w // 9), line)


def amoeba(cx, cy, r, seed, rot=0):
    body = blob(cx, cy, r, r * .82, .28, seed, 9, rot)
    return ('<path d="%s" fill="#DDE8E4" stroke="%s" stroke-width="6"/>' % (body, INK)
            + '<path d="%s" fill="#C3D9D2" opacity=".7"/>' % blob(cx, cy, r * .78, r * .62, .2, seed + 1, 9, rot)
            + '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="#66A4A4" stroke="%s" stroke-width="5"/>' % (cx - r * .15, cy - r * .1, r * .24, INK)
            + '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="#ABCDC6"/>' % (cx - r * .18, cy - r * .13, r * .12))


def pathogen(cx, cy, r):
    spikes = []
    for k in range(14):
        a = 2 * math.pi * k / 14
        spikes.append('<path d="M%.0f %.0f L%.0f %.0f" stroke="#3B2340" stroke-width="7" stroke-linecap="round"/>'
                      % (cx + math.cos(a) * r * .8, cy + math.sin(a) * r * .8, cx + math.cos(a) * r * 1.35, cy + math.sin(a) * r * 1.35))
    return ("".join(spikes) + '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="#6B3F6E" stroke="#2A1530" stroke-width="6"/>' % (cx, cy, r)
            + '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="#8E5C90"/>' % (cx - r * .25, cy - r * .25, r * .35))


def crumb(cx, cy, rx, ry, seed, fill="#8A6446", line="#5A3E29", grains=True):
    out = '<path d="%s" fill="%s" stroke="%s" stroke-width="6"/>' % (blob(cx, cy, rx, ry, .14, seed, 10), fill, line)
    if grains:
        r = random.Random(seed)
        for _ in range(int(rx * ry / 2200)):
            a, d = r.random() * 2 * math.pi, math.sqrt(r.random()) * .78
            gx, gy = cx + math.cos(a) * rx * d, cy + math.sin(a) * ry * d
            c = r.choice(("#B59A7A", "#A88B68", "#5E4330", "#C9B497"))
            out += '<path d="%s" fill="%s" opacity=".9"/>' % (blob(gx, gy, r.uniform(9, 22), r.uniform(8, 18), .3, r.randint(0, 9999), 6), c)
    return out


# ---------- plants, drawn in the line style of the plant icon ----------
LEAF_LIGHT, LEAF_DARK, LEAF_VEIN, LEAF_INK = "#E8EEE6", "#9DBBA4", "#5F7A66", "#26293A"
WILT_LIGHT, WILT_DARK, WILT_VEIN = "#F2E3BE", "#D3A85A", "#8E6A2E"


def leaf_on(pl, wmax, kind="ovate", teeth=0, light=LEAF_LIGHT, dark=LEAF_DARK, vein=LEAF_VEIN, ink=LEAF_INK, lw=5):
    """A two-tone leaf along midrib polyline pl: lighter half on one side, darker on the other."""
    n = len(pl)
    ns = normals(pl)

    def w(t):
        if kind == "strap":
            v = wmax * min(1, t * 8) * (1 - t) ** .55
        else:
            v = wmax * math.sin(math.pi * min(t * 1.05, 1)) ** .75
        if teeth:
            v *= 1 - .45 * ((t * teeth) % 1)
        if kind == "lobed":
            v *= .68 + .32 * math.sin(t * math.pi * 4.5) ** 2
        if kind == "wavy":
            v *= .9 + .1 * math.sin(t * math.pi * 14)
        if kind == "heart":
            v = wmax * math.sin(math.pi * min(t * 1.02, 1)) ** .5 * (1 - .55 * t)
        return v

    L = [(p[0] + nn[0] * w(i / (n - 1)), p[1] + nn[1] * w(i / (n - 1))) for i, (p, nn) in enumerate(zip(pl, ns))]
    R = [(p[0] - nn[0] * w(i / (n - 1)), p[1] - nn[1] * w(i / (n - 1))) for i, (p, nn) in enumerate(zip(pl, ns))]
    out = '<path d="%s" fill="%s"/>' % (d_poly(L + pl[::-1]), light)
    out += '<path d="%s" fill="%s"/>' % (d_poly(pl + R[::-1]), dark)
    if kind == "strap":
        for f in (.45, -.45):
            vp = [(p[0] + nn[0] * w(i / (n - 1)) * f, p[1] + nn[1] * w(i / (n - 1)) * f) for i, (p, nn) in enumerate(zip(pl, ns))]
            out += '<path d="%s" stroke="%s" stroke-width="2.5" fill="none" opacity=".8"/>' % (d_poly(vp[2:-4], False), vein)
    else:
        for i in range(n // 7, n - n // 6, max(3, n // 9)):
            t = i / (n - 1)
            j = min(n - 1, i + max(2, n // 12))
            for side, E in ((1, L), (-1, R)):
                e = E[j]
                out += '<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="3" opacity=".85"/>' % (
                    pl[i][0], pl[i][1], pl[i][0] + (e[0] - pl[i][0]) * .85, pl[i][1] + (e[1] - pl[i][1]) * .85, vein)
    out += '<path d="%s" stroke="%s" stroke-width="3.5" fill="none"/>' % (d_poly(pl[:-2], False), vein)
    out += '<path d="%s" fill="none" stroke="%s" stroke-width="%d" stroke-linejoin="round"/>' % (d_poly(L + R[::-1]), ink, lw)
    return out


def stem(pts, w0, w1, col="#8FAE8F", ink=LEAF_INK, lw=5):
    return tube(curve(pts, 30), w0, w1, fill=col, line=ink, lw=lw, cap=False)


def dandelion(x, y, s=1.0, wilt=False):
    """Rosette of toothed leaves at ground level, two yellow flower heads."""
    lc = dict(light=WILT_LIGHT, dark=WILT_DARK, vein=WILT_VEIN) if wilt else {}
    out = ""
    for k, (ang, ln) in enumerate([(-165, 300), (-140, 330), (-115, 280), (-65, 290), (-40, 330), (-15, 300), (-90, 250)]):
        a = math.radians(ang)
        bend = 60 * (1 if ang < -90 else -1)
        pts = [(x, y), (x + math.cos(a) * ln * .5 * s, y + math.sin(a) * ln * .5 * s),
               (x + math.cos(a) * ln * s - (0 if ang == -90 else bend * .0), y + math.sin(a) * ln * s + abs(bend) * .5 * s)]
        out += leaf_on(curve(pts, 20), 46 * s, teeth=5, **lc)
    if not wilt:
        for fx, fy, sx in [(x - 40 * s, y - 400 * s, -1), (x + 70 * s, y - 340 * s, 1)]:
            out += '<path d="M%.0f %.0f Q%.0f %.0f %.0f %.0f" stroke="%s" stroke-width="%d" fill="none"/>' % (
                x, y - 20, x + sx * 40 * s, (y + fy) / 2, fx, fy, LEAF_INK, 14 * s)
            out += '<path d="M%.0f %.0f Q%.0f %.0f %.0f %.0f" stroke="#8FAE8F" stroke-width="%d" fill="none"/>' % (
                x, y - 20, x + sx * 40 * s, (y + fy) / 2, fx, fy, 7 * s)
            for r_, col in ((62, "#E8A817"), (48, "#F4C430"), (28, "#F9DA62")):
                pet = []
                for i in range(36):
                    a = 2 * math.pi * i / 36
                    rr = r_ * s * (1 if i % 2 else .82)
                    pet.append((fx + math.cos(a) * rr, fy + math.sin(a) * rr))
                out += '<path d="%s" fill="%s" stroke="%s" stroke-width="%d"/>' % (d_poly(pet), col, "#9A6A10" if r_ == 62 else "none", 4 if r_ == 62 else 0)
    return out


def grass(x, y, s=1.0, n=7, wilt=False, seed=1):
    r = random.Random(seed)
    lc = dict(light=WILT_LIGHT, dark=WILT_DARK, vein=WILT_VEIN) if wilt else {}
    out = ""
    for k in range(n):
        a = math.radians(-90 + (k - n / 2) * 14 + r.uniform(-6, 6))
        ln = r.uniform(260, 380) * s
        lean = (k - n / 2) * 30 * s
        pts = [(x + (k - n / 2) * 8 * s, y), (x + math.cos(a) * ln * .5, y + math.sin(a) * ln * .5),
               (x + math.cos(a) * ln + lean, y + math.sin(a) * ln + (60 if wilt else 0) * s)]
        out += leaf_on(curve(pts, 20), 18 * s, kind="strap", **lc)
    return out


def corn(x, y, h, s=1.0):
    """Corn: tassel at the very top, cob halfway down in a green husk with silk, arching strap leaves."""
    top = y - h
    out = ""
    # leaves behind the stem
    for k, (fy, side, ln) in enumerate([(.16, 1, 380), (.30, -1, 420), (.44, 1, 330), (.60, -1, 380), (.74, -1, 280), (.86, -1, 150)]):
        by = y - h * fy
        pts = [(x, by), (x + side * ln * .45 * s, by - 170 * s), (x + side * ln * .85 * s, by - 120 * s), (x + side * ln * s, by + 40 * s)]
        out += leaf_on(curve(pts, 12), 40 * s, kind="strap")
    out += stem([(x, y), (x - 6, y - h * .5), (x, top + 40 * s)], 46 * s, 24 * s)
    # cob in husk, halfway down
    cy = y - h * .5
    cob = blob(x + 62 * s, cy - 10 * s, 34 * s, 90 * s, .03, 3, 14, 0.25)
    out += '<g transform="rotate(14 %.0f %.0f)">' % (x + 40 * s, cy)
    out += '<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="#F2D06B" stroke="%s" stroke-width="5"/>' % (x + 66 * s, cy - 30 * s, 40 * s, 100 * s, LEAF_INK)
    for k in range(-2, 3):
        out += '<path d="M%.0f %.0f L%.0f %.0f" stroke="#D9A23A" stroke-width="3"/>' % (x + 66 * s + k * 13 * s, cy - 115 * s, x + 66 * s + k * 13 * s, cy + 55 * s)
    out += leaf_on(curve([(x + 22 * s, cy + 80 * s), (x + 30 * s, cy - 20 * s), (x + 62 * s, cy - 130 * s)], 14), 34 * s, kind="strap")
    out += leaf_on(curve([(x + 110 * s, cy + 70 * s), (x + 104 * s, cy - 20 * s), (x + 74 * s, cy - 120 * s)], 14), 30 * s, kind="strap")
    for k in range(5):
        out += '<path d="M%.0f %.0f q%.0f %.0f %.0f %.0f" stroke="#B9821C" stroke-width="3" fill="none"/>' % (
            x + 68 * s, cy - 128 * s, (k - 2) * 14 * s, -40 * s, (k - 2) * 26 * s, -80 * s)
    out += '</g>'
    # tassel
    for k in range(7):
        a = math.radians(-90 + (k - 3) * 17)
        ln = (120 if k == 3 else 95) * s
        x2, y2 = x + math.cos(a) * ln, top + 40 * s + math.sin(a) * ln
        out += '<path d="M%.0f %.0f Q%.0f %.0f %.0f %.0f" stroke="#B9955A" stroke-width="%d" fill="none" stroke-linecap="round"/>' % (
            x, top + 40 * s, (x + x2) / 2, top + 10 * s, x2, y2 + 25 * s, 7 * s)
        for j in range(1, 5):
            t = j / 5
            px, py = x + (x2 - x) * t, top + 40 * s + (y2 + 25 * s - top - 40 * s) * t - 12 * s * math.sin(math.pi * t)
            out += '<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="#E2C988" stroke="#8E6A2E" stroke-width="2"/>' % (px, py, 6 * s, 10 * s)
    return out


def bean(x, y, s=1.0):
    """Bush bean: heart-shaped leaflets in threes, slim hanging pods."""
    out = stem([(x, y), (x - 10 * s, y - 180 * s), (x + 10 * s, y - 360 * s)], 22 * s, 14 * s)
    out += stem([(x - 6 * s, y - 170 * s), (x - 120 * s, y - 260 * s)], 12 * s, 8 * s)
    out += stem([(x + 4 * s, y - 250 * s), (x + 130 * s, y - 330 * s)], 12 * s, 8 * s)
    for k in range(3):   # pods
        px = x + (-40 + k * 34) * s
        out += leaf_on(curve([(px, y - 140 * s), (px + (k - 1) * 14 * s, y - 70 * s), (px + (k - 1) * 30 * s, y - 10 * s)], 14),
                       14 * s, kind="strap", light="#BFD99A", dark="#8DB86A", vein="#5F7A3E")
    for cx, cy, base in [(x - 120 * s, y - 260 * s, -150), (x + 130 * s, y - 330 * s, -30), (x + 10 * s, y - 360 * s, -90)]:
        for d in (-55, 0, 55):
            a = math.radians(base + d)
            ln = 150 * s
            pts = [(cx, cy), (cx + math.cos(a) * ln * .5, cy + math.sin(a) * ln * .5), (cx + math.cos(a) * ln, cy + math.sin(a) * ln)]
            out += leaf_on(curve(pts, 18), 62 * s, kind="heart")
    return out


def lettuce(x, y, s=1.0):
    """Butterhead lettuce: a ruffled rosette at ground level."""
    out = ""
    for ring, (n, ln, wd, lift) in enumerate([(7, 250, 170, 0), (5, 190, 150, 30), (3, 140, 120, 60)]):
        for k in range(n):
            a = math.radians(-180 + (k + .5) * 180 / n)
            pts = [(x, y - lift * s), (x + math.cos(a) * ln * .55 * s, y - lift * s + math.sin(a) * ln * .55 * s),
                   (x + math.cos(a) * ln * s, y - lift * s + math.sin(a) * ln * s * .9)]
            lc = dict(light="#EAF4D8", dark="#A9CF7A", vein="#6E8F4A") if ring else {}
            out += leaf_on(curve(pts, 18), wd * s, kind="heart", **lc)
    return out


def oak(x, y, h, s=1.0):
    """Young oak: brown trunk, branches, clusters of lobed leaves."""
    out = tube(curve([(x, y), (x + 6, y - h * .5), (x - 4, y - h * .78)], 30), 46 * s, 22 * s, fill="#8A6446", line=LEAF_INK, lw=5, cap=False)
    tips = []
    for k, (fy, side, ln) in enumerate([(.45, -1, 230), (.52, 1, 250), (.66, -1, 200), (.72, 1, 210), (.82, 0, 120)]):
        bx, by = x, y - h * fy
        ex, ey = bx + side * ln * s, by - (90 if side else 160) * s
        out += tube(curve([(bx, by), ((bx + ex) / 2, by - 50 * s), (ex, ey)], 16), 18 * s, 8 * s, fill="#8A6446", line=LEAF_INK, lw=4, cap=False)
        tips.append((ex, ey))
    r = random.Random(7)
    for ex, ey in tips:
        for d in (-60, 0, 60, 130):
            a = math.radians(-90 + d + r.uniform(-10, 10))
            ln = r.uniform(150, 185) * s
            pts = [(ex, ey), (ex + math.cos(a) * ln * .5, ey + math.sin(a) * ln * .5), (ex + math.cos(a) * ln, ey + math.sin(a) * ln)]
            out += leaf_on(curve(pts, 70), 58 * s, kind="lobed")
    return out


def tomato(x, y, s=1.0):
    """Tomato vine: compound leaves, red fruit hanging in clusters."""
    out = stem([(x, y), (x + 14 * s, y - 220 * s), (x - 6 * s, y - 470 * s)], 26 * s, 14 * s)
    for fy, side in [(.25, -1), (.42, 1), (.6, -1), (.78, 1), (.92, -1)]:
        bx, by = x + 6 * s, y - 470 * s * fy
        ex, ey = bx + side * 200 * s, by - 60 * s
        out += stem([(bx, by), ((bx + ex) / 2, by - 50 * s), (ex, ey)], 9 * s, 6 * s)
        for t in (.35, .65, 1.0):
            px, py = bx + (ex - bx) * t, by + (ey - by) * t - 40 * s * math.sin(math.pi * t)
            for d in ((-1, 1) if t < 1 else (0,)):
                a = math.atan2(ey - by, ex - bx) + (d * 1.1 if d else 0)
                ln = 75 * s
                out += leaf_on(curve([(px, py), (px + math.cos(a) * ln * .5, py + math.sin(a) * ln * .5 - 6), (px + math.cos(a) * ln, py + math.sin(a) * ln)], 14), 26 * s, kind="lobed")
    for cx, cy, n in [(x - 90 * s, y - 170 * s, 3), (x + 100 * s, y - 300 * s, 3)]:
        for k in range(n):
            fx, fy = cx + (k - 1) * 46 * s, cy + (abs(k - 1) * -18 + 40) * s
            out += '<path d="M%.0f %.0f L%.0f %.0f" stroke="#5F7A66" stroke-width="4"/>' % (cx, cy - 40 * s, fx, fy - 26 * s)
            out += '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="#D9442E" stroke="%s" stroke-width="5"/>' % (fx, fy, 32 * s, LEAF_INK)
            out += '<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="#F07A5E"/>' % (fx - 10 * s, fy - 12 * s, 9 * s, 6 * s)
            out += '<path d="M%.0f %.0f l%.0f %.0f M%.0f %.0f l%.0f %.0f" stroke="#5F7A66" stroke-width="4"/>' % (
                fx, fy - 30 * s, -12 * s, -6 * s, fx, fy - 30 * s, 12 * s, -6 * s)
    return out


def lens(inner, src, k, cx=1300, cy=500, R=420, spot=None, bg=SOIL):
    """A magnifier circle showing `inner` (drawn in full-frame coordinates) zoomed by k around src."""
    out = '<defs><clipPath id="lens"><circle cx="%d" cy="%d" r="%d"/></clipPath></defs>' % (cx, cy, R)
    if spot:
        sx, sy, sr = spot
        # tangent lines from the small spot circle to the lens
        d = math.hypot(cx - sx, cy - sy)
        a = math.atan2(cy - sy, cx - sx)
        b_ = math.asin((R - sr) / d)
        for sg in (1, -1):
            n = a + sg * (math.pi / 2 + b_)
            out += '<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="5"/>' % (
                sx + math.cos(n) * sr, sy + math.sin(n) * sr, cx + math.cos(n) * R, cy + math.sin(n) * R, INK)
        out += '<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="6"/>' % (sx, sy, sr, INK)
    out += '<g clip-path="url(#lens)"><rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (cx - R, cy - R, 2 * R, 2 * R, bg)
    out += '<g transform="translate(%d %d) scale(%.3f) translate(%d %d)">%s</g></g>' % (cx, cy, k, -src[0], -src[1], inner)
    out += '<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="22"/>' % (cx, cy, R + 8, CREAM)
    out += '<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="6"/>' % (cx, cy, R + 20, INK)
    out += '<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="6"/>' % (cx, cy, R - 3, INK)
    return out


def lens_scene(plant_svg, px, inner, src, k, soil_y=760):
    b = ground(soil_y, CREAM, 61)
    b += plant_svg
    b += roots_fan(px, soil_y, [[(px - 10, soil_y + 120), (px + 10, soil_y + 260)], [(px + 60, soil_y + 90), (px + 120, soil_y + 200)],
                                [(px - 60, soil_y + 100), (px - 120, soil_y + 190)]], 22)
    b += lens(inner, src, k * 360 / 400, 1320, 450, 360, spot=(px, soil_y + 150, 70))
    return b


def roots_fan(x, y, spec, w=22, seed=1):
    out = ""
    for pts in spec:
        out += tube(curve([(x, y)] + pts, 20), w, max(6, w // 3), lw=5)
    return out


def svg(body, bg=SOIL):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s<rect width="%d" height="%d" fill="%s"/>%s</svg>'
            % (W, H, W, H, DEFS, W, H, bg, body))


# ---------- the six scenes ----------
# Each returns the SVG body; the free area for the title is noted per scene.

def ground(soil_y, sky, seed, soil=SOIL):
    b = '<rect width="%d" height="%d" fill="%s"/>' % (W, soil_y, sky)
    b += '<rect y="%d" width="%d" height="%d" fill="%s"/>' % (soil_y, W, H - soil_y, soil)
    b += speckles(0, soil_y, W, H - soil_y, int(90 * (H - soil_y) / H) + 20, seed)
    return b + '<line x1="0" y1="%d" x2="%d" y2="%d" stroke="#5A3E29" stroke-width="6"/>' % (soil_y, W, soil_y)


def scene_food_web(opt):
    if opt == "B":
        return lens_scene(bean(430, 764, .85), 430, scene_food_web("A"), (1300, 700), .62)
    """A: close-up soil field around a root tip. B: bean plant above, the same community below."""
    if opt == "A":
        b = speckles(0, 0, W, H, 140, 1)
        rp = curve([(1320, -40), (1300, 260), (1330, 520), (1300, 760), (1270, 900)])
        top = 0
    else:
        b = ground(440, CREAM, 1)
        rp = curve([(1320, 440), (1305, 600), (1330, 760), (1300, 880), (1270, 960)])
        top = 440
    b += hypha([(1960, top + 260), (1700, top + 300), (1480, top + 380), (1350, top + 470)], 4, w=8, branches=7, blen=140)
    b += hypha([(1350, 760), (1500, 840), (1700, 880), (1960, 960)], 5, w=8, branches=6, blen=120)
    b += hairs(rp, 150, 80, 9, 70, 2)
    b += tube(rp, 150, 80)
    b += bacteria_along(rp, 120, 34, 3, 1.25)
    for x, y in [(1260, 975), (1305, 1010), (1225, 1030), (1335, 960)]:
        b += sugar_dot(x, y, 12)
    b += ciliate(1060 if opt == "A" else 1000, 720 if opt == "A" else 800, 560 if opt == "A" else 440, -25)
    b += nematode([(1480, 1070), (1560, 990), (1650, 1010), (1730, 950), (1820, 970)], 48, 7)
    b += bacteria_cloud(1660, 560 if opt == "A" else 700, 110, 80, 10, 8, 1.2)
    if opt == "B":
        b += bean(1320, 444, 1.05)
    return b


def scene_nutrient(opt):
    if opt == "B":
        return lens_scene(lettuce(430, 764, 1.0), 430, scene_nutrient("A"), (1100, 520), .58)
    """A: soil field, amoeba eating bacteria next to a root hair. B: lettuce above, the same loop below."""
    if opt == "A":
        b = speckles(0, 0, W, H, 140, 11)
        rp = curve([(-60, 120), (300, 170), (620, 290), (880, 470)])
        cy = 560
    else:
        b = ground(330, CREAM, 11)
        rp = curve([(420, 330), (520, 470), (700, 560), (900, 640)])
        cy = 720
        b += lettuce(420, 334, 1.0)
    b += hairs(rp, 100, 60, 6, 60, 12)
    b += tube(rp, 100, 60)
    cx = 1340
    b += ciliate(cx, cy, 700 if opt == "A" else 560, 20)
    b += bacteria_cloud(1380, cy + 40, 520, 380 if opt == "A" else 300, 22, 13, 1.3,
                        avoid=lambda x, y: math.hypot((x - cx) / 330, (y - cy) / 240) < 1 or y < (0 if opt == "A" else 360) or (x > 1500 and y < 300))
    for x, y in ([(1040, 600), (980, 545), (920, 505), (1090, 660)] if opt == "A" else [(1080, 760), (1020, 710), (960, 670), (1130, 810)]):
        b += glow_dot(x, y, 17)
    b += arrow([(1090, 700), (990, 610), (930, 550)] if opt == "A" else [(1120, 850), (1030, 760), (960, 700)], w=14)
    return b


def scene_structure(opt):
    """A: crumbs in a soil field. B: the same crumbs as a specimen on cream."""
    b = speckles(0, 0, W, H, 120, 21) if opt == "A" else '<rect width="%d" height="%d" fill="%s"/>' % (W, H, CREAM)
    crumbs = [(1180, 380, 300, 260, 1), (1620, 740, 280, 250, 2), (980, 860, 230, 200, 3), (1740, 230, 200, 170, 4)]
    for cx, cy, rx, ry, sd in crumbs:
        b += crumb(cx, cy, rx, ry, sd)
    for cx, cy, rx, ry, sd in crumbs:
        r = random.Random(sd)
        for _ in range(8):
            a = r.random() * 2 * math.pi
            b += bacterium(cx + math.cos(a) * rx * r.uniform(.3, .8), cy + math.sin(a) * ry * r.uniform(.3, .8), r.randint(0, 179), 1.25)
    col = HYPHA if opt == "A" else "#FFFFFF"
    hl = "" if opt == "A" else ' style="filter:drop-shadow(0 0 2px #8A6E4E)"'
    hy = hypha([(700, 300), (900, 250), (1150, 140), (1400, 180), (1560, 330), (1700, 470), (1900, 520)], 22, w=8, branches=8, blen=120, col=col)
    hy += hypha([(860, 1100), (900, 700), (1100, 640), (1380, 560), (1560, 520), (1820, 560), (1960, 760)], 23, w=8, branches=8, blen=120, col=col)
    hy += hypha([(1300, 1100), (1380, 900), (1500, 640), (1460, 420), (1380, 250), (1500, 40)], 24, w=7, branches=6, blen=100, col=col)
    b += "<g%s>%s</g>" % (hl, hy)
    for x, y, rr in [(1420, 600, 26), (1280, 700, 18), (1820, 450, 20)]:
        b += '<circle cx="%d" cy="%d" r="%d" fill="#BFE3F5" stroke="#4C8FBF" stroke-width="4"/>' % (x, y, rr)
    return b


def scene_weed(opt):
    soil_y = 680
    sky_l, sky_r = {"A": (CREAM, CREAM), "B": ("#F6EED3", "#2E6B3A"), "C": (SKY, SKY)}[opt]
    b = '<rect width="%d" height="%d" fill="%s"/>' % (W // 2, soil_y, sky_l)
    b += '<rect x="%d" width="%d" height="%d" fill="%s"/>' % (W // 2, W - W // 2, soil_y, sky_r)
    # one soil band: left disturbed (pale, bacterial), right fungal (dark)
    b += '<rect x="0" y="%d" width="%d" height="%d" fill="#B49372"/>' % (soil_y, W // 2, H - soil_y)
    b += '<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (W // 2, soil_y, W - W // 2, H - soil_y, SOIL)
    b += speckles(0, soil_y, W // 2, H - soil_y, 40, 31, ("#A2835F", "#C2A483"))
    b += speckles(W // 2, soil_y, W - W // 2, H - soil_y, 50, 32)
    b += '<line x1="0" y1="%d" x2="%d" y2="%d" stroke="#5A3E29" stroke-width="6"/>' % (soil_y, W, soil_y)
    # left: weeds thriving, shallow roots, bacteria
    b += roots_fan(560, soil_y, [[(540, 790), (500, 880)], [(600, 770), (680, 830)], [(510, 750), (420, 800)]], 26)
    b += roots_fan(270, soil_y, [[(260, 780), (230, 850)], [(300, 760), (350, 810)]], 18)
    b += bacteria_cloud(470, 880, 400, 150, 28, 33, 1.5)
    b += grass(270, soil_y + 4, .85, 8, seed=3)
    b += dandelion(600, soil_y + 4, .78)
    # right: corn with a fungal net around its roots; weeds fading at the border
    b += roots_fan(1440, soil_y, [[(1430, 860), (1450, 1110)], [(1530, 800), (1640, 920), (1700, 1080)], [(1350, 800), (1260, 920), (1220, 1080)],
                                  [(1480, 840), (1540, 1020)]], 30)
    b += hypha([(1150, 1110), (1260, 990), (1400, 920), (1560, 900), (1760, 970), (1980, 930)], 34, w=7, branches=10, blen=110)
    b += hypha([(1230, 740), (1380, 780), (1500, 930), (1650, 1020), (1940, 1070)], 35, w=7, branches=9, blen=100)
    b += hypha([(1700, 720), (1560, 800), (1450, 1000), (1380, 1110)], 36, w=6, branches=6, blen=90)
    b += corn(1420, soil_y + 6, 520, .95)
    b += dandelion(1090, soil_y + 4, .45, wilt=True)
    b += grass(1830, soil_y + 4, .5, 6, wilt=True, seed=9)
    return b


def scene_pests(opt):
    if opt == "C":
        return lens_scene(tomato(430, 764, .78), 430, scene_pests("A"), (1300, 640), .55)
    """A root sleeved in beneficial bacteria and fungi; a pathogen kept out. A: soil field. B: cream specimen."""
    b = speckles(0, 0, W, H, 140, 41) if opt == "A" else '<rect width="%d" height="%d" fill="%s"/>' % (W, H, CREAM)
    rp = curve([(2000, 470), (1500, 500), (1000, 570), (640, 660)])
    col = HYPHA if opt == "A" else "#FFFFFF"
    hy = hypha([(1960, 260), (1600, 380), (1300, 430), (1000, 490)], 42, w=7, branches=6, blen=110, col=col)
    hy += hypha([(1960, 780), (1600, 650), (1250, 660), (900, 720)], 43, w=7, branches=6, blen=110, col=col)
    b += hy if opt == "A" else '<g style="filter:drop-shadow(0 0 2px #8A6E4E)">%s</g>' % hy
    b += hairs(rp, 170, 110, 7, 70, 44)
    b += tube(rp, 170, 110)
    b += bacteria_along(rp, 150, 90, 45, 1.25, spread=40)
    b += pathogen(1000, 900, 72)
    b += ('<circle cx="1000" cy="900" r="132" fill="none" stroke="#C0392B" stroke-width="12"/>'
          '<line x1="907" y1="807" x2="1093" y2="993" stroke="#C0392B" stroke-width="12" stroke-linecap="round"/>')
    b += ciliate(1640, 880, 300, 30)
    return b


def scene_carbon(opt):
    """Oak pulls carbon from the air; a gold flow runs down the roots, along fungal threads, into dark soil clumps."""
    soil_y = 560
    b = ground(soil_y, SKY if opt == "A" else CREAM, 51)
    for pts in [[(600, 700), (620, 880)], [(700, 640), (800, 720)], [(500, 640), (420, 760)]]:
        b += tube(curve([(600, soil_y)] + pts, 20), 34, 12, lw=5)
    b += hypha([(640, 840), (860, 830), (1080, 860), (1320, 900), (1540, 900)], 52, w=8, branches=8, blen=110)
    b += hypha([(780, 720), (1000, 690), (1240, 700), (1480, 730), (1700, 690)], 53, w=7, branches=7, blen=100)
    for cx, cy, rx, ry, sd in [(1600, 880, 160, 125, 54), (1790, 680, 120, 100, 55), (1320, 990, 110, 80, 56)]:
        b += crumb(cx, cy, rx, ry, sd, fill="#2E2420", line="#17110E", grains=False)
    b += oak(600, soil_y + 6, 360, .85)
    b += arrow([(760, 230), (640, 330), (605, 540), (640, 800), (900, 830), (1200, 870), (1460, 880)], w=18)
    return b


SCENES = {
    "what-is-the-soil-food-web": scene_food_web,
    "nutrient-cycling": scene_nutrient,
    "formation-of-structure": scene_structure,
    "weed-suppression": scene_weed,
    "inhibiting-pests-and-diseases": scene_pests,
    "sequestering-carbon": scene_carbon,
}


def render(svg_path, png_path):
    """Headless Chromium; the window is taller than the art and the PNG is cropped to W x H."""
    html = svg_path[:-4] + ".html"
    with open(html, "w", encoding="utf-8") as f:
        f.write('<html><body style="margin:0;overflow:hidden"><img src="%s" width="%d" height="%d" style="display:block"></body></html>'
                % (os.path.basename(svg_path), W, H))
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=%d,%d" % (W, H + 200),
                    "--screenshot=" + png_path, "file://" + html], check=True, capture_output=True)
    os.remove(html)
    from PIL import Image
    Image.open(png_path).convert("RGB").crop((0, 0, W, H)).save(png_path)


OPTIONS = {
    "what-is-the-soil-food-web": "AB", "nutrient-cycling": "AB", "formation-of-structure": "AB",
    "weed-suppression": "ABC", "inhibiting-pests-and-diseases": "ABC", "sequestering-carbon": "AB",
}


def main(slugs, opts=None):
    os.makedirs(OUT, exist_ok=True)
    for slug in slugs:
        for o in opts or OPTIONS[slug]:
            p = os.path.join(OUT, "%s-%s" % (slug, o))
            with open(p + ".svg", "w", encoding="utf-8") as f:
                f.write(svg(SCENES[slug](o)))
            render(p + ".svg", p + ".png")
            print(p + ".png")


if __name__ == "__main__":
    main(sys.argv[1:] or list(SCENES))
