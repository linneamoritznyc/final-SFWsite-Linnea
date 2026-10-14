"""More sunny single-image designs for the Regenerative post, logo top right on each.
  python3 social/regenerative-2026-10-15/more.py -> more-a/ .. more-d/ and more-compare.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from concepts import Single, grain, cover
from sunny import sunlight
from variants import W, H, DEEP, GREEN, CREAM, rgb, cut, NEW, FLOW, HEAD, SMALL1, logo_img

HERE = os.path.dirname(os.path.abspath(__file__))
M = 90


class D(Single):
    def __init__(self, key):
        super().__init__(key); self.dir = os.path.join(HERE, f"more-{key}")
        self.lay = os.path.join(self.dir, "layers"); os.makedirs(self.lay, exist_ok=True)

    def write(self):
        super().write()
        os.replace(os.path.join(self.dir, f"regenerative-concept-{self.key}-canva.pptx"),
                   os.path.join(self.dir, f"regenerative-more-{self.key}-canva.pptx"))


def vgrad(stops):
    """Vertical gradient from (position, hex) stops."""
    y = np.linspace(0, 1, H)
    pos = [p for p, _ in stops]; cols = np.array([rgb(c) for _, c in stops], np.float32)
    g = np.stack([np.interp(y, pos, cols[:, k]) for k in range(3)], -1)
    return Image.fromarray(np.repeat(g[:, None, :], W, 1).astype(np.uint8))


def flower(f, h, rot=0): return cut(f, h=h, rot=rot, folder=FLOW)


# A. Poppy field full bleed, headline low in white over a soft dark fade, sun top left
d = D("a"); s = d.slide(CREAM)
ph = cover(Image.open(os.path.join(NEW, "ending-donate-poppy-field-wild-ken-hill.jpg")).convert("RGB"), W, H, .5, .25)
ph = np.asarray(sunlight(ph, 120, 60, 600, .8), np.float32)
fade = np.clip((np.arange(H) - 700) / 650, 0, 1)[:, None, None] * .6
ph = ph * (1 - fade) + np.array(rgb("#1B2C18"), np.float32) * fade
d.bg(s, Image.fromarray(ph.astype(np.uint8)))
d.img(s, "logo", logo_img(130, disc=True), W - 72 - 163, 56)
d.text(s, "headline", [(HEAD, "#FFFFFF", False)], M, 900, W - 2 * M, 300, 84, lh=1.05)
d.text(s, "small-line", [(SMALL1, "#FFE9B0", False)], M + 2, 1190, W - 2 * M, 60, 48, font="Source Sans 3", weight=600)
d.write()

# B. A big low sun behind the words, one tall flower rising into it
d = D("b"); s = d.slide(CREAM)
bg = vgrad([(0, "#FFF4DC"), (.55, "#FFD9A0"), (1, "#F6B26B")])
a = np.asarray(bg, np.float32); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
disc = np.clip((470 - np.hypot(xx - 540, yy - 560)) / 4, 0, 1)[..., None]
a = a * (1 - disc * .85) + np.array([255, 196, 92], np.float32) * disc * .85
d.bg(s, grain(sunlight(Image.fromarray(a.astype(np.uint8)), 540, 560, 700, .35), 4, 11))
d.img(s, "logo", logo_img(160), W - 72 - 160, 56)
d.text(s, "headline", [(HEAD, DEEP, False)], M, 330, W - 2 * M, 300, 92, lh=1.05)
d.text(s, "small-line", [(SMALL1, DEEP, False)], M + 2, 650, W - 2 * M, 60, 50, font="Source Sans 3", weight=600)
for f, h_, cx, r in [("costa-rica-heliconia.png", 700, 860, 4), ("norfolk-common-poppy.png", 520, 180, -6), ("tamil-nadu-marigold.png", 380, 400, 4)]:
    im = flower(f, h_, r); d.img(s, f[:-4], im, round(cx - im.width / 2), H - im.height + 40)
d.write()

# C. Flowers framing the page top and bottom, headline in the middle on warm cream
d = D("c"); s = d.slide(CREAM)
d.bg(s, grain(sunlight(vgrad([(0, "#FFF8EA"), (1, "#FCEFD2")]), 540, 675, 800, .3), 4, 12))
for f, h_, cx, r in [("santa-fe-indian-paintbrush.png", 360, 120, 180 - 12), ("tamil-nadu-jasmine.png", 260, 330, 175),
                     ("norfolk-cornflower.png", 340, 560, 185)]:
    im = flower(f, h_, r); d.img(s, "top-" + f[:-4], im, round(cx - im.width / 2), -40)
d.img(s, "logo", logo_img(160), W - 72 - 160, 56)
d.text(s, "headline", [(HEAD, DEEP, False)], M, 430, W - 2 * M, 300, 88, lh=1.05)
d.text(s, "small-line", [(SMALL1, GREEN, False)], M + 2, 740, W - 2 * M, 60, 48, font="Source Sans 3", weight=600)
for f, h_, cx, r in [("costa-rica-hibiscus.png", 300, 140, -8), ("santa-fe-chamisa.png", 380, 380, 0),
                     ("tamil-nadu-marigold.png", 330, 600, 6), ("norfolk-common-poppy.png", 420, 800, -4), ("costa-rica-torch-ginger.png", 420, 990, 6)]:
    im = flower(f, h_, r); d.img(s, "bottom-" + f[:-4], im, round(cx - im.width / 2), H - im.height + 40)
d.write()

# D. Deep green sky warming to a golden sunrise, meadow along the bottom
d = D("d"); s = d.slide(DEEP)
bg = vgrad([(0, "#1B2C18"), (.45, "#2F5A2A"), (.78, "#E9B85C"), (1, "#FFE3A3")])
d.bg(s, grain(sunlight(bg, 540, H - 250, 520, .55), 5, 13))
d.img(s, "logo", logo_img(120, disc=True), W - 72 - 150, 56)
d.text(s, "headline", [(HEAD, CREAM, False)], M, 230, W - 2 * M, 300, 92, lh=1.05)
d.text(s, "small-line", [(SMALL1, "#F3D27A", False)], M + 2, 550, W - 2 * M, 60, 50, font="Source Sans 3", weight=600)
for f, h_, cx, r in [("norfolk-common-poppy.png", 480, 100, -8), ("tamil-nadu-marigold.png", 360, 270, 5),
                     ("santa-fe-indian-paintbrush.png", 520, 440, -3), ("costa-rica-hibiscus.png", 280, 610, 6),
                     ("santa-fe-chamisa.png", 420, 760, -4), ("costa-rica-heliconia.png", 560, 920, 6), ("norfolk-cornflower.png", 420, 1050, 8)]:
    im = flower(f, h_, r); d.img(s, f[:-4], im, round(cx - im.width / 2), H - im.height + 30)
d.write()

tw_, th_, g_ = 400, 500, 26
cmp_ = Image.new("RGB", (g_ + 4 * (tw_ + g_), th_ + 80), (31, 31, 31)); dr = ImageDraw.Draw(cmp_)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
for i, (k, n) in enumerate([("a", "A  Poppy field"), ("b", "B  Low sun"), ("c", "C  Flower frame"), ("d", "D  Golden sunrise")]):
    x = g_ + i * (tw_ + g_); dr.text((x, 16), n, font=f, fill=(240, 240, 240))
    cmp_.paste(Image.open(os.path.join(HERE, f"more-{k}", "post.png")).convert("RGB").resize((tw_, th_), Image.LANCZOS), (x, 56))
cmp_.save(os.path.join(HERE, "more-compare.png")); print("done")
