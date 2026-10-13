/* Render the two spreads to vector PDF, for the printer.
 *
 *   node "trifold-farmers/build/render-pdf.js"
 *   python3 "trifold-farmers/build/make-pdfx.py"    # then CMYK + PDF/X + boxes
 *
 * Chromium's page.pdf() keeps text as text and vector art as vector, which is
 * the whole point: the QR modules stay geometry rather than resampled pixels,
 * and the type stays sharp at any magnification. Photographs are the only
 * raster in the file, which is correct, they are photographs.
 *
 * Page size is trim plus bleed, 11.25 x 8.75in, with no margin. The trim and
 * bleed boxes are written afterwards by make-pdfx.py, because Chromium has no
 * way to set them.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http = require('http');
const path = require('path');
const fs = require('fs');

const REPO = path.resolve(__dirname, '..', '..');
const OUT = path.resolve(__dirname, '..', 'print', 'alternates');  // RGB source, not for sending
fs.mkdirSync(OUT, { recursive: true });

const TYPES = { '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8',
  '.svg':'image/svg+xml', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg',
  '.woff2':'font/woff2' };

function serve() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '');
      const file = path.join(REPO, rel);
      if (!file.startsWith(REPO) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
        res.writeHead(404); res.end('not found: ' + rel); return;
      }
      res.writeHead(200, { 'Content-Type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream' });
      fs.createReadStream(file).pipe(res);
    });
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

(async () => {
  const server = await serve();
  const port = server.address().port;
  const browser = await chromium.launch();
  const page = await browser.newPage();

  for (const src of ['outside', 'inside']) {
    await page.goto(`http://127.0.0.1:${port}/trifold-farmers/build/${src}.html`, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const out = path.join(OUT, `sfw-farmers-trifold-${src}.pdf`);
    await page.pdf({ path: out, width: '11.25in', height: '8.75in',
                     margin: { top: 0, right: 0, bottom: 0, left: 0 },
                     printBackground: true, pageRanges: '1' });
    console.log(`${src}  ${(fs.statSync(out).size / 1024 / 1024).toFixed(2)} MB  ${out}`);
  }

  await browser.close();
  server.close();
})();
