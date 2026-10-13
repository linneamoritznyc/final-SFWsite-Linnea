"""More design options for the Regenerative carousel (B to E), same words. B, C, D have no photos; E has one.

  python3 social/regenerative-2026-10-15/variants.py
    -> option-b/, option-c/, option-d/ (layers, slides.html, slide-N.png, contact-sheet.png, regenerative-option-X-canva.pptx)
    -> options-compare.png (A = the current version, then B, C, D, E)
"""
import os, json, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SOILC = os.path.join(ROOT, "social", "cutouts-soil"); FLOW = os.path.join(ROOT, "social", "cutouts-flowers")
NEW = os.path.join(ROOT, "img", "new-2026-10")
W, H = 1080, 1350
DEEP, GREEN, LIGHT, CREAM, KRAFT = "#22371F", "#156826", "#59A66C", "#F4F1EA", "#CDB38A"
def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

Q = [("A destination", "or a direction?"), ("A certified status", "or a way of thinking?"),
     ("A premium product,", "or a standard everyone who works the land can reach?")]
HEAD, SMALL1 = "What does Regenerative actually mean?", "And who gets to decide?"
HEAD5, SMALL5 = "Living soil in the hands of every person who works the land.", "What does regenerative mean to you? Tell us in the comments."


def paper(color, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    n = np.array(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255 - .5
    img = np.array(rgb(color), np.float32)[None, None] + n[..., None] * 14 + rng.normal(0, 3, (H, W, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def ragged(w, h, edges, seed, amp=12):
    rnd = random.Random(seed)
    def line(n):
        v, o = 0.0, []
        for _ in range(n):
            v = max(-1, min(1, v + rnd.uniform(-.35, .35))); o.append(v * amp + rnd.uniform(-2, 2))
        return np.array(o)
    yy, xx = np.mgrid[0:h, 0:w]
    t = (line(w) + amp + 2) if "t" in edges else np.zeros(w)
    b = h - ((line(w) + amp + 2) if "b" in edges else np.zeros(w))
    m = (yy >= t[None]) & (yy <= b[None])
    return Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7))


def shadow(im, off=(6, 10), blur=9, a=.35):
    pad = blur * 3 + 12
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (30, 22, 15, 255)); sh.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    s = Image.new("RGBA", out.size, (0, 0, 0, 0)); s.alpha_composite(sh, (pad + off[0], pad + off[1]))
    out.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur))); out.alpha_composite(im, (pad, pad))
    return out, pad


def cover(path, w, h, fy=.5):
    im = Image.open(path).convert("RGB"); s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    y = round((im.height - h) * fy); x = (im.width - w) // 2
    return im.crop((x, y, x + w, y + h))


def cut(name, w=None, h=None, rot=0, folder=SOILC):
    im = Image.open(os.path.join(folder, name)).convert("RGBA")
    im = im.resize((w, round(im.height * w / im.width)) if w else (round(im.width * h / im.height), h), Image.LANCZOS)
    return im.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else im


def soil_strip(h=300, seed=1):
    """A cross-section of soil from real textures: compost on top, then soil with roots, torn edges."""
    out = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    a = cover(os.path.join(NEW, "R5A_4007.jpg"), W, h, .5).convert("RGBA"); a.putalpha(ragged(W, h, "t", seed, 14))
    out.alpha_composite(a)
    b = cover(os.path.join(NEW, "santa-fe-2026-10-aged-wood-chips.jpg"), W, h // 3, .9).convert("RGBA"); b.putalpha(ragged(W, h // 3, "tb", seed + 1, 10))
    out.alpha_composite(b, (0, 0))
    return out


logo = Image.open(os.path.join(ROOT, "img", "sfwlogo-240.png")).convert("RGBA")
def logo_img(w=150, disc=False):
    l = logo.resize((w, round(w * logo.height / logo.width)), Image.LANCZOS)
    if not disc: return l
    d = round(w * 1.25); o = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    ImageDraw.Draw(o).ellipse((0, 0, d - 1, d - 1), fill=rgb(CREAM) + (255,)); o.alpha_composite(l, ((d - l.width) // 2, (d - l.height) // 2))
    return o


class Deck:
    def __init__(self, key):
        self.key, self.dir = key, os.path.join(HERE, f"option-{key}")
        self.lay = os.path.join(self.dir, "layers"); os.makedirs(self.lay, exist_ok=True)
        self.slides = []

    def slide(self, bg):
        s = dict(n=len(self.slides) + 1, items=[]); self.slides.append(s)
        self.img(s, "background", paper(bg, s["n"] + ord(self.key)), 0, 0, jpg=True)
        return s

    def img(self, s, name, im, x, y, jpg=False, center=False, shade=False):
        if shade:
            im, pad = shadow(im); x -= pad; y -= pad
        if center: x, y = round(x - im.width / 2), round(y - im.height / 2)
        box = (max(0, -x), max(0, -y), min(im.width, W - x), min(im.height, H - y)); im = im.crop(box); x += box[0]; y += box[1]
        fn = f"s{s['n']}-{len(s['items']) + 1:02d}-{name}." + ("jpg" if jpg else "png")
        (im.convert("RGB").save(os.path.join(self.lay, fn), quality=88) if jpg else im.save(os.path.join(self.lay, fn), optimize=True))
        s["items"].append(dict(type="image", name=name, file="layers/" + fn, x=x, y=y, w=im.width, h=im.height))

    def text(self, s, name, runs, x, y, w, h, size, font="Montserrat", weight=700, lh=1.1, align="left"):
        s["items"].append(dict(type="text", name=name, runs=runs, x=x, y=y, w=w, h=h, size=size, font=font, weight=weight, lh=lh, align=align))

    def write(self):
        css = """@font-face{font-family:"Montserrat";src:url("../../../fonts/montserrat-latin-variable.woff2");font-weight:100 900}
@font-face{font-family:"Source Sans 3";src:url("../../../fonts/source-sans-3-latin-400-normal.woff2");font-weight:400}
@font-face{font-family:"Source Sans 3";src:url("../../../fonts/source-sans-3-latin-600-normal.woff2");font-weight:600}
*{margin:0;box-sizing:border-box}body{background:#555;display:grid;gap:40px;padding:40px;justify-content:center}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden}.slide img{position:absolute;display:block}.slide p{position:absolute}"""
        out = [f"<!doctype html><html><head><meta charset='utf-8'><title>Regenerative option {self.key.upper()}</title><style>{css}</style></head><body>"]
        for s in self.slides:
            out.append(f"<section class='slide'>")
            for it in s["items"]:
                if it["type"] == "image":
                    out.append(f"<img src='{it['file']}' style='left:{it['x']}px;top:{it['y']}px;width:{it['w']}px;height:{it['h']}px' alt=''>")
            for it in s["items"]:
                if it["type"] == "text":
                    body = "".join(f"<span style='color:{c}'>{t}</span>" + ("<br>" if nl else "") for t, c, nl in it["runs"])
                    out.append(f"<p style='left:{it['x']}px;top:{it['y']}px;width:{it['w']}px;font-family:\"{it['font']}\";font-size:{it['size']}px;"
                               f"font-weight:{it['weight']};line-height:{it['lh']};text-align:{it['align']}'>{body}</p>")
            out.append("</section>")
        open(os.path.join(self.dir, "slides.html"), "w").write("\n".join(out + ["</body></html>"]))
        subprocess.run(["node", os.path.join(ROOT, "social", "turns-one-2026-10-16", "render.cjs"), self.dir], check=True)
        from pptx import Presentation
        from pptx.util import Emu, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        E = 914400 / 108
        prs = Presentation(); prs.slide_width, prs.slide_height = Emu(round(W * E)), Emu(round(H * E))
        for s in self.slides:
            sl = prs.slides.add_slide(prs.slide_layouts[6])
            for it in s["items"]:
                if it["type"] == "image":
                    sl.shapes.add_picture(os.path.join(self.dir, it["file"]), *[Emu(round(it[k] * E)) for k in ("x", "y", "w", "h")]).name = it["name"]
            for it in s["items"]:
                if it["type"] != "text": continue
                tb = sl.shapes.add_textbox(*[Emu(round(it[k] * E)) for k in ("x", "y", "w", "h")]); tb.name = it["name"]
                tf = tb.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                p = tf.paragraphs[0]
                for t, c, nl in it["runs"]:
                    p.line_spacing = it["lh"]; p.alignment = PP_ALIGN.CENTER if it["align"] == "center" else PP_ALIGN.LEFT
                    r = p.add_run(); r.text = t; f = r.font; f.name = it["font"]; f.size = Pt(round(it["size"] * 72 / 108, 1))
                    f.bold = it["weight"] >= 600; f.color.rgb = RGBColor(*rgb(c))
                    if nl: p = tf.add_paragraph()
        prs.save(os.path.join(self.dir, f"regenerative-option-{self.key}-canva.pptx"))


# ---------- B. Deep green ground: the whole post on dark green, questions in cream and Light Green ----------
d = Deck("b")
s = d.slide(DEEP)
d.text(s, "headline", [(HEAD, CREAM, False)], 72, 300, 936, 400, 112, lh=1.04)
d.text(s, "small-line", [(SMALL1, LIGHT, False)], 76, 730, 900, 70, 54, font="Source Sans 3", weight=600)
d.img(s, "earthworm", cut("earthworm.png", h=380, rot=-35), 840, 1130, center=True)
d.img(s, "fern-fiddlehead", cut("fern-fiddlehead.png", w=280), 230, 1160, center=True)
for (before, after), item in zip(Q, [("pebbles.png", 260), ("acorns.png", 280), ("moss-clump.png", 300)]):
    s = d.slide(DEEP)
    d.img(s, "logo", logo_img(110, disc=True), W - 72 - 138, 64)
    d.text(s, "question", [(before, CREAM, True), (after, LIGHT, False)], 72, 340, 936, 700, 108, lh=1.06)
    d.img(s, item[0][:-4], cut(item[0], w=item[1]), 200, 1200, center=True)
s = d.slide(DEEP)
for nm, f, h_, cx, cy, r in [("poppy", "norfolk-common-poppy.png", 460, 170, 330, -6), ("marigold", "tamil-nadu-marigold.png", 380, 410, 360, 6),
                             ("paintbrush", "santa-fe-indian-paintbrush.png", 500, 650, 300, -4), ("heliconia", "costa-rica-heliconia.png", 540, 900, 300, 8)]:
    d.img(s, "flower-" + nm, cut(f, h=h_, rot=r, folder=FLOW), cx, cy, center=True)
d.text(s, "headline", [(HEAD5, CREAM, False)], 72, 720, 936, 330, 80, lh=1.08)
d.text(s, "small-line", [(SMALL5, LIGHT, False)], 76, 1080, 900, 130, 46, font="Source Sans 3", weight=600, lh=1.25)
d.img(s, "logo", logo_img(110, disc=True), W - 72 - 138, 1180)
d.write()

# ---------- C. The soil line: cream pages standing on a torn cross-section of real soil ----------
d = Deck("c")
s = d.slide(CREAM)
band = Image.new("RGBA", (W, 470), rgb(DEEP) + (255,)); band.putalpha(ragged(W, 470, "b", 31, 12))
d.img(s, "band", band, 0, 0)
d.text(s, "headline", [(HEAD, CREAM, False)], 72, 72, 936, 200, 80, lh=1.06)
d.text(s, "small-line", [(SMALL1, CREAM, False)], 76, 345, 900, 60, 46, font="Source Sans 3")
d.img(s, "soil-strip", soil_strip(360, 3), 0, H - 360)
d.img(s, "fern-fiddlehead", cut("fern-fiddlehead.png", w=330), 540, 870, center=True)
d.img(s, "earthworm", cut("earthworm.png", h=200, rot=-80), 300, 1200, center=True)
for i, ((before, after), (sprout, sw)) in enumerate(zip(Q, [("moss-clump.png", 300), ("mushrooms.png", 280), ("fern-fiddlehead.png", 230)])):
    s = d.slide(CREAM)
    d.img(s, "logo", logo_img(150), W - 72 - 150, 64)
    d.text(s, "question", [(before, DEEP, True), (after, GREEN, False)], 72, 260, 936, 640, 104, lh=1.06)
    d.img(s, "soil-strip", soil_strip(300, 10 + i), 0, H - 300)
    im = cut(sprout, w=sw); d.img(s, sprout[:-4], im, 820, H - 300 - im.height // 2 + 60, center=True)
s = d.slide(CREAM)
band = Image.new("RGBA", (W, 480), rgb(DEEP) + (255,)); band.putalpha(ragged(W, 480, "b", 51, 12))
d.img(s, "band", band, 0, 0)
d.text(s, "headline", [(HEAD5, CREAM, False)], 72, 72, 936, 260, 72, lh=1.08)
d.text(s, "small-line", [(SMALL5, CREAM, False)], 76, 340, 900, 110, 42, font="Source Sans 3", lh=1.25)
d.img(s, "soil-strip", soil_strip(300, 55), 0, H - 300)
for nm, f, h_, cx, r in [("poppy", "norfolk-common-poppy.png", 470, 170, -4), ("marigold", "tamil-nadu-marigold.png", 400, 410, 4),
                         ("paintbrush", "santa-fe-indian-paintbrush.png", 520, 650, -3), ("heliconia", "costa-rica-heliconia.png", 520, 900, 5)]:
    im = cut(f, h=h_, rot=r, folder=FLOW); d.img(s, "flower-" + nm, im, cx, H - 300 - im.height // 2 + 40, center=True)
d.write()

# ---------- D. Specimen sheet: kraft paper, one soil specimen per page, type on a torn cream label ----------
d = Deck("d")
def label(w, h, seed):
    im = Image.new("RGBA", (w, h), rgb(CREAM) + (255,)); m = ragged(w, h, "tb", seed, 9)
    im.putalpha(m); return im
s = d.slide(KRAFT)
lab = Image.new("RGBA", (W - 96, 470), rgb(DEEP) + (255,)); lab.putalpha(ragged(W - 96, 470, "tb", 61, 10))
d.img(s, "band", lab, 48, 70, shade=True)
d.text(s, "headline", [(HEAD, CREAM, False)], 100, 125, 880, 260, 78, lh=1.04)
d.text(s, "small-line", [(SMALL1, CREAM, False)], 104, 420, 860, 60, 46, font="Source Sans 3")
d.img(s, "dark-soil", cut("dark-soil-clump.png", w=720), 540, 980, center=True, shade=True)
d.img(s, "mushrooms", cut("mushrooms.png", w=260), 860, 1150, center=True)
for i, ((before, after), (spec, sw, rot)) in enumerate(zip(Q, [("earthworm.png", 520, -20), ("acorns.png", 420, 8), ("fern-fiddlehead.png", 380, 0)])):
    s = d.slide(KRAFT)
    d.img(s, "label", label(W - 96, 720, 70 + i), 48, 100, shade=True)
    d.text(s, "question", [(before, DEEP, True), (after, GREEN, False)], 100, 170, 880, 600, 88, lh=1.06)
    d.img(s, spec[:-4], cut(spec, w=sw, rot=rot), 540, 1090, center=True, shade=True)
    d.img(s, "logo", logo_img(130), 72, H - 72 - 113)
s = d.slide(KRAFT)
for nm, f, h_, cx, cy, r in [("poppy", "norfolk-common-poppy.png", 520, 190, 360, -8), ("marigold", "tamil-nadu-marigold.png", 420, 420, 400, 6),
                             ("paintbrush", "santa-fe-indian-paintbrush.png", 540, 660, 330, -4), ("heliconia", "costa-rica-heliconia.png", 560, 900, 330, 8)]:
    d.img(s, "flower-" + nm, cut(f, h=h_, rot=r, folder=FLOW), cx, cy, center=True, shade=True)
lab = Image.new("RGBA", (W - 96, 520), rgb(DEEP) + (255,)); lab.putalpha(ragged(W - 96, 520, "tb", 81, 10))
d.img(s, "band", lab, 48, 760, shade=True)
d.text(s, "headline", [(HEAD5, CREAM, False)], 100, 830, 880, 260, 70, lh=1.08)
d.text(s, "small-line", [(SMALL5, CREAM, False)], 104, 1110, 860, 110, 42, font="Source Sans 3", lh=1.25)
d.write()


# ---------- E. One photo only: slide 1 is the August 2023 high-five over the compost, the rest is type and cutouts ----------
d = Deck("e")
s = d.slide(CREAM)
ph = Image.open(os.path.join(NEW, "students-high-five-at-compost.jpg")).convert("RGB")   # 2400 x 1350, catalog best for Aug 2023
cw = round(ph.height * W / H); x0 = round((ph.width - cw) * 0.5)
d.img(s, "photo-high-five-at-compost", ph.crop((x0, 0, x0 + cw, ph.height)).resize((W, H), Image.LANCZOS), 0, 0, jpg=True)
band = Image.new("RGBA", (W, 330), rgb(DEEP) + (255,)); d.img(s, "band", band, 0, 0)
d.text(s, "headline", [(HEAD, CREAM, False)], 72, 64, 936, 160, 64, lh=1.15)
d.text(s, "small-line", [(SMALL1, CREAM, False)], 72, 236, 936, 56, 42, font="Source Sans 3", lh=1.3)
for (before, after) in Q:
    s = d.slide(CREAM)
    d.img(s, "logo", logo_img(168), W - 72 - 168, 64)
    d.text(s, "question", [(before, DEEP, True), (after, GREEN, False)], 96, 420, 888, 760, 96, lh=1.1)
s = d.slide(CREAM)
for nm, f, h_, cx, cy, r in [("poppy", "norfolk-common-poppy.png", 520, 160, 520, -6), ("marigold", "tamil-nadu-marigold.png", 420, 400, 560, 6),
                             ("paintbrush", "santa-fe-indian-paintbrush.png", 560, 640, 470, -4), ("heliconia", "costa-rica-heliconia.png", 600, 900, 460, 8)]:
    d.img(s, "flower-" + nm, cut(f, h=h_, rot=r, folder=FLOW), cx, cy, center=True)
d.img(s, "band", Image.new("RGBA", (W, 440), rgb(DEEP) + (255,)), 0, H - 440)
d.text(s, "headline", [(HEAD5, CREAM, False)], 72, H - 376, 936, 230, 60, lh=1.15)
d.text(s, "small-line", [(SMALL5, CREAM, False)], 72, H - 140, 936, 110, 42, font="Source Sans 3", lh=1.3)
d.write()

# ---------- side-by-side comparison ----------
rows = [("A  current", HERE)] + [(f"{k.upper()}  " + n, os.path.join(HERE, f"option-{k}")) for k, n in
                                 [("b", "deep green ground"), ("c", "the soil line"), ("d", "specimen sheet"), ("e", "one photo only")]]
tw, th, g = 300, 375, 18
cmp_ = Image.new("RGB", (60 + 5 * (tw + g) + 200, 40 + len(rows) * (th + 60)), (31, 31, 31)); dr = ImageDraw.Draw(cmp_)
from PIL import ImageFont
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
for r, (lab_, folder) in enumerate(rows):
    y = 30 + r * (th + 60); dr.text((30, y), lab_, font=f, fill=(240, 240, 240))
    for i in range(5):
        im = Image.open(os.path.join(folder, f"slide-{i + 1}.png")).convert("RGB").resize((tw, th), Image.LANCZOS)
        cmp_.paste(im, (30 + i * (tw + g), y + 40))
cmp_.crop((0, 0, 30 + 5 * (tw + g) + 12, cmp_.height)).save(os.path.join(HERE, "options-compare.png"))
print("done")
