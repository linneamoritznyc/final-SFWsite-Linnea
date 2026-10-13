// Render the three slide 1 directions and a side-by-side sheet at feed size.
const { chromium } = require("playwright");
const { pathToFileURL } = require("node:url");
const path = require("node:path");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 3500, height: 1450 } });
  await p.goto(pathToFileURL(path.join(__dirname, "slide-1-directions.html")).href);
  await p.evaluate(() => document.fonts.ready);
  for (const id of ["a", "b", "c"]) await (await p.$("#" + id)).screenshot({ path: path.join(__dirname, `direction-${id}.png`) });
  await b.close();
})();
