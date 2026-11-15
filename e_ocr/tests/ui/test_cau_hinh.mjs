import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import test from "node:test";

const nguon = await readFile(new URL("../../goi/e_ocr/ui/cau_hinh.js", import.meta.url), "utf8");
const {mount} = await import("data:text/javascript;base64," + Buffer.from(nguon).toString("base64"));
const khai = JSON.parse(await readFile(new URL("../../goi/e_ocr/KHAI-SDK-2.1.json", import.meta.url), "utf8"));
const schema = JSON.parse(await readFile(new URL("../../goi/e_ocr/cau_hinh.schema.json", import.meta.url), "utf8"));

function kiemPhamVi(ten, loc) {
  const bang = khai.ngan_du_lieu.find(b => b.bang === ten);
  if (!bang || (bang.pham_vi === "phap_nhan" &&
      (typeof loc?.phap_nhan_id !== "string" || !loc.phap_nhan_id.trim()))) {
    throw Object.assign(Error("Thiếu phạm vi pháp nhân."), {ma: "NGAN_KHONG_HOP_LE"});
  }
}

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

async function dung({cauHinh = {}, phien = 4, loiLuu = null, loiDoc = false, loiNgan = false, loiPhan = null, tt = null, chuaRo = null, bang = {}} = {}) {
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
          kiemPhamVi(bang, khoa);
          lenh.push({ten: bang, khoa});
          assert.equal(bang, "trang_thai_engine");
          assert.ok(["abbyy", "chua_ro"].includes(khoa.ma));
          if (loiNgan || loiPhan === khoa.ma) throw Error("DEMO lỗi nguồn riêng");
          const b = khoa.ma === "abbyy" ? tt : chuaRo;
          return b == null ? null : {gia_tri: b, row_version: 1};
        },
        async tim(ten, {loc, gioi_han, tiep}) {
          kiemPhamVi(ten, loc);
          lenh.push({ten, loc, tiep});
          if (loiNgan || loiPhan === ten) throw Error("DEMO lỗi nguồn riêng");
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
  return {goc, man, lenh, ngan: gia.engine("e_ocr").ngan,
    input: ma => tim(goc, n => n.name === ma),
    form: () => tim(goc, n => n.tagName === "form"),
    button: text => tim(goc, n => n.tagName === "button" && n.textContent === text),
    cauHinh: () => cauHinh, soLuu: () => soLuu, daDong: () => daDong,
    doiLoi: v => {loiLuu = v;}, tienGio: n => {luc += n;}, chuKy: () => chuKy,
    doiLoiPhan: v => {loiPhan = v;},
  };
}

test("đọc đủ phân trang; cửa sổ đúng 30 ngày, trừ cả trang đang giữ; ẩn mã", async () => {
  const now = Date.parse("2026-11-15T12:00:00Z");
  const a = await dung({tt: {abbyy_bat: true, ly_do: "bat", luc_kiem: new Date(now).toISOString()}, bang: {
    han_muc_ngay: [
      {ngay: "2026-10-16", da_nhan: {43199: 99, 43200: 20, 43201: 3}, dang_giu: {}},
      {ngay: "2026-11-15", da_nhan: {43200: 1250}, dang_giu: {DEMO: 2}},
    ],
  }, chuaRo: {so_luot: 3, theo_ngay: {"2026-11-15": 2, "2026-11-14": 1},
    ma_tuong_quan: "MA_KY_THUAT_DEMO", ten_tep: "DEMO-ten-rieng", phap_nhan_id: "DEMO-phap-nhan"}});
  assert.match(a.goc.textContent, /Đã dùng 1\.253 trang/);
  assert.match(a.goc.textContent, /Đang giữ 2 trang · Còn lại 3\.745 trang/);
  assert.match(a.goc.textContent, /ABBYY: Bật/);
  assert.match(a.goc.textContent, /15\/11\/2026/);
  assert.match(a.goc.textContent, /Lượt 3/);
  assert.match(a.goc.textContent, /Có 3 lượt chưa rõ kết quả/);
  assert.match(a.goc.textContent, /Lượt 1 · 14\/11\/2026/);
  assert.doesNotMatch(a.goc.textContent, /MA_KY_THUAT|DEMO-ten-rieng|DEMO-phap-nhan|Lượt 4/);
  assert.ok(a.lenh.some(l => l.ten === "han_muc_ngay" && l.tiep === "1"));
  assert.ok(a.lenh.some(l => l.ten === "trang_thai_engine" && l.khoa?.ma === "chua_ro"));
  assert.ok(a.lenh.every(l => l.ten !== "luot_abbyy"));
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

test("KttCore giả từ chối bảng pháp nhân thiếu ngữ cảnh như NganBoNho", async () => {
  const a = await dung();
  for (const phap_nhan_id of [undefined, null, "", "   ", 1]) {
    const loc = {phap_nhan_id};
    await assert.rejects(a.ngan.doc("luot_abbyy", loc), {ma: "NGAN_KHONG_HOP_LE"});
    await assert.rejects(a.ngan.tim("luot_abbyy", {loc, gioi_han: 500}), {ma: "NGAN_KHONG_HOP_LE"});
  }
  assert.deepEqual(await a.ngan.tim("luot_abbyy", {loc: {phap_nhan_id: "DEMO-P"}, gioi_han: 500}),
    {danh_sach: [], tiep: null});
  a.man.destroy();
});

for (const phan of ["abbyy", "han_muc_ngay", "chua_ro"]) {
  test(`lỗi riêng ${phan} không làm mất hai phần khác; tải lại khôi phục`, async () => {
    const a = await dung({loiPhan: phan,
      tt: {abbyy_bat: true, luc_kiem: "2026-11-15T12:00:00Z"},
      chuaRo: {so_luot: 1, theo_ngay: {"2026-11-15": 1}}});
    assert.match(a.goc.textContent, phan === "abbyy" ? /Chưa đọc được trạng thái ABBYY/ : /ABBYY: Bật/);
    assert.match(a.goc.textContent, phan === "han_muc_ngay" ? /Chưa đọc được hạn mức/ : /Đã dùng 0 trang/);
    assert.match(a.goc.textContent, phan === "chua_ro" ? /Chưa đọc được các lượt chưa rõ/ : /Lượt 1/);
    assert.doesNotMatch(a.goc.textContent, /lỗi nguồn riêng/);
    a.doiLoiPhan(null); await a.man.refresh();
    assert.doesNotMatch(a.goc.textContent, /Chưa đọc được/);
    a.man.destroy();
  });
}

test("ngôn ngữ là ô chọn đúng enum; từ chối giá trị ngoài danh sách", async () => {
  const a = await dung();
  const input = a.input("ngon_ngu");
  assert.equal(input.tagName, "select");
  assert.deepEqual(input.children.map(n => n.value), schema.properties.tesseract.properties.ngon_ngu.enum);
  assert.equal(input.value, "vie+eng");
  input.value = "fra";
  await a.form().bam("submit"); assert.equal(a.soLuu(), 0);
  for (const v of ["vie", "eng", "vie+eng", "eng+vie"]) {
    input.value = v;
    await a.form().bam("submit");
    assert.equal(a.cauHinh().tesseract.ngon_ngu, v);
  }
  assert.equal(a.soLuu(), 4); a.man.destroy();
});
