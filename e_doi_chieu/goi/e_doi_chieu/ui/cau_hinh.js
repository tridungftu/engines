// Màn do Core nạp. Cấu hình/bản CAS qua SDK; không đọc schema bằng mạng.
export const TRUONG_SO = [
  ["so_trang_toi_da", "Số trang bản ký tối đa", 60, 60, "trang"],
  ["ky_tu_moi_tai_lieu", "Độ dài mỗi tài liệu", 500000, 500000, "ký tự"],
  ["ky_tu_hai_tai_lieu", "Độ dài hai tài liệu", 1000000, 1000000, "ký tự"],
  ["diem_lech_toi_da", "Số điểm lệch tối đa", 10000, 10000, "điểm"],
  ["ho_so_mib", "Dung lượng hồ sơ", 20, 20, "MiB"],
  ["tep_mib", "Dung lượng mỗi tệp", 20, 20, "MiB"],
  ["pixel_anh", "Kích thước mỗi ảnh", 20000000, 20000000, "pixel"],
  ["tong_byte_tep_con", "Tổng dữ liệu đọc mỗi việc", 134217728, 134217728, "byte"],
  ["docx_giai_nen_mib", "Dung lượng Word sau giải nén", 100, 100, "MiB"],
  ["docx_so_muc", "Số phần trong tệp Word", 2000, 2000, "phần"],
  ["thoi_han_chiem_luot_giay", "Thời hạn giữ lượt (để trống dùng thời hạn bước cộng 60 giây)", null, null, "giây"],
];
const BO_GHIM = ["phien_ban_cau_hinh", "ma_bo_chuan_hoa", "bam_bo_chuan_hoa", "ma_tu_dien",
  "bam_tu_dien", "phuong_phap_detector", "phien_ban_detector"];

export default async function cauHinh(goc, KttCore = globalThis.KttCore) {
  const api = KttCore.engine("e_doi_chieu"), doc = goc.ownerDocument;
  const tao = (the, chu, cha = goc) => {
    const e = doc.createElement(the);
    if (chu !== undefined) e.textContent = chu;
    cha.appendChild(e); return e;
  };
  goc.replaceChildren(); goc.classList.add("dc-cau-hinh");
  tao("style").textContent = `.dc-cau-hinh{font-family:inherit;color:#243e50;max-width:70rem}
    .dc-cau-hinh p{max-width:75ch;line-height:1.6}.dc-cau-hinh fieldset{border:1px solid #b7c9d1;padding:1rem;margin:1rem 0}
    .dc-cau-hinh .dc-tran{display:grid;grid-template-columns:repeat(auto-fit,minmax(17rem,1fr));gap:1rem}
    .dc-cau-hinh label{display:flex;flex-direction:column;gap:.4rem}.dc-cau-hinh input{font:inherit;padding:.5rem;max-width:100%;box-sizing:border-box}
    .dc-cau-hinh button{font:inherit;padding:.55rem .9rem;margin:.4rem .6rem .4rem 0;cursor:pointer}
    .dc-cau-hinh :focus-visible{outline:3px solid #006baa;outline-offset:2px}.dc-cau-hinh [role=alert]{color:#982525}`;
  tao("h2", "Cấu hình đối chiếu bản ký");
  tao("p", "Giới hạn áp dụng cho việc mới. Hồ sơ cũ giữ bộ quy tắc đã ghim; ngưỡng chưa đo vẫn cần kiểm tra.");
  const form = tao("form"), bo = tao("fieldset", undefined, form);
  tao("legend", "Bộ kiểm đã duyệt", bo);
  const tinhTrang = tao("p", "Đang đọc cấu hình…", bo);
  tao("p", "Ngưỡng trang OCR kém: chưa đo. Chưa đủ căn cứ để kết luận sạch.", bo);
  const tran = tao("fieldset", undefined, form);
  tao("legend", "Giới hạn xử lý", tran);
  const grid = tao("div", undefined, tran); grid.classList.add("dc-tran");
  const o = new Map();
  for (const [ma, ten, max, , donVi] of TRUONG_SO) {
    const label = tao("label", `${ten} (${donVi})`, grid), input = tao("input", undefined, label);
    input.type = "number"; input.min = "1"; input.step = "1";
    if (max !== null) {input.max = String(max); input.required = true;}
    o.set(ma, input);
  }
  const luu = tao("button", "Lưu cấu hình", form); luu.type = "submit"; luu.disabled = true;
  const tai = tao("button", "Tải lại cấu hình", form); tai.type = "button";
  const thongBao = tao("p", "", form); thongBao.setAttribute("role", "status"); thongBao.setAttribute("aria-live", "polite");
  let banChup = {}, phienBan = null, dangLuu = false, canTaiLai = true;
  const coBo = ch => BO_GHIM.every(k => typeof ch[k] === "string" && ch[k].trim());
  async function docLai() {
    if (dangLuu) return;
    luu.disabled = true; tai.disabled = true; canTaiLai = true;
    try {
      const kq = await api.cau_hinh.doc();
      if (kq.phien_ban_cau_hinh === undefined || kq.phien_ban_cau_hinh === null) throw Error();
      banChup = structuredClone(kq.cau_hinh || {}); phienBan = kq.phien_ban_cau_hinh;
      for (const [ma, , , macDinh] of TRUONG_SO) o.get(ma).value = String(banChup[ma] ?? macDinh ?? "");
      tinhTrang.textContent = coBo(banChup)
        ? "Đã ghim bộ chuẩn hóa, từ điển và bộ phát hiện. Chi tiết phiên bản nằm trong thông tin engine."
        : "Chưa đủ bộ kiểm đã duyệt. Anh nhờ quản trị viên cấp bộ chuẩn hóa, từ điển và bộ phát hiện trước khi lưu.";
      canTaiLai = !coBo(banChup); luu.disabled = canTaiLai;
      thongBao.textContent = "";
    } catch {
      thongBao.setAttribute("role", "alert");
      thongBao.textContent = "Chưa đọc được cấu hình. Anh tải lại trước khi lưu.";
    } finally {tai.disabled = false;}
  }
  tai.addEventListener("click", docLai);
  form.addEventListener("submit", async ev => {
    ev.preventDefault();
    if (dangLuu || canTaiLai || luu.disabled || !form.reportValidity()) return;
    // Chỉ gửi các thuộc tính schema đã khai, giữ nguyên bộ đã duyệt.
    const giaTri = Object.fromEntries(BO_GHIM.map(k => [k, banChup[k]]));
    // Ngưỡng học chỉ do Core cấp sau đo/duyệt; form giới hạn giữ nguyên.
    if (Object.hasOwn(banChup, "hoc_loi_ocr")) giaTri.hoc_loi_ocr = structuredClone(banChup.hoc_loi_ocr);
    giaTri.nguong_ocr_kem = null;
    for (const [ma, , max] of TRUONG_SO) {
      const text = o.get(ma).value.trim();
      if (!text && max === null) continue;
      const n = Number(text);
      if (!Number.isSafeInteger(n) || n < 1 || max !== null && n > max) {
        thongBao.setAttribute("role", "alert"); thongBao.textContent = "Anh nhập giới hạn là số nguyên dương trong khoảng cho phép."; return;
      }
      giaTri[ma] = n;
    }
    dangLuu = true; luu.disabled = true; tai.disabled = true;
    try {
      const kq = await api.cau_hinh.luu(giaTri, phienBan);
      if (kq.phien_ban_cau_hinh === undefined || kq.phien_ban_cau_hinh === null) {canTaiLai = true; throw Error();}
      phienBan = kq.phien_ban_cau_hinh; banChup = structuredClone(giaTri);
      thongBao.setAttribute("role", "status"); thongBao.textContent = "Đã lưu cấu hình cho việc mới.";
    } catch (loi) {
      const xungDot = loi.status === 409 || [loi.ma, loi.code].some(v => ["NGAN_XUNG_DOT", "CAU_HINH_XUNG_DOT"].includes(v));
      canTaiLai = true;
      thongBao.setAttribute("role", "alert");
      thongBao.textContent = xungDot ? "Cấu hình đã được người khác thay đổi. Anh tải lại trước khi lưu."
        : "Chưa xác nhận được việc lưu cấu hình. Anh tải lại trước khi lưu tiếp.";
    } finally {dangLuu = false; luu.disabled = canTaiLai; tai.disabled = false;}
  });
  await docLai();
}
