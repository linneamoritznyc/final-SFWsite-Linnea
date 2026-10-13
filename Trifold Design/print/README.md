# Print files

Soil Food Web Foundation trifold, 2026 event brochure.

**Do not send anything from this folder.** The two files for the print shop are
in `SEND-TO-PRINTER/` at the top of the repository, copied there by
`build/assemble-delivery.py`.

This folder is build output. `sfw-trifold-2page-CMYK-PDFX.pdf` is the master
that gets copied; `alternates/` holds the X-1a versions, the single-sheet
separates and the RGB source PDFs, none of which anyone needs unless a shop
specifically asks. `PRINT-SPEC.md` is the one-page spec, deliberately short; the
background a shop does not need, but we might, is in this README.

## Send this one

**`sfw-trifold-2page-CMYK-PDFX.pdf`** — both sheets, outside as page 1, inside as
page 2. PDF/X-4, CMYK, trim and bleed marked. Type, rules and all five QR codes
are live vector.

| File | |
| :-- | :-- |
| `sfw-trifold-2page-CMYK-PDFX.pdf` | **The file to send.** X-4, 2 pages |
| `sfw-trifold-outside-CMYK-PDFX.pdf` | X-4 separate, outside |
| `sfw-trifold-inside-CMYK-PDFX.pdf` | X-4 separate, inside |
| `sfw-trifold-2page-CMYK-PDFX1a.pdf` | X-1a, 2 pages. Only if the shop asks |
| `sfw-trifold-outside-CMYK-PDFX1a.pdf` | X-1a separate, outside |
| `sfw-trifold-inside-CMYK-PDFX1a.pdf` | X-1a separate, inside |
| `sfw-trifold-{outside,inside}.pdf` | RGB, before colour conversion. Reference only |

## Specification

- **Trim** 11 x 8.5in, letter, roll fold. The tuck panel is 1/16in narrower.
- **Bleed** 0.125in all four sides. Page 11.25 x 8.75in (810 x 630pt).
- **TrimBox** 9 9 801 621pt. **BleedBox** and **MediaBox** 0 0 810 630pt.
- No drawn crop marks: the boxes carry the trim. Ask if your workflow wants
  visible marks and a slug.
- CMYK throughout, embedded output intent, fonts embedded and subsetted.
- Photographs 400 to 800 ppi in the X-4 files. Nothing is downsampled.

## Imposition

**The two sheets are mirrored, on purpose.** A roll fold has one narrow tuck
panel, so that panel sits on the right of one side of the sheet and the left of
the other. Printed with the narrow panel on the same side of both, every panel
would be 1/4in out of register with its own back.

| sheet | left to right | folds from its own left trim |
| :-- | :-- | :-- |
| page 1, outside | Teaching (**tuck**, 3.5in), Community, Cover | 3.5in, 7.25in |
| page 2, inside | Our story, Research, Practice (**tuck**, 3.5in) | 3.75in, 7.5in |

Each fold mirrors the other. Practice folds in first, Our story folds over it,
and the Cover lands face up. Community is the back of the folded piece, which
is where the donation code sits.

## Folding one by hand

`HOME-PROOF-cut-and-fold.pdf` is a separate two-page proof for a desktop
printer: the trimmed artwork at 94.2%, with a cut outline, corner crop marks and
labelled fold ticks. Print at 100%, not fit-to-page. It is not for the press.

    python3 "Trifold Design/build/make-home-proof.py"

## X-4 or X-1a

**X-4 is the better file and the one to send.** It keeps live transparency, so
nothing is flattened and every vector stays a vector, the QR codes included.

**X-1a is a fallback for shops that require it, and it is rasterised.** That is
the standard, not a choice made here: X-1a forbids live transparency, this
design has rgba fills and gradient fades over photographs, so the sheet has to
be flattened, and flattening rasterises it. It is flattened at 600 DPI, twice
what a press needs, and every code was decoded out of the finished file before
it shipped. Expect preflight to describe it as image-only; that is what it is.

## Two things worth knowing

**The output intent is a generic CMYK profile**, not a press condition. There is
no licensed FOGRA or SWOP profile in this repository, and naming one we had not
converted through would be worse than declaring a generic one. Re-target it.

**A few small images per sheet in the X-4 files are low resolution, and that is
correct.** They are the colour gradients behind the panel headers; the browser
writes them as shading patterns and Ghostscript converts pattern fills to images
whatever it is told. The largest lands near 45ppi. They are smooth two-colour
ramps with no detail and are marked `/Interpolate` so the RIP smooths rather
than steps them. Preflight will flag them.

## Rebuilding

    python3 "Trifold Design/build/make-qr.py"        # the codes
    node    "Trifold Design/build/render.js"         # 300 DPI PNG proofs
    python3 "Trifold Design/build/check-qr.py"       # decode them back out
    node    "Trifold Design/build/render-pdf.js"     # vector PDFs
    python3 "Trifold Design/build/make-pdfx.py"      # X-4 and X-1a, separates and merged
    python3 "Trifold Design/build/check-qr.py" "Trifold Design/print/sfw-trifold-2page-CMYK-PDFX.pdf"
    python3 "Trifold Design/build/assemble-delivery.py"

`check-qr.py` takes any built PDF and fails if a code does not decode. Run it on
whatever you are about to send; it has caught four real faults so far.
