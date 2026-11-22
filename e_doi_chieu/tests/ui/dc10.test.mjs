// Node + DOM/KttCore trong RAM, không dependency hoặc mạng; không là trình duyệt Core thật.
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import test from "node:test";

const goi = new URL("../../goi/e_doi_chieu/", import.meta.url);
const nguon = {};
async function nap(ten) {
  const code = await readFile(new URL(`ui/${ten}.js`, goi), "utf8"); nguon[ten] = code;
  return import(`data:text/javascript;base64,${Buffer.from(code).toString("base64")}`);
}
const {default: cauHinh, TRUONG_SO} = await nap("cau_hinh");
const {default: ketQua, dinhDang} = await nap("ket_qua");
globalThis.fetch = () => {throw Error("Cấm mạng trong kiểm UI DEMO");};
globalThis.XMLHttpRequest = class {constructor() {throw Error("Cấm mạng");}};
globalThis.WebSocket = class {constructor() {throw Error("Cấm mạng");}};

class PhanTu {
  constructor(the, doc) {
    this.the = the; this.ownerDocument = doc; this.con = []; this.suKien = {}; this.thuocTinh = {};
    this.classList = {add: (...ten) => {this.lop.push(...ten);}}; this.lop = [];
    this.value = ""; this._chu = ""; this.disabled = false; this.hidden = false;
  }
  set textContent(v) {this._chu = String(v); this.con = [];}
  get textContent() {return this._chu;}
  set innerHTML(_) {throw Error("Cấm HTML");}
  set src(_) {throw Error("Chỉ Core được dựng phần xem tệp");}
  set href(_) {throw Error("Chỉ Core được dựng phần xem tệp");}
  appendChild(e) {this.con.push(e); return e;}
  replaceChildren() {this.con = []; this._chu = "";}
  setAttribute(k, v) {this.thuocTinh[k] = v;}
  addEventListener(k, fn) {this.suKien[k] = fn;}
  reportValidity() {return true;}
  async goi(k) {await this.suKien[k]?.({preventDefault() {}});}
}
const tatCa = e => [e, ...e.con.flatMap(tatCa)];
const chu = e => e.textContent + " " + e.con.map(chu).join(" ");
const tim = (e, the, ten) => tatCa(e).find(n => n.the === the && (!ten || n.textContent === ten));
const nhap = (e, ten) => tim(e, "label", ten).con[0];
const nut = (e, ten) => tim(e, "button", ten);
function goc() {
  const doc = {createElement: the => new PhanTu(the, doc)};
  return new PhanTu("main", doc);
}
const CH = {phien_ban_cau_hinh: "DEMO-pb-an", ma_bo_chuan_hoa: "DEMO-bo-an", bam_bo_chuan_hoa: "sha256:DEMO-an",
  ma_tu_dien: "DEMO-td-an", bam_tu_dien: "sha256:DEMO-td-an", phuong_phap_detector: "DEMO-det-an", phien_ban_detector: "DEMO-pb-det-an"};
function mau() {
  const html = '<img src=x onerror="DEMO()"><script>DEMO()</script>';
  const diem = Object.keys({nghiem_trong: 1, can_xem: 1, hinh_thuc: 1, nhieu_ocr: 1}).map((muc, i) => ({
    ma_diem: `DEMO-diem-${i}`, muc, word: {nguyen_van: i === 0 ? html : "Công ty DEMO Ánh Dương", vi_tri: {}},
    ban_ky: {nguyen_van: "Bản ký DEMO", vi_tri: {so_trang: 1, hop: [0, 0, 2, 2], don_vi: "px"}},
    ly_do_ai: i === 0 ? html : "Lý do DEMO", quy_tac_trung: [],
  }));
  return {ma_luot: "DEMO-luot-an", row_version: 7, bao_cao: {
    ket_luan: "chua_doi_chieu_duoc", da_kiem_du: false,
    tom_tat: {so_nghiem_trong: 1, so_can_xem: 1, so_hinh_thuc: 1, so_nhieu_ocr: 1, so_vung_sua_tay: null, so_trang_ocr_kem: null},
    tong_hop: {phan_chua_kiem: ["sua_tay", "do_chat_luong_ocr", "DEMO-kiem-an"]}, diem_lech: diem,
    anh_trang: [{so: 1, tep: {tep_id: "DEMO-anh", ten: "DEMO.png"}, bam: "sha256:DEMO-anh"}],
    bao_cao_pdf: {tep: {tep_id: "DEMO-pdf", ten: "DEMO.pdf"}, bam: "sha256:DEMO-pdf"},
  }, xac_nhan: [{ma_diem: "DEMO-diem-0", ten_nguoi: "Người phụ trách DEMO", luc: "2026-11-15T13:15:00Z",
    lua_chon: "khong_anh_huong", noi_dung_dung: "", ly_do: html}],
    quyen: {xac_nhan: true, diem_duoc_xac_nhan: diem.map(d => d.ma_diem), gui_yeu_cau_module: true},
    dieu_kien_module: {du_dieu_kien_de_nghi: false}};
}
async function dungCH({xungDot = false, trong = false, loiDoc = false} = {}) {
  const root = goc(), luu = [], doc = []; let rv = 7;
  const core = {engine(ma) {assert.equal(ma, "e_doi_chieu"); return {
    cau_hinh: {async doc() {doc.push(1); if (loiDoc) throw Error("DEMO-khong-lo");
      return {cau_hinh: trong ? {} : structuredClone(CH), phien_ban_cau_hinh: rv};},
    async luu(v, r) {luu.push({v, r}); if (xungDot) throw {ma: "NGAN_XUNG_DOT", message: "DEMO-khong-lo"};
      assert.equal(r, rv); return {phien_ban_cau_hinh: ++rv};}},
    ngan: {doc() {throw Error("Màn cấu hình không đọc phần kết quả");}},
  };}};
  await cauHinh(root, core); return {root, luu, doc};
}
async function dungKQ({quyen = true, coCua = true, luuThat = true, loiDoc = false, xungDot = false, matAck = false, loiAnh = false, gui = true} = {}) {
  const root = goc(), view = mau(), daLuu = [], daDoc = [], daMo = [], daGui = [];
  view.quyen.xac_nhan = quyen; view.quyen.gui_yeu_cau_module = gui;
  let rv = 7, loiAck = matAck;
  const core = {engine(ma) {assert.equal(ma, "e_doi_chieu"); return {
    cau_hinh: {doc() {throw Error("Màn kết quả không đọc cấu hình");}},
    ngan: {async doc(bang, khoa) {assert.equal(bang, "luot_doi_chieu"); assert.deepEqual(khoa, {ma_luot: view.ma_luot});
      daDoc.push(khoa); if (loiDoc) throw Error("DEMO-khong-lo"); return {row_version: rv};},
      ghi_lo() {assert.fail("UI không được ghi trực tiếp");}},
  };}};
  const cua = {async doc_ket_qua(y) {assert.equal(y.row_version, rv); return {...structuredClone(view), row_version: rv};},
    async hien_tep(ref, cha) {daMo.push(ref); if (loiAnh) throw Error("DEMO-khong-lo");
      const p = cha.ownerDocument.createElement("p"); p.textContent = "Phần xem tệp do Core cấp DEMO"; cha.appendChild(p);},
    async xac_nhan(y) {
      daLuu.push(y);
      if (xungDot) {rv++; throw {ma: "DC_XUNG_DOT", message: "DEMO-khong-lo"};}
      if (loiAck) {loiAck = false; throw Error("DEMO-mat-ACK");}
      assert.equal(y.row_version, rv); rv++; return {da_luu: true, ma_yeu_cau: y.ma_yeu_cau};
    },
    async gui_yeu_cau_module(y) {daGui.push(y); return {da_nhan: true};},
  };
  if (!luuThat) delete cua.xac_nhan;
  await ketQua(root, core, {ma_luot: view.ma_luot, ...(coCua ? {cua} : {})});
  return {root, view, daLuu, daDoc, daMo, daGui};
}

test("Schema số, mặc định và trần UI khớp schema gói; Core vẫn là bộ kiểm quyết định", async () => {
  const schema = JSON.parse(await readFile(new URL("cau_hinh.schema.json", goi), "utf8"));
  for (const [ma, , max, macDinh] of TRUONG_SO) {
    const s = schema.properties[ma]; assert.equal(s.type, "integer"); assert.equal(s.minimum, 1);
    assert.equal(s.maximum ?? null, max); assert.equal(s.default ?? null, macDinh);
  }
});
test("Cấu hình đọc/lưu CAS, giữ nguyên bộ ghim và ẩn thông tin kỹ thuật", async () => {
  const {root, luu} = await dungCH();
  nhap(root, "Số trang bản ký tối đa (trang)").value = "30";
  await tim(root, "form").goi("submit");
  assert.equal(luu.length, 1); assert.equal(luu[0].r, 7); assert.equal(luu[0].v.so_trang_toi_da, 30);
  assert.equal(luu[0].v.ma_bo_chuan_hoa, CH.ma_bo_chuan_hoa); assert.equal(luu[0].v.nguong_ocr_kem, null);
  assert.doesNotMatch(chu(tim(root, "section")), /sha256|DEMO-pb-an|DEMO-bo-an/);
  assert.match(chu(tim(root, "details")), /sha256/); // Chỉ có trong Nâng cao thu gọn.
  await tim(root, "form").goi("submit"); assert.equal(luu[1].r, 8);
});
test("CAS cấu hình xung đột khóa lưu, chỉ đọc lại khi bấm tải lại", async () => {
  const {root, luu, doc} = await dungCH({xungDot: true});
  await tim(root, "form").goi("submit"); await tim(root, "form").goi("submit");
  assert.equal(luu.length, 1); assert.equal(doc.length, 1);
  assert.match(chu(root), /người khác sửa, tải lại/); assert.doesNotMatch(chu(root), /DEMO-khong-lo/);
  assert.equal(nut(root, "Lưu cấu hình").disabled, true);
  await nut(root, "Tải lại cấu hình").goi("click"); assert.equal(doc.length, 2);
});
for (const n of ["0", "61", "1.5", "NaN"]) test(`Trần số không hợp lệ ${n} không được lưu`, async () => {
  const {root, luu} = await dungCH(); nhap(root, "Số trang bản ký tối đa (trang)").value = n;
  await tim(root, "form").goi("submit"); assert.equal(luu.length, 0);
});
test("Thiếu bộ đã duyệt hoặc đọc lỗi không được lưu đè", async () => {
  for (const opts of [{trong: true}, {loiDoc: true}]) {
    const {root, luu} = await dungCH(opts); await tim(root, "form").goi("submit"); assert.equal(luu.length, 0);
  }
});
test("Hai cột, HTML độc hại là chữ, phần chưa kiểm có nhãn Việt và không lộ mã", async () => {
  const {root, view} = await dungKQ();
  assert.equal(tatCa(root).filter(n => n.the === "mark").length, 8);
  assert.equal(tatCa(root).filter(n => n.the === "img" || n.the === "script").length, 0);
  assert.match(chu(root), /<img src=x onerror=/); assert.match(chu(root), /Chưa kiểm đầy đủ/);
  assert.match(chu(root), /Chất lượng OCR/); assert.match(chu(root), /15\/11\/2026/);
  assert.doesNotMatch(chu(root), /DEMO-luot-an|DEMO-diem|DEMO-kiem-an|sha256/);
  const n = tatCa(root).find(e => e.lop.includes("dc-hai-ben")); assert.equal(n.con.length, 2);
  assert.equal(tatCa(root).find(e => e.the === "mark").textContent, view.bao_cao.diem_lech[0].word.nguyen_van);
});
test("Nhiễu OCR ẩn mặc định, xem được và lọc mức", async () => {
  const {root} = await dungKQ(); const ds = tatCa(root).filter(n => n.the === "article");
  assert.deepEqual(ds.map(d => d.hidden), [false, false, false, true]);
  await nut(root, "Xem nhiễu OCR (1)").goi("click"); assert.equal(ds[3].hidden, false);
  const loc = nhap(root, "Lọc mức"); loc.value = "can_xem"; await loc.goi("change");
  assert.deepEqual(ds.map(d => d.hidden), [true, false, true, true]);
});
for (const lc of ["loi_ocr", "thay_doi_da_thong_nhat", "ban_ky_sai", "khong_anh_huong"]) test(`Xác nhận ${lc} chỉ qua cổng Core`, async () => {
  const {root, daLuu} = await dungKQ();
  const form = tim(root, "form"), chon = nhap(form, "Lựa chọn xác nhận"); chon.value = lc; await chon.goi("change");
  nhap(form, "Nội dung đúng (bắt buộc khi thay đổi đã thống nhất)").value = "Nội dung DEMO đúng";
  nhap(form, "Lý do (bắt buộc khi không ảnh hưởng)").value = "Lý do DEMO";
  await form.goi("submit"); assert.equal(daLuu.length, 1); assert.equal(daLuu[0].lua_chon, lc);
  assert.deepEqual(Object.keys(daLuu[0]).sort(), ["ma_luot", "ma_diem", "ma_yeu_cau", "row_version", "lua_chon", "noi_dung_dung", "ly_do"].sort());
  assert.match(chu(form), /Đã lưu xác nhận/); assert.match(chu(root), /hai người khác nhau/);
});
for (const lc of ["thay_doi_da_thong_nhat", "khong_anh_huong"]) test(`Thiếu nội dung bắt buộc ${lc} không gửi`, async () => {
  const {root, daLuu} = await dungKQ(); const form = tim(root, "form"); nhap(form, "Lựa chọn xác nhận").value = lc;
  await form.goi("submit"); assert.equal(daLuu.length, 0); assert.match(chu(form), /nội dung đúng hoặc lý do/);
});
test("Xung đột xác nhận không tự ghi đè hoặc thử lại, cần tải lại", async () => {
  const {root, daLuu} = await dungKQ({xungDot: true}); const form = tim(root, "form");
  await form.goi("submit"); await form.goi("submit"); assert.equal(daLuu.length, 1);
  assert.match(chu(form), /Kết quả vừa thay đổi. Tải lại/); assert.doesNotMatch(chu(form), /Đã lưu|DEMO-khong-lo/);
});
test("Mất ACK gửi lại cùng mã yêu cầu và cùng nội dung", async () => {
  const {root, daLuu} = await dungKQ({matAck: true}); const form = tim(root, "form");
  await form.goi("submit"); assert.match(chu(form), /Chưa xác nhận được việc lưu/);
  await form.goi("submit"); assert.deepEqual(daLuu[0], daLuu[1]); assert.match(chu(form), /Đã lưu xác nhận/);
});
test("Chưa có cổng, không quyền hoặc không có binding xác nhận: không có nút lưu", async () => {
  for (const opts of [{quyen: false}, {coCua: false}, {luuThat: false}, {loiDoc: true}]) {
    const {root, daLuu} = await dungKQ(opts); assert.equal(nut(root, "Lưu xác nhận"), undefined); assert.equal(daLuu.length, 0);
  }
});
test("Ảnh chỉ mở qua Core, quyền hết không lộ lỗi hoặc địa chỉ", async () => {
  const {root, daMo} = await dungKQ({loiAnh: true});
  assert.equal(daMo.length, 0); await nut(root, "Xem ảnh tại vị trí").goi("click");
  assert.equal(daMo.length, 1); assert.deepEqual(daMo[0].hop, [0, 0, 2, 2]);
  assert.match(chu(root), /quyền xem đã thay đổi/); assert.doesNotMatch(chu(root), /DEMO-khong-lo/);
});
test("Gửi module qua cổng chung, vẫn nói rõ hiệu lực thuộc module", async () => {
  const {root, daGui} = await dungKQ(); await nut(root, "Gửi yêu cầu module kiểm tra").goi("click");
  assert.deepEqual(daGui, [{ma_luot: "DEMO-luot-an"}]); assert.match(chu(root), /Hiệu lực do module quyết định/);
  const b = await dungKQ({gui: false}); assert.equal(nut(b.root, "Gửi yêu cầu module kiểm tra"), undefined);
});
test("Ngày dd/mm/yyyy, tiền có đơn vị; UI không dùng mạng, HTML, ghi ngăn hoặc lưu đĩa", () => {
  assert.equal(dinhDang("2026-10-30"), "30/10/2026"); assert.equal(dinhDang({so: 1000000, tien_te: "VND"}), "1.000.000 VND");
  for (const code of Object.values(nguon)) assert.doesNotMatch(code, /innerHTML|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage|\.ghi_lo\s*\(/);
});
