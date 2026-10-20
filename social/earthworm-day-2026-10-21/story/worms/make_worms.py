"""Three silly earthworms in hats for the World Earthworm Day story, google/nano-banana with our earthworm
photo as the reference, then BiRefNet background removal.
  python3 social/earthworm-day-2026-10-21/story/worms/make_worms.py [names]
"""
import os, sys, concurrent.futures as cf, requests
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "social", "tools"))
import soil_cutouts as sc

REF = os.path.join(ROOT, "social", "cutouts-soil", "_raw", "earthworm.png")
STYLE = ("Use this earthworm photo as the reference for a real, natural-looking earthworm. Make a new high-detail macro photograph "
         "of ONE earthworm with a funny, charming personality, curled in a loose S shape, its front end raised up like it is posing, "
         "wearing a tiny hat that fits its head. {who} Soft daylight, sharp focus, plain pure white background, nothing else in frame. "
         "A real photograph with a playful twist, no cartoon face, no eyes, no text.")
WORMS = {
    "epigeic": "A small, slim, bright red earthworm wearing a tiny hat made from a curled autumn leaf, with a few crumbs of leaf litter on it.",
    "endogeic": "A pale pink-grey earthworm wearing a tiny woven straw sun hat, a few crumbs of soil on its body.",
    "anecic": "A big, long, dark reddish-brown earthworm wearing a tiny black miner's helmet with a little glowing headlamp, ready for a night shift.",
}


def one(name, ref):
    raw = os.path.join(HERE, f"raw-{name}.png")
    if not os.path.exists(raw):
        try:
            out = sc.predict(f"{sc.API}/models/google/nano-banana/predictions",
                             {"input": {"prompt": STYLE.format(who=WORMS[name]), "image_input": [ref], "output_format": "png"}})
        except RuntimeError as e:
            return f"{name}: failed {e}"
        open(raw, "wb").write(requests.get(out, headers=sc.H).content)
    cut = sc.predict(f"{sc.API}/predictions", {"version": sc.BIREFNET, "input": {"image": sc.upload(raw)}})
    dest = os.path.join(HERE, f"worm-{name}.png"); open(dest, "wb").write(requests.get(cut, headers=sc.H).content)
    im = Image.open(dest).convert("RGBA"); im.crop(im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()).save(dest)
    return f"{name}: ok"

ref = sc.upload(REF)
with cf.ThreadPoolExecutor(2) as ex:
    for r in ex.map(lambda n: one(n, ref), sys.argv[1:] or list(WORMS)): print(r)
