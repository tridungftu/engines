// Chạy Node để dựng HTML DEMO tự chứa, sau đó chụp bằng Chrome headless offline.
import {readFile, mkdir, writeFile} from "node:fs/promises";
import {fileURLToPath} from "node:url";
const ui = await readFile(new URL("../../goi/e_doi_chieu/ui/soan_quy_tac.js", import.meta.url), "utf8");
const fake = await readFile(new URL("./ts_dc_gia.mjs", import.meta.url), "utf8");
const out = new URL("../../docs/anh-ts-dc/", import.meta.url);
await mkdir(out, {recursive:true});
const dataUrl = s => "data:text/javascript;base64," + Buffer.from(s).toString("base64");
for (const mode of ["rong", "vung", "loi", "cas"]) {
  const html = `<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TS-DC · DEMO CoreGia</title><style>body{margin:0;padding:22px;background:#f4f6fa}body>p{font:14px 'Segoe UI',sans-serif;color:#62758b;max-width:1100px;margin:auto}</style>
<p>DEMO · Cài đặt bước Đối chiếu · 21/11/2026 · đã kiểm bằng Core giả (CoreGia)</p><main id="goc"></main>
<script type="module">
import soan, {xuatThamSo} from "${dataUrl(ui)}";
import {BO_DEMO,coreGia,cuaGia} from "${dataUrl(fake)}";
globalThis.fetch = () => {throw Error('Cấm mạng DEMO');};
globalThis.WebSocket = globalThis.XMLHttpRequest = class {constructor(){throw Error('Cấm mạng DEMO');}};
const bo = structuredClone(BO_DEMO);
if ('${mode}' !== 'rong') bo.quy_tac_cung.vung_bao_ve.push({ben:'word',loai:'ben_ky',bat_dau:0,ket_thuc:21,nguyen_van:'Công ty DEMO Ánh Dương',bam_van_ban:'sha256:'+'a'.repeat(64)});
const fake = cuaGia(await xuatThamSo(JSON.stringify(bo,null,2)), {xungDot:'${mode}'==='cas'});
await soan(document.querySelector('#goc'),coreGia(),{cua:fake.cua});
if ('${mode}' === 'loi') {const e=document.querySelector('[aria-label="Nguyên văn"]');e.value='';e.dispatchEvent(new Event('input'));}
if ('${mode}' === 'cas') {const b=[...document.querySelectorAll('button')].find(b=>b.textContent==='Áp dụng vào bước');b.click();}
document.documentElement.dataset.xong='true';
</script></html>`;
  const path = new URL(`DEMO-${mode}.html`, out); await writeFile(path, html, "utf8");
  console.log(fileURLToPath(path));
}
