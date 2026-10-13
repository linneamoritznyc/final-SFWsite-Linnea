#!/usr/bin/env python3
"""Put the downloads where a person can find them, named so there is no choice
to make.

    python3 "Trifold Design/build/assemble-delivery.py"

Two folders, and they answer two different questions.

    SEND-TO-PRINTER/        what goes to the print shop. Two files, no options.
    exports/brochure-2026/  everything else: proofs, the QR codes, a zip.

Both are copies, rebuilt from scratch each run, so neither can hold a stale file
that quietly disagrees with the artwork. The build outputs themselves live in
Trifold Design/print/, with the formats nobody asked for under alternates/.
"""
import hashlib, pathlib, shutil, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "exports" / "brochure-2026"
SEND = ROOT / "SEND-TO-PRINTER"
TRI = ROOT / "Trifold Design"

# The two files the print shop gets, and nothing else in the folder with them.
SEND_FILES = {
    "SFW-brochure-2026-print-ready.pdf": TRI / "print/sfw-trifold-2page-CMYK-PDFX.pdf",
    "PRINT-SPEC.md":                     TRI / "print/PRINT-SPEC.md",
    # The same two pages as pictures, for looking at and sharing. Named
    # "preview" so nobody mistakes them for artwork: a printer given a PNG has
    # no bleed box, no trim box, no CMYK and no vector type.
    "preview-page-1-outside.png":        TRI / "outside-spread.png",
    "preview-page-2-inside.png":         TRI / "inside-spread.png",
}

FILES = {
    # proofs, for looking at and for anyone who wants a picture
    "sfw-trifold-outside-300dpi.png":    TRI / "outside-spread.png",
    "sfw-trifold-inside-300dpi.png":     TRI / "inside-spread.png",
    # the codes on their own
    "sfw-brochure-qr-webinar.png":       ROOT / "exports/qr/sfw-brochure-qr-webinar.png",
    "sfw-brochure-qr-courses.png":       ROOT / "exports/qr/sfw-brochure-qr-courses.png",
    "sfw-brochure-qr-website.png":       ROOT / "exports/qr/sfw-brochure-qr-website.png",
    "sfw-brochure-qr-casestudies.png":   ROOT / "exports/qr/sfw-brochure-qr-casestudies.png",
    "sfw-brochure-qr-donate.png":        ROOT / "exports/qr/sfw-brochure-qr-donate.png",
}

for d in (OUT, SEND):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)

missing = [n for n, p in {**FILES, **SEND_FILES}.items() if not p.exists()]
if missing:
    raise SystemExit("not built yet: " + ", ".join(missing))

for name, src in FILES.items():
    shutil.copy2(src, OUT / name)

# The README lives in build/ as a source file, not written into the folder by
# hand: this script deletes the folder every run, so a note left in there would
# be destroyed by the next rebuild. It was, once.
shutil.copy2(pathlib.Path(__file__).parent / "delivery-README.md", OUT / "README.md")

for name, src in SEND_FILES.items():
    shutil.copy2(src, SEND / name)
shutil.copy2(pathlib.Path(__file__).parent / "send-README.md", SEND / "README.md")

with zipfile.ZipFile(OUT / "sfw-brochure-2026-all.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for name in FILES:
        z.write(OUT / name, name)

for name, folder in ([(n, SEND) for n in list(SEND_FILES) + ["README.md"]]
                     + [(n, OUT) for n in list(FILES) + ["sfw-brochure-2026-all.zip"]]):
    p = folder / name
    digest = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
    print(f"  {folder.name + '/' + name:<52}{p.stat().st_size/1024:>9.0f} KB  {digest}")
