#!/usr/bin/env python3
"""A proof to print, cut and fold at home.

    python3 "Trifold Design/build/make-home-proof.py"

The press file has no crop or fold marks, because a shop reads the TrimBox.
Folding one at a kitchen table means guessing where 3.75in falls on a sheet you
have cut by hand, and a fold a couple of millimetres out is the difference
between a flap that tucks and a flap that needs scissors.

So: the trimmed artwork, scaled to fit inside what a desktop printer can
actually reach, with corner crop marks and fold ticks in the margin. Print at
100%, not "fit to page", or the marks stop meaning anything.
"""
import pathlib, subprocess, json
from PIL import Image

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "print"
DPI, BLEED = 300, 0.125
TRIM_W, TRIM_H = 11.0, 8.5
MARGIN = 0.32          # what a desktop printer will not print inside
PAGE_W, PAGE_H = 11.0, 8.5
SCALE = (PAGE_W - 2 * MARGIN) / TRIM_W

FOLDS = {"outside": [3.5, 7.25], "inside": [3.75, 7.5]}
TITLE = {"outside": "SIDE 1 of 2: cover side. Print at 100%, not fit-to-page.",
         "inside":  "SIDE 2 of 2: print on the back of side 1, same edge first."}

def trimmed(name):
    """The bleed cut off, which is what a person with scissors ends up with."""
    im = Image.open(HERE.parent / f"{name}-spread.png")
    b = int(BLEED * DPI)
    out = HERE.parent / "print" / f".home-{name}.png"
    im.crop((b, b, im.width - b, im.height - b)).save(out)
    return out

def page(name):
    w, h = TRIM_W * SCALE, TRIM_H * SCALE
    x0, y0 = (PAGE_W - w) / 2, (PAGE_H - h) / 2
    marks = []
    for fold in FOLDS[name]:
        fx = x0 + fold * SCALE
        marks.append(f'<div class="tick" style="left:{fx}in; top:{y0 - 0.22}in"></div>')
        marks.append(f'<div class="tick" style="left:{fx}in; top:{y0 + h + 0.04}in"></div>')
        marks.append(f'<div class="lbl" style="left:{fx + 0.04}in; top:{y0 + h + 0.10}in">'
                     f'fold {fold}"</div>')
    for cx in (x0, x0 + w):
        for cy in (y0, y0 + h):
            marks.append(f'<div class="cropv" style="left:{cx}in; top:{cy - 0.20}in"></div>')
            marks.append(f'<div class="croph" style="left:{cx - 0.20}in; top:{cy}in"></div>')
    return f"""<section>
  <img src="{trimmed(name).name}" style="left:{x0}in; top:{y0}in; width:{w}in; height:{h}in">
  <div class="cut" style="left:{x0}in; top:{y0}in; width:{w}in; height:{h}in"></div>
  {''.join(marks)}
  <div class="title" style="left:{x0}in; top:{y0 - 0.26}in">{TITLE[name]}</div>
</section>"""

html = f"""<!doctype html><meta charset="utf-8">
<style>
  @page {{ size: {PAGE_W}in {PAGE_H}in; margin: 0; }}
  html, body {{ margin: 0; padding: 0; }}
  section {{ position: relative; width: {PAGE_W}in; height: {PAGE_H}in;
             page-break-after: always; overflow: hidden; }}
  img {{ position: absolute; }}
  .cut {{ position: absolute; outline: 0.5pt dashed #C00; }}
  .tick {{ position: absolute; width: 0; height: 0.18in; border-left: 0.5pt dashed #C00; }}
  .cropv {{ position: absolute; width: 0; height: 0.20in; border-left: 0.5pt solid #C00; }}
  .croph {{ position: absolute; width: 0.20in; height: 0; border-top: 0.5pt solid #C00; }}
  .lbl, .title {{ position: absolute; font: 7pt/1 Helvetica, Arial, sans-serif; color: #C00; }}
</style>
{page('outside')}
{page('inside')}"""

(OUT / ".home-proof.html").write_text(html)
subprocess.run(["node", str(HERE / "render-home-proof.js")], check=True,
               cwd=HERE.parent.parent)
for f in OUT.glob(".home-*"):
    f.unlink()
print(f"print/HOME-PROOF-cut-and-fold.pdf   scaled to {SCALE:.1%}")
