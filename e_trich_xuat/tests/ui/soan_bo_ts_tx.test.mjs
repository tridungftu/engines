import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";

const ma = await readFile(new URL("../../goi/e_trich_xuat/ui/soan_bo_tham_so.js",import.meta.url),"utf8");
const { nap } = await import("data:text/javascript;base64,"+Buffer.from(ma).toString("base64"));
const python = process.env.TX_PYTHON || fileURLToPath(new URL("../../../.venv/Scripts/python.exe",import.meta.url));
const cau = fileURLToPath(new URL("cong_soan_bo.py",import.meta.url));
const dem = new Map();
const goi = vao => {
  const khoa = JSON.stringify(vao);
  if (!dem.has(khoa)) dem.set(khoa,JSON.parse(execFileSync(python,["-B",cau],{input:khoa,encoding:"utf8",maxBuffer:1024*1024})));
  return structuredClone(dem.get(khoa));
};
const boMau = () => ({phien_ban:1,module:"module_demo",loai_hop_dong:"DEMO",phien_ban_bo:"demo-1",quy_tac:[],
  cac_dong:[{ma:"TT-01",nhom:"Thông tin chung",mo_ta:"Trích tên hợp đồng DEMO",tk:"tên",bk:"",dung:true,muc:1,bat_buoc:"",loai_tru:"",luon_cloud:false}]});
const mau = () => goi({lenh:"kiem_bo",bo:boMau()});

class PhanTu {
  constructor(ten,doc) { this.ten=ten;this.ownerDocument=doc;this.children=[];this.listeners=new Map();this.textContent="";this.value="";this.disabled=false; }
  append(...ds) { this.children.push(...ds); }
  replaceChildren(...ds) { this.children=[...ds]; }
  setAttribute(k,v) { this[k]=v; }
  addEventListener(k,h) { this.listeners.set(k,h); }
  removeEventListener(k,h) { if (this.listeners.get(k)===h) this.listeners.delete(k); }
  async gui(k) { if (!this.disabled) return this.listeners.get(k)?.({preventDefault(){}}); }
}
function tatCa(goc) { return [goc,...goc.children.flatMap(tatCa)]; }
const chu = goc => tatCa(goc).map(e=>e.textContent).join("\n");
async function man({thao,luu,tham_so=mau().tham_so,...khac}={}) {
  const doc={createElement(ten){return new PhanTu(ten,doc);}},goc=new PhanTu("root",doc),cacGoi=[];
  const KttCore={engine(ma){assert.equal(ma,"e_trich_xuat");return {async thao_tac(ten,vao){
    assert.equal(ten,"soan_bo_tham_so");cacGoi.push(structuredClone(vao));return thao ? thao(vao) : goi(vao);
  }};}};
  const api=await nap({goc,KttCore,tham_so,phien_ban:7,luu,...khac});
  return {goc,api,cacGoi,o:k=>tatCa(goc).find(e=>e["data-truong"]===k),nut:t=>tatCa(goc).find(e=>e.ten==="button"&&e.textContent===t),text:()=>chu(goc)};
}

test("đọc bộ, sửa từng trường, băm đúng bytes và xuất hai chuỗi",async()=>{
  const m=await man(); assert.equal(m.cacGoi[0].lenh,"doc_bo");
  m.o("cac_dong.0.mo_ta").value="Trích công ty DEMO Ánh Dương 🌞";await m.o("cac_dong.0.mo_ta").gui("input");
  const kq=await m.api.xuat();assert.deepEqual(Object.keys(kq).sort(),["bam_bo_tham_so","bo_tham_so_json"]);
  assert.equal(JSON.parse(kq.bo_tham_so_json).cac_dong[0].mo_ta,"Trích công ty DEMO Ánh Dương 🌞");
  assert.equal(goi({lenh:"doc_bo",tham_so:kq}).dat,true);assert.match(m.text(),/Đã xuất tham số/);
});
test("lưu vào module dùng CAS và tiếp tục phiên bản mới",async()=>{
  const ds=[];const m=await man({luu:async(v,p)=>{ds.push([v,p]);return {phien_ban:p+1};}});
  await m.api.xuat();await m.api.xuat();assert.deepEqual(ds.map(x=>x[1]),[7,8]);assert.match(m.text(),/Đã lưu bộ vào module/);
});
test("CAS xung đột khóa lưu tiếp, giữ nội dung và không lộ chi tiết",async()=>{
  let n=0;const m=await man({luu:async()=>{n++;throw {status:409,message:"DEMO_CHI_TIET_BI_MAT"};}});
  await m.api.xuat();await m.api.xuat();assert.equal(n,1);assert.match(m.text(),/người khác sửa, tải lại/);
  assert.doesNotMatch(m.text(),/DEMO_CHI_TIET_BI_MAT/);assert.equal(m.o("cac_dong.0.ma").value,"TT-01");
});
test("lỗi nhập sát ô; không gửi kiểm hay lưu khi sai",async()=>{
  const m=await man();const n=m.cacGoi.length;
  for(const [k,v] of [["ma","SAI"],["nhom",""],["mo_ta",""],["tk","x".repeat(61)]]) {
    m.o(`cac_dong.0.${k}`).value=v;await m.o(`cac_dong.0.${k}`).gui("input");
    assert.equal(m.o(`cac_dong.0.${k}`)["aria-invalid"],"true");
  }
  assert.equal(await m.api.xuat(),null);assert.equal(m.cacGoi.length,n);
});
test("nút kiểm thành công và lỗi E1 giữ bảng để sửa",async()=>{
  const m=await man();await m.nut("Kiểm tra và tính băm").gui("click");assert.match(m.text(),/Đã kiểm tra/);
  const n=await man({thao:vao=>vao.lenh==="doc_bo"?goi(vao):{dat:false,loi:[{truong:"cac_dong.0.ma",thong_bao:"Dòng 1: mã trùng; đổi mã."}]}});
  await n.nut("Kiểm tra và tính băm").gui("click");assert.match(n.text(),/mã trùng/);assert.equal(n.o("cac_dong.0.ma")["aria-invalid"],"true");
});
test("đọc/kiểm lỗi không hiện thông báo kỹ thuật, không xuất đè bộ lỗi",async()=>{
  const m=await man({thao:()=>{throw new Error("DEMO_CHI_TIET_BI_MAT");}});
  assert.doesNotMatch(m.text(),/DEMO_CHI_TIET_BI_MAT/);assert.match(m.text(),/Không thực hiện được/);
  assert.equal(await m.api.xuat(),null);
  const n=await man({thao:vao=>{if(vao.lenh==="doc_bo")return goi(vao);throw new Error("DEMO_CHI_TIET_BI_MAT");}});
  assert.equal(await n.api.xuat(),null);assert.match(n.text(),/Không thực hiện được/);
});
test("thêm/xóa dòng và quy tắc, giữ nguyên cờ Cloud, không gọi bí mật",async()=>{
  const m=await man();await m.nut("Thêm tham số").gui("click");
  for(const[k,v]of [["ma","TT-02"],["nhom","DEMO"],["mo_ta","Giá trị 1.000.000 VND"]]){m.o(`cac_dong.1.${k}`).value=v;await m.o(`cac_dong.1.${k}`).gui("input");}
  await m.nut("Thêm quy tắc").gui("click");
  m.o("quy_tac.0.ma_tham_so").value="TT-01;TT-02";await m.o("quy_tac.0.ma_tham_so").gui("input");
  m.o("cac_dong.0.luon_cloud").checked=true;await m.o("cac_dong.0.luon_cloud").gui("input");
  const kq=await m.api.xuat();const bo=JSON.parse(kq.bo_tham_so_json);
  assert.equal(bo.cac_dong.length,2);assert.equal(bo.cac_dong[0].luon_cloud,true);assert.equal(bo.quy_tac.length,1);
  await m.nut("Xóa quy tắc").gui("click");await m.nut("Xóa dòng").gui("click");
  assert.equal(JSON.parse((await m.api.xuat()).bo_tham_so_json).cac_dong.length,1);
});
test("nhập Excel hợp lệ, sai tệp và quá trần không cắt ngầm",async()=>{
  const m=await man();const tep=tatCa(m.goc).find(e=>e.type==="file");
  tep.files=[{name:"DEMO.xlsx",size:3,arrayBuffer:async()=>new Uint8Array([1,2,3]).buffer}];
  await m.nut("Nhập Excel").gui("click");assert.match(m.text(),/Excel .xlsx hợp lệ/);assert.equal(m.o("cac_dong.0.ma").value,"TT-01");
  const n=m.cacGoi.length;tep.files=[{name:"DEMO.xlsx",size:2*1024*1024+1}];await m.nut("Nhập Excel").gui("click");assert.equal(m.cacGoi.length,n);
  // Excel do SDK E1 tạo; không tải thư viện hoặc mạng.
  const raw=execFileSync(python,["-B","-c","import sys; sys.path.insert(0,'e_trich_xuat/tests'); from test_soan_bo_ts_tx import excel; import base64; print(base64.b64encode(excel()).decode())"],{encoding:"utf8",env:{...process.env,PYTHONPATH:"e_trich_xuat/goi/e_trich_xuat"}}).trim();
  const bytes=Buffer.from(raw,"base64");tep.files=[{name:"DEMO.xlsx",size:bytes.length,arrayBuffer:async()=>bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength)}];
  await m.nut("Nhập Excel").gui("click");assert.match(m.text(),/Đã kiểm tra/);assert.equal(m.cacGoi.at(-1).lenh,"nhap_excel");
});
test("chặn gửi lặp và bỏ phản hồi cũ nếu sửa khi đang kiểm",async()=>{
  let tra;const m=await man({thao:vao=>vao.lenh==="doc_bo"?goi(vao):new Promise(r=>{tra=()=>r(goi(vao));})});
  const p=m.api.xuat();await m.api.xuat();assert.equal(m.cacGoi.length,2);
  m.o("cac_dong.0.mo_ta").value="DEMO đã đổi";await m.o("cac_dong.0.mo_ta").gui("input");tra();assert.equal(await p,null);
  assert.equal(m.o("cac_dong.0.mo_ta").value,"DEMO đã đổi");assert.doesNotMatch(m.text(),/Đã xuất tham số/);
});
test("tháo màn bỏ listener và không vẽ phản hồi muộn",async()=>{
  let tra;const m=await man({thao:vao=>vao.lenh==="doc_bo"?goi(vao):new Promise(r=>{tra=()=>r(goi(vao));})});
  const cacEl=tatCa(m.goc),p=m.api.xuat();m.api.dong();tra();await p;
  assert.equal(m.goc.children.length,0);assert.ok(cacEl.every(e=>e.listeners.size===0));
});
test("màn chỉ dùng cổng engine, không mạng/lưu đĩa/mã thực thi động",()=>{
  assert.doesNotMatch(ma,/\bfetch\s*\(|XMLHttpRequest|WebSocket|\beval\s*\(|innerHTML|localStorage|sessionStorage|indexedDB/);
  assert.doesNotMatch(ma,/\.bi_mat|\.ngan|\.cau_hinh/); // TS-TX không chứa bí mật hoặc kho bộ riêng.
  assert.match(ma,/@media\(max-width:700px\)/);
});
