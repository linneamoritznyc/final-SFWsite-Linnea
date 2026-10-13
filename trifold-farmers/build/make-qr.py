#!/usr/bin/env python3
"""The one new code on the farmers trifold: the back panel's link to the website.

soilfoodweb-qr.png was named in the brief but is not in the repository, so it
is made here, the same way the first trifold makes its codes (Trifold
Design/build/make-qr.py): error correction H, four modules of quiet zone, the
panel's own colour on white. The SVG is what the artwork places, so the code
stays vector in the PDF; the PNG is the standalone copy under the brief's name.

The case studies code is not made here. It is the first trifold's own file,
copied byte for byte into build/qr/.

    python3 trifold-farmers/build/make-qr.py
"""
import pathlib
import segno

HERE = pathlib.Path(__file__).parent
URL = "https://www.sfw.one/brochure-website"   # the tracked Switchy link Linnea uploaded (qr-uploads/)
DARK, LIGHT = "#22371F", "#FFFFFF"   # --moss, as the website code on the first trifold's Community panel

qr = segno.make(URL, error="h")
qr.save(HERE / "qr" / "brochure-website.svg", scale=10, border=4, dark=DARK, light=LIGHT)
modules = qr.symbol_size(scale=1, border=4)[0]
qr.save(HERE / "qr" / "brochure-website.png", scale=-(-1200 // modules), border=4, dark=DARK, light=LIGHT)
print(f"brochure-website  version {qr.version}, {modules} modules, {URL}")


# The three codes whose panels changed colour. Each takes the colour of the
# panel it now sits in, by position, as the first trifold does. Same links as
# the first trifold's codes.
for name, url, colour in (
    ("webinar-blue",       "https://www.sfw.one/brochure-webinar",     "#3780B8"),  # --edu, first flap
    ("case-studies-purple","https://www.sfw.one/brochure-casestudies", "#6B4C7A"),  # --legacy, inside left
    ("scholarship-green",  "https://www.sfw.one/brochure-scholarship", "#156826"),  # --green, inside right
):
    q = segno.make(url, error="h")
    q.save(HERE / "qr" / f"{name}.svg", scale=10, border=4, dark=colour, light=LIGHT)
    print(f"{name:<20} {colour}  {url}")
