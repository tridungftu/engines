// HTML tự chứa: màn thật + két DEMO trong RAM; CSP chặn toàn bộ mạng.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
const ui=await readFile(new URL('../../goi/e_hoi_ai/ui/cloud.js',import.meta.url),'utf8');
const gia=await readFile(new URL('./cloud_core_gia.mjs',import.meta.url),'utf8');
const dich=new URL('../../docs/anh-ui-ai-2/',import.meta.url);
await mkdir(dich,{recursive:true});
const html=`<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'">
<title>DEMO Cổng Cloud AI — KttCore giả</title>
<style>body{margin:0;background:#f4f6fa;padding:22px;font-family:'Segoe UI',sans-serif}.demo{max-width:1100px;margin:0 auto 16px;color:#657a90;font-size:13px}main{margin:auto}@media(max-width:640px){body{padding:12px}}</style>
<p class="demo">DEMO · KttCore giả · 22/11/2026 · Chưa nối Core hoặc Cloud thật</p><main></main>
<script type="module">
const assert={equal(a,b){if(a!==b)throw Error('Sai hợp đồng DEMO');}};
${gia.replace("import assert from 'node:assert/strict';",'').replace('export function','function')}
${ui.replace('export default async function','async function')}
const ctx=taoKet({loiDoc:location.hash==='#loi'});
await congCloud(document.querySelector('main'),ctx.core);
if(location.hash==='#cas'){
  ctx.state.phien_ban=10;
  const key=document.querySelector('input[type=password]');key.value='DEMO-KEY-THAY-7XBB';
  document.querySelector('form').dispatchEvent(new Event('submit',{cancelable:true}));
  await new Promise(r=>setTimeout(r,0));
  if(!document.body.textContent.includes('Key đã được người khác sửa'))throw Error('Thiếu lỗi CAS');
}
if(document.documentElement.scrollWidth>innerWidth)throw Error('Màn bị tràn ngang');
if(document.querySelector('input[type=password]').value)throw Error('Ô key chưa được xóa');
document.body.dataset.kiem='dat';
</script></html>`;
await writeFile(new URL('cloud-ai-demo.html',dich),html,'utf8');
console.log('Đã dựng e_hoi_ai/docs/anh-ui-ai-2/cloud-ai-demo.html (DEMO, không mạng).');
