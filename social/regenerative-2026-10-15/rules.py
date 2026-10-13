"""Two Regenerative concepts redone to the Instagram text-post rules: one idea, one size jump,
text on a clean area, one visual hook, generous margins, no logo on the image (the handle is on the post).

  python3 social/regenerative-2026-10-15/rules.py -> rules-1/ and rules-3/ and rules-compare.png (before above, after below)
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import concepts as c
from concepts import Single, grain, cover, radial, MONT, SOIL
from variants import W, H, DEEP, GREEN, LIGHT, CREAM, rgb, NEW, HEAD, SMALL1

HERE = os.path.dirname(os.path.abspath(__file__))


class R(Single):
    def __init__(self, key):
        super().__init__(key); self.dir = os.path.join(HERE, f"rules-{key}")
        self.lay = os.path.join(self.dir, "layers"); os.makedirs(self.lay, exist_ok=True)

    def write(self):
        super().write()
        old = os.path.join(self.dir, f"regenerative-concept-{self.key}-canva.pptx")
        os.replace(old, os.path.join(self.dir, f"regenerative-rules-{self.key}-canva.pptx"))


M = 96  # margin: keeps type inside the grid crop on every side

# 1. Cracked to alive, top 60%; the type sits on clean deep green below it
d = R("1"); s = d.slide(DEEP)
top = 800
dry = cover(Image.open(os.path.join(HERE, "textures", "dry-cracked-earth.png")).convert("RGB"), W, top, .5, .3)
alive = cover(Image.open(os.path.join(NEW, "R5A_4007.jpg")).convert("RGB"), W, top, .5, .6)
yy = np.mgrid[0:top, 0:W][0].astype(np.float32) / top
noise = np.array(Image.fromarray((np.random.default_rng(3).random((top // 24, W // 24)) * 255).astype(np.uint8)).resize((W, top), Image.BICUBIC), np.float32) / 255
m = np.clip((yy - 0.42 + (noise - .5) * .18) / 0.18, 0, 1)
pic = Image.composite(alive, dry, Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)))
canvas = np.zeros((H, W, 3), np.float32); canvas[:] = rgb("#1B2C18")
canvas[:top] = np.asarray(pic, np.float32)
fade = np.clip((np.arange(H) - (top - 260)) / 260, 0, 1)[:, None, None]      # photo melts into the green
g = np.array(rgb("#1B2C18"), np.float32)
canvas = canvas * (1 - fade) + g * fade
d.bg(s, grain(Image.fromarray(canvas.astype(np.uint8)), 6, 1))
d.text(s, "headline", [(HEAD, CREAM, False)], M, 830, W - 2 * M, 300, 84, lh=1.05)
d.text(s, "small-line", [(SMALL1, LIGHT, False)], M + 2, 1120, W - 2 * M, 60, 46, font="Source Sans 3", weight=600)
d.write()

# 3. Soil in the letters: one huge heavy word cut from dark compost; the small lines stay small
d = R("3"); s = d.slide(CREAM)
d.bg(s, grain(radial("#F7F3EA", "#E2D6BE", .5, .5, 1.0), 6, 4))
font = ImageFont.truetype(MONT, 200); font.set_variation_by_axes([900])
word = "Regenerative"; bb = font.getbbox(word)
font = ImageFont.truetype(MONT, int(200 * (W - 2 * 60) / (bb[2] - bb[0]))); font.set_variation_by_axes([900])
bb = font.getbbox(word); tw, th = bb[2] - bb[0], bb[3] - bb[1]
tm = Image.new("L", (tw + 8, th + 8), 0); ImageDraw.Draw(tm).text((4 - bb[0], 4 - bb[1]), word, font=font, fill=255)
soil = cover(Image.open(os.path.join(NEW, "R5A_4007.jpg")).convert("RGB"), tm.width, tm.height, .45, .55)
soil = Image.eval(soil, lambda v: int(v * .78))                                # darker so it reads on cream
wimg = soil.convert("RGBA"); wimg.putalpha(tm)
d.text(s, "what-does", [("What does", SOIL, False)], 62, 470, W - 124, 80, 64, lh=1.0)
d.img(s, "word-regenerative-soil", wimg, 540, 640, center=True)
d.text(s, "actually-mean", [("actually mean?", SOIL, False)], 62, 735, W - 124, 80, 64, lh=1.0)
d.text(s, "small-line", [(SMALL1, GREEN, False)], 64, 860, W - 124, 60, 46, font="Source Sans 3", weight=600)
d.write()

# before (concept-N) above, after (rules-N) below
tw_, th_, g_ = 400, 500, 28
cmp_ = Image.new("RGB", (g_ + 2 * (tw_ + g_), 2 * (th_ + 70) + 20), (31, 31, 31)); dr = ImageDraw.Draw(cmp_)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
for row, (pre, lab) in enumerate([("concept", "Before"), ("rules", "After: Instagram text-post rules")]):
    y = 14 + row * (th_ + 70); dr.text((g_, y), lab, font=f, fill=(240, 240, 240))
    for i, k in enumerate(("1", "3")):  # the microscope concept is out: it does not belong in this post
        cmp_.paste(Image.open(os.path.join(HERE, f"{pre}-{k}", "post.png")).convert("RGB").resize((tw_, th_), Image.LANCZOS), (g_ + i * (tw_ + g_), y + 40))
cmp_.save(os.path.join(HERE, "rules-compare.png")); print("done")
