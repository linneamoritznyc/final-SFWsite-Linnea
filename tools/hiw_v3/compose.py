#!/usr/bin/env python3
"""Lay out the six How It Works v3 thumbnails from the chosen Replicate art.

    python3 tools/hiw_v3/compose.py

Reads the artwork named in LAYOUT from docs/replicate-outputs/v3/, and writes:
  exports/stephanie/how-it-works/thumbnails/<topic>.jpg     1920x1080, < 400 KB
  exports/stephanie/how-it-works/layers/<topic>-art.png     artwork + leaf sprig
  exports/stephanie/how-it-works/layers/logo-green.png      logo layer
  exports/stephanie/how-it-works/how-it-works-thumbnails.pptx
  docs/how-it-works-thumbnails-final.png                    review sheet
Title: Montserrat Bold (Google Fonts), the same size on all six, SFW deep green
on the white art. Logo: the school logo recoloured to the same green.
"""
import io, math, os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "docs", "replicate-outputs", "v3")
HIW = os.path.join(ROOT, "exports", "stephanie", "how-it-works")
FONT = os.environ.get("MONTSERRAT_BOLD", os.path.expanduser("~/.fonts/Montserrat-Bold.ttf"))
W, H = 1920, 1080
MX, MY = round(W * 0.08), round(H * 0.08)          # 8% safe margin
GREEN = (21, 104, 38)                               # #156826
SAGE = (157, 184, 154)                              # pale sage sprig
TITLE_PX, LEADING = 92, 1.14
LOGO_H = 170

# art: raw file, drawn h px tall with its top-left at pos on the white field
# title: lines, anchor point, align; logo and sprig: top-left points; sprig angle
LAYOUT = [
    dict(slug="what-is-the-soil-food-web", title="What is the Soil Food Web?",
         art="1-what-is-the-soil-food-web-r3.png", h=1362, pos=(700, -277),
         lines=["What is the", "Soil Food", "Web?"], tx=MX, ty="mid", align="left",
         logo=(MX, MY), sprig=(250, 700, -15)),
    dict(slug="nutrient-cycling", title="Nutrient Cycling",
         art="2-nutrient-cycling-r1-clean.png", h=H, pos=(0, 0),
         lines=["Nutrient", "Cycling"], tx=MX, ty="bottom", align="left",
         logo=(W - MX - 196, MY), sprig=(1560, 700, 10)),
    dict(slug="formation-of-structure", title="Formation of Structure",
         art="3-formation-of-structure-r1.png", h=H, pos=(-96, 0),
         lines=["Formation of", "Structure"], tx=W - MX, ty="top", align="right",
         logo=(W - MX - 196, H - MY - LOGO_H), sprig=(1360, 470, 5)),
    dict(slug="weed-suppression", title="Weed Suppression",
         art="4-weed-suppression-r2.png", h=H, pos=(520, 0),
         lines=["Weed", "Suppression"], tx=MX, ty="top", align="left",
         logo=(MX, H - MY - LOGO_H), sprig=(380, 420, -20)),
    dict(slug="inhibiting-pests-and-diseases", title="Inhibiting Pests & Diseases",
         art="5-inhibiting-pests-and-diseases-r3.png", h=1300, pos=(-60, -230),
         lines=["Inhibiting Pests", "& Diseases"], tx=W - MX, ty="bottom", align="right",
         logo=(MX, MY), sprig=(420, 80, 15)),
    dict(slug="sequestering-carbon", title="Sequestering Carbon",
         art="6-sequestering-carbon-r2.png", h=H, pos=(0, 0),
         lines=["Sequestering", "Carbon"], tx=MX, ty="bottom", align="left",
         logo=(W - MX - 196, MY), sprig=(1080, 110, 20)),
]


def font():
    return ImageFont.truetype(FONT, TITLE_PX)


def art_layer(spec):
    im = Image.open(os.path.join(RAW, spec["art"])).convert("RGB")
    s = spec["h"] / im.height
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), "white")
    canvas.paste(im, spec["pos"])
    return canvas


def sprig(angle):
    """A slim pale sage vine with leaves and three small fan flowers, as in the logo."""
    k = 4
    S = 300 * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(S * 0.12 + S * 0.76 * t, S * 0.55 - math.sin(t * math.pi) * S * 0.16 + t * S * 0.1)
           for t in [i / 60 for i in range(61)]]
    d.line(pts, fill=SAGE + (255,), width=4 * k, joint="curve")

    def leaf(cx, cy, ang, ln, wd):
        poly = []
        for i in range(41):
            t = i / 40 * 2 * math.pi
            x, y = math.cos(t) * ln / 2, math.sin(t) * wd / 2 * (1 - 0.35 * math.cos(t))
            poly.append((x, y))
        c, s_ = math.cos(ang), math.sin(ang)
        return [(cx + x * c - y * s_, cy + x * s_ + y * c) for x, y in poly]

    for j, (i, side) in enumerate([(14, -1), (24, 1), (34, -1), (44, 1), (56, 1)]):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        a = math.atan2(y1 - y0, x1 - x0) + side * 0.75
        ln = (52 if j < 4 else 64) * k
        cx, cy = x0 + math.cos(a) * ln * 0.5, y0 + math.sin(a) * ln * 0.5
        d.polygon(leaf(cx, cy, a, ln, ln * 0.42), fill=SAGE + (255,))
    for i, up in [(8, -1), (30, -1), (50, -1)]:
        x0, y0 = pts[i]
        d.line([(x0, y0), (x0, y0 + up * 18 * k)], fill=SAGE + (255,), width=3 * k)
        fx, fy = x0, y0 + up * 18 * k
        for p in range(5):
            a = -math.pi / 2 + (p - 2) * 0.42
            d.polygon(leaf(fx + math.cos(a) * 9 * k, fy + math.sin(a) * 9 * k, a, 20 * k, 9 * k),
                      fill=SAGE + (255,))
    im = im.resize((300, 300), Image.LANCZOS).rotate(angle, resample=Image.BICUBIC, expand=True)
    a = im.getchannel("A").point(lambda v: round(v * 0.7))
    im.putalpha(a)
    return im


def logo():
    src = Image.open(os.path.join(ROOT, "img", "brand", "sfw-school-logo-black.png")).convert("RGBA")
    green = Image.new("RGBA", src.size, GREEN + (255,))
    green.putalpha(src.getchannel("A"))
    w = round(src.width * LOGO_H / src.height)
    return green.resize((w, LOGO_H), Image.LANCZOS)


def title_box(spec):
    """Top-left of the title block, its size, and per-line x offsets."""
    f = font()
    lh = round(TITLE_PX * LEADING)
    widths = [f.getlength(t) for t in spec["lines"]]
    bw, bh = max(widths), lh * (len(spec["lines"]) - 1) + TITLE_PX
    x = {"left": spec["tx"], "right": spec["tx"] - bw, "center": spec["tx"] - bw / 2}[spec["align"]]
    y = {"top": MY, "bottom": H - MY - bh, "mid": (H - bh) / 2}[spec["ty"]]
    return x, y, bw, bh, lh, widths


def render(spec, art, lg):
    im = art.copy()
    d = ImageDraw.Draw(im)
    f = font()
    x, y, bw, bh, lh, widths = title_box(spec)
    for i, (t, w) in enumerate(zip(spec["lines"], widths)):
        lx = {"left": x, "right": x + bw - w, "center": x + (bw - w) / 2}[spec["align"]]
        # Montserrat cap height sits ~0.21 em below the ascender line
        d.text((lx, y + i * lh - TITLE_PX * 0.21), t, font=f, fill=GREEN)
    im.paste(lg, spec["logo"], lg)
    return im


def save_jpg(im, path):
    for q in range(92, 60, -3):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True, subsampling=0 if q > 85 else 2)
        if buf.tell() < 400 * 1024:
            break
    with open(path, "wb") as fh:
        fh.write(buf.getvalue())
    return q, buf.tell()


def pptx(specs):
    from pptx import Presentation
    from pptx.util import Emu, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
    px = 12192000 / W
    layers = os.path.join(HIW, "layers")
    for spec in specs:
        s = prs.slides.add_slide(prs.slide_layouts[6])
        s.shapes.add_picture(os.path.join(layers, spec["slug"] + "-art.png"), 0, 0,
                             prs.slide_width, prs.slide_height).name = "Artwork"
        lx, ly = spec["logo"]
        lg = Image.open(os.path.join(layers, "logo-green.png"))
        s.shapes.add_picture(os.path.join(layers, "logo-green.png"), Emu(round(lx * px)), Emu(round(ly * px)),
                             Emu(round(lg.width * px)), Emu(round(lg.height * px))).name = "Logo"
        x, y, bw, bh, lh, _ = title_box(spec)
        pad = 24
        tb = s.shapes.add_textbox(Emu(round((x - pad) * px)), Emu(round((y - TITLE_PX * 0.3) * px)),
                                  Emu(round((bw + 2 * pad) * px)), Emu(round((bh + TITLE_PX * 0.5) * px)))
        tb.name = "Title"
        tf = tb.text_frame
        tf.word_wrap = False
        tf.vertical_anchor = MSO_ANCHOR.TOP
        for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
            setattr(tf, m, 0)
        for i, line in enumerate(spec["lines"]):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER}[spec["align"]]
            p.line_spacing = Pt(lh * 0.5)
            r = p.add_run()
            r.text = line
            r.font.name = "Montserrat"
            r.font.bold = True
            r.font.size = Pt(TITLE_PX * 0.5)
            r.font.color.rgb = RGBColor(*GREEN)
        s.notes_slide.notes_text_frame.text = spec["title"]
    prs.save(os.path.join(HIW, "how-it-works-thumbnails.pptx"))


def sheet(specs):
    tw, th, g = 900, 506, 30
    f = ImageFont.truetype(FONT, 26)
    ims = [Image.open(os.path.join(HIW, "thumbnails", s["slug"] + ".jpg")) for s in specs]
    out = Image.new("RGB", (g + 3 * (tw + g), 2 * (th + 60) + 60 + 95 + 40), (244, 241, 234))
    d = ImageDraw.Draw(out)
    for i, (s, im) in enumerate(zip(specs, ims)):
        x, y = g + (i % 3) * (tw + g), 20 + (i // 3) * (th + 60)
        d.text((x, y), "%d  %s" % (i + 1, s["title"]), font=f, fill=(35, 31, 29))
        out.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 38))
        d.rectangle([x, y + 38, x + tw - 1, y + 38 + th - 1], outline=(210, 205, 195))
    y = 20 + 2 * (th + 60) + 10
    d.text((g, y), "At 168 px wide", font=f, fill=(35, 31, 29))
    for i, im in enumerate(ims):
        x = g + i * (168 + 20)
        out.paste(im.resize((168, 95), Image.LANCZOS), (x, y + 40))
        d.rectangle([x, y + 40, x + 167, y + 134], outline=(210, 205, 195))
    out.save(os.path.join(ROOT, "docs", "how-it-works-thumbnails-final.png"), optimize=True)


def main(specs=LAYOUT):
    os.makedirs(os.path.join(HIW, "thumbnails"), exist_ok=True)
    os.makedirs(os.path.join(HIW, "layers"), exist_ok=True)
    lg = logo()
    lg.save(os.path.join(HIW, "layers", "logo-green.png"))
    for spec in specs:
        art = art_layer(spec)
        sx, sy, sa = spec["sprig"]
        sp = sprig(sa)
        art.paste(sp, (sx, sy), sp)
        art.save(os.path.join(HIW, "layers", spec["slug"] + "-art.png"), optimize=True)
        q, n = save_jpg(render(spec, art, lg), os.path.join(HIW, "thumbnails", spec["slug"] + ".jpg"))
        print("%-32s q%d %d KB" % (spec["slug"], q, n // 1024))
    pptx(specs)
    sheet(specs)


if __name__ == "__main__":
    main()
