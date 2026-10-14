"""Put the cover words and logo onto the painted backgrounds (raw-N.png). Words sit in the glowing arch.
  python3 social/turns-one-cover/painted-gen/compose.py -> option-1, option-3, option-4 (post.png, layers, pptx) + options.png
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cover as cv
from cover import Cover, W, H, HEAD, SUB

# raw file: (headline top, width/left of the arch interior)
LAYOUT = {"1": (330, 200, 740), "3": (250, 260, 820), "4": (220, 290, 790)}


class Opt(Cover):
    def __init__(self, key):
        self.key, self.dir = key, os.path.join(HERE, f"option-{key}")
        self.lay = os.path.join(self.dir, "layers"); os.makedirs(self.lay, exist_ok=True)
        for f in os.listdir(self.lay): os.remove(os.path.join(self.lay, f))
        self.items = []
        bg = Image.open(os.path.join(HERE, f"raw-{key}.png")).convert("RGB").resize((W, H), Image.LANCZOS)
        self._save("painting", bg, 0, 0, jpg=True)


for k, (top, x0, x1) in LAYOUT.items():
    o = Opt(k); w = x1 - x0
    o.logo((x0 + x1) // 2 - 50, top - 150, 100)
    o.text("headline", HEAD, x0, top, w, 260, 112, True, "#22371F", "center")
    o.text("small-line", SUB, x0, top + 250, w, 60, 32, False, "#4F3433", "center", 400)
    o.write()

tw, th, g = 480, 600, 30
cmp_ = Image.new("RGB", (g + 3 * (tw + g), th + 90), (31, 31, 31)); dr = ImageDraw.Draw(cmp_)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
for i, k in enumerate(LAYOUT):
    x = g + i * (tw + g); dr.text((x, 18), f"Option {k}", font=f, fill=(240, 240, 240))
    cmp_.paste(Image.open(os.path.join(HERE, f"option-{k}", "post.png")).convert("RGB").resize((tw, th), Image.LANCZOS), (x, 60))
cmp_.save(os.path.join(HERE, "options.png")); print("done")
