"""Crop the chosen workshop photos to 4:5 at 1080 x 1350.

Run from the repo root: python3 social/tools/crop.py
The crop box is always 4:5 in the source, so nothing is stretched.
Sources under 1080 px wide are refused.
"""
from PIL import Image

W, H = 1080, 1350
# name: (source, horizontal anchor 0..1, vertical anchor 0..1)
PHOTOS = {
    "microscope": ("img/costa-rica-2025-microscopy-students-mentors.jpg", 0.0, 0.5),
    "compost-pile": ("img/pile-turning-wes-8-scaled.jpg", 0.5, 0.5),
    "group": ("img/wild-ken-hill/IMG_1500.jpg", 0.5, 0.75),
    "living-soil": ("img/ctpfw-student-squeezing-compost-1.jpg", 0.5, 0.5),
    "field": ("img/uploads/loida-teaching-3.jpg", 0.22, 0.5),
}

for name, (src, ax, ay) in PHOTOS.items():
    im = Image.open(src).convert("RGB")
    sw, sh = im.size
    if sw < 1080:
        raise SystemExit(f"{src} is {sw} px wide, under 1080: skipped")
    if sw / sh > W / H:  # wider than 4:5: full height, cut the sides
        ch, cw = sh, round(sh * W / H)
    else:                # taller: full width, cut top and bottom
        cw, ch = sw, round(sw * H / W)
    x = round((sw - cw) * ax)
    y = round((sh - ch) * ay)
    out = im.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)
    out.save(f"social/photos/{name}.jpg", quality=90, optimize=True)
    print(f"{name}: {src} {sw}x{sh}, crop {cw}x{ch} at {x},{y}, scale {W/cw:.2f}")
