#!/usr/bin/env python3
"""Image handoff for Stephanie: every final image, cut to the slot it fills on new.soilfoodweb.com.

    python3 tools/handoff/export.py <slots.json>

slots.json comes from tools/handoff/slots.js (the local preview measured at 1440 px wide). For each
slot the image the page shows is cropped to the slot's shape (as the browser does: object-fit
cover, centred unless the page sets a position), sized for sharp display (twice the slot width,
at most 1600 px, never upscaled), saved as JPG under 300 KB without EXIF in
exports/stephanie/<page>/<page> - <section> - <slot>.jpg, and listed in
exports/stephanie/image-handoff.csv.
"""
import csv, json, os, re, shutil, sys
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "exports", "stephanie")
STAGING = "https://new.soilfoodweb.com"
MAX_W, LIMIT = 1600, 300 * 1024


def source_file(src):
    """The best local copy of what the browser showed: the largest generated width of that picture."""
    path = re.sub(r"^https?://[^/]+", "", src).split("?")[0].lstrip("/")
    m = re.match(r"(img/new/.+?)-\d+w\.(jpg|webp)$", path)
    if m:
        stem = m.group(1)
        d, base = os.path.split(stem)
        sizes = [f for f in os.listdir(os.path.join(ROOT, d)) if re.fullmatch(re.escape(base) + r"-\d+w\.jpg", f)]
        if sizes:
            return os.path.join(ROOT, d, max(sizes, key=lambda f: int(f.rsplit("-", 1)[1][:-5])))
    return os.path.join(ROOT, path)


def clean(t):
    t = re.sub(r"[\\/:*?\"<>|#]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()[:70] or "Top"


def page_name(path):
    return "home" if path == "/" else clean(path.strip("/").replace("/", " "))


def pct(v):
    m = re.match(r"([\d.]+)%", v or "")
    return float(m.group(1)) / 100 if m else .5


def cut(im, w, h, fit, pos):
    if fit not in ("cover",) or not w or not h:
        return im
    want = w / h
    iw, ih = im.size
    if iw / ih > want:
        cw, ch = round(ih * want), ih
    else:
        cw, ch = iw, round(iw / want)
    px, py = (pct(p) for p in ((pos or "50% 50%").split() + ["50%"])[:2])
    x, y = round((iw - cw) * px), round((ih - ch) * py)
    return im.crop((x, y, x + cw, y + ch))


def save(im, dest):
    q = 86
    while True:
        im.save(dest, "JPEG", quality=q, optimize=True, progressive=True)
        if os.path.getsize(dest) <= LIMIT:
            return
        if q > 70:
            q -= 4
        else:
            im = im.resize((round(im.size[0] * .9), round(im.size[1] * .9)), Image.LANCZOS)


def main():
    slots = json.load(open(sys.argv[1], encoding="utf-8"))
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    rows, used = [], set()
    for s in slots:
        page = page_name(s["page"])
        section = clean(s["head"])
        slot = s["kind"] if s["kind"] in ("hero", "banner") and s["index"] == 1 else "%s %d" % (s["kind"], s["index"])
        name = "%s - %s - %s.jpg" % (page, section, slot)
        n = 2
        while (page, name) in used:
            name = "%s - %s - %s (%d).jpg" % (page, section, slot, n)
            n += 1
        used.add((page, name))
        src = source_file(s["src"])
        if not os.path.exists(src):
            print("missing source", s["page"], s["src"])
            continue
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im = cut(im, s["w"], s["h"], s["fit"], s["pos"])
        tw = min(2 * s["w"], MAX_W, im.size[0])
        if tw < im.size[0]:
            im = im.resize((tw, round(im.size[1] * tw / im.size[0])), Image.LANCZOS)
        os.makedirs(os.path.join(OUT, page), exist_ok=True)
        save(im, os.path.join(OUT, page, name))
        rows.append({"wordpress_page_url": STAGING + s["page"], "section_heading": s["head"] or "(top of page)",
                     "slot": slot, "file_name": "%s/%s" % (page, name), "alt_text": s["alt"], "caption": s["caption"],
                     "recommended_size_px": "%d x %d (shown at %d x %d on a 1440 px screen)" % (2 * s["w"], 2 * s["h"], s["w"], s["h"])})
    with open(os.path.join(OUT, "image-handoff.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "images in", len({r["wordpress_page_url"] for r in rows}), "pages")


if __name__ == "__main__":
    main()
