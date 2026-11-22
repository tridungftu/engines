// Dựng trang DEMO tự chứa, dùng đúng mã màn và KttCore giả, không máy chủ/mạng.
import {readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {duLieu as d, maMan} from "./nap_man.mjs";
const ra = process.argv[2]; if (!ra) throw new Error("Cần đường dẫn HTML trong worktree.");
const urlMa = "data:text/javascript;base64," + Buffer.from(maMan).toString("base64");
const urlCore = "data:text/javascript;base64," + Buffer.from(readFileSync(new URL("./kttcore_gia.mjs", import.meta.url))).toString("base64");
const css = readFileSync(new URL("../../goi/e_phan_luong/ui/tham_so.css", import.meta.url), "utf8");
const ts = Object.fromEntries(d.CAC_O.map(k => [k, d.vietJson(d.MAU[k])]));
const html = `<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' data:; style-src 'unsafe-inline'; connect-src 'none'; img-src 'none'">
<title>Cài đặt bước Phân luồng · DEMO</title><style>body{margin:0;padding:28px;background:#f3f6fa} .nhan-demo{max-width:1120px;margin:0 auto 18px;color:#61758c;font:14px 'Segoe UI',sans-serif} @media(max-width:680px){body{padding:16px}}</style>
<style>${css}</style><p class="nhan-demo">DEMO · Đã kiểm bằng Core giả (CoreGia) · 21/11/2026</p><main id="goc"></main><script type="module">
import {mount} from ${JSON.stringify(urlMa)};
import {taoCoreGia} from ${JSON.stringify(urlCore)};
const core=taoCoreGia(${JSON.stringify(ts)}), goc=document.getElementById("goc");
const q=new URL(location.href).searchParams;
const opts={nang_luc:"audit.phan_luong@1",KttCore:core.KttCore,doc_tham_so:core.doc_tham_so,luu_tham_so:core.luu_tham_so};
if(q.get("che_do")==="tam_khoa"){delete opts.doc_tham_so;delete opts.luu_tham_so;opts.tham_so=core.tham_so;}
const man=await mount(goc,opts);
if(q.get("che_do")==="cas"){core.phien++;await man.save();}
if(q.get("che_do")==="loi"){const e=goc.querySelector('[data-o="nguong_json.sad.so"]');e.value="3000000001";e.dispatchEvent(new Event("input"));}
const cacO=${JSON.stringify(d.CAC_O)};
if(q.has("the")){const hien=q.get("the").split(",");goc.querySelectorAll("section").forEach((e,i)=>e.hidden=!hien.includes(cacO[i]));}
document.documentElement.setAttribute("data-demo-da-dung","true");
document.documentElement.setAttribute("data-demo-kich-thuoc",JSON.stringify({viewport:innerWidth,html:document.documentElement.clientWidth,body:document.body.clientWidth,goc:goc.clientWidth,tran:document.documentElement.scrollWidth}));
if(document.documentElement.scrollWidth>innerWidth||goc.scrollWidth>goc.clientWidth)document.documentElement.setAttribute("data-tran-ngang","true");
</script></html>`;
writeFileSync(resolve(ra), html, "utf8");
console.log("Đã dựng trang DEMO tự chứa.");
