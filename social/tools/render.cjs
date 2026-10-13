// Render every .slide in the post files to 1080 x 1350 PNGs, then one contact sheet per post.
// Run from the repo root: node social/tools/render.cjs
const { chromium } = require("playwright");
const { pathToFileURL } = require("node:url");
const path = require("node:path");
const fs = require("node:fs");

(async () => {

const root = path.resolve(__dirname, "..");
const posts = fs.readdirSync(root).filter((f) => /^post-.*\.html$/.test(f));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 1500 }, deviceScaleFactor: 1 });

for (const file of posts) {
  const name = file.replace(/\.html$/, "");
  const out = path.join(root, name);
  fs.mkdirSync(out, { recursive: true });
  await page.goto(pathToFileURL(path.join(root, file)).href);
  await page.evaluate(() => document.fonts.ready);
  const slides = await page.$$(".slide");
  const shots = [];
  for (const [i, s] of slides.entries()) {
    const png = path.join(out, `slide-${i + 1}.png`);
    await s.screenshot({ path: png });
    shots.push(path.basename(png));
  }
  // Contact sheet: all slides in a row, scaled down, numbered.
  const sheet = await browser.newPage({ viewport: { width: 2140, height: 600 } });
  const sheetHtml = path.join(out, "contact-sheet.html");
  fs.writeFileSync(sheetHtml, `<body style="margin:0;background:#E6E1D6;font:600 22px 'Source Sans 3',Arial;color:#22371F">
    <div style="padding:28px 40px 8px">${name}</div>
    <div style="display:flex;gap:20px;padding:12px 40px 40px">${shots.map((s, i) =>
      `<figure style="margin:0"><img src="${s}" style="width:396px;height:495px;display:block;box-shadow:0 2px 10px rgba(0,0,0,.18)"><figcaption style="margin-top:10px">${i + 1}</figcaption></figure>`).join("")}</div></body>`);
  await sheet.goto(pathToFileURL(sheetHtml).href);
  await sheet.screenshot({ path: path.join(out, "contact-sheet.png"), fullPage: true });
  await sheet.close();
  fs.unlinkSync(sheetHtml);
  console.log(`${name}: ${shots.length} slides`);
}
await browser.close();
})();
