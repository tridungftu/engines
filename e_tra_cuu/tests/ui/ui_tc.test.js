import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {mount, kiemCauHinh} from "../../goi/e_tra_cuu/ui/cau_hinh.js";
import {goc, coreGia, cauHinh} from "./ho_tro.js";

test("Cơ bản chỉ có ngưỡng chỉ đọc và độ dài; đủ 15 trần trong Nâng cao thu gọn", async () => {
  const root = goc(); await mount(root, coreGia());
  const nangCao = root.all().find(n => n.tagName === "details");
  assert.ok(!nangCao.open);
  assert.equal(nangCao.all().filter(n => n.tagName === "input" && n.type === "number").length, 15);
  assert.ok(!nangCao.all().includes(root.ten("cat_doan.do_dai_muc_tieu")));
  assert.equal(root.all().find(n => n.id === "tc-nguong").readOnly, true);
  for (const input of root.all().filter(n => n.name)) {
    assert.ok(input.placeholder);
    assert.ok(input["aria-describedby"]);
    assert.ok(root.all().some(n => n.tagName === "label" && n.for === input.id));
  }
});

test("Lỗi cạnh ô cập nhật khi nhập; tự mở Nâng cao khi lưu sai; sửa lại lưu được", async () => {
  const root = goc(), fake = coreGia(); await mount(root, fake);
  const input = root.ten("ngan_sach.so_trang_toi_da"); input.value = "61";
  await input.fire("input");
  const loi = root.all().find(n => n.id === input.id + "-loi");
  assert.match(loi.textContent, /Trần số trang.*1.*60/);
  assert.equal(input["aria-invalid"], "true");
  await root.all().find(n => n.tagName === "form").fire("submit");
  assert.equal(fake.luu.length, 0);
  assert.equal(root.all().find(n => n.tagName === "details").open, true);
  input.value = "60"; await input.fire("input");
  assert.equal(loi.textContent, "");
  assert.equal(input["aria-invalid"], "false");
  await root.all().find(n => n.tagName === "form").fire("submit");
  assert.equal(fake.luu.length, 1);
});

test("Không mặc định ngưỡng đẹp; ngưỡng đã đo vẫn nguyên vẹn sau lưu", async () => {
  const c = cauHinh(); c.phan_loai = {trang_thai: "da_do", nguong: 0.917, bam_bo_do: c.quy_tac_nhom.bam};
  const root = goc(), fake = coreGia({cau_hinh: c}); await mount(root, fake);
  assert.equal(root.all().find(n => n.id === "tc-nguong").value, "91,7%");
  await root.all().find(n => n.tagName === "form").fire("submit");
  assert.deepEqual(fake.luu[0].v.phan_loai, c.phan_loai);
});

test("Không có dịch vụ/máy/bí mật trong UI-TC; không chạm cổng thao tác hoặc két", async () => {
  const fake = coreGia(), root = goc();
  for (const ten of ["thao_tac", "bi_mat"]) Object.defineProperty(fake.cong, ten, {get() {throw new Error("Không được chạm cổng này.");}});
  await mount(root, fake);
  await root.all().find(n => n.tagName === "form").fire("submit");
  assert.equal(fake.luu.length, 1);
  assert.ok(!root.all().some(n => n.type === "password"));
  assert.deepEqual(root.all().filter(n => n.tagName === "button").map(n => n.textContent), ["Lưu cấu hình", "Đọc lại cấu hình"]);
});

test("Không gửi hai lần khi lưu chậm; khóa sửa và đọc lại cho tới khi hoàn tất", async () => {
  const root = goc(), fake = coreGia(); const ctl = await mount(root, fake);
  const luu = fake.cong.cau_hinh.luu;
  let tiep;
  fake.cong.cau_hinh.luu = async (...args) => {await new Promise(r => {tiep = r;}); return luu(...args);};
  const form = root.all().find(n => n.tagName === "form");
  const pending = form.fire("submit");
  assert.equal(root.ten("tep_id").disabled, true);
  assert.equal(root.nut("Đọc lại cấu hình").disabled, true);
  assert.equal(await ctl.refresh(), false);
  await form.fire("submit"); tiep(); await pending;
  assert.equal(fake.luu.length, 1);
  assert.equal(root.ten("tep_id").disabled, false);
});

test("Metadata tiếng Việt đủ từng cấp; mẫu đầy đủ qua kiểm nghiệp vụ hiện hành", async () => {
  const schema = JSON.parse(await readFile(new URL("../../goi/e_tra_cuu/cau_hinh.schema.json", import.meta.url)));
  function kiem(n, duong = "") {
    assert.ok(n.title && n.description && n.examples?.length, duong);
    assert.doesNotMatch(n.title + n.description, /\?/);
    for (const [k, v] of Object.entries(n.properties ?? {})) {
      assert.ok(schema.description.includes(duong + k));
      kiem(v, duong + k + ".");
    }
  }
  kiem(schema);
  for (const mau of schema.examples) assert.doesNotThrow(() => kiemCauHinh(mau));
  assert.equal(Object.keys(schema.examples[0].ngan_sach).length, 13);
});

test("Hai màn bỏ xưng hô; không còn thông báo ngăn RAM đã lỗi thời", async () => {
  for (const ten of ["cau_hinh", "trang_thai"]) {
    const ma = await readFile(new URL(`../../goi/e_tra_cuu/ui/${ten}.js`, import.meta.url), "utf8");
    assert.doesNotMatch(ma, /\bAnh\b|\bbạn\b|Ngăn RAM/);
  }
});
