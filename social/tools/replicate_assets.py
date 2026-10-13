"""Make the collage assets with the Replicate API.

  python3 social/tools/replicate_assets.py people          cut people out of the five workshop photos
  python3 social/tools/replicate_assets.py elements [names] generate cut-paper elements, then remove backgrounds

Needs REPLICATE_API_TOKEN. Outputs go to social/assets/.
"""
import os, sys, io, time, json, concurrent.futures as cf
import requests
from PIL import Image

API = "https://api.replicate.com/v1"
H = {"Authorization": f"Bearer {os.environ['REPLICATE_API_TOKEN']}"}
ROOT = os.path.join(os.path.dirname(__file__), "..", "assets")
BIREFNET = "f74986db0355b58403ed20963af156525e2891ea3c2d499bfbfb2a28cd87c5d7"

PHOTOS = {
    "group-pergola": "img/cy-workshop-8.jpg",
    "microscope": "img/costa-rica-2025-microscopy-students-mentors.jpg",
    "compost-turning": "img/pile-turning-wes-8-scaled.jpg",
    "barn-gathering": "img/IMG_1942-scaled.jpg",
    "group-laughing": "img/wild-ken-hill/IMG_1500.jpg",
}

STYLE = (
    "Handmade cut-paper collage element. Layered hand-cut matte paper with crisp scissor-cut and torn edges, "
    "visible paper fibre texture, small soft drop shadows between the paper layers, warm and joyful, "
    "like a page from a scrapbook made by a gifted illustrator. Strict limited palette: deep forest green #22371F, "
    "food web green #156826, light leaf green #59A66C, cream paper #F4F1EA, soil brown #4F3433, "
    "small touches of mustard gold #C9A227. Isolated on a plain flat pure white background, nothing else in frame, "
    "no text, no letters. Subject: "
)
ELEMENTS = {
    "flower-daisy": ("1:1", "a single cream daisy-like flower with a mustard gold centre and a short green stem with two leaves"),
    "flower-cluster": ("1:1", "a small bouquet cluster of meadow flowers: cream daisies, gold buttercups and green buds on stems"),
    "flower-gold": ("1:1", "a single mustard gold wildflower with layered petals and a deep green stem"),
    "leaf-sprig": ("2:3", "a single tall sprig of leaves on a stem, leaves in three greens, with cut vein lines"),
    "leaves-cluster": ("1:1", "a loose cluster of seven overlapping leaves in deep green, food web green and light green"),
    "fern": ("2:3", "a single curling fern frond in light and food web green"),
    "seedling": ("2:3", "a small seedling sprouting with two leaves above and white-cream roots spreading below"),
    "roots-tangle": ("3:2", "a wide tangle of branching plant roots in cream and soil brown, fine root hairs, spreading sideways"),
    "worm": ("3:2", "a single happy earthworm curving in an S shape, in dusty pink-brown paper with segment lines"),
    "mushrooms-cluster": ("1:1", "a cluster of three mushrooms of different heights with cream stems and soil brown and gold caps, a little moss at the base"),
    "mushroom-single": ("2:3", "a single tall mushroom with a cream stem and a soil brown cap with cream spots"),
    "fungal-threads": ("3:2", "a delicate branching network of cream fungal hyphae threads, like a web"),
    "nematode": ("3:2", "a single cute microscopic nematode: a long slender translucent cream worm with a curving body and visible inner line, scientific but friendly"),
    "protozoa": ("1:1", "three small friendly soil microorganisms: a round amoeba, an oval ciliate with tiny hairs, and a testate amoeba shell, in light green and cream"),
    "compost-heap": ("3:2", "a rounded compost heap made of layered torn paper in soil brown, dark brown and green, with leaf scraps and straw bits"),
    "stones": ("3:2", "a group of five smooth pebbles and stones in grey-brown, cream and soil brown paper"),
    "confetti": ("1:1", "a scatter of paper confetti: small circles, triangles and wavy strips in gold, cream, light green and food web green, spread apart from each other"),
    "torn-strip-cream": ("21:9", "one long horizontal strip of torn cream paper with ragged torn edges on the long sides"),
    "torn-strip-green": ("21:9", "one long horizontal strip of torn deep green paper with ragged torn edges on the long sides"),
    "soil-layers": ("21:9", "a wide horizontal cross-section of soil layers made of stacked torn paper: green grass edge on top, dark brown topsoil, roots, a worm, tiny organisms, stones, lighter subsoil at the bottom"),
    "sun-burst": ("1:1", "a small mustard gold paper sun with cut rays"),
}


def upload(path):
    with open(path, "rb") as f:
        r = requests.post(f"{API}/files", headers=H, files={"content": (os.path.basename(path), f, "application/octet-stream")})
    r.raise_for_status()
    return r.json()["urls"]["get"]


def run(url, body):
    r = requests.post(url, headers={**H, "Prefer": "wait=60"}, json=body)
    r.raise_for_status()
    p = r.json()
    while p["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(2)
        p = requests.get(p["urls"]["get"], headers=H).json()
    if p["status"] != "succeeded":
        raise RuntimeError(p.get("error"))
    out = p["output"]
    return out[0] if isinstance(out, list) else out


def fetch(url, dest):
    data = requests.get(url, headers=H).content
    with open(dest, "wb") as f:
        f.write(data)
    return dest


def remove_bg(src, dest):
    out = run(f"{API}/predictions", {"version": BIREFNET, "input": {"image": upload(src)}})
    fetch(out, dest)
    im = Image.open(dest).convert("RGBA")
    bbox = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    im.crop(bbox).save(dest)  # trim to the cut edge
    return dest


def people():
    def one(item):
        name, src = item
        remove_bg(src, os.path.join(ROOT, "people", f"{name}-cutout.png"))
        return name
    with cf.ThreadPoolExecutor(2) as ex:
        for n in ex.map(one, PHOTOS.items()):
            print("cut out", n)


def elements(names):
    def one(name):
        ar, subject = ELEMENTS[name]
        raw = os.path.join(ROOT, "raw", f"{name}.png")
        out = run(f"{API}/models/black-forest-labs/flux-1.1-pro/predictions",
                  {"input": {"prompt": STYLE + subject, "aspect_ratio": ar, "output_format": "png", "safety_tolerance": 2}})
        fetch(out, raw)
        remove_bg(raw, os.path.join(ROOT, "elements", f"{name}.png"))
        return name
    with cf.ThreadPoolExecutor(2) as ex:
        for n in ex.map(one, names or list(ELEMENTS)):
            print("element", n)


if __name__ == "__main__":
    {"people": lambda: people(), "elements": lambda: elements(sys.argv[2:])}[sys.argv[1]]()
