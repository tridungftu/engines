// TS-PL: mô hình thuần, không IO. Cấu trúc bám bộ đọc Python hiện hành.
export const CAC_O = ["danh_muc_loai_json", "bo_phan_loai_json", "nguong_json", "chinh_sach_json", "khuon_cot_json"];
export const NANG_LUC = {
  "audit.phan_luong@1": CAC_O,
  "audit.chuan_bi_phan_loai@1": CAC_O,
  "audit.phan_luong_sau_ai@1": CAC_O,
  "audit.phan_luong_hoa_don@1": CAC_O.slice(0, 4),
  "audit.ghi_ket_qua@1": [CAC_O[0], CAC_O[2], CAC_O[3]],
};
export const TRAN = {danh_muc_loai_json: 16384, bo_phan_loai_json: 32768,
  nguong_json: 4096, chinh_sach_json: 8192, khuon_cot_json: 32768};
export const TEN_O = {danh_muc_loai_json: "Danh mục loại", bo_phan_loai_json: "Bộ phân loại",
  nguong_json: "Ngưỡng kiểm tra", chinh_sach_json: "Chính sách kiểm tra", khuon_cot_json: "Khuôn cột Excel/CSV"};
export const COT = {ma: "Mã nghiệp vụ", ngay: "Ngày nghiệp vụ", so_tien: "Số tiền",
  tien_te: "Tiền tệ", so_tien_quy_doi: "Số tiền quy đổi", tien_te_quy_doi: "Tiền tệ quy đổi",
  loai: "Loại nghiệp vụ", doi_tac: "Đối tác", dien_giai: "Diễn giải", tai_khoan_no: "Tài khoản Nợ",
  tai_khoan_co: "Tài khoản Có", nhap_tay: "Nhập tay", co_do_cung: "Cờ đỏ cứng"};
export const CO = {SO_TIEN_BAT_THUONG: "Số tiền bất thường", DOI_TAC_MOI: "Đối tác mới",
  SO_TRON: "Số tròn", NGAY_NGHI: "Ngày nghỉ", CUOI_KY: "Cuối kỳ", NHAP_TAY: "Nhập tay"};
export const CHINH_SACH = {bac: [0.30, 0.20, 0.10, 0.05], nguong_xuong: [0.10, 0.05, 0.03],
  mau_toi_thieu: [30, 60, 100], ty_le_chua_phan_loai: 0.30, mau_sach_toan_bo: 30,
  nguong_diem_rui_ro: 0.10, do_tin_cay: 0.95, he_so: {SO_TIEN_BAT_THUONG: 2, DOI_TAC_MOI: 2,
    SO_TRON: 1.5, NGAY_NGHI: 1.5, CUOI_KY: 1.5, NHAP_TAY: 1.5},
  don_vi_so_tron: 10000000, ty_le_duoi_sad: 0.02, san: 0.05, toi_thieu_ho_so_doi_tac_moi: 0};

// Không đưa tiền qua Number: giữ nguyên token số JSON, kể cả > 2^53.
export class SoJson { constructor(chuoi) { this.chuoi = chuoi; } toString() { return this.chuoi; } }
export const laSo = v => v instanceof SoJson || typeof v === "number" && Number.isFinite(v);
export const chuSo = v => v instanceof SoJson ? v.chuoi : String(v ?? "");
export const sao = v => docJson(vietJson(v));
export function vietJson(v, dep = false, bac = 0) {
  if (v instanceof SoJson) {
    if (!/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$/.test(v.chuoi)) throw new Error("Số chưa hợp lệ.");
    return v.chuoi;
  }
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  const mang = Array.isArray(v), cap = mang ? v.map(x => vietJson(x, dep, bac + 1))
    : Object.entries(v).map(([k, x]) => JSON.stringify(k) + (dep ? ": " : ":") + vietJson(x, dep, bac + 1));
  const [mo, dong] = mang ? ["[", "]"] : ["{", "}"];
  return mo + (dep && cap.length ? "\n" + "  ".repeat(bac + 1) : "") +
    cap.join(dep ? ",\n" + "  ".repeat(bac + 1) : ",") +
    (dep && cap.length ? "\n" + "  ".repeat(bac) : "") + dong;
}
export function docJson(chuoi) {
  let i = 0;
  const loi = () => { throw new Error(`Dòng ${chuoi.slice(0, i).split("\n").length}, cột ${i - chuoi.lastIndexOf("\n", i - 1)}: kiểm tra dấu ngoặc, dấu phẩy, khóa trùng hoặc giá trị.`); };
  const cach = () => { while (/[\x20\t\r\n]/.test(chuoi[i] ?? "!") && i < chuoi.length) i++; };
  function chu() {
    const dau = i++;
    while (i < chuoi.length) {
      const c = chuoi[i++];
      if (c === "\\") i++;
      else if (c === '"') { try { return JSON.parse(chuoi.slice(dau, i)); } catch { loi(); } }
    }
    loi();
  }
  function giaTri(sau = 0) {
    if (sau > 64) loi();
    cach(); const c = chuoi[i];
    if (c === '"') return chu();
    if (c === "[" || c === "{") {
      const mang = c === "[", dong = mang ? "]" : "}", v = mang ? [] : Object.create(null);
      i++; cach(); if (chuoi[i] === dong) { i++; return v; }
      while (i < chuoi.length) {
        cach(); let k;
        if (!mang) { if (chuoi[i] !== '"') loi(); k = chu(); cach();
          if (Object.hasOwn(v, k) || chuoi[i++] !== ":") loi(); }
        const x = giaTri(sau + 1); if (mang) v.push(x); else v[k] = x;
        cach(); if (chuoi[i] === dong) { i++; return v; }
        if (chuoi[i++] !== ",") loi();
      }
      loi();
    }
    for (const [t, v] of [["true", true], ["false", false], ["null", null]]) {
      if (chuoi.startsWith(t, i)) { i += t.length; return v; }
    }
    const m = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(chuoi.slice(i));
    if (!m) loi(); i += m[0].length; return new SoJson(m[0]);
  }
  if (typeof chuoi !== "string") throw new Error("Giá trị phải là chuỗi JSON.");
  const v = giaTri(); cach(); if (i !== chuoi.length) loi(); return v;
}

export const MAU = {
  danh_muc_loai_json: [{ma: "thanh_toan_demo", ten: "Thanh toán DEMO", mo_ta: "Thanh toán nhà cung cấp DEMO"}],
  bo_phan_loai_json: {phien_ban: 1, quy_tac: [{loai: "thanh_toan_demo",
    khi: [{tat_ca: [["thanh toán", "=chi"], ["đợt #"]], khong_co: ["hủy"]}]}]},
  nguong_json: {pm: {so: "5000000000", tien_te: "VND"}, te: {so: "3000000000", tien_te: "VND"}, sad: {so: "250000000", tien_te: "VND"}},
  chinh_sach_json: CHINH_SACH,
  khuon_cot_json: {phien_ban: 1, sheet: null, cot: [
    {ma: "ma", tu_khoa: ["Mã"], bat_buoc: true}, {ma: "ngay", tu_khoa: ["Ngày"], bat_buoc: true},
    {ma: "so_tien", tu_khoa: ["Số tiền"], bat_buoc: true}, {ma: "tien_te", tu_khoa: ["Tiền tệ"], bat_buoc: false}], dong_dung: ["Cộng", "Tổng cộng"]},
};

export function docThamSo(thamSo, nangLuc) {
  if (!Object.hasOwn(NANG_LUC, nangLuc)) throw new Error("Năng lực chưa có trình soạn.");
  if (!thamSo || typeof thamSo !== "object" || Array.isArray(thamSo)) throw new Error("Cài đặt bước phải là một bộ tham số.");
  const mo = {goc: {...thamSo}, du_lieu: {}, da_doi: new Set(), loi_doc: {}};
  for (const k of NANG_LUC[nangLuc]) {
    const chuoi = thamSo[k] ?? "";
    if (chuoi === "") { mo.du_lieu[k] = null; continue; }
    try {
      if (typeof chuoi !== "string" || chuoi.length > TRAN[k] || new TextEncoder().encode(chuoi).length > TRAN[k])
        throw new Error(`Vượt trần ${TRAN[k].toLocaleString("vi-VN")} ký tự hoặc byte UTF-8; giảm số dòng hoặc độ dài nội dung.`);
      mo.du_lieu[k] = docJson(chuoi);
      if (mo.du_lieu[k] === null) throw new Error("Giá trị null không hợp lệ; dùng nút Bỏ thiết lập để để trống tham số.");
    } catch (e) { mo.loi_doc[k] = e.message; mo.du_lieu[k] = null; }
  }
  return mo;
}
export function doi(mo, k, v) { mo.du_lieu[k] = v; mo.da_doi.add(k); delete mo.loi_doc[k]; }
export function xuatThamSo(mo) {
  const ra = {...mo.goc};
  for (const k of mo.da_doi) ra[k] = mo.du_lieu[k] === null ? "" : vietJson(mo.du_lieu[k]);
  return ra;
}
const doiTuong = v => v !== null && typeof v === "object" && !Array.isArray(v) && !(v instanceof SoJson);
const dungKhoa = (v, khoa) => doiTuong(v) && Object.keys(v).length === khoa.length && khoa.every(k => Object.hasOwn(v, k));
const chu = v => typeof v === "string";
const khongRong = v => chu(v) && !!v.trim();
function soChuan(v) {
  if (!laSo(v)) return null;
  const m = /^(-?)(0|[1-9][0-9]*)(?:\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?$/.exec(chuSo(v));
  if (!m) return null;
  let so = (m[2] + (m[3] ?? "")).replace(/^0+/, ""), mu = BigInt(m[4] ?? 0) - BigInt((m[3] ?? "").length);
  if (!so) return {dau: 0, so: "0", mu: 0n};
  const gon = so.replace(/0+$/, ""); mu += BigInt(so.length - gon.length); so = gon;
  return {dau: m[1] ? -1 : 1, so, mu};
}
function soSanh(a, b) {
  const x = soChuan(a), y = soChuan(b); if (!x || !y) return NaN;
  if (x.dau !== y.dau) return Math.sign(x.dau - y.dau);
  if (!x.dau) return 0;
  const daiX = BigInt(x.so.length) + x.mu, daiY = BigInt(y.so.length) + y.mu;
  if (daiX !== daiY) return (daiX > daiY ? 1 : -1) * x.dau;
  const dai = Math.max(x.so.length, y.so.length), sx = x.so.padEnd(dai, "0"), sy = y.so.padEnd(dai, "0");
  return (sx === sy ? 0 : sx > sy ? 1 : -1) * x.dau;
}
export const chuan = v => String(v).normalize("NFD").replace(/\p{M}/gu, "").replace(/đ/g, "d").replace(/Đ/g, "D").toLowerCase().trim().replace(/\s+/g, " ");
// So chính xác số tiền cố định sáu chữ số lẻ bằng BigInt.
export function tienChinhXac(v) {
  if (!(chu(v) || laSo(v))) return null;
  if (laSo(v)) {
    const n = soChuan(v);
    if (!n || n.dau < 0 || n.mu < -6n || BigInt(n.so.length) + n.mu > 18n) return null;
    return BigInt(n.so) * 10n ** (n.mu + 6n);
  }
  const s = chuSo(v), m = /^([0-9]+)(?:\.([0-9]+))?$/.exec(s);
  if (!m || m[1].replace(/^0+/, "").length > 18 || (m[2] ?? "").replace(/0+$/, "").length > 6) return null;
  return BigInt(m[1]) * 1000000n + BigInt((m[2] ?? "").slice(0, 6).padEnd(6, "0"));
}
export function hienTien(v, tienTe) {
  const n = tienChinhXac(v); if (n === null) return "Chưa có số tiền hợp lệ";
  const nguyen = n / 1000000n, le = (n % 1000000n).toString().padStart(6, "0").replace(/0+$/, "");
  return nguyen.toLocaleString("vi-VN") + (le ? "," + le : "") + " " + tienTe;
}

export function kiemThamSo(mo, nangLuc) {
  const ds = [], them = (k, d, cau) => ds.push({truong: k, duong_dan: d, thong_diep: cau});
  for (const k of NANG_LUC[nangLuc]) {
    if (mo.loi_doc[k]) { them(k, [], mo.loi_doc[k]); continue; }
    const v = mo.du_lieu[k]; if (v === null) continue;
    const bao = (d, cau) => them(k, d, cau);
    const nguyen = x => { const n = soChuan(x); return !!n && n.mu >= 0n; };
    const phienBan1 = x => x === 1 || x instanceof SoJson && x.chuoi === "1";
    const trongTyLe = x => soSanh(x, 0) >= 0 && soSanh(x, 1) <= 0;
    if (k === "danh_muc_loai_json") {
      if (!Array.isArray(v) || v.length > 100) { bao([], "Danh mục phải là danh sách, tối đa 100 loại."); continue; }
      const ma = new Set();
      v.forEach((r, i) => {
        if (!dungKhoa(r, ["ma", "ten", "mo_ta"])) { bao([i], "Mỗi loại cần đúng ba trường: mã, tên và mô tả."); return; }
        if (!chu(r.ma) || !/^[a-z][a-z0-9_]{0,39}$/.test(r.ma) || r.ma === "chua_phan_loai" || ma.has(r.ma))
          bao([i, "ma"], "Mã cần bắt đầu bằng chữ thường, tối đa 40 chữ/số/gạch dưới, không trùng và không dùng mã dành riêng chua_phan_loai.");
        ma.add(r.ma);
        if (!khongRong(r.ten)) bao([i, "ten"], "Nhập tên loại nghiệp vụ.");
        if (!chu(r.mo_ta)) bao([i, "mo_ta"], "Mô tả cần là văn bản; có thể để trống.");
      });
    } else if (k === "bo_phan_loai_json") {
      if (!dungKhoa(v, ["phien_ban", "quy_tac"]) || !phienBan1(v.phien_ban) || !Array.isArray(v.quy_tac)) {
        bao([], "Bộ phân loại cần phiên bản 1 và danh sách quy tắc."); continue;
      }
      const loai = new Set((Array.isArray(mo.du_lieu.danh_muc_loai_json) ? mo.du_lieu.danh_muc_loai_json : []).map(r => r?.ma));
      v.quy_tac.forEach((r, i) => {
        if (!dungKhoa(r, ["loai", "khi"])) { bao(["quy_tac", i], "Quy tắc cần loại và các điều kiện khi."); return; }
        if (!loai.has(r.loai)) bao(["quy_tac", i, "loai"], "Chọn một loại đã có trong danh mục.");
        if (!Array.isArray(r.khi) || !r.khi.length) { bao(["quy_tac", i, "khi"], "Thêm ít nhất một điều kiện khớp."); return; }
        let dem = 0;
        r.khi.forEach((dk, j) => {
          const d = ["quy_tac", i, "khi", j];
          if (!doiTuong(dk) || !Object.hasOwn(dk, "tat_ca") || Object.keys(dk).some(x => !["tat_ca", "khong_co"].includes(x)) ||
            !Array.isArray(dk.tat_ca) || !dk.tat_ca.length || dk.tat_ca.some(n => !Array.isArray(n) || !n.length) ||
            !Array.isArray(dk.khong_co ?? [])) { bao(d, "Điều kiện cần ít nhất một nhóm từ khóa bắt buộc; loại trừ là danh sách."); return; }
          for (const tu of [...dk.tat_ca.flat(), ...(dk.khong_co ?? [])]) {
            dem++;
            if (!khongRong(tu) || !chuan(tu.trim().startsWith("=") ? tu.trim().slice(1) : tu)) bao(d, "Từ khóa không được rỗng hoặc chỉ có dấu =.");
          }
        });
        if (dem > 200) bao(["quy_tac", i], "Mỗi quy tắc tối đa 200 từ khóa, tính cả loại trừ.");
      });
    } else if (k === "nguong_json") {
      if (!doiTuong(v)) { bao([], "Ngưỡng cần các khối PM, TE và SAD."); continue; }
      const tien = [], te = [];
      for (const ten of ["pm", "te", "sad"]) {
        const r = v[ten];
        if (!doiTuong(r)) { bao([ten, "so"], "Nhập số tiền và tiền tệ cho ngưỡng này."); tien.push(null); te.push(null); continue; }
        const n = tienChinhXac(r.so); tien.push(n); te.push(r.tien_te);
        if (n === null || n <= 0n) bao([ten, "so"], "Nhập số dương, tối đa 18 chữ số nguyên và 6 chữ số lẻ; dùng dấu chấm cho phần lẻ.");
        if (!chu(r.tien_te) || !/^[A-Z]{3}$/.test(r.tien_te)) bao([ten, "tien_te"], "Tiền tệ gồm đúng 3 chữ in hoa, ví dụ VND.");
      }
      if (te.some(x => x !== te[0])) bao(["te", "tien_te"], "PM, TE và SAD phải dùng cùng tiền tệ.");
      if (tien.every(x => x !== null) && !(0n < tien[2] && tien[2] < tien[1] && tien[1] <= tien[0])) bao(["sad", "so"], "Cần thỏa mãn 0 < SAD < TE ≤ PM.");
    } else if (k === "chinh_sach_json") {
      if (!doiTuong(v) || Object.keys(v).some(x => !Object.hasOwn(CHINH_SACH, x))) { bao([], "Chính sách có trường không được hỗ trợ."); continue; }
      const cs = {...CHINH_SACH, ...v};
      for (const ten of ["bac", "nguong_xuong", "mau_toi_thieu"]) if (!Array.isArray(cs[ten])) bao([ten], "Giá trị phải là danh sách số.");
      if (!["bac", "nguong_xuong", "mau_toi_thieu"].every(x => Array.isArray(cs[x]))) continue;
      if (!cs.bac.length || cs.bac.some(x => !(soSanh(x, 0) > 0 && soSanh(x, 1) <= 0)) || cs.bac.some((x, i) => i > 0 && soSanh(cs.bac[i - 1], x) <= 0)) bao(["bac"], "Các bậc cần giảm dần, mỗi bậc lớn hơn 0 và không quá 100%.");
      if (cs.nguong_xuong.length !== cs.bac.length - 1 || cs.mau_toi_thieu.length !== cs.bac.length - 1) bao(["bac"], "Số ngưỡng xuống bậc và số mẫu tối thiểu cần ít hơn số bậc đúng một dòng.");
      for (const ten of ["ty_le_chua_phan_loai", "nguong_diem_rui_ro", "ty_le_duoi_sad", "san"])
        if (!trongTyLe(cs[ten])) bao([ten], "Nhập tỷ lệ từ 0% đến 100%.");
      if (cs.nguong_xuong.some(x => !trongTyLe(x))) bao(["nguong_xuong"], "Ngưỡng xuống bậc từ 0% đến 100%.");
      for (const ten of ["mau_sach_toan_bo", "don_vi_so_tron", "toi_thieu_ho_so_doi_tac_moi"])
        if (!nguyen(cs[ten]) || !(soSanh(cs[ten], ten === "toi_thieu_ho_so_doi_tac_moi" ? 0 : 1) >= 0)) bao([ten], "Nhập số nguyên lớn hơn 0 (hồ sơ đối tác mới có thể bằng 0).");
      if (cs.mau_toi_thieu.some(x => !nguyen(x) || !(soSanh(x, 0) > 0))) bao(["mau_toi_thieu"], "Số mẫu tối thiểu cần là số nguyên dương.");
      if (!(soSanh(cs.do_tin_cay, 0) > 0 && soSanh(cs.do_tin_cay, 1) < 0)) bao(["do_tin_cay"], "Độ tin cậy phải lớn hơn 0% và nhỏ hơn 100%.");
      if (!doiTuong(cs.he_so) || Object.keys(cs.he_so).some(x => !Object.hasOwn(CO, x)) || Object.values(cs.he_so).some(x => !(soSanh(x, 1) >= 0))) bao(["he_so"], "Mỗi hệ số cần là số từ 1 trở lên và thuộc cờ đã hỗ trợ.");
    } else if (k === "khuon_cot_json") {
      if (!dungKhoa(v, ["phien_ban", "sheet", "cot", "dong_dung"]) || !phienBan1(v.phien_ban) ||
        !(v.sheet === null || khongRong(v.sheet)) || !Array.isArray(v.cot) || !v.cot.length || v.cot.length > 30 || !Array.isArray(v.dong_dung)) {
        bao([], "Khuôn cần phiên bản 1, sheet (trống để tự dò), 1–30 cột và danh sách dòng dừng."); continue;
      }
      const ma = new Set(), batBuoc = new Set(); let tu = [...v.dong_dung];
      v.cot.forEach((r, i) => {
        if (!dungKhoa(r, ["ma", "tu_khoa", "bat_buoc"])) { bao(["cot", i], "Mỗi cột cần trường, danh sách tiêu đề và cờ bắt buộc."); return; }
        if (!chu(r.ma) || !(Object.hasOwn(COT, r.ma) || r.ma.startsWith("thuoc_tinh.") && r.ma.length > 11) || ma.has(r.ma)) bao(["cot", i, "ma"], "Chọn trường không trùng, hoặc nhập thuộc tính bổ sung.");
        ma.add(r.ma); if (r.bat_buoc === true) batBuoc.add(r.ma);
        if (typeof r.bat_buoc !== "boolean") bao(["cot", i, "bat_buoc"], "Cờ bắt buộc cần bật hoặc tắt.");
        if (!Array.isArray(r.tu_khoa) || !r.tu_khoa.length) bao(["cot", i, "tu_khoa"], "Nhập ít nhất một tên tiêu đề cho cột.");
        else tu.push(...r.tu_khoa);
      });
      if (["ma", "ngay", "so_tien"].some(x => !batBuoc.has(x))) bao(["cot"], "Cần đủ ba cột bắt buộc: mã nghiệp vụ, ngày nghiệp vụ, số tiền.");
      if (tu.length > 200 || tu.some(x => !khongRong(x) || !chuan(x))) bao([], "Tối đa 200 từ khóa gồm tên tiêu đề và dòng dừng; không để từ khóa rỗng.");
    }
    try { const s = mo.da_doi.has(k) ? vietJson(v) : mo.goc[k];
      if (s.length > TRAN[k] || new TextEncoder().encode(s).length > TRAN[k]) bao([], `Vượt trần ${TRAN[k].toLocaleString("vi-VN")} ký tự hoặc byte UTF-8; giảm số dòng hoặc nội dung.`);
    } catch { bao([], "Có ô số chưa hợp lệ. Kiểm tra các trường đang đánh dấu."); }
  }
  return ds;
}
