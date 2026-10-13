# SFW 2026 event brochure, final files

Everything for the trifold, in one place, named so it is obvious what each file
is. Rebuild with `python3 "Trifold Design/build/assemble-delivery.py"`, which
deletes this folder and copies the current build back in, so it can never hold a
stale file that quietly disagrees with the artwork.

**Download everything: `sfw-brochure-2026-all.zip`**

## For the printer

**Send `sfw-trifold-2page-CMYK-PDFX.pdf`.** One file, outside as page 1 and
inside as page 2.

| File | |
| :-- | :-- |
| `sfw-trifold-2page-CMYK-PDFX.pdf` | **The file to send.** X-4, both sheets |
| `sfw-trifold-outside-CMYK-PDFX.pdf` | X-4 separate, outside |
| `sfw-trifold-inside-CMYK-PDFX.pdf` | X-4 separate, inside |
| `sfw-trifold-2page-CMYK-PDFX1a.pdf` | X-1a, both sheets. Only if the shop asks for X-1a; it is rasterised at 600 DPI, because X-1a forbids the live transparency this design uses |

The two sheets are mirrored on purpose: a roll fold has one narrow tuck panel,
so it sits on the left of one side of the sheet and the right of the other.

PDF 1.6, PDF/X-4, CMYK with an embedded output intent. Page 810 x 630pt
(11.25 x 8.75in). TrimBox 9 9 801 621pt, so the 0.125in bleed is marked on all
four sides. Fonts embedded and subsetted. Type, rules and all five QR codes are
vector; photographs are 400 to 800 ppi and nothing is downsampled.

Two notes for them are in `Trifold Design/print/README.md`: the output intent is
a generic CMYK profile and should be re-targeted to their own press condition,
and a handful of small images per sheet are low resolution on purpose. Those are
the smooth colour ramps behind the panel headers, and they are marked
`/Interpolate` so a RIP smooths rather than steps them.

## To look at

| File | |
| :-- | :-- |
| `sfw-trifold-outside-300dpi.png` | 3375 x 2625px, 11.25 x 8.75in at 300 DPI |
| `sfw-trifold-inside-300dpi.png` | same |

## The QR codes on their own

1215 x 1215px, coloured ink on white, error correction H, four modules of quiet
zone. Each holds a Switchy short link, so a destination can be repointed later
without reprinting.

| File | Encodes | Ink |
| :-- | :-- | :-- |
| `sfw-brochure-qr-webinar.png` | `https://www.sfw.one/brochure-webinar` | `#6B4C7A` Legacy Purple |
| `sfw-brochure-qr-courses.png` | `https://www.sfw.one/brochure-courses` | `#3780B8` Education Blue |
| `sfw-brochure-qr-casestudies.png` | `https://www.sfw.one/brochure-casestudies` | `#156826` Food Web Green |
| `sfw-brochure-qr-website.png` | `https://www.sfw.one/brochure-website` | `#22371F` Moss |
| `sfw-brochure-qr-donate.png` | `https://www.sfw.one/brochure-donate` | `#C9A227` Gold |

Every one was decoded out of the delivered PNG, again out of the zip, and again
out of the CMYK PDF, and matched its link exactly.

**Check the gold first on a press proof.** Blur tolerance runs from 2.4px on the
website code down to 1.2px on the gold, which is the lightest ink and has the
least margin. If it disappoints, `#8A6E15` still reads as gold and survives
about twice the blur.
