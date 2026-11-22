// `luaChon.cua` do host Core cấp khi nạp màn, là adapter C-DC-03/04 đang đề nghị.
// Không suy quyền từ JSON hồ sơ hoặc dùng API ghi ngăn Admin để xác nhận.
const MUC = {nghiem_trong: "Nghiêm trọng", can_xem: "Cần xem", hinh_thuc: "Thay đổi hình thức", nhieu_ocr: "Nhiễu OCR"};
const KET_LUAN = {khop: "Khớp", khop_co_thay_doi_hinh_thuc: "Khớp – có thay đổi hình thức",
  can_xem: "Cần xem", lech_nghiem_trong: "Lệch nghiêm trọng", chua_doi_chieu_duoc: "Chưa đối chiếu được"};
const LUA_CHON = {loi_ocr: "Lỗi OCR", thay_doi_da_thong_nhat: "Thay đổi đã thống nhất",
  ban_ky_sai: "Bản ký sai", khong_anh_huong: "Không ảnh hưởng"};
const KIEM = {doc_hai_ban: "Đọc hai bản", chuan_hoa: "Chuẩn hóa", can_chinh: "Căn chỉnh",
  so_van_ban: "So văn bản", quy_tac_cung: "Quy tắc bắt buộc", phan_loai_ai: "Phân loại nội dung",
  sua_tay: "Vùng sửa tay", lech_dau: "Lệch dấu", nguon_trang_ocr: "Nguồn trang OCR",
  do_chat_luong_sua_tay: "Chất lượng bộ phát hiện sửa tay", do_chat_luong_ocr: "Chất lượng OCR",
  kiem_trang_vat_ly: "Kiểm trang", quy_tac_vung_bao_ve: "Vùng bảo vệ",
  quy_tac_so_va_ngay: "Số và ngày", quy_tac_tien_bang_chu: "Tiền bằng chữ"};

export function dinhDang(v) {
  if (v === null || v === undefined) return "Chưa đo";
  if (typeof v === "object" && "so" in v && /^[A-Z]{3}$/.test(v.tien_te))
    return `${new Intl.NumberFormat("vi-VN", {maximumFractionDigits: 20}).format(v.so)} ${v.tien_te}`;
  if (typeof v === "string" && /^\d{4}-\d{2}-\d{2}(T.*)?$/.test(v)) {
    if (v.length === 10) return v.slice(8, 10) + "/" + v.slice(5, 7) + "/" + v.slice(0, 4);
    const d = new Date(v);
    if (Number.isFinite(d.getTime())) return new Intl.DateTimeFormat("vi-VN", {
      timeZone: "Asia/Ho_Chi_Minh", day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
    }).format(d);
  }
  return typeof v === "string" || typeof v === "number" ? String(v) : "Chưa có thông tin";
}

export default async function ketQua(goc, KttCore = globalThis.KttCore, luaChon = {}) {
  const api = KttCore.engine("e_doi_chieu"), cua = luaChon.cua, doc = goc.ownerDocument;
  const tao = (the, chu, cha = goc) => {
    const e = doc.createElement(the);
    if (chu !== undefined) e.textContent = chu;
    cha.appendChild(e); return e;
  };
  goc.replaceChildren(); goc.classList.add("dc-ket-qua");
  tao("style").textContent = `.dc-ket-qua{font-family:inherit;color:#243e50;max-width:90rem}
    .dc-ket-qua p{line-height:1.6;max-width:78ch}.dc-ket-qua .dc-diem{border-top:2px solid #b7c9d1;padding:1rem 0 1.5rem}
    .dc-ket-qua .dc-hai-ben{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}
    .dc-ket-qua .dc-hai-ben>section{min-width:0;background:#f3f7fa;padding:1rem}
    .dc-ket-qua .dc-nguyen-van{white-space:pre-wrap;overflow-wrap:anywhere;max-width:78ch}
    .dc-ket-qua mark{background:#fff1b9;color:#243e50}.dc-ket-qua img{max-width:100%;height:auto}
    .dc-ket-qua label{display:block;margin:.7rem 0}.dc-ket-qua textarea{display:block;width:100%;max-width:48rem;min-height:5rem;box-sizing:border-box}
    .dc-ket-qua select,.dc-ket-qua textarea,.dc-ket-qua button{font:inherit;padding:.5rem}
    .dc-ket-qua button{margin:.4rem .6rem .4rem 0;cursor:pointer}.dc-ket-qua :focus-visible{outline:3px solid #006baa;outline-offset:2px}
    .dc-ket-qua [role=alert]{color:#982525}.dc-ket-qua .dc-thieu{border-left:4px solid #ba7620;padding-left:1rem}
    @media(max-width:48rem){.dc-ket-qua .dc-hai-ben{grid-template-columns:1fr}}
    .dc-ket-qua [hidden]{display:none!important}`;
  tao("h2", "Kết quả đối chiếu bản ký");
  const thongBao = tao("p", "Đang đọc kết quả…"); thongBao.setAttribute("role", "status"); thongBao.setAttribute("aria-live", "polite");
  const noiDung = tao("div"), tai = tao("button", "Tải lại kết quả"); tai.type = "button";
  let dangTai = false, view;
  const baoLoi = chu => {thongBao.setAttribute("role", "alert"); thongBao.textContent = chu;};
  async function hienTep(ref, cha, nhan) {
    if (!ref) {tao("p", "Chưa có ảnh đúng vị trí được cấp quyền.", cha); return;}
    const nut = tao("button", nhan, cha); nut.type = "button";
    const vung = tao("div", undefined, cha);
    nut.addEventListener("click", async () => {
      if (nut.disabled) return;
      nut.disabled = true; vung.replaceChildren();
      try {
        if (!cua || typeof cua.hien_tep !== "function") throw Error();
        // Core kiểm quyền và tự dựng phần xem tệp. Không gán src/href từ nội dung.
        await cua.hien_tep(structuredClone(ref), vung);
      } catch {tao("p", "Chưa mở được tệp hoặc quyền xem đã thay đổi. Tải lại kết quả.", vung);}
      finally {nut.disabled = false;}
    });
  }
  function xacNhan(d, cha) {
    const rows = (view.xac_nhan || []).filter(r => r.ma_diem === d.ma_diem);
    if (rows.length) {
      const lichSu = tao("ul", undefined, cha);
      for (const r of rows) tao("li", `${r.ten_nguoi} — ${dinhDang(r.luc)}: ${LUA_CHON[r.lua_chon] || "Cần kiểm tra"}. ${r.noi_dung_dung || r.ly_do || ""}`, lichSu);
    }
    if (!["nghiem_trong", "can_xem"].includes(d.muc)) return;
    if (d.muc === "nghiem_trong") tao("p", "Thay đổi đã thống nhất cần hai người khác nhau, trong đó có người duyệt có thẩm quyền.", cha);
    if (view.quyen?.xac_nhan !== true || !view.quyen.diem_duoc_xac_nhan?.includes(d.ma_diem) || typeof cua?.xac_nhan !== "function") {
      tao("p", "Chỉ có quyền xem. Chưa có cổng xác nhận hoặc chưa được giao quyền xác nhận điểm này.", cha); return;
    }
    const form = tao("form", undefined, cha), nhan = tao("label", "Lựa chọn xác nhận", form);
    const chon = tao("select", undefined, nhan);
    for (const [ma, ten] of Object.entries(LUA_CHON)) {const opt = tao("option", ten, chon); opt.value = ma;}
    chon.value = "loi_ocr";
    const nhanDung = tao("label", "Nội dung đúng (bắt buộc khi thay đổi đã thống nhất)", form), dung = tao("textarea", undefined, nhanDung);
    const nhanLyDo = tao("label", "Lý do (bắt buộc khi không ảnh hưởng)", form), lyDo = tao("textarea", undefined, nhanLyDo);
    dung.maxLength = 4000; lyDo.maxLength = 4000;
    const nut = tao("button", "Lưu xác nhận", form); nut.type = "submit";
    const trangThai = tao("p", "", form); trangThai.setAttribute("role", "status"); trangThai.setAttribute("aria-live", "polite");
    let dangGui = false, choTaiLai = false, yeuCau = null;
    chon.addEventListener("change", () => {dung.required = chon.value === "thay_doi_da_thong_nhat"; lyDo.required = chon.value === "khong_anh_huong";});
    form.addEventListener("submit", async ev => {
      ev.preventDefault();
      if (dangGui || choTaiLai || nut.disabled) return;
      if (!yeuCau) {
        if (!Object.hasOwn(LUA_CHON, chon.value) || !form.reportValidity() ||
            chon.value === "thay_doi_da_thong_nhat" && !dung.value.trim() ||
            chon.value === "khong_anh_huong" && !lyDo.value.trim() || dung.value.length > 4000 || lyDo.value.length > 4000) {
          trangThai.textContent = "Nhập nội dung đúng hoặc lý do bắt buộc trước khi xác nhận."; return;
        }
        yeuCau = {ma_luot: view.ma_luot, row_version: view.row_version, ma_diem: d.ma_diem,
          ma_yeu_cau: globalThis.crypto.randomUUID(), lua_chon: chon.value, noi_dung_dung: dung.value.trim(), ly_do: lyDo.value.trim()};
      }
      dangGui = true; nut.disabled = true; chon.disabled = dung.disabled = lyDo.disabled = true; tai.disabled = true;
      try {
        const ack = await cua.xac_nhan(structuredClone(yeuCau));
        if (ack?.da_luu !== true || ack.ma_yeu_cau !== yeuCau.ma_yeu_cau) throw Error();
        choTaiLai = true; trangThai.textContent = "Đã lưu xác nhận. Tải lại để xem trạng thái mới. Hiệu lực do module quyết định.";
      } catch (loi) {
        trangThai.setAttribute("role", "alert");
        const ma = loi?.ma || loi?.code;
        if (loi?.status === 409 || ["DC_XUNG_DOT", "NGAN_XUNG_DOT", "DC_DA_XAC_NHAN", "DC_TRUNG_YEU_CAU"].includes(ma)) {
          choTaiLai = true; trangThai.textContent = "Kết quả vừa thay đổi. Tải lại trước khi xác nhận.";
        } else if (["DC_KHONG_CO_QUYEN", "DC_CHUA_CO_CONG_XAC_NHAN"].includes(ma)) {
          choTaiLai = true; trangThai.textContent = "Chưa có cổng xác nhận hoặc chưa được giao quyền. Tải lại kết quả.";
        } else {
          trangThai.textContent = "Chưa xác nhận được việc lưu. Gửi lại để kiểm tra cùng yêu cầu.";
        }
      } finally {dangGui = false; nut.disabled = choTaiLai; tai.disabled = false;}
    });
  }
  async function ve() {
    noiDung.replaceChildren();
    const s = view.bao_cao;
    tao("h3", KET_LUAN[s.ket_luan] || "Chưa đối chiếu được", noiDung);
    tao("p", Object.entries(MUC).map(([ma, ten]) => `${ten}: ${dinhDang(s.tom_tat["so_"+ma])}`).join("; ") +
      `; Vùng sửa tay: ${dinhDang(s.tom_tat.so_vung_sua_tay)}; Trang OCR kém: ${dinhDang(s.tom_tat.so_trang_ocr_kem)}.`, noiDung);
    const thieu = s.tong_hop?.phan_chua_kiem || [];
    if (!s.da_kiem_du || thieu.length) {
      const p = tao("div", undefined, noiDung); p.classList.add("dc-thieu");
      tao("h3", "Chưa kiểm đầy đủ — hồ sơ vẫn cần kiểm tra", p);
      const ul = tao("ul", undefined, p);
      for (const k of thieu) tao("li", KIEM[k] || "Một phần kiểm bắt buộc chưa hoàn tất", ul);
    }
    tao("p", view.dieu_kien_module?.du_dieu_kien_de_nghi === true
      ? "Đã đủ điều kiện đề nghị module kiểm tra mở chặn. Hiệu lực chưa được xác nhận tại màn này."
      : "Chưa đủ điều kiện đề nghị mở chặn. Cần hoàn tất kiểm tra và xác nhận hợp lệ; Bản ký sai tiếp tục giữ chặn.", noiDung);
    const boLoc = tao("label", "Lọc mức", noiDung), loc = tao("select", undefined, boLoc);
    for (const [ma, ten] of [["tat_ca", "Tất cả mức đang hiển thị"], ...Object.entries(MUC)]) {
      const opt = tao("option", ten, loc); opt.value = ma;
    }
    loc.value = "tat_ca";
    const nhieu = tao("button", `Xem nhiễu OCR (${s.tom_tat.so_nhieu_ocr ?? 0})`, noiDung); nhieu.type = "button";
    let xemNhieu = false;
    const ds = tao("div", undefined, noiDung), cacKhoi = [];
    const diem = [...s.diem_lech, ...(s.vung_sua_tay || []).map(v => ({...v, ma_diem: v.ma, muc: "nghiem_trong", la_vung: true}))];
    for (const [i, d] of diem.entries()) {
      const khoi = tao("article", undefined, ds); khoi.classList.add("dc-diem");
      tao("h3", `${d.la_vung ? "Vùng sửa tay" : "Điểm khác biệt"} ${i+1}: ${MUC[d.muc] || "Cần kiểm tra"}`, khoi);
      const haiBen = tao("div", undefined, khoi); haiBen.classList.add("dc-hai-ben");
      for (const [ben, ten] of [["word", "Bản Word đã chốt"], ["ban_ky", "Bản ký và chữ OCR"]]) {
        const cot = tao("section", undefined, haiBen); tao("h4", ten, cot);
        const p = tao("p", undefined, cot); p.classList.add("dc-nguyen-van");
        tao("mark", d[ben]?.nguyen_van ?? (d.la_vung ? "Máy chưa đọc chữ tay; xem ảnh để xác nhận." : "Không có đoạn tương ứng."), p);
        const viTri = d[ben]?.vi_tri;
        const viTriChu = [];
        if (viTri?.so_trang || d.la_vung) viTriChu.push(`Trang ${viTri?.so_trang || d.so_trang}`);
        for (const [k, tenViTri] of [["dieu", "Điều"], ["khoan", "Khoản"], ["so_doan", "Đoạn"], ["hang", "Hàng"], ["cot", "Cột"]])
          if (viTri?.[k] !== undefined && viTri[k] !== null) viTriChu.push(`${tenViTri} ${viTri[k]}`);
        if (viTriChu.length) tao("p", viTriChu.join("; "), cot);
        if (ben === "ban_ky") {
          const ref = d.la_vung ? {tep: d.anh_cat, bam: d.bam_anh_cat} :
            (s.lech_dau?.ket_qua || []).find(r => r.ma_diem === d.ma_diem)?.anh_cat;
          const trang = s.anh_trang.find(a => a.so === viTri?.so_trang);
          if (ref) await hienTep(ref, cot, "Xem ảnh vùng");
          else if (trang && viTri?.hop) await hienTep({...trang, hop: viTri.hop, vi_tri: viTri}, cot, "Xem ảnh tại vị trí");
          else await hienTep(null, cot, "Xem ảnh");
        }
      }
      tao("p", d.ly_do_ai || (d.quy_tac_trung?.length ? "Khác biệt thuộc quy tắc bắt buộc." : "Kiểm tra bằng chứng hai phía."), khoi);
      xacNhan(d, khoi); cacKhoi.push([khoi, d.muc]);
    }
    function locLai() {
      for (const [khoi, muc] of cacKhoi) khoi.hidden = (muc === "nhieu_ocr" && !xemNhieu) || (loc.value !== "tat_ca" && loc.value !== muc);
    }
    loc.addEventListener("change", () => {if (loc.value === "nhieu_ocr") xemNhieu = true; locLai();});
    nhieu.addEventListener("click", () => {xemNhieu = !xemNhieu; nhieu.textContent = xemNhieu ? "Ẩn nhiễu OCR" : `Xem nhiễu OCR (${s.tom_tat.so_nhieu_ocr ?? 0})`; locLai();});
    locLai();
    await hienTep({tep: s.bao_cao_pdf.tep, bam: s.bao_cao_pdf.bam}, noiDung, "Xem báo cáo PDF");
    if (view.quyen?.gui_yeu_cau_module === true && typeof cua?.gui_yeu_cau_module === "function") {
      const gui = tao("button", "Gửi yêu cầu module kiểm tra", noiDung); gui.type = "button";
      gui.addEventListener("click", async () => {
        if (gui.disabled) return; gui.disabled = true;
        try {
          const ack = await cua.gui_yeu_cau_module({ma_luot: view.ma_luot});
          if (ack?.da_nhan !== true) throw Error();
          thongBao.textContent = "Module đã nhận yêu cầu kiểm tra. Hiệu lực do module quyết định.";
        } catch {baoLoi("Chưa xác nhận được module nhận yêu cầu. Tải lại để kiểm tra; hiệu lực chưa được cập nhật tại màn này.");}
        finally {gui.disabled = false;}
      });
    }
  }
  async function taiLai() {
    if (dangTai) return; dangTai = true; tai.disabled = true; noiDung.replaceChildren();
    try {
      if (!luaChon.ma_luot || typeof cua?.doc_ket_qua !== "function") throw Error();
      const b = await api.ngan.doc("luot_doi_chieu", {ma_luot: luaChon.ma_luot});
      if (!b) throw Error();
      view = await cua.doc_ket_qua({ma_luot: luaChon.ma_luot, row_version: b.row_version});
      if (view.ma_luot !== luaChon.ma_luot || view.row_version !== b.row_version) throw Error();
      await ve(); thongBao.setAttribute("role", "status"); thongBao.textContent = "Đã đọc kết quả theo quyền Core cấp.";
    } catch {noiDung.replaceChildren(); baoLoi("Chưa đọc được kết quả có quyền từ Core. Tải lại; hiện chưa thể lưu xác nhận.");}
    finally {dangTai = false; tai.disabled = false;}
  }
  tai.addEventListener("click", taiLai);
  await taiLai();
}
