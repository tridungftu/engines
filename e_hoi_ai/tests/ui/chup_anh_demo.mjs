// Chrome headless, điều khiển CDP chỉ trên loopback; không gọi dịch vụ ngoài.
// Node test của màn vẫn hoàn toàn trong RAM; công cụ này dành riêng cho ảnh PR.
import {spawn} from 'node:child_process';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {setTimeout as cho} from 'node:timers/promises';
await import('./dung_anh_demo.mjs');
const profile=resolve('.pytest-tmp-chrome-ui-ai-1-cdp',String(Date.now()));
await mkdir(profile,{recursive:true});
const chrome=spawn(process.env.UI_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe',[
  '--headless','--disable-gpu','--disable-background-networking','--no-first-run',
  '--no-default-browser-check','--disable-extensions','--disable-component-update',
  '--disable-crash-reporter','--disable-breakpad','--no-sandbox',
  `--user-data-dir=${profile}`,'--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','about:blank',
],{windowsHide:true,stdio:'ignore'});
let ws;
try {
  let port;
  for(let i=0;i<150;i++) {
    try { port=(await readFile(resolve(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break; } catch { await cho(100); }
  }
  if(!port)throw Error('Chrome chưa mở cổng kiểm ảnh trên loopback.');
  const tabs=await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((ok,loi)=>{ws.addEventListener('open',ok,{once:true});ws.addEventListener('error',loi,{once:true});});
  let dem=0;const choTra=new Map();
  ws.addEventListener('message',ev=>{
    const kq=JSON.parse(ev.data), p=choTra.get(kq.id);
    if(p){choTra.delete(kq.id);kq.error?p.reject(Error(kq.error.message)):p.resolve(kq.result);}
  });
  function goi(method,params={}) {
    return new Promise((resolve,reject)=>{const id=++dem;choTra.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
  }
  await goi('Page.enable');
  const file=pathToFileURL(resolve('e_hoi_ai/docs/anh-ui-ai-1/may-ai-demo.html')).href;
  for(const [ten,width,height,hash] of [['rong',1160,1340,''],['hep',390,2100,''],['loi',1160,1340,'#loi']]) {
    await goi('Page.navigate',{url:'about:blank'});
    await goi('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false,screenWidth:width,screenHeight:height});
    await goi('Page.navigate',{url:file+hash});
    let dat=false;
    for(let i=0;i<100;i++) {
      const kq=await goi('Runtime.evaluate',{expression:"document.body?.dataset.kiem === 'dat'",returnByValue:true});
      if(kq.result.value){dat=true;break;}await cho(50);
    }
    if(!dat)throw Error(`Màn ${ten} chưa đạt kiểm DOM hoặc bị tràn ngang.`);
    const size=await goi('Runtime.evaluate',{expression:'({rong:innerWidth,noiDung:document.documentElement.scrollWidth})',returnByValue:true});
    if(size.result.value.rong!==width || size.result.value.noiDung>width)throw Error('Sai kích thước viewport hoặc tràn ngang.');
    const png=await goi('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    await writeFile(resolve(`e_hoi_ai/docs/anh-ui-ai-1/may-ai-${ten}.png`),Buffer.from(png.data,'base64'));
    console.log(`[ĐẠT] Ảnh ${ten}: ${width}×${height}; DOM không tràn ngang, KttCore giả.`);
  }
  await goi('Browser.close');
} finally { if(ws)ws.close();chrome.kill(); }
