// TS-DC: trình soạn thuần; cửa D2 do Core cấp, không tự cất dữ liệu.
export const QUY_TAC = [
  ["DC_CHU_SO", "Chữ số"], ["DC_NGAY_THOI_HAN", "Ngày và thời hạn"],
  ["DC_TIEN_TY_LE", "Tiền và tỷ lệ"], ["DC_TIEN_CHU", "Tiền bằng chữ"],
  ["DC_DINH_DANH", "Thông tin định danh"], ["DC_CAU_TRUC", "Cấu trúc điều khoản"],
  ["DC_PHU_DINH_BAT_BUOC", "Phủ định và nghĩa vụ"], ["DC_OCR_NHAM", "Ký tự OCR dễ nhầm"],
];
export const CAP_DOI_NGHIA = [["thuê", "thuế"], ["lãi", "lại"], ["phạt", "phát"],
  ["bán", "bàn"], ["không", "khống"], ["hạn", "hàn"]];
export const VUNG = {ben_ky: "Bên ký", nguoi_dai_dien: "Người đại diện", chuc_vu: "Chức vụ",
  mst: "Mã số thuế", stk: "Số tài khoản", dia_chi: "Địa chỉ", so_hop_dong: "Số hợp đồng"};
const laObj = v => v !== null && typeof v === "object" && !Array.isArray(v);
const chuan = s => s.normalize("NFC").toLocaleLowerCase("vi").trim().replace(/\s+/gu, " ");
const loi = (truong, thongDiep) => {throw Object.assign(new Error(thongDiep), {truong});};
const dungKhoa = (v, keys, p) => {
  if (!laObj(v) || Object.keys(v).sort().join("|") !== [...keys].sort().join("|"))
    loi(p, "Cấu trúc chưa đúng. Cần đủ các trường được mô tả trong hướng dẫn.");
};
const chuoi = (v, max) => typeof v === "string" && v.trim() && [...v].length <= max;
const bamDung = s => typeof s === "string" && /^sha256:[0-9a-f]{64}$/i.test(s);

// Không để JSON.parse bỏ ngầm khóa trùng; cùng giới hạn cây sâu của lõi.
export function docJson(text) {
  if (typeof text !== "string" || [...text].length > 65536 || new TextEncoder().encode(text).length > 65536)
    loi("bo_quy_tac_json", "Bộ quy tắc tối đa 65.536 ký tự và 65.536 byte UTF-8. Cần giảm nội dung.");
  let i = 0;
  const cach = () => {while (/[\x20\t\r\n]/.test(text[i] || "x")) i++;};
  function tokenChuoi() {
    const start = i++;
    while (i < text.length) {const c = text[i++]; if (c === "\\") i++; else if (c === '"') break;}
    const v = JSON.parse(text.slice(start, i));
    if (/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(v)) throw Error();
    return v;
  }
  function value(depth) {
    cach(); if (depth > 64) loi("bo_quy_tac_json", "Bộ quy tắc lồng quá 64 cấp. Cần giảm số cấp.");
    if (text[i] === '"') {tokenChuoi(); return;}
    if (text[i] === "{" || text[i] === "[") {
      const obj = text[i++] === "{", end = obj ? "}" : "]", keys = new Set(); cach();
      if (text[i] === end) {i++; return;}
      while (i < text.length) {
        if (obj) {
          cach(); if (text[i] !== '"') throw Error();
          const k = tokenChuoi(); if (keys.has(k)) loi("bo_quy_tac_json", "Có trường trùng tên. Cần giữ đúng một trường cho mỗi tên.");
          keys.add(k); cach(); if (text[i++] !== ":") throw Error();
        }
        value(depth + 1); cach(); const c = text[i++]; if (c === end) return; if (c !== ",") throw Error();
      }
      throw Error();
    }
    const start = i; while (i < text.length && !/[\x20\t\r\n,\]}]/.test(text[i])) i++;
    const v = JSON.parse(text.slice(start, i));
    if (typeof v === "number" && (!Number.isFinite(v) || Number.isInteger(v) && !Number.isSafeInteger(v)))
      loi("bo_quy_tac_json", "Có số vượt độ chính xác của trình soạn. Cần giữ bộ gốc và kiểm lại nguồn trước khi sửa.");
  }
  try {value(0); cach(); if (i !== text.length) throw Error(); return JSON.parse(text);}
  catch (e) {if (e.truong) throw e; loi("bo_quy_tac_json", "Bộ quy tắc chưa đọc được: kiểm dấu ngoặc, dấu phẩy và kiểu dữ liệu trong nguồn đã chọn.");}
}

export function kiemBo(bo) {
  if (!laObj(bo) || bo.phien_ban !== 1 || !chuoi(bo.phien_ban_bo, 1000) || !chuoi(bo.ma_bo_chuan_hoa, 1000) || !laObj(bo.chuan_hoa))
    loi("bo_quy_tac_json", "Cần bộ phiên bản 1 có mã bộ, phiên bản bộ và phần chuẩn hóa đã được duyệt.");
  const luaChon = {unicode: ["NFC"], khoang_trang: ["gop", "giu_nguyen"], dau_nhay: ["thang", "giu_nguyen"],
    gach_noi: ["thong_nhat", "giu_nguyen"], ngat_dong: ["noi_trong_doan", "giu_nguyen"],
    ngat_tu_cuoi_dong: ["chi_gach_noi_mem", "giu_nguyen"]};
  const ch = bo.chuan_hoa;
  dungKhoa(ch, [...Object.keys(luaChon), "dau_chan_trang", "bo_so_trang"], "chuan_hoa");
  if (Object.entries(luaChon).some(([k, options]) => !options.includes(ch[k])) || typeof ch.bo_so_trang !== "boolean" ||
      !Array.isArray(ch.dau_chan_trang) || ch.dau_chan_trang.length > 100 ||
      ch.dau_chan_trang.some(s => typeof s !== "string" || [...s].length < 1 || [...s].length > 1000))
    loi("chuan_hoa", "Phần chuẩn hóa chưa hợp lệ. Cần chọn lại bộ đã duyệt, không tự sửa các trường chuẩn hóa tại bước so.");
  const q = bo.quy_tac_cung;
  if (q === undefined) return bo; // Bộ cũ vẫn được lõi nhận, không tự thêm mặc định.
  dungKhoa(q, ["phien_ban", "dinh_dang_so", "don_vi_tien", "dinh_dang_ngay", "vung_bao_ve"], "quy_tac_cung");
  if (q.phien_ban !== 1) loi("quy_tac_cung", "Phiên bản quy tắc cứng phải là 1.");
  if (!Array.isArray(q.dinh_dang_so) || q.dinh_dang_so.length > 10) loi("dinh_dang_so", "Tối đa 10 định dạng số.");
  q.dinh_dang_so.forEach((f, n) => {
    const p = `dinh_dang_so.${n}`; dungKhoa(f, ["nghin", "thap_phan"], p);
    if (![null, ".", ",", " "].includes(f.nghin) || ![null, ".", ","].includes(f.thap_phan) || f.nghin !== null && f.nghin === f.thap_phan)
      loi(p, `Định dạng số dòng ${n + 1}: dấu hàng nghìn và thập phân phải khác nhau.`);
  });
  if (!laObj(q.don_vi_tien) || Object.keys(q.don_vi_tien).length > 100) loi("don_vi_tien", "Tối đa 100 cách ghi tiền.");
  const daCo = new Set();
  Object.entries(q.don_vi_tien).forEach(([ten, ma], n) => {
    if (!chuoi(ten, 100) || typeof ma !== "string" || !/^[A-Z]{3}$/.test(ma) || daCo.has(chuan(ten)) ||
      /^[A-Z]{3}$/.test(ten) && ten !== ma || ["đồng", "vnđ"].includes(chuan(ten)) && ma !== "VND")
      loi(`don_vi_tien.${n}`, `Cách ghi tiền dòng ${n + 1}: nhập tên không trùng và mã tiền tệ 3 chữ hoa đúng nghĩa (đồng là VND).`);
    daCo.add(chuan(ten));
  });
  if (!Array.isArray(q.dinh_dang_ngay) || !q.dinh_dang_ngay.length || q.dinh_dang_ngay.length > 3 ||
      q.dinh_dang_ngay.some(v => !["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"].includes(v)))
    loi("dinh_dang_ngay", "Chọn ít nhất một và tối đa ba định dạng ngày.");
  if (!Array.isArray(q.vung_bao_ve) || q.vung_bao_ve.length > 1000) loi("vung_bao_ve", "Tối đa 1.000 vùng bảo vệ.");
  q.vung_bao_ve.forEach((v, n) => {
    const p = `vung_bao_ve.${n}`;
    dungKhoa(v, ["ben", "loai", "bat_dau", "ket_thuc", "nguyen_van", "bam_van_ban"], p);
    if (!["word", "ban_ky"].includes(v.ben)) loi(p + ".ben", `Vùng dòng ${n + 1}: chọn bản Word hoặc bản ký.`);
    if (!Object.hasOwn(VUNG, v.loai)) loi(p + ".loai", `Vùng dòng ${n + 1}: chọn loại thông tin cần bảo vệ.`);
    if (!Number.isSafeInteger(v.bat_dau) || !Number.isSafeInteger(v.ket_thuc) || v.bat_dau < 0 || v.bat_dau >= v.ket_thuc || v.ket_thuc > 500000)
      loi(p + ".bat_dau", `Vùng dòng ${n + 1}: vị trí đầu/cuối là số nguyên, 0 ≤ đầu < cuối ≤ 500.000.`);
    if (!chuoi(v.nguyen_van, 65536)) loi(p + ".nguyen_van", `Vùng dòng ${n + 1}: cần nguyên văn không rỗng.`);
    if (!bamDung(v.bam_van_ban)) loi(p + ".bam_van_ban", `Vùng dòng ${n + 1}: cần băm toàn văn gồm sha256: và 64 ký tự hex.`);
  });
  return bo;
}

export async function xuatThamSo(text) {
  kiemBo(docJson(text));
  const bytes = new TextEncoder().encode(text);
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return {bo_quy_tac_json: text, bam_bo_quy_tac: "sha256:" + [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, "0")).join("")};
}

export default async function soanQuyTac(goc, KttCore = globalThis.KttCore, {cua} = {}) {
  // KttCore chưa có cửa D2. Host truyền cua; không mượn cấu hình engine để lưu tham số bước.
  KttCore.engine("e_doi_chieu");
  const doc = goc.ownerDocument;
  const tao = (the, text, cha = goc) => {const e = doc.createElement(the); if (text !== undefined) e.textContent = text; cha.appendChild(e); return e;};
  goc.replaceChildren(); goc.classList.add("dc-soan-quy-tac");
  tao("style").textContent = `.dc-soan-quy-tac{font:16px/1.5 'Segoe UI',sans-serif;color:#243e50;max-width:1100px;margin:auto}
    .dc-soan-quy-tac *{box-sizing:border-box}.dc-soan-quy-tac section{background:#fff;border:1px solid #d8e1eb;border-radius:12px;margin:18px 0;padding:24px 28px}
    .dc-soan-quy-tac header{display:flex;justify-content:space-between;gap:16px;align-items:center}.dc-soan-quy-tac h2{margin:0;font-size:24px}.dc-soan-quy-tac h3{margin:0 0 12px;font-size:19px}
    .dc-soan-quy-tac p{max-width:78ch;color:#62758b}.dc-soan-quy-tac .dc-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px 26px}
    .dc-soan-quy-tac label{display:flex;flex-direction:column;gap:6px;min-width:0}.dc-soan-quy-tac small{color:#62758b;font-size:13px}
    .dc-soan-quy-tac input,.dc-soan-quy-tac select{font:inherit;width:100%;min-width:0;padding:10px;border:1px solid #cad7e5;border-radius:7px;background:white;color:#243e50}
    .dc-soan-quy-tac button{font:inherit;border:1px solid #cad7e5;border-radius:7px;background:#fff;color:#244765;padding:10px 16px;cursor:pointer;margin:10px 10px 0 0}
    .dc-soan-quy-tac button:disabled{opacity:.55;cursor:default}.dc-soan-quy-tac .dc-primary{background:#215e92;color:white;border-color:#215e92}
    .dc-soan-quy-tac .dc-badge{padding:7px 12px;background:#edf7f0;border:1px solid #cce6d7;border-radius:6px;white-space:nowrap;color:#146c61}
    .dc-soan-quy-tac .dc-warning{background:#fff7e6;border:1px solid #f0d59f;padding:14px 18px;border-radius:8px;color:#8a590e}
    .dc-soan-quy-tac fieldset{border:1px solid #d8e1eb;border-radius:8px;margin:14px 0;padding:16px;min-width:0}
    .dc-soan-quy-tac [role=alert],.dc-soan-quy-tac .dc-error{color:#a32424}.dc-soan-quy-tac .dc-error:empty{display:none}
    .dc-soan-quy-tac pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6fa;padding:16px;font-size:13px}
    .dc-soan-quy-tac summary{cursor:pointer;font-weight:600}.dc-soan-quy-tac :focus-visible{outline:3px solid #2879b6;outline-offset:2px}
    @media(max-width:650px){.dc-soan-quy-tac .dc-grid{grid-template-columns:1fr}.dc-soan-quy-tac section{padding:18px}.dc-soan-quy-tac header{align-items:flex-start;flex-direction:column}}`;
  const top = tao("section"), header = tao("header", undefined, top);
  tao("h2", "☷ Bộ quy tắc đối chiếu", header);
  const badge = tao("span", "Đang đọc…", header); badge.classList.add("dc-badge");
  tao("p", "Cài đặt bước so văn bản. Quy tắc cứng luôn bật; không có tùy chọn hạ mức bảo vệ.", top);
  tao("p", "Sau khi sửa bộ, cần ghim lại cùng nội dung tại bước nhận cặp trước khi chạy quy trình.", top).classList.add("dc-warning");
  const rules = tao("section"); tao("h3", "Quy tắc cứng luôn áp dụng", rules);
  const list = tao("div", undefined, rules); list.classList.add("dc-grid");
  for (const [, ten] of QUY_TAC) tao("div", "✓ " + ten, list);
  const pairs = tao("section"); tao("h3", "Cặp đổi nghĩa được bảo vệ", pairs);
  tao("p", "Danh sách cố định của bộ xử lý; không thể thêm, xóa hoặc coi là lỗi OCR vô nghĩa từ cài đặt bước.", pairs);
  const pairGrid = tao("div", undefined, pairs); pairGrid.classList.add("dc-grid");
  for (const [a, b] of CAP_DOI_NGHIA) tao("div", `${a} / ${b}`, pairGrid);
  const editor = tao("section"); tao("h3", "Vùng bảo vệ bổ sung", editor);
  tao("p", "Thêm thông tin cần bảo vệ trong nguồn đã ghim. Bỏ trống danh sách vẫn giữ nhận diện tự động và mọi quy tắc cứng.", editor);
  const rows = tao("div", undefined, editor);
  const add = tao("button", "Thêm vùng bảo vệ", editor); add.type = "button";
  const advanced = tao("details", undefined, tao("section")); tao("summary", "Nâng cao · định dạng và dữ liệu bộ", advanced);
  tao("p", "Định dạng số, cách ghi tiền và ngày lấy từ bộ đã duyệt; mã, băm và vị trí dùng để ghim nguồn. JSON bên dưới chỉ đọc.", advanced);
  const formats = tao("div", undefined, advanced), raw = tao("pre", "", advanced);
  const actions = tao("section"), check = tao("button", "Kiểm tra bộ quy tắc", actions), save = tao("button", "Áp dụng vào bước", actions), reload = tao("button", "Tải lại", actions);
  save.classList.add("dc-primary"); for (const b of [check, save, reload]) b.type = "button";
  const status = tao("p", "", actions); status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
  let bo, original, dirty = false, version, busy = false, locked = true;
  let errors = new Map();
  const msg = (s, fail = false) => {status.textContent = s; status.setAttribute("role", fail ? "alert" : "status");};
  function enable() {for (const b of [check, save, add]) b.disabled = busy || locked; reload.disabled = busy || !cua?.doc; for (const e of editor.querySelectorAll("input,select,button")) e.disabled = busy || locked; for (const e of formats.querySelectorAll("input,select,button")) e.disabled = busy || locked;}
  function textNow() {return dirty ? JSON.stringify(bo) : original;}
  function valid() {
    for (const e of errors.values()) {e.textContent = "";}
    try {kiemBo(bo); docJson(textNow()); raw.textContent = textNow(); badge.textContent = "Hợp lệ về cấu trúc"; return true;}
    catch (e) {raw.textContent = textNow() || ""; badge.textContent = "Cần sửa"; const local = errors.get(e.truong); if (local) local.textContent = e.message; msg(e.message, true); return false;}
  }
  function changed() {dirty = true; msg("Có thay đổi chưa áp dụng."); valid();}
  function field(parent, ten, hint, value, path, options, change) {
    const label = tao("label", ten, parent), input = tao(options ? "select" : "input", undefined, label);
    input.setAttribute("aria-label", ten);
    if (options) for (const [v, t] of options) {const op = tao("option", t, input); op.value = v;}
    else {input.type = "text"; input.placeholder = hint;}
    input.value = String(value ?? ""); tao("small", hint, label);
    const error = tao("small", "", label); error.classList.add("dc-error"); error.setAttribute("aria-live", "polite"); errors.set(path, error);
    input.addEventListener(options ? "change" : "input", () => {change(input.value); changed();}); return input;
  }
  function draw() {
    rows.replaceChildren(); formats.replaceChildren(); errors = new Map();
    const q = bo.quy_tac_cung;
    add.disabled = !q;
    if (!q) {tao("p", "Bộ cũ chưa khai nhận diện bổ sung. Cần chọn bộ đã duyệt có phần quy tắc cứng để thêm vùng.", rows); return;}
    if (!q.vung_bao_ve.length) tao("p", "Chưa có vùng bổ sung. Có thể thêm vùng từ nguồn đã ghim.", rows);
    q.vung_bao_ve.forEach((v, n) => {
      const row = tao("fieldset", undefined, rows); tao("legend", `Vùng ${n + 1}`, row);
      const grid = tao("div", undefined, row); grid.classList.add("dc-grid");
      const p = `vung_bao_ve.${n}`;
      field(grid, "Bản tài liệu", "Chọn nguồn chứa vùng cần bảo vệ.", v.ben, p + ".ben", [["word", "Bản Word"], ["ban_ky", "Bản ký"]], s => v.ben = s);
      field(grid, "Loại thông tin", "Ví dụ: bên ký hoặc số tài khoản.", v.loai, p + ".loai", Object.entries(VUNG), s => v.loai = s);
      field(grid, "Nguyên văn", "Ví dụ: Công ty DEMO Ánh Dương; phải khớp nguồn.", v.nguyen_van, p + ".nguyen_van", null, s => v.nguyen_van = s);
      const detail = tao("details", undefined, row); tao("summary", "Nâng cao · vị trí và băm nguồn", detail);
      const dg = tao("div", undefined, detail); dg.classList.add("dc-grid");
      for (const [key, ten] of [["bat_dau", "Vị trí bắt đầu"], ["ket_thuc", "Vị trí kết thúc"]]) {
        const input = field(dg, ten, "Số nguyên 0–500.000; đếm Unicode code point, cuối không tính.", v[key], p + ".bat_dau", null, s => v[key] = /^\d+$/.test(s) ? Number(s) : null);
        input.type = "number"; input.min = "0"; input.max = "500000"; input.step = "1";
      }
      field(detail, "Băm toàn văn nguồn", "sha256: và 64 ký tự hex; dùng băm văn bản, không phải băm tệp.", v.bam_van_ban, p + ".bam_van_ban", null, s => v.bam_van_ban = s);
      const del = tao("button", `Xóa vùng ${n + 1}`, row); del.type = "button";
      del.addEventListener("click", () => {q.vung_bao_ve.splice(n, 1); draw(); changed(); enable();});
    });
    tao("h3", "Định dạng số", formats);
    q.dinh_dang_so.forEach((f, n) => {
      const grid = tao("div", undefined, formats); grid.classList.add("dc-grid");
      const opts = [["", "Không dùng"], [".", "Dấu chấm"], [",", "Dấu phẩy"]];
      field(grid, `Dấu hàng nghìn ${n + 1}`, "Ví dụ: 1.000.000 VND.", f.nghin, `dinh_dang_so.${n}`, [...opts, [" ", "Khoảng trắng"]], s => f.nghin = s || null);
      field(grid, `Dấu thập phân ${n + 1}`, "Phải khác dấu hàng nghìn.", f.thap_phan, `dinh_dang_so.${n}`, opts, s => f.thap_phan = s || null);
    });
    tao("h3", "Cách ghi tiền", formats);
    Object.entries(q.don_vi_tien).forEach(([ten, ma], n) => {
      field(formats, ten, "Mã tiền tệ 3 chữ hoa, ví dụ VND; giữ tên gọi của bộ đã duyệt.", ma, `don_vi_tien.${n}`, null, s => q.don_vi_tien[ten] = s);
    });
    tao("h3", "Định dạng ngày trong tài liệu", formats);
    const opts = [["YYYY-MM-DD", "30/10/2026 · nguồn theo năm-tháng-ngày"], ["DD/MM/YYYY", "30/10/2026 · nguồn theo ngày/tháng/năm"], ["MM/DD/YYYY", "30/10/2026 · nguồn theo tháng/ngày/năm"]];
    q.dinh_dang_ngay.forEach((v, n) => field(formats, `Kiểu ngày ${n + 1}`, "Ngày hiển thị theo ngày/tháng/năm; mã nguồn nằm trong dữ liệu nâng cao.", v, "dinh_dang_ngay", opts, s => q.dinh_dang_ngay[n] = s));
    raw.textContent = textNow();
  }
  add.addEventListener("click", () => {
    if (busy || locked || !bo.quy_tac_cung) return;
    if (bo.quy_tac_cung.vung_bao_ve.length >= 1000) {msg("Tối đa 1.000 vùng bảo vệ; không thêm được dòng mới.", true); return;}
    bo.quy_tac_cung.vung_bao_ve.push({ben: "word", loai: "ben_ky", bat_dau: 0, ket_thuc: 1, nguyen_van: "", bam_van_ban: ""});
    draw(); changed(); enable();
  });
  async function read() {
    if (busy) return; busy = true; locked = true; enable();
    try {
      if (!cua?.doc) {badge.textContent = "Chờ Core"; msg("Chưa có cửa Cài đặt bước của Core. Trình soạn chưa thể đọc hoặc áp dụng.", true); return;}
      const r = await cua.doc();
      if (r?.phien_ban === undefined || r.phien_ban === null) throw Error();
      const text = r.tham_so?.bo_quy_tac_json; const parsed = kiemBo(docJson(text));
      const exported = await xuatThamSo(text);
      if (r.tham_so.bam_bo_quy_tac !== exported.bam_bo_quy_tac) {msg("Băm bộ không khớp nội dung. Cần chọn lại bộ đã ghim trước khi soạn.", true); badge.textContent = "Sai băm"; return;}
      original = text; bo = parsed; version = r.phien_ban; dirty = false; draw(); locked = !cua.luu;
      badge.textContent = "Đã đọc bộ"; msg(locked ? "Cửa Core chỉ đọc; chưa thể áp dụng vào bước." : "Đã đọc Cài đặt bước. Bộ chỉ có hiệu lực sau khi được duyệt và ghim đúng nguồn.");
    } catch (e) {badge.textContent = "Chưa đọc được"; msg(e.truong ? e.message : "Chưa đọc được Cài đặt bước. Tải lại trước khi áp dụng.", true);}
    finally {busy = false; enable(); if (!bo?.quy_tac_cung) add.disabled = true;}
  }
  check.addEventListener("click", () => {if (!busy && !locked && valid()) msg("Cấu trúc bộ hợp lệ. Kiểm nguồn, quyền và phê duyệt vẫn do Core và engine thực hiện.");});
  save.addEventListener("click", async () => {
    if (busy || locked || !valid()) return;
    busy = true; enable();
    try {
      const thamSo = await xuatThamSo(textNow());
      const r = await cua.luu({tham_so: thamSo, phien_ban: version});
      if (r?.da_luu !== true || r.phien_ban === undefined || r.phien_ban === null || r.phien_ban === version) throw Error();
      version = r.phien_ban; original = thamSo.bo_quy_tac_json; dirty = false; badge.textContent = "Đã áp dụng";
      msg("Đã áp dụng vào Cài đặt bước. Cần ghim cùng nội dung tại bước nhận cặp trước khi chạy.");
    } catch (e) {
      locked = true;
      const conflict = e?.status === 409 || [e?.ma, e?.code].some(s => ["NGAN_XUNG_DOT", "CAU_HINH_XUNG_DOT", "BUOC_XUNG_DOT"].includes(s));
      msg(conflict ? "Cài đặt bước đã được người khác sửa, tải lại trước khi lưu." : "Chưa xác nhận được việc áp dụng. Tải lại trước khi lưu tiếp.", true);
      badge.textContent = "Cần tải lại";
    } finally {busy = false; enable();}
  });
  reload.addEventListener("click", read);
  await read();
  return {doc_gia_tri: () => {if (locked || busy || !valid()) throw Error("Chưa thể xuất bộ quy tắc."); return textNow();}};
}
