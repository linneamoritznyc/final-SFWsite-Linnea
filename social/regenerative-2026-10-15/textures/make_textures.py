"""Background textures for the Regenerative post, generated on google/nano-banana with one of our own
soil photos as the reference (never plain text-to-image).
  python3 social/regenerative-2026-10-15/textures/make_textures.py
"""
import os, sys, concurrent.futures as cf, requests
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "social", "tools"))
import soil_cutouts as sc

STYLE = ("Use this photo as the reference for real soil colour, light and texture. Make a new real photograph, "
         "high detail, natural daylight, no text, no people, no hands. ")
JOBS = {
    "dry-cracked-earth": ("card-roots-in-soil-capri.jpg", "4:5",
        "Looking straight down at bare, degraded, sun-baked earth: pale dusty ochre soil broken into a pattern of deep "
        "cracks, a few dead dry grass stems, nothing living. Fill the whole frame evenly."),
    "living-soil-profile": ("card-roots-in-soil-capri.jpg", "4:5",
        "A side view cross-section of healthy living soil, like a cut soil profile: a band of green grass and clover on "
        "the top edge, below it dark crumbly topsoil full of fine white roots, white fungal threads, an earthworm burrow "
        "and small aggregates, getting slightly lighter toward the bottom. Fill the whole frame."),
    "living-soil-topdown": ("costa-rica-2024-07-20-fungal-hyphae.jpg", "4:5",
        "Looking straight down at dark, rich, moist living soil covered with young green seedlings, clover, moss, "
        "fallen leaves and fine white fungal threads. Fill the whole frame evenly."),
}

def one(item):
    name, (ref, ar, subject) = item
    small = os.path.join(HERE, "_ref-" + ref)
    im = Image.open(os.path.join(ROOT, "img", "new-2026-10", ref)).convert("RGB"); im.thumbnail((1200, 1200)); im.save(small, quality=90)
    out = sc.predict(f"{sc.API}/models/google/nano-banana/predictions",
                     {"input": {"prompt": STYLE + subject, "image_input": [sc.upload(small)], "aspect_ratio": ar, "output_format": "png"}})
    open(os.path.join(HERE, name + ".png"), "wb").write(requests.get(out, headers=sc.H).content)
    os.remove(small)
    return name

with cf.ThreadPoolExecutor(2) as ex:
    for n in ex.map(one, JOBS.items()): print(n, Image.open(os.path.join(HERE, n + ".png")).size)
