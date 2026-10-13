const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http=require('http'),path=require('path'),fs=require('fs');
const REPO='/home/user/SFW-newwebsite';
const T={'.html':'text/html','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.woff2':'font/woff2'};
(async()=>{const srv=http.createServer((q,r)=>{const rel=decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/,'');const f=path.join(REPO,rel);
 if(!fs.existsSync(f)||fs.statSync(f).isDirectory()){r.writeHead(404);r.end();return;}
 r.writeHead(200,{'Content-Type':T[path.extname(f).toLowerCase()]||'application/octet-stream'});fs.createReadStream(f).pipe(r);});
 await new Promise(r=>srv.listen(0,'127.0.0.1',r)); const port=srv.address().port;
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:840}});
 const out={};
 for(const src of ['outside','inside']){
  await p.goto(`http://127.0.0.1:${port}/Trifold%20Design/build/${src}.html`,{waitUntil:'networkidle'});
  await p.evaluate(()=>document.fonts.ready);
  out[src]=await p.evaluate(()=>[...document.querySelectorAll('.qr img')].map(i=>{
    const r=i.getBoundingClientRect();
    return {src:i.getAttribute('src'),x:r.x,y:r.y,w:r.width,h:r.height};}));
 }
 console.log(JSON.stringify(out)); await b.close(); srv.close();})();
