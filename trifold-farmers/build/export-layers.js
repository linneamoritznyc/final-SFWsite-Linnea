/* Read the rendered sheets and write every visual piece out separately, for
 * an editable PowerPoint: shapes as geometry and colour, photographs, icons
 * and QR codes as their own transparent PNGs, text as runs with their styles.
 *
 *   node trifold-farmers/build/export-layers.js <outdir> [build dir, default trifold-farmers/build]
 *   python3 trifold-farmers/build/make-pptx.py <outdir>
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http = require('http'), path = require('path'), fs = require('fs');
const REPO = path.resolve(__dirname, '..', '..');
const OUT = path.resolve(process.argv[2]);
const BUILD = (process.argv[3] || 'trifold-farmers/build').replace(/\/$/, '');
fs.mkdirSync(OUT, { recursive: true });
const T = {'.html':'text/html; charset=utf-8','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.woff2':'font/woff2'};
const server = http.createServer((q, r) => {
  const f = path.join(REPO, decodeURIComponent(q.url.split('?')[0]));
  if (f.startsWith(REPO) && fs.existsSync(f) && fs.statSync(f).isFile()) {
    r.writeHead(200, {'Content-Type': T[path.extname(f).toLowerCase()] || 'application/octet-stream'}); fs.createReadStream(f).pipe(r);
  } else { r.writeHead(404); r.end(); }
});

(async () => {
  await new Promise(r => server.listen(0, r));
  const port = server.address().port;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 840 }, deviceScaleFactor: 300 / 96 });
  const result = {};
  for (const sheet of ['outside', 'inside']) {
    await page.goto(`http://127.0.0.1:${port}/${BUILD.split('/').map(encodeURIComponent).join('/')}/${sheet}.html`, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const items = await page.evaluate(() => {
      const sheetBox = document.querySelector('.sheet').getBoundingClientRect();
      const box = (el) => { const r = el.getBoundingClientRect();
        return { x: r.left - sheetBox.left, y: r.top - sheetBox.top, w: r.width, h: r.height }; };
      // The fade on a colour panel's photograph is a ::after; make it a real
      // element so it can be cut out as its own layer.
      document.querySelectorAll('.panel--field .figure--fade').forEach((fig) => {
        const cs = getComputedStyle(fig, '::after');
        if (cs.content === 'none') return;
        const d = document.createElement('div');
        d.className = '__fade';
        Object.assign(d.style, { position: 'absolute', left: '0', right: '0', bottom: '0',
          height: cs.height, backgroundImage: cs.backgroundImage, zIndex: '0' });
        fig.insertBefore(d, fig.querySelector('figcaption'));
      });
      const st = document.createElement('style');
      st.textContent = '.figure--fade::after{display:none !important}';
      document.head.appendChild(st);

      const out = []; let n = 0;
      const TEXT = 'p, h1, h2, h3, figcaption, .t, .d, .h, .l, .n, .wordmark, .sub, .checks li > div, .eyebrow';
      const hasBg = (cs) => (cs.backgroundImage && cs.backgroundImage.includes('gradient')) ||
                            (cs.backgroundColor && !/rgba\(0, 0, 0, 0\)|transparent/.test(cs.backgroundColor));
      const runsOf = (el) => {
        const runs = [];
        const walk = (node) => {
          for (const c of node.childNodes) {
            if (c.nodeType === 3) {
              const t = c.textContent.replace(/\s+/g, ' ');
              if (!t.trim() && !runs.length) continue;
              const cs = getComputedStyle(c.parentElement);
              let text = cs.textTransform === 'uppercase' ? t.toUpperCase() : t;
              runs.push({ text, font: cs.fontFamily.split(',')[0].replace(/"/g, '').trim(),
                size: parseFloat(cs.fontSize) * 0.75, weight: parseInt(cs.fontWeight),
                italic: cs.fontStyle === 'italic', color: cs.color,
                spacing: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) * 0.75 });
            } else if (c.nodeType === 1) {
              if (c.tagName.toLowerCase() === 'br') { runs.push({ text: '\n' }); continue; }
              if (c.tagName.toLowerCase() === 'svg') continue;
              walk(c);
              const d = getComputedStyle(c).display;
              if ((d === 'block' || d === 'flex') && c.nextSibling) runs.push({ text: '\n' });
            }
          }
        };
        walk(el);
        // trim edges
        while (runs.length && runs[0].text !== '\n' && !runs[0].text.trim()) runs.shift();
        if (runs.length && runs[0].text) runs[0].text = runs[0].text.replace(/^\s+/, '');
        const last = runs[runs.length - 1]; if (last && last.text) last.text = last.text.replace(/\s+$/, '');
        runs.forEach((r, i) => { if (r.text && r.text !== '\n' && runs[i - 1] && runs[i - 1].text === '\n') r.text = r.text.replace(/^\s+/, ''); });
        return runs;
      };

      const visit = (el, depth) => {
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') return;
        const tag = el.tagName.toLowerCase();
        // Panel ground: the panel's own colour, then a field panel's gradient.
        if (el.classList.contains('panel')) {
          out.push({ kind: 'rect', name: `panel ${el.dataset.panel} ground`, ...box(el), fill: cs.backgroundColor, image: 'none', radius: 0 });
          const b = getComputedStyle(el, '::before');
          if (b.content !== 'none' && b.backgroundImage.includes('gradient'))
            out.push({ kind: 'rect', name: `panel ${el.dataset.panel} colour field`, ...box(el), fill: b.backgroundColor, image: b.backgroundImage, radius: 0 });
        } else if (hasBg(cs) && tag !== 'img' && !el.classList.contains('__fade')) {
          out.push({ kind: 'rect', name: (el.className || tag) + ' background', ...box(el), fill: cs.backgroundColor, image: cs.backgroundImage,
                     radius: parseFloat(cs.borderTopLeftRadius) || 0 });
        }
        // Rules: a left border (the boxes) and a top border (hairlines).
        const bl = parseFloat(cs.borderLeftWidth), bt = parseFloat(cs.borderTopWidth);
        if (bl > 0 && cs.borderLeftStyle !== 'none') { const b = box(el);
          out.push({ kind: 'rect', name: 'left rule', x: b.x, y: b.y, w: bl, h: b.h, fill: cs.borderLeftColor, image: 'none', radius: 0 }); }
        if (bt > 0 && cs.borderTopStyle !== 'none') { const b = box(el);
          out.push({ kind: 'rect', name: 'hairline', x: b.x, y: b.y, w: b.w, h: bt, fill: cs.borderTopColor, image: 'none', radius: 0 }); }

        if (tag === 'img' || (tag === 'svg' && el.classList.contains('icon')) || el.classList.contains('__fade')) {
          el.dataset.layer = String(n);
          out.push({ kind: 'image', name: tag === 'img' ? (el.getAttribute('src').split('/').pop()) : (tag === 'svg' ? 'icon ' + (el.querySelector('use') || {getAttribute:()=>''}).getAttribute('href') : 'photo fade'),
                     id: n++, ...box(el) });
          return;
        }
        if (el.matches(TEXT) && [...el.childNodes].some(c => c.nodeType === 3 && c.textContent.trim())
            || (el.matches(TEXT) && el.matches('p.pull, p.addr, .tagline, .l, .n, h1, h2, h3, .t, .d, .h, figcaption'))) {
          const runs = runsOf(el);
          if (runs.some(r => r.text && r.text.trim())) {
            // An icon set inline at the start of the text (the box standfirsts)
            // becomes a first-line indent, so the text clears the icon.
            const ic = el.querySelector('svg.icon');
            const indent = ic ? ic.getBoundingClientRect().right + 4.5 - el.getBoundingClientRect().left : 0;
            out.push({ kind: 'text', name: (el.className || tag), ...box(el), runs, indent,
              align: cs.textAlign, lineHeight: parseFloat(cs.lineHeight) * 0.75 || null });
            // icons inside a text block (the box standfirsts) still need out
            el.querySelectorAll('svg.icon').forEach((s) => visit(s, depth + 1));
            return;
          }
        }
        for (const c of el.children) visit(c, depth + 1);
      };
      document.querySelectorAll('.panel').forEach((p) => visit(p, 0));
      return out;
    });

    // Cut every image layer out on its own, on a transparent ground.
    await page.addStyleTag({ content: `
      html.__iso, html.__iso body, html.__iso .sheet { background: transparent !important; }
      html.__iso * { visibility: hidden !important; }
      html.__iso [data-layer].__on, html.__iso [data-layer].__on * { visibility: visible !important; }
      /* Icons are drawn from the sprite's <symbol>s through <use>; the clones
         take the symbol's own styles, so the symbols must stay visible. A
         symbol never paints on its own, so this shows nothing else. */
      html.__iso symbol, html.__iso symbol * { visibility: visible !important; }` });
    await page.evaluate(() => document.documentElement.classList.add('__iso'));
    for (const it of items.filter(i => i.kind === 'image')) {
      await page.evaluate((id) => {
        document.querySelectorAll('.__on').forEach(e => e.classList.remove('__on'));
        document.querySelector(`[data-layer="${id}"]`).classList.add('__on');
      }, it.id);
      const clip = await page.evaluate((id) => { const r = document.querySelector(`[data-layer="${id}"]`).getBoundingClientRect();
        return { x: r.left, y: r.top, width: r.width, height: r.height }; }, it.id);
      it.file = `${sheet}-${String(it.id).padStart(3, '0')}.png`;
      await page.screenshot({ path: path.join(OUT, it.file), clip, omitBackground: true });
    }
    result[sheet] = items;
    console.log(sheet, items.length, 'layers:', ['rect', 'image', 'text'].map(k => `${items.filter(i => i.kind === k).length} ${k}`).join(', '));
  }
  fs.writeFileSync(path.join(OUT, 'layers.json'), JSON.stringify(result));
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
