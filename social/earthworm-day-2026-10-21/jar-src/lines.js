// node lines.js a.html b.html ... -> JSON {file: [[line, line], ...per .t div]}
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  const out = {};
  for (const f of process.argv.slice(2)) {
    await p.goto('file://' + f);
    await p.evaluate(() => document.fonts.ready);
    out[f] = await p.evaluate(() => [...document.querySelectorAll('.t')].map(div => {
      const lines = []; let cur = '', top = null;
      const walker = document.createTreeWalker(div, NodeFilter.SHOW_TEXT);
      let n;
      while ((n = walker.nextNode())) {
        for (let i = 0; i < n.length; i++) {
          const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + 1);
          const rects = r.getClientRects();
          if (!rects.length) { cur += n.data[i]; continue; }
          const t = Math.round(rects[0].top);
          if (top !== null && Math.abs(t - top) > 4) { lines.push(cur.trim()); cur = ''; }
          top = t; cur += n.data[i];
        }
      }
      lines.push(cur.trim());
      return lines.filter(l => l.length);
    }));
  }
  console.log(JSON.stringify(out));
  await b.close();
})();
