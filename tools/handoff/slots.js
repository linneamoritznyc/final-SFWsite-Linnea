// Measure every image slot on every page of the local preview at 1440 px wide.
//   NODE_PATH=/opt/node-tools/node_modules node tools/handoff/slots.js <base-url> <pages.json> <out.json>
// For each content image (header, footer, logos and portraits left out) it records the page, the
// section heading above it, the kind of slot (hero, card, tile, gallery, ...), the rendered box, the
// file the browser chose, alt text and caption.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [base, pagesFile, out] = process.argv.slice(2);
  const pages = JSON.parse(fs.readFileSync(pagesFile, 'utf8'));
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
  const rows = [];
  for (const path of pages) {
    await p.goto(base + path, { waitUntil: 'load', timeout: 60000 });
    await p.evaluate(() => document.querySelectorAll('img[loading=lazy]').forEach(i => { i.loading = 'eager'; }));
    for (let y = 0; y < 40000; y += 900) {
      const h = await p.evaluate(y => { window.scrollTo(0, y); return document.body.scrollHeight; }, y);
      await p.waitForTimeout(40);
      if (y > h) break;
    }
    await p.waitForTimeout(400);
    const found = await p.evaluate(() => {
      const main = document.querySelector('main');
      const heads = [...main.querySelectorAll('h1, h2, section[aria-label], .eyebrow')];
      const res = [];
      for (const img of main.querySelectorAll('img')) {
        const src = img.currentSrc || img.src;
        const alt = img.getAttribute('alt') || '';
        if (!src || /\.svg($|\?)|sfwlogo|logo/i.test(src) || /^(Portrait of|Photo of)/.test(alt)) continue;
        if (img.closest('.person, .people, .sfw-team-card, .byline, .vcard, .plist, .vfacade, .embed')) continue;
        const r = img.getBoundingClientRect();
        if (r.width < 2 || r.height < 2) continue;
        // Section heading: the last h1/h2 (or labelled section) before the image in document order.
        let head = '';
        for (const h of heads) {
          if (h.compareDocumentPosition(img) & Node.DOCUMENT_POSITION_FOLLOWING) {
            head = h.matches('section[aria-label]') ? h.getAttribute('aria-label') : h.textContent.trim().replace(/\s+/g, ' ');
          }
        }
        if (!head && main.querySelector('h1')) head = main.querySelector('h1').textContent.trim().replace(/\s+/g, ' ');
        const anc = s => img.closest(s);
        let kind = 'image';
        if (anc('.post-hero, .hero, .sfw-workshop-single__hero, .band--photo')) kind = anc('.band--photo') ? 'banner' : 'hero';
        else if (anc('.tile')) kind = 'tile';
        else if (anc('.sfw-workshop-gallery, #photos')) kind = 'gallery';
        else if (anc('.card, .sfw-workshops__card, .grid > li, .scroller > li')) kind = 'card';
        else if (anc('.split__media')) kind = 'side image';
        else if (anc('.prose, .event-single__body')) kind = 'body image';
        const fig = img.closest('figure');
        const cap = fig && fig.querySelector('figcaption') ? fig.querySelector('figcaption').textContent.trim() : '';
        const cs = getComputedStyle(img);
        res.push({ head, kind, src, alt, caption: cap, w: Math.round(r.width), h: Math.round(r.height),
                   fit: cs.objectFit, pos: cs.objectPosition, y: Math.round(r.top + scrollY) });
      }
      return res;
    });
    const n = {};
    for (const f of found) {
      const key = f.head + '|' + f.kind;
      n[key] = (n[key] || 0) + 1;
      rows.push(Object.assign({ page: path, index: n[key] }, f));
    }
  }
  fs.writeFileSync(out, JSON.stringify(rows, null, 1));
  console.log(rows.length, 'slots on', pages.length, 'pages');
  await b.close();
})();
