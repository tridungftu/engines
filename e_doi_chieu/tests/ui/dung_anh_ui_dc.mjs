// Dựng trang DEMO độc lập để Chrome headless chụp, không gọi Core hoặc mạng.
// node e_doi_chieu/tests/ui/dung_anh_ui_dc.mjs
import {readFile, mkdir, writeFile} from "node:fs/promises";
const goi = new URL("../../goi/e_doi_chieu/", import.meta.url);
const dich = new URL("../../docs/ui-dc/", import.meta.url);
const modules = {};
for (const ten of ["cau_hinh", "ket_qua", "loi_ocr"]) {
  modules[ten] = "data:text/javascript;base64," + Buffer.from(await readFile(new URL(`ui/${ten}.js`, goi))).toString("base64");
}
const schema = JSON.parse(await readFile(new URL("cau_hinh.schema.json", goi), "utf8"));
const html = `<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' data:; style-src 'unsafe-inline'; connect-src 'none'; img-src 'none'">
<title>UI-DC · DEMO bằng KttCore giả</title>
<style>body{background:#f4f6fa;color:#203b55;font:18px 'Segoe UI',Arial,sans-serif;margin:0;padding:22px}body>p{font-size:14px;color:#61758b;margin:0 0 12px}main{margin:0 auto;max-width:1120px}main.dc-cau-hinh{max-width:1120px}@media(max-width:42rem){body{padding:12px;font-size:16px}}</style>
<p>DEMO · Đã kiểm bằng Core giả (CoreGia) · 21/11/2026</p><main></main>
<output id="kiem-layout" hidden></output>
<script type="module">
const modules = ${JSON.stringify(modules)}, ch = ${JSON.stringify(schema.examples[0])};
const mode = location.hash.slice(1), root = document.querySelector('main');
globalThis.fetch = () => {throw Error('Cấm mạng trong DEMO');};
globalThis.XMLHttpRequest = globalThis.WebSocket = class {constructor(){throw Error('Cấm mạng');}};
let rv = 7;
const core = {engine(ma) {
  if(ma !== 'e_doi_chieu') throw Error('Sai engine DEMO');
  return {cau_hinh: {async doc(){return {cau_hinh: mode === 'thieu-bo' ? {} : structuredClone(ch), phien_ban_cau_hinh:rv};},
    async luu(v, ver){if(mode === 'cas' || ver !== rv) throw {status:409};return {phien_ban_cau_hinh:++rv};}},
    ngan:{async doc(){return {row_version:7};},async tim(){return {danh_sach:[{gia_tri:{noi_dung:JSON.stringify({ocr:'hơp đồng',word:'hợp đồng',lan_gap:[{}],trang_thai:'cho_duyet'})}}],tiep:null};}}};
}};
if(mode === 'ket-qua') {
  const {default: ve} = await import(modules.ket_qua);
  const view = {ma_luot:'DEMO-luot',row_version:7,quyen:{xac_nhan:false},xac_nhan:[],
    dieu_kien_module:{du_dieu_kien_de_nghi:false},bao_cao:{ket_luan:'can_xem',da_kiem_du:false,
    tom_tat:{so_nghiem_trong:0,so_can_xem:1,so_hinh_thuc:0,so_nhieu_ocr:0,so_vung_sua_tay:null,so_trang_ocr_kem:null},
    tong_hop:{phan_chua_kiem:['sua_tay','do_chat_luong_ocr']},
    diem_lech:[{ma_diem:'DEMO-diem',muc:'can_xem',word:{nguyen_van:'Công ty DEMO Ánh Dương giao hàng trong 30 ngày.',vi_tri:{}},ban_ky:{nguyen_van:'Công ty DEMO Ánh Dương giao hàng trong 30 ngày làm việc.',vi_tri:{so_trang:1}},quy_tac_trung:[]}],
    anh_trang:[],bao_cao_pdf:{tep:{tep_id:'DEMO-pdf'},bam:'DEMO'}}};
  await ve(root,core,{ma_luot:'DEMO-luot',cua:{async doc_ket_qua(){return view;}}});
} else if(mode === 'loi-ocr') {
  const {default:ve}=await import(modules.loi_ocr);await ve(root,core,{nguCanhDaGan:true});
} else {
  const {default:ve}=await import(modules.cau_hinh);await ve(root,core);
  if(mode === 'nang-cao') root.querySelector('details').open=true;
  if(mode === 'loi-nhap') {
    const o=root.querySelector('[name=so_trang_toi_da]');o.value='61';o.dispatchEvent(new Event('input'));
    root.querySelector('form').dispatchEvent(new Event('submit',{cancelable:true}));
  }
  if(mode === 'cas') root.querySelector('form').dispatchEvent(new Event('submit',{cancelable:true}));
}
await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
document.querySelector('#kiem-layout').textContent=JSON.stringify({mode,viewport:innerWidth,
  rong:document.documentElement.scrollWidth,khongTran:document.documentElement.scrollWidth<=innerWidth,
  cot:root.querySelector('.dc-tran')?getComputedStyle(root.querySelector('.dc-tran')).gridTemplateColumns:null,
  nangCaoMo:root.querySelector('details')?.open??null});
document.documentElement.dataset.daDung='true';
</script></html>`;
await mkdir(dich, {recursive:true});
await writeFile(new URL("demo.html", dich), html, "utf8");
console.log("Đã dựng e_doi_chieu/docs/ui-dc/demo.html; mở với #co-ban, #nang-cao, #loi-nhap, #cas, #thieu-bo, #ket-qua hoặc #loi-ocr.");
