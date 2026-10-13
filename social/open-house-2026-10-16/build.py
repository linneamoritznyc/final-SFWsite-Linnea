"""Open House post, Soil Food Web Foundation one-year anniversary (Fri Oct 16, 2026).
Cut-paper house with an open door in the centre, cut-outs of SFW people and flowers around it.
Run from the repo root:  python3 social/open-house-2026-10-16/build.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
IMG = os.path.join(ROOT, "img", "new-2026-10")
CUT = os.path.join(HERE, "cutouts")
FONT = os.path.join(HERE, "fonts")
W, H = 1080, 1350

CREAM = (244, 241, 234)
DEEP = (34, 55, 31)
GREEN = (21, 104, 38)
LIGHTG = (89, 166, 108)
SOIL = (79, 52, 51)
TAN = (200, 155, 123)
PALE = (221, 232, 211)


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
    a = np.array(im.split()[3])
    m = a > thr
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        big = sizes.max()
        m = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= big * keep])
    m = ndimage.binary_fill_holes(m) if False else m
    al = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8))
    im.putalpha(al)
    bb = im.getbbox()
    return im.crop(bb)


def fit_h(im, h):
    return im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)


def fit_w(im, w):
    return im.resize((w, max(1, int(im.height * w / im.width))), Image.LANCZOS)


def paste(canvas, im, x, y, shadow=True, angle=0):
    """Paste a cut-out with a paper drop shadow. (x, y) = top-left."""
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    if shadow:
        a = im.split()[3]
        sh = Image.new("RGBA", im.size, (40, 30, 20, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.35)).filter(ImageFilter.GaussianBlur(6)))
        canvas.alpha_composite(sh, (int(x) + 6, int(y) + 9))
    canvas.alpha_composite(im, (int(x), int(y)))


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


def shape(size, draw_fn):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(im))
    return im


canvas = Image.new("RGBA", (W, H), CREAM + (255,))
d = ImageDraw.Draw(canvas)

# ---------- big pale "microscope field" circle behind the house ----------
cx, cy, r = 540, 770, 375
d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PALE)
for k in range(60):  # eyepiece tick marks around it
    ang = np.deg2rad(k * 6)
    r1, r2 = r + 10, r + (26 if k % 5 == 0 else 18)
    d.line((cx + r1 * np.cos(ang), cy + r1 * np.sin(ang), cx + r2 * np.cos(ang), cy + r2 * np.sin(ang)),
           fill=LIGHTG, width=3 if k % 5 == 0 else 2)

# ---------- ground: real compost photo, wavy top edge ----------
GY = 1075
tex = Image.open(os.path.join(IMG, "R5A_4007.jpg")).convert("RGB")
tex = tex.crop((0, 0, int(tex.width * 0.42), int(tex.height * 0.55)))
tex = tex.resize((W, H - GY + 60), Image.LANCZOS)
tex = Image.eval(tex, lambda v: int(v * 0.82))
gm = Image.new("L", (W, H - GY + 60), 0)
gd = ImageDraw.Draw(gm)
pts = [(x, 30 + 16 * np.sin(x / 95.0) + 9 * np.sin(x / 37.0)) for x in range(0, W + 10, 10)]
gd.polygon(pts + [(W, H), (0, H)], fill=255)
ground = tex.convert("RGBA")
ground.putalpha(gm)
canvas.alpha_composite(ground, (0, GY - 30))

# ---------- the house (cut paper) ----------
hx0, hx1, wall_top, wall_bot = 330, 750, 735, GY + 18
roof_apex = (540, 530)


def house_body(dr):
    dr.rectangle((hx0 - 30, wall_top - 30, hx1 - 30, wall_bot - 30), fill=TAN)


body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
bd.rectangle((hx0, wall_top, hx1, wall_bot), fill=(232, 214, 190))
# board lines on the wall
for yy in range(wall_top + 26, wall_bot, 26):
    bd.line((hx0, yy, hx1, yy), fill=(214, 192, 164), width=2)
# chimney
bd.rectangle((655, 545, 705, 660), fill=SOIL)
bd.rectangle((645, 535, 715, 555), fill=(60, 38, 37))
# roof
bd.polygon([(hx0 - 45, wall_top + 8), roof_apex, (hx1 + 45, wall_top + 8)], fill=GREEN)
bd.polygon([(hx0 - 45, wall_top + 8), roof_apex, (540, wall_top + 8)], fill=(18, 88, 33))
bd.line([(hx0 - 45, wall_top + 8), (hx1 + 45, wall_top + 8)], fill=DEEP, width=8)
# shadow under body
a = body.split()[3]
sh = Image.new("RGBA", body.size, (40, 30, 20, 0))
sh.putalpha(a.point(lambda v: int(v * 0.3)).filter(ImageFilter.GaussianBlur(10)))
canvas.alpha_composite(sh, (10, 12))
canvas.alpha_composite(body)

# doorway: real workshop photo inside, warm light
dx0, dx1, dy0, dy1 = 478, 600, 862, wall_bot
inside = Image.open(os.path.join(IMG, "community-laughing-at-microscope.jpg")).convert("RGB")
iw, ih = inside.size
inside = inside.crop((int(iw * 0.12), int(ih * 0.08), int(iw * 0.62), int(ih * 0.98)))
ratio = (dx1 - dx0) / (dy1 - dy0)
cw = inside.width
chh = int(cw / ratio)
if chh > inside.height:
    chh = inside.height
    cw = int(chh * ratio)
inside = inside.crop((0, 0, cw, chh)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS)
glow = Image.new("RGB", inside.size, (255, 214, 150))
inside = Image.blend(inside, glow, 0.12)
canvas.paste(inside, (dx0, dy0))
d = ImageDraw.Draw(canvas)
d.rectangle((dx0 - 8, dy0 - 8, dx1 + 8, dy0), fill=SOIL)
d.rectangle((dx0 - 8, dy0 - 8, dx0, dy1), fill=SOIL)
d.rectangle((dx1, dy0 - 8, dx1 + 8, dy1), fill=SOIL)

# the door, swung open outwards to the right
door = [(dx1 + 8, dy0 - 4), (dx1 + 88, dy0 + 26), (dx1 + 88, dy1 - 4), (dx1 + 8, dy1)]
ds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(ds).polygon([(x + 8, y + 10) for x, y in door], fill=(40, 30, 20, 90))
canvas.alpha_composite(ds.filter(ImageFilter.GaussianBlur(6)))
d = ImageDraw.Draw(canvas)
d.polygon(door, fill=DEEP)
d.polygon([(dx1 + 22, dy0 + 18), (dx1 + 74, dy0 + 38), (dx1 + 74, dy0 + 100), (dx1 + 22, dy0 + 88)], fill=GREEN)
d.polygon([(dx1 + 22, dy0 + 112), (dx1 + 74, dy0 + 124), (dx1 + 74, dy1 - 24), (dx1 + 22, dy1 - 18)], fill=GREEN)
d.ellipse((dx1 + 70, dy0 + 112, dx1 + 82, dy0 + 124), fill=CREAM)

# step
d.rectangle((dx0 - 22, dy1 - 2, dx1 + 22, dy1 + 14), fill=(120, 96, 80))

# round windows: student micrographs
w1 = disc(os.path.join(IMG, "Bacterial-feeding nematode, 40x obj, Sid Jensen (I3).jpg"), 96, ring=9)
w2 = disc(os.path.join(IMG, "Testate amoeba (Arcella), 40x obj, Mark Horton.jpg"), 96, ring=9)
paste(canvas, w1, 365, 770)
paste(canvas, w2, 625, 760)

# OPEN sign hanging over the door
d = ImageDraw.Draw(canvas)
d.line((515, 806, 525, 826), fill=SOIL, width=2)
d.line((563, 806, 553, 826), fill=SOIL, width=2)
d.rounded_rectangle((492, 822, 586, 852), radius=4, fill=CREAM, outline=SOIL, width=2)
fsign = font("montserrat-latin-variable.ttf", 17, 800)
d.text((539, 838), "OPEN", font=fsign, fill=GREEN, anchor="mm")

# ---------- cut-outs ----------
cut = lambda n, **k: clean(os.path.join(CUT, n), **k)

# flowers growing up from the ground around the house
poppy = fit_h(cut("raw-poppies.png", thr=170, keep=0.02), 230)
paste(canvas, poppy, 250, GY - 215)
kneel = fit_h(cut("raw-kneeling-field.png", thr=170), 215)
paste(canvas, kneel, 175, GY - 150)
passion = fit_w(cut("raw-passion-flower.png", box=(0, 0, 1, 0.72)), 230)
paste(canvas, passion, 790, 470, angle=-12)
orchid = fit_w(Image.open(os.path.join(CUT, "orchid-costa-rica.webp")).convert("RGBA"), 200)
paste(canvas, orchid, 120, 520, angle=8)
clover = fit_h(Image.open(os.path.join(CUT, "crimson-clover-capri.webp")).convert("RGBA"), 190)
paste(canvas, clover, 770, GY - 150, angle=-6)
paste(canvas, fit_h(clover, 150), 300, GY - 115, angle=10)

# people
mist = fit_h(cut("raw-misting-man.png", box=(0, 0, 0.6, 1)), 400)
paste(canvas, mist, 18, GY - 300)
smell = fit_h(cut("raw-smelling-compost.png"), 390)
paste(canvas, smell, W - smell.width + 40, GY - 280)
fork = fit_h(cut("raw-woman-manure-fork.png", thr=170), 290)
paste(canvas, fork, -30, H - fork.height + 4)
crouch = fit_h(cut("raw-crouching-garden.png", thr=170), 300)
paste(canvas, crouch, W - crouch.width + 20, H - crouch.height + 4)

# hats on the doorstep, thermometer in the ground
hats = fit_w(cut("raw-hats.png"), 210)
paste(canvas, hats, 420, H - 210)
thermo = fit_w(Image.open(os.path.join(CUT, "compost-thermometer.webp")).convert("RGBA"), 120)
paste(canvas, thermo, 640, H - 170, angle=-15)

# ---------- type ----------
d = ImageDraw.Draw(canvas)
small = font("montserrat-latin-variable.ttf", 21, 700)
d.text((70, 62), "SOIL FOOD WEB FOUNDATION", font=small, fill=DEEP)
d.text((W - 70, 62), "TURNING ONE", font=small, fill=DEEP, anchor="ra")
d.line((70, 100, W - 70, 100), fill=(190, 200, 180), width=2)

big = font("eb-garamond-latin-500-italic.ttf", 168)
d.text((64, 108), "Open House", font=big, fill=DEEP)

sub = font("eb-garamond-latin-400-normal.ttf", 38)
d.text((72, 316), "Come celebrate our first year", font=sub, fill=SOIL)
date = font("montserrat-latin-variable.ttf", 26, 700)
pill_w = int(d.textlength("FRIDAY, OCTOBER 16", font=date)) + 44
d.rounded_rectangle((72, 380, 72 + pill_w, 428), radius=24, fill=GREEN)
d.text((72 + pill_w // 2, 404), "FRIDAY, OCTOBER 16", font=date, fill=CREAM, anchor="mm")

out = os.path.join(HERE, "open-house-oct16-1080x1350.png")
canvas.convert("RGB").save(out, optimize=True)
print(out)
