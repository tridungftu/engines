import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {createHash} from "node:crypto";
import test from "node:test";
import {BO_DEMO, coreGia, cuaGia, gocGia, nut, oNhap, chu, tatCa} from "./ts_dc_gia.mjs";
const source = await readFile(new URL("../../goi/e_doi_chieu/ui/soan_quy_tac.js", import.meta.url), "utf8");
const {default: soan, docJson, kiemBo, xuatThamSo, QUY_TAC, CAP_DOI_NGHIA} = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
globalThis.fetch = () => {throw Error("Cấm mạng");};
globalThis.XMLHttpRequest = globalThis.WebSocket = class {constructor() {throw Error("Cấm mạng");}};
const thamSo = async (bo = BO_DEMO) => xuatThamSo(JSON.stringify(bo, null, 2));
async function dung(mode = {}, ts) {
  const root = gocGia(), fake = cuaGia(ts || await thamSo(), mode);
  const component = await soan(root, coreGia(), {cua: fake.cua}); return {root, fake, component};
}
async function nhap(root, ten, value, event = "input") {const e = oNhap(root, ten); assert.ok(e, ten); e.value = value; await e.goi(event);}

test("Đọc bộ, danh sách cố định và trả đúng bytes cũ; không chạm ngăn/cấu hình/bí mật", async () => {
  const {root, fake, component} = await dung();
  assert.equal(component.doc_gia_tri(), (await thamSo()).bo_quy_tac_json);
  for (const [, ten] of QUY_TAC) assert.ok(chu(root).includes(ten));
  for (const [a, b] of CAP_DOI_NGHIA) assert.ok(chu(root).includes(`${a} / ${b}`));
  assert.equal(QUY_TAC.length, 8); assert.equal(CAP_DOI_NGHIA.length, 6);
  assert.ok(!tatCa(root).some(e => e.type === "password"));
  assert.equal(fake.calls.length, 1);
});
test("Áp dụng hai tham số đúng SHA-256 và CAS; giữ phần bộ khác và tham số khác", async () => {
  const ts = {...await thamSo(), tham_so_khac: "DEMO-giu-nguyen"};
  const {root, fake} = await dung({}, ts);
  await nhap(root, "Dấu hàng nghìn 1", " ", "change");
  await nut(root, "Áp dụng vào bước").goi("click");
  const call = fake.calls.find(c => c[0] === "luu")[1];
  assert.equal(call.phien_ban, 7);
  const out = JSON.parse(call.tham_so.bo_quy_tac_json);
  assert.deepEqual(out.lech_dau, BO_DEMO.lech_dau);
  assert.deepEqual(out.chuan_hoa, BO_DEMO.chuan_hoa);
  assert.equal(out.quy_tac_cung.dinh_dang_so[0].nghin, " ");
  assert.equal(call.tham_so.bam_bo_quy_tac, "sha256:" + createHash("sha256").update(call.tham_so.bo_quy_tac_json).digest("hex"));
  assert.equal(fake.xem().tham_so.tham_so_khac, "DEMO-giu-nguyen");
  assert.match(chu(root), /Đã áp dụng vào Cài đặt bước/);
});
test("Thêm/sửa/xóa vùng; lỗi nguyên văn/băm/vị trí tại trường, không lưu sai", async () => {
  const {root, fake} = await dung();
  await nut(root, "Thêm vùng bảo vệ").goi("click");
  assert.match(chu(root), /cần nguyên văn không rỗng/);
  await nut(root, "Áp dụng vào bước").goi("click");
  assert.ok(!fake.calls.some(c => c[0] === "luu"));
  await nhap(root, "Nguyên văn", "Công ty DEMO Ánh Dương");
  assert.match(chu(root), /cần băm toàn văn/);
  await nhap(root, "Băm toàn văn nguồn", "sha256:" + "a".repeat(64));
  await nhap(root, "Vị trí kết thúc", "21");
  await nhap(root, "Vị trí bắt đầu", "22");
  assert.match(chu(root), /đầu < cuối/);
  await nhap(root, "Vị trí bắt đầu", "0");
  await nut(root, "Áp dụng vào bước").goi("click");
  assert.equal(JSON.parse(fake.xem().tham_so.bo_quy_tac_json).quy_tac_cung.vung_bao_ve.length, 1);
  await nut(root, "Xóa vùng 1").goi("click");
  await nut(root, "Áp dụng vào bước").goi("click");
  assert.deepEqual(JSON.parse(fake.xem().tham_so.bo_quy_tac_json).quy_tac_cung.vung_bao_ve, []);
});
test("Nút kiểm thành công và thất bại; lỗi định dạng ngay cạnh ô", async () => {
  const {root} = await dung();
  await nut(root, "Kiểm tra bộ quy tắc").goi("click"); assert.match(chu(root), /Cấu trúc bộ hợp lệ/);
  await nhap(root, "Dấu thập phân 1", ".", "change");
  await nut(root, "Kiểm tra bộ quy tắc").goi("click"); assert.match(chu(root), /phải khác nhau/);
  const alerts = tatCa(root).filter(e => e.the === "small" && e.textContent.includes("phải khác nhau"));
  assert.equal(alerts.length, 1);
});
for (const [name, mode] of [["CAS tranh chấp", {xungDot: true}], ["lỗi lưu", {loiLuu: true}], ["mất ACK", {matAck: true}]]) {
  test(`${name}: khóa áp dụng, giữ bản đang sửa, tải lại mới cho lưu`, async () => {
    const {root, fake} = await dung(mode);
    await nhap(root, "Dấu hàng nghìn 1", " ", "change");
    await nut(root, "Áp dụng vào bước").goi("click");
    assert.equal(nut(root, "Áp dụng vào bước").disabled, true);
    assert.equal(oNhap(root, "Dấu hàng nghìn 1").value, " ");
    assert.match(chu(root), name.startsWith("CAS") ? /người khác sửa, tải lại/ : /Chưa xác nhận được/);
    assert.ok(!chu(root).includes("DEMO-chi-tiet-khong-lo"));
    await nut(root, "Áp dụng vào bước").goi("click");
    assert.equal(fake.calls.filter(c => c[0] === "luu").length, 1);
    await nut(root, "Tải lại").goi("click"); assert.equal(nut(root, "Áp dụng vào bước").disabled, false);
  });
}
test("Chống bấm lưu lặp và sửa trong lúc chờ", async () => {
  let release; const cho = new Promise(r => release = r);
  const {root, fake} = await dung({cho});
  const waiting = nut(root, "Áp dụng vào bước").goi("click");
  await Promise.resolve();
  assert.equal(oNhap(root, "Dấu hàng nghìn 1").disabled, true);
  await nut(root, "Áp dụng vào bước").goi("click"); release(); await waiting;
  assert.equal(fake.calls.filter(c => c[0] === "luu").length, 1);
});
test("Thiếu D2, đọc lỗi, sai băm, thiếu CAS đều khóa; không lộ ngoại lệ", async () => {
  const root = gocGia(); await soan(root, coreGia());
  assert.match(chu(root), /Chưa có cửa Cài đặt bước/); assert.ok(nut(root, "Áp dụng vào bước").disabled);
  const r = await dung({loiDoc: true}); assert.ok(nut(r.root, "Áp dụng vào bước").disabled);
  assert.ok(!chu(r.root).includes("DEMO-chi-tiet-khong-lo"));
  const ts = await thamSo(); ts.bam_bo_quy_tac = "sha256:" + "b".repeat(64);
  const bad = await dung({}, ts); assert.match(chu(bad.root), /Băm bộ không khớp/);
  assert.ok(nut(bad.root, "Áp dụng vào bước").disabled);
  await soan(root, coreGia(), {cua: {doc: async () => ({tham_so: await thamSo()})}});
  assert.ok(nut(root, "Áp dụng vào bước").disabled);
});
test("Bộ cũ thiếu phần quy tắc cứng giữ nguyên, không tự thêm mặc định", async () => {
  const bo = structuredClone(BO_DEMO); delete bo.quy_tac_cung;
  const ts = await thamSo(bo), {root, fake} = await dung({}, ts);
  assert.ok(nut(root, "Thêm vùng bảo vệ").disabled);
  await nut(root, "Áp dụng vào bước").goi("click");
  assert.equal(fake.xem().tham_so.bo_quy_tac_json, ts.bo_quy_tac_json);
});
test("JSON độc hại/hỏng/trùng/sâu/quá trần bị từ chối, không cắt ngầm", () => {
  for (const text of ['{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}', '{"a":"\\ud800"}', '{"a":1}x', "[".repeat(66)+"0"+"]".repeat(66), " ".repeat(65537), JSON.stringify({x:"đ".repeat(40000)})])
    assert.throws(() => docJson(text));
  assert.deepEqual(docJson('{"DEMO":"😀 Ánh"}'), {DEMO:"😀 Ánh"});
});
test("Ràng buộc runtime: cấu trúc, tiền tệ, ngày, vị trí và trần danh sách", () => {
  const mutate = fn => {const bo = structuredClone(BO_DEMO); fn(bo.quy_tac_cung); assert.throws(() => kiemBo(bo));};
  mutate(q => q.bat = false); mutate(q => q.phien_ban = 2);
  mutate(q => q.don_vi_tien["đồng"] = "USD"); mutate(q => q.don_vi_tien[" VND "] = "VND");
  mutate(q => q.dinh_dang_ngay = []); mutate(q => q.dinh_dang_so = Array(11).fill({nghin:".",thap_phan:","}));
  mutate(q => q.vung_bao_ve = Array(1001).fill({}));
});
test("Dữ liệu hiển thị là text, không HTML/mạng/bí mật và không xưng hô", async () => {
  const bo = structuredClone(BO_DEMO); bo.phien_ban_bo = '<img src=x onerror=DEMO()>';
  const {root} = await dung({}, await thamSo(bo));
  assert.ok(chu(root).includes('<img src=x onerror=DEMO()>'));
  assert.ok(!tatCa(root).some(e => ["img", "script", "iframe"].includes(e.the)));
  assert.doesNotMatch(source, /\bfetch\s*\(|\beval\s*\(|innerHTML|localStorage|sessionStorage|\.bi_mat\b/);
  assert.doesNotMatch(chu(root), /\bAnh\b|\bbạn\b/u);
});

// Cho pytest kiểm dữ liệu xuất thật bằng lõi Python, không sao chép validator.
if (process.argv.includes("--xuat-demo")) {
  const {root, fake} = await dung();
  await nhap(root, "Dấu hàng nghìn 1", " ", "change");
  await nut(root, "Áp dụng vào bước").goi("click");
  console.log("TS_DC_DEMO=" + JSON.stringify(fake.xem().tham_so));
}
