// MASK-R7: chỉ metadata. C-P4-06 chưa được SDK đăng ký.
// thao_tac là cửa Core chung đề nghị: xem_du_lieu mở màn Core, chỉ trả vé
// ID/phiên bản; quyet_dinh_duyet kiểm vé/quyền/CAS qua backend, không tên.
// Thiếu cửa hoặc lệnh chưa hỗ trợ: để chờ. Không ghi ngăn từ trình duyệt.
export function taoMan({ KttCore, goc, document = globalThis.document }) {
  const engine = KttCore.engine("e_mask");
  const noi = document.createElement("div");
  const thongBao = document.createElement("p");
  const bang = document.createElement("table");
  const tao = (ten, chu) => { const e = document.createElement(ten); e.textContent = chu; return e; };
  noi.append(tao("h2", "Duyệt danh sách chờ"), thongBao, bang);
  goc.append(noi);
  const nhom = { CONG_TY: "Công ty", CA_NHAN: "Cá nhân", DIA_CHI: "Địa chỉ",
    MA_SO_THUE: "Mã số thuế", TAI_KHOAN: "Tài khoản", KHAC: "Khác" };
  const idDung = (v) => typeof v === "string" && /^(?:[0-9a-f]{32}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})$/.test(v);
  const phienDung = (v) => Number.isSafeInteger(v) && v > 0;
  const cho = "Chưa xác minh được tại Core. Anh hãy tải lại danh sách và xem lại tại Core.";
  let ds = [], tiep = null, dangChay = false, luot = 0;
  const veXem = new Map();
  function metadata(r) {
    const m = r?.gia_tri;
    if (!m || !idDung(m.id_dinh_danh) || !phienDung(r.row_version) ||
        !["DEMO", "THAT"].includes(m.vung_du_lieu) || !Object.hasOwn(nhom, m.nhom) ||
        m.trang_thai !== "CHO_DUYET" ||
        m.gia_tri_goc !== null || m.gia_tri_chuan !== null ||
        m.gia_tri_goc_da_ma_hoa !== true || m.gia_tri_chuan_da_ma_hoa !== true ||
        !/^(?:0|[1-9][0-9]*)$/.test(String(m.so_gap)) ||
        !Number.isSafeInteger(Number(m.so_gap))) throw new Error("du_lieu");
    // Hàng chờ chưa có alias chính thức; không lấy cột bổ sung từ nguồn.
    return Object.freeze({ id_dinh_danh: m.id_dinh_danh, row_version: r.row_version,
      vung_du_lieu: m.vung_du_lieu, nhom: m.nhom, trang_thai: m.trang_thai,
      so_gap: Number(m.so_gap), bi_danh: null });
  }
  function thamChieu(m) {
    return { bang: "dinh_danh", id_dinh_danh: m.id_dinh_danh,
      row_version: m.row_version, vung_du_lieu: m.vung_du_lieu };
  }
  function timMuc(m) {
    const r = ds.find((v) => v.id_dinh_danh === m?.id_dinh_danh && v.row_version === m?.row_version);
    if (!r) throw new Error("phien");
    return r;
  }
  async function cua(ma, dl) {
    if (typeof engine.thao_tac !== "function") throw new Error("chua_co_cua");
    return engine.thao_tac(ma, dl);
  }
  async function bao(ham) {
    if (dangChay) return false;
    dangChay = true;
    try { await ham(); return true; }
    catch (loi) {
      veXem.clear();
      thongBao.textContent = ["NGAN_XUNG_DOT", "MASK_XUNG_DOT"].includes(loi?.ma)
        ? "Danh sách vừa thay đổi. Anh hãy tải lại và xem lại tại Core." : cho;
      return false;
    } finally { dangChay = false; ve(); }
  }
  async function xem(muc) {
    return bao(async () => {
      const m = timMuc(muc), hienTai = luot;
      veXem.delete(m.id_dinh_danh);
      const v = await cua("xem_du_lieu", thamChieu(m));
      // Cửa Core không được callback tên/object khác vào màn engine.
      if (!v || Object.keys(v).sort().join(",") !== "bien_nhan,id_dinh_danh,row_version" ||
          v.id_dinh_danh !== m.id_dinh_danh || v.row_version !== m.row_version ||
          !phienDung(v.row_version) || typeof v.bien_nhan !== "string" ||
          !/^[0-9a-f]{32}$/.test(v.bien_nhan) || hienTai !== luot) throw new Error("bien_nhan");
      veXem.set(m.id_dinh_danh, Object.freeze({ ...v }));
      thongBao.textContent = "Đã nhận biên nhận xem tại Core.";
    });
  }
  async function quyetDinh(muc, quyet_dinh, maJunsky) {
    return bao(async () => {
      const m = timMuc(muc), v = veXem.get(m.id_dinh_danh);
      if (!v || v.row_version !== m.row_version) throw new Error("chua_xem");
      if (typeof maJunsky !== "string" || (maJunsky &&
          (!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$/.test(maJunsky) ||
           /^MASK(?:CT|CN|DC|MST|TK|KHAC|TAM)/i.test(maJunsky)))) throw new Error("ma");
      veXem.delete(m.id_dinh_danh); // Không dùng lại sau lỗi hoặc mất ACK.
      const kq = await cua("quyet_dinh_duyet", { ...thamChieu(m), bien_nhan: v.bien_nhan,
        quyet_dinh, ma_junsky: maJunsky || null });
      if (!kq || Object.keys(kq).sort().join(",") !== "bi_danh,id_dinh_danh,trang_thai" ||
          kq.id_dinh_danh !== m.id_dinh_danh ||
          kq.trang_thai !== (quyet_dinh === "DUYET" ? "CHINH_THUC" : "TU_CHOI") ||
          (quyet_dinh === "DUYET" ? typeof kq.bi_danh !== "string" ||
            !/^\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]$/.test(kq.bi_danh) : kq.bi_danh !== null))
        throw new Error("xac_nhan");
      await tai(null);
      thongBao.textContent = "Đã cập nhật danh sách.";
    });
  }
  const duyet = (m, ma = "") => quyetDinh(m, "DUYET", ma);
  const tuChoi = (m) => quyetDinh(m, "TU_CHOI", "");
  function nut(ten, ham, cam = false) {
    const n = tao("button", ten); n.disabled = cam || dangChay;
    n.addEventListener("click", () => ham()); return n;
  }
  function ve() {
    bang.replaceChildren();
    const dau = document.createElement("tr");
    for (const t of ["ID tham chiếu", "Bí danh", "Nhóm", "Trạng thái", "Số gặp", "Mã đối tác (nếu có)", "Thao tác"]) dau.append(tao("th", t));
    bang.append(dau);
    for (const m of ds) {
      const hang = document.createElement("tr");
      hang.append(tao("td", m.id_dinh_danh), tao("td", m.bi_danh || "Chưa cấp"),
        tao("td", nhom[m.nhom]), tao("td", "Chờ duyệt"), tao("td", String(m.so_gap)));
      const cot = document.createElement("td"), o = document.createElement("input");
      o.setAttribute("aria-label", "Mã đối tác"); cot.append(o); hang.append(cot);
      const tac = document.createElement("td"), chuaXem = !veXem.has(m.id_dinh_danh);
      tac.append(nut("Xem tại Core", () => xem(m), typeof engine.thao_tac !== "function"),
        nut("Duyệt", () => duyet(m, o.value.trim()), chuaXem),
        nut("Từ chối", () => tuChoi(m), chuaXem));
      hang.append(tac); bang.append(hang);
    }
    trangSau.disabled = dangChay || tiep === null;
  }
  async function tai(conTro) {
    const hienTai = ++luot;
    veXem.clear(); ds = []; tiep = null; ve();
    const trang = await engine.ngan.tim("dinh_danh", {
      loc: { trang_thai: "CHO_DUYET" }, gioi_han: 100, tiep: conTro });
    if (hienTai !== luot) return;
    if (!Array.isArray(trang.danh_sach) || trang.danh_sach.length > 100 ||
        !(trang.tiep === null || typeof trang.tiep === "string")) throw new Error("trang");
    const moi = trang.danh_sach.map(metadata);
    if (new Set(moi.map((m) => m.id_dinh_danh)).size !== moi.length) throw new Error("trung");
    ds = moi; tiep = trang.tiep; ve();
  }
  const nap = () => bao(() => tai(null));
  const trangSau = nut("Trang sau", () => bao(() => tai(tiep)), true);
  noi.append(nut("Tải lại", nap), trangSau);
  thongBao.textContent = cho;
  return { nap, xem, duyet, tuChoi, thongBao };
}
export default taoMan;
