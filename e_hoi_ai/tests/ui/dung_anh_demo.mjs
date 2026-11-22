// Dựng HTML DEMO từ chính màn gói; Chrome headless chụp lại, không cần mạng.
// Chạy: node e_hoi_ai/tests/ui/dung_anh_demo.mjs
import {readFile,writeFile,mkdir} from 'node:fs/promises';
const ui=await readFile(new URL('../../goi/e_hoi_ai/ui/cau_hinh.js',import.meta.url),'utf8');
const dich=new URL('../../docs/anh-ui-ai-1/',import.meta.url);
await mkdir(dich,{recursive:true});
const html=`<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'">
<title>DEMO Máy AI — KttCore giả</title>
<style>body{margin:0;background:#f4f6fa;padding:22px;font-family:'Segoe UI',sans-serif}.demo{max-width:1100px;margin:0 auto 16px;color:#657a90;font-size:13px}main{margin:auto}@media(max-width:640px){body{padding:12px}}</style>
<p class="demo">DEMO · KttCore giả · 21/11/2026 · Chưa nối Core hoặc máy AI thật</p><main></main>
<script type="module">
${ui.replace('export default async function','async function')}
const models=[{id_model:'model-demo',kha_dung:true},{id_model:'model-demo-b',kha_dung:true}];
let phien=7;
const core={engine(ma){if(ma!=='e_hoi_ai')throw Error('Sai engine');return {
 cau_hinh:{async doc(){return {cau_hinh:{local_ai:{url:'http://127.0.0.1:11434',timeout_giay:60},quy_tac_model:[{mau_ma_prompt:'demo.*',uu_tien:'model-demo',du_phong:['model-demo-b']}]},phien_ban_cau_hinh:phien}},async luu(gt,rv){if(rv!==phien)throw {status:409};return {phien_ban_cau_hinh:++phien}}},
 ngan:{async tim(){return {danh_sach:models.map(gia_tri=>({gia_tri})),tiep:null}}},
 async thao_tac(ma,gt){if(location.hash==='#loi')return {ket_noi:false,models:[]};return ma==='tim_may_ai'?{danh_sach:[],so_da_kiem:2}:{ket_noi:true,models,kiem_luc:'2026-11-21T14:25:00Z'}}
}}};
await cauHinh(document.querySelector('main'),core);
document.querySelector('button').click();
await new Promise(resolve=>setTimeout(resolve,0));
if(document.querySelectorAll('input').length<3)throw Error('Thiếu ô cấu hình');
if(document.documentElement.scrollWidth>innerWidth)throw Error('Màn bị tràn ngang');
document.body.dataset.kiem='dat';
</script></html>`;
await writeFile(new URL('may-ai-demo.html',dich),html,'utf8');
console.log('Đã dựng e_hoi_ai/docs/anh-ui-ai-1/may-ai-demo.html (DEMO, không mạng).');
