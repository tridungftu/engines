import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import test from "node:test";

const nguon = await readFile(new URL("../../goi/e_ocr/ui/cau_hinh.js", import.meta.url), "utf8");
const {mount} = await import("data:text/javascript;base64," + Buffer.from(nguon).toString("base64"));

class Nut {
  constructor(ten, doc) { this.tagName = ten; this.ownerDocument = doc; this.children = []; this.events = {}; this.chu = ""; }
  appendChild(n) { this.children.push(n); return n; }
  replaceChildren(...ds) { this.children = ds; this.chu = ""; }
  set textContent(v) { this.chu = String(v); this.children = []; }
  get textContent() { return this.chu + this.children.map(n => n.textContent).join(" "); }
  setAttribute(k, v) { this[k] = v; }
  addEventListener(ten, ham) { this.events[ten] = ham; }
  async bam(ten = "click") { await this.events[ten]?.({preventDefault() {}}); }
}
function tim(goc, ham) { return ham(goc) ? goc : goc.children.map(n => tim(n, ham)).find(Boolean); }
function duyet(goc) { return [goc, ...goc.children.flatMap(duyet)]; }

async function dung({cauHinh = {}, phien = 4, loiLuu = null, loiDoc = false, loiNgan = false, tt = null, bang = {}} = {}) {
  let luc = Date.parse("2026-11-15T12:00:00Z"), soLuu = 0, daDong = false, chuKy;
  const lenh = [];
  const doc = {createElement: ten => new Nut(ten, doc)};
  const goc = new Nut("div", doc);
  const gia = {engine(ma) {
    assert.equal(ma, "e_ocr");
    return {
      cau_hinh: {
        async doc() {
          if (loiDoc) throw Error("DEMO đường dẫn riêng");
          return cauHinh == null ? null : {gia_tri: structuredClone(cauHinh), phien_ban_cau_hinh: phien};
        },
        async luu(giaTri, phienCu) {
          soLuu++;
          if (loiLuu) throw loiLuu;
          assert.equal(phienCu, phien);
          cauHinh = structuredClone(giaTri);
          phien = (phien ?? 0) + 1;
          return {phien_ban_cau_hinh: phien};
        },
      },
      ngan: {
        async doc(bang, khoa) {
          assert.equal(bang, "trang_thai_engine"); assert.deepEqual(khoa, {ma: "abbyy"});
          if (loiNgan) throw Error("DEMO lỗi nguồn riêng");
          return tt == null ? null : {gia_tri: tt, row_version: 1};
        },
        async tim(ten, {loc, gioi_han, tiep}) {
          lenh.push({ten, loc, tiep});
          assert.equal(gioi_han, 500);
          const ds = (bang[ten] ?? []).filter(b => Object.entries(loc).every(([k, v]) => b[k] === v));
          const dau = Number(tiep ?? 0);
          // Chỉ trả một hàng để bắt buộc màn đọc hết phân trang.
          return {danh_sach: ds.slice(dau, dau + 1).map(b => ({gia_tri: b})), tiep: dau + 1 < ds.length ? String(dau + 1) : null};
        },
      },
    };
  }};
  const man = await mount(goc, {KttCore: gia, dongHo: () => luc,
    lapLai(ham, n) { assert.equal(n, 30000); chuKy = ham; return 123; },
    dungLap(ma) { assert.equal(ma, 123); daDong = true; },
  });
  return {goc, man, lenh,
    input: ma => tim(goc, n => n.name === ma),
    form: () => tim(goc, n => n.tagName === "form"),
    button: text => tim(goc, n => n.tagName === "button" && n.textContent === text),
    cauHinh: () => cauHinh, soLuu: () => soLuu, daDong: () => daDong,
    doiLoi: v => {loiLuu = v;}, tienGio: n => {luc += n;}, chuKy: () => chuKy,
  };
}

test("đọc đủ phân trang; cửa sổ đúng 30 ngày, trừ cả trang đang giữ; ẩn mã", async () => {
  const now = Date.parse("2026-11-15T12:00:00Z");
  const a = await dung({tt: {abbyy_bat: true, ly_do: "bat", luc_kiem: new Date(now).toISOString()}, bang: {
    han_muc_ngay: [
      {ngay: "2026-10-16", da_nhan: {43199: 99, 43200: 20, 43201: 3}, dang_giu: {}},
      {ngay: "2026-11-15", da_nhan: {43200: 1250}, dang_giu: {DEMO: 2}},
    ],
    luot_abbyy: [
      {ma_tuong_quan: "MA_KY_THUAT_DEMO", trang_thai: "chua_ro", so_trang: 1, luc_giu: now / 1000},
      {ma_tuong_quan: "MA_KY_THUAT_KHAC", trang_thai: "chua_ro", so_trang: 2, luc_giu: now / 1000},
      {trang_thai: "dang_gui", so_trang: 3, luc_giu: now / 1000},
      {trang_thai: "xong", so_trang: 60, luc_giu: now / 1000},
    ],
  }});
  assert.match(a.goc.textContent, /Đã dùng 1\.253 trang/);
  assert.match(a.goc.textContent, /Đang giữ 2 trang · Còn lại 3\.745 trang/);
  assert.match(a.goc.textContent, /ABBYY: Bật/);
  assert.match(a.goc.textContent, /15\/11\/2026/);
  assert.match(a.goc.textContent, /Lượt 3/);
  assert.doesNotMatch(a.goc.textContent, /MA_KY_THUAT|Lượt 4/);
  assert.ok(a.lenh.some(l => l.ten === "luot_abbyy" && l.tiep === "1"));
  a.man.destroy(); assert.equal(a.daDong(), true); assert.equal(a.goc.textContent, "");
});

test("lưu tất cả trường bằng CAS, giữ tiếng Việt và phiên mới", async () => {
  const a = await dung();
  a.input("bat").checked = true;
  a.input("thu_muc_vao").value = "DEMO/nhan";
  a.input("thu_muc_ra").value = "DEMO/tra";
  a.input("thoi_han_giay").value = "120";
  a.input("han_muc_trang_30_ngay").value = "4000";
  a.input("duong_dan").value = "DEMO/tesseract";
  a.input("ngon_ngu").value = "vie+eng";
  await a.form().bam("submit");
  assert.deepEqual(a.cauHinh(), {abbyy: {bat: true, thu_muc_vao: "DEMO/nhan", thu_muc_ra: "DEMO/tra", thoi_han_giay: 120, han_muc_trang_30_ngay: 4000},
    tesseract: {duong_dan: "DEMO/tesseract", ngon_ngu: "vie+eng"}});
  assert.match(a.goc.textContent, /Đã lưu cấu hình OCR/);
  await a.form().bam("submit"); assert.equal(a.soLuu(), 2);
  a.man.destroy();
});

test("CAS xung đột: giữ nội dung, khóa lưu tới khi tải lại; không lộ lỗi kỹ thuật", async () => {
  const a = await dung({loiLuu: {ma: "NGAN_XUNG_DOT", message: "DEMO lỗi riêng"}});
  a.input("ngon_ngu").value = "eng";
  await a.form().bam("submit");
  assert.match(a.goc.textContent, /Cấu hình đã được người khác sửa/);
  assert.doesNotMatch(a.goc.textContent, /NGAN_XUNG_DOT|lỗi riêng/);
  assert.equal(a.input("ngon_ngu").value, "eng");
  await a.form().bam("submit"); assert.equal(a.soLuu(), 1);
  a.doiLoi(null);
  await a.button("Tải lại cấu hình").bam();
  assert.equal(a.input("ngon_ngu").value, "vie+eng");
  await a.form().bam("submit"); assert.equal(a.soLuu(), 2);
  a.man.destroy();
});

test("từ chối số ngoài trần và không gửi API", async () => {
  const a = await dung();
  for (const [ma, v] of [["han_muc_trang_30_ngay", "5001"], ["thoi_han_giay", "1.5"]]) {
    a.input(ma).value = v;
    await a.form().bam("submit");
    assert.match(a.goc.textContent, /Thời hạn phải từ 1 đến 900 giây/);
    a.input(ma).value = ma === "thoi_han_giay" ? "900" : "5000";
  }
  assert.equal(a.soLuu(), 0); a.man.destroy();
});

test("trạng thái từ engine, không suy từ công tắc; hết hạn phải báo chưa cập nhật", async () => {
  const a = await dung({cauHinh: {abbyy: {bat: true}}, tt: {
    abbyy_bat: false, ly_do: "khong_ket_noi", luc_kiem: "2026-11-15T12:00:00Z",
  }});
  assert.match(a.goc.textContent, /ABBYY: Tắt — không truy cập được thư mục/);
  a.tienGio(91000); await a.man.refresh();
  assert.match(a.goc.textContent, /ABBYY: chưa có cập nhật gần đây/);
  a.man.destroy();
});

test("cấu hình mới dùng phiên null; lỗi đọc không cho ghi đè", async () => {
  const a = await dung({cauHinh: null, phien: null});
  await a.form().bam("submit"); assert.equal(a.soLuu(), 1); a.man.destroy();
  const b = await dung({loiDoc: true, loiNgan: true});
  assert.match(b.goc.textContent, /Chưa đọc được cấu hình/);
  assert.match(b.goc.textContent, /Chưa đọc được hạn mức/);
  await b.form().bam("submit"); assert.equal(b.soLuu(), 0); b.man.destroy();
});

test("nội dung lạ chỉ vào ô chữ, mã màn không dùng mạng hoặc thực thi HTML", async () => {
  assert.doesNotMatch(nguon, /\b(?:fetch|XMLHttpRequest|WebSocket|eval)\s*\(|\.innerHTML\s*=/);
  const a = await dung({cauHinh: {abbyy: {thu_muc_vao: '<img src=x onerror="DEMO">'}}});
  assert.equal(a.input("thu_muc_vao").value, '<img src=x onerror="DEMO">');
  assert.ok(duyet(a.goc).every(n => n.tagName !== "img")); a.man.destroy();
});
