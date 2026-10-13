"""Build the blank house used as the nano-banana input: the house from main's layers with an
empty logo plaque, plain window glass, a dark doorway and a blank OPEN board.
The logo and photos go back on top afterwards (compose_house.py), so they are never redrawn.
Coordinates are the post's (1080 x 1350); the house crop is x 250..830, y 500..1120."""
import os
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
LY = os.path.join(HERE, "layers-from-main")
W, H = 1080, 1350
CROP = (250, 500, 830, 1120)
SOIL, CREAM = (79, 52, 51), (244, 241, 234)

def shadow_of(im, strength=0.35, blur=6):
    sh = Image.new("RGBA", im.size, (40, 30, 20, 0))
    sh.putalpha(im.split()[3].point(lambda v: int(v * strength)).filter(ImageFilter.GaussianBlur(blur)))
    return sh

def place(canvas, file, x, y, shadow=False):
    im = Image.open(os.path.join(LY, file)).convert("RGBA")
    canvas.alpha_composite(im, (x, y))

c = Image.new("RGBA", (W, H), CREAM + (255,))
place(c, "03-house.png", 275, 523)

# empty plaque: ring and cream face, no logo
pd = 172
pl = Image.new("RGBA", (pd, pd), (0, 0, 0, 0))
d = ImageDraw.Draw(pl)
d.ellipse((0, 0, pd - 1, pd - 1), fill=SOIL + (255,))
d.ellipse((7, 7, pd - 8, pd - 8), fill=CREAM + (255,))
c.alpha_composite(shadow_of(pl), (540 - pd // 2 + 6, 650 - pd // 2 + 9))
c.alpha_composite(pl, (540 - pd // 2, 650 - pd // 2))

# windows: ring with plain pale glass
for x, y in ((365, 770), (625, 760)):
    w = Image.new("RGBA", (114, 114), (0, 0, 0, 0))
    d = ImageDraw.Draw(w)
    d.ellipse((0, 0, 113, 113), fill=SOIL + (255,))
    d.ellipse((9, 9, 104, 104), fill=(226, 232, 214, 255))
    c.alpha_composite(shadow_of(w), (x + 6, y + 9))
    c.alpha_composite(w, (x, y))

# doorway: flat warm dark interior where the photo goes
d = ImageDraw.Draw(c)
d.rectangle((478, 862, 599, 1092), fill=(58, 42, 34, 255))
place(c, "06-door-open.png", 456, 854)
place(c, "09-open-sign.png", 492, 806)   # board only; the word OPEN is a text box in the PPTX

c.convert("RGB").crop(CROP).save(os.path.join(HERE, "house-blank-reference.png"))
print("saved house-blank-reference.png")
