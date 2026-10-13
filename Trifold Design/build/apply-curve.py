#!/usr/bin/env python3
"""Clip the six photographs to one curve drawn across the sheet.

Each picture is clipped by the segment of a single curve that falls in its own
panel, so the lower edges join into one line across both folds rather than
three repeated arcs.

The maths has to happen in SHEET coordinates, not per image. The cover's
photograph starts higher than the other five, because that panel carries the
wordmark where the others carry a colour band, so the same percentage means a
different height on the page. Positions come from build/measure-figs.js rather
than from reading the CSS, so this stays correct if the band or photo height
moves.

    node "Trifold Design/build/measure-figs.js"      # what the numbers are
    python3 "Trifold Design/build/apply-curve.py"    # apply them
    node "Trifold Design/build/render.js"
"""
import json, math, re, subprocess, pathlib

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent.parent

raw = subprocess.run(["node", str(HERE / "measure-figs.js")],
                     capture_output=True, text=True, cwd=REPO, check=True).stdout
sheets = {}
for line in raw.strip().splitlines():
    name, payload = line.split(" ", 1)
    sheets[name] = json.loads(payload)

# The curve is a FRACTION OF EACH FRAME, not a line at a fixed height on the
# sheet, and that distinction is the whole correctness of this file.
#
# It was written in sheet coordinates, clamped to stay inside every photograph
# on both sheets. Five of the six panels open with the colour band and so carry
# their picture at exactly the same height; the cover opens with the masthead
# instead and carries its picture about six tenths of an inch higher. Holding
# one sheet-space line inside the cover's frame as well therefore dragged the
# line up into the top half of the other five, and they were left showing about
# a third of their picture with a dead band of panel colour beneath it. The
# shorter the photographs got, the worse it read.
#
# Taking the same fractional curve in every frame fixes both ends of that. The
# five banner panels share a top and a height, so an identical fraction is an
# identical height on the sheet: the line still runs unbroken across both folds,
# which is the point of it. The cover gets the same shape inside its own taller
# frame rather than dictating the curve for everyone else, and every panel keeps
# at least KEEP of its picture.
KEEP = 0.75   # the least of a frame the trough may leave

def frac(x):
    """How much of the frame the curve keeps at x, x being 0 to 1 across the sheet.

    Clamped, because the bleeding photographs now overshoot the sheet by
    --overshoot and so start a little below 0 and end a little above 1. A
    negative base to a fractional power is a complex number in Python, which is
    how that first showed up."""
    x = max(0.0, min(1.0, x))
    return KEEP + (1.0 - KEEP) * math.sin(math.pi * (x ** 0.92))

def clip(p, n=64):
    pts = ["0% 0%", "100% 0%"]
    for i in range(n, -1, -1):
        u = i / n
        y = frac(p["imgX0"] + u * (p["imgX1"] - p["imgX0"]))
        pts.append(f"{u*100:.2f}% {max(0.0, min(1.0, y))*100:.2f}%")
    return "clip-path: polygon(" + ", ".join(pts) + ")"

FIG = re.compile(r'(<figure class="figure figure--full[^"]*"[^>]*>\s*<img [^>]*?)(style="([^"]*)")?(>)')
for name, panels in sheets.items():
    f = HERE / f"{name}.html"
    s = re.sub(r';?\s*clip-path: polygon\([^)]*\)', '', f.read_text())
    out, last = [], 0
    for m, panel in zip(FIG.finditer(s), panels):
        keep = (m.group(3) or "").strip().rstrip(";").strip()
        style = (keep + "; " if keep else "") + clip(panel)
        out.append(s[last:m.start()]); out.append(m.group(1) + f'style="{style}"' + m.group(4))
        last = m.end()
    out.append(s[last:])
    f.write_text("".join(out))
    print(f"{name}: each frame kept from {KEEP:.0%} at the outer edges "
          f"to 100% at the crest")
