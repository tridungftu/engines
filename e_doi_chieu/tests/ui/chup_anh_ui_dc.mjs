// Chỉ công cụ chụp DEMO: CDP loopback của Chrome cục bộ; trang không gọi mạng.
// node e_doi_chieu/tests/ui/chup_anh_ui_dc.mjs <chrome.exe>
// Không nằm trong bộ node --test; không thêm thư viện hoặc đường máy cố định.
import {spawn} from "node:child_process";
import {readFile, writeFile, mkdir} from "node:fs/promises";
import {fileURLToPath} from "node:url";
import assert from "node:assert/strict";
const chrome = process.argv[2];
if (!chrome) throw Error("Cần truyền chương trình Chrome để chụp DEMO.");
const base = new URL("../../../", import.meta.url);
const dich = new URL("e_doi_chieu/docs/ui-dc/", base);
const profile = new URL(`.dong-goi-thu/chrome-ui-dc-${Date.now()}/`, base);
await mkdir(profile, {recursive: true});
const processChrome = spawn(chrome, ["--headless", "--no-sandbox", "--disable-gpu", "--in-process-gpu",
  "--disable-software-rasterizer", "--no-first-run", "--disable-background-networking", "--disable-extensions",
  "--disable-sync", "--hide-scrollbars", "--remote-debugging-port=0", `--user-data-dir=${fileURLToPath(profile)}`],
  {windowsHide: true, stdio: "ignore"});
const cho = ms => new Promise(resolve => setTimeout(resolve, ms));
let ws;
try {
  let active;
  for (let i = 0; i < 100; i++) {
    try {active = (await readFile(new URL("DevToolsActivePort", profile), "utf8")).trim().split(/\r?\n/); break;}
    catch {await cho(100);}
  }
  if (!active) throw Error("Chrome chưa mở cổng chụp DEMO.");
  ws = new WebSocket(`ws://127.0.0.1:${active[0]}${active[1]}`);
  await new Promise((resolve, reject) => {ws.addEventListener("open", resolve, {once:true}); ws.addEventListener("error", reject, {once:true});});
  const choTra = new Map(); let id = 0;
  ws.addEventListener("message", ev => {
    const v = JSON.parse(ev.data), p = choTra.get(v.id);
    if (p) {choTra.delete(v.id); clearTimeout(p.timeout); v.error ? p.reject(Error(v.error.message)) : p.resolve(v.result);}
  });
  function goi(method, params = {}, sessionId) {
    return new Promise((resolve,reject) => {
      const n = ++id, timeout = setTimeout(() => {choTra.delete(n); reject(Error(`Quá hạn ${method}`));}, 10000);
      choTra.set(n,{resolve,reject,timeout}); ws.send(JSON.stringify({id:n,method,params,...(sessionId ? {sessionId} : {})}));
    });
  }
  const {targetId} = await goi("Target.createTarget", {url:"about:blank"});
  const {sessionId} = await goi("Target.attachToTarget", {targetId,flatten:true});
  const tab = (method, params) => goi(method, params, sessionId);
  await tab("Page.enable");
  const baoCao = [];
  for (const [ten,width,height] of [["co-ban",1200,980],["nang-cao",1200,2350],["mobile",390,1650],
    ["loi-nhap",1200,1050],["cas",1200,1050],["thieu-bo",1200,1050],["ket-qua",1200,1050],["loi-ocr",1200,750]]) {
    await tab("Emulation.setDeviceMetricsOverride",{width,height,deviceScaleFactor:1,mobile:false});
    const url = new URL("demo.html",dich); url.search = ten; url.hash = ten === "mobile" ? "co-ban" : ten;
    await tab("Page.navigate",{url:url.href});
    let rendered = false;
    for(let i=0;i<50;i++) {
      const r=await tab("Runtime.evaluate",{expression:"document.documentElement.dataset.daDung === 'true'",returnByValue:true});
      if(r.result?.value) {rendered=true;break;} await cho(100);
    }
    assert.ok(rendered, `Chưa dựng ${ten}`);
    const r = await tab("Runtime.evaluate",{expression:"document.querySelector('#kiem-layout').textContent",returnByValue:true});
    const metrics = JSON.parse(r.result.value);
    assert.equal(metrics.mode, ten === "mobile" ? "co-ban" : ten);
    assert.equal(metrics.viewport,width); assert.equal(metrics.khongTran,true,`${ten} bị tràn ngang`);
    const {data} = await tab("Page.captureScreenshot",{format:"png",captureBeyondViewport:true});
    await writeFile(new URL(`${ten}.png`,dich),Buffer.from(data,"base64"));
    baoCao.push({anh:`${ten}.png`,...metrics}); console.log(`Đã chụp ${ten}: ${width}px, không tràn ngang.`);
  }
  await writeFile(new URL("kiem-layout.json",dich),JSON.stringify(baoCao,null,2)+"\n","utf8");
  await goi("Browser.close");
} finally {ws?.close(); if(processChrome.exitCode === null) processChrome.kill();}
