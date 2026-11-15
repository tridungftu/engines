// Màn quản trị OCR; chỉ trao đổi qua KttCore, mọi nội dung dùng textContent.
const macDinh = {
  abbyy: {bat: false, thu_muc_vao: "", thu_muc_ra: "", thoi_han_giay: 900, han_muc_trang_30_ngay: 5000},
  tesseract: {duong_dan: "", ngon_ngu: "vie+eng"},
};
const so = n => new Intl.NumberFormat("vi-VN").format(n);
const ngayGio = luc => new Intl.DateTimeFormat("vi-VN", {
  day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
}).format(new Date(luc));

export async function mount(goc, {
  KttCore = globalThis.KttCore, dongHo = () => Date.now(),
  lapLai = globalThis.setInterval, dungLap = globalThis.clearInterval,
} = {}) {
  const cong = KttCore.engine("e_ocr");
  const doc = goc.ownerDocument;
  let phien = null, cauHinh = structuredClone(macDinh), daDong = false;
  const o = {};
  function nut(ten, text, cha = goc) {
    const n = doc.createElement(ten);
    if (text !== undefined) n.textContent = text;
    cha.appendChild(n);
    return n;
  }
  goc.replaceChildren();
  nut("h2", "Cấu hình OCR");
  nut("p", "Ưu tiên ABBYY; dùng Tesseract khi nguồn ưu tiên không xử lý được.");
  const form = nut("form");
  function truong(ma, nhan, kieu, cha, min, max) {
    const label = nut("label", nhan, cha);
    const input = nut("input", undefined, label);
    input.name = ma;
    input.type = kieu;
    if (min !== undefined) input.min = String(min);
    if (max !== undefined) input.max = String(max);
    if (kieu !== "checkbox") input.required = kieu === "number" || ma === "ngon_ngu";
    if (kieu === "text") input.maxLength = ma === "ngon_ngu" ? 200 : 4096;
    o[ma] = input;
  }
  const abbyy = nut("fieldset", undefined, form);
  nut("legend", "ABBYY Hot Folder", abbyy);
  truong("bat", "Bật ABBYY", "checkbox", abbyy);
  truong("thu_muc_vao", "Thư mục nhận tài liệu", "text", abbyy);
  truong("thu_muc_ra", "Thư mục trả kết quả", "text", abbyy);
  truong("thoi_han_giay", "Thời hạn chờ (giây)", "number", abbyy, 1, 900);
  truong("han_muc_trang_30_ngay", "Hạn mức trang trong 30 ngày", "number", abbyy, 0, 5000);
  const tess = nut("fieldset", undefined, form);
  nut("legend", "Tesseract dự phòng", tess);
  truong("duong_dan", "Đường dẫn Tesseract (để trống để tự tìm)", "text", tess);
  truong("ngon_ngu", "Ngôn ngữ", "text", tess);
  const luu = nut("button", "Lưu cấu hình", form);
  luu.type = "submit";
  luu.disabled = true;
  const taiLai = nut("button", "Tải lại cấu hình", form);
  taiLai.type = "button";
  const thongBao = nut("p", "");
  thongBao.setAttribute("role", "status");
  nut("h3", "Hạn mức và trạng thái");
  const trangThai = nut("p", "Đang đọc trạng thái ABBYY…");
  const hanMuc = nut("p", "Đang đọc hạn mức…");
  nut("h3", "Các lượt đang chờ đối chiếu");
  const danhSach = nut("ul");

  async function taiCauHinh() {
    const data = await cong.cau_hinh.doc();
    phien = data?.phien_ban_cau_hinh ?? null;
    const giaTri = data?.gia_tri ?? {};
    cauHinh = {
      abbyy: {...macDinh.abbyy, ...giaTri.abbyy},
      tesseract: {...macDinh.tesseract, ...giaTri.tesseract},
    };
    for (const [ma, input] of Object.entries(o)) {
      const value = (ma in cauHinh.abbyy ? cauHinh.abbyy : cauHinh.tesseract)[ma];
      if (input.type === "checkbox") input.checked = value;
      else input.value = String(value);
    }
    luu.disabled = false;
  }

  async function timHet(bang, loc) {
    const ds = [];
    let tiep = null;
    do {
      const trang = await cong.ngan.tim(bang, {loc, gioi_han: 500, tiep});
      ds.push(...trang.danh_sach.map(b => b.gia_tri));
      tiep = trang.tiep;
    } while (tiep != null);
    return ds;
  }

  async function refresh() {
    try {
      const [tt, ngay, chuaRo, dangGui] = await Promise.all([
        cong.ngan.doc("trang_thai_engine", {ma: "abbyy"}),
        timHet("han_muc_ngay", {}),
        timHet("luot_abbyy", {trang_thai: "chua_ro"}),
        timHet("luot_abbyy", {trang_thai: "dang_gui"}),
      ]);
      if (daDong) return;
      const moc = Math.floor(dongHo() / 1000) - 30 * 86400;
      let daDung = 0, dangGiu = 0;
      for (const b of ngay) {
        const dauNgay = Date.parse(b.ngay + "T00:00:00Z") / 1000;
        for (const [giay, n] of Object.entries(b.da_nhan)) {
          if (dauNgay + Number(giay) > moc) daDung += n;
        }
        dangGiu += Object.values(b.dang_giu).reduce((a, b) => a + b, 0);
      }
      const conLai = Math.max(0, cauHinh.abbyy.han_muc_trang_30_ngay - daDung - dangGiu);
      hanMuc.textContent = `Đã dùng ${so(daDung)} trang trong 30 ngày · Đang giữ ${so(dangGiu)} trang · Còn lại ${so(conLai)} trang`;
      const b = tt?.gia_tri;
      const luc = Date.parse(b?.luc_kiem);
      if (!Number.isFinite(luc) || dongHo() - luc > 90000 || luc > dongHo() + 5000) {
        trangThai.textContent = "ABBYY: chưa có cập nhật gần đây.";
      } else {
        const lyDo = {chua_cau_hinh: "chưa cấu hình", dang_tat: "đã tắt trong cấu hình",
          khong_ket_noi: "không truy cập được thư mục", cau_hinh_loi: "cần kiểm tra cấu hình"};
        trangThai.textContent = `ABBYY: ${b.abbyy_bat ? "Bật" : "Tắt"}${lyDo[b.ly_do] ? " — " + lyDo[b.ly_do] : ""}. Kiểm tra lúc ${ngayGio(luc)}.`;
      }
      danhSach.replaceChildren();
      const ds = [...chuaRo, ...dangGui].sort((a, b) => a.luc_giu - b.luc_giu);
      if (!ds.length) nut("li", "Không có lượt đang chờ đối chiếu.", danhSach);
      ds.forEach((b, i) => nut("li", `Lượt ${so(i + 1)} · ${so(b.so_trang)} trang · ${ngayGio(b.luc_giu * 1000)} · ${b.trang_thai === "chua_ro" ? "Chưa rõ kết quả" : "Đang gửi hoặc chờ đối chiếu"}`, danhSach));
    } catch {
      if (!daDong) {
        trangThai.textContent = "Chưa đọc được trạng thái ABBYY.";
        hanMuc.textContent = "Chưa đọc được hạn mức. Hãy tải lại màn hình.";
        danhSach.replaceChildren();
        nut("li", "Chưa đọc được các lượt đang chờ đối chiếu.", danhSach);
      }
    }
  }

  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (luu.disabled) return;
    const moi = {abbyy: {bat: o.bat.checked}, tesseract: {}};
    for (const ma of Object.keys(macDinh.abbyy).filter(ma => ma !== "bat")) {
      moi.abbyy[ma] = o[ma].type === "number" ? Number(o[ma].value) : o[ma].value.trim();
    }
    moi.tesseract = {duong_dan: o.duong_dan.value.trim(), ngon_ngu: o.ngon_ngu.value.trim()};
    if (!Number.isInteger(moi.abbyy.thoi_han_giay) || moi.abbyy.thoi_han_giay < 1 || moi.abbyy.thoi_han_giay > 900 ||
        !Number.isInteger(moi.abbyy.han_muc_trang_30_ngay) || moi.abbyy.han_muc_trang_30_ngay < 0 || moi.abbyy.han_muc_trang_30_ngay > 5000 ||
        !moi.tesseract.ngon_ngu) {
      thongBao.textContent = "Thời hạn phải từ 1 đến 900 giây, hạn mức từ 0 đến 5.000 trang và cần có ngôn ngữ.";
      return;
    }
    luu.disabled = true;
    try {
      const ketQua = await cong.cau_hinh.luu(moi, phien);
      phien = ketQua.phien_ban_cau_hinh;
      cauHinh = moi;
      thongBao.textContent = "Đã lưu cấu hình OCR.";
      await refresh();
    } catch (loi) {
      if (loi.ma === "NGAN_XUNG_DOT" || loi.status === 409) {
        thongBao.textContent = "Cấu hình đã được người khác sửa. Hãy bấm Tải lại cấu hình trước khi lưu lại.";
        return; // Giữ khóa Lưu cho tới khi đã đọc phiên mới.
      }
      thongBao.textContent = "Chưa lưu được cấu hình. Hãy thử lại.";
    }
    luu.disabled = false;
  });
  taiLai.addEventListener("click", async () => {
    try {
      await taiCauHinh();
      thongBao.textContent = "Đã tải lại cấu hình.";
      await refresh();
    } catch {
      thongBao.textContent = "Chưa đọc được cấu hình. Hãy thử lại.";
    }
  });
  try {
    await taiCauHinh();
  } catch {
    thongBao.textContent = "Chưa đọc được cấu hình. Hãy bấm Tải lại cấu hình.";
  }
  await refresh();
  const chuKy = lapLai(() => { if (!daDong) void refresh(); }, 30000);
  return {refresh, destroy() { daDong = true; dungLap(chuKy); goc.replaceChildren(); }};
}

export default mount;
