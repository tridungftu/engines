// Màn module; schema và quyền/CAS vẫn phải được Core kiểm lại.
export const catDoan = {
  do_dai_muc_tieu: ["Mục tiêu ký tự mỗi đoạn", 200, 8000, 2000],
  ky_tu_don_vi_toi_da: ["Trần ký tự mỗi đơn vị", 200, 8000, 8000],
  so_doan_toi_da: ["Trần số đoạn", 1, 5000, 5000],
};
export const nganSach = {
  json_chinh_toi_da_byte: ["Trần byte yêu cầu JSON", 1, 1048576, 1048576],
  tep_toi_da_byte: ["Trần byte mỗi tệp", 1, 20971520, 20971520],
  tong_doc_toi_da_byte: ["Trần tổng byte đọc", 1, 67108864, 67108864],
  van_ban_toi_da_ky_tu: ["Trần ký tự văn bản", 1, 500000, 500000],
  so_trang_toi_da: ["Trần số trang", 1, 60, 60],
  cau_hoi_toi_da_ky_tu: ["Trần ký tự câu hỏi", 1, 4000, 4000],
  so_ham_toi_da: ["Trần số hàm", 1, 100, 100],
  so_muc_danh_muc_toi_da: ["Trần số mục danh mục", 1, 1000, 1000],
  so_ung_vien_toi_da: ["Trần số ứng viên", 1, 50, 50],
  ai_toi_da_ky_tu: ["Trần ký tự ngữ cảnh AI", 1, 100000, 100000],
  khuon_toi_da_byte: ["Trần byte khuôn AI", 1, 32768, 32768],
  chuyen_tiep_toi_da_byte: ["Trần byte chuyển tiếp", 1, 65536, 65536],
  ho_so_toi_da_byte: ["Trần byte phong bì hồ sơ", 1, 65536, 65536],
};
const laObject = v => v !== null && typeof v === "object" && !Array.isArray(v);
const dungKhoa = (v, keys) => laObject(v) && Object.keys(v).every(k => keys.includes(k));
const bam = v => typeof v === "string" && /^sha256:[0-9a-f]{64}$/.test(v);
const loiCauHinh = () => { throw new Error("Cấu hình không hợp lệ. Kiểm tra lại các giá trị."); };

export function kiemCauHinh(v) {
  if (!dungKhoa(v, ["phien_ban", "quy_tac_nhom", "phan_loai", "cat_doan", "ngan_sach"])
      || v.phien_ban !== 1 || !dungKhoa(v.quy_tac_nhom, ["tep_id", "bam"])
      || typeof v.quy_tac_nhom.tep_id !== "string" || !/^[^\s/\\:]{1,200}$/.test(v.quy_tac_nhom.tep_id)
      || !bam(v.quy_tac_nhom.bam)) loiCauHinh();
  const c = structuredClone(v);
  if (c.phan_loai === undefined) c.phan_loai = {};
  if (!dungKhoa(c.phan_loai, ["trang_thai", "nguong", "bam_bo_do"])) loiCauHinh();
  if (c.phan_loai.trang_thai === undefined) c.phan_loai.trang_thai = "chua_do";
  const p = c.phan_loai;
  if (p.trang_thai === "da_do") {
    if (typeof p.nguong !== "number" || !Number.isFinite(p.nguong) || p.nguong < 0 || p.nguong > 1
        || !bam(p.bam_bo_do)) loiCauHinh();
  } else if (p.trang_thai !== "chua_do" || "nguong" in p || "bam_bo_do" in p) loiCauHinh();
  for (const [nhom, cacTruong] of [["cat_doan", catDoan], ["ngan_sach", nganSach]]) {
    if (c[nhom] === undefined) c[nhom] = {};
    if (!dungKhoa(c[nhom], Object.keys(cacTruong))) loiCauHinh();
    for (const [ma, [, min, max, md]] of Object.entries(cacTruong)) {
      if (c[nhom][ma] === undefined) c[nhom][ma] = md;
      if (!Number.isInteger(c[nhom][ma]) || c[nhom][ma] < min || c[nhom][ma] > max) loiCauHinh();
    }
  }
  if (c.cat_doan.do_dai_muc_tieu > c.cat_doan.ky_tu_don_vi_toi_da) loiCauHinh();
  return c;
}

export async function mount(goc, {KttCore = globalThis.KttCore} = {}) {
  const cong = KttCore.engine("e_tra_cuu");
  const doc = goc.ownerDocument;
  let phien = null, phanLoai = {trang_thai: "chua_do"}, daDong = false, dangLuu = false, luot = 0;
  const o = {}, loiO = {};
  function tao(tag, text, cha = goc) {
    const n = doc.createElement(tag);
    if (text !== undefined) n.textContent = text;
    cha.appendChild(n);
    return n;
  }
  goc.replaceChildren();
  goc.className = "ktt-tra-cuu";
  tao("style", `
    .ktt-tra-cuu {font:16px/1.5 "Segoe UI",Arial,sans-serif;color:#213951;max-width:1040px;margin:auto}
    .ktt-tra-cuu * {box-sizing:border-box}
    .ktt-tra-cuu .tc-the {border:1px solid #d9e2ed;border-radius:12px;background:#fff;margin:20px 0;padding:26px 30px}
    .ktt-tra-cuu .tc-dau {display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
    .ktt-tra-cuu h2,.ktt-tra-cuu h3 {margin:0;font-weight:600}
    .ktt-tra-cuu h2 {font-size:24px}.ktt-tra-cuu h3,.ktt-tra-cuu summary {font-size:20px}
    .ktt-tra-cuu .tc-nhan {padding:6px 12px;border:1px solid #d9e2ed;border-radius:6px;font-size:14px;background:#f4f7fa}
    .ktt-tra-cuu p {margin:8px 0 20px;color:#65778b}
    .ktt-tra-cuu .tc-canh-bao {border:1px solid #f0d49a;background:#fff8e8;color:#92600c;padding:16px 20px;border-radius:8px}
    .ktt-tra-cuu .tc-luoi {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px 28px;margin-top:24px}
    .ktt-tra-cuu label {display:block;font-weight:600}
    .ktt-tra-cuu input {display:block;width:100%;font:inherit;color:inherit;background:#fff;border:1px solid #cbd8e7;border-radius:7px;padding:12px 14px;margin:8px 0}
    .ktt-tra-cuu input[readonly] {background:#f4f7fa}
    .ktt-tra-cuu input[aria-invalid="true"] {border-color:#b42318}
    .ktt-tra-cuu small {display:block;font-size:14px;color:#65778b;overflow-wrap:anywhere}
    .ktt-tra-cuu .tc-loi {color:#b42318;font-size:14px;margin:6px 0 0;min-height:0}
    .ktt-tra-cuu button {font:inherit;border:1px solid #cbd8e7;border-radius:7px;padding:11px 20px;background:#fff;color:#213951;cursor:pointer}
    .ktt-tra-cuu button[type="submit"] {background:#213951;color:white;border-color:#213951}
    .ktt-tra-cuu button:disabled {opacity:.55;cursor:default}
    .ktt-tra-cuu .tc-hanh-dong {display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}
    .ktt-tra-cuu :focus-visible {outline:3px solid #3879b5;outline-offset:3px}
    .ktt-tra-cuu summary {cursor:pointer;font-weight:600}
    .ktt-tra-cuu details h3 {font-size:18px;margin-top:28px}
    @media(max-width:640px) {.ktt-tra-cuu .tc-luoi {grid-template-columns:1fr}.ktt-tra-cuu .tc-the {padding:20px}.ktt-tra-cuu h2 {font-size:21px}}
  `);
  const dau = tao("header", undefined, tao("section", undefined)); dau.className = "tc-dau";
  tao("h2", "⌕ Tra cứu tài liệu", dau);
  const nhanTrangThai = tao("span", "Đang đọc", dau); nhanTrangThai.className = "tc-nhan";
  tao("p", "Điều chỉnh cách phân loại và chia đoạn tài liệu. Cấu hình được lưu tại Core.");
  const thongBao = tao("p", "Đang đọc cấu hình…");
  thongBao.setAttribute("role", "status");
  const form = tao("form");
  form.noValidate = true;
  function truong(ma, nhan, cha, gioiHan, huongDan, mau) {
    const hang = tao("div", undefined, cha);
    const label = tao("label", nhan, hang);
    const input = tao("input", undefined, hang);
    input.name = ma;
    input.id = `tc-${ma}`; label.setAttribute("for", input.id);
    input.type = gioiHan ? "number" : "text";
    input.required = true;
    input.placeholder = mau;
    if (gioiHan) {
      input.min = String(gioiHan[0]); input.max = String(gioiHan[1]); input.step = "1";
    } else input.maxLength = ma === "bam" ? 71 : 200;
    const goiY = tao("small", `${huongDan} Ví dụ: ${mau}.`, hang); goiY.id = `${input.id}-goi-y`;
    const loi = tao("p", "", hang); loi.className = "tc-loi"; loi.id = `${input.id}-loi`;
    loi.setAttribute("aria-live", "polite"); input.setAttribute("aria-describedby", `${goiY.id} ${loi.id}`);
    loiO[ma] = loi;
    input.addEventListener("input", kiemNhap);
    o[ma] = input;
  }
  const coBan = tao("section", undefined, form); coBan.className = "tc-the";
  const dauCoBan = tao("div", undefined, coBan); dauCoBan.className = "tc-dau";
  tao("h3", "⚙ Cơ bản", dauCoBan);
  const trangThaiDo = tao("span", "Chưa đo", dauCoBan); trangThaiDo.className = "tc-nhan";
  tao("p", "Ngưỡng phân loại và độ dài mục tiêu của mỗi đoạn văn bản.", coBan);
  const luoiCoBan = tao("div", undefined, coBan); luoiCoBan.className = "tc-luoi";
  const nhomNguong = tao("div", undefined, luoiCoBan);
  const nhanNguong = tao("label", "Ngưỡng phân loại", nhomNguong); nhanNguong.setAttribute("for", "tc-nguong");
  const nguong = tao("input", undefined, nhomNguong); nguong.id = "tc-nguong"; nguong.readOnly = true;
  const goiYNguong = tao("small", "Chỉ đọc. Chỉ dùng ngưỡng đã đo và được duyệt; không đặt giá trị mặc định. Ví dụ sau đo: 91%.", nhomNguong);
  goiYNguong.id = "tc-nguong-goi-y"; nguong.setAttribute("aria-describedby", goiYNguong.id);
  truong("cat_doan.do_dai_muc_tieu", "Độ dài mục tiêu mỗi đoạn (ký tự)", luoiCoBan, [200, 8000], "Từ 200 đến 8.000 ký tự; không vượt trần mỗi đơn vị trong Nâng cao.", "2000");
  const canhBao = tao("p", "Chưa đo ngưỡng phân loại. Màn này không kích hoạt ngưỡng; cần kết quả đo và phê duyệt trước khi áp dụng.", coBan);
  canhBao.className = "tc-canh-bao";
  const nangCao = tao("details", undefined, form); nangCao.className = "tc-the";
  tao("summary", "Nâng cao · Giới hạn xử lý và bộ quy tắc", nangCao);
  tao("p", "Giữ giới hạn mặc định nếu chưa có số đo phù hợp. Vượt giới hạn sẽ bị từ chối, không cắt ngầm dữ liệu.", nangCao);
  const quyTac = tao("section", undefined, nangCao);
  tao("h3", "Bộ quy tắc nhóm", quyTac);
  const luoiQuyTac = tao("div", undefined, quyTac); luoiQuyTac.className = "tc-luoi";
  truong("tep_id", "Tham chiếu bộ quy tắc tại Core", luoiQuyTac, null, "Mã tệp do Core cấp, 1–200 ký tự; không nhập đường dẫn hoặc khoảng trắng.", "tep-quy-tac-DEMO");
  truong("bam", "Băm xác nhận bộ quy tắc", luoiQuyTac, null, "Dùng sha256: theo sau bởi 64 ký tự 0–9 hoặc a–f, khớp bộ quy tắc.", "sha256:" + "a".repeat(64));
  for (const [nhom, ten, fields] of [["cat_doan", "Giới hạn cắt đoạn", catDoan], ["ngan_sach", "Ngân sách xử lý", nganSach]]) {
    tao("h3", ten, nangCao);
    const fs = tao("div", undefined, nangCao); fs.className = "tc-luoi";
    for (const [ma, [nhan, min, max, md]] of Object.entries(fields)) {
      if (ma === "do_dai_muc_tieu") continue;
      const donVi = ma.endsWith("byte") ? "byte" : ma.includes("ky_tu") ? "ký tự" : ma.includes("trang") ? "trang" : ma.includes("doan") ? "đoạn" : "mục";
      truong(`${nhom}.${ma}`, nhan, fs, [min, max], `Số nguyên từ ${min.toLocaleString("vi-VN")} đến ${max.toLocaleString("vi-VN")} ${donVi}; mặc định ${md.toLocaleString("vi-VN")} ${donVi}.`, String(md));
    }
  }
  const hanhDong = tao("div", undefined, form); hanhDong.className = "tc-hanh-dong";
  const luu = tao("button", "Lưu cấu hình", hanhDong);
  luu.type = "submit"; luu.disabled = true;
  const taiLai = tao("button", "Đọc lại cấu hình", hanhDong);
  taiLai.type = "button";

  function dien(c) {
    o.tep_id.value = c?.quy_tac_nhom.tep_id ?? "";
    o.bam.value = c?.quy_tac_nhom.bam ?? "";
    phanLoai = structuredClone(c?.phan_loai ?? {trang_thai: "chua_do"});
    nguong.value = phanLoai.trang_thai === "da_do"
      ? new Intl.NumberFormat("vi-VN", {style: "percent", maximumFractionDigits: 2}).format(phanLoai.nguong) : "Chưa đo";
    trangThaiDo.textContent = phanLoai.trang_thai === "da_do" ? "Đã đo · Chỉ đọc" : "Chưa đo";
    canhBao.textContent = phanLoai.trang_thai === "da_do"
      ? "Đã có ngưỡng đo. Màn này chỉ hiển thị kết quả; việc áp dụng cần phê duyệt tại Core."
      : "Chưa đo ngưỡng phân loại. Màn này không kích hoạt ngưỡng; cần kết quả đo và phê duyệt trước khi áp dụng.";
    for (const [nhom, fields] of [["cat_doan", catDoan], ["ngan_sach", nganSach]]) {
      for (const [ma, [, , , md]] of Object.entries(fields)) o[`${nhom}.${ma}`].value = String(c?.[nhom][ma] ?? md);
    }
  }
  function kiemNhap() {
    let hopLe = true;
    function bao(ma, cau) {loiO[ma].textContent = cau; o[ma].setAttribute("aria-invalid", String(Boolean(cau))); if (cau) hopLe = false;}
    bao("tep_id", /^[^\s/\\:]{1,200}$/.test(o.tep_id.value) ? "" : "Tham chiếu bộ quy tắc: nhập mã tệp 1–200 ký tự, không dùng đường dẫn hoặc khoảng trắng.");
    bao("bam", bam(o.bam.value) ? "" : "Băm xác nhận: nhập sha256: và đúng 64 ký tự 0–9 hoặc a–f.");
    for (const [nhom, fields] of [["cat_doan", catDoan], ["ngan_sach", nganSach]]) {
      for (const [ma, [nhan, min, max]] of Object.entries(fields)) {
        const ten = `${nhom}.${ma}`, v = o[ten].value;
        bao(ten, v.trim() && Number.isInteger(Number(v)) && Number(v) >= min && Number(v) <= max ? "" : `${nhan}: nhập số nguyên từ ${min.toLocaleString("vi-VN")} đến ${max.toLocaleString("vi-VN")}.`);
      }
    }
    if (Number(o["cat_doan.do_dai_muc_tieu"].value) > Number(o["cat_doan.ky_tu_don_vi_toi_da"].value)) bao("cat_doan.do_dai_muc_tieu", "Độ dài mục tiêu không được vượt trần ký tự mỗi đơn vị trong Nâng cao.");
    return hopLe;
  }
  async function refresh() {
    const lan = ++luot;
    luu.disabled = true;
    nhanTrangThai.textContent = "Đang đọc";
    try {
      const data = await cong.cau_hinh.doc();
      if (daDong || lan !== luot) return false;
      const c = data == null ? null : kiemCauHinh(data.gia_tri);
      if (data != null && (!Number.isSafeInteger(data.phien_ban_cau_hinh) || data.phien_ban_cau_hinh < 1)) loiCauHinh();
      phien = data?.phien_ban_cau_hinh ?? null;
      dien(c);
      luu.disabled = false;
      for (const ma of Object.keys(o)) {loiO[ma].textContent = ""; o[ma].setAttribute("aria-invalid", "false");}
      nhanTrangThai.textContent = c ? "Đã đọc cấu hình" : "Chưa cấu hình";
      thongBao.textContent = c ? "Đã đọc cấu hình." : "Engine chưa được cấu hình. Chọn bộ quy tắc trong Nâng cao và lưu cấu hình.";
      return true;
    } catch {
      if (!daDong && lan === luot) {
        phien = null; dien(null);
        nhanTrangThai.textContent = "Chưa đọc được";
        thongBao.textContent = "Chưa đọc được cấu hình hợp lệ hoặc chưa có quyền. Nhờ quản trị viên kiểm tra và đọc lại.";
      }
      return false;
    }
  }
  const docLai = () => dangLuu ? Promise.resolve(false) : refresh();
  async function luuCauHinh(event) {
    event?.preventDefault();
    if (daDong || dangLuu || luu.disabled) return;
    if (!kiemNhap()) {
      nangCao.open = true;
      Object.keys(o).find(ma => {if (loiO[ma].textContent) {o[ma].focus?.(); return true;} return false;});
      thongBao.textContent = "Chưa lưu. Sửa các ô được đánh dấu.";
      return;
    }
    let c;
    try {
      c = {phien_ban: 1, quy_tac_nhom: {tep_id: o.tep_id.value, bam: o.bam.value}, phan_loai: structuredClone(phanLoai)};
      for (const [nhom, fields] of [["cat_doan", catDoan], ["ngan_sach", nganSach]]) {
        c[nhom] = Object.fromEntries(Object.keys(fields).map(ma => {
          const v = o[`${nhom}.${ma}`].value;
          return [ma, v.trim() === "" ? NaN : Number(v)];
        }));
      }
      c = kiemCauHinh(c);
    } catch {
      thongBao.textContent = "Cấu hình không hợp lệ. Kiểm tra bộ quy tắc, mục tiêu và các giới hạn.";
      return;
    }
    dangLuu = true; luu.disabled = true; taiLai.disabled = true;
    for (const input of Object.values(o)) input.disabled = true;
    try {
      await cong.cau_hinh.luu(c, phien);
      if (!daDong && await refresh()) thongBao.textContent = "Đã lưu cấu hình.";
    } catch (e) {
      if (daDong) return;
      if (e?.ma === "NGAN_XUNG_DOT" || e?.ma === "CAU_HINH_XUNG_DOT" || e?.status === 409) {
        const daDoc = await refresh();
        if (!daDong) thongBao.textContent = daDoc
          ? "Cấu hình đã được người khác sửa. Đã tải lại; kiểm tra bản mới trước khi thử lưu lại."
          : "Cấu hình đã được người khác sửa, tải lại trước khi lưu. Nhờ quản trị viên kiểm tra quyền.";
      } else {
        // Không phản chiếu thông điệp SDK có thể chứa path hoặc dữ liệu.
        dien(null); phien = null;
        nhanTrangThai.textContent = "Chưa lưu được";
        thongBao.textContent = "Chưa lưu được cấu hình hoặc chưa có quyền. Đọc lại rồi thử lại.";
      }
    } finally {
      dangLuu = false; taiLai.disabled = false;
      for (const input of Object.values(o)) input.disabled = false;
    }
  }
  form.addEventListener("submit", luuCauHinh);
  taiLai.addEventListener("click", docLai);
  await refresh();
  return {refresh: docLai, unmount() {daDong = true; ++luot; form.removeEventListener("submit", luuCauHinh); taiLai.removeEventListener("click", docLai); for (const input of Object.values(o)) input.removeEventListener("input", kiemNhap); goc.replaceChildren();}};
}

export default mount;
