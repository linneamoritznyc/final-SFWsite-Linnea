/* Render the two trifold spreads to 300 DPI PNGs.
 *
 *   node "Trifold Design/build/render.js"
 *
 * Layout is written in inches and points. CSS defines 1in as 96px, so a
 * deviceScaleFactor of 300/96 = 3.125 gives exactly 300 DPI:
 *   trim   11in x 8.5in      -> 3300 x 2550 px
 *   +bleed 11.25in x 8.75in  -> 3375 x 2625 px  (0.125in all round)
 *
 * The pages are served over http rather than opened as file:// because
 * Chromium will not load @font-face files across a file:// origin, and the
 * brochure is set in the repository's own self-hosted fonts.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http = require('http');
const path = require('path');
const fs = require('fs');

const REPO = path.resolve(__dirname, '..', '..');
const OUT = path.resolve(__dirname, '..');

const DPI = 300;
const SCALE = DPI / 96;
const W_IN = 11 + 0.25;   // trim width  + bleed both sides
const H_IN = 8.5 + 0.25;  // trim height + bleed both sides

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.woff2': 'font/woff2',
};

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
  const page = await browser.newPage({
    viewport: { width: Math.round(W_IN * 96), height: Math.round(H_IN * 96) },
    deviceScaleFactor: SCALE,
  });

  for (const [src, out] of [['outside', 'outside-spread.png'], ['inside', 'inside-spread.png']]) {
    await page.goto(`http://127.0.0.1:${port}/Trifold%20Design/build/${src}.html`, { waitUntil: 'networkidle' });

    // The review copy shows the production notes; the piece itself never does.
    if (process.env.TRIFOLD_NOTES) {
      await page.evaluate(() => document.querySelector('.sheet').setAttribute('data-notes', 'true'));
    }
    await page.evaluate(() => document.fonts.ready);

    // Overflow check: does any panel's content run past its own box?
    const report = await page.evaluate(() => {
      const out = [];
      // Bleeding elements are pushed --overshoot past the panel on purpose, so
      // that much spill is expected and is not a panel running out of room.
      // Without this allowance every outer panel reports a permanent couple of
      // pixels and a real overflow stops standing out.
      const ob = parseFloat(getComputedStyle(document.documentElement)
                   .getPropertyValue('--overshoot')) * 96;
      document.querySelectorAll('.panel').forEach((p) => {
        const pad = parseFloat(getComputedStyle(p).paddingBottom);
        const inner = p.clientHeight - parseFloat(getComputedStyle(p).paddingTop) - pad;
        let used = 0;
        p.querySelectorAll(':scope > *').forEach((c) => { used += c.getBoundingClientRect().height; });
        // Horizontal too: a flex row that refuses to shrink runs off the side
        // of the panel, and panel overflow:hidden means it is invisible in the
        // numbers and only shows up as a neighbour's photograph looking wrong.
        const box = p.getBoundingClientRect();
        let wide = 0;
        p.querySelectorAll('*').forEach((el) => {
          const r = el.getBoundingClientRect();
          wide = Math.max(wide, r.right - box.right, box.left - r.left);
        });
        out.push({ panel: p.dataset.panel, inner: +inner.toFixed(1), used: +used.toFixed(1),
                   overflow: +Math.max(0, p.scrollHeight - p.clientHeight - ob).toFixed(1),
                   sideways: +Math.max(0, wide - ob).toFixed(1) });
      });
      return out;
    });
    console.log(src, JSON.stringify(report));


    await page.screenshot({ path: path.join(OUT, out), scale: 'device' });
  }

  await browser.close();
  server.close();

  for (const f of ['outside-spread.png', 'inside-spread.png']) {
    const p = path.join(OUT, f);
    console.log(f, (fs.statSync(p).size / 1024 / 1024).toFixed(2) + ' MB');
  }
})();
