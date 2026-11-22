// Node, DOM/KttCore giả, chỉ DEMO; không mạng hoặc trình duyệt Core thật.
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import test from "node:test";

const base = new URL("../../goi/e_doi_chieu/", import.meta.url);
const code = await readFile(new URL("ui/loi_ocr.js", base), "utf8");
const {default: loiOCR} = await import(`data:text/javascript;base64,${Buffer.from(code).toString("base64")}`);
const chCode = await readFile(new URL("ui/cau_hinh.js", base), "utf8");
const {default: cauHinh} = await import(`data:text/javascript;base64,${Buffer.from(chCode).toString("base64")}`);
globalThis.fetch = () => {throw Error("Cấm mạng");};
class E {
  constructor(the,doc) {this.the=the; this.ownerDocument=doc; this.con=[]; this.sk={}; this.tt={}; this._chu=""; this.value=""; this.disabled=false; this.classList={add(){}};}
  set textContent(v) {this._chu=String(v); this.con=[];}
  get textContent() {return this._chu;}
  set innerHTML(_) {assert.fail("Không dùng HTML");}
  appendChild(e) {this.con.push(e);return e;}
  replaceChildren() {this.con=[];this._chu="";}
  setAttribute(k,v) {this.tt[k]=v;}
  addEventListener(k,f) {this.sk[k]=f;}
  async goi(k) {await this.sk[k]?.({preventDefault(){}});}
  reportValidity() {return true;}
}
const all = e=>[e,...e.con.flatMap(all)];
const chu = e=>e.textContent+" "+e.con.map(chu).join(" ");
const nut = (e,ten)=>all(e).find(n=>n.the==="button"&&n.textContent===ten);
function root() {const d={createElement:t=>new E(t,d)};return new E("main",d);}
const row = (o={})=>({gia_tri:{noi_dung:JSON.stringify({word:"hợp",ocr:"hơp",lan_gap:[{ma_xac_nhan:"DEMO-an"}],trang_thai:"cho_duyet",...o})}});
async function dung({context=true,fail=false,pages=null}={}) {
  const r=root(), calls=[];
  const core={engine(ma) {assert.equal(ma,"e_doi_chieu");return {ngan:{
    async tim(bang,q) {calls.push(q);assert.equal(bang,"loi_ocr_de_xuat");assert.equal(q.gioi_han,100);
      if(fail) throw Error("DEMO-loi-khong-lo");
      return pages?pages(q):{danh_sach:[row()],tiep:null};},
    ghi_lo(){assert.fail("Không ghi trực tiếp ngăn");},
  },cau_hinh:{doc(){assert.fail("Màn danh mục không đọc cấu hình");}},thao_tac(){assert.fail("Chưa có thao tác SDK");}};}};
  await loiOCR(r,core,{nguCanhDaGan:context,quyen:["admin_core"]});return {r,calls};
}
test("đọc đề xuất không tự duyệt hoặc tự cấp quyền",async()=>{
  const {r,calls}=await dung();assert.equal(calls.length,1);
  assert.match(chu(r),/hơp.*hợp.*1.*Chờ quản trị viên duyệt/s);
  assert.deepEqual(all(r).filter(e=>e.the==="button").map(e=>e.textContent),["Tải lại danh mục","Xem trang tiếp"]);
  assert.match(chu(r),/Đề xuất chưa duyệt không ảnh hưởng kết quả máy/);
  assert.doesNotMatch(chu(r),/DEMO-an/);
});
test("thiếu ngữ cảnh Core không đọc ngăn dù có chuỗi quyền Admin",async()=>{
  const {r,calls}=await dung({context:false});assert.equal(calls.length,0);
  assert.match(chu(r),/Chưa đọc được danh mục có quyền/);
});
test("lỗi có câu Việt cố định, tải lại, không lộ lỗi kỹ thuật",async()=>{
  const {r,calls}=await dung({fail:true});assert.doesNotMatch(chu(r),/DEMO-loi/);
  await nut(r,"Tải lại danh mục").goi("click");assert.equal(calls.length,2);
});
test("phân trang đúng cursor, không cắt ngầm danh sách",async()=>{
  const {r,calls}=await dung({pages:q=>q.tiep?{danh_sach:[row({trang_thai:"da_duyet"})],tiep:null}:{danh_sach:[row()],tiep:"DEMO-cursor"}});
  assert.equal(nut(r,"Xem trang tiếp").hidden,false);
  await nut(r,"Xem trang tiếp").goi("click");assert.equal(calls[1].tiep,"DEMO-cursor");
  assert.match(chu(r),/Đã duyệt cho bộ phiên bản mới/);
  await nut(r,"Tải lại danh mục").goi("click");assert.equal(calls[2].tiep,null);
});
test("XSS là chữ, không HTML/mạng/eval/ghi kho",async()=>{
  const x='<img src=x onerror="DEMO()"><script>DEMO()</script>';
  const {r}=await dung({pages:()=>({danh_sach:[row({word:x,ocr:x})],tiep:null})});
  assert.ok(chu(r).includes(x));assert.ok(!all(r).some(e=>["img","script"].includes(e.the)));
  assert.doesNotMatch(code,/innerHTML|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage|\.ghi_lo\s*\(/);
});
test("rỗng và bản ghi lỗi không giả thành đã duyệt",async()=>{
  const a=await dung({pages:()=>({danh_sach:[],tiep:null})});assert.match(chu(a.r),/Chưa có đề xuất/);
  const b=await dung({pages:()=>({danh_sach:[{noi_dung:"DEMO-JSON-hong"}],tiep:null})});assert.match(chu(b.r),/Chưa đọc được/);
});
test("màn cấu hình giữ nguyên ngưỡng đã đo duyệt khi lưu giới hạn",async()=>{
  const r=root(), saved=[];
  const n={so_lan:2,phien_ban:"DEMO-1",nguon_do:"DEMO-gia",ma_phe_duyet:"DEMO-duyet-gia"};
  const ch=Object.fromEntries(["phien_ban_cau_hinh","ma_bo_chuan_hoa","bam_bo_chuan_hoa","ma_tu_dien","bam_tu_dien","phuong_phap_detector","phien_ban_detector"].map(k=>[k,"DEMO-1"]));
  ch.hoc_loi_ocr=n;
  await cauHinh(r,{engine(){return {cau_hinh:{async doc(){return {cau_hinh:ch,phien_ban_cau_hinh:7};},
    async luu(v,rv){assert.equal(rv,7);saved.push(v);return {phien_ban_cau_hinh:8};}}};}});
  await all(r).find(e=>e.the==="form").goi("submit");
  assert.equal(saved.length,1);assert.deepEqual(saved[0].hoc_loi_ocr,n);
  assert.doesNotMatch(chu(all(r).find(e=>e.the==="section")),/DEMO-duyet-gia/);
  assert.match(chu(all(r).find(e=>e.the==="details")),/DEMO-duyet-gia/);
});
