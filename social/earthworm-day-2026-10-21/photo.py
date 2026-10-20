"""World Earthworm Day, one image: the hand-with-earthworm photo full bleed, headline on the dark soil.
Photo: img/hand-wet-dirt-worm.jpg (Canva licence, already on the site). Not one of SFW's own workshop photos.
  python3 social/earthworm-day-2026-10-21/photo.py -> earthworm-day-photo-1080x1350.png + earthworm-day-photo-editable.pptx
"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "social", "regenerative-2026-10-15"))
from concepts import Single, grain, cover
from variants import W, H, CREAM, rgb, logo_img


class Post(Single):
    def __init__(self):
        super().__init__("x"); self.dir = os.path.join(HERE, "photo")
        self.lay = os.path.join(self.dir, "layers"); os.makedirs(self.lay, exist_ok=True)
        for f in os.listdir(self.lay): os.remove(os.path.join(self.lay, f))

    def write(self):
        super().write()
        os.replace(os.path.join(self.dir, "regenerative-concept-x-canva.pptx"), os.path.join(HERE, "earthworm-day-photo-editable.pptx"))
        os.replace(os.path.join(self.dir, "post.png"), os.path.join(HERE, "earthworm-day-photo-1080x1350.png"))


p = Post(); s = p.slide(CREAM)
ph = cover(Image.open(os.path.join(ROOT, "img", "hand-wet-dirt-worm.jpg")).convert("RGB"), round(W * 1.1), round(H * 1.1), .62, .5)
ph = ph.crop((60, 140, 60 + W, 140 + H))   # zoom a little and lift the hand away from the words
a = np.asarray(ph, np.float32)
shade = np.clip((np.linspace(0, 1, H) - .68) / .32, 0, 1)[:, None, None] * .5   # deepen the soil at the bottom so the words read
a = a * (1 - shade)
p.bg(s, grain(Image.fromarray(a.astype(np.uint8)), 3, 5))
p.img(s, "logo", logo_img(110, disc=True), W - 72 - 138, 64)
p.text(s, "headline", [("How do worms work their magic?", "#F4F1EA", False)], 84, 1010, 912, 200, 80, lh=1.04)
p.text(s, "small-line", [("World Earthworm Day, 21 October", "#E6C77A", False)], 88, 1200, 800, 60, 42, font="Source Sans 3", weight=600)
p.write(); print("done")
