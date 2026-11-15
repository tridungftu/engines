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
const loiCauHinh = () => { throw new Error("Cấu hình không hợp lệ. Anh kiểm tra lại các giá trị."); };

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
  const o = {};
  function tao(tag, text, cha = goc) {
    const n = doc.createElement(tag);
    if (text !== undefined) n.textContent = text;
    cha.appendChild(n);
    return n;
  }
  goc.replaceChildren();
  tao("h2", "Cấu hình Tra cứu tài liệu");
  tao("p", "Bản tạm dùng Ngăn RAM sẽ mất cấu hình và bài đo khi khởi động lại. Chưa kiểm Ngăn Core thật.");
  const thongBao = tao("p", "Đang đọc cấu hình…");
  thongBao.setAttribute("role", "status");
  const form = tao("form");
  function truong(ma, nhan, cha, gioiHan) {
    const label = tao("label", nhan, cha);
    const input = tao("input", undefined, label);
    input.name = ma;
    input.type = gioiHan ? "number" : "text";
    input.required = true;
    if (gioiHan) {
      input.min = String(gioiHan[0]); input.max = String(gioiHan[1]); input.step = "1";
    } else input.maxLength = ma === "bam" ? 71 : 200;
    o[ma] = input;
  }
  const quyTac = tao("fieldset", undefined, form);
  tao("legend", "Bộ quy tắc nhóm do Core quản lý", quyTac);
  truong("tep_id", "Tham chiếu bộ quy tắc tại Core", quyTac);
  truong("bam", "Băm xác nhận bộ quy tắc", quyTac);
  const nguong = tao("p", "Ngưỡng phân loại: Chưa đo.", form);
  tao("p", "Màn này không kích hoạt ngưỡng. Ngưỡng đã đo cần được duyệt qua Core.", form);
  for (const [nhom, ten, fields] of [["cat_doan", "Cắt đoạn", catDoan], ["ngan_sach", "Ngân sách xử lý", nganSach]]) {
    const fs = tao("fieldset", undefined, form);
    tao("legend", ten, fs);
    for (const [ma, [nhan, min, max]] of Object.entries(fields)) truong(`${nhom}.${ma}`, nhan, fs, [min, max]);
  }
  const luu = tao("button", "Lưu cấu hình", form);
  luu.type = "submit"; luu.disabled = true;
  const taiLai = tao("button", "Đọc lại cấu hình");
  taiLai.type = "button";

  function dien(c) {
    o.tep_id.value = c?.quy_tac_nhom.tep_id ?? "";
    o.bam.value = c?.quy_tac_nhom.bam ?? "";
    phanLoai = structuredClone(c?.phan_loai ?? {trang_thai: "chua_do"});
    nguong.textContent = phanLoai.trang_thai === "da_do"
      ? `Ngưỡng phân loại đã đo: ${new Intl.NumberFormat("vi-VN", {style: "percent", maximumFractionDigits: 2}).format(phanLoai.nguong)}. Chưa xác nhận kích hoạt thật.`
      : "Ngưỡng phân loại: Chưa đo. Chưa kích hoạt.";
    for (const [nhom, fields] of [["cat_doan", catDoan], ["ngan_sach", nganSach]]) {
      for (const [ma, [, , , md]] of Object.entries(fields)) o[`${nhom}.${ma}`].value = String(c?.[nhom][ma] ?? md);
    }
  }
  async function refresh() {
    const lan = ++luot;
    luu.disabled = true;
    try {
      const data = await cong.cau_hinh.doc();
      if (daDong || lan !== luot) return false;
      const c = data == null ? null : kiemCauHinh(data.gia_tri);
      if (data != null && (!Number.isSafeInteger(data.phien_ban_cau_hinh) || data.phien_ban_cau_hinh < 1)) loiCauHinh();
      phien = data?.phien_ban_cau_hinh ?? null;
      dien(c);
      luu.disabled = false;
      thongBao.textContent = c ? "Đã đọc cấu hình." : "Engine chưa được cấu hình. Anh chọn bộ quy tắc và lưu cấu hình.";
      return true;
    } catch {
      if (!daDong && lan === luot) {
        phien = null; dien(null);
        thongBao.textContent = "Chưa đọc được cấu hình hợp lệ hoặc chưa có quyền. Anh nhờ quản trị viên kiểm tra và đọc lại.";
      }
      return false;
    }
  }
  async function luuCauHinh(event) {
    event?.preventDefault();
    if (daDong || dangLuu || luu.disabled) return;
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
      thongBao.textContent = "Cấu hình không hợp lệ. Anh kiểm tra bộ quy tắc, mục tiêu và các giới hạn.";
      return;
    }
    dangLuu = true; luu.disabled = true; taiLai.disabled = true;
    try {
      await cong.cau_hinh.luu(c, phien);
      if (!daDong && await refresh()) thongBao.textContent = "Đã lưu cấu hình.";
    } catch (e) {
      if (daDong) return;
      if (e?.ma === "NGAN_XUNG_DOT" || e?.ma === "CAU_HINH_XUNG_DOT" || e?.status === 409) {
        const daDoc = await refresh();
        if (!daDong) thongBao.textContent = daDoc
          ? "Cấu hình đã thay đổi. Đã đọc lại; Anh kiểm tra và thử lưu lại."
          : "Cấu hình đã thay đổi. Anh nhờ quản trị viên kiểm tra quyền rồi đọc lại và thử lại.";
      } else {
        // Không phản chiếu thông điệp SDK có thể chứa path hoặc dữ liệu.
        dien(null); phien = null;
        thongBao.textContent = "Chưa lưu được cấu hình hoặc chưa có quyền. Anh đọc lại rồi thử lại.";
      }
    } finally {
      dangLuu = false; taiLai.disabled = false;
    }
  }
  form.addEventListener("submit", luuCauHinh);
  taiLai.addEventListener("click", refresh);
  await refresh();
  return {refresh, unmount() {daDong = true; ++luot; form.removeEventListener("submit", luuCauHinh); taiLai.removeEventListener("click", refresh); goc.replaceChildren();}};
}

export default mount;
