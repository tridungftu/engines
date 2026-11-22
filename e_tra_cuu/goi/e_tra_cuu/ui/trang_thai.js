// Chỉ đọc dot_kiem. Pháp nhân do host Core cấp; Core kiểm quyền MỖI truy vấn.
const chiSo = {tra_loi_dung: "Trả lời đúng", trich_dan_dung: "Trích dẫn đúng",
  tu_choi_dung: "Từ chối đúng khi thiếu căn cứ", phan_loai_dung: "Phân loại đúng"};
const so = n => new Intl.NumberFormat("vi-VN", {maximumFractionDigits: 2}).format(n);
const loiQuyen = e => [401, 403].includes(e?.status) || ["KHONG_DU_QUYEN", "CHUA_DANG_NHAP"].includes(e?.ma);
export function tyLe(v) {
  if (v == null) return "Chưa đo";
  if (!Number.isSafeInteger(v.tu_so) || !Number.isSafeInteger(v.mau_so)
      || v.tu_so < 0 || v.mau_so < 0 || v.tu_so > v.mau_so) return "Số đo không hợp lệ";
  if (v.mau_so === 0) return "Chưa đo";
  return `${so(v.tu_so)}/${so(v.mau_so)} (${so(100 * v.tu_so / v.mau_so)}%)`;
}
export function ngayViet(v) {
  if (typeof v !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(v)) return "Chưa có ngày";
  const d = new Date(`${v}T00:00:00Z`);
  if (!Number.isFinite(d.getTime()) || d.toISOString().slice(0, 10) !== v) return "Ngày không hợp lệ";
  return `${v.slice(8, 10)}/${v.slice(5, 7)}/${v.slice(0, 4)}`;
}
export function tienViet(v) {
  if (!v || !Number.isSafeInteger(v.so) || !/^[A-Z]{3}$/.test(v.tien_te)) return "Chưa có số tiền";
  return `${so(v.so)} ${v.tien_te}`;
}

export async function mount(goc, {KttCore = globalThis.KttCore, phapNhanId} = {}) {
  const cong = KttCore.engine("e_tra_cuu");
  const doc = goc.ownerDocument;
  const p = phapNhanId;
  let tiep = null, daDong = false, luot = 0, luotDoc = 0;
  function tao(tag, text, cha = goc) {
    const n = doc.createElement(tag);
    if (text !== undefined) n.textContent = text;
    cha.appendChild(n); return n;
  }
  goc.replaceChildren();
  tao("h2", "Trạng thái bài đo DEMO");
  tao("p", "Chỉ hiển thị bài đo thuộc pháp nhân Core cho phép. Bài đo DEMO chưa chứng nhận chất lượng thật.");
  tao("p", "Bài đo do Core lưu theo pháp nhân; chưa kiểm lưu bền trên Core thật.");
  const thongBao = tao("p", ""); thongBao.setAttribute("role", "status");
  const ds = tao("section");
  const sau = tao("button", "Trang sau"); sau.type = "button"; sau.disabled = true;
  const taiLai = tao("button", "Đọc lại danh sách"); taiLai.type = "button";
  const chiTiet = tao("section");
  const thongBaoDoc = tao("p", "", chiTiet); thongBaoDoc.setAttribute("role", "status");
  const noiDungDoc = tao("section", undefined, chiTiet);
  function kiemPhamVi(b) {
    if (!b || b.gia_tri?.phap_nhan_id !== p) throw new Error("Sai phạm vi pháp nhân.");
    const v = {...b.gia_tri};
    for (const ten of ["chi_so", "bao_cao"]) {
      if (v[ten] == null) continue;
      if (typeof v[ten] !== "string" || new TextEncoder().encode(v[ten]).length > 65536) throw new Error("Sai cấu trúc bài đo.");
      v[ten] = JSON.parse(v[ten]);
      if (!v[ten] || typeof v[ten] !== "object" || Array.isArray(v[ten])) throw new Error("Sai cấu trúc bài đo.");
    }
    return v;
  }
  function ve(b, cha) {
    const trangThai = {chua_do: "Chưa đo", dang_do: "Đang đo", da_do: "Đã đo DEMO", loi: "Bài đo có lỗi"};
    tao("h3", "Bài đo DEMO", cha);
    tao("p", Object.hasOwn(trangThai, b.trang_thai) ? trangThai[b.trang_thai] : "Trạng thái chưa hợp lệ", cha);
    for (const [ma, ten] of Object.entries(chiSo)) tao("p", `${ten}: ${tyLe(b.chi_so?.[ma])}`, cha);
    tao("p", b.bao_cao ? "Có tham chiếu báo cáo tại Core; Core kiểm quyền khi mở báo cáo." : "Chưa có báo cáo.", cha);
  }
  async function taiTrang(cursor = null) {
    const lan = ++luot;
    // Chỉ nhận cursor vừa được Core cấp cho màn này, cùng bảng/loc/pháp nhân.
    const hopLe = cursor == null || (typeof cursor === "string" && cursor === tiep);
    ds.replaceChildren(); sau.disabled = true; tiep = null;
    try {
      if (!hopLe || typeof p !== "string" || !p.trim()) throw new Error("Thiếu phạm vi Core.");
      const trang = await cong.ngan.tim("dot_kiem", {loc: {}, gioi_han: 500, tiep: cursor});
      if (daDong || lan !== luot) return false;
      if (!Array.isArray(trang?.danh_sach) || trang.danh_sach.length > 500
          || (trang.tiep != null && (typeof trang.tiep !== "string" || trang.tiep === cursor))) throw new Error("Trang không hợp lệ.");
      const cacBan = trang.danh_sach.map(kiemPhamVi); // Kiểm hết trước khi vẽ bất kỳ hàng nào.
      for (const b of cacBan) {
        const hang = tao("article", undefined, ds);
        ve(b, hang);
        const xem = tao("button", "Xem chi tiết bài đo", hang);
        xem.type = "button";
        xem.addEventListener("click", () => docBaiDo(b.ma_dot));
      }
      tiep = trang.tiep ?? null; sau.disabled = tiep == null;
      thongBao.textContent = cacBan.length ? "Đã đọc bài đo DEMO." : "Chưa có bài đo DEMO trong phạm vi được phép.";
      return true;
    } catch (e) {
      if (!daDong && lan === luot) {
        ds.replaceChildren(); tiep = null; sau.disabled = true;
        if (loiQuyen(e)) {++luotDoc; noiDungDoc.replaceChildren(); thongBaoDoc.textContent = "";}
        thongBao.textContent = "Chưa đọc được bài đo hoặc chưa có quyền trong pháp nhân này. Đọc lại hoặc nhờ quản trị viên kiểm tra.";
      }
      return false;
    }
  }
  async function docBaiDo(maDot) {
    const lan = ++luotDoc;
    noiDungDoc.replaceChildren();
    try {
      if (typeof p !== "string" || !p.trim() || typeof maDot !== "string" || !/^DEMO-[A-Za-z0-9_.-]{1,195}$/.test(maDot)) throw new Error("Mã bài đo không hợp lệ.");
      const b = await cong.ngan.doc("dot_kiem", {ma_dot: maDot});
      if (daDong || lan !== luotDoc) return false;
      if (b) {
        const v = kiemPhamVi(b);
        if (v.ma_dot !== maDot) throw new Error("Sai bài đo.");
        ve(v, noiDungDoc);
      }
      thongBaoDoc.textContent = b ? "Đã đọc bài đo DEMO." : "Chưa có bài đo này trong phạm vi được phép.";
      return true;
    } catch (e) {
      if (!daDong && lan === luotDoc) {
        noiDungDoc.replaceChildren();
        if (loiQuyen(e)) {++luot; ds.replaceChildren(); tiep = null; sau.disabled = true;}
        thongBaoDoc.textContent = "Chưa đọc được chi tiết bài đo hoặc chưa có quyền. Thử lại.";
      }
      return false;
    }
  }
  const trangSau = () => taiTrang(tiep);
  const refresh = () => taiTrang();
  sau.addEventListener("click", trangSau); taiLai.addEventListener("click", refresh);
  await refresh();
  return {refresh, taiTrang, docBaiDo, unmount() {daDong = true; ++luot; ++luotDoc; sau.removeEventListener("click", trangSau); taiLai.removeEventListener("click", refresh); goc.replaceChildren();}};
}

export default mount;
