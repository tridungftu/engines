import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const ma = await readFile(new URL("../../goi/e_trich_xuat/ui/cau_hinh.js", import.meta.url), "utf8");
const { nap } = await import("data:text/javascript;base64," + Buffer.from(ma).toString("base64"));

class PhanTu {
  constructor(ten, doc) { this.ten = ten; this.ownerDocument = doc; this.children = []; this.listeners = new Map(); this.textContent = ""; }
  append(...ds) { this.children.push(...ds); }
  replaceChildren(...ds) { this.children = [...ds]; }
  setAttribute(ten, v) { this[ten] = v; }
  addEventListener(ten, ham) { this.listeners.set(ten, ham); }
  removeEventListener(ten, ham) { if (this.listeners.get(ten) === ham) this.listeners.delete(ten); }
  async submit() { await this.listeners.get("submit")?.({ preventDefault() {} }); }
}

async function man({ giaTri = { ngan_sach_token_vao_toi_da: 16000 }, phienBan = 7, luu, doc } = {}) {
  const taiLieu = { createElement(ten) { return new PhanTu(ten, taiLieu); } };
  const goc = new PhanTu("root", taiLieu);
  const daLuu = [];
  const KttCore = { engine(ma) {
    assert.equal(ma, "e_trich_xuat");
    return { cau_hinh: {
      doc: doc ?? (async () => ({ gia_tri: giaTri, phien_ban_cau_hinh: phienBan })),
      luu: async (v, pv) => { daLuu.push([v, pv]); return luu ? luu(v, pv) : { gia_tri: v, phien_ban_cau_hinh: 8 }; }
    } };
  } };
  const dong = await nap({ goc, KttCore });
  const form = goc.children[0];
  const [nhan, o, nut, bao] = form.children;
  return { goc, form, nhan, o, nut, bao, daLuu, dong };
}

test("đọc và lưu giá trị cùng phiên bản CAS, không hiện mã kỹ thuật", async () => {
  const m = await man();
  assert.equal(m.o.value, "16000");
  m.o.value = "20000";
  await m.form.submit();
  assert.deepEqual(m.daLuu, [[{ ngan_sach_token_vao_toi_da: 20000 }, 7]]);
  assert.equal(m.bao.textContent, "Đã lưu cấu hình.");
  m.o.value = "21000";
  await m.form.submit();
  assert.equal(m.daLuu[1][1], 8);
  assert.doesNotMatch(m.bao.textContent, /row_version|phien_ban|UUID|sha256/);
});

test("thiếu bản ghi chỉ gợi ý, không tự lưu; nút Lưu tạo qua Core", async () => {
  const m = await man({ giaTri: null, phienBan: null });
  assert.equal(m.o.value, "16000");
  assert.equal(m.daLuu.length, 0);
  assert.match(m.bao.textContent, /chưa được cấu hình/);
  await m.form.submit();
  assert.deepEqual(m.daLuu, [[{ ngan_sach_token_vao_toi_da: 16000 }, null]]);
});

test("xung đột CAS hiện câu tiếng Việt, giữ phiên bản cũ và không ghi đè", async () => {
  const m = await man({ luu() { throw { ma: "NGAN_XUNG_DOT", message: "DEMO nội dung kỹ thuật không được hiện" }; } });
  m.o.value = "20000";
  await m.form.submit();
  assert.equal(m.bao.textContent, "Cấu hình đã được người khác thay đổi. Hãy mở lại màn hình rồi lưu.");
  assert.equal(m.daLuu.length, 1);
  assert.equal(m.o.value, "20000");
  await m.form.submit();
  assert.equal(m.daLuu[1][1], 7);
});

test("giới hạn số nguyên và chặn gửi lặp khi đang lưu", async () => {
  let tra;
  const m = await man({ luu: () => new Promise((resolve) => { tra = resolve; }) });
  for (const v of ["", "1023", "100001", "16000.5", "NaN", "1e4"]) {
    m.o.value = v;
    await m.form.submit();
  }
  assert.equal(m.daLuu.length, 0);
  m.o.value = "1024";
  const dangLuu = m.form.submit();
  await m.form.submit();
  assert.equal(m.daLuu.length, 1);
  tra({ phien_ban_cau_hinh: 8 });
  await dangLuu;
  assert.equal(m.nut.disabled, false);
});

test("lỗi đọc/lưu không lộ nội dung; tháo màn bỏ listener", async () => {
  const m = await man({ doc() { throw new Error("DEMO chi tiết kỹ thuật"); } });
  assert.equal(m.bao.textContent, "Không đọc được cấu hình. Hãy mở lại màn hình.");
  assert.equal(m.nut.disabled, true);
  m.dong();
  assert.equal(m.form.listeners.size, 0);
  const n = await man({ luu() { throw new Error("DEMO chi tiết kỹ thuật"); } });
  await n.form.submit();
  assert.equal(n.bao.textContent, "Không lưu được cấu hình. Hãy thử lại.");
});

test("màn chỉ có một ô, một nút và dùng cổng KttCore", async () => {
  const m = await man();
  assert.equal(m.form.children.filter((e) => e.ten === "input").length, 1);
  assert.equal(m.form.children.filter((e) => e.ten === "button").length, 1);
  assert.doesNotMatch(ma, /\bfetch\s*\(|XMLHttpRequest|WebSocket|\beval\s*\(|innerHTML|https?:\/\//);
});
