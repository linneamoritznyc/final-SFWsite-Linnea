// node render.js in.html out.png [transparent]
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const [,, inp, out, transp] = process.argv;
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + inp);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({ path: out, omitBackground: !!transp });
  await b.close();
})();
