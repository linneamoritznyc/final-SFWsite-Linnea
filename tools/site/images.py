#!/usr/bin/env python3
"""Resolve an image a page uses to a local WebP in img/, repo copy first.

For each image URL a page asks for (usually a new.soilfoodweb.com upload):
  1. img/replacements/<same name> wins outright, if it exists.
  2. Otherwise look for the same picture already in this repo (img/, img/w/,
     img/uploads/, img/video/, ...): first by normalised file name,
     then by perceptual hash, so a renamed or recompressed copy still matches.
     The staging side of the comparison uses thumbs/ (the sweet-babbage
     thumbnails of every live image) when it can, so most checks need no
     download. The largest matching repo file is used.
  3. Only if the repo has no copy is the original downloaded from staging.
The chosen source is resized to at most 1600 px wide and saved as WebP under
300 KB at img/<name>.webp. content/staging/images.json records, per URL, the
output file, its size, where it came from and any review flags.

Alt text comes from image-descriptions.csv (the sweet-babbage inventory) when
it has the file, else from content/alt.json, else the page must supply it.
"""
import csv, io, json, os, re, subprocess, urllib.parse, urllib.request
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMG = os.path.join(ROOT, "img")
MANIFEST = os.path.join(ROOT, "content", "staging", "images.json")
CACHE = os.environ.get("SFW_IMG_CACHE", "/tmp/sfw-img-cache")
MAX_W, MAX_BYTES = 1600, 300 * 1024
REPO_DIRS = ["img", "img/w", "img/uploads", "img/video", "img/wild-ken-hill", "trifold-farmers"]
EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")

_manifest = None
_repo = None
_desc = None


def norm(name):
    """'Elaine Smile talking.png' and 'elaine-smile-talking-800.jpg' -> 'elaine-smile-talking'.

    Strips only WordPress and repo size suffixes (-1024x576, -scaled, -800),
    never an arbitrary number, so IMG_1069 and IMG_1494 stay different."""
    n = os.path.splitext(os.path.basename(name))[0].lower()
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    for _ in range(3):
        n = re.sub(r"-(\d{2,4}x\d{2,4}|scaled|400|600|800|1200|1600|2000)$", "", n)
    n = re.sub(r"-1$", "", n)
    return n


def dhash(im, size=16):
    g = ImageOps.exif_transpose(im).convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for y in range(size):
        for x in range(size):
            bits = (bits << 1) | (px[y * (size + 1) + x] > px[y * (size + 1) + x + 1])
    return bits


def ham(a, b):
    return bin(a ^ b).count("1")


def repo_index():
    global _repo
    if _repo is not None:
        return _repo
    cache = os.path.join(CACHE, "repo-index.json")
    old = json.load(open(cache)) if os.path.exists(cache) else {}
    _repo = []
    for d in REPO_DIRS:
        full = os.path.join(ROOT, d)
        if not os.path.isdir(full):
            continue
        for f in sorted(os.listdir(full)):
            p = os.path.join(full, f)
            if not f.lower().endswith(EXT) or not os.path.isfile(p):
                continue
            rel = os.path.relpath(p, ROOT)
            # Our own outputs live in img/ too; never match an image to itself.
            if d == "img" and f.endswith(".webp"):
                continue
            st = os.stat(p)
            key = "%s|%d|%d" % (rel, st.st_size, int(st.st_mtime))
            if key in old:
                _repo.append(old[key]); continue
            try:
                im = Image.open(p); w, h = im.size; hs = dhash(im)
            except Exception:
                continue
            rec = {"key": key, "path": rel, "norm": norm(f), "w": w, "h": h, "hash": hs}
            old[key] = rec
            _repo.append(rec)
    os.makedirs(CACHE, exist_ok=True)
    json.dump(old, open(cache, "w"))
    return _repo


def descriptions():
    global _desc
    if _desc is None:
        _desc = {}
        p = os.path.join(ROOT, "image-descriptions.csv")
        for r in csv.DictReader(open(p, encoding="utf-8")):
            _desc[norm(r["Current file name"])] = r
        extra = os.path.join(ROOT, "content", "alt.json")
        if os.path.exists(extra):
            for k, v in json.load(open(extra, encoding="utf-8")).items():
                _desc.setdefault(norm(k), {})["Alt text"] = v
    return _desc


def fetch(url):
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9._-]+", "_", url)[-180:])
    if not os.path.exists(fn):
        parts = urllib.parse.urlsplit(url)
        url = urllib.parse.urlunsplit(parts._replace(path=urllib.parse.quote(urllib.parse.unquote(parts.path))))
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (preview build)"})
        with urllib.request.urlopen(req, timeout=60) as r, open(fn, "wb") as f:
            f.write(r.read())
    return fn


def original_url(url):
    """WordPress size variants -> the uploaded original."""
    return re.sub(r"-\d{2,4}x\d{2,4}(\.\w+)$", r"\1", url)


def load_manifest():
    global _manifest
    if _manifest is None:
        _manifest = json.load(open(MANIFEST, encoding="utf-8")) if os.path.exists(MANIFEST) else {}
    return _manifest


def save_manifest():
    json.dump(load_manifest(), open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)


def encode(src_path, out_path):
    im = ImageOps.exif_transpose(Image.open(src_path))
    if im.mode in ("P", "LA") or (im.mode == "RGBA" and im.getextrema()[3][0] == 255):
        im = im.convert("RGBA" if im.mode in ("P", "LA") else "RGB")
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    for q in (82, 76, 70, 64, 58, 50, 42):
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=q, method=6)
        if buf.tell() <= MAX_BYTES:
            break
    else:
        # Still too heavy at q42: step the width down until it fits.
        w = im.width
        while buf.tell() > MAX_BYTES and w > 400:
            w = int(w * 0.85)
            sm = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            buf = io.BytesIO(); sm.save(buf, "WEBP", quality=60, method=6)
        im = sm
    open(out_path, "wb").write(buf.getvalue())
    return im.width, im.height, buf.tell()


def resolve(url, name=None):
    """Return the manifest record for url, creating the WebP on first use."""
    man = load_manifest()
    if url in man and os.path.exists(os.path.join(ROOT, man[url]["file"])):
        return man[url]
    base = os.path.basename(url.split("?")[0])
    n = name or norm(base) or "image"
    flags = []
    src_kind, src = None, None
    rep = os.path.join(IMG, "replacements")
    if os.path.isdir(rep):
        for f in os.listdir(rep):
            if norm(f) == norm(base):
                src_kind, src = "replacement", os.path.join(rep, f)
    match = None
    if not src and not url.startswith("http"):
        src_kind, src = "repo", os.path.join(ROOT, url)
    if not src:
        idx = repo_index()
        byname = [r for r in idx if r["norm"] == norm(base)]
        probe = None
        th = os.path.join(ROOT, "thumbs", os.path.splitext(base)[0] + ".jpg")
        try:
            probe = Image.open(th) if os.path.exists(th) else Image.open(fetch(original_url(url) if "soilfoodweb.com" in url else url))
            ph = dhash(probe)
        except Exception:
            ph = None
        if ph is not None:
            # A file name alone never decides: the pixels have to agree too.
            byname = [r for r in byname if ham(ph, r["hash"]) <= 40]
            if byname:
                match = max(byname, key=lambda r: r["w"] * r["h"]); how = "name and picture"
            else:
                near = sorted(((ham(ph, r["hash"]), r) for r in idx), key=lambda t: t[0])
                same = [r for d, r in near if d <= 18]
                if same:
                    match = max(same, key=lambda r: r["w"] * r["h"]); how = "picture"
        if match:
            src_kind, src = "repo (%s match)" % how, os.path.join(ROOT, match["path"])
    if not src:
        try:
            src = fetch(original_url(url)) if "soilfoodweb.com" in url else fetch(url)
        except Exception:
            src = fetch(url)
        src_kind = "staging download"
    with Image.open(src) as im:
        sw, sh = im.size
    out_name = n + ".webp"
    taken = {v["file"] for k, v in man.items() if k != url}
    i = 2
    while "img/" + out_name in taken:
        out_name = "%s-%d.webp" % (n, i); i += 1
    w, h, b = encode(src, os.path.join(IMG, out_name))
    if "screenshot" in base.lower():
        flags.append("screenshot")
    if sw < 800:
        flags.append("low resolution (%dx%d source)" % (sw, sh))
    d = descriptions().get(norm(base), {})
    rec = {"file": "img/" + out_name, "w": w, "h": h, "bytes": b,
           "source": src_kind, "source_path": os.path.relpath(src, ROOT) if src.startswith(ROOT) else url,
           "source_size": "%dx%d" % (sw, sh), "alt": d.get("Alt text", ""), "shows": d.get("What it shows", ""),
           "flags": flags}
    man[url] = rec
    return rec


if __name__ == "__main__":
    import sys
    for u in sys.argv[1:]:
        print(json.dumps(resolve(u), indent=1))
    save_manifest()
