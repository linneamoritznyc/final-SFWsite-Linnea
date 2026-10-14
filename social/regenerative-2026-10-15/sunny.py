"""'What does Regenerative actually mean?' as one sunny image: plants, life and sun. Three options.
  python3 social/regenerative-2026-10-15/sunny.py -> sunny-1/ .. sunny-3/ and sunny-compare.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from concepts import Single, grain, cover
from variants import W, H, DEEP, GREEN, CREAM, rgb, cut, NEW, FLOW, HEAD, SMALL1, logo_img

HERE = os.path.dirname(os.path.abspath(__file__))
WHITE = "#FFFFFF"


class S(Single):
    def __init__(self, key):
        super().__init__(key); self.dir = os.path.join(HERE, f"sunny-{key}")
        self.lay = os.path.join(self.dir, "layers"); os.makedirs(self.lay, exist_ok=True)

    def write(self):
        super().write()
        os.replace(os.path.join(self.dir, f"regenerative-concept-{self.key}-canva.pptx"),
                   os.path.join(self.dir, f"regenerative-sunny-{self.key}-canva.pptx"))


def sunlight(im, cx, cy, r, strength=.55):
    """Warm sunlight from one point: a soft golden glow added onto the picture."""
    a = np.asarray(im.convert("RGB"), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot(xx - cx, yy - cy) / r
    glow = np.exp(-d ** 2)[..., None] * strength
    warm = np.array([255, 236, 190], np.float32)
    return Image.fromarray(np.clip(a + (warm - a) * glow, 0, 255).astype(np.uint8))


M = 90

# 1. Wild Ken Hill poppy field under a big blue sky, sun in the corner
d = S("1"); s = d.slide(CREAM)
ph = cover(Image.open(os.path.join(NEW, "ending-donate-poppy-field-wild-ken-hill.jpg")).convert("RGB"), W, H, .5, .2)
d.bg(s, sunlight(ph, W - 60, 40, 520, .75))
d.text(s, "headline", [(HEAD, WHITE, False)], M, 150, W - 2 * M, 300, 92, lh=1.05)
d.text(s, "small-line", [(SMALL1, WHITE, False)], M + 2, 470, W - 2 * M, 60, 50, font="Source Sans 3", weight=600)
d.write()

# 2. Capri cover crop between the vines on a clear sunny day
d = S("2"); s = d.slide(CREAM)
ph = cover(Image.open(os.path.join(NEW, "card-cover-crop-inter-row-capri.jpg")).convert("RGB"), W, H, .5, .35)
d.bg(s, sunlight(ph, 160, 60, 640, .9))
d.text(s, "headline", [(HEAD, DEEP, False)], M, 90, W - 2 * M, 280, 80, lh=1.05)
d.text(s, "small-line", [(SMALL1, DEEP, False)], M + 2, 365, W - 2 * M, 60, 46, font="Source Sans 3", weight=600)
d.write()

# 3. A warm morning sky and a meadow of flowers from our four workshop regions
d = S("3"); s = d.slide(CREAM)
yy = np.mgrid[0:H, 0:W][0].astype(np.float32)[..., None] / H
top, mid, low = np.array([255, 214, 140], np.float32), np.array([255, 236, 200], np.float32), np.array([250, 246, 232], np.float32)
sky = np.where(yy < .45, top * (1 - yy / .45) + mid * (yy / .45), mid * (1 - (yy - .45) / .55) + low * ((yy - .45) / .55))
d.bg(s, grain(sunlight(Image.fromarray(sky.astype(np.uint8)), W - 200, 160, 420, .9), 4, 7))
d.img(s, "logo", logo_img(180), W - 72 - 180, 64)
d.text(s, "headline", [(HEAD, DEEP, False)], M, 330, W - 2 * M, 300, 92, lh=1.05)
d.text(s, "small-line", [(SMALL1, GREEN, False)], M + 2, 650, W - 2 * M, 60, 50, font="Source Sans 3", weight=600)
meadow = [("cornflower", "norfolk-common-poppy.png", 520, 90, -8), ("marigold", "tamil-nadu-marigold.png", 380, 250, 5),
          ("paintbrush", "santa-fe-indian-paintbrush.png", 560, 400, -3), ("hibiscus", "costa-rica-hibiscus.png", 300, 560, 6),
          ("chamisa", "santa-fe-chamisa.png", 440, 700, -4), ("heliconia", "costa-rica-heliconia.png", 600, 860, 6),
          ("cornflower-2", "norfolk-cornflower.png", 460, 1000, 8)]
for nm, f, h_, cx, r in meadow:
    im = cut(f, h=h_, rot=r, folder=FLOW)
    d.img(s, "flower-" + nm, im, round(cx - im.width / 2), H - im.height + 30)
d.write()

tw_, th_, g_ = 480, 600, 30
cmp_ = Image.new("RGB", (g_ + 3 * (tw_ + g_), th_ + 90), (31, 31, 31)); dr = ImageDraw.Draw(cmp_)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
for i, (k, n) in enumerate([("1", "Poppy field, Wild Ken Hill"), ("2", "Cover crops, Capri"), ("3", "Morning sun, flowers")]):
    x = g_ + i * (tw_ + g_); dr.text((x, 18), n, font=f, fill=(240, 240, 240))
    cmp_.paste(Image.open(os.path.join(HERE, f"sunny-{k}", "post.png")).convert("RGB").resize((tw_, th_), Image.LANCZOS), (x, 60))
cmp_.save(os.path.join(HERE, "sunny-compare.png")); print("done")
