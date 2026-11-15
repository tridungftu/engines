import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {mount} from "../../goi/e_tra_cuu/ui/trang_thai.js";
import {goc, coreGia, ban} from "./ho_tro.js";

test("TC-10 hiện bốn cặp số đo DEMO thực, không kích hoạt nhóm hoặc nhận accuracy thật", async () => {
  const report = JSON.parse(await readFile(new URL("../../docs/TC-10-KET-QUA-DEMO.json", import.meta.url), "utf8"));
  assert.equal(report.da_duyet_nghiep_vu, false);
  assert.equal(report.accuracy_model_that, null);
  assert.deepEqual(report.nhom_duoc_kich_hoat, []);
  const b = ban("DEMO-P", "DEMO-TC10");
  b.gia_tri.trang_thai = "da_do";
  b.gia_tri.chi_so = JSON.stringify(Object.fromEntries(Object.entries(report.chi_so).map(([ma, c]) => [ma, {tu_so: c.tu_so, mau_so: c.mau_so}])));
  const fake = coreGia({cacBan: [b]}), root = goc();
  await mount(root, {...fake, phapNhanId: "DEMO-P"});
  assert.match(root.textContent, /12\/12/);
  assert.match(root.textContent, /6\/6/);
  assert.match(root.textContent, /20\/20/);
  assert.equal(fake.luu.length, 0);
  assert.deepEqual(fake.engines, ["e_tra_cuu"]);
});
