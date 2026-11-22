import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {mount, tyLe, ngayViet, tienViet} from "../../goi/e_tra_cuu/ui/trang_thai.js";
import {goc, coreGia, ban} from "./ho_tro.js";

test("Chưa đo/null/mẫu số 0 không thành 0%; giữ tử số/mẫu số riêng", () => {
  for (const v of [null, undefined, {tu_so: 0, mau_so: 0}]) assert.equal(tyLe(v), "Chưa đo");
  assert.equal(tyLe({tu_so: 0, mau_so: 10}), "0/10 (0%)");
  assert.equal(tyLe({tu_so: 9, mau_so: 10}), "9/10 (90%)");
  for (const v of [{tu_so: 3, mau_so: 2}, {tu_so: -1, mau_so: 2}, {tu_so: true, mau_so: 2}, {tu_so: 0, mau_so: null}]) {
    assert.equal(tyLe(v), "Số đo không hợp lệ");
  }
  assert.equal(ngayViet("2026-10-30"), "30/10/2026");
  assert.equal(ngayViet("2026-02-30"), "Ngày không hợp lệ");
  assert.equal(tienViet({so: 1000000, tien_te: "VND"}), "1.000.000 VND");
  assert.equal(tienViet({so: 1000000}), "Chưa có số tiền");
});
test("Đọc/tìm dùng phạm vi host Core, không tự khai pháp nhân trong khoa/loc", async () => {
  const root = goc(), fake = coreGia({cacBan: [ban(), ban("DEMO-P", "DEMO-2"), ban("DEMO-Q")], kichThuocTrang: 1});
  const ctl = await mount(root, {...fake, phapNhanId: "DEMO-P"});
  assert.match(root.textContent, /Chưa đo/); assert.doesNotMatch(root.textContent, /0%/);
  await root.nut("Trang sau").fire("click");
  assert.equal(root.nut("Trang sau").disabled, true);
  await ctl.docBaiDo("DEMO-1");
  assert.ok(fake.goi.length >= 3);
  for (const [tt, bang, opts] of fake.goi) {
    assert.equal(bang, "dot_kiem");
    assert.ok(!Object.hasOwn(tt === "tim" ? opts.loc : opts, "phap_nhan_id"));
    if (tt === "tim") assert.ok(opts.gioi_han <= 500);
  }
  assert.deepEqual(fake.engines, ["e_tra_cuu"]);
});
test("Không quyền/thiếu pháp nhân không hiện bài đo, không fallback Admin", async () => {
  for (const p of [undefined, "", "DEMO-Q"]) {
    const root = goc(), fake = coreGia();
    const ctl = await mount(root, {...fake, phapNhanId: p});
    assert.match(root.textContent, /Chưa đọc được bài đo/);
    assert.equal(root.all().filter(n => n.tagName === "h3").length, 0);
    await ctl.docBaiDo("DEMO-1");
    assert.equal(root.all().filter(n => n.tagName === "h3").length, 0);
    assert.doesNotMatch(root.textContent, /noi-dung-khong-duoc-hien/);
  }
});
test("Cursor không chuyển phạm vi: UI từ chối cursor lạ; KttCore giả kiểm bảng/loc/pháp nhân", async () => {
  const fake = coreGia({phap_nhan: ["DEMO-P", "DEMO-Q"], cacBan: [ban(), ban("DEMO-P", "DEMO-2"), ban("DEMO-Q")], kichThuocTrang: 1});
  const root = goc(); const ctl = await mount(root, {...fake, phapNhanId: "DEMO-P"});
  const cursor = [...fake.cursors.keys()][0];
  await assert.rejects(() => fake.cong.ngan.tim("dot_kiem", {loc: {phap_nhan_id: "DEMO-Q"}, gioi_han: 500, tiep: cursor}));
  await assert.rejects(() => fake.cong.ngan.tim("dot_kiem", {loc: {phap_nhan_id: "DEMO-P", trang_thai: "da_do"}, gioi_han: 500, tiep: cursor}));
  assert.equal((await fake.cong.ngan.doc("dot_kiem", {ma_dot: "DEMO-1"})).gia_tri.phap_nhan_id, "DEMO-P");
  const truoc = fake.goi.length;
  assert.equal(await ctl.taiTrang("DEMO-cursor-gia"), false);
  assert.equal(fake.goi.length, truoc);
  const other = await mount(goc(), {...fake, phapNhanId: "DEMO-Q"});
  assert.equal(await other.taiTrang(cursor), false);
});
test("Server trả hàng chéo: từ chối cả trang trước khi vẽ, không lộ dữ liệu", async () => {
  const fake = coreGia(), root = goc();
  fake.cong.ngan.tim = async () => ({danh_sach: [ban(), ban("DEMO-Q")], tiep: null});
  const ctl = await mount(root, {...fake, phapNhanId: "DEMO-P"});
  assert.equal(root.all().filter(n => n.tagName === "h3").length, 0);
  fake.cong.ngan.doc = async () => ban("DEMO-Q");
  assert.equal(await ctl.docBaiDo("DEMO-1"), false);
  assert.equal(root.all().filter(n => n.tagName === "h3").length, 0);
});
test("Lỗi từng phần chỉ báo ở phần đó; lỗi quyền không giữ dữ liệu trong phần lỗi", async () => {
  const fake = coreGia(), root = goc(); const ctl = await mount(root, {...fake, phapNhanId: "DEMO-P"});
  await ctl.docBaiDo("DEMO-1");
  assert.equal(root.all().filter(n => n.tagName === "h3").length, 2);
  fake.loi({chiTiet: new Error("DEMO/path/private")});
  assert.equal(await ctl.docBaiDo("DEMO-1"), false);
  assert.equal(root.all().filter(n => n.tagName === "h3").length, 1);
  assert.match(root.textContent, /Đã đọc bài đo DEMO/);
  fake.loi({tim: new Error("DEMO/private")}); await ctl.refresh();
  assert.equal(root.all().filter(n => n.tagName === "h3").length, 0);
  assert.doesNotMatch(root.textContent, /private/);
});
test("Thu quyền rồi đọc lại phải xóa bài đo đang hiện", async () => {
  const fake = coreGia(), root = goc(); const ctl = await mount(root, {...fake, phapNhanId: "DEMO-P"});
  await ctl.docBaiDo("DEMO-1");
  fake.quyen.clear(); await ctl.refresh();
  assert.equal(root.all().filter(n => n.tagName === "h3").length, 0);
  assert.equal(root.nut("Trang sau").disabled, true);
});
test("Lỗi quyền đọc chi tiết cũng xóa dữ liệu cũ, chỉ phần lỗi báo lỗi", async () => {
  const fake = coreGia(), root = goc(); const ctl = await mount(root, {...fake, phapNhanId: "DEMO-P"});
  await ctl.docBaiDo("DEMO-1");
  fake.quyen.clear(); await ctl.docBaiDo("DEMO-1");
  assert.equal(root.all().filter(n => n.tagName === "h3").length, 0);
  assert.match(root.textContent, /Chưa đọc được chi tiết/);
  assert.equal(root.nut("Trang sau").disabled, true);
});
test("XSS trong metadata/lỗi SDK không dựng HTML hoặc phản chiếu vào màn", async () => {
  const b = ban(); b.gia_tri.trang_thai = '<img src=x onerror="DEMO">';
  b.gia_tri.chi_so = JSON.stringify({tra_loi_dung: {tu_so: "<script>DEMO</script>", mau_so: 1}});
  const root = goc(), fake = coreGia({cacBan: [b]});
  await mount(root, {...fake, phapNhanId: "DEMO-P"});
  assert.equal(root.all().filter(n => ["img", "script"].includes(n.tagName)).length, 0);
  assert.doesNotMatch(root.textContent, /<script>|<img/);
});
test("Đọc chậm/unmount không vẽ lại, quá 500 hàng hoặc cursor lặp bị từ chối", async () => {
  const fake = coreGia(), root = goc(); const ctl = await mount(root, {...fake, phapNhanId: "DEMO-P"});
  fake.cong.ngan.tim = async () => ({danh_sach: Array.from({length: 501}, () => ban()), tiep: null});
  assert.equal(await ctl.refresh(), false);
  fake.cong.ngan.tim = async () => ({danh_sach: [ban()], tiep: "DEMO-cursor-lap"});
  assert.equal(await ctl.refresh(), true);
  assert.equal(await ctl.taiTrang("DEMO-cursor-lap"), false);
  let resolve;
  fake.cong.ngan.tim = () => new Promise(r => {resolve = r;});
  const pending = ctl.refresh(); ctl.unmount(); resolve({danh_sach: [ban()], tiep: null}); await pending;
  assert.equal(root.textContent, "");
});
test("Quét tĩnh UI: không mạng/mã thực thi động/HTML, quyền manifest tách khỏi SDK 2.0", async () => {
  for (const ten of ["cau_hinh", "trang_thai"]) {
    const text = await readFile(new URL(`../../goi/e_tra_cuu/ui/${ten}.js`, import.meta.url), "utf8");
    assert.doesNotMatch(text, /\b(?:fetch|eval|XMLHttpRequest|WebSocket)\s*\(|\binnerHTML\s*=|\bnew\s+Function\b/);
    assert.match(text, /KttCore\.engine\("e_tra_cuu"\)/);
  }
  const khai = JSON.parse(await readFile(new URL("../../goi/e_tra_cuu/KHAI-SDK-2.1.json", import.meta.url)));
  assert.equal(khai.giao_dien_quan_tri.find(m => m.ma === "cau_hinh").quyen, "admin_core");
  assert.equal(khai.giao_dien_quan_tri.find(m => m.ma === "trang_thai").quyen, "xem_dot_kiem_theo_phap_nhan");
  const phieu = JSON.parse(await readFile(new URL("../../goi/e_tra_cuu/engine.json", import.meta.url)));
  assert.ok(!("giao_dien_quan_tri" in phieu) && "ngan_du_lieu" in phieu);
  assert.equal(phieu.tuong_thich.sdk, ">=2.2.0 <3.0.0");
});
