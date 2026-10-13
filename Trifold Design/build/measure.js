/* Measure where each .below block starts, as a fraction of sheet height, and
   where each panel sits horizontally. The horizon path is then set from these
   numbers instead of by eye. */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http = require('http'); const path = require('path'); const fs = require('fs');
const REPO = path.resolve(__dirname, '..', '..');
const TYPES = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.woff2':'font/woff2'};
const server = http.createServer((req,res)=>{
  const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/,'');
  for (const base of [path.join(REPO,'Trifold Design','build'), REPO]) {
    const f = path.join(base, rel);
    if (fs.existsSync(f) && fs.statSync(f).isFile()) {
      res.writeHead(200,{'Content-Type':TYPES[path.extname(f)]||'application/octet-stream'});
      return fs.createReadStream(f).pipe(res);
    }
  }
  res.writeHead(404); res.end();
});
(async () => {
  await new Promise(r => server.listen(0, r));
  const port = server.address().port;
  const br = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  for (const page_name of ['outside-horizon','inside-horizon']) {
    const page = await br.newPage({ viewport:{width:1200,height:950} });
    await page.goto(`http://127.0.0.1:${port}/${page_name}.html`, { waitUntil:'networkidle' });
    const data = await page.evaluate(() => {
      const sheet = document.querySelector('.sheet').getBoundingClientRect();
      return [...document.querySelectorAll('.panel')].map(p => {
        const pr = p.getBoundingClientRect();
        const b = p.querySelector('.below');
        return {
          panel: p.dataset.panel,
          x0: +(((pr.left - sheet.left) / sheet.width) * 1125).toFixed(0),
          x1: +(((pr.right - sheet.left) / sheet.width) * 1125).toFixed(0),
          belowTopFrac: b ? +(((b.getBoundingClientRect().top - sheet.top) / sheet.height).toFixed(4)) : null,
        };
      });
    });
    // sheet is 8.75in tall; the horizon svg is 4.30in tall sitting at the foot,
    // so svg y (100 units per inch) = (frac * 8.75 - 4.45) * 100
    for (const d of data) {
      d.svgY = d.belowTopFrac === null ? null : Math.round((d.belowTopFrac * 8.75 - 4.45) * 100);
      d.mid = Math.round((d.x0 + d.x1) / 2);
    }
    console.log(page_name, JSON.stringify(data));
    await page.close();
  }
  await br.close(); server.close();
})().catch(e => { console.error(e.message); process.exit(1); });
