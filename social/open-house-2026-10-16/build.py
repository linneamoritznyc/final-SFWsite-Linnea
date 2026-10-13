"""Open House post, Soil Food Web Foundation one-year anniversary (Fri Oct 16, 2026).
Cut-paper house with an open door in the centre, cut-outs of SFW people and flowers around it.

Run from the repo root:
  python3 social/open-house-2026-10-16/build.py      -> the PNG + layers/ + layout.json
  node social/open-house-2026-10-16/make-pptx.js     -> the editable PowerPoint

Every element is drawn on its own layer, so the PowerPoint gets each cut-out as a
separate picture you can move, and the text as real text boxes.
"""
import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
IMG = os.path.join(ROOT, "img", "new-2026-10")
CUT = os.path.join(HERE, "cutouts")
FONT = os.path.join(HERE, "fonts")
LAYERS_DIR = os.path.join(HERE, "layers")
W, H = 1080, 1350

CREAM = (244, 241, 234)
DEEP = (34, 55, 31)
GREEN = (21, 104, 38)
LIGHTG = (89, 166, 108)
SOIL = (79, 52, 51)
PALE = (221, 232, 211)


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
    """Hard-edge the rembg alpha (removes ghosting), drop small specks, light feather."""
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


def disc(path, d, ring=10, ring_col=SOIL):
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


# ---------------- layer system ----------------
LAYERS = []  # (name, full-canvas RGBA)


def layer(name):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    LAYERS.append((name, im))
    return im


def shadow_of(im, strength=0.35, blur=6):
    sh = Image.new("RGBA", im.size, (40, 30, 20, 0))
    sh.putalpha(im.split()[3].point(lambda v: int(v * strength)).filter(ImageFilter.GaussianBlur(blur)))
    return sh


def cutout(name, im, x, y, angle=0):
    """One cut-out on its own layer, with a paper drop shadow."""
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    L = layer(name)
    L.alpha_composite(shadow_of(im), (int(x) + 6, int(y) + 9))
    L.alpha_composite(im, (int(x), int(y)))


TEXT = []  # native text boxes for PowerPoint


# ---------- microscope-field circle behind the house ----------
L = layer("microscope-field-circle")
d = ImageDraw.Draw(L)
cx, cy, r = 540, 770, 375
d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PALE)
for k in range(60):
    ang = np.deg2rad(k * 6)
    r1, r2 = r + 10, r + (26 if k % 5 == 0 else 18)
    d.line((cx + r1 * np.cos(ang), cy + r1 * np.sin(ang), cx + r2 * np.cos(ang), cy + r2 * np.sin(ang)),
           fill=LIGHTG, width=3 if k % 5 == 0 else 2)

# ---------- ground: real compost photo, wavy top edge ----------
GY = 1075
tex = Image.open(os.path.join(IMG, "R5A_4007.jpg")).convert("RGB")
tex = tex.crop((0, 0, int(tex.width * 0.42), int(tex.height * 0.55)))
tex = tex.resize((W, H - GY + 30), Image.LANCZOS)
tex = Image.eval(tex, lambda v: int(v * 0.82)).convert("RGBA")
gm = Image.new("L", tex.size, 0)
pts = [(x, 30 + 16 * np.sin(x / 95.0) + 9 * np.sin(x / 37.0)) for x in range(0, W + 10, 10)]
ImageDraw.Draw(gm).polygon(pts + [(W, tex.height), (0, tex.height)], fill=255)
tex.putalpha(gm)
layer("ground-compost").alpha_composite(tex, (0, GY - 30))

# ---------- the house (cut paper) ----------
hx0, hx1, wall_top, wall_bot = 330, 750, 735, GY + 18
body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
bd.rectangle((hx0, wall_top, hx1, wall_bot), fill=(232, 214, 190))
for yy in range(wall_top + 26, wall_bot, 26):
    bd.line((hx0, yy, hx1, yy), fill=(214, 192, 164), width=2)
bd.rectangle((655, 545, 705, 660), fill=SOIL)
bd.rectangle((645, 535, 715, 555), fill=(60, 38, 37))
bd.polygon([(hx0 - 45, wall_top + 8), (540, 530), (hx1 + 45, wall_top + 8)], fill=GREEN)
bd.polygon([(hx0 - 45, wall_top + 8), (540, 530), (540, wall_top + 8)], fill=(18, 88, 33))
bd.line([(hx0 - 45, wall_top + 8), (hx1 + 45, wall_top + 8)], fill=DEEP, width=8)
L = layer("house")
L.alpha_composite(shadow_of(body, 0.3, 10), (10, 12))
L.alpha_composite(body)

# logo plaque in the roof gable
logo = fit_w(Image.open(os.path.join(ROOT, "img", "sfwlogo-240.png")).convert("RGBA"), 142)
pd = 172
plaque = Image.new("RGBA", (pd, pd), (0, 0, 0, 0))
pdr = ImageDraw.Draw(plaque)
pdr.ellipse((0, 0, pd - 1, pd - 1), fill=SOIL + (255,))
pdr.ellipse((7, 7, pd - 8, pd - 8), fill=CREAM + (255,))
plaque.alpha_composite(logo, ((pd - logo.width) // 2, (pd - logo.height) // 2 + 2))
cutout("sfw-logo-roof", plaque, 540 - pd // 2, 650 - pd // 2)

# doorway: a workshop photo inside, door frame, open door, step
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
L = layer("doorway-photo")
L.paste(inside, (dx0, dy0))

L = layer("door-open")
d = ImageDraw.Draw(L)
d.rectangle((dx0 - 8, dy0 - 8, dx1 + 8, dy0), fill=SOIL)
d.rectangle((dx0 - 8, dy0 - 8, dx0, dy1), fill=SOIL)
d.rectangle((dx1, dy0 - 8, dx1 + 8, dy1), fill=SOIL)
door = [(dx1 + 8, dy0 - 4), (dx1 + 88, dy0 + 26), (dx1 + 88, dy1 - 4), (dx1 + 8, dy1)]
ds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(ds).polygon([(x + 8, y + 10) for x, y in door], fill=(40, 30, 20, 90))
L.alpha_composite(ds.filter(ImageFilter.GaussianBlur(6)))
d = ImageDraw.Draw(L)
d.polygon(door, fill=DEEP)
d.polygon([(dx1 + 22, dy0 + 18), (dx1 + 74, dy0 + 38), (dx1 + 74, dy0 + 100), (dx1 + 22, dy0 + 88)], fill=GREEN)
d.polygon([(dx1 + 22, dy0 + 112), (dx1 + 74, dy0 + 124), (dx1 + 74, dy1 - 24), (dx1 + 22, dy1 - 18)], fill=GREEN)
d.ellipse((dx1 + 70, dy0 + 112, dx1 + 82, dy0 + 124), fill=CREAM)
d.rectangle((dx0 - 22, dy1 - 2, dx1 + 22, dy1 + 14), fill=(120, 96, 80))

# round windows with student micrographs
cutout("window-nematode", disc(os.path.join(IMG, "Bacterial-feeding nematode, 40x obj, Sid Jensen (I3).jpg"), 96, ring=9), 365, 770)
cutout("window-arcella", disc(os.path.join(IMG, "Testate amoeba (Arcella), 40x obj, Mark Horton.jpg"), 96, ring=9), 625, 760)

# OPEN sign (strings + board as a picture, the word as a text box)
L = layer("open-sign")
d = ImageDraw.Draw(L)
d.line((515, 806, 525, 826), fill=SOIL, width=2)
d.line((563, 806, 553, 826), fill=SOIL, width=2)
d.rounded_rectangle((492, 822, 586, 852), radius=4, fill=CREAM, outline=SOIL, width=2)
TEXT.append(dict(name="open-sign-text", text="OPEN", x=492, y=822, w=94, h=30, font="Montserrat",
                 size=17, bold=True, color=GREEN, align="center", valign="middle",
                 pil=("montserrat-latin-variable.ttf", 17, 800), anchor="mm", at=(539, 838)))

# ---------- cut-outs ----------
cut = lambda n, **k: clean(os.path.join(CUT, n), **k)
rgba = lambda n: Image.open(os.path.join(CUT, n)).convert("RGBA")

cutout("poppies", fit_h(cut("raw-poppies.png", thr=170, keep=0.02), 230), 250, GY - 215)
cutout("person-kneeling-field", fit_h(cut("raw-kneeling-field.png", thr=170), 215), 175, GY - 150)
cutout("passion-flower", fit_w(cut("raw-passion-flower.png", box=(0, 0, 1, 0.72)), 230), 790, 470, angle=-12)
cutout("orchid", fit_w(rgba("orchid-costa-rica.webp"), 200), 120, 520, angle=8)
clover = fit_h(rgba("crimson-clover-capri.webp"), 190)
cutout("clover-right", clover, 770, GY - 150, angle=-6)
cutout("clover-left", fit_h(clover, 150), 300, GY - 115, angle=10)

cutout("person-misting-pile", fit_h(cut("raw-misting-man.png", box=(0, 0, 0.6, 1)), 400), 18, GY - 300)
smell = fit_h(cut("raw-smelling-compost.png"), 390)
cutout("person-smelling-compost", smell, W - smell.width + 40, GY - 280)
fork = fit_h(cut("raw-woman-manure-fork.png", thr=170), 290)
cutout("person-manure-fork", fork, -30, H - fork.height + 4)
crouch = fit_h(cut("raw-crouching-garden.png", thr=170), 300)
cutout("person-crouching-garden", crouch, W - crouch.width + 20, H - crouch.height + 4)

cutout("sfw-caps", fit_w(cut("raw-hats.png"), 210), 420, H - 210)
cutout("compost-thermometer", fit_w(rgba("compost-thermometer.webp"), 120), 640, H - 170, angle=-15)

# ---------- type ----------
TEXT += [
    dict(name="kicker-left", text="SOIL FOOD WEB FOUNDATION", x=70, y=58, w=520, h=34, font="Montserrat",
         size=21, bold=True, color=DEEP, align="left", pil=("montserrat-latin-variable.ttf", 21, 700), at=(70, 62)),
    dict(name="kicker-right", text="TURNING ONE", x=W - 70 - 300, y=58, w=300, h=34, font="Montserrat",
         size=21, bold=True, color=DEEP, align="right", pil=("montserrat-latin-variable.ttf", 21, 700),
         anchor="ra", at=(W - 70, 62)),
    dict(name="headline", text="Open House", x=64, y=118, w=900, h=200, font="EB Garamond", size=168,
         italic=True, color=DEEP, align="left", pil=("eb-garamond-latin-500-italic.ttf", 168, None), at=(64, 108)),
    dict(name="subline", text="Come celebrate our first year", x=72, y=318, w=700, h=52, font="EB Garamond",
         size=38, color=SOIL, align="left", pil=("eb-garamond-latin-400-normal.ttf", 38, None), at=(72, 316)),
]

# divider line under the kickers, date pill
L = layer("kicker-rule")
ImageDraw.Draw(L).line((70, 100, W - 70, 100), fill=(190, 200, 180), width=2)
pill_font = font("montserrat-latin-variable.ttf", 26, 700)
pill_w = int(ImageDraw.Draw(L).textlength("FRIDAY, OCTOBER 16", font=pill_font)) + 44
PILL = dict(x=72, y=380, w=pill_w, h=48, color=GREEN)
TEXT.append(dict(name="date", text="FRIDAY, OCTOBER 16", x=72, y=380, w=pill_w, h=48, font="Montserrat",
                 size=26, bold=True, color=CREAM, align="center", valign="middle",
                 pil=("montserrat-latin-variable.ttf", 26, 700), anchor="mm", at=(72 + pill_w // 2, 404)))

# ---------- flatten to PNG ----------
canvas = Image.new("RGBA", (W, H), CREAM + (255,))
for name, im in LAYERS:
    canvas.alpha_composite(im)
d = ImageDraw.Draw(canvas)
d.rounded_rectangle((PILL["x"], PILL["y"], PILL["x"] + PILL["w"], PILL["y"] + PILL["h"]), radius=24, fill=GREEN)
for t in TEXT:
    fn, sz, wt = t["pil"]
    d.text(t["at"], t["text"], font=font(fn, sz, wt), fill=t["color"], anchor=t.get("anchor", "la"))
out = os.path.join(HERE, "open-house-oct16-1080x1350.png")
canvas.convert("RGB").save(out, optimize=True)

# ---------- layers + layout for the PowerPoint ----------
os.makedirs(LAYERS_DIR, exist_ok=True)
for f in os.listdir(LAYERS_DIR):
    os.remove(os.path.join(LAYERS_DIR, f))
layout = {"w": W, "h": H, "background": hexc(CREAM), "items": []}
for i, (name, im) in enumerate(LAYERS):
    bb = im.getbbox()
    fn = "%02d-%s.png" % (i + 1, name)
    im.crop(bb).save(os.path.join(LAYERS_DIR, fn), optimize=True)
    layout["items"].append({"type": "image", "name": name, "file": "layers/" + fn,
                            "x": bb[0], "y": bb[1], "w": bb[2] - bb[0], "h": bb[3] - bb[1]})
layout["items"].append({"type": "pill", "name": "date-pill", **{k: PILL[k] for k in "xywh"},
                        "color": hexc(PILL["color"])})
for t in TEXT:
    layout["items"].append({"type": "text", **{k: t[k] for k in ("name", "text", "x", "y", "w", "h", "font", "size", "align")},
                            "bold": t.get("bold", False), "italic": t.get("italic", False),
                            "valign": t.get("valign", "top"), "color": hexc(t["color"])})
json.dump(layout, open(os.path.join(HERE, "layout.json"), "w"), indent=1)
print(out)
