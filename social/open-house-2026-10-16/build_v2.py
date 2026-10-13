"""Open House post, version 2: the ground is cut open under the house.
Above ground: the house, the people, the flowers, a steaming compost pile, a laptop playing a
microscope webinar. Below ground: the soil food web Dr. Elaine Ingham taught, as a
cut-paper cross-section with roots, fungal hyphae, an earthworm, pebbles and five student
micrographs.

Run from the repo root:
  python3 social/open-house-2026-10-16/build_v2.py
  node social/open-house-2026-10-16/make-pptx.js v2
"""
import json
import math
import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
IMG = os.path.join(ROOT, "img", "new-2026-10")
CUT = os.path.join(HERE, "cutouts")
FONT = os.path.join(HERE, "fonts")
LAYERS_DIR = os.path.join(HERE, "layers-v2")
W, H = 1080, 1350
random.seed(16)

CREAM = (244, 241, 234)
DEEP = (34, 55, 31)
GREEN = (21, 104, 38)
LIGHTG = (89, 166, 108)
SOIL = (79, 52, 51)
PALE = (221, 232, 211)
ROOT_C = (228, 206, 168)


def hexc(c):
    return "%02X%02X%02X" % c


def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONT, name), size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def clean(path, thr=150, keep=0.04, box=None):
    im = Image.open(path).convert("RGBA")
    if box:
        w, h = im.size
        im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    m = np.array(im.split()[3]) > thr
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= sizes.max() * keep])
    im.putalpha(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8)))
    return im.crop(im.getbbox())


def fit_h(im, h):
    return im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)


def fit_w(im, w):
    return im.resize((w, max(1, int(im.height * w / im.width))), Image.LANCZOS)


def disc(path, d, ring=8, ring_col=SOIL):
    im = Image.open(path).convert("RGB")
    s = min(im.size)
    im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2))
    im = im.resize((d, d), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (d, d), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    im.putalpha(m)
    out = Image.new("RGBA", (d + 2 * ring, d + 2 * ring), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, d + 2 * ring - 1, d + 2 * ring - 1), fill=ring_col + (255,))
    out.alpha_composite(im, (ring, ring))
    return out


LAYERS = []
TEXT = []


def layer(name):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    LAYERS.append((name, im))
    return im


def shadow_of(im, strength=0.35, blur=6):
    sh = Image.new("RGBA", im.size, (30, 20, 15, 0))
    sh.putalpha(im.split()[3].point(lambda v: int(v * strength)).filter(ImageFilter.GaussianBlur(blur)))
    return sh


def cutout(name, im, x, y, angle=0, strength=0.35):
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    L = layer(name)
    L.alpha_composite(shadow_of(im, strength), (int(x) + 6, int(y) + 9))
    L.alpha_composite(im, (int(x), int(y)))


def ff(name, size, weight=None):
    return {"montserrat": "montserrat-latin-variable.ttf", "garamond-it": "eb-garamond-latin-500-italic.ttf",
            "garamond": "eb-garamond-latin-400-normal.ttf"}[name], size, weight


cut = lambda n, **k: clean(os.path.join(CUT, n), **k)
rgba = lambda n: Image.open(os.path.join(CUT, n)).convert("RGBA")

GY = 930  # ground line

# ================= ABOVE GROUND =================
L = layer("microscope-field-circle")
d = ImageDraw.Draw(L)
cx, cy, r = 540, 690, 300
d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PALE)
for k in range(60):
    a = math.radians(k * 6)
    r1, r2 = r + 9, r + (24 if k % 5 == 0 else 16)
    d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r2 * math.cos(a), cy + r2 * math.sin(a)),
           fill=LIGHTG, width=3 if k % 5 == 0 else 2)

# ---- the house, drawn at full size on its own canvas, then scaled down ----
G = Image.new("RGBA", (W, 1200), (0, 0, 0, 0))
hx0, hx1, wall_top, wall_bot = 330, 750, 735, 1093
body = Image.new("RGBA", G.size, (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
bd.rectangle((hx0, wall_top, hx1, wall_bot), fill=(232, 214, 190))
for yy in range(wall_top + 26, wall_bot, 26):
    bd.line((hx0, yy, hx1, yy), fill=(214, 192, 164), width=2)
bd.rectangle((655, 545, 705, 660), fill=SOIL)
bd.rectangle((645, 535, 715, 555), fill=(60, 38, 37))
bd.polygon([(hx0 - 45, wall_top + 8), (540, 530), (hx1 + 45, wall_top + 8)], fill=GREEN)
bd.polygon([(hx0 - 45, wall_top + 8), (540, 530), (540, wall_top + 8)], fill=(18, 88, 33))
bd.line([(hx0 - 45, wall_top + 8), (hx1 + 45, wall_top + 8)], fill=DEEP, width=8)
G.alpha_composite(shadow_of(body, 0.3, 10), (10, 12))
G.alpha_composite(body)


def gpaste(im, x, y):
    G.alpha_composite(shadow_of(im), (int(x) + 6, int(y) + 9))
    G.alpha_composite(im, (int(x), int(y)))


logo = fit_w(Image.open(os.path.join(ROOT, "img", "sfwlogo-240.png")).convert("RGBA"), 142)
pd = 172
plaque = Image.new("RGBA", (pd, pd), (0, 0, 0, 0))
pdr = ImageDraw.Draw(plaque)
pdr.ellipse((0, 0, pd - 1, pd - 1), fill=SOIL + (255,))
pdr.ellipse((7, 7, pd - 8, pd - 8), fill=CREAM + (255,))
plaque.alpha_composite(logo, ((pd - logo.width) // 2, (pd - logo.height) // 2 + 2))
gpaste(plaque, 540 - pd // 2, 650 - pd // 2)

dx0, dx1, dy0, dy1 = 478, 600, 862, wall_bot
inside = Image.open(os.path.join(IMG, "community-laughing-at-microscope.jpg")).convert("RGB")
iw, ih = inside.size
inside = inside.crop((int(iw * 0.12), int(ih * 0.08), int(iw * 0.62), int(ih * 0.98)))
ratio = (dx1 - dx0) / (dy1 - dy0)
cw, chh = inside.width, int(inside.width / ratio)
if chh > inside.height:
    chh, cw = inside.height, int(inside.height * ratio)
inside = inside.crop((0, 0, cw, chh)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS)
inside = Image.blend(inside, Image.new("RGB", inside.size, (255, 214, 150)), 0.12)
G.paste(inside, (dx0, dy0))
d = ImageDraw.Draw(G)
d.rectangle((dx0 - 8, dy0 - 8, dx1 + 8, dy0), fill=SOIL)
d.rectangle((dx0 - 8, dy0 - 8, dx0, dy1), fill=SOIL)
d.rectangle((dx1, dy0 - 8, dx1 + 8, dy1), fill=SOIL)
door = [(dx1 + 8, dy0 - 4), (dx1 + 88, dy0 + 26), (dx1 + 88, dy1 - 4), (dx1 + 8, dy1)]
ds = Image.new("RGBA", G.size, (0, 0, 0, 0))
ImageDraw.Draw(ds).polygon([(x + 8, y + 10) for x, y in door], fill=(40, 30, 20, 90))
G.alpha_composite(ds.filter(ImageFilter.GaussianBlur(6)))
d = ImageDraw.Draw(G)
d.polygon(door, fill=DEEP)
d.polygon([(dx1 + 22, dy0 + 18), (dx1 + 74, dy0 + 38), (dx1 + 74, dy0 + 100), (dx1 + 22, dy0 + 88)], fill=GREEN)
d.polygon([(dx1 + 22, dy0 + 112), (dx1 + 74, dy0 + 124), (dx1 + 74, dy1 - 24), (dx1 + 22, dy1 - 18)], fill=GREEN)
d.ellipse((dx1 + 70, dy0 + 112, dx1 + 82, dy0 + 124), fill=CREAM)
d.rectangle((dx0 - 22, dy1 - 2, dx1 + 22, dy1 + 14), fill=(120, 96, 80))
gpaste(disc(os.path.join(IMG, "Bacterial-feeding nematode, 40x obj, Sid Jensen (I3).jpg"), 96, ring=9), 365, 770)
gpaste(disc(os.path.join(IMG, "Testate amoeba (Arcella), 40x obj, Mark Horton.jpg"), 96, ring=9), 625, 760)
d = ImageDraw.Draw(G)
d.line((515, 806, 525, 826), fill=SOIL, width=2)
d.line((563, 806, 553, 826), fill=SOIL, width=2)
d.rounded_rectangle((492, 822, 586, 852), radius=4, fill=CREAM, outline=SOIL, width=2)
d.text((539, 838), "OPEN", font=font(*ff("montserrat", 17, 800)), fill=GREEN, anchor="mm")

S = 0.74
hb = G.getbbox()
G = G.crop(hb)
G = G.resize((int(G.width * S), int(G.height * S)), Image.LANCZOS)
step_bottom = (1107 - hb[1]) * S
hx = int(540 - (540 - hb[0]) * S)
hy = int(GY + 14 - step_bottom)
layer("house").alpha_composite(G, (hx, hy))

# ---- steaming thermophilic compost pile (compost photo cut into a mound) ----
px0, pw, ph = 728, 160, 96
tex = Image.open(os.path.join(IMG, "R5A_4027.jpg")).convert("RGB")
tex = tex.crop((int(tex.width * 0.5), int(tex.height * 0.45), int(tex.width * 0.95), int(tex.height * 0.8)))
tex = tex.resize((pw, ph), Image.LANCZOS).convert("RGBA")
m = Image.new("L", (pw, ph), 0)
ImageDraw.Draw(m).pieslice((0, 0, pw, ph * 2), 180, 360, fill=255)
tex.putalpha(m)
P = layer("compost-pile-steaming")
P.alpha_composite(shadow_of(tex), (px0 + 6, GY - ph + 16))
P.alpha_composite(tex, (px0, GY - ph + 8))
steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(steam)
for k, sx in enumerate((px0 + 45, px0 + 80, px0 + 115)):
    pts = [(sx + 8 * math.sin(t / 11.0 + k), GY - ph + 4 - t) for t in range(0, 80, 3)]
    sd.line(pts, fill=(200, 196, 188, 150), width=9, joint="curve")
P.alpha_composite(steam.filter(ImageFilter.GaussianBlur(5)))
cutout("compost-thermometer", fit_w(rgba("compost-thermometer.webp"), 70), px0 + 92, GY - ph - 22, angle=-18)

# ---- laptop showing the Living Legacy webinar ----
lw, lh = 150, 96
scr = Image.open(os.path.join(IMG, "Ciliate (stalked), 40x obj, Sid Jensen.jpg")).convert("RGB")
sw_, sh_ = lw - 12, lh - 12
k = max(sw_ / scr.width, sh_ / scr.height)
scr = scr.resize((int(scr.width * k) + 1, int(scr.height * k) + 1), Image.LANCZOS).crop((0, 0, sw_, sh_))
sdr = ImageDraw.Draw(scr)
pcx, pcy = sw_ // 2, sh_ // 2
sdr.ellipse((pcx - 18, pcy - 18, pcx + 18, pcy + 18), fill=(21, 104, 38))
sdr.polygon([(pcx - 6, pcy - 10), (pcx - 6, pcy + 10), (pcx + 11, pcy)], fill=CREAM)
lap = Image.new("RGBA", (lw + 40, lh + 18), (0, 0, 0, 0))
ldr = ImageDraw.Draw(lap)
ldr.rounded_rectangle((20, 0, 20 + lw, lh), radius=6, fill=(48, 48, 50))
lap.paste(scr, (26, 6))
ldr.polygon([(8, lh + 2), (32 + lw, lh + 2), (40 + lw, lh + 16), (0, lh + 16)], fill=(175, 175, 178))
ldr.rectangle((0, lh + 14, 40 + lw, lh + 17), fill=(120, 120, 124))
cutout("laptop-webinar-video", lap, 300, GY - lh - 8)

# ---- flowers and people ----
cutout("passion-flower", fit_w(cut("raw-passion-flower.png", box=(0, 0, 1, 0.72)), 200), 835, 450, angle=-12)
cutout("orchid", fit_w(rgba("orchid-costa-rica.webp"), 170), 135, 465, angle=8)
cutout("poppies", fit_h(cut("raw-poppies.png", thr=170, keep=0.02), 190), 225, GY - 185)
clover = fit_h(rgba("crimson-clover-capri.webp"), 150)
cutout("clover-left", clover, 318, GY - 128, angle=8)
cutout("clover-right", fit_h(clover, 130), 700, GY - 118, angle=-6)
cutout("person-misting-pile", fit_h(cut("raw-misting-man.png", box=(0, 0, 0.6, 1)), 310), 14, GY - 290)
cutout("person-kneeling-field", fit_h(cut("raw-kneeling-field.png", thr=170), 165), 190, GY - 150)
smell = fit_h(cut("raw-smelling-compost.png"), 300)
cutout("person-smelling-compost", smell, W - smell.width + 36, GY - 285)
cutout("sfw-caps", fit_w(cut("raw-hats.png"), 112), 610, GY - 40)

# ================= BELOW GROUND: the soil food web =================
SOILTOP = GY - 12
L = layer("soil-cross-section")
tex = Image.open(os.path.join(IMG, "R5A_4027.jpg")).convert("RGB")
tex = tex.crop((int(tex.width * 0.42), int(tex.height * 0.42), tex.width, tex.height)).resize((W, H - SOILTOP), Image.LANCZOS)
tex = Image.eval(tex, lambda v: int(v * 0.62)).convert("RGBA")
gm = Image.new("L", tex.size, 0)
edge = [(x, 10 + 8 * math.sin(x / 70.0) + 5 * math.sin(x / 23.0)) for x in range(0, W + 10, 10)]
ImageDraw.Draw(gm).polygon(edge + [(W, tex.height), (0, tex.height)], fill=255)
tex.putalpha(gm)
L.alpha_composite(tex, (0, SOILTOP))
# deeper horizons as cut paper layers
for top, col, amp in ((1150, (66, 44, 38), 14), (1265, (48, 33, 29), 10)):
    band = Image.new("RGBA", (W, H - top + 30), (0, 0, 0, 0))
    edge = [(x, 20 + amp * math.sin(x / 83.0 + top) + 6 * math.sin(x / 29.0)) for x in range(0, W + 10, 10)]
    ImageDraw.Draw(band).polygon(edge + [(W, band.height), (0, band.height)], fill=col + (255,))
    L.alpha_composite(shadow_of(band, 0.5, 8), (0, top - 26))
    L.alpha_composite(band, (0, top - 20))
# grass edge at the surface
gd = ImageDraw.Draw(L)
for x in range(-4, W + 4, 7):
    hgt = random.randint(10, 22)
    lean = random.randint(-5, 5)
    gd.polygon([(x, SOILTOP + 14), (x + 6, SOILTOP + 14), (x + 3 + lean, SOILTOP + 14 - hgt)],
               fill=random.choice([GREEN, (18, 88, 33), LIGHTG]))

# pebbles
L = layer("pebbles")
pd_ = ImageDraw.Draw(L)
for (x, y, rw, rh) in ((70, 1195, 34, 22), (238, 1300, 28, 18), (468, 1186, 22, 15), (640, 1318, 36, 22),
                       (905, 1192, 26, 17), (1010, 1308, 30, 20), (180, 1040, 18, 12), (850, 1060, 20, 13)):
    g = random.randint(150, 190)
    pd_.ellipse((x + 3, y + 5, x + rw + 3, y + rh + 5), fill=(20, 14, 12, 140))
    pd_.ellipse((x, y, x + rw, y + rh), fill=(g, g - 8, g - 18))
    pd_.ellipse((x + rw * 0.2, y + rh * 0.15, x + rw * 0.5, y + rh * 0.4), fill=(g + 30, g + 22, g + 12))


# roots from the plants above, branching down
def branch(dr, x, y, ang, length, width, depth):
    if depth == 0 or length < 8:
        return
    x2 = x + length * math.cos(ang)
    y2 = y + length * math.sin(ang)
    dr.line((x, y, x2, y2), fill=ROOT_C + (255,), width=max(1, int(width)))
    n = 2 if depth > 1 else 3
    for _ in range(n):
        branch(dr, x2, y2, ang + random.uniform(-0.65, 0.65), length * random.uniform(0.6, 0.8), width * 0.65, depth - 1)


R = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(R)
for x0, ln, w0 in ((262, 70, 6), (345, 60, 5), (735, 62, 5), (90, 55, 5), (985, 58, 5), (540, 40, 4)):
    branch(rd, x0, SOILTOP + 12, math.pi / 2 + random.uniform(-0.2, 0.2), ln, w0, 5)
L = layer("roots")
L.alpha_composite(shadow_of(R, 0.55, 3), (2, 3))
L.alpha_composite(R)

# fungal hyphae: fine white threads linking the roots
F = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fd = ImageDraw.Draw(F)
for k in range(9):
    x, y = random.randint(40, 1040), random.randint(1000, 1230)
    pts = [(x, y)]
    ang = random.uniform(0, math.tau)
    for _ in range(26):
        ang += random.uniform(-0.45, 0.45)
        x += 9 * math.cos(ang)
        y += 9 * math.sin(ang) * 0.6
        pts.append((x, y))
    fd.line(pts, fill=(250, 248, 240, 190), width=2, joint="curve")
    for j in range(4, len(pts) - 2, 6):
        bx, by = pts[j]
        ba = ang + random.choice((-1, 1)) * random.uniform(0.6, 1.2)
        fd.line((bx, by, bx + 26 * math.cos(ba), by + 26 * math.sin(ba)), fill=(250, 248, 240, 160), width=1)
layer("fungal-hyphae").alpha_composite(F)

cutout("compost-clump", fit_w(rgba("compost-clump.webp"), 105), 170, 1255, angle=-6, strength=0.5)
cutout("mycelium-on-bark", fit_w(rgba("mycelium-on-bark.webp"), 110), 815, 1240, angle=8, strength=0.5)

# earthworm, cut-paper
E = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ed = ImageDraw.Draw(E)
path = [(560 + 190 * (t / 60.0) - 95, 1238 + 26 * math.sin(t / 7.0)) for t in range(0, 61)]
for i, (x, y) in enumerate(path):
    rr = 11 * min(1, (i + 4) / 10, (len(path) - i + 3) / 10)
    col = (196, 112, 112) if not 20 <= i <= 26 else (172, 86, 92)
    ed.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + (255,))
for i in range(3, len(path) - 3, 3):
    x, y = path[i]
    x2, y2 = path[i + 1]
    a = math.atan2(y2 - y, x2 - x) + math.pi / 2
    ed.line((x - 9 * math.cos(a), y - 9 * math.sin(a), x + 9 * math.cos(a), y + 9 * math.sin(a)),
            fill=(160, 84, 88, 200), width=2)
L = layer("earthworm")
L.alpha_composite(shadow_of(E, 0.55, 5), (4, 6))
L.alpha_composite(E)

# five student micrographs, looking into the soil
MICRO = [
    ("Bacterial-feeding nematode (omnivore), 40x obj, Jane Monteagle.jpg", "NEMATODE", 120, 1075),
    ("Ciliate, 60x obj, Patricia J Coppola.jpg", "CILIATE", 335, 1165),
    ("Fungal hypha, 100x obj, Marco Trevisan.jpg", "FUNGAL HYPHA", 540, 1065),
    ("Naked amoeba (stellate), ciliate, 40x obj, Cameron Radman.jpg", "AMOEBA", 745, 1165),
    ("Testate amoeba (Arcella), 40x obj, Joy Kaluf.jpg", "TESTATE AMOEBA", 960, 1075),
]
DD = 112
for f, label, x, y in MICRO:
    im = disc(os.path.join(IMG, f), DD, ring=7, ring_col=CREAM)
    cutout("micrograph-" + label.lower().replace(" ", "-"), im, x - im.width // 2, y - im.height // 2, strength=0.6)
    TEXT.append(dict(name="label-" + label.lower().replace(" ", "-"), text=label, x=x - 90, y=y + im.height // 2 + 8,
                     w=180, h=22, font="Montserrat", size=15, bold=True, color=CREAM, align="center",
                     pil=ff("montserrat", 15, 700), anchor="ma", at=(x, y + im.height // 2 + 8)))

# ================= TYPE =================
L = Image.new("RGBA", (W, H))  # scratch, for measuring the date pill
TEXT += [
    dict(name="headline", text="Open House", x=64, y=118, w=900, h=200, font="EB Garamond", size=168, italic=True,
         color=DEEP, align="left", pil=ff("garamond-it", 168), at=(64, 108)),
    dict(name="subline", text="Come celebrate our first year", x=72, y=318, w=700, h=52, font="EB Garamond",
         size=38, color=SOIL, align="left", pil=ff("garamond", 38), at=(72, 316)),
]
pill_font = font(*ff("montserrat", 26, 700))
pill_w = int(ImageDraw.Draw(L).textlength("FRIDAY, OCTOBER 16", font=pill_font)) + 44
PILL = dict(x=72, y=380, w=pill_w, h=48, color=GREEN)
TEXT.append(dict(name="date", text="FRIDAY, OCTOBER 16", x=72, y=380, w=pill_w, h=48, font="Montserrat", size=26,
                 bold=True, color=CREAM, align="center", valign="middle", pil=ff("montserrat", 26, 700),
                 anchor="mm", at=(72 + pill_w // 2, 404)))

# ================= OUTPUT =================
canvas = Image.new("RGBA", (W, H), CREAM + (255,))
for name, im in LAYERS:
    canvas.alpha_composite(im)
d = ImageDraw.Draw(canvas)
d.rounded_rectangle((PILL["x"], PILL["y"], PILL["x"] + PILL["w"], PILL["y"] + PILL["h"]), radius=24, fill=GREEN)
for t in TEXT:
    d.text(t["at"], t["text"], font=font(*t["pil"]), fill=t["color"], anchor=t.get("anchor", "la"))
out = os.path.join(HERE, "open-house-oct16-v2-1080x1350.png")
canvas.convert("RGB").save(out, optimize=True)

os.makedirs(LAYERS_DIR, exist_ok=True)
for f in os.listdir(LAYERS_DIR):
    os.remove(os.path.join(LAYERS_DIR, f))
layout = {"w": W, "h": H, "background": hexc(CREAM), "out": "open-house-oct16-v2-editable.pptx", "items": []}
for i, (name, im) in enumerate(LAYERS):
    bb = im.getbbox()
    fn = "%02d-%s.png" % (i + 1, name)
    im.crop(bb).save(os.path.join(LAYERS_DIR, fn), optimize=True)
    layout["items"].append({"type": "image", "name": name, "file": "layers-v2/" + fn,
                            "x": bb[0], "y": bb[1], "w": bb[2] - bb[0], "h": bb[3] - bb[1]})
layout["items"].append({"type": "pill", "name": "date-pill", **{k: PILL[k] for k in "xywh"},
                        "color": hexc(PILL["color"])})
for t in TEXT:
    layout["items"].append({"type": "text", **{k: t[k] for k in ("name", "text", "x", "y", "w", "h", "font", "size", "align")},
                            "bold": t.get("bold", False), "italic": t.get("italic", False),
                            "valign": t.get("valign", "top"), "color": hexc(t["color"])})
json.dump(layout, open(os.path.join(HERE, "layout-v2.json"), "w"), indent=1)
print(out)
