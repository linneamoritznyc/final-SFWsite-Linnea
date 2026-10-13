/* Render the home proof to PDF. Separate from render-pdf.js because this one
   is Letter with margins and marks, not the press sheet. */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const OUT = path.resolve(__dirname, '..', 'print');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(OUT, '.home-proof.html'), { waitUntil: 'networkidle' });
  await page.pdf({ path: path.join(OUT, 'HOME-PROOF-cut-and-fold.pdf'),
                   width: '11in', height: '8.5in', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await browser.close();
})();
