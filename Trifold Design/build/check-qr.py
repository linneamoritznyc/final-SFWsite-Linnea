#!/usr/bin/env python3
"""Decode every QR code out of a rendered sheet, and fail if any does not read.

    python3 "Trifold Design/build/check-qr.py"                      the PNG proofs
    python3 "Trifold Design/build/check-qr.py" path/to/file.pdf ...  any built PDF

Nothing else in this build catches a dead code: the artwork looks perfectly
correct with one on it. This has already found four real faults. A code set in
Education Blue that a decoder could not read at all; codes on the colour panels
set 0.11in smaller than the rest, which put them under the print minimum for
module size; Ghostscript's -dPDFX switch flattening the sheet to a single
raster; and the merged and X-1a files, which are checked here for the same
reason rather than assumed to be fine because their source was.

For a PDF, page 1 is the outside sheet and page 2 the inside. A single-page PDF
is matched by its filename.

Needs opencv-python-headless and poppler-utils.
"""
import json, pathlib, subprocess, sys, tempfile
import cv2, numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = pathlib.Path(__file__).parent
SPREADS = HERE.parent
DPI = 600


def boxes():
    """Where each code sits, in CSS pixels, from the live page."""
    return json.loads(subprocess.run(
        ["node", str(HERE / "qr-boxes.js")], capture_output=True, text=True,
        cwd=SPREADS.parent, check=True).stdout)


def sheets_of(pdf):
    """Which sheet each page of this PDF holds."""
    n = int(subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True,
                           check=True).stdout.split("Pages:")[1].split()[0])
    if n == 2:
        return {1: "outside", 2: "inside"}
    name = pdf.name.lower()
    for s in ("outside", "inside"):
        if s in name:
            return {1: s}
    sys.exit(f"{pdf.name}: {n} page(s) and no sheet in the filename")


def decode(img, box, scale):
    pad = 10
    crop = img.crop((int(box["x"] * scale) - pad, int(box["y"] * scale) - pad,
                     int((box["x"] + box["w"]) * scale) + pad,
                     int((box["y"] + box["h"]) * scale) + pad))
    return cv2.QRCodeDetector().detectAndDecode(np.array(crop))[0]


def main():
    where = boxes()
    targets = [pathlib.Path(a) for a in sys.argv[1:]]
    failures, checked = [], 0

    with tempfile.TemporaryDirectory() as tmp:
        jobs = []
        if targets:
            for pdf in targets:
                if not pdf.exists():
                    sys.exit(f"no such file: {pdf}")
                for page, sheet in sheets_of(pdf).items():
                    out = pathlib.Path(tmp) / f"{pdf.stem}-{page}"
                    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", "-singlefile",
                                    "-f", str(page), "-l", str(page), str(pdf), str(out)],
                                   check=True)
                    jobs.append((f"{pdf.name} p{page}", sheet,
                                 Image.open(f"{out}.png").convert("RGB"), DPI / 96))
        else:
            for sheet in ("outside", "inside"):
                jobs.append((f"{sheet}-spread.png", sheet,
                             Image.open(SPREADS / f"{sheet}-spread.png").convert("RGB"),
                             300 / 96))

        for label, sheet, img, scale in jobs:
            for box in where[sheet]:
                url = decode(img, box, scale)
                checked += 1
                print(f"  {label:<44}{box['src'].split('/')[-1]:<20}"
                      f"{'ok  ' if url else 'FAIL'}  {url}")
                if not url:
                    failures.append(f"{label} {box['src']}")

    if failures:
        sys.exit("could not decode: " + ", ".join(failures))
    print(f"all {checked} codes decode")


if __name__ == "__main__":
    main()
