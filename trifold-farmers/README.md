# Trifold for farmers

The first trifold's sheet, panels, fold, bleed, type and colours by position,
with the farmers copy. First use: Farm Aid "Homegrown 101," Virginia Beach,
September 26, 2026.

**Status: print-ready.** Every panel fits, every eyebrow and headline lines up,
the green feet on the back and cover meet across the fold, and all five QR
codes decode from the print file.

## The files

| File | What it is |
| :-- | :-- |
| `print/sfw-farmers-trifold-2page-CMYK-PDFX.pdf` | **The file to send.** Page 1 outside, page 2 inside. PDF/X-4, CMYK, 0.125 in bleed, same boxes as the first trifold's file. |
| `sfw-farmers-trifold-editable.pptx` | For Canva. Every band, box, hairline, photograph, icon, QR code and text block is its own object. |
| `COPY-farmers-trifold.txt` | Every word, panel by panel, generated from the final sheets. |
| `outside-spread.png`, `inside-spread.png` | 300 DPI previews with bleed. `final-page-*.jpg` are the print file itself. |
| `qr-uploads/` | QR files Linnea uploaded. |
| `build/` | The sheets, the stylesheet, and the build scripts. |

The first trifold's editable PowerPoint is in `../editable-pptx/`.

## Where it differs from the first trifold's layout

All additions sit at the foot of `build/trifold.css`; everything above them is
the first trifold's stylesheet.

- Cover subheadline in green at about half the headline size.
- Why Biology flap body and Our story box at 8.8 pt, so the flap fills.
- On your farm list and box text slightly larger, so the panel fills.
- Back: the gaps around the community code one step tighter, so its green foot meets the cover's. Both feet are 2.98 in tall rather than 2.80 in.
- The photograph curve rises across the sheet rather than arching, so the cover photograph reaches its right edge.

## Before print

- The Switchy links (brochure-webinar, -casestudies, -scholarship, -community, -website) must be live.
- Scan the codes on the press proof.

## Rebuild

From the repository root:

    python3 trifold-farmers/build/make-qr.py
    python3 trifold-farmers/build/apply-curve.py
    node    trifold-farmers/build/render.js
    node    trifold-farmers/build/render-pdf.js
    python3 trifold-farmers/build/make-pdfx.py
    python3 trifold-farmers/build/check-qr.py
    node    trifold-farmers/build/export-layers.js <tmp dir>
    python3 trifold-farmers/build/make-pptx.py <tmp dir>

The first trifold's PowerPoint:

    node    trifold-farmers/build/export-layers.js <tmp dir> "Trifold Design/build"
    python3 trifold-farmers/build/make-pptx.py <tmp dir> editable-pptx/sfw-trifold-2026-editable.pptx
