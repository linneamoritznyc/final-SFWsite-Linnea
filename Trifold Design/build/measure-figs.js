const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http = require('http'); const path = require('path'); const fs = require('fs');
const REPO = path.resolve(__dirname, '..', '..');
const T = {'.html':'text/html','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.JPG':'image/jpeg','.woff2':'font/woff2'};
const server = http.createServer((q,r)=>{const rel=decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/,'');
 for(const b of [path.join(REPO,'Trifold Design','build'),REPO]){const f=path.join(b,rel);
  if(fs.existsSync(f)&&fs.statSync(f).isFile()){r.writeHead(200,{'Content-Type':T[path.extname(f)]||'application/octet-stream'});return fs.createReadStream(f).pipe(r);}}
 r.writeHead(404);r.end();});
(async()=>{await new Promise(r=>server.listen(0,r));const port=server.address().port;
 const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
 for(const pg of ['outside','inside']){
  const page=await br.newPage({viewport:{width:1200,height:950}});
  await page.goto(`http://127.0.0.1:${port}/${pg}.html`,{waitUntil:'networkidle'});
  const d=await page.evaluate(()=>{const s=document.querySelector('.sheet').getBoundingClientRect();
   return [...document.querySelectorAll('.panel')].map(p=>{const img=p.querySelector('.figure--full img');
    const r=img.getBoundingClientRect();const pr=p.getBoundingClientRect();
    return {panel:p.dataset.panel,
      imgX0:+(((r.left-s.left)/s.width)).toFixed(4), imgX1:+(((r.right-s.left)/s.width)).toFixed(4),
      imgTop:+(((r.top-s.top)/s.height)).toFixed(4), imgBot:+(((r.bottom-s.top)/s.height)).toFixed(4),
      hFrac:+((r.height/s.height)).toFixed(4)};});});
  console.log(pg, JSON.stringify(d,null,0));
  await page.close();}
 await br.close();server.close();})().catch(e=>{console.error(e.message);process.exit(1);});
