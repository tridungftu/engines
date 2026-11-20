// PL-8B. Core kiểm quyền admin_core khi nạp màn và khi đọc ngăn.
// Không có cổng engine trong wheel SDK 2.2.0 hiện tại: dừng an toàn, chờ Core.
const cotTyLe = [
  ["khau", "Khâu"], ["loai", "Loại"], ["bac", "Bậc"], ["che_do", "Chế độ"],
  ["diem", "Điểm rủi ro"], ["nhan", "Nhãn"],
  ["mau_tu_doi_bac", "Mẫu từ lần đổi bậc"], ["loi_tu_doi_bac", "Lỗi từ lần đổi bậc"],
  ["mau_12t", "Mẫu 12 tháng"], ["loi_12t", "Lỗi 12 tháng"],
];
const tenGiaTri = {bac: "Theo bậc", toan_bo: "Kiểm toàn bộ", rui_ro_cao: "Rủi ro cao",
  loi_ngoai_mau: "Lỗi ngoài mẫu", chua_phan_loai: "Chưa phân loại"};
const lyDoDo = new Set(["VUOT_PM", "VUOT_TE", "CHUA_QUY_DOI", "CHUA_RO_TIEN_TE",
  "NGHI_CHIA_NHO", "CO_DO_CUNG", "NOP_LAI", "CHON_MAU"]);
const loiDuLieu = () => Object.assign(new Error(), {ma: "PL_UI_DU_LIEU_KHONG_HOP_LE"});
const chu = v => v === null || v === undefined || v === "" ? "Chưa có" : String(v);
const soDem = v => {
  if (!/^(0|[1-9][0-9]*)(?:\.0+)?$/.test(String(v))) throw loiDuLieu();
  const n = Number(v);
  if (!Number.isSafeInteger(n)) throw loiDuLieu();
  return n;
};

export async function mount(goc, {KttCore = globalThis.KttCore} = {}) {
  const doc = goc.ownerDocument;
  let daDong = false, phienTai = 0, phienTra = 0;
  function tao(ten, noiDung, cha = goc) {
    const e = doc.createElement(ten);
    if (noiDung !== undefined) e.textContent = noiDung;
    cha.appendChild(e);
    return e;
  }
  function nut(ten, cha = goc) {
    const e = tao("button", ten, cha);
    e.type = "button";
    return e;
  }
  function bang(cha, cot, ds) {
    if (!ds.length) { tao("p", "Chưa có dữ liệu.", cha); return; }
    const b = tao("table", undefined, cha);
    const dau = tao("tr", undefined, tao("thead", undefined, b));
    for (const [, ten] of cot) tao("th", ten, dau).scope = "col";
    const than = tao("tbody", undefined, b);
    for (const r of ds) {
      const hang = tao("tr", undefined, than);
      for (const [ma] of cot) {
        const v = r[ma];
        tao("td", ["che_do", "nhan", "loai"].includes(ma)
          ? (Object.hasOwn(tenGiaTri, v) ? tenGiaTri[v] : chu(v)) : chu(v), hang);
      }
    }
  }
  function muc(ten) {
    const s = tao("section");
    tao("h3", ten, s);
    return tao("div", undefined, s);
  }
  goc.replaceChildren();
  tao("h2", "Bảng tỷ lệ kiểm tra");
  tao("p", "Chỉ Admin Core được xem. Màn chỉ đọc dữ liệu của pháp nhân đang chọn.");
  tao("p", "Bậc là chỉ số bậc lưu trong ngăn; điểm là cận trên tỷ lệ lỗi 12 tháng.");
  const taiLai = nut("Tải lại");
  const thongBao = tao("div");
  thongBao.setAttribute("role", "status");
  const tyLe = muc("Tỷ lệ theo khâu × loại");
  const saiLoai = muc("Sai loại theo nguồn");
  const lichSu = muc("Lịch sử chốt kỳ");
  const canhBao = muc("Hồ sơ hành vi");
  const tra = muc("Tra lượt phân luồng");
  const form = tao("form", undefined, tra);
  const nhan = tao("label", "Mã lượt ", form);
  const maLuot = tao("input", undefined, nhan);
  maLuot.type = "text";
  maLuot.required = true;
  maLuot.maxLength = 200;
  maLuot.autocomplete = "off";
  const tim = tao("button", "Tra lượt", form);
  tim.type = "submit";
  const ketQuaTra = tao("div", undefined, tra);
  const cacMuc = [tyLe, saiLoai, lichSu, canhBao];

  function baoLoi(loi) {
    thongBao.replaceChildren();
    tao("p", typeof loi?.thong_diep === "string" && loi.thong_diep.trim() &&
      loi.thong_diep.length <= 1000 ? loi.thong_diep
      : "Chưa đọc được dữ liệu. Hãy tải lại hoặc kiểm tra quyền Admin và pháp nhân đang chọn.", thongBao);
    const chiTiet = tao("details", undefined, thongBao);
    chiTiet.open = false;
    tao("summary", "Chi tiết hỗ trợ", chiTiet);
    const ma = /^[A-Z][A-Z0-9_]{0,79}$/.test(loi?.ma) ? loi.ma : "PL_UI_LOI";
    tao("p", `Mã lỗi: ${ma}`, chiTiet);
    if (/^[A-Za-z0-9_-]{1,100}$/.test(loi?.request_id)) {
      tao("p", `Mã yêu cầu: ${loi.request_id}`, chiTiet);
    }
    if ([401, 403].includes(loi?.status)) {
      for (const s of cacMuc) s.replaceChildren();
      ketQuaTra.replaceChildren();
      ++phienTai; ++phienTra;
      taiLai.disabled = false;
    }
  }
  // Không tự dựng HTTP thay cho SDK còn thiếu; không suy quyền từ dữ liệu nhập.
  if (typeof KttCore?.engine !== "function") {
    taiLai.disabled = true; tim.disabled = true; maLuot.disabled = true;
    baoLoi({ma: "PL_UI_THIEU_CONG_ENGINE", thong_diep:
      "SDK hiện tại chưa có cổng quản trị engine. Cần cập nhật SDK từ Core để mở màn này."});
    return {destroy() { daDong = true; goc.replaceChildren(); }};
  }
  let cong;
  try {
    cong = KttCore.engine("e_phan_luong");
    if (typeof cong?.ngan?.doc !== "function" || typeof cong?.ngan?.tim !== "function") {
      throw Object.assign(new Error(), {ma: "PL_UI_THIEU_CONG_NGAN", thong_diep:
        "SDK chưa có đủ cổng đọc ngăn engine. Cần cập nhật SDK từ Core để mở màn này."});
    }
  } catch (loi) {
    baoLoi(loi);
    taiLai.disabled = true; tim.disabled = true; maLuot.disabled = true;
    return {destroy() { daDong = true; goc.replaceChildren(); }};
  }
  // Đọc hết các trang; vượt trần thì từ chối, không hiển thị số đếm bị cắt.
  async function timHet(bangNgan, loc, nhanDong, conHieuLuc) {
    let tiep = null, dem = 0;
    const daGap = new Set();
    do {
      if (!conHieuLuc()) return;
      const trang = await cong.ngan.tim(bangNgan, {loc, gioi_han: 500, tiep});
      if (!conHieuLuc()) return;
      if (!Array.isArray(trang?.danh_sach) || trang.danh_sach.length > 500 ||
          !(trang.tiep === null || typeof trang.tiep === "string")) throw loiDuLieu();
      dem += trang.danh_sach.length;
      if (dem > 200000 || daGap.size >= 400) {
        throw Object.assign(new Error(), {ma: "PL_UI_VUOT_GIOI_HAN", thong_diep:
          "Dữ liệu vượt giới hạn đọc của màn quản trị. Cần Core hỗ trợ tổng hợp hoặc lọc thêm."});
      }
      for (const r of trang.danh_sach) {
        if (!r?.gia_tri || typeof r.gia_tri !== "object") throw loiDuLieu();
        nhanDong(r.gia_tri);
      }
      tiep = trang.tiep;
      if (tiep !== null) {
        if (!tiep || daGap.has(tiep)) throw loiDuLieu();
        daGap.add(tiep);
      }
    } while (tiep !== null);
  }
  async function refresh() {
    const phien = ++phienTai;
    const conHieuLuc = () => !daDong && phien === phienTai;
    ++phienTra;
    ketQuaTra.replaceChildren();
    for (const s of cacMuc) s.replaceChildren();
    thongBao.textContent = "Đang đọc dữ liệu…";
    taiLai.disabled = true;
    const dsTyLe = [], dsChot = [], dsCanhBao = [], theoNguon = new Map();
    try {
      await timHet("ty_le", {}, r => dsTyLe.push(r), conHieuLuc);
      await timHet("ket_qua_kiem", {}, r => {
        if (!["quy_tac", "ai"].includes(r.nguon_loai_sai)) return;
        const khoa = JSON.stringify([r.khau, r.loai]);
        if (!theoNguon.has(khoa)) theoNguon.set(khoa, {khau: r.khau, loai: r.loai, quy_tac: 0, ai: 0});
        theoNguon.get(khoa)[r.nguon_loai_sai] += 1;
      }, conHieuLuc);
      await timHet("chot_ky", {}, r => dsChot.push(r), conHieuLuc);
      let coDem = false;
      await timHet("ho_so_hanh_vi", {}, r => {
        let n = r.so_doi_tac;
        if (n === undefined && r.bam_doi_tac != null) {
          const tap = JSON.parse(r.bam_doi_tac);
          if (!tap || typeof tap !== "object") throw loiDuLieu();
          n = Array.isArray(tap) ? tap.length : Object.keys(tap).length;
        }
        if (n === undefined) return;
        coDem = true;
        if (soDem(n) >= 20000) dsCanhBao.push({khau: r.khau, loai: r.loai, so_doi_tac: n});
      }, conHieuLuc);
      if (!conHieuLuc()) return;
      const sap = (a, b) => chu(a.khau).localeCompare(chu(b.khau)) || chu(a.loai).localeCompare(chu(b.loai));
      bang(tyLe, cotTyLe, dsTyLe.sort(sap));
      tao("p", "Đếm trên kết quả kiểm còn hạn 365 ngày; loại hiển thị là loại đúng sau khi sửa.", saiLoai);
      const tong = [...theoNguon.values()].reduce((a, r) =>
        ({quy_tac: a.quy_tac + r.quy_tac, ai: a.ai + r.ai}), {quy_tac: 0, ai: 0});
      tao("p", `Tổng sai loại — Quy tắc: ${tong.quy_tac}; AI nội bộ: ${tong.ai}.`, saiLoai);
      bang(saiLoai, [["khau", "Khâu"], ["loai", "Loại"], ["quy_tac", "Quy tắc"], ["ai", "AI nội bộ"]],
        [...theoNguon.values()].sort(sap));
      dsChot.sort((a, b) => chu(b.ky).localeCompare(chu(a.ky)) || sap(a, b));
      bang(lichSu, [["ky", "Kỳ (năm-tháng)"], ...cotTyLe], dsChot);
      if (dsCanhBao.length) {
        tao("p", "Cảnh báo: hồ sơ đã chạm trần 20.000 đối tác. Đối tác lâu không gặp có thể đã bị loại khỏi hồ sơ.", canhBao);
        bang(canhBao, [["khau", "Khâu"], ["loai", "Loại"], ["so_doi_tac", "Số đối tác đang giữ"]], dsCanhBao.sort(sap));
      } else tao("p", coDem ? "Chưa ghi nhận hồ sơ chạm trần 20.000 đối tác."
        : "Chưa có số đếm đối tác để kiểm tra trần hồ sơ.", canhBao);
      thongBao.textContent = "Đã đọc dữ liệu. Bấm Tải lại để xem cập nhật mới.";
    } catch (loi) {
      if (conHieuLuc()) {
        for (const s of cacMuc) s.replaceChildren();
        baoLoi(loi);
      }
    } finally { if (!daDong && phien === phienTai) taiLai.disabled = false; }
  }
  maLuot.addEventListener("input", () => { ++phienTra; ketQuaTra.replaceChildren(); });
  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (tim.disabled || daDong) return;
    const phien = ++phienTra, ma = maLuot.value.trim();
    const conHieuLuc = () => !daDong && phien === phienTra;
    ketQuaTra.replaceChildren();
    thongBao.replaceChildren();
    if (!ma || ma.length > 200 || /[\u0000-\u001f\u007f]/.test(ma)) {
      tao("p", "Cần nhập mã lượt hợp lệ, tối đa 200 ký tự.", ketQuaTra); return;
    }
    tim.disabled = true;
    try {
      const banGhi = await cong.ngan.doc("luot", {ma_luot: ma});
      if (!conHieuLuc()) return;
      if (!banGhi) { tao("p", "Không tìm thấy lượt phân luồng còn hạn lưu.", ketQuaTra); return; }
      const r = banGhi.gia_tri;
      if (!r || r.ma_luot !== ma) throw loiDuLieu();
      let doDem = 0, xanhDem = 0;
      await timHet("dong_luot", {ma_luot: ma}, dong => {
        if (dong.ma_luot !== ma) throw loiDuLieu();
        const lyDo = typeof dong.ly_do === "string" ? dong.ly_do.split(",") : [];
        if (lyDo.length === 1 && lyDo[0] === "KHONG_CHON") xanhDem += 1;
        else if (lyDo.length && lyDo.every(v => lyDoDo.has(v))) doDem += 1;
        else throw loiDuLieu();
      }, conHieuLuc);
      if (!conHieuLuc()) return;
      bang(ketQuaTra, [["ma_luot", "Mã lượt"], ["ma_module", "Mã module"], ["khau", "Khâu"],
        ["bam_dau_vao", "Băm đầu vào"], ["so_do", "Số dòng Đỏ"], ["so_xanh", "Số dòng Xanh"]],
      [{...r, so_do: doDem, so_xanh: xanhDem}]);
      const hat = tao("p", "Hạt giống đang ẩn.", ketQuaTra);
      const xem = nut("Xem", ketQuaTra);
      xem.setAttribute("aria-label", "Xem hạt giống");
      xem.setAttribute("aria-expanded", "false");
      let daXem = false;
      xem.addEventListener("click", () => {
        if (!conHieuLuc()) return;
        daXem = !daXem;
        hat.textContent = daXem ? `Hạt giống: ${chu(r.hat_giong)}` : "Hạt giống đang ẩn.";
        xem.textContent = daXem ? "Ẩn" : "Xem";
        xem.setAttribute("aria-label", daXem ? "Ẩn hạt giống" : "Xem hạt giống");
        xem.setAttribute("aria-expanded", String(daXem));
      });
    } catch (loi) {
      if (conHieuLuc()) { ketQuaTra.replaceChildren(); baoLoi(loi); }
    } finally { if (!daDong) tim.disabled = false; }
  });
  taiLai.addEventListener("click", () => { if (!daDong) void refresh(); });
  await refresh();
  return {refresh, destroy() { daDong = true; ++phienTai; ++phienTra; goc.replaceChildren(); }};
}

export default mount;
