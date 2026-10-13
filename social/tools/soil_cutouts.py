"""Soil-life cutouts: nano-banana with one of our real photos as reference, then BiRefNet background removal.

  python3 social/tools/soil_cutouts.py [names]   generate (all by default) into social/cutouts-soil/
  python3 social/tools/soil_cutouts.py sheet     contact sheet of the cutouts on a checkerboard
"""
import os, sys, time, concurrent.futures as cf
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "img", "new-2026-10")
OUT = os.path.join(ROOT, "social", "cutouts-soil")
RAW = os.path.join(OUT, "_raw")
API = "https://api.replicate.com/v1"
H = {"Authorization": f"Bearer {os.environ['REPLICATE_API_TOKEN']}"}
BIREFNET = "f74986db0355b58403ed20963af156525e2891ea3c2d499bfbfb2a28cd87c5d7"

PROMPT = ("Use this photo as the reference for real soil, colour, light and texture. Make a new high-detail macro photograph "
          "of {subject}. One single object, centred, fully in frame with space around it, sharp focus, natural daylight, "
          "true-to-life colours, on a plain pure white background with nothing else. A real photograph, not an illustration. "
          "No text, no hands, no people.")
ITEMS = {
    "earthworm": ("costa-rica-2024-07-11-hands-in-the-compost.jpg", "one live pink-brown earthworm in a loose S curve with a few crumbs of dark soil on it"),
    "compost-white-fungal-threads": ("costa-rica-2024-07-20-fungal-hyphae.jpg", "a clump of dark finished compost with fluffy white fungal threads growing over it"),
    "dark-soil-clump": ("card-roots-in-soil-capri.jpg", "one crumbly clump of dark rich living soil with visible aggregates and tiny root hairs"),
    "roots-with-soil": ("card-roots-in-soil-capri.jpg", "a plant root ball: branching roots with soil crumbs clinging to them"),
    "wood-chips-pile": ("santa-fe-2026-10-aged-wood-chips.jpg", "a small heap of aged weathered wood chips"),
    "cracked-corn-pile": ("costa-rica-2024-07-05-cracked-corn-close-up.jpg", "a small mound of golden cracked corn kernels"),
    "pebbles": ("card-roots-in-soil-capri.jpg", "a small group of five smooth pebbles in earthy greys and browns"),
    "mushrooms": ("costa-rica-2024-07-20-fungal-hyphae.jpg", "a small cluster of three wild brown mushrooms with soil and white mycelium at their base"),
    "moss-clump": ("costa-rica-2023-08-17-tropical-undergrowth.jpg", "one cushion of bright green moss lifted from the ground with a thin layer of soil under it"),
    "fern-fiddlehead": ("costa-rica-2023-08-16-tropical-leaves.jpg", "a single fern fiddlehead, a young green frond unrolling in a tight spiral"),
    "ground-beetle": ("costa-rica-2024-07-20-fungal-hyphae.jpg", "one shiny dark ground beetle seen from above"),
    "dry-leaves-twigs": ("santa-fe-2026-10-aged-wood-chips.jpg", "a small loose bundle of dry brown fallen leaves and thin twigs"),
    "seedling-in-soil": ("card-roots-in-soil-capri.jpg", "a young green seedling with two leaves, pulled up with its white roots and a clump of soil"),
    "acorns": ("santa-fe-2026-10-aged-wood-chips.jpg", "two brown acorns with their caps"),
}


def upload(path):
    with open(path, "rb") as f:
        r = requests.post(f"{API}/files", headers=H, files={"content": (os.path.basename(path), f, "application/octet-stream")})
    r.raise_for_status()
    return r.json()["urls"]["get"]


def predict(url, body):
    for attempt in range(8):
        r = requests.post(url, headers={**H, "Prefer": "wait=60"}, json=body)
        if r.status_code == 429:
            time.sleep(10 * (attempt + 1)); continue
        r.raise_for_status(); p = r.json(); break
    while p["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(2); p = requests.get(p["urls"]["get"], headers=H).json()
    if p["status"] != "succeeded":
        raise RuntimeError(p.get("error"))
    o = p["output"]
    return o[0] if isinstance(o, list) else o


REFS = {}
def ref_url(name):
    if name not in REFS:
        small = os.path.join(RAW, "ref-" + name)
        im = Image.open(os.path.join(SRC, name)).convert("RGB"); im.thumbnail((1200, 1200)); im.save(small, quality=90)
        REFS[name] = upload(small)
    return REFS[name]


def one(name):
    ref, subject = ITEMS[name]
    try:
        out = predict(f"{API}/models/google/nano-banana/predictions",
                      {"input": {"prompt": PROMPT.format(subject=subject), "image_input": [ref_url(ref)], "output_format": "png"}})
        raw = os.path.join(RAW, f"{name}.png")
        open(raw, "wb").write(requests.get(out, headers=H).content)
        cut = predict(f"{API}/predictions", {"version": BIREFNET, "input": {"image": upload(raw)}})
        dest = os.path.join(OUT, f"{name}.png")
        open(dest, "wb").write(requests.get(cut, headers=H).content)
        im = Image.open(dest).convert("RGBA")
        im.crop(im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()).save(dest)
        return f"{name}: ok {im.size}"
    except Exception as e:
        return f"{name}: FAILED {e}"


def sheet():
    fs = sorted(f for f in os.listdir(OUT) if f.endswith(".png") and not f.startswith("contact"))
    T, cols = 300, 5
    rows = (len(fs) + cols - 1) // cols
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    S = Image.new("RGB", (cols * (T + 20) + 20, rows * (T + 46) + 20), (40, 40, 40))
    d = ImageDraw.Draw(S)
    for i, f in enumerate(fs):
        x, y = 20 + (i % cols) * (T + 20), 20 + (i // cols) * (T + 46)
        cb = Image.new("RGB", (T, T), (255, 255, 255)); cd = ImageDraw.Draw(cb)
        for yy in range(0, T, 20):
            for xx in range(0, T, 20):
                if (xx + yy) // 20 % 2: cd.rectangle((xx, yy, xx + 19, yy + 19), fill=(215, 215, 215))
        im = Image.open(os.path.join(OUT, f)).convert("RGBA"); im.thumbnail((T - 10, T - 10))
        cb.paste(im, ((T - im.width) // 2, (T - im.height) // 2), im)
        S.paste(cb, (x, y))
        d.text((x, y + T + 8), f[:-4], font=font, fill=(240, 240, 240))
    S.save(os.path.join(OUT, "contact-sheet.png"))


if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True)
    if sys.argv[1:] == ["sheet"]:
        sheet()
    else:
        names = sys.argv[1:] or list(ITEMS)
        for n in names: ref_url(ITEMS[n][0])
        with cf.ThreadPoolExecutor(2) as ex:
            for r in ex.map(one, names): print(r, flush=True)
        sheet()
