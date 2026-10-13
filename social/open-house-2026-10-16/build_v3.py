"""Open House post, version 3: you stand outside an open front door and look in.
The whole post is the front of the house in Food Web Green. The front door stands
open; through it you see a room full of SFW people and flowers, micrographs hanging on
the wall, and the living soil as the floor. The date is on the doormat.

Run from the repo root:
  python3 social/open-house-2026-10-16/build_v3.py
  node social/open-house-2026-10-16/make-pptx.js v3
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
LAYERS_DIR = os.path.join(HERE, "layers-v3")
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

# ================= FACADE =================
L = layer("facade-boards")
d = ImageDraw.Draw(L)
d.rectangle((0, 0, W, H), fill=DEEP)
for y in range(0, H, 34):
    d.line((0, y, W, y), fill=(28, 47, 26), width=3)
    d.line((0, y + 3, W, y + 3), fill=(44, 68, 40), width=1)

# door opening and room
OX0, OX1, OY0, OY1 = 262, 838, 318, 1196
FLOOR = 968
L = layer("room-wall")
d = ImageDraw.Draw(L)
d.rectangle((OX0, OY0, OX1, FLOOR), fill=PALE)
for x in range(OX0 + 20, OX1, 48):  # faint wallpaper stripes
    d.line((x, OY0, x, FLOOR), fill=(211, 225, 199), width=10)

# floor = living soil cross-section
L = layer("room-floor-soil")
tex = Image.open(os.path.join(IMG, "R5A_4027.jpg")).convert("RGB")
tex = tex.crop((int(tex.width * 0.42), int(tex.height * 0.42), tex.width, tex.height))
tex = tex.resize((OX1 - OX0, OY1 - FLOOR), Image.LANCZOS)
tex = Image.eval(tex, lambda v: int(v * 0.62))
L.paste(tex, (OX0, FLOOR))
d = ImageDraw.Draw(L)
band = [(x, 1110 + 9 * math.sin(x / 40.0)) for x in range(OX0, OX1 + 6, 6)]
d.polygon(band + [(OX1, OY1), (OX0, OY1)], fill=(60, 40, 35))
for x in range(OX0, OX1, 6):
    hgt = random.randint(8, 18)
    d.polygon([(x, FLOOR + 8), (x + 6, FLOOR + 8), (x + 3 + random.randint(-4, 4), FLOOR + 8 - hgt)],
              fill=random.choice([GREEN, (18, 88, 33), LIGHTG]))
R = Image.new("RGBA", (W, H), (0, 0, 0, 0))


def branch(dr, x, y, ang, length, width, depth):
    if depth == 0 or length < 7:
        return
    x2, y2 = x + length * math.cos(ang), y + length * math.sin(ang)
    if OX0 + 4 < x2 < OX1 - 4 and y2 < OY1 - 4:
        dr.line((x, y, x2, y2), fill=ROOT_C + (255,), width=max(1, int(width)))
    for _ in range(2 if depth > 1 else 3):
        branch(dr, x2, y2, ang + random.uniform(-0.7, 0.7), length * random.uniform(0.6, 0.8), width * 0.65, depth - 1)


rd = ImageDraw.Draw(R)
for x0 in (300, 455, 640, 800):
    branch(rd, x0, FLOOR + 8, math.pi / 2 + random.uniform(-0.2, 0.2), 48, 5, 5)
L.alpha_composite(shadow_of(R, 0.55, 3), (2, 3))
L.alpha_composite(R)

cutout("mycelium-on-bark", fit_w(rgba("mycelium-on-bark.webp"), 92), 735, 1128, angle=10, strength=0.5)
# micrographs in the soil, labelled
for f, label, x, y in (("Bacterial-feeding nematode (omnivore), 40x obj, Jane Monteagle.jpg", "NEMATODE", 345, 1062),
                       ("Fungal hypha, 100x obj, Marco Trevisan.jpg", "FUNGAL HYPHA", 550, 1085),
                       ("Naked amoeba (stellate), ciliate, 40x obj, Cameron Radman.jpg", "AMOEBA", 755, 1062)):
    im = disc(os.path.join(IMG, f), 84, ring=6, ring_col=CREAM)
    cutout("micrograph-" + label.lower().replace(" ", "-"), im, x - im.width // 2, y - im.height // 2, strength=0.6)
    TEXT.append(dict(name="label-" + label.lower().replace(" ", "-"), text=label, x=x - 80, y=y + im.height // 2 + 5,
                     w=160, h=18, font="Montserrat", size=13, bold=True, color=CREAM, align="center",
                     pil=ff("montserrat", 13, 700), anchor="ma", at=(x, y + im.height // 2 + 5)))

# earthworm
E = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ed = ImageDraw.Draw(E)
path = [(300 + 150 * (t / 50.0), 1170 + 10 * math.sin(t / 6.0)) for t in range(0, 51)]
for i, (x, y) in enumerate(path):
    rr = 8 * min(1, (i + 4) / 9, (len(path) - i + 3) / 9)
    ed.ellipse((x - rr, y - rr, x + rr, y + rr), fill=((196, 112, 112) if not 16 <= i <= 21 else (172, 86, 92)) + (255,))
for i in range(3, len(path) - 3, 3):
    x, y = path[i]
    ed.line((x, y - 7, x, y + 7), fill=(160, 84, 88, 200), width=2)
L = layer("earthworm")
L.alpha_composite(shadow_of(E, 0.55, 4), (3, 5))
L.alpha_composite(E)

# framed micrographs hanging on the back wall
for f, x, y in (("Bacterial-feeding nematode, 40x obj, Sid Jensen (I3).jpg", 330, 362),
                ("Testate amoeba (Arcella), 40x obj, Mark Horton.jpg", 700, 368)):
    im = disc(os.path.join(IMG, f), 88, ring=8)
    L = layer("wall-frame-" + os.path.basename(f).split(",")[0].lower().replace(" ", "-").replace("(", "").replace(")", ""))
    d = ImageDraw.Draw(L)
    d.line((x + im.width // 2, OY0 + 4, x + im.width // 2 - 22, y + 6), fill=SOIL, width=2)
    d.line((x + im.width // 2, OY0 + 4, x + im.width // 2 + 22, y + 6), fill=SOIL, width=2)
    L.alpha_composite(shadow_of(im), (x + 5, y + 8))
    L.alpha_composite(im, (x, y))

# people and flowers inside the room, standing on the soil
cheer = fit_h(cut("raw-cheering-cage.png", thr=170, keep=0.2), 290)
cutout("people-cheering-compost-cage", cheer, 545 - cheer.width // 2, FLOOR - 292)
cutout("person-misting-pile", fit_h(cut("raw-misting-man.png", box=(0, 0, 0.6, 1)), 360), OX0 + 6, FLOOR - 350)
cutout("person-kneeling-field", fit_h(cut("raw-kneeling-field.png", thr=170), 190), 452, FLOOR - 176)
smell = fit_h(cut("raw-smelling-compost.png"), 350)
cutout("person-smelling-compost", smell, OX1 - smell.width + 8, FLOOR - 338)
cutout("poppies", fit_h(cut("raw-poppies.png", thr=170, keep=0.02), 200), 395, FLOOR - 196)
clover = fit_h(rgba("crimson-clover-capri.webp"), 150)
cutout("clover-room", clover, 615, FLOOR - 140, angle=-4)
cutout("sfw-caps", fit_w(cut("raw-hats.png"), 120), 520, FLOOR - 52)

# door frame (drawn over the room edges)
L = layer("door-frame")
d = ImageDraw.Draw(L)
fr = 24
d.rectangle((OX0 - fr, OY0 - fr, OX1 + fr, OY0), fill=SOIL)
d.rectangle((OX0 - fr, OY0 - fr, OX0, OY1), fill=SOIL)
d.rectangle((OX1, OY0 - fr, OX1 + fr, OY1), fill=SOIL)
d.rectangle((OX0 - fr - 10, OY0 - fr - 16, OX1 + fr + 10, OY0 - fr), fill=(60, 38, 37))

# the door, swung open towards us on its left hinge
door = [(OX0 - fr, OY0 - 4), (60, OY0 - 60), (60, OY1 + 70), (OX0 - fr, OY1)]
L = layer("front-door-open")
ds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(ds).polygon([(x + 14, y + 16) for x, y in door], fill=(10, 14, 8, 130))
L.alpha_composite(ds.filter(ImageFilter.GaussianBlur(10)))
d = ImageDraw.Draw(L)
d.polygon(door, fill=GREEN)


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def door_pt(u, v):  # u: 0 hinge -> 1 free edge, v: 0 top -> 1 bottom
    top = lerp(door[0], door[1], u)
    bot = lerp(door[3], door[2], u)
    return lerp(top, bot, v)


for (u0, u1, v0, v1) in ((0.18, 0.82, 0.06, 0.40), (0.18, 0.82, 0.48, 0.92)):
    d.polygon([door_pt(u0, v0), door_pt(u1, v0), door_pt(u1, v1), door_pt(u0, v1)], fill=(18, 88, 33))
kx, ky = door_pt(0.88, 0.52)
d.ellipse((kx - 9, ky - 9, kx + 9, ky + 9), fill=CREAM)

# SFW logo plaque on the door
logo = fit_w(Image.open(os.path.join(ROOT, "img", "sfwlogo-240.png")).convert("RGBA"), 118)
pd = 142
plaque = Image.new("RGBA", (pd, pd), (0, 0, 0, 0))
pdr = ImageDraw.Draw(plaque)
pdr.ellipse((0, 0, pd - 1, pd - 1), fill=SOIL + (255,))
pdr.ellipse((6, 6, pd - 7, pd - 7), fill=CREAM + (255,))
plaque.alpha_composite(logo, ((pd - logo.width) // 2, (pd - logo.height) // 2 + 2))
px, py = door_pt(0.5, 0.23)
cutout("sfw-logo-door", plaque, px - pd // 2, py - pd // 2)

# outside: passion flower climbing the facade, clover and hats by the step
# a vine climbs the facade from a pot by the step
V = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(V)
vine = [(965 + 26 * math.sin(t / 55.0), t) for t in range(1150, 470, -6)]
vd.line(vine, fill=(46, 120, 52), width=6, joint="curve")
for i, (x, y) in enumerate(vine[4::9]):
    side = 1 if i % 2 else -1
    lx, ly = x + side * 30, y - 10
    vd.polygon([(x, y), (lx, ly - 14), (lx + side * 24, ly), (lx, ly + 12)], fill=random.choice([GREEN, LIGHTG, (18, 88, 33)]))
L = layer("vine")
L.alpha_composite(shadow_of(V, 0.5, 5), (5, 7))
L.alpha_composite(V)
cutout("passion-flower", fit_w(cut("raw-passion-flower.png", box=(0, 0, 1, 0.72)), 200), 862, 360, angle=-14)
cutout("orchid", fit_w(rgba("orchid-costa-rica.webp"), 150), 900, 700, angle=-8)
pot = Image.new("RGBA", (140, 104), (0, 0, 0, 0))
ImageDraw.Draw(pot).polygon([(0, 0), (140, 0), (118, 104), (22, 104)], fill=(178, 92, 60))
ImageDraw.Draw(pot).rectangle((0, 0, 140, 18), fill=(158, 78, 50))
cutout("clover-in-pot", fit_h(clover, 200), 922, 990, angle=4)
cutout("pot", pot, 900, 1146)

# step and doormat with the date
L = layer("step")
d = ImageDraw.Draw(L)
d.rectangle((OX0 - 60, OY1, OX1 + 60, OY1 + 26), fill=(150, 132, 118))
d.rectangle((OX0 - 60, OY1 + 26, OX1 + 60, OY1 + 34), fill=(110, 94, 84))
mat = Image.new("RGBA", (470, 92), (0, 0, 0, 0))
md = ImageDraw.Draw(mat)
md.rounded_rectangle((0, 0, 469, 91), radius=10, fill=(196, 160, 112))
for x in range(6, 466, 5):
    md.line((x, 8, x + random.randint(-2, 2), 84), fill=(176, 140, 94), width=2)
md.rounded_rectangle((10, 10, 459, 81), radius=6, outline=SOIL, width=3)
mat = mat.transform((470, 92), Image.AFFINE, (1, 0, 0, 0, 1, 0))
MX, MY = 305, OY1 + 40
cutout("doormat", mat, MX, MY)
TEXT.append(dict(name="date", text="FRIDAY, OCTOBER 16", x=MX, y=MY, w=470, h=92, font="Montserrat", size=34,
                 bold=True, color=SOIL, align="center", valign="middle", pil=ff("montserrat", 34, 800),
                 anchor="mm", at=(MX + 235, MY + 46)))

# ================= TYPE =================
TEXT += [
    dict(name="headline", text="Open House", x=0, y=40, w=W, h=190, font="EB Garamond", size=160, italic=True,
         color=CREAM, align="center", pil=ff("garamond-it", 160), anchor="ma", at=(W // 2, 28)),
    dict(name="subline", text="Come celebrate our first year", x=0, y=208, w=W, h=48, font="EB Garamond",
         size=36, color=(221, 232, 211), align="center", pil=ff("garamond", 36), anchor="ma", at=(W // 2, 204)),
]
PILL = None

# ================= OUTPUT =================
canvas = Image.new("RGBA", (W, H), DEEP + (255,))
for name, im in LAYERS:
    canvas.alpha_composite(im)
d = ImageDraw.Draw(canvas)
for t in TEXT:
    d.text(t["at"], t["text"], font=font(*t["pil"]), fill=t["color"], anchor=t.get("anchor", "la"))
out = os.path.join(HERE, "open-house-oct16-v3-1080x1350.png")
canvas.convert("RGB").save(out, optimize=True)

os.makedirs(LAYERS_DIR, exist_ok=True)
for f in os.listdir(LAYERS_DIR):
    os.remove(os.path.join(LAYERS_DIR, f))
layout = {"w": W, "h": H, "background": hexc(DEEP), "out": "open-house-oct16-v3-editable.pptx", "items": []}
for i, (name, im) in enumerate(LAYERS):
    bb = im.getbbox()
    fn = "%02d-%s.png" % (i + 1, name)
    im.crop(bb).save(os.path.join(LAYERS_DIR, fn), optimize=True)
    layout["items"].append({"type": "image", "name": name, "file": "layers-v3/" + fn,
                            "x": bb[0], "y": bb[1], "w": bb[2] - bb[0], "h": bb[3] - bb[1]})
for t in TEXT:
    layout["items"].append({"type": "text", **{k: t[k] for k in ("name", "text", "x", "y", "w", "h", "font", "size", "align")},
                            "bold": t.get("bold", False), "italic": t.get("italic", False),
                            "valign": t.get("valign", "top"), "color": hexc(t["color"])})
json.dump(layout, open(os.path.join(HERE, "layout-v3.json"), "w"), indent=1)
print(out)
