"""World Earthworm Day (Wednesday 21 October 2026): one Instagram image, 1080 x 1350.
Sunny sky, plants at the surface, a real soil cross-section with vertical earthworm burrows and roots following them.
  python3 social/earthworm-day-2026-10-21/build.py -> post/ (post.png, layers, editable pptx)
"""
import os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "social", "regenerative-2026-10-15"))
from concepts import Single, grain, cover
from sunny import sunlight
from variants import W, H, DEEP, GREEN, CREAM, rgb, cut, NEW, FLOW, logo_img

SOILC = os.path.join(ROOT, "social", "cutouts-soil")
CLOVER = os.path.join(ROOT, "social", "open-house-2026-10-16", "cutouts", "crimson-clover-capri.webp")
SURFACE = 780          # where the ground starts
M = 90


class Post(Single):
    def __init__(self):
        super().__init__("w"); self.dir = os.path.join(HERE, "post")
        self.lay = os.path.join(self.dir, "layers"); os.makedirs(self.lay, exist_ok=True)
        for f in os.listdir(self.lay): os.remove(os.path.join(self.lay, f))

    def write(self):
        super().write()
        os.replace(os.path.join(self.dir, "regenerative-concept-w-canva.pptx"), os.path.join(HERE, "earthworm-day-editable.pptx"))
        os.replace(os.path.join(self.dir, "post.png"), os.path.join(HERE, "earthworm-day-1080x1350.png"))


def wiggle(x0, y0, length, seed, amp=14):
    rnd = random.Random(seed); pts = []; x = x0; ph = rnd.uniform(0, 6)
    for i in range(0, length, 8):
        x = x0 + math.sin(i / 70 + ph) * amp + rnd.uniform(-1.5, 1.5); pts.append((x, y0 + i))
    return pts


def soil_section():
    """The ground: real compost texture, darker with depth, with three vertical burrows lined with lighter casts."""
    h = H - SURFACE
    # an even field of soil: the lower, sharp part of the finished-compost pile in R5A_4027 (no fork in this part)
    src = Image.open(os.path.join(NEW, "R5A_4027.jpg")).convert("RGB").crop((60, 500, 1499, 1000))
    soil = cover(src, W, h, .5, .5)
    a = np.asarray(soil, np.float32)
    depth = np.linspace(0, 1, h)[:, None, None]
    a = a * (1.0 - depth * .35)                                             # darker with depth
    a = a * .9 + np.array([92, 62, 44], np.float32) * .1
    soil = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    # ragged top edge where the surface is
    rnd = random.Random(4); top = Image.new("L", (W, h), 255); d = ImageDraw.Draw(top)
    poly = [(0, 0)] + [(x, rnd.uniform(0, 14)) for x in range(0, W + 20, 20)] + [(W, 0)]
    d.polygon(poly, fill=0); soil.putalpha(top.filter(ImageFilter.GaussianBlur(1)))
    burrows = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    for k, (x0, length, wdt) in enumerate([(230, h - 20, 30), (560, h - 60, 34), (880, h - 10, 28)]):
        pts = wiggle(x0, 6, length, k + 1)
        lining = Image.new("RGBA", (W, h), (0, 0, 0, 0)); ld = ImageDraw.Draw(lining)
        ld.line(pts, fill=(166, 124, 88, 150), width=wdt + 18, joint="curve")    # cast lining, a lighter rim
        ld.line(pts, fill=(34, 22, 16, 215), width=wdt, joint="curve")            # the open channel
        hi = Image.new("RGBA", (W, h), (0, 0, 0, 0)); ImageDraw.Draw(hi).line([(x - wdt // 2 - 4, y) for x, y in pts], fill=(214, 182, 140, 150), width=3)
        burrows.alpha_composite(lining.filter(ImageFilter.GaussianBlur(4))); burrows.alpha_composite(hi.filter(ImageFilter.GaussianBlur(1.2)))
    soil.alpha_composite(burrows)
    # fine roots following the burrows down
    roots = Image.new("RGBA", (W, h), (0, 0, 0, 0)); rd = ImageDraw.Draw(roots)
    for k, x0 in enumerate([230, 560, 880]):
        for j in range(3):
            pts = wiggle(x0 + (j - 1) * 26, 0, int((h - 80) * (.55 + j * .15)), 40 + k * 3 + j, amp=10)
            rd.line(pts, fill=(236, 222, 196, 210), width=3 - (j == 2), joint="curve")
            rnd = random.Random(k * 10 + j)
            for _ in range(6):                                                 # little side hairs
                px, py = pts[rnd.randrange(5, len(pts) - 1)]; s = rnd.choice([-1, 1])
                rd.line([(px, py), (px + s * rnd.randint(18, 40), py + rnd.randint(10, 30))], fill=(236, 222, 196, 170), width=2)
    soil.alpha_composite(roots.filter(ImageFilter.GaussianBlur(.6)))
    return soil


p = Post(); s = p.slide(CREAM); s["items"].clear()
# sunny sky
yy = np.linspace(0, 1, H)[:, None, None]
sky = np.array([255, 214, 140], np.float32) * (1 - yy) + np.array([255, 243, 216], np.float32) * yy
sky = np.repeat(sky, W, 1)
p.bg(s, grain(sunlight(Image.fromarray(sky.astype(np.uint8)), W - 180, 120, 460, .9), 4, 21))
p.img(s, "logo", logo_img(170), W - 72 - 170, 60)
p.text(s, "headline", [("How do worms work their magic?", DEEP, False)], M, 150, W - 2 * M - 80, 300, 84, lh=1.05)
p.text(s, "small-line", [("World Earthworm Day, 21 October", GREEN, False)], M + 2, 345, W - 2 * M, 60, 46, font="Source Sans 3", weight=600)
# the ground and life above it
p.img(s, "soil-cross-section", soil_section(), 0, SURFACE)
for k, (f, h_, cx, r) in enumerate([("clover", 150, 120, -4), ("clover", 120, 450, 5), ("clover", 160, 690, -3), ("clover", 130, 990, 6)]):
    im = cut(os.path.basename(CLOVER), h=h_, rot=r, folder=os.path.dirname(CLOVER))
    p.img(s, f"cover-crop-{k + 1}", im, round(cx - im.width / 2), SURFACE - im.height + 22)
for k, (f, h_, cx, r) in enumerate([("norfolk-common-poppy.png", 220, 300, -6), ("tamil-nadu-marigold.png", 190, 860, 5)]):
    im = cut(f, h=h_, rot=r, folder=FLOW); p.img(s, "flower-" + f[:-4], im, round(cx - im.width / 2), SURFACE - im.height + 20)
worm = cut("earthworm.png", h=250, folder=SOILC)
p.img(s, "earthworm", worm, 560 - worm.width // 2, SURFACE + 220)
p.write(); print("done")
