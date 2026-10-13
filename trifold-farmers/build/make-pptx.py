#!/usr/bin/env python3
"""Build an editable PowerPoint of the farmers trifold for Canva, from the
layers export-layers.js writes. Every band, box, hairline, photograph, icon,
QR code and text block is its own object, named, in paint order.

    node    trifold-farmers/build/export-layers.js <dir>
    python3 trifold-farmers/build/make-pptx.py <dir> [output .pptx]

Slides are the trim size, 11 x 8.5 in. Anything that bleeds runs 0.125 in
past the slide edge, as it does in the print file, so turn on "Show print
bleed" in Canva to see it.
"""
import json, re, sys, pathlib
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.oxml.ns import qn

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(__file__).resolve().parent.parent / "sfw-farmers-trifold-editable.pptx"
PX = 914400 / 96            # EMU per CSS pixel
BLEED = 0.125 * 96          # the sheet includes bleed; the slide is the trim

def emu(v): return Emu(int(round(v * PX)))

def rgba(s):
    m = re.match(r"rgba?\(([^)]+)\)", s or "")
    if not m: return None
    p = [float(x) for x in m.group(1).split(",")]
    return (int(p[0]), int(p[1]), int(p[2]), p[3] if len(p) > 3 else 1.0)

def clr_xml(c):
    r, g, b, a = c
    x = f'<a:srgbClr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="{r:02X}{g:02X}{b:02X}">'
    if a < 1: x += f'<a:alpha val="{int(a * 100000)}"/>'
    return x + "</a:srgbClr>"

def set_fill(shape, fill, image):
    spPr = shape._element.spPr
    for tag in ("a:solidFill", "a:gradFill", "a:noFill"):
        for e in spPr.findall(qn(tag)): spPr.remove(e)
    g = re.match(r"linear-gradient\((.*)\)", image or "")
    if g:
        parts = re.split(r",(?![^()]*\))", g.group(1))
        ang = 180.0
        if parts[0].strip().endswith("deg"): ang = float(parts[0].strip()[:-3]); parts = parts[1:]
        elif parts[0].strip().startswith("to "):
            ang = {"to bottom": 180, "to top": 0, "to right": 90, "to left": 270}[parts[0].strip()]; parts = parts[1:]
        stops = []
        for i, p in enumerate(parts):
            m = re.match(r"\s*(rgba?\([^)]+\))\s*([\d.]+%)?", p)
            if not m: continue
            pos = float(m.group(2)[:-1]) if m.group(2) else (0 if i == 0 else 100)
            stops.append((min(max(pos, 0), 100), rgba(m.group(1))))
        gs = "".join(f'<a:gs pos="{int(p * 1000)}">{clr_xml(c)}</a:gs>' for p, c in stops)
        ooxml_ang = int(((ang - 90) % 360) * 60000)
        xml = (f'<a:gradFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" rotWithShape="1">'
               f'<a:gsLst>{gs}</a:gsLst><a:lin ang="{ooxml_ang}" scaled="0"/></a:gradFill>')
    else:
        c = rgba(fill)
        if not c or c[3] == 0:
            xml = '<a:noFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>'
        else:
            xml = f'<a:solidFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">{clr_xml(c)}</a:solidFill>'
    el = etree.fromstring(xml)
    prst = spPr.find(qn("a:prstGeom"))
    prst.addnext(el)
    shape.line.fill.background()

prs = Presentation()
prs.slide_width, prs.slide_height = emu(11 * 96), emu(8.5 * 96)
layers = json.loads((SRC / "layers.json").read_text())
counts = {}
for sheet in ("outside", "inside"):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    n = {"rect": 0, "image": 0, "text": 0}
    for it in layers[sheet]:
        x, y, w, h = it["x"] - BLEED, it["y"] - BLEED, it["w"], it["h"]
        if w <= 0 or h <= 0: continue
        if it["kind"] == "rect":
            r = it.get("radius", 0)
            shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE,
                                         emu(x), emu(y), emu(w), emu(h))
            if r: shp.adjustments[0] = min(0.5, r / min(w, h))
            set_fill(shp, it["fill"], it.get("image"))
            shp.shadow.inherit = False
        elif it["kind"] == "image":
            shp = slide.shapes.add_picture(str(SRC / it["file"]), emu(x), emu(y), emu(w), emu(h))
        else:
            # A little extra measure so Canva's own line breaking does not
            # wrap a line early; text stays anchored at its left edge.
            shp = slide.shapes.add_textbox(emu(x), emu(y), emu(w * 1.06 + 3), emu(h))
            tf = shp.text_frame
            tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            para = tf.paragraphs[0]
            def style_para(p):
                p.alignment = {"center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT, "end": PP_ALIGN.RIGHT}.get(it["align"], PP_ALIGN.LEFT)
                if it.get("lineHeight"): p.line_spacing = Pt(it["lineHeight"])
            style_para(para)
            if it.get("indent"):
                para._p.get_or_add_pPr().set("indent", str(int(it["indent"] * PX)))
            for run in it["runs"]:
                if run["text"] == "\n":
                    para = tf.add_paragraph(); style_para(para); continue
                rr = para.add_run(); rr.text = run["text"]
                f = rr.font
                f.name = run["font"]; f.size = Pt(round(run["size"] * 2) / 2)
                f.bold = run["weight"] >= 600; f.italic = run["italic"]
                c = rgba(run["color"])
                rPr = rr._r.get_or_add_rPr()
                if c:
                    # The fill has to come before the font elements in a:rPr,
                    # or the file is invalid and PowerPoint asks to repair it.
                    sf = etree.Element(qn("a:solidFill")); sf.append(etree.fromstring(clr_xml(c)))
                    rPr.insert(0, sf)
                if run.get("spacing"): rPr.set("spc", str(int(run["spacing"] * 100)))
        shp.name = f'{it["kind"]}: {it["name"]}'[:80]
        n[it["kind"]] += 1
    counts[sheet] = n
prs.save(OUT)
for s, n in counts.items():
    print(f"{s}: {n['rect']} shapes, {n['image']} images, {n['text']} text boxes")
print("wrote", OUT)
