"""Soil Food Web Foundation turns one: 9-slide Instagram carousel, Friday 16 October 2026.

Words are exactly the slide words in the post doc. Photos are the 'Amazing Community Images' set
(all in the repo), the Isha/India workshop photos and the cutout kits in social/cutouts-*.

  python3 social/turns-one-2026-10-16/build.py
    -> layers/ (every photo, cutout and background as its own PNG)
    -> slides.html (the 9 slides), slide-1.png ... slide-9.png, contact-sheet.png
    -> turns-one-canva.pptx  (import into Canva: every picture and text box stays separate and editable)
"""
import os, math, random, json, subprocess, zipfile, io
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
NEW = os.path.join(ROOT, "img", "new-2026-10")
LAY = os.path.join(HERE, "layers")
os.makedirs(LAY, exist_ok=True)
W, H = 1080, 1350

DEEP, GREEN, CREAM, KRAFT, SOIL, GOLD, PURPLE = "#22371F", "#156826", "#F4F1EA", "#CDB38A", "#4F3433", "#C9A227", "#6B4C7A"


def P(*a): return os.path.join(ROOT, *a)
def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def india(name):
    z = zipfile.ZipFile(P("exports", "workshop-images", "accelerator-workshop-october-2026.zip"))
    n = [x for x in z.namelist() if x.endswith(name)][0]
    return Image.open(io.BytesIO(z.read(n))).convert("RGB")


def load(src):
    return src if isinstance(src, Image.Image) else Image.open(src).convert("RGB")


def cover(im, w, h, fx=0.5, fy=0.5):
    sw, sh = im.size
    s = max(w / sw, h / sh)
    im = im.resize((max(w, round(sw * s)), max(h, round(sh * s))), Image.LANCZOS)
    x = round((im.width - w) * fx); y = round((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def shadow(im, off=(8, 12), blur=10, alpha=0.38):
    a = im.getchannel("A")
    pad = blur * 3 + max(abs(off[0]), abs(off[1]))
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (30, 22, 15, 255)); sh.putalpha(a.point(lambda v: int(v * alpha)))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0)); s.alpha_composite(sh, (pad + off[0], pad + off[1]))
    out.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(im, (pad, pad))
    return out


def ragged(w, h, edges, seed, amp=10):
    """Mask with torn edges on the given sides ('t','b','l','r')."""
    rnd = random.Random(seed)
    def line(n):
        v, out = 0.0, []
        for _ in range(n):
            v = max(-1, min(1, v + rnd.uniform(-0.35, 0.35))); out.append(v * amp + rnd.uniform(-2, 2))
        return out
    m = Image.new("L", (w, h), 0)
    top = line(w) if "t" in edges else [0] * w
    bot = line(w) if "b" in edges else [0] * w
    lef = line(h) if "l" in edges else [0] * h
    rig = line(h) if "r" in edges else [0] * h
    a = np.zeros((h, w), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    t = np.array(top) + (amp + 2 if "t" in edges else 0)
    b = h - (np.array(bot) + (amp + 2 if "b" in edges else 0))
    l = np.array(lef) + (amp + 2 if "l" in edges else 0)
    r = w - (np.array(rig) + (amp + 2 if "r" in edges else 0))
    inside = (yy >= t[None, :]) & (yy <= b[None, :]) & (xx >= l[:, None]) & (xx <= r[:, None])
    a[inside] = 255
    return Image.fromarray(a).filter(ImageFilter.GaussianBlur(0.7))


def print_photo(src, w, h, fx=0.5, fy=0.5, border=14):
    im = cover(load(src), w, h, fx, fy)
    out = Image.new("RGBA", (w + 2 * border, h + 2 * border), hexrgb("#FBF8F1") + (255,))
    out.paste(im, (border, border))
    return out


def torn_photo(src, w, h, edges, fx=0.5, fy=0.5, seed=1, amp=14):
    im = cover(load(src), w, h, fx, fy).convert("RGBA")
    im.putalpha(ragged(w, h, edges, seed, amp))
    return im


def circle_photo(src, d, ring=10, fx=0.5, fy=0.5):
    im = cover(load(src), d, d, fx, fy).convert("RGBA")
    m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255); im.putalpha(m)
    out = Image.new("RGBA", (d + 2 * ring, d + 2 * ring), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, d + 2 * ring - 1, d + 2 * ring - 1), fill=hexrgb(CREAM) + (255,))
    out.alpha_composite(im, (ring, ring))
    return out


def cutout(path, w=None, h=None):
    im = Image.open(path).convert("RGBA")
    if w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    elif h: im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    return im


def paper(color, seed):
    rng = np.random.default_rng(seed)
    base = np.array(hexrgb(color), np.float32)[None, None, :]
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    n = np.array(Image.fromarray(((n - n.min()) / (np.ptp(n)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255 - 0.5
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)
    img = base + (n[..., None] * 16) + (fine[..., None] * 3.5)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


# ---------------- slide model ----------------
SLIDES = []


class Slide:
    def __init__(self, n, bg):
        self.n, self.items, self.z = n, [], 0
        SLIDES.append(self)
        self.layer("background", paper(bg, n), 0, 0, shadowed=False, anchor="tl")

    def layer(self, name, im, cx, cy, rot=0, shadowed=True, anchor="center"):
        """Place an RGBA picture. cx, cy is its centre (or top-left with anchor='tl')."""
        if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        pad = 0
        if shadowed:
            big = shadow(im); pad = (big.width - im.width) // 2; im = big
        if anchor == "tl": x, y = cx - pad, cy - pad
        else: x, y = round(cx - im.width / 2), round(cy - im.height / 2)
        # clip to the slide so Canva gets clean pieces
        box = (max(0, -x), max(0, -y), min(im.width, W - x), min(im.height, H - y))
        im = im.crop(box); x, y = x + box[0], y + box[1]
        self.z += 1
        if name == "background":  # opaque paper: JPEG keeps the PowerPoint small
            fn = f"s{self.n}-{self.z:02d}-{name}.jpg"; im.convert("RGB").save(os.path.join(LAY, fn), quality=88)
        else:
            fn = f"s{self.n}-{self.z:02d}-{name}.png"; im.save(os.path.join(LAY, fn), optimize=True)
        self.items.append(dict(type="image", name=name, file="layers/" + fn, x=x, y=y, w=im.width, h=im.height))

    def text(self, name, text, x, y, w, size, font="garamond", italic=True, weight=500, color=DEEP, align="left", lh=1.08, h=None):
        self.items.append(dict(type="text", name=name, text=text, x=x, y=y, w=w, h=h or round(size * lh * 3), size=size,
                               font=font, italic=italic, weight=weight, color=color, align=align, lh=lh))


C = P("social", "cutouts-flowers"); S = P("social", "cutouts-soil")
logo = Image.open(P("img", "sfwlogo-240.png")).convert("RGBA")


def logo_disc(d=130):
    out = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, d - 1, d - 1), fill=hexrgb(CREAM) + (255,))
    l = logo.resize((round(d * 0.78), round(d * 0.78 * logo.height / logo.width)), Image.LANCZOS)
    out.alpha_composite(l, ((d - l.width) // 2, (d - l.height) // 2))
    return out


# ---------- 1. Today we turn 1 ----------
s = Slide(1, DEEP)
s.layer("logo", logo_disc(), 960, 112)
s.text("headline", "Today we turn 1 🎂", 72, 120, 820, 132, color=CREAM, lh=1.0)
s.text("small", "One year as a 501(c)(3) nonprofit.", 76, 410, 800, 36, font="montserrat", italic=False, weight=600, color=CREAM)
# soil-layer cake on a cream plate
plate = Image.new("RGBA", (820, 120), (0, 0, 0, 0))
ImageDraw.Draw(plate).ellipse((0, 0, 819, 119), fill=hexrgb("#FBF8F1") + (255,))
s.layer("cake-plate", plate, 540, 1205)
tiers = [("cake-tier-compost", P("img", "new-2026-10", "R5A_4007.jpg"), 660, 170, 1110, 0.5),
         ("cake-tier-wood-chips", P("img", "new-2026-10", "santa-fe-2026-10-aged-wood-chips.jpg"), 540, 150, 950, 0.9),
         ("cake-tier-soil-roots", P("img", "new-2026-10", "card-roots-in-soil-capri.jpg"), 420, 140, 805, 0.5)]
for i, (nm, src, w, h, cy, fy) in enumerate(tiers):
    s.layer(nm, torn_photo(src, w, h, "tb", fy=fy, seed=10 + i, amp=9), 540, cy)
# candle and flame
cd = Image.new("RGBA", (60, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(cd)
d.rounded_rectangle((8, 50, 52, 189), radius=8, fill=hexrgb("#FBF8F1") + (255,))
for yy in range(62, 189, 26): d.polygon([(8, yy), (52, yy - 12), (52, yy - 2), (8, yy + 10)], fill=hexrgb(GOLD) + (255,))
fl = Image.new("RGBA", (60, 70), (0, 0, 0, 0)); fd = ImageDraw.Draw(fl)
fd.ellipse((14, 6, 46, 66), fill=(255, 196, 70, 255)); fd.ellipse((22, 26, 38, 64), fill=(255, 240, 190, 255))
glow = Image.new("RGBA", (60, 70), (255, 200, 80, 0)); gd = ImageDraw.Draw(glow); gd.ellipse((4, 0, 56, 70), fill=(255, 200, 80, 120))
cd.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)), (0, 0)); cd.alpha_composite(fl, (0, 0))
d.line((30, 50, 30, 62), fill=(60, 40, 30, 255), width=3)
s.layer("candle", cd, 540, 640, shadowed=False)
# seedling: the sprout from the generated seedling photo, soil and roots left out
sd = Image.open(P("social", "cutouts-soil", "_raw", "seedling-in-soil.png")).convert("RGB")
arr = np.array(sd).astype(int); g = (arr[..., 1] > arr[..., 0] + 15) & (arr[..., 1] > arr[..., 2] + 15)
rows = np.where(g.any(1))[0]; cols = np.where(g.any(0))[0]
top, bot = rows.min(), rows.min() + int((rows.max() - rows.min()) * 0.98)
sprout = sd.crop((cols.min() - 10, top - 10, cols.max() + 10, bot)).convert("RGBA")
sa = np.array(sprout); white = (sa[..., :3].min(2) > 225); sa[white, 3] = 0; sprout = Image.fromarray(sa)
sprout = sprout.resize((150, round(150 * sprout.height / sprout.width)), Image.LANCZOS)
s.layer("seedling", sprout, 640, 760 - sprout.height // 2 + 10, shadowed=False)
s.layer("flower-hibiscus", cutout(os.path.join(C, "costa-rica-hibiscus.png"), w=250), 190, 1040, rot=12)
s.layer("flower-marigold", cutout(os.path.join(C, "tamil-nadu-marigold.png"), h=300), 905, 1010, rot=-10)
s.layer("flower-poppy", cutout(os.path.join(C, "norfolk-common-poppy.png"), h=360), 120, 760, rot=-8)
s.layer("flower-paintbrush", cutout(os.path.join(C, "santa-fe-indian-paintbrush.png"), h=330), 975, 740, rot=8)
s.layer("flower-jasmine", cutout(os.path.join(C, "tamil-nadu-jasmine.png"), w=190), 870, 1240, rot=0)

# ---------- 2. Dr. Elaine Ingham ----------
s = Slide(2, CREAM)
s.layer("photo-elaine", torn_photo(P("img", "Dr Elaine Ingham with Microscope.jpg"), W, 760, "b", fy=0.25, seed=21, amp=16), 0, 0, shadowed=True, anchor="tl")
s.layer("photo-elaine-ceremony", print_photo(P("img", "new-2026-10", "elaine-ceremonial-compost-group-photo.jpg"), 330, 230), 860, 1150, rot=-4)
s.text("words", "A year ago, we became a nonprofit foundation to carry Dr. Elaine Ingham's work to everyone who wants to learn it.", 72, 830, 640, 50, color=PURPLE, lh=1.14, h=420)
s.layer("flower-foxglove", cutout(os.path.join(C, "norfolk-foxglove.png"), h=360), 960, 790, rot=10)
orch = P("social", "open-house-2026-10-16", "cutouts", "orchid-costa-rica.webp")
s.layer("flower-orchid", cutout(orch, w=230), 120, 760, rot=-14)

# ---------- 3. Scholarships ----------
s = Slide(3, KRAFT)
s.text("big", "More than $72,000", 64, 80, 960, 112, italic=False, weight=600, lh=1.0, h=130)
s.text("words", "in full scholarships in June alone, plus around $250,000 in partial scholarships.", 68, 225, 900, 48, lh=1.15, h=130)
s.layer("photo-certificates-stone-wall", print_photo(P("img", "new-2026-10", "community-certificate-stone-wall-jul-2024.jpg"), 470, 350, fy=0.3), 290, 600, rot=-4)
s.layer("photo-graduates-purple", print_photo(P("past-workshop-images", "accelerator-workshop-february-2026", "accelerator-workshop-february-2026-05-graduates-with-certificates.jpg"), 470, 330), 790, 640, rot=3)
s.layer("photo-certificates-terrace", print_photo(P("img", "new-2026-10", "community-certificate-terrace-jul-2024.jpg"), 420, 360, fy=0.4), 300, 1040, rot=3)
s.layer("photo-graduates-aug-2023", print_photo(P("img", "aug2023-workshop-group-7.jpg"), 500, 360, fy=0.55), 780, 1060, rot=-3)
s.layer("flower-gloriosa", cutout(os.path.join(C, "tamil-nadu-gloriosa-lily.png"), h=230), 560, 1250, rot=-70)

# ---------- 4. 35 live events ----------
s = Slide(4, DEEP)
s.text("big", "35", 64, 40, 420, 300, italic=False, weight=500, color=CREAM, lh=1.0, h=300)
s.text("words", "live events, with guests like Vandana Shiva, David Holmgren and Mary Cole.", 470, 120, 560, 50, color=CREAM, lh=1.14, h=260)
s.layer("photo-microscopy-group", print_photo(P("img", "new-2026-10", "community-beginner-microscopy-group.jpg"), 560, 400), 330, 640, rot=-3)
s.layer("photo-microscopy-costa-rica", print_photo(P("img", "new-2026-10", "costa-rica-2025-microscopy-students-mentors.jpg"), 470, 360), 790, 760, rot=4)
s.layer("photo-laughing-at-microscope", print_photo(P("img", "new-2026-10", "community-laughing-at-microscope.jpg"), 520, 370), 380, 1080, rot=2)
s.layer("flower-cornflower", cutout(os.path.join(C, "norfolk-cornflower.png"), h=330), 900, 1150, rot=-12)
s.layer("mushrooms", cutout(os.path.join(S, "mushrooms.png"), w=200), 990, 1250)

# ---------- 5. First course in Spanish ----------
s = Slide(5, CREAM)
s.text("big", "Our first course in Spanish.", 64, 80, 900, 118, italic=True, weight=500, color=GREEN, lh=1.0, h=260)
s.layer("photo-high-five", print_photo(P("img", "new-2026-10", "students-high-five-at-compost.jpg"), 560, 380, fy=0.35), 340, 520, rot=-3)
s.layer("photo-staff-and-mentors", print_photo(P("past-workshop-images", "accelerator-workshop-march-2025", "accelerator-workshop-march-2025-06-staff-and-mentors.jpg"), 480, 340), 790, 760, rot=4)
s.layer("photo-group-at-compost-pile", print_photo(P("img", "new-2026-10", "workshop-group-around-compost-pile.jpg"), 600, 420), 400, 1060, rot=-2)
s.layer("flower-heliconia", cutout(os.path.join(C, "costa-rica-heliconia.png"), h=420), 990, 470, rot=6)
s.layer("flower-torch-ginger", cutout(os.path.join(C, "costa-rica-torch-ginger.png"), h=320), 930, 1180, rot=-14)

# ---------- 6. First workshop in Asia ----------
s = Slide(6, DEEP)
s.text("big", "Our first workshop in Asia!", 64, 80, 860, 112, italic=True, weight=500, color=CREAM, lh=1.0, h=240)
s.text("words", "Hosted at the Save Soil Farm in Coimbatore India.", 68, 330, 760, 46, font="garamond", italic=True, color=CREAM, lh=1.15, h=120)
s.layer("photo-isha-adiyogi", print_photo(india("header-1.jpg"), 600, 480, fy=0.3), 380, 760, rot=-3)
s.layer("photo-india-meal", print_photo(india("header-3.jpg"), 400, 400), 800, 1050, rot=5)
s.layer("flower-lotus", cutout(os.path.join(C, "tamil-nadu-pink-lotus.png"), w=280), 180, 1150, rot=-8)
s.layer("flower-marigold", cutout(os.path.join(C, "tamil-nadu-marigold.png"), h=280), 950, 520, rot=10)
s.layer("flower-jasmine", cutout(os.path.join(C, "tamil-nadu-jasmine.png"), w=240), 540, 1230)

# ---------- 7. Courses and support ----------
s = Slide(7, KRAFT)
s.text("words", "Foundation courses that no longer expire, weekly office hours, and every support message answered within 48 hours.", 64, 80, 930, 62, color=DEEP, lh=1.1, h=300)
s.layer("photo-amaranth-kenya", print_photo(P("img", "new-2026-10", "community-amaranth-harvest-aberdares-kenya.jpg"), 440, 440, fy=0.3), 290, 640, rot=-4)
s.layer("photo-lined-tank", print_photo(P("img", "new-2026-10", "community-man-beside-lined-tank.jpg"), 440, 340), 790, 620, rot=3)
s.layer("photo-greenhouse-nairobi", print_photo(P("img", "new-2026-10", "community-greenhouse-training-nairobi.jpg"), 640, 380, fy=0.6), 560, 1060, rot=-2)
s.layer("earthworm", cutout(os.path.join(S, "earthworm.png"), h=230), 110, 1230, rot=-20)
s.layer("flower-globemallow", cutout(os.path.join(C, "santa-fe-globemallow.png"), h=320), 990, 1180, rot=8)

# ---------- 8. Compost Intensive Course ----------
s = Slide(8, CREAM)
s.text("words", "Launched our Compost Intensive Course, the first in a series of online group programs.", 64, 80, 920, 64, color=DEEP, lh=1.1, h=240)
s.layer("photo-cheering-compost-cage", print_photo(P("img", "new-2026-10", "community-cheering-compost-cage-jun-2026.jpg"), 420, 520, fy=0.4), 270, 640, rot=-4)
s.layer("photo-wild-ken-hill-pile", print_photo(P("img", "wild-ken-hill", "IMG_1495.jpg"), 400, 500, fy=0.55), 760, 600, rot=3)
s.layer("photo-four-men-plant-pile", print_photo(P("img", "new-2026-10", "community-four-men-plant-pile.jpg"), 470, 340), 300, 1100, rot=3)
s.layer("photo-grey-shirts", print_photo(P("img", "new-2026-10", "community-group-grey-shirts-jun-2025.jpg"), 470, 340), 790, 1060, rot=-3)
s.layer("compost-fungal-threads", cutout(os.path.join(S, "compost-white-fungal-threads.png"), w=230), 980, 1280)
s.layer("wood-chips", cutout(os.path.join(S, "wood-chips-pile.png"), w=260), 90, 1290)

# ---------- 9. Thank you ----------
s = Slide(9, DEEP)
s.layer("photo-poppy-field-group", torn_photo(P("img", "new-2026-10", "building-community-poppy-field-group.jpg"), W, 800, "b", fy=0.55, seed=91, amp=16), 0, 0, anchor="tl")
s.text("words", "Thank you for growing with us. Here's to year two. 💚", 64, 860, 620, 72, color=CREAM, lh=1.08, h=330)
s.layer("photo-cyprus-group", print_photo(P("img", "new-2026-10", "community-group-cyprus-jan-2025.jpg"), 300, 210), 880, 1000, rot=4)
s.layer("photo-field-walk-norfolk", print_photo(P("img", "new-2026-10", "community-field-walk-norfolk-jun-2025.jpg"), 300, 210), 860, 1215, rot=-3)
s.layer("logo", logo_disc(120), 120, 1250)
s.layer("flower-poppy", cutout(os.path.join(C, "norfolk-common-poppy.png"), h=300), 1010, 770, rot=12)
s.layer("flower-hibiscus", cutout(os.path.join(C, "costa-rica-hibiscus.png"), w=170), 640, 1260, rot=-10)

# ---------------- outputs ----------------
json.dump([dict(n=s.n, items=s.items) for s in SLIDES], open(os.path.join(HERE, "layout.json"), "w"), indent=1)

FONTS = {"garamond": '"EB Garamond", Georgia, serif', "montserrat": '"Montserrat", Arial, sans-serif'}
css = """
@font-face{font-family:"EB Garamond";src:url("../../fonts/eb-garamond-latin-500-italic.woff2");font-weight:500;font-style:italic}
@font-face{font-family:"EB Garamond";src:url("../../fonts/eb-garamond-latin-500-normal.woff2");font-weight:500;font-style:normal}
@font-face{font-family:"EB Garamond";src:url("../../fonts/eb-garamond-latin-600-normal.woff2");font-weight:600;font-style:normal}
@font-face{font-family:"Montserrat";src:url("../../fonts/montserrat-latin-variable.woff2");font-weight:100 900}
*{margin:0;box-sizing:border-box} body{background:#555;display:grid;gap:40px;padding:40px;justify-content:center}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden}
.slide img{position:absolute;display:block}
.slide p{position:absolute;white-space:pre-wrap}
.e{font-family:"Noto Color Emoji";font-style:normal}
"""
html = ["<!doctype html><html><head><meta charset='utf-8'><title>SFW turns one</title><style>", css, "</style></head><body>"]
import re
for s in SLIDES:
    html.append(f"<section class='slide' id='slide-{s.n}'>")
    for it in s.items:
        if it["type"] == "image":
            html.append(f"<img src='{it['file']}' style='left:{it['x']}px;top:{it['y']}px;width:{it['w']}px;height:{it['h']}px' alt=''>")
    for it in s.items:
        if it["type"] == "text":
            t = re.sub("([\U0001F300-\U0001FAFF])", r"<span class='e'>\1</span>", it["text"])
            html.append(f"<p style='left:{it['x']}px;top:{it['y']}px;width:{it['w']}px;font-family:{FONTS[it['font']]};"
                        f"font-size:{it['size']}px;line-height:{it['lh']};font-weight:{it['weight']};"
                        f"font-style:{'italic' if it['italic'] else 'normal'};color:{it['color']};text-align:{it['align']}'>{t}</p>")
    html.append("</section>")
html.append("</body></html>")
open(os.path.join(HERE, "slides.html"), "w").write("\n".join(html))

subprocess.run(["node", os.path.join(HERE, "render.cjs")], check=True)

# editable PowerPoint for Canva
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
EMU = 914400 / 108
prs = Presentation(); prs.slide_width = Emu(round(W * EMU)); prs.slide_height = Emu(round(H * EMU))
for s in SLIDES:
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    for it in s.items:
        if it["type"] == "image":
            pic = sl.shapes.add_picture(os.path.join(HERE, it["file"]), Emu(round(it["x"] * EMU)), Emu(round(it["y"] * EMU)),
                                        Emu(round(it["w"] * EMU)), Emu(round(it["h"] * EMU)))
            pic.name = it["name"]
    for it in s.items:
        if it["type"] != "text": continue
        tb = sl.shapes.add_textbox(Emu(round(it["x"] * EMU)), Emu(round(it["y"] * EMU)), Emu(round(it["w"] * EMU)), Emu(round(it["h"] * EMU)))
        tb.name = it["name"]; tf = tb.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]; p.line_spacing = it["lh"]
        r = p.add_run(); r.text = it["text"]; f = r.font
        f.name = "EB Garamond" if it["font"] == "garamond" else "Montserrat"
        f.size = Pt(round(it["size"] * 72 / 108, 1)); f.italic = it["italic"]; f.bold = it["weight"] >= 600
        f.color.rgb = RGBColor(*hexrgb(it["color"]))
prs.save(os.path.join(HERE, "turns-one-canva.pptx"))
print("done:", len(SLIDES), "slides")
