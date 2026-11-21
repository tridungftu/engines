import {test} from "node:test";
import assert from "node:assert/strict";
import {duLieu as d, mount, maMan, data} from "./nap_man.mjs";
import {taoGoc, taoCoreGia, tatCa, nut, oNhap, phat} from "./kttcore_gia.mjs";
const NL = "audit.phan_luong@1";
const mau = () => Object.fromEntries(d.CAC_O.map(k => [k, d.vietJson(d.MAU[k])]));
const khongMang = () => { throw new Error("Bộ kiểm TS-PL cấm mạng."); };
globalThis.fetch = khongMang; globalThis.WebSocket = khongMang; globalThis.XMLHttpRequest = khongMang;
async function dung(nl = NL, thamSo = mau(), sua = {}) {
  const goc = taoGoc(), core = Object.assign(taoCoreGia(thamSo), sua);
  const man = await mount(goc, {nang_luc: nl, KttCore: core.KttCore, doc_tham_so: core.doc_tham_so, luu_tham_so: core.luu_tham_so});
  return {goc, core, man};
}

for (const nl of Object.keys(d.NANG_LUC)) test("Đọc, kiểm và lưu bằng cùng thành phần: " + nl, async () => {
  const v = {...mau(), khau: "ktt_demo", prompt: "Hướng dẫn DEMO giữ nguyên", ty_le_duoi_sad: 0.02};
  const {goc, man, core} = await dung(nl, v);
  assert.equal(man.validate().length, 0);
  assert.deepEqual(man.getValue(), v);
  assert.equal(tatCa(goc).filter(e => e.tagName === "SECTION").length, d.NANG_LUC[nl].length);
  await man.save();
  assert.equal(core.goi.filter(x => x[0] === "luu").length, 1);
  assert.equal(core.goi.at(-1)[2], 7);
  assert.deepEqual(core.tham_so, v);
  assert.match(goc.textContent, /Đã lưu cài đặt vào bước/);
  assert.equal(core.goi.filter(x => x[0] === "engine").length, 1);
  man.destroy(); assert.equal(goc.textContent, "");
});

test("Sửa tiền chính xác, giữ tham số khác và JSON không đổi nguyên byte", async () => {
  const v = {...mau(), khau: "cfo_demo"}; v.danh_muc_loai_json = "  " + v.danh_muc_loai_json + "\n";
  const {goc, core, man} = await dung(NL, v);
  await phat(oNhap(goc, "nguong_json.pm.so"), "input", "999999999999999999.123456");
  assert.match(goc.querySelector('[data-tien="pm"]').textContent, /999\.999\.999\.999\.999\.999,123456 VND/);
  await man.save();
  assert.equal(JSON.parse(core.tham_so.nguong_json).pm.so, "999999999999999999.123456");
  assert.equal(core.tham_so.danh_muc_loai_json, v.danh_muc_loai_json);
  assert.equal(core.tham_so.khau, "cfo_demo");
});

test("Nút kiểm đạt, lỗi ngay cạnh ô và cấm lưu khi sai", async () => {
  const {goc, core, man} = await dung();
  await phat(nut(goc, "Kiểm tra cài đặt"), "click"); assert.match(goc.textContent, /Kiểm tra đạt/);
  await phat(oNhap(goc, "danh_muc_loai_json.0.ten"), "input", "");
  assert.equal(oNhap(goc, "danh_muc_loai_json.0.ten").getAttribute("aria-invalid"), "true");
  assert.match(oNhap(goc, "danh_muc_loai_json.0.ten").parentNode.textContent, /Nhập tên loại/);
  await phat(nut(goc, "Kiểm tra cài đặt"), "click"); assert.match(goc.textContent, /Kiểm tra chưa đạt/);
  assert.throws(() => man.getValue(), /chưa hợp lệ/); await man.save();
  assert.equal(core.goi.filter(x => x[0] === "luu").length, 0);
  await phat(oNhap(goc, "danh_muc_loai_json.0.ten"), "input", "Đã sửa DEMO");
  await phat(oNhap(goc, "nguong_json.sad.so"), "input", "3000000001");
  assert.match(goc.textContent, /0 < SAD < TE ≤ PM/);
});

test("CAS giữ bản nháp, khóa lưu đến khi tải lại và dùng phiên bản mới", async () => {
  const {goc, core, man} = await dung();
  await phat(oNhap(goc, "danh_muc_loai_json.0.ten"), "input", "Bản nháp DEMO");
  core.phien++; await man.save();
  assert.match(goc.textContent, /đã được người khác sửa, tải lại trước khi lưu/);
  assert.equal(JSON.parse(man.getValue().danh_muc_loai_json)[0].ten, "Bản nháp DEMO");
  await man.save(); assert.equal(core.goi.filter(x => x[0] === "luu").length, 1);
  await phat(nut(goc, "Tải lại"), "click"); await man.save();
  assert.equal(core.goi.at(-1)[2], 8);
});

test("Lỗi đọc/lưu an toàn, không in thông điệp máy và có thể thử lại", async () => {
  const {goc, core, man} = await dung(NL, mau(), {loi_doc: new Error("DUONG-DAN-BI-MAT-DEMO")});
  assert.match(goc.textContent, /Không đọc được/); assert.doesNotMatch(goc.textContent, /DUONG-DAN/);
  await man.save(); assert.equal(core.goi.filter(x => x[0] === "luu").length, 0);
  core.loi_doc = null; await man.refresh();
  core.loi_luu = new Error("KEY-DEMO-KHONG-HIEN"); await man.save();
  assert.match(goc.textContent, /Không lưu được/); assert.doesNotMatch(goc.textContent, /KEY-DEMO/);
  core.loi_luu = null; await man.save(); assert.match(goc.textContent, /Đã lưu/);
});

test("Không lưu giả khi Core không trả phiên bản mới", async () => {
  const goc = taoGoc(), core = taoCoreGia(mau());
  await mount(goc, {nang_luc: NL, KttCore: core.KttCore, tham_so: mau(), phien_ban_tham_so: 7,
    luu_tham_so: async () => ({da_luu: true})}).then(m => m.save());
  assert.match(goc.textContent, /Không lưu được/);
});

test("Dừng an toàn khi thiếu SDK, D2 hoặc năng lực không hỗ trợ", async () => {
  const goc = taoGoc(), core = taoCoreGia(mau());
  const man = await mount(goc, {nang_luc: NL, KttCore: {}, tham_so: mau(), phien_ban_tham_so: 0, luu_tham_so: core.luu_tham_so});
  assert.match(goc.textContent, /Chưa nối bộ lưu/); await man.save(); assert.equal(core.goi.length, 0);
  assert.ok(man.getValue()); man.destroy();
  await mount(goc, {nang_luc: "audit.khong_co_demo@1"}); assert.match(goc.textContent, /Không mở được/);
});

test("Thêm/xóa danh mục, thứ tự quy tắc và nhóm AND/OR giữ nguyên", async () => {
  const {goc, man} = await dung();
  await phat(nut(goc, "Thêm loại"), "click");
  await phat(oNhap(goc, "danh_muc_loai_json.1.ten"), "input", "Loại khác DEMO");
  await phat(oNhap(goc, "danh_muc_loai_json.1.ma"), "input", "khac_demo");
  await phat(oNhap(goc, "danh_muc_loai_json.1.ten"), "change");
  await phat(nut(goc, "Thêm quy tắc"), "click");
  await phat(oNhap(goc, "bo_phan_loai_json.quy_tac.1.loai"), "change", "khac_demo");
  await phat(oNhap(goc, "bo_phan_loai_json.quy_tac.1.khi.0.tat_ca.0.0"), "input", "DEMO, có | dấu");
  await phat(nut(goc, "Lên", 1), "click");
  const b = JSON.parse(man.getValue().bo_phan_loai_json);
  assert.equal(b.quy_tac[0].loai, "khac_demo");
  assert.equal(b.quy_tac[0].khi[0].tat_ca[0][0], "DEMO, có | dấu");
  assert.equal(b.quy_tac[1].khi[0].tat_ca.length, 2);
  await phat(nut(goc, "Xóa loại", 1), "click"); assert.match(goc.textContent, /Chọn một loại đã có/);
});

test("Đổi tên loại cập nhật lựa chọn và giữ nút Lưu khi rời ô nhập", async () => {
  const {goc, man} = await dung();
  const luu = nut(goc, "Lưu vào bước"), ten = oNhap(goc, "danh_muc_loai_json.0.ten");
  await phat(ten, "input", "Tên mới DEMO"); await phat(ten, "change");
  assert.equal(nut(goc, "Lưu vào bước"), luu);
  const e = oNhap(goc, "bo_phan_loai_json.quy_tac.0.loai");
  assert.ok(e.children.some(x => x.value === "thanh_toan_demo" && x.textContent === "Tên mới DEMO"));
  await man.save(); assert.match(goc.textContent, /Đã lưu cài đặt vào bước/);
});

test("Chính sách sửa từng ô, kế thừa mặc định, các bậc và hệ số", async () => {
  const {goc, man} = await dung(NL, {...mau(), chinh_sach_json: "{}"});
  assert.equal(man.getValue().chinh_sach_json, "{}");
  await phat(oNhap(goc, "chinh_sach_json.he_so.NGAY_NGHI"), "input", "0.9");
  assert.match(goc.textContent, /hệ số cần là số từ 1/);
  await phat(oNhap(goc, "chinh_sach_json.he_so.NGAY_NGHI"), "input", "2.5");
  assert.deepEqual(JSON.parse(man.getValue().chinh_sach_json), {he_so: {NGAY_NGHI: 2.5}});
  await phat(nut(goc, "Thêm mức"), "click"); assert.ok(man.validate().length);
  await phat(nut(goc, "Dùng lại mặc định"), "click"); assert.equal(man.getValue().chinh_sach_json, "{}");
});

test("Tỷ lệ dưới SAD chưa ghi đè kế thừa đúng ô sẵn có của bước", async () => {
  const {goc, man} = await dung(NL, {...mau(), chinh_sach_json: "{}", ty_le_duoi_sad: 0.11});
  assert.equal(oNhap(goc, "chinh_sach_json.ty_le_duoi_sad").value, "0.11");
  await phat(oNhap(goc, "chinh_sach_json.mau_sach_toan_bo"), "input", "40");
  assert.deepEqual(JSON.parse(man.getValue().chinh_sach_json), {mau_sach_toan_bo: 40});
  assert.equal(man.getValue().ty_le_duoi_sad, 0.11);
});

test("Khuôn cột tùy chỉnh và các cột bắt buộc", async () => {
  const {goc, man} = await dung();
  await phat(nut(goc, "Thêm cột"), "click");
  await phat(oNhap(goc, "khuon_cot_json.cot.4.ma"), "change", "thuoc_tinh");
  await phat(oNhap(goc, "khuon_cot_json.cot.4.thuoc_tinh"), "input", "bo_phan_demo");
  await phat(oNhap(goc, "khuon_cot_json.cot.4.tu_khoa.0"), "input", "Bộ phận DEMO");
  assert.equal(JSON.parse(man.getValue().khuon_cot_json).cot[4].ma, "thuoc_tinh.bo_phan_demo");
  await phat(oNhap(goc, "khuon_cot_json.cot.0.bat_buoc"), "change", false);
  assert.match(goc.textContent, /đủ ba cột bắt buộc/);
});

test("Để trống, chèn mẫu và bỏ thiết lập không tự điền giá trị chưa chọn", async () => {
  const {goc, core, man} = await dung(NL, {khau: "demo"});
  assert.deepEqual(man.getValue(), {khau: "demo"});
  await phat(nut(goc, "Chèn mẫu DEMO"), "click");
  assert.equal(JSON.parse(man.getValue().danh_muc_loai_json)[0].ma, "thanh_toan_demo");
  await phat(nut(goc, "Bỏ thiết lập"), "click"); await man.save();
  assert.equal(core.tham_so.danh_muc_loai_json, ""); assert.equal(core.tham_so.nguong_json, undefined);
});

test("Khóa trùng, JSON hỏng, trần byte và cấu trúc sai không làm hỏng màn", async () => {
  for (const [k, raw] of [["nguong_json", '{"pm":1,"pm":2}'], ["nguong_json", "null"],
    ["bo_phan_loai_json", '{"phien_ban":1,"quy_tac":[{"loai":"thanh_toan_demo","khi":3}]}'],
    ["chinh_sach_json", '{"bac":null}'], ["khuon_cot_json", '{"cot":[null]}'],
    ["danh_muc_loai_json", "[null]"], ["danh_muc_loai_json", "x".repeat(16385)]]) {
    const {man, goc, core} = await dung(NL, {...mau(), [k]: raw});
    assert.ok(man.validate().length); await man.save(); assert.equal(core.goi.filter(x => x[0] === "luu").length, 0);
    assert.ok(nut(goc, "Bỏ giá trị lỗi"));
  }
  const mo = d.docThamSo({...mau(), danh_muc_loai_json: JSON.stringify([{ma: "demo", ten: "ấ".repeat(6000), mo_ta: ""}])}, NL);
  assert.match(mo.loi_doc.danh_muc_loai_json, /byte UTF-8/);
});

test("Không diễn dịch HTML, không có ô bí mật hoặc gọi két ở TS-PL", async () => {
  const v = mau(), dm = JSON.parse(v.danh_muc_loai_json); dm[0].ten = '<img src="DEMO" onerror="DEMO">';
  v.danh_muc_loai_json = JSON.stringify(dm); v.khoa_demo = "BI-MAT-DEMO-1234";
  const {goc, man} = await dung(NL, v);
  assert.ok(goc.textContent.includes("<img")); assert.equal(tatCa(goc).filter(e => e.tagName === "IMG").length, 0);
  assert.doesNotMatch(goc.textContent, /BI-MAT-DEMO-1234/); assert.equal(tatCa(goc).filter(e => e.type === "password").length, 0);
  assert.equal(man.getValue().khoa_demo, v.khoa_demo);
  assert.doesNotMatch(maMan + data, /\b(?:fetch|XMLHttpRequest|WebSocket|eval)\s*\(|\.innerHTML\s*=|localStorage|indexedDB/);
});

test("Lưu một lần, không sửa trong khi lưu, bỏ phản hồi khi destroy", async () => {
  const {goc, man, core} = await dung(); let tra;
  core.cho_luu = new Promise(r => { tra = r; });
  const dang = man.save(); await man.save();
  await phat(oNhap(goc, "nguong_json.pm.so"), "input", "1");
  assert.equal(core.goi.filter(x => x[0] === "luu").length, 1);
  man.destroy(); tra(); await dang; assert.equal(goc.textContent, "");
});

test("Bộ đọc số JSON không mất chính xác hay chấp nhận JSON sai", () => {
  const raw = '{"so":999999999999999999.123456,"x":[0.3000000000000000001,1e-3]}';
  assert.equal(d.vietJson(d.docJson(raw)), raw);
  for (const s of ['{"a":1,"a":2}', "[1,]", "01", "NaN", '"a\nb"', "{} x", '{"x":Infinity}']) assert.throws(() => d.docJson(s));
  const v = mau(); v.nguong_json = '{"pm":{"so":999999999999999999.123456,"tien_te":"VND"},"te":{"so":"2","tien_te":"VND"},"sad":{"so":"1","tien_te":"VND"}}';
  const mo = d.docThamSo(v, NL); assert.equal(d.kiemThamSo(mo, NL).length, 0);
  d.doi(mo, "nguong_json", mo.du_lieu.nguong_json);
  assert.ok(d.xuatThamSo(mo).nguong_json.includes("999999999999999999.123456"));
});

test("Tỷ lệ sát nhau vẫn so đúng thập phân, phiên bản phải là số nguyên 1", () => {
  const v = mau();
  v.chinh_sach_json = '{"bac":[0.3000000000000000002,0.3000000000000000001],"nguong_xuong":[0.1],"mau_toi_thieu":[30],"do_tin_cay":0.9999999999999999999}';
  assert.equal(d.kiemThamSo(d.docThamSo(v, NL), NL).length, 0);
  v.chinh_sach_json = '{"do_tin_cay":1.0000000000000000001}';
  assert.ok(d.kiemThamSo(d.docThamSo(v, NL), NL).length);
  v.chinh_sach_json = "{}";
  v.bo_phan_loai_json = '{"phien_ban":1.0,"quy_tac":[]}';
  assert.ok(d.kiemThamSo(d.docThamSo(v, NL), NL).length);
  v.bo_phan_loai_json = "";
  v.nguong_json = '{"pm":{"so":1e10,"tien_te":"VND"},"te":{"so":2e9,"tien_te":"VND"},"sad":{"so":1e8,"tien_te":"VND"}}';
  assert.equal(d.kiemThamSo(d.docThamSo(v, NL), NL).length, 0);
});
