import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {mount, kiemCauHinh, catDoan, nganSach} from "../../goi/e_tra_cuu/ui/cau_hinh.js";
import {goc, coreGia, cauHinh} from "./ho_tro.js";

test("Các trường, trần, default UI khớp schema đóng gói", async () => {
  const schema = JSON.parse(await readFile(new URL("../../goi/e_tra_cuu/cau_hinh.schema.json", import.meta.url)));
  for (const [nhom, fields] of [["cat_doan", catDoan], ["ngan_sach", nganSach]]) {
    const props = schema.properties[nhom].properties;
    assert.deepEqual(Object.keys(fields).sort(), Object.keys(props).sort());
    for (const [ma, [, min, max, md]] of Object.entries(fields)) {
      assert.deepEqual([min, max, md], [props[ma].minimum, props[ma].maximum, props[ma].default]);
    }
  }
});
test("Đọc/lưu CAS; default trên bản sao, không tự lưu khi mount", async () => {
  const fake = coreGia(), root = goc();
  await mount(root, fake);
  assert.equal(fake.luu.length, 0);
  assert.equal(root.ten("cat_doan.do_dai_muc_tieu").value, "2000");
  root.ten("cat_doan.do_dai_muc_tieu").value = "3000";
  await root.all().find(n => n.tagName === "form").fire("submit");
  assert.equal(fake.luu.length, 1);
  assert.equal(fake.luu[0].ver, 1);
  assert.equal(fake.luu[0].v.cat_doan.do_dai_muc_tieu, 3000);
  assert.match(root.textContent, /Đã lưu cấu hình/);
  assert.match(root.textContent, /Chưa đo/);
  assert.doesNotMatch(root.textContent, /0%/);
  assert.deepEqual(fake.engines, ["e_tra_cuu"]);
});
test("Thiếu cấu hình: chỉ lưu khi người dùng điền hợp lệ, CAS tạo null", async () => {
  const fake = coreGia({cau_hinh: null}), root = goc();
  await mount(root, fake);
  assert.match(root.textContent, /chưa được cấu hình/);
  const form = root.all().find(n => n.tagName === "form");
  await form.fire("submit");
  assert.equal(fake.luu.length, 0);
  root.ten("tep_id").value = "tep-DEMO"; root.ten("bam").value = cauHinh().quy_tac_nhom.bam;
  await form.fire("submit");
  assert.equal(fake.luu[0].ver, null);
});
for (const sua of [c => c.local_ai = {url: "DEMO"}, c => c.phien_ban = 2,
  c => c.phan_loai = {trang_thai: null}, c => c.phan_loai = {nguong: 0.99},
  c => c.phan_loai = {trang_thai: "da_do"}, c => c.cat_doan = {do_dai_muc_tieu: 9000},
  c => c.ngan_sach = {so_ung_vien_toi_da: false}, c => c.ngan_sach = null,
  c => c.quy_tac_nhom.bam = "DEMO-sai"]) {
  test(`Cấu hình sai bị chặn: ${sua}`, async () => {
    const c = cauHinh(); sua(c);
    assert.throws(() => kiemCauHinh(c));
    const root = goc(), fake = coreGia({cau_hinh: c});
    await mount(root, fake);
    assert.equal(root.nut("Lưu cấu hình").disabled, true);
    assert.equal(fake.luu.length, 0);
  });
}
test("CAS xung đột đọc lại bản mới, không âm thầm ghi đè; lần sau dùng phiên bản mới", async () => {
  const root = goc(), fake = coreGia(); await mount(root, fake);
  const c = cauHinh(); c.cat_doan = {do_dai_muc_tieu: 4000}; fake.doiCauHinh(c);
  const form = root.all().find(n => n.tagName === "form");
  await form.fire("submit");
  assert.equal(fake.luu.length, 1);
  assert.match(root.textContent, /đã thay đổi.*thử lưu lại/);
  assert.equal(root.ten("cat_doan.do_dai_muc_tieu").value, "4000");
  await form.fire("submit");
  assert.equal(fake.luu[1].ver, 2);
  assert.match(root.textContent, /Đã lưu/);
});
test("CAS + lỗi quyền đọc lại: khóa lưu, không lộ dữ liệu cũ hoặc lỗi SDK", async () => {
  const root = goc(), fake = coreGia(); await mount(root, fake);
  fake.loi({ghi: {ma: "NGAN_XUNG_DOT"}, doc: new Error("DEMO-BI-MAT")});
  await root.all().find(n => n.tagName === "form").fire("submit");
  assert.equal(root.nut("Lưu cấu hình").disabled, true);
  assert.equal(root.ten("tep_id").value, "");
  assert.doesNotMatch(root.textContent, /DEMO-BI-MAT/);
});
test("XSS là text/value; không có ô URL/model/khóa và không kích hoạt ngưỡng", async () => {
  const root = goc(), c = cauHinh(); c.quy_tac_nhom.tep_id = '<img-onerror="DEMO">';
  c.phan_loai = {trang_thai: "da_do", nguong: 0.91, bam_bo_do: c.quy_tac_nhom.bam};
  const fake = coreGia({cau_hinh: c}); await mount(root, fake);
  assert.equal(root.ten("tep_id").value, c.quy_tac_nhom.tep_id);
  assert.equal(root.all().filter(n => n.tagName === "img").length, 0);
  assert.ok(!root.ten("nguong") && !root.ten("url") && !root.ten("model") && !root.ten("khoa"));
  await root.all().find(n => n.tagName === "form").fire("submit");
  assert.deepEqual(fake.luu[0].v.phan_loai, c.phan_loai);
});
test("Trường số rỗng/ngoài trần/quan hệ sai không được lưu", async () => {
  const root = goc(), fake = coreGia(); await mount(root, fake);
  const form = root.all().find(n => n.tagName === "form");
  for (const v of ["", "0", "200.5", "8001", "Infinity", "NaN"]) {
    root.ten("cat_doan.do_dai_muc_tieu").value = v; await form.fire("submit");
  }
  root.ten("cat_doan.do_dai_muc_tieu").value = "8000";
  root.ten("cat_doan.ky_tu_don_vi_toi_da").value = "200"; await form.fire("submit");
  assert.equal(fake.luu.length, 0);
});
test("Lỗi quyền khi lưu không lộ path/data và phải đọc lại", async () => {
  const root = goc(), fake = coreGia(); await mount(root, fake);
  fake.loi({ghi: new Error("DEMO/path/private")});
  await root.all().find(n => n.tagName === "form").fire("submit");
  assert.doesNotMatch(root.textContent, /private/);
  assert.equal(root.nut("Lưu cấu hình").disabled, true);
});
test("Unmount ngăn response đọc chậm vẽ lại", async () => {
  const root = goc(), fake = coreGia(); const ctl = await mount(root, fake);
  let resolve;
  fake.cong.cau_hinh.doc = () => new Promise(r => {resolve = r;});
  const pending = ctl.refresh(); ctl.unmount(); resolve({gia_tri: cauHinh(), phien_ban_cau_hinh: 1}); await pending;
  assert.equal(root.textContent, "");
});
