// Ảnh kiểm UI thật bằng Edge/Chrome headless + KttCore giả, không gói Node ngoài.
// Trình duyệt và toàn bộ hồ sơ tạm nằm ngoài gói engine, trong worktree.
import {spawn} from 'node:child_process';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {moduleUrl,dulieu,DEMO} from './core_gia.mjs';
const browser = process.env.KTT_TRINH_DUYET || resolve(process.env['PROGRAMFILES(X86)'] || process.env.PROGRAMFILES, 'Microsoft/Edge/Application/msedge.exe');
const thuMuc = resolve('.venv',`chup-TS-EX-${Date.now()}`);
const ra = resolve('e_kiem_excel/docs/anh-TS-EX');
await mkdir(thuMuc,{recursive:true}); await mkdir(ra,{recursive:true});
const proc=spawn(browser,['--headless=new','--no-sandbox','--disable-gpu','--no-first-run','--no-default-browser-check',
  '--disable-background-networking','--disable-component-update','--disable-extensions',
  `--user-data-dir=${thuMuc}/ho-so`,'--remote-debugging-port=0','about:blank'],{windowsHide:true,stdio:'ignore'});
let ws, so=0; const cho=new Map();
function goi(method,params={},sessionId) {
  return new Promise((ok,loi)=>{
    const id=++so;
    const timer=setTimeout(()=>{cho.delete(id);loi(Error(`Hết thời hạn ${method}`));},15000);
    cho.set(id,{ok:v=>{clearTimeout(timer);ok(v);},loi:v=>{clearTimeout(timer);loi(v);}});
    ws.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));
  });
}
try {
  let port;
  for (let i=0;i<100;i++) {
    try { port=(await readFile(`${thuMuc}/ho-so/DevToolsActivePort`,'utf8')).split('\n'); break; } catch { await new Promise(r=>setTimeout(r,100)); }
  }
  assert.ok(port,'Không khởi động được trình duyệt headless.');
  ws=new WebSocket(`ws://127.0.0.1:${port[0]}${port[1]}`);
  await new Promise((ok,loi)=>{ws.onopen=ok;ws.onerror=loi;});
  ws.onmessage=({data})=>{const v=JSON.parse(data);const p=cho.get(v.id);if(p){cho.delete(v.id);v.error?p.loi(Error(v.error.message)):p.ok(v.result);}};
  const kq=[];
  for (const [ten,rong,nangLuc,thamSo] of [
    ['toan-ven-desktop',1180,'excel.toan_ven@1',DEMO],
    ['khuon-cot-desktop',1180,'excel.doc_bang@1',{khuon:'tong_quat',tien_te:'VND',khuon_cot_json:JSON.stringify(dulieu.MAU.khuon_cot_json)}],
    ['toan-ven-mobile',390,'excel.toan_ven@1',DEMO]
  ]) {
    const html=`<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
      <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' data:; style-src 'unsafe-inline'; img-src data:">
      <title>DEMO TS-EX · KttCore giả</title><style>body{margin:0;padding:24px;background:#f4f6fa}header{font:14px 'Segoe UI',sans-serif;max-width:1120px;margin:auto auto 12px;color:#64758a}@media(max-width:680px){body{padding:12px}}</style>
      <header>DEMO · Công ty DEMO Ánh Dương · 21/11/2026 · KttCore giả</header><main id="goc"></main>
      <script type="module">import nap from '${moduleUrl}';
      const KttCore={engine(ma){if(ma!=='e_kiem_excel')throw Error('Sai engine');return {};}};
      let phien=7,ts=${JSON.stringify(thamSo)};
      globalThis.man=await nap(document.getElementById('goc'),KttCore,{nang_luc:${JSON.stringify(nangLuc)},
        async doc(){return {tham_so:structuredClone(ts),phien_ban:phien,ds_sheet:['BTH','DEMO']};},
        async luu(giaTri,rv){if(rv!==phien)throw {status:409};ts=structuredClone(giaTri);return {phien_ban:++phien};}});
      document.documentElement.dataset.daNap='true';</script></html>`;
    const tep=resolve(thuMuc,`${ten}.html`); await writeFile(tep,html,'utf8');
    const {targetId}=await goi('Target.createTarget',{url:'about:blank'});
    const {sessionId:sid}=await goi('Target.attachToTarget',{targetId,flatten:true});
    const cd=(m,p={})=>goi(m,p,sid);
    await cd('Page.enable');
    await cd('Emulation.setDeviceMetricsOverride',{width:rong,height:900,deviceScaleFactor:1,mobile:rong<680});
    await cd('Page.navigate',{url:pathToFileURL(tep).href});
    for(let i=0;i<100;i++) {
      const {result}=await cd('Runtime.evaluate',{expression:"document.documentElement.dataset.daNap==='true'",returnByValue:true});
      if(result.value)break;
      if(i===99)throw Error('Màn chưa nạp được.');
      await new Promise(r=>setTimeout(r,100));
    }
    const {result}=await cd('Runtime.evaluate',{expression:`JSON.stringify({rong:innerWidth,noiDung:document.documentElement.scrollWidth,loi:man.kiem().length})`,returnByValue:true});
    const check=JSON.parse(result.value); assert.equal(check.loi,0); assert.ok(check.noiDung<=check.rong,`Tràn ngang ${ten}`);
    // Click nút thật để kiểm wiring DOM, sau đó chụp trạng thái đã kiểm.
    const run=await cd('Runtime.evaluate',{expression:`document.querySelectorAll('button').forEach(b=>{if(b.textContent==='Kiểm tra cài đặt')b.click()}); document.body.innerText.includes('Kiểm tra đạt')`,returnByValue:true});
    assert.equal(run.result.value,true);
    const {cssContentSize:s}=await cd('Page.getLayoutMetrics');
    const png=await cd('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:rong,height:Math.ceil(s.height),scale:1}});
    await writeFile(resolve(ra,`${ten}.png`),Buffer.from(png.data,'base64'));
    kq.push({anh:`${ten}.png`,...check,cao:Math.ceil(s.height)});
    await goi('Target.closeTarget',{targetId});
  }
  await writeFile(resolve(ra,'ket-qua.json'),JSON.stringify(kq,null,2)+'\n','utf8');
  console.log('ĐẠT: 3 ảnh desktop/mobile, không tràn ngang, nút kiểm DOM thật hoạt động.');
} finally {
  if(ws?.readyState===WebSocket.OPEN){await goi('Browser.close').catch(()=>{});ws.close();}
  proc.kill();
}
