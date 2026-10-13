// Builds an editable PowerPoint of the Open House post from layout.json (made by build.py).
// Each cut-out is its own picture; the text is real text boxes. Slide is 10 x 12.5 in (1080 x 1350 px).
// Run from the repo root: node social/open-house-2026-10-16/make-pptx.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const HERE = __dirname;
const L = JSON.parse(fs.readFileSync(path.join(HERE, "layout.json"), "utf8"));
const PX = 108; // px per inch
const inch = (v) => v / PX;
const pt = (px) => Math.round((px * 72) / PX * 10) / 10;

const pres = new pptxgen();
pres.defineLayout({ name: "INSTA_4x5", width: inch(L.w), height: inch(L.h) });
pres.layout = "INSTA_4x5";
pres.title = "SFW Open House, October 16";

const slide = pres.addSlide();
slide.background = { color: L.background };

for (const it of L.items) {
  if (it.type === "image") {
    slide.addImage({ path: path.join(HERE, it.file), x: inch(it.x), y: inch(it.y), w: inch(it.w), h: inch(it.h),
      objectName: it.name, altText: it.name.replace(/-/g, " ") });
  } else if (it.type === "pill") {
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: inch(it.x), y: inch(it.y), w: inch(it.w), h: inch(it.h),
      fill: { color: it.color }, line: { color: it.color, width: 0 }, rectRadius: 0.5, objectName: it.name });
  }
}
for (const it of L.items) {
  if (it.type !== "text") continue;
  slide.addText(it.text, { x: inch(it.x), y: inch(it.y), w: inch(it.w), h: inch(it.h), margin: 0,
    fontFace: it.font, fontSize: pt(it.size), bold: it.bold, italic: it.italic, color: it.color,
    align: it.align, valign: it.valign, fit: "none", wrap: false, isTextBox: true, objectName: it.name });
}

pres.writeFile({ fileName: path.join(HERE, "open-house-oct16-editable.pptx") }).then((f) => console.log(f));
