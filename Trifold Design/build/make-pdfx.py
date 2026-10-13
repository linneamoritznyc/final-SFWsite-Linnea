#!/usr/bin/env python3
"""Build the printer set: CMYK PDF/X-4 and PDF/X-1a, separates and 2-page.

    node "Trifold Design/build/render-pdf.js"    # first, the vector PDFs
    python3 "Trifold Design/build/make-pdfx.py"
    python3 "Trifold Design/build/check-qr.py" "Trifold Design/print/<file>.pdf"

Produces one file to send and a folder of alternates nobody should have to
choose between:

    print/sfw-trifold-2page-CMYK-PDFX.pdf          X-4, both sheets. The file.
    print/alternates/*-CMYK-PDFX.pdf               X-4 separates
    print/alternates/*-CMYK-PDFX1a.pdf             X-1a, merged and separate

X-4 keeps every vector: the type, the rules, and the QR codes as roughly 2,300
path segments each. It is the better file and the one to send.

X-1a CANNOT keep them, and that is the standard's doing rather than a choice
here. X-1a forbids live transparency; this design has rgba fills and gradient
fades over photographs; so the page is flattened, and Ghostscript flattens by
rasterising the whole sheet. It is done at 600 DPI, twice what a press needs,
and every code was decoded out of the result before shipping. Never build it
with Ghostscript's -dPDFX switch, which flattens to 72 DPI-ish garbage and
silently destroys the codes; the flattening resolution below is the point.
"""
import pathlib, subprocess, sys
import pikepdf

HERE = pathlib.Path(__file__).parent
PRINT = HERE.parent / "print"
ALT = PRINT / "alternates"     # everything that is not the file to send
ICC = pathlib.Path("/usr/share/ghostscript/10.02.1/iccprofiles/default_cmyk.icc")

PT = 72.0
BLEED, TRIM_W, TRIM_H = 0.125 * PT, 11.0 * PT, 8.5 * PT
MEDIA = (TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED)           # 810 x 630 pt
TRIM = (BLEED, BLEED, MEDIA[0] - BLEED, MEDIA[1] - BLEED)  # 9 9 801 621
FLATTEN_DPI = 600

XMP = """<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
    xmlns:pdfxid="http://www.npes.org/pdfx/ns/id/"
    xmlns:xmp="http://ns.adobe.com/xap/1.0/">
   <dc:title><rdf:Alt><rdf:li xml:lang="x-default">Soil Food Web Foundation trifold</rdf:li></rdf:Alt></dc:title>
   <pdfxid:GTS_PDFXVersion>{version}</pdfxid:GTS_PDFXVersion>
   <pdf:Trapped>False</pdf:Trapped>
   <xmp:CreatorTool>Soil Food Web Foundation trifold build</xmp:CreatorTool>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""

GS_COMMON = [
    "gs", "-dBATCH", "-dNOPAUSE", "-dQUIET", "-dSAFER", "-sDEVICE=pdfwrite",
    "-dProcessColorModel=/DeviceCMYK", "-sColorConversionStrategy=CMYK",
    "-dOverrideICC=true", f"-sOutputICCProfile={ICC}",
    # Photographs are capped at 400 ppi. They used to go in at whatever
    # resolution the file happened to be, which put the test tubes photograph
    # on panel 4 into the PDF at 3083 x 2235, about 811 ppi over its 3.8in
    # frame and nearly seven megapixels, more than twice any other image in the
    # piece. It printed as a near black rectangle on a home printer while every
    # other photograph came out right, which is what a decoder that has run out
    # of room for one image looks like. 400 ppi is well above what a 175 line
    # screen can resolve, so nothing visible is given up, and the outlier is
    # gone. Grey and mono images are left alone: the only ones are the gradient
    # ramps, at well under 100 ppi already.
    "-dDownsampleColorImages=true", "-dColorImageDownsampleType=/Bicubic",
    "-dColorImageResolution=400", "-dColorImageDownsampleThreshold=1.2",
    "-dDownsampleGrayImages=false",
    "-dDownsampleMonoImages=false", "-dAutoFilterColorImages=false",
    "-dColorImageFilter=/DCTEncode",
]


def gs_run(args, src, dst):
    r = subprocess.run(GS_COMMON + args + [f"-sOutputFile={dst}", str(src)],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)


def to_cmyk_x4(src, dst):
    """Colour-convert only. PDF 1.6 keeps transparency live, so nothing
    is flattened and every vector stays a vector."""
    gs_run(["-dCompatibilityLevel=1.6"], src, dst)


def to_cmyk_x1a(src, dst):
    """X-1a: PDF 1.3, which forbids live transparency, so the sheet is
    flattened. At 600 DPI, because whatever this rasterises has to hold up
    on a press, the QR codes included."""
    gs_run([f"-r{FLATTEN_DPI}", "-dCompatibilityLevel=1.3"], src, dst)


def finish(path, version, pages=1):
    """Boxes on every page, output intent, XMP, interpolation on gradient ramps."""
    with pikepdf.open(path, allow_overwriting_input=True) as pdf:
        assert len(pdf.pages) == pages, f"{path.name}: {len(pdf.pages)} pages, wanted {pages}"
        smoothed = 0
        for page in pdf.pages:
            page.MediaBox = pikepdf.Array([0, 0, *MEDIA])
            page.CropBox = pikepdf.Array([0, 0, *MEDIA])
            page.BleedBox = pikepdf.Array([0, 0, *MEDIA])
            page.TrimBox = pikepdf.Array(list(TRIM))
            page.ArtBox = pikepdf.Array(list(TRIM))
            for _, xo in dict(page.Resources.get("/XObject", {})).items():
                # The gradient ramps are the only images under 600px wide; they
                # are smooth two-colour ramps, so let the RIP interpolate them
                # rather than step them. Photographs are left alone.
                if str(xo.get("/Subtype")) == "/Image" and int(xo.Width) < 600:
                    xo.Interpolate = True
                    smoothed += 1

        # A transparency group blending in DeviceRGB inside a CMYK PDF/X file is
        # a conformance failure and blends in the wrong space. Chromium writes
        # one; retarget it.
        for obj in pdf.objects:
            try:
                if (str(obj.get("/Type")) == "/Group"
                        and str(obj.get("/S")) == "/Transparency"
                        and str(obj.get("/CS")) == "/DeviceRGB"):
                    obj.CS = pikepdf.Name("/DeviceCMYK")
            except (AttributeError, TypeError):
                continue

        icc = pdf.make_stream(ICC.read_bytes())
        icc.N = 4
        pdf.Root.OutputIntents = pikepdf.Array([pdf.make_indirect(pikepdf.Dictionary(
            Type=pikepdf.Name("/OutputIntent"), S=pikepdf.Name("/GTS_PDFX"),
            OutputCondition=pikepdf.String("Generic CMYK"),
            OutputConditionIdentifier=pikepdf.String("Custom"),
            Info=pikepdf.String("Generic CMYK. Re-target to the press condition."),
            DestOutputProfile=icc))])
        pdf.Root.Metadata = pdf.make_stream(
            XMP.format(version=version).encode("utf-8"),
            Type=pikepdf.Name("/Metadata"), Subtype=pikepdf.Name("/XML"))
        pdf.docinfo["/GTS_PDFXVersion"] = version
        pdf.docinfo["/Trapped"] = pikepdf.Name("/False")
        pdf.save(path)
    return smoothed


def merge(outside, inside, dst):
    """Outside as page 1, inside as page 2, by copying the finished pages.
    No re-rendering: nothing is resampled and the vectors are the same objects."""
    with pikepdf.open(outside) as a, pikepdf.open(inside) as b:
        a.pages.extend(b.pages)
        a.save(dst)


def main():
    if not ICC.exists():
        sys.exit(f"no CMYK profile at {ICC}")
    ALT.mkdir(exist_ok=True)
    built = []
    for tag, convert, version in (("PDFX", to_cmyk_x4, "PDF/X-4"),
                                  ("PDFX1a", to_cmyk_x1a, "PDF/X-1a:2001")):
        pages = {}
        for src in ("outside", "inside"):
            o = ALT / f"sfw-trifold-{src}-CMYK-{tag}.pdf"
            convert(ALT / f"sfw-trifold-{src}.pdf", o)
            finish(o, version)
            pages[src] = o
            built.append(o)
        m = (PRINT if tag == "PDFX" else ALT) / f"sfw-trifold-2page-CMYK-{tag}.pdf"
        merge(pages["outside"], pages["inside"], m)
        finish(m, version, pages=2)
        built.append(m)

    for p in built:
        where = "print/" if p.parent == PRINT else "print/alternates/"
        print(f"  {where + p.name:<56}{p.stat().st_size/1024/1024:>7.2f} MB")


if __name__ == "__main__":
    main()
