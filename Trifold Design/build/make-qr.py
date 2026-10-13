#!/usr/bin/env python3
"""Generate the five QR codes for the trifold, and the standalone PNGs.

Each code carries a Switchy short link, not the destination. Three reasons,
and the first two are the important ones:

  1. A printed code cannot be changed. The short link can, so a destination
     that moves, or a rebuilt site that renames a path, is a redirect edit
     rather than a reprint. This brochure has already had three addresses go
     404 under it once.
  2. Short payloads mean few modules, and few modules mean each module is
     physically large enough to survive press. These fit at error correction
     H with room to spare; the long URLs with UTM tails did not.
  3. The UTM parameters ride on the redirect, so the campaign reporting is
     unchanged and none of it costs modules here.

Each code takes its own panel's colour, on white, at error correction H with
four modules of quiet zone.

The colours are gated, but by a scan test rather than a contrast rule. An
earlier version of this file used a WCAG contrast threshold of 4.5:1, which is
a readability figure for text and turns out to be far too strict for a QR code
at this size: it rejected Education Blue #3780B8 at 4.25:1 and the brand gold
#C9A227 at 2.42:1, and both of those decode reliably at error correction H with
0.649mm modules. A code IS readable or it is not, and that is measurable, so
every colour is now rendered at its printed size, degraded to simulate ink
spread and a phone camera, and decoded. If it does not come back, the build
stops. The deep ends of the gradients survive about twice as much blur, so if a
proof off the press ever disappoints, they are the fallback.

    python3 "Trifold Design/build/make-qr.py"
    python3 "Trifold Design/build/check-qr.py"   # decodes them back out
"""
import pathlib
import segno

HERE = pathlib.Path(__file__).parent
SVG_OUT = HERE / "qr"                                   # placed in the artwork
PNG_OUT = HERE.parent.parent / "exports" / "qr"         # standalone, for reuse
SVG_OUT.mkdir(exist_ok=True)
PNG_OUT.mkdir(parents=True, exist_ok=True)

LIGHT = "#FFFFFF"   # every code keeps its own white ground, whatever it sits on
ECC = "h"           # 30% recoverable: survives a crease, a thumb, a bad press day
QUIET = 4           # modules of quiet zone on every side, the spec minimum


def contrast_on_white(hex_colour):
    """WCAG contrast ratio against white. Reported, not enforced: see above."""
    ch = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    ch = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 1.05 / (0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2] + 0.05)


def survives_a_press(url, colour, mm=1.15 * 25.4):
    """Render at printed size, add ink spread and a phone camera, decode it.

    Returns the worst Gaussian blur, in pixels at 300 DPI, the code still reads
    through. Anything that fails even the gentlest pass is not printable.
    """
    import io
    import cv2
    import numpy as np
    from PIL import Image, ImageFilter

    px = int(mm / 25.4 * 300)
    buf = io.BytesIO()
    segno.make(url, error=ECC).save(buf, kind="png", scale=20, border=QUIET,
                                    dark=colour, light=LIGHT)
    art = Image.open(buf).convert("RGB").resize((px, px), Image.LANCZOS)
    rng = np.random.default_rng(3)
    det = cv2.QRCodeDetector()
    worst = 0.0
    for blur in (0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8):
        a = np.asarray(art.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32)
        a = np.clip(a + rng.normal(0, 8, a.shape), 0, 255).astype(np.uint8)
        shot = Image.fromarray(a).resize((int(px * 0.45),) * 2, Image.LANCZOS)
        if det.detectAndDecode(np.array(shot))[0] == url:
            worst = blur
    return worst

# One colour per code, each taken from the panel it stands on. Tokens are
# css/site.css section 1, same as the rest of the piece.
CODES = {
    # name            short link                                    PNG name       colour
    "webinar":      ("https://www.sfw.one/brochure-webinar",     "webinar",     "#6B4C7A"),  # --legacy, the Dr. Elaine panel
    "courses":      ("https://www.sfw.one/brochure-courses",     "courses",     "#3780B8"),  # --edu, the teaching panel
    "case-studies": ("https://www.sfw.one/brochure-casestudies", "casestudies", "#156826"),  # --green, the practice panel
    "website":      ("https://www.sfw.one/brochure-website",     "website",     "#22371F"),  # --moss, the deep end of the community field
    "donate":       ("https://www.sfw.one/brochure-donate",      "donate",      "#C9A227"),  # --gold, the donate accent
}

# The placed codes are 1.15in square including their quiet zone. Anything at or
# above 2cm is fine for print; this is 29.2mm.
PLACED_MM = 1.15 * 25.4

unreadable = [(n, c) for n, (u, _, c) in CODES.items() if not survives_a_press(u, c)]
if unreadable:
    raise SystemExit("colour does not survive a press: " + ", ".join(
        f"{n} {c}" for n, c in unreadable))

print(f"{'code':<14}{'colour':<9}{'contrast':>9}{'blur ok':>9}{'ver':>4}{'modules':>9}{'mm/module':>11}   payload")
for name, (url, png_name, DARK) in CODES.items():
    qr = segno.make(url, error=ECC)
    modules = qr.symbol_size(scale=1, border=QUIET)[0]

    # Vector for the artwork: no resolution to get wrong at the printer.
    qr.save(SVG_OUT / f"{name}.svg", scale=10, border=QUIET,
            dark=DARK, light=LIGHT)

    # Standalone raster, comfortably over 1200px on the short side.
    scale = -(-1200 // modules)          # ceiling division
    qr.save(PNG_OUT / f"sfw-brochure-qr-{png_name}.png", scale=scale,
            border=QUIET, dark=DARK, light=LIGHT)

    print(f"{name:<14}{DARK:<9}{contrast_on_white(DARK):>8.2f}:1"
          f"{survives_a_press(url, DARK):>8.1f}px{qr.version:>4}"
          f"{modules:>9}{PLACED_MM/modules:>10.3f}   {url}")
