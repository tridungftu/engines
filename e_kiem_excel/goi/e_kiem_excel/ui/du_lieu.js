// Cùng cấu trúc và trần với bo_nhom.py, doc_tong_quat.py, kiem_tra.py.
export const VUNG = {tieu_de_cot: "Tiêu đề cột", ten_sheet: "Tên sheet", nhan_dong: "Nhãn dòng"};
export const KIEU = {van_ban: "Văn bản", so: "Số", so_tien: "Số tiền (kèm tiền tệ)", ngay: "Ngày"};
export const MAU = {
  nhan_o_dich_json: ["=tổng cộng", "giá trị đề nghị"],
  bo_nhom_json: {phien_ban: 1, ten_bo: "Nhóm DEMO", nhom: [{ma: "don_gia", ten: "Đơn giá DEMO",
    tai_lieu: "Bảng giá DEMO", khi: [{vung: ["tieu_de_cot"], tat_ca: [["đơn giá", "giá đợt #"]], khong_co: ["tạm tính"]}]}]},
  khuon_cot_json: {phien_ban: 1, cot: [
    {ma: "ma_hang", tu_khoa: ["=mã hàng"], kieu: "van_ban", bat_buoc: true},
    {ma: "don_gia", tu_khoa: ["đơn giá", "giá đợt #"], kieu: "so_tien", bat_buoc: true}
  ], dong_dung: ["=tổng cộng"]}
};
export const sao = v => structuredClone(v);
const byte = s => new TextEncoder().encode(s).length;
const chu = v => typeof v === "string" && !!v.trim() && !/[\uD800-\uDFFF]/u.test(v);
const obj = v => v !== null && typeof v === "object" && !Array.isArray(v);

// JSON.parse chỉ dùng sau khi quét khóa trùng; không sửa ngầm JSON đã lưu.
export function docJson(raw) {
  const v = JSON.parse(raw);
  const tokens = raw.match(/"(?:[^"\\]|\\.)*"|[{}\[\]:,]|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null/g) || [];
  let i = 0;
  function quet() {
    const t = tokens[i++];
    if (t === "{") {
      const keys = new Set();
      while (tokens[i] !== "}") {
        const key = JSON.parse(tokens[i++]);
        if (keys.has(key)) throw Error("Khóa JSON bị trùng; cần giữ đúng một giá trị cho mỗi trường.");
        keys.add(key); i++; quet();
        if (tokens[i] !== ",") break;
        i++;
      }
      i++;
    } else if (t === "[") {
      while (tokens[i] !== "]") {
        quet(); if (tokens[i] !== ",") break; i++;
      }
      i++;
    }
  }
  quet();
  return v;
}

export function kiemJson(ma, d) {
  const loi = [];
  const bao = (p, cau) => loi.push({truong: p, cau});
  function khoa(v, p, batBuoc, tuyChon = []) {
    if (!obj(v)) { bao(p, "Cần một cấu trúc có các trường theo hướng dẫn."); return false; }
    for (const k of batBuoc) if (!Object.hasOwn(v, k)) bao(`${p}.${k}`, "Thiếu trường bắt buộc.");
    for (const k of Object.keys(v)) if (![...batBuoc, ...tuyChon].includes(k)) bao(p, "Có trường ngoài cấu trúc hỗ trợ; không thể bỏ qua khi lưu.");
    return true;
  }
  let dem = 0;
  function tu(ds, p, can = true) {
    if (!Array.isArray(ds) || can && !ds.length) { bao(p, "Cần ít nhất một từ khóa."); return; }
    ds.forEach((t, i) => {
      dem++;
      if (!chu(t) || t.trim() === "=") bao(`${p}.${i}`, "Nhập từ khóa; dấu = cần có cụm từ theo sau.");
    });
  }
  const p = ma;
  if (ma === "nhan_o_dich_json") tu(d, p);
  else if (ma === "bo_nhom_json") {
    if (!khoa(d, p, ["phien_ban", "ten_bo", "nhom"])) return loi;
    if (d.phien_ban !== 1) bao(p, "Chỉ hỗ trợ phiên bản bộ nhóm 1.");
    if (!chu(d.ten_bo)) bao(`${p}.ten_bo`, "Nhập tên bộ nhóm.");
    if (!Array.isArray(d.nhom) || !d.nhom.length || d.nhom.length > 30) bao(p, "Bộ nhóm cần từ 1 đến 30 nhóm.");
    const mas = new Set(), tens = new Set();
    (Array.isArray(d.nhom) ? d.nhom : []).forEach((n, i) => {
      const q = `${p}.nhom.${i}`;
      if (!khoa(n, q, ["ma", "ten", "tai_lieu", "khi"])) return;
      for (const k of ["ma", "ten", "tai_lieu"]) if (!chu(n[k])) bao(`${q}.${k}`, "Trường này cần có nội dung.");
      if (mas.has(n.ma)) bao(`${q}.ma`, "Mã nhóm đã có; cần dùng mã khác.");
      if (tens.has(n.ten) || ["Chưa phân nhóm", "Ngoài nhóm — cần giải thích"].includes(n.ten)) bao(`${q}.ten`, "Tên nhóm trùng hoặc là tên dành riêng; cần dùng tên khác.");
      mas.add(n.ma); tens.add(n.ten);
      if (!Array.isArray(n.khi) || !n.khi.length) bao(`${q}.khi`, "Cần ít nhất một điều kiện nhận diện.");
      (Array.isArray(n.khi) ? n.khi : []).forEach((dk, j) => {
        const r = `${q}.khi.${j}`;
        if (!khoa(dk, r, ["vung", "tat_ca"], ["khong_co"])) return;
        if (!Array.isArray(dk.vung) || !dk.vung.length || dk.vung.some(v => typeof v !== 'string' || !Object.hasOwn(VUNG, v)) || new Set(dk.vung).size !== dk.vung.length) bao(`${r}.vung`, "Chọn ít nhất một vùng, mỗi vùng một lần.");
        if (!Array.isArray(dk.tat_ca) || !dk.tat_ca.length) bao(`${r}.tat_ca`, "Cần ít nhất một cụm từ khóa bắt buộc.");
        (Array.isArray(dk.tat_ca) ? dk.tat_ca : []).forEach((a, k) => tu(a, `${r}.tat_ca.${k}`));
        if (Object.hasOwn(dk, "khong_co")) tu(dk.khong_co, `${r}.khong_co`, false);
      });
    });
  } else if (ma === "khuon_cot_json") {
    if (!khoa(d, p, ["phien_ban", "cot", "dong_dung"])) return loi;
    if (d.phien_ban !== 1) bao(p, "Chỉ hỗ trợ phiên bản khuôn cột 1.");
    if (!Array.isArray(d.cot) || !d.cot.length || d.cot.length > 30) bao(p, "Khuôn cần từ 1 đến 30 cột.");
    const mas = new Set();
    (Array.isArray(d.cot) ? d.cot : []).forEach((c, i) => {
      const q = `${p}.cot.${i}`;
      if (!khoa(c, q, ["ma", "tu_khoa", "bat_buoc", "kieu"])) return;
      if (typeof c.ma !== "string" || c.ma.trim() !== c.ma || !/^[a-z][a-z0-9_]{0,63}$/.test(c.ma) || mas.has(c.ma)) bao(`${q}.ma`, "Mã cột không trùng, bắt đầu a–z; dùng chữ thường, số, gạch dưới, tối đa 64 ký tự.");
      mas.add(c.ma); tu(c.tu_khoa, `${q}.tu_khoa`);
      if (typeof c.kieu !== 'string' || !Object.hasOwn(KIEU, c.kieu)) bao(`${q}.kieu`, "Chọn văn bản, số, số tiền hoặc ngày.");
      if (typeof c.bat_buoc !== "boolean") bao(`${q}.bat_buoc`, "Bắt buộc phải là công tắc bật hoặc tắt.");
    });
    if (Array.isArray(d.cot) && !d.cot.some(c => c?.bat_buoc === true)) bao(p, "Cần ít nhất một cột bắt buộc.");
    tu(d.dong_dung, `${p}.dong_dung`, false);
  } else bao(p, "Tham số chưa được hỗ trợ.");
  if (ma !== "nhan_o_dich_json" && dem > 200) bao(p, "Tổng từ khóa vượt 200; cần giảm số từ khóa.");
  const raw = JSON.stringify(d);
  if (byte(raw) > (ma === "nhan_o_dich_json" ? 4096 : 32768)) bao(p, "Nội dung vượt giới hạn UTF-8; cần giảm nội dung.");
  return loi;
}

export function tachODich(raw) {
  const m = /^(?<sh>'(?:[^']|'')+'|[^'!]+)!\$?(?<c>[A-Za-z]{1,3})\$?(?<r>[1-9][0-9]{0,6})$/.exec(raw);
  if (!m || m[0] !== raw) return null;
  let sheet = m.groups.sh;
  if (sheet.startsWith("'")) sheet = sheet.slice(1, -1).replaceAll("''", "'");
  const col = m.groups.c.toUpperCase();
  const n = [...col].reduce((a, c) => a * 26 + c.charCodeAt(0) - 64, 0);
  if (n > 16384 || +m.groups.r > 1048576 || [...raw].length > 512) return null;
  return {sheet, o: col + m.groups.r};
}
export function ghepODich(sheet, o) {
  return `'${sheet.replaceAll("'", "''")}'!${o}`;
}
export function kiemThamSo(nangLuc, ts, sheets = []) {
  const loi = [];
  const them = (truong, cau) => loi.push({truong, cau});
  const cacMa = nangLuc === "excel.toan_ven@1" ? ["nhan_o_dich_json", "bo_nhom_json"] : ["khuon_cot_json"];
  for (const ma of cacMa) {
    const raw = ts[ma] ?? "";
    if (typeof raw !== "string") { them(ma, "Tham số cần là chuỗi JSON."); continue; }
    if (!raw) continue;
    if (byte(raw) > (ma === "nhan_o_dich_json" ? 4096 : 32768)) { them(ma, "Nội dung vượt giới hạn UTF-8; cần giảm nội dung."); continue; }
    try { loi.push(...kiemJson(ma, docJson(raw))); }
    catch { them(ma, "Không đọc được JSON hoặc có khóa trùng; cần sửa nguồn cài đặt hoặc chèn mẫu thay thế."); }
  }
  if (nangLuc === "excel.toan_ven@1") {
    const raw = ts.o_dich ?? "";
    const dich = typeof raw === "string" && tachODich(raw);
    if (raw !== '' && !dich) them("o_dich", "Chọn sheet và nhập ô từ A1 đến XFD1048576.");
    else if (dich && sheets.length && !sheets.includes(dich.sheet)) them("o_dich", "Sheet không có trong danh sách của tệp đã chọn.");
    if (ts.kiem_nguon_kl !== undefined && typeof ts.kiem_nguon_kl !== "boolean") them("kiem_nguon_kl", "Cần một công tắc bật hoặc tắt.");
  } else if (nangLuc === "excel.doc_bang@1") {
    if (!["tong_quat", "xay_dung_klgt"].includes(ts.khuon)) them("khuon", "Chọn khuôn đọc bảng.");
    if (ts.khuon === "tong_quat" && !ts.khuon_cot_json) them("khuon_cot_json", "Khuôn tổng quát cần ít nhất một cột bắt buộc.");
    if (typeof ts.tien_te !== "string" || ts.tien_te && (ts.tien_te.length !== 3 || !/^[A-Z]{3}$/.test(ts.tien_te))) them("tien_te", "Để trống hoặc nhập 3 chữ in hoa, ví dụ VND, USD.");
  } else them("nang_luc", "Năng lực chưa được trình soạn hỗ trợ.");
  return loi;
}
