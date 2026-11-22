// Đã kiểm bằng Core giả (CoreGia): DOM/KttCore trong RAM, Node, không mạng.
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import test from "node:test";

const goi = new URL("../../goi/e_doi_chieu/", import.meta.url);
const code = await readFile(new URL("ui/cau_hinh.js", goi), "utf8");
const {default: cauHinh, TRUONG_SO} = await import(`data:text/javascript;base64,${Buffer.from(code).toString("base64")}`);
const schema = JSON.parse(await readFile(new URL("cau_hinh.schema.json", goi), "utf8"));
const CH = {...schema.examples[0]};
globalThis.fetch = () => assert.fail("Cấm mạng");
globalThis.XMLHttpRequest = globalThis.WebSocket = class {constructor() {assert.fail("Cấm mạng");}};
class E {
  constructor(the, doc) {
    Object.assign(this, {the, ownerDocument: doc, con: [], sk: {}, tt: {}, value: "", _chu: "", disabled: false});
    this.classList = {add() {}};
  }
  set textContent(v) {this._chu = String(v); this.con = [];}
  get textContent() {return this._chu;}
  set innerHTML(_) {assert.fail("Cấm HTML");}
  appendChild(e) {this.con.push(e); return e;}
  replaceChildren() {this.con = []; this._chu = "";}
  setAttribute(k, v) {this.tt[k] = v;}
  addEventListener(k, f) {this.sk[k] = f;}
  focus() {this.focused = true;}
  async goi(k) {await this.sk[k]?.({preventDefault() {}});}
}
const all = e => [e, ...e.con.flatMap(all)];
const chu = e => e.textContent + " " + e.con.map(chu).join(" ");
const tim = (r, the, ten) => all(r).find(e => e.the === the && (!ten || e.textContent === ten));
const input = (r, ma) => all(r).find(e => e.tt.name === ma);
function root() {const doc = {createElement: t => new E(t, doc)}; return new E("main", doc);}
async function dung({ch = CH, doc, luu} = {}) {
  const r = root(), calls = []; let rv = 7;
  const core = {engine(ma) {
    assert.equal(ma, "e_doi_chieu");
    return {cau_hinh: {
      doc: doc || (async () => ({cau_hinh: structuredClone(ch), phien_ban_cau_hinh: rv})),
      async luu(v, ver) {calls.push({v: structuredClone(v), ver}); if (luu) return luu(v, ver); assert.equal(ver, rv); return {phien_ban_cau_hinh: ++rv};},
    }, ngan: new Proxy({}, {get() {assert.fail("Màn cấu hình không đọc ngăn khác");}}),
    thao_tac() {assert.fail("UI-DC không có máy ngoài hoặc nút kiểm kết nối");},
    bi_mat: new Proxy({}, {get() {assert.fail("UI-DC không có bí mật");}})};
  }};
  await cauHinh(r, core); return {r, calls};
}
test("Cơ bản chỉ có bốn trần; bộ, băm, detector và học OCR chỉ đọc trong Nâng cao", async () => {
  const {r} = await dung(), basic = tim(r, "section"), adv = tim(r, "details");
  assert.equal(all(basic).filter(e => e.the === "input").length, 4);
  assert.equal(adv.open ?? false, false);
  assert.equal(all(adv).filter(e => e.the === "input").length, 7);
  assert.doesNotMatch(chu(basic), /sha256|DEMO/);
  for (const k of ["ma_bo_chuan_hoa", "bam_bo_chuan_hoa", "phuong_phap_detector", "hoc_loi_ocr"]) {
    assert.equal(input(r, k), undefined);
  }
  assert.match(chu(adv), /DEMO-chuan-hoa/);
});
test("Mọi ô có nhãn, mẫu, hướng dẫn, liên kết lỗi; báo lỗi ngay khi nhập và xóa khi sửa", async () => {
  const {r, calls} = await dung();
  for (const [ma] of TRUONG_SO) {
    const o = input(r, ma);
    assert.ok(o.placeholder); assert.ok(o.tt["aria-describedby"].includes(`dc-loi-${ma}`));
    o.value = "0"; await o.goi("input");
    assert.equal(o.tt["aria-invalid"], "true");
    assert.match(all(r).find(e => e.tt.id === `dc-loi-${ma}`).textContent, /nhập số nguyên/);
    o.value = "1"; await o.goi("input"); assert.equal(o.tt["aria-invalid"], "false");
  }
  assert.equal(calls.length, 0);
});
for (const [ma, , max] of TRUONG_SO) test(`Trần ${ma}: kiểm biên và không gửi dữ liệu sai`, async () => {
  for (const sai of ["0", "-1", "1.5", "NaN", "Infinity", "9007199254740992", ...(max === null ? [] : ["", String(max + 1)])]) {
    const {r, calls} = await dung(); input(r, ma).value = sai;
    await tim(r, "form").goi("submit"); assert.equal(calls.length, 0, sai);
    assert.equal(input(r, ma).tt["aria-invalid"], "true"); assert.equal(input(r, ma).focused, true);
    if (TRUONG_SO.findIndex(v => v[0] === ma) >= 4) assert.equal(tim(r, "details").open, true);
  }
  for (const dat of ["1", ...(max === null ? [""] : [String(max)])]) {
    const {r, calls} = await dung(); input(r, ma).value = dat;
    await tim(r, "form").goi("submit"); assert.equal(calls.length, 1);
  }
});
test("Giữ nguyên bộ và ngưỡng học; không thêm thời hạn khi để trống; CAS tăng cho lần lưu sau", async () => {
  const {r, calls} = await dung(); input(r, "thoi_han_chiem_luot_giay").value = "";
  await tim(r, "form").goi("submit"); await tim(r, "form").goi("submit");
  assert.deepEqual(calls.map(c => c.ver), [7, 8]);
  assert.equal(Object.hasOwn(calls[0].v, "thoi_han_chiem_luot_giay"), false);
  assert.deepEqual(calls[0].v.hoc_loi_ocr, CH.hoc_loi_ocr);
  for (const k of ["ma_bo_chuan_hoa", "bam_tu_dien", "phien_ban_detector"]) assert.equal(calls[0].v[k], CH[k]);
});
for (const loi of [{status: 409}, {ma: "CAU_HINH_XUNG_DOT"}, {code: "NGAN_XUNG_DOT"}, Error("DEMO-loi-an"), null]) {
  test(`Lưu lỗi ${loi?.ma || loi?.code || loi?.status || "chung"}: khóa lưu, không lộ chi tiết, tải lại để phục hồi`, async () => {
    let lan = 0;
    const {r, calls} = await dung({luu: async () => {if (!lan++) throw loi; return {phien_ban_cau_hinh: 8};}});
    await tim(r, "form").goi("submit"); await tim(r, "form").goi("submit");
    assert.equal(calls.length, 1); assert.equal(tim(r, "button", "Lưu cấu hình").disabled, true);
    assert.doesNotMatch(chu(r), /DEMO-loi-an|Đã lưu cấu hình cho việc mới/);
    await tim(r, "button", "Tải lại cấu hình").goi("click");
    assert.equal(tim(r, "button", "Lưu cấu hình").disabled, false);
    await tim(r, "form").goi("submit"); assert.equal(calls.length, 2);
  });
}
test("Thiếu phiên bản đọc hoặc ACK: không báo lưu thành công", async () => {
  for (const kq of [null, {}, {phien_ban_cau_hinh: null}]) {
    const a = await dung({doc: async () => kq}); assert.equal(tim(a.r, "button", "Lưu cấu hình").disabled, true);
    const b = await dung({luu: async () => kq}); await tim(b.r, "form").goi("submit");
    assert.match(chu(b.r), /Chưa xác nhận được việc lưu/); assert.equal(tim(b.r, "button", "Lưu cấu hình").disabled, true);
  }
});
test("Đang đọc hoặc lưu thì khóa ô và không gửi trùng", async () => {
  let xong, soDoc = 0;
  const {r, calls} = await dung({doc: async () => {
    if (++soDoc === 1) return {cau_hinh: CH, phien_ban_cau_hinh: 7};
    return new Promise(resolve => {xong = () => resolve({cau_hinh: CH, phien_ban_cau_hinh: 8});});
  }, luu: async () => new Promise(resolve => {xong = () => resolve({phien_ban_cau_hinh: 9});})});
  const p = tim(r, "button", "Tải lại cấu hình").goi("click");
  await tim(r, "form").goi("submit"); await tim(r, "button", "Tải lại cấu hình").goi("click");
  assert.equal(soDoc, 2); assert.equal(calls.length, 0); assert.equal(input(r, "so_trang_toi_da").disabled, true); xong(); await p;
  const q = tim(r, "form").goi("submit"); await tim(r, "form").goi("submit");
  assert.equal(calls.length, 1); assert.equal(calls[0].ver, 8); assert.equal(input(r, "so_trang_toi_da").disabled, true); xong(); await q;
  assert.equal(input(r, "so_trang_toi_da").disabled, false);
});
test("Schema đủ mô tả mọi cấp; chỉ thêm annotation, mẫu đầy đủ, không còn chữ lỗi mã hóa", () => {
  function kiem(s) {
    assert.ok(s.title); assert.ok(s.description); assert.ok(s.examples?.length);
    assert.doesNotMatch(s.title + s.description, /\?/);
    for (const v of Object.values(s.properties || {})) kiem(v);
  }
  kiem(schema); assert.deepEqual(Object.keys(schema.examples[0]).sort(), Object.keys(schema.properties).sort());
  assert.match(schema.description, /hoc_loi_ocr\.ma_phe_duyet/);
  assert.equal(schema.additionalProperties, false); assert.deepEqual(schema.properties.nguong_ocr_kem.enum, [null]);
});
test("Ba màn không xưng hô, không kênh mạng hoặc kho trình duyệt; dữ liệu bộ có HTML chỉ là chữ", async () => {
  for (const ten of ["cau_hinh", "ket_qua", "loi_ocr"]) {
    const js = await readFile(new URL(`ui/${ten}.js`, goi), "utf8");
    assert.doesNotMatch(js, /\bAnh\b|\bbạn\b|innerHTML|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage/);
  }
  const {r} = await dung({ch: {...CH, ma_bo_chuan_hoa: '<img src=x onerror="DEMO()">'}});
  assert.match(chu(tim(r, "details")), /<img/); assert.equal(all(r).some(e => ["img", "script"].includes(e.the)), false);
});
