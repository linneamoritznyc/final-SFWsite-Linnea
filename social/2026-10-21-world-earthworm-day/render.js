// Render frame-1..3.html to png/frame-N.png (with text) and png/frame-N-art.png (art only), 1080 x 1920.
// node social/2026-10-21-world-earthworm-day/render.js   (Playwright; Chromium at /opt/pw-browsers/chromium or PW default)
const path = require('path'), fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const dir = __dirname, out = path.join(dir, 'png');
  fs.mkdirSync(out, { recursive: true });
  const exe = fs.existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined;
  const b = await chromium.launch(exe ? { executablePath: exe } : {});
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  for (const n of [1, 2, 3]) {
    await pg.goto('file://' + path.join(dir, `frame-${n}.html`), { waitUntil: 'load' });
    await pg.evaluate(() => document.fonts.ready);
    await pg.screenshot({ path: path.join(out, `frame-${n}.png`) });
    await pg.evaluate(() => document.body.classList.add('art-only'));
    await pg.screenshot({ path: path.join(out, `frame-${n}-art.png`) });
  }
  await b.close();
  console.log('rendered', out);
})();
