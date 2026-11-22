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
  ["thoi_han_chiem_luot_giay", "Thời hạn giữ lượt", null, null, "giây"],
];
const BO_GHIM = ["phien_ban_cau_hinh", "ma_bo_chuan_hoa", "bam_bo_chuan_hoa", "ma_tu_dien",
  "bam_tu_dien", "phuong_phap_detector", "phien_ban_detector"];
const TEN_BO = ["Phiên bản cấu hình", "Bộ chuẩn hóa", "Băm bộ chuẩn hóa", "Từ điển đã duyệt",
  "Băm từ điển", "Phương pháp phát hiện sửa tay", "Phiên bản bộ phát hiện"];
const HUONG_DAN = [
  "Áp dụng cho bản ký; vượt trần thì từ chối, không bỏ trang.",
  "Đếm riêng từng bản Word và bản ký; không cắt bớt nội dung.",
  "Tổng số ký tự của cả bản Word và bản ký.",
  "Vượt trần thì từ chối; không lược bỏ điểm khác biệt.",
  "Giới hạn dung lượng một hồ sơ JSON.", "Giới hạn cho từng tệp gốc hoặc ảnh.",
  "Chiều rộng nhân chiều cao của một ảnh.", "Tổng số byte tệp con được đọc trong một việc.",
  "Tổng dung lượng các phần trong tệp Word sau giải nén.", "Số mục trong gói Word.",
  "Không bắt buộc. Để trống dùng thời hạn bước nhận cặp cộng 60 giây; ví dụ 180 giây.",
];
const so = n => new Intl.NumberFormat("vi-VN").format(n);

export default async function cauHinh(goc, KttCore = globalThis.KttCore) {
  const api = KttCore.engine("e_doi_chieu"), doc = goc.ownerDocument;
  const tao = (the, chu, cha = goc) => {
    const e = doc.createElement(the);
    if (chu !== undefined) e.textContent = chu;
    cha.appendChild(e); return e;
  };
  goc.replaceChildren(); goc.classList.add("dc-cau-hinh");
  tao("style").textContent = `.dc-cau-hinh{font-family:inherit;color:#203b55;max-width:70rem}
    .dc-cau-hinh *{box-sizing:border-box}.dc-cau-hinh p{line-height:1.6;margin:.6rem 0 1.2rem;max-width:78ch}
    .dc-cau-hinh .dc-the{background:#fff;border:1px solid #d7e1ed;border-radius:12px;margin:1rem 0;overflow:hidden}
    .dc-cau-hinh .dc-dau{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1.5rem 2rem;border-bottom:1px solid #d7e1ed}
    .dc-cau-hinh h2{font-size:1.35rem;margin:0}.dc-cau-hinh h3{font-size:1.1rem;margin:0 0 1rem}
    .dc-cau-hinh .dc-noi-dung{padding:1.5rem 2rem}.dc-cau-hinh .dc-tran{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}
    .dc-cau-hinh label{display:block;margin-bottom:.6rem}.dc-cau-hinh input{font:inherit;color:inherit;background:#fff;border:1px solid #cbd9e8;border-radius:7px;padding:.85rem 1rem;width:100%;min-width:0}
    .dc-cau-hinh small{display:block;color:#61758b;line-height:1.5;margin-top:.6rem}
    .dc-cau-hinh .dc-loi{color:#a02626;min-height:1.4em}.dc-cau-hinh input[aria-invalid=true]{border-color:#a02626}
    .dc-cau-hinh button{font:inherit;border:1px solid #cbd9e8;border-radius:7px;background:#fff;color:#203b55;padding:.8rem 1.1rem;margin:0 .7rem .5rem 0;cursor:pointer}
    .dc-cau-hinh button[type=submit]{background:#203b55;color:#fff;border-color:#203b55}
    .dc-cau-hinh button:disabled{opacity:.55;cursor:default}.dc-cau-hinh :focus-visible{outline:3px solid #006baa;outline-offset:3px}
    .dc-cau-hinh .dc-nhan{font-size:.9rem;padding:.45rem .65rem;background:#edf7f0;color:#176b57;border:1px solid #d5eadd;border-radius:6px}
    .dc-cau-hinh .dc-canh-bao{padding:1rem 1.2rem;background:#fff7e6;border:1px solid #f1d59c;border-radius:7px;color:#875700}
    .dc-cau-hinh summary{padding:1.4rem 2rem;cursor:pointer;font-weight:600}.dc-cau-hinh details[open]>summary{border-bottom:1px solid #d7e1ed}
    .dc-cau-hinh dl{display:grid;grid-template-columns:minmax(10rem,1fr) 2fr;gap:.8rem 1.2rem;margin:0 0 1.8rem}
    .dc-cau-hinh dt{color:#61758b}.dc-cau-hinh dd{margin:0;overflow-wrap:anywhere}.dc-cau-hinh [role=alert]{color:#a02626}
    @media(max-width:42rem){.dc-cau-hinh .dc-tran,.dc-cau-hinh dl{grid-template-columns:1fr}.dc-cau-hinh .dc-dau{align-items:flex-start;flex-direction:column}.dc-cau-hinh .dc-dau,.dc-cau-hinh .dc-noi-dung,.dc-cau-hinh summary{padding:1.2rem}}`;
  const form = tao("form"); form.noValidate = true;
  const the = tao("section", undefined, form); the.classList.add("dc-the");
  const dau = tao("header", undefined, the); dau.classList.add("dc-dau");
  tao("h2", "⚖ Cấu hình đối chiếu bản ký", dau);
  const tinhTrang = tao("span", "Đang đọc cấu hình…", dau); tinhTrang.classList.add("dc-nhan");
  const coBan = tao("div", undefined, the); coBan.classList.add("dc-noi-dung");
  tao("h3", "Cơ bản", coBan);
  tao("p", "Giới hạn áp dụng cho việc mới. Hồ sơ cũ giữ bộ quy tắc đã ghim. Vượt giới hạn thì từ chối xử lý, không cắt bớt dữ liệu.", coBan);
  const grid = tao("div", undefined, coBan); grid.classList.add("dc-tran");
  const nangCao = tao("details", undefined, form); nangCao.classList.add("dc-the");
  tao("summary", "Nâng cao · Bộ kiểm và giới hạn kỹ thuật", nangCao);
  const chiTiet = tao("div", undefined, nangCao); chiTiet.classList.add("dc-noi-dung");
  tao("h3", "Bộ kiểm đã duyệt · Chỉ đọc", chiTiet);
  tao("p", "Mã, băm và bộ phát hiện do Core cấp theo bộ đã duyệt. Màn này chỉ điều chỉnh giới hạn xử lý.", chiTiet);
  const bo = tao("dl", undefined, chiTiet), thongTin = new Map();
  for (const [i, ma] of BO_GHIM.entries()) {tao("dt", TEN_BO[i], bo); thongTin.set(ma, tao("dd", "Chưa được cấp", bo));}
  tao("dt", "Ngưỡng trang OCR kém", bo); tao("dd", "Chưa đo · Chưa đủ căn cứ để kết luận sạch", bo);
  tao("dt", "Học lỗi OCR đã duyệt", bo); const hocOCR = tao("dd", "Chưa được cấp; không tự học hoặc duyệt", bo);
  tao("h3", "Giới hạn kỹ thuật", chiTiet);
  const gridKyThuat = tao("div", undefined, chiTiet); gridKyThuat.classList.add("dc-tran");
  const o = new Map(), loiO = new Map();
  for (const [i, [ma, ten, max, macDinh, donVi]] of TRUONG_SO.entries()) {
    const vung = tao("div", undefined, i < 4 ? grid : gridKyThuat);
    const label = tao("label", `${ten} (${donVi})`, vung), input = tao("input", undefined, label);
    input.type = "number"; input.min = "1"; input.step = "1"; input.disabled = true; input.setAttribute("name", ma);
    if (max !== null) {input.max = String(max); input.required = true; input.placeholder = String(macDinh);}
    else input.placeholder = "Ví dụ: 180";
    const help = tao("small", HUONG_DAN[i] + (max === null ? "" : ` Nhập số nguyên từ 1 đến ${so(max)}; ví dụ ${so(macDinh)} ${donVi}.`), vung);
    help.setAttribute("id", `dc-huong-dan-${ma}`);
    const err = tao("small", "", vung); err.classList.add("dc-loi"); err.setAttribute("id", `dc-loi-${ma}`); err.setAttribute("aria-live", "polite");
    input.setAttribute("aria-describedby", `dc-huong-dan-${ma} dc-loi-${ma}`);
    input.addEventListener("input", () => {kiemO(ma); if (!canTaiLai) tinhTrang.textContent = "Có thay đổi chưa lưu";});
    o.set(ma, input); loiO.set(ma, err);
  }
  const canhBao = tao("p", "Ngưỡng OCR kém và độ chính xác phát hiện sửa tay cần đo trước khi kết luận sạch. Lưu cấu hình không xác nhận kết quả đối chiếu.", form);
  canhBao.classList.add("dc-canh-bao");
  const luu = tao("button", "Lưu cấu hình", form); luu.type = "submit"; luu.disabled = true;
  const tai = tao("button", "Tải lại cấu hình", form); tai.type = "button";
  const thongBao = tao("p", "", form); thongBao.setAttribute("role", "status"); thongBao.setAttribute("aria-live", "polite");
  let banChup = {}, phienBan = null, dangLuu = false, dangDoc = false, canTaiLai = true;
  const coBo = ch => BO_GHIM.every(k => typeof ch[k] === "string" && ch[k].trim());
  const khoaO = khoa => {for (const input of o.values()) input.disabled = khoa;};
  function kiemO(ma) {
    const [, ten, max] = TRUONG_SO.find(t => t[0] === ma), text = o.get(ma).value.trim(), n = Number(text);
    const dat = (!text && max === null) || (text !== "" && Number.isSafeInteger(n) && n >= 1 && (max === null || n <= max));
    loiO.get(ma).textContent = dat ? "" : `${ten}: nhập số nguyên từ 1${max === null ? "" : ` đến ${so(max)}`}${max === null ? ", hoặc để trống" : ""}.`;
    o.get(ma).setAttribute("aria-invalid", String(!dat)); return dat;
  }
  async function docLai() {
    if (dangLuu || dangDoc) return;
    dangDoc = true; luu.disabled = true; tai.disabled = true; canTaiLai = true; khoaO(true);
    tinhTrang.textContent = "Đang đọc cấu hình…";
    try {
      const kq = await api.cau_hinh.doc();
      if (kq?.phien_ban_cau_hinh === undefined || kq.phien_ban_cau_hinh === null) throw Error();
      banChup = structuredClone(kq.cau_hinh || {}); phienBan = kq.phien_ban_cau_hinh;
      for (const [ma, , , macDinh] of TRUONG_SO) {o.get(ma).value = String(banChup[ma] ?? macDinh ?? ""); loiO.get(ma).textContent = ""; o.get(ma).setAttribute("aria-invalid", "false");}
      for (const ma of BO_GHIM) thongTin.get(ma).textContent = typeof banChup[ma] === "string" ? banChup[ma] : "Chưa được cấp";
      const hoc = banChup.hoc_loi_ocr;
      hocOCR.textContent = hoc ? `Ngưỡng: ${hoc.so_lan} lần; phiên bản: ${hoc.phien_ban}; nguồn đo: ${hoc.nguon_do}; mã phê duyệt: ${hoc.ma_phe_duyet}` : "Chưa được cấp; không tự học hoặc duyệt";
      tinhTrang.textContent = coBo(banChup) ? "✓ Đã đọc cấu hình" : "Chưa đủ bộ kiểm";
      canTaiLai = !coBo(banChup); luu.disabled = canTaiLai; khoaO(canTaiLai);
      thongBao.setAttribute("role", canTaiLai ? "alert" : "status");
      thongBao.textContent = canTaiLai ? "Chưa đủ bộ kiểm đã duyệt. Cần quản trị viên cấp bộ chuẩn hóa, từ điển và bộ phát hiện, rồi tải lại trước khi lưu." : "";
    } catch {
      tinhTrang.textContent = "Chưa đọc được";
      thongBao.setAttribute("role", "alert");
      thongBao.textContent = "Chưa đọc được cấu hình. Tải lại trước khi lưu.";
    } finally {dangDoc = false; tai.disabled = false;}
  }
  tai.addEventListener("click", docLai);
  form.addEventListener("submit", async ev => {
    ev.preventDefault();
    if (dangLuu || dangDoc || canTaiLai || luu.disabled) return;
    const sai = TRUONG_SO.filter(([ma]) => !kiemO(ma));
    if (sai.length) {
      if (TRUONG_SO.indexOf(sai[0]) >= 4) nangCao.open = true;
      o.get(sai[0][0]).focus?.(); thongBao.setAttribute("role", "alert"); thongBao.textContent = "Chưa lưu. Sửa các ô có thông báo lỗi."; return;
    }
    // Chỉ gửi các thuộc tính schema đã khai, giữ nguyên bộ đã duyệt.
    const giaTri = Object.fromEntries(BO_GHIM.map(k => [k, banChup[k]]));
    // Ngưỡng học chỉ do Core cấp sau đo/duyệt; form giới hạn giữ nguyên.
    if (Object.hasOwn(banChup, "hoc_loi_ocr")) giaTri.hoc_loi_ocr = structuredClone(banChup.hoc_loi_ocr);
    giaTri.nguong_ocr_kem = null;
    for (const [ma, , max] of TRUONG_SO) {
      const text = o.get(ma).value.trim();
      if (!text && max === null) continue;
      giaTri[ma] = Number(text);
    }
    dangLuu = true; luu.disabled = true; tai.disabled = true; khoaO(true); tinhTrang.textContent = "Đang lưu…";
    try {
      const kq = await api.cau_hinh.luu(giaTri, phienBan);
      if (kq?.phien_ban_cau_hinh === undefined || kq.phien_ban_cau_hinh === null) {canTaiLai = true; throw Error();}
      phienBan = kq.phien_ban_cau_hinh; banChup = structuredClone(giaTri);
      tinhTrang.textContent = "✓ Đã lưu cấu hình";
      thongBao.setAttribute("role", "status"); thongBao.textContent = "Đã lưu cấu hình cho việc mới.";
    } catch (loi) {
      const xungDot = loi?.status === 409 || [loi?.ma, loi?.code].some(v => ["NGAN_XUNG_DOT", "CAU_HINH_XUNG_DOT"].includes(v));
      canTaiLai = true; tinhTrang.textContent = "Cần tải lại";
      thongBao.setAttribute("role", "alert");
      thongBao.textContent = xungDot ? "Cấu hình đã được người khác sửa, tải lại trước khi lưu."
        : "Chưa xác nhận được việc lưu cấu hình. Tải lại trước khi lưu tiếp.";
    } finally {dangLuu = false; luu.disabled = canTaiLai; tai.disabled = false; khoaO(canTaiLai);}
  });
  await docLai();
}
