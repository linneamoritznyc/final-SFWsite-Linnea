// Screenshot every .slide in slides.html to slide-N.png, then a contact sheet.
const { chromium } = require("playwright");
const { pathToFileURL } = require("node:url");
const path = require("node:path");
const fs = require("node:fs");
const DIR = process.argv[2] || __dirname;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 1500 } });
  await p.goto(pathToFileURL(path.join(DIR, "slides.html")).href);
  await p.evaluate(() => document.fonts.ready);
  const slides = await p.$$(".slide");
  for (const [i, s] of slides.entries()) await s.screenshot({ path: path.join(DIR, `slide-${i + 1}.png`) });
  const n = slides.length;
  const sheet = path.join(DIR, "contact-sheet.html");
  fs.writeFileSync(sheet, `<body style="margin:0;background:#1f1f1f;font:600 22px Arial;color:#eee"><div style="display:grid;grid-template-columns:repeat(5,324px);gap:18px;padding:30px">${
    Array.from({ length: n }, (_, i) => `<figure style="margin:0"><img src="slide-${i + 1}.png" style="width:324px;height:405px;display:block"><figcaption style="margin-top:6px">${i + 1}</figcaption></figure>`).join("")}</div></body>`);
  const q = await b.newPage({ viewport: { width: 1770, height: 400 } });
  await q.goto(pathToFileURL(sheet).href);
  await q.screenshot({ path: path.join(DIR, "contact-sheet.png"), fullPage: true });
  fs.unlinkSync(sheet);
  await b.close();
})();
