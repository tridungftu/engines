// Màn chỉ đọc. Core phải cấp ngữ cảnh pháp nhân và quyền trước khi nạp.
// Chưa có thao tác quản trị SDK/C-DC-03: không có nút duyệt hoặc ghi ngăn.
export default async function loiOCR(goc, KttCore = globalThis.KttCore, luaChon = {}) {
  const api = KttCore.engine("e_doi_chieu"), doc = goc.ownerDocument;
  const tao = (the, chu, cha = goc) => {
    const e = doc.createElement(the);
    if (chu !== undefined) e.textContent = chu;
    cha.appendChild(e); return e;
  };
  goc.replaceChildren(); goc.classList.add("dc-loi-ocr");
  tao("style").textContent = `.dc-loi-ocr{font-family:inherit;color:#243e50;max-width:75rem}
    .dc-loi-ocr p{line-height:1.6;max-width:78ch}.dc-loi-ocr table{width:100%;border-collapse:collapse}
    .dc-loi-ocr td,.dc-loi-ocr th{text-align:left;border-bottom:1px solid #b7c9d1;padding:.7rem;overflow-wrap:anywhere}
    .dc-loi-ocr button{font:inherit;padding:.55rem;margin:.5rem}.dc-loi-ocr :focus-visible{outline:3px solid #006baa}
    .dc-loi-ocr [role=alert]{color:#982525}.dc-loi-ocr .dc-bang{overflow-x:auto}`;
  tao("h2", "Danh mục lỗi OCR thường gặp");
  tao("p", "Chỉ xem. Đề xuất chưa duyệt không ảnh hưởng kết quả máy. Duyệt cần quản trị viên qua cổng xác nhận của Core và nguồn từ điển đã duyệt.");
  const thongBao = tao("p", ""); thongBao.setAttribute("role", "status"); thongBao.setAttribute("aria-live", "polite");
  const noiDung = tao("div"), tai = tao("button", "Tải lại danh mục"); tai.type = "button";
  const tiep = tao("button", "Xem trang tiếp"); tiep.type = "button"; tiep.hidden = true;
  let dangTai = false, cursor = null;
  const giaiMa = row => {
    const s = row?.gia_tri?.noi_dung ?? row?.noi_dung;
    if (typeof s !== "string") throw Error();
    return JSON.parse(s);
  };
  async function docTrang(taiLai) {
    if (dangTai) return; dangTai = true; tai.disabled = tiep.disabled = true;
    noiDung.replaceChildren(); tiep.hidden = true;
    try {
      // Ngữ cảnh do khung host cấp, không lấy pháp nhân/quyền từ bản ghi.
      if (luaChon.nguCanhDaGan !== true) throw Error();
      const page = await api.ngan.tim("loi_ocr_de_xuat", {gioi_han: 100, tiep: taiLai ? null : cursor});
      if (!Array.isArray(page?.danh_sach)) throw Error();
      const ds = page.danh_sach.map(giaiMa);
      if (!ds.length) tao("p", "Chưa có đề xuất trong pháp nhân đang chọn.", noiDung);
      else {
        const vung = tao("div", undefined, noiDung); vung.classList.add("dc-bang");
        const bang = tao("table", undefined, vung); tao("caption", "Đề xuất thuộc pháp nhân đang chọn", bang);
        const dau = tao("tr", undefined, tao("thead", undefined, bang));
        for (const ten of ["Chữ OCR", "Chữ đúng", "Số lần có căn cứ", "Trạng thái"]) tao("th", ten, dau).setAttribute("scope", "col");
        const than = tao("tbody", undefined, bang);
        for (const r of ds) {
          const hang = tao("tr", undefined, than);
          for (const v of [r.ocr, r.word, Array.isArray(r.lan_gap) ? r.lan_gap.length : "Chưa đủ căn cứ",
            {cho_nguong: "Chưa đạt ngưỡng đã duyệt", cho_duyet: "Chờ quản trị viên duyệt", da_duyet: "Đã duyệt cho bộ phiên bản mới"}[r.trang_thai] || "Cần kiểm tra"])
            tao("td", typeof v === "string" || typeof v === "number" ? String(v) : "Chưa đủ căn cứ", hang);
        }
      }
      cursor = page.tiep ?? null; tiep.hidden = cursor === null;
      thongBao.setAttribute("role", "status"); thongBao.textContent = "Đã đọc danh mục. Hồ sơ cũ giữ nguyên bộ đã ghim.";
    } catch {
      noiDung.replaceChildren(); cursor = null;
      thongBao.setAttribute("role", "alert");
      thongBao.textContent = "Chưa đọc được danh mục có quyền. Chọn pháp nhân trong Core và tải lại.";
    } finally {dangTai = false; tai.disabled = tiep.disabled = false;}
  }
  tai.addEventListener("click", () => docTrang(true));
  tiep.addEventListener("click", () => docTrang(false));
  await docTrang(true);
}
