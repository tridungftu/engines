// Thành phần TS-TX nhúng trong module. Dữ liệu chỉ nằm trong RAM tới khi module lưu.
export async function nap({ goc, KttCore = globalThis.KttCore, tham_so = null,
  dinh_danh = {}, phien_ban = null, luu = null }) {
  const doc = goc.ownerDocument;
  const cong = KttCore.engine("e_trich_xuat");
  let bo = { phien_ban: 1, module: "", loai_hop_dong: "", phien_ban_bo: "", ...dinh_danh,
    cac_dong: [], quy_tac: [] };
  let phienBan = phien_ban, banXuat = null, dong = false, banNhapLoi = false, xungDot = false, soDoi = 0;
  const suKien = [], truong = new Map();
  let suKienBang = [];
  const tao = (ten, chu, lop) => {
    const el = doc.createElement(ten);
    if (chu !== undefined) el.textContent = chu;
    if (lop) el.className = lop;
    return el;
  };
  let dangVeBang = false;
  const nghe = (el, ten, ham) => { el.addEventListener(ten, ham); (dangVeBang ? suKienBang : suKien).push([el, ten, ham]); };
  const man = tao("section", undefined, "tx-soan");
  const css = tao("style", `
    .tx-soan{font:16px/1.5 "Segoe UI",Arial,sans-serif;color:#203a54;max-width:1180px;margin:auto}
    .tx-soan *{box-sizing:border-box}.tx-soan .the{background:#fff;border:1px solid #d9e2ef;border-radius:12px;margin:16px 0;overflow:hidden}
    .tx-soan header{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:22px 26px;border-bottom:1px solid #d9e2ef}
    .tx-soan h2,.tx-soan h3{margin:0;font-size:21px}.tx-soan .noi{padding:22px 26px}
    .tx-soan .luoi{display:grid;grid-template-columns:1fr 1fr;gap:20px}.tx-soan label{display:block;font-weight:600}
    .tx-soan input:not([type=checkbox]),.tx-soan select,.tx-soan textarea{width:100%;border:1px solid #cbd9ea;border-radius:7px;padding:10px 12px;background:#fff;color:inherit;font:inherit;margin-top:5px}
    .tx-soan textarea{min-height:80px;resize:vertical}.tx-soan small{display:block;font-size:13px;font-weight:400;color:#647b91;margin:5px 0}
    .tx-soan button{font:inherit;border:1px solid #cbd9ea;border-radius:7px;padding:9px 16px;background:white;color:#245c91;cursor:pointer}
    .tx-soan button.chinh{background:#245c91;color:white}.tx-soan button:disabled{opacity:.5;cursor:default}
    .tx-soan .nut{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0}.tx-soan .nhan{font-size:14px;padding:6px 10px;background:#edf6f0;color:#216956;border-radius:6px}
    .tx-soan .canh{padding:14px 18px;background:#fff7e6;border:1px solid #f3dbad;border-radius:8px;color:#8a5900}
    .tx-soan .loi{display:block;color:#ae3030;font-size:13px;white-space:pre-line}.tx-soan [aria-invalid=true]{border-color:#ae3030!important}
    .tx-soan .cuon{overflow:auto}.tx-soan table{width:100%;border-collapse:collapse;min-width:650px}
    .tx-soan th,.tx-soan td{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #e4eaf1}
    .tx-soan th{font-size:14px;background:#f5f8fc}.tx-soan td:first-child{width:100px}.tx-soan pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;background:#f5f8fc;padding:14px}
    .tx-soan summary{cursor:pointer;font-weight:600}.tx-soan details{margin:14px 0}.tx-soan :focus-visible{outline:3px solid #709cc3;outline-offset:2px}
    @media(max-width:700px){.tx-soan .luoi{grid-template-columns:1fr}.tx-soan header,.tx-soan .noi{padding:16px}.tx-soan header{align-items:flex-start}.tx-soan table{min-width:0}.tx-soan thead{display:none}.tx-soan tbody,.tx-soan tr,.tx-soan td{display:block;width:100%!important}.tx-soan td{border:0;padding:10px 0}.tx-soan tr{border-bottom:1px solid #d9e2ef}.tx-soan td:first-child{display:flex;align-items:center;justify-content:space-between}.tx-soan .cuon{overflow:visible}}
  `);
  const the = tao("div", undefined, "the"), dau = tao("header");
  const trangThai = tao("span", "Chưa kiểm tra", "nhan"); trangThai.setAttribute("role", "status");
  dau.append(tao("h2", "▤ Bộ tham số trích xuất"), trangThai);
  const noi = tao("div", undefined, "noi");
  noi.append(tao("p", "Nhập Excel theo mẫu E1, sửa các dòng rồi kiểm tra trước khi xuất. Bộ tham số do module quản lý."));
  noi.append(tao("p", "Chờ Core nối màn nhúng và thao tác kiểm bộ. Màn này chưa được nạp trong Core thật.", "canh"));
  const nhap = tao("input"); nhap.type = "file"; nhap.accept = ".xlsx"; nhap.setAttribute("aria-label", "Tệp Excel bộ tham số");
  nhap.hidden = true;
  const chonTep = tao("button", "Chọn tệp Excel"), tenTep = tao("span", "Chưa chọn tệp"); chonTep.type = "button";
  nghe(chonTep, "click", () => nhap.click());
  nghe(nhap, "change", () => { tenTep.textContent = nhap.files?.[0]?.name ?? "Chưa chọn tệp"; });
  const chon = tao("div", undefined, "nut"); chon.append(chonTep, tenTep);
  const nutNhap = tao("button", "Nhập Excel"); nutNhap.type = "button";
  noi.append(tao("label", "Tệp Excel bộ tham số"), nhap, chon,
    tao("small", "Tệp .xlsx tối đa 2 MiB; đủ 10 cột E1, không công thức, ô gộp hoặc macro. Ví dụ: DEMO-bo-tham-so.xlsx."), nutNhap);
  const bang = tao("div"); noi.append(bang);
  const bao = tao("p"); bao.setAttribute("role", "status"); bao.setAttribute("aria-live", "polite");
  const kiem = tao("button", "Kiểm tra và tính băm"), xuat = tao("button", luu ? "Lưu bộ vào module" : "Xuất tham số");
  kiem.type = xuat.type = "button"; xuat.className = "chinh";
  const cacNut = tao("div", undefined, "nut"); cacNut.append(kiem, xuat);
  const nangCao = tao("details"), dinhDanh = tao("div", undefined, "luoi");
  nangCao.append(tao("summary", "Nâng cao · định danh và kết quả xuất"), dinhDanh);
  const ketQua = tao("pre", "Chưa có bản xuất đã kiểm."); ketQua.setAttribute("aria-label", "Tham số đã xuất");
  nangCao.append(ketQua);
  noi.append(nangCao, cacNut, bao); the.append(dau, noi); man.append(css, the); goc.replaceChildren(man);
  const moi = () => {
    soDoi++; banXuat = null; ketQua.textContent = "Chưa có bản xuất đã kiểm.";
    trangThai.textContent = "Có thay đổi · cần kiểm tra";
  };
  function oNhap(gocO, ten, giaTri, goiY, duong, doi, kieu = "text") {
    const nhan = tao("label", ten), el = tao(kieu === "textarea" ? "textarea" : kieu === "select" ? "select" : "input");
    if (kieu === "checkbox") { el.type = "checkbox"; el.checked = giaTri; }
    else if (kieu === "select") {
      for (let i = 0; i <= 3; i++) { const opt = tao("option", String(i)); opt.value = String(i); el.append(opt); }
      el.value = String(giaTri);
    } else { if (kieu !== "textarea") el.type = "text"; el.value = giaTri; el.placeholder = goiY; }
    el.setAttribute("data-truong", duong);
    const loi = tao("span", "", "loi");
    nhan.append(el, tao("small", goiY), loi); gocO.append(nhan); truong.set(duong, { el, loi });
    nghe(el, "input", () => { moi(); doi(kieu === "checkbox" ? el.checked : kieu === "select" ? Number(el.value) : el.value); kiemNhanh(); });
    return el;
  }
  for (const [k, ten, mau] of [["module", "Mã module", "module_demo"], ["loai_hop_dong", "Mã loại hợp đồng", "DEMO"], ["phien_ban_bo", "Phiên bản bộ", "demo-1"]]) {
    oNhap(dinhDanh, ten, bo[k], `Bắt buộc · ví dụ ${mau}; tối đa 200 ký tự.`, k, v => { bo[k] = v; });
  }
  if (!bo.module || !bo.loai_hop_dong || !bo.phien_ban_bo) nangCao.open = true;
  const baoLoi = (ds) => {
    for (const { el, loi } of truong.values()) { loi.textContent = ""; el.setAttribute("aria-invalid", "false"); }
    for (const v of ds) {
      const o = truong.get(v.truong);
      if (o) { o.loi.textContent += v.thong_bao + "\n"; o.el.setAttribute("aria-invalid", "true"); }
    }
    bao.textContent = ds.map(v => v.thong_bao).join("\n");
    return ds.length === 0;
  };
  function kiemNhanh() {
    const ds = [], ma = new Set();
    for (const k of ["module", "loai_hop_dong", "phien_ban_bo"]) if (!/^[A-Za-z0-9_.:-]{1,200}$/.test(bo[k]))
      ds.push({ truong: k, thong_bao: "Điền mã hợp lệ; xem mẫu tại ô trong Nâng cao." });
    bo.cac_dong.forEach((r, i) => {
      const them = (k, t) => ds.push({ truong: `cac_dong.${i}.${k}`, thong_bao: `Dòng ${i + 1}: ${t}` });
      if (!/^[A-Z]{2,3}-[0-9]{2,3}$/.test(r.ma)) them("ma", "mã theo mẫu TT-01.");
      else if (ma.has(r.ma)) them("ma", "mã trùng; đổi sang mã khác.");
      ma.add(r.ma);
      if (!r.nhom.trim()) them("nhom", "điền tên nhóm.");
      if (!r.mo_ta.trim() || [...r.mo_ta].length > 1000) them("mo_ta", "mô tả bắt buộc, tối đa 1.000 ký tự.");
      for (const k of ["tk", "bk", "bat_buoc", "loai_tru"]) if (r[k].split(/[;\n]/).some(w => [...w.trim()].length > 60 || (w.includes("@") && !(k === "tk" && w.trim().toLowerCase() === "@mo_dau"))))
        them(k, "mỗi từ khóa tối đa 60 ký tự; chỉ tiêu đề dùng @mo_dau.");
    });
    if (!bo.cac_dong.some(r => r.dung)) ds.push({ truong: "cac_dong", thong_bao: "Bật Dùng cho ít nhất một tham số." });
    if (bo.cac_dong.filter(r => r.dung).length > 200) ds.push({ truong: "cac_dong", thong_bao: "Tối đa 200 tham số đang dùng." });
    bo.quy_tac.forEach((r, i) => {
      const them = (k,t) => ds.push({truong:`quy_tac.${i}.${k}`,thong_bao:`Quy tắc ${i+1}: ${t}`});
      if (!r.ma_tham_so.length || new Set(r.ma_tham_so).size !== r.ma_tham_so.length || r.ma_tham_so.some(k=>!ma.has(k))) them("ma_tham_so","chọn mã có trong bảng, không lặp.");
      if (r.kieu === "Tổng tỷ lệ") {
        if (!["=","<="].includes(r.dieu_kien)) them("dieu_kien","chỉ dùng = hoặc <=.");
        if (r.doi_chieu !== "100") them("doi_chieu","điền 100.");
      } else {
        if (r.ma_tham_so.length !== 1) them("ma_tham_so","điền đúng một mã nguồn.");
        if (!ma.has(r.doi_chieu)) them("doi_chieu","điền một mã có trong bảng.");
        if (r.dieu_kien !== (r.kieu === "Ngày không sau" ? "<=" : "")) them("dieu_kien","Ngày không sau dùng <=; Có thì phải có để trống.");
      }
    });
    return baoLoi(ds);
  }
  function veBang() {
    for (const [el,ten,ham] of suKienBang) el.removeEventListener(ten,ham);
    suKienBang = []; dangVeBang = true;
    for (const k of [...truong.keys()]) if (k.startsWith("cac_dong.") || k.startsWith("quy_tac.")) truong.delete(k);
    const tieuDe = tao("div", undefined, "nut"), them = tao("button", "Thêm tham số"); them.type = "button";
    tieuDe.append(tao("h3", `${bo.cac_dong.length} tham số`), them);
    nghe(them, "click", () => { bo.cac_dong.push({ma:"",nhom:"",mo_ta:"",tk:"",bk:"",dung:true,muc:1,bat_buoc:"",loai_tru:"",luon_cloud:false}); moi(); veBang(); kiemNhanh(); });
    const table = tao("table"), head = tao("tr");
    for (const chu of ["Dòng", "Nội dung trích xuất", "Tìm kiếm và kiểm soát"]) head.append(tao("th", chu));
    const thead = tao("thead"); thead.append(head); table.append(thead); const tbody = tao("tbody"); table.append(tbody);
    bo.cac_dong.forEach((r, i) => {
      const tr = tao("tr"), so = tao("td", String(i + 1)), chinh = tao("td"), phu = tao("td"), xoa = tao("button", "Xóa dòng"); xoa.type = "button";
      nghe(xoa, "click", () => { bo.cac_dong.splice(i, 1); moi(); veBang(); kiemNhanh(); }); so.append(xoa);
      const themO = (g, k, ten, mau, kieu) => oNhap(g, ten, r[k], mau, `cac_dong.${i}.${k}`, v => { r[k] = v; }, kieu);
      themO(chinh, "ma", "Mã tham số", "Bắt buộc · ví dụ TT-01.");
      themO(chinh, "nhom", "Nhóm", "Bắt buộc · ví dụ Thông tin chung.");
      themO(chinh, "mo_ta", "Mô tả cho AI", "Bắt buộc · tối đa 1.000 ký tự; ví dụ Trích tên hợp đồng.", "textarea");
      themO(chinh, "dung", "Dùng", "Bật để đưa tham số vào yêu cầu trích xuất.", "checkbox");
      themO(chinh, "muc", "Mức quan trọng", "Chọn 0–3; ví dụ 1.", "select");
      const ct = tao("details"); ct.append(tao("summary", "Từ khóa và tùy chọn"));
      for (const [k, ten, mau] of [["tk","Từ khóa tiêu đề","Ví dụ: thông tin; @mo_dau"],["bk","Từ khóa nội dung","Ví dụ: tên hợp đồng; mỗi từ tối đa 60 ký tự."],["bat_buoc","Từ khóa bắt buộc","Ví dụ: hợp đồng; bỏ trống nếu không ràng buộc."],["loai_tru","Từ khóa loại trừ","Ví dụ: phụ lục; bỏ trống nếu không loại trừ."]]) themO(ct, k, ten, mau, "textarea");
      themO(ct, "luon_cloud", "Luôn hỏi Cloud", "Chỉ giữ cờ của bộ; không bật hoặc gọi Cloud từ màn này.", "checkbox");
      phu.append(ct); tr.append(so, chinh, phu); tbody.append(tr);
    });
    const cuon = tao("div", undefined, "cuon"); cuon.append(table);
    const qt = tao("details"), themQT = tao("button", "Thêm quy tắc"); themQT.type = "button";
    qt.append(tao("summary", `Quy tắc hậu kiểm (${bo.quy_tac.length})`), tao("small", "Không bắt buộc. Chọn kiểu và mã có trong bảng; ví dụ Tổng tỷ lệ, TT-01;TT-02, <=, 100."));
    bo.quy_tac.forEach((r, i) => {
      const hang = tao("div", undefined, "luoi"), chon = tao("select"), nhan = tao("label", "Kiểu quy tắc");
      for (const k of ["Tổng tỷ lệ", "Ngày không sau", "Có thì phải có"]) { const opt = tao("option", k); opt.value = k; chon.append(opt); } chon.value = r.kieu;
      nhan.append(chon); hang.append(nhan);
      nghe(chon, "input", () => { r.kieu = chon.value; moi(); kiemNhanh(); });
      for (const [k, ten, mau] of [["ma_tham_so","Mã tham số","Bắt buộc · ví dụ TT-01;TT-02"],["dieu_kien","Điều kiện","Tổng tỷ lệ: = hoặc <=; Ngày không sau: <=; Có thì phải có: trống."],["doi_chieu","Giá trị hoặc mã đối chiếu","Tổng tỷ lệ: 100; kiểu khác: một mã, ví dụ TT-02."]])
        oNhap(hang, ten, k === "ma_tham_so" ? r[k].join(";") : r[k], mau, `quy_tac.${i}.${k}`, v => { r[k] = k === "ma_tham_so" ? v.split(";").map(s=>s.trim()).filter(Boolean) : v; });
      const boQT = tao("button", "Xóa quy tắc"); boQT.type = "button";
      nghe(boQT, "click", () => { bo.quy_tac.splice(i, 1); moi(); veBang(); }); hang.append(boQT); qt.append(hang);
    });
    nghe(themQT, "click", () => { bo.quy_tac.push({kieu:"Tổng tỷ lệ",ma_tham_so:[],dieu_kien:"<=",doi_chieu:"100"}); moi(); veBang(); }); qt.append(themQT);
    bang.replaceChildren(tieuDe, cuon, qt);
    dangVeBang = false;
  }
  function apDung(kq) {
    if (!kq?.dat) { baoLoi(kq?.loi ?? [{thong_bao:"Không kiểm được bộ tham số."}]); trangThai.textContent = "Cần sửa nội dung"; return false; }
    bo = kq.bo; banXuat = kq.tham_so;
    for (const k of ["module", "loai_hop_dong", "phien_ban_bo"]) truong.get(k).el.value = bo[k];
    veBang(); baoLoi([]); ketQua.textContent = JSON.stringify(banXuat, null, 2);
    trangThai.textContent = "✓ Đã kiểm tra";
    bao.textContent = (kq.canh_bao ?? []).map(v => v.thong_bao).join("\n") || "Bộ hợp lệ. Có thể xuất tham số.";
    return true;
  }
  let ban = false;
  async function thucHien(ham) {
    if (ban || dong) return null; ban = true;
    for (const el of [kiem,xuat,nutNhap]) el.disabled = true;
    try { return await ham(); }
    catch (loi) {
      if (dong) return null;
      const cas = [loi?.ma,loi?.code].some(m => ["NGAN_XUNG_DOT","CAU_HINH_XUNG_DOT","MODULE_XUNG_DOT"].includes(m)) || loi?.status === 409 || loi?.http_status === 409;
      if (cas) xungDot = true;
      bao.textContent = cas ? "Bộ tham số đã được người khác sửa, tải lại trước khi lưu." : "Không thực hiện được thao tác. Giữ nội dung hiện tại và thử lại.";
      trangThai.textContent = cas ? "Có tranh chấp" : "Chưa kiểm được"; return null;
    } finally { ban = false; if (!dong) for (const el of [kiem,xuat,nutNhap]) el.disabled = false; }
  }
  async function kiemBo() {
    banXuat = null;
    ketQua.textContent = "Chưa có bản xuất đã kiểm.";
    if (banNhapLoi || xungDot || !kiemNhanh()) return null;
    const moc = soDoi, kq = await cong.thao_tac("soan_bo_tham_so", {lenh:"kiem_bo", bo: JSON.parse(JSON.stringify(bo))});
    if (dong || moc !== soDoi) return null;
    return apDung(kq) ? {...banXuat} : null;
  }
  nghe(kiem, "click", () => thucHien(kiemBo));
  async function xuatBo() {
    return thucHien(async () => {
      if (xungDot) { bao.textContent = "Bộ tham số đã được người khác sửa, tải lại trước khi lưu."; return null; }
      const giaTri = await kiemBo(); if (!giaTri || dong) return null;
      if (luu) {
        const moc = soDoi, kq = await luu({...giaTri}, phienBan);
        if (dong) return null;
        if (kq?.phien_ban == null) throw new Error();
        phienBan = kq.phien_ban;
        bao.textContent = moc === soDoi ? "Đã lưu bộ vào module." : "Đã lưu bản đã kiểm; thay đổi mới chưa lưu.";
      } else bao.textContent = "Đã xuất tham số trong mục Nâng cao. Chưa lưu vào module.";
      return giaTri;
    });
  }
  nghe(xuat, "click", xuatBo);
  nghe(nutNhap, "click", () => thucHien(async () => {
    const file = nhap.files?.[0]; if (!file || !/\.xlsx$/i.test(file.name) || file.size > 2*1024*1024) {
      bao.textContent = "Chọn tệp Excel .xlsx tối đa 2 MiB."; return;
    }
    const moc = soDoi, bytes = new Uint8Array(await file.arrayBuffer());
    let text = ""; for (const b of bytes) text += String.fromCharCode(b);
    const kq = await cong.thao_tac("soan_bo_tham_so", {lenh:"nhap_excel",bo:{...bo},tep_base64:btoa(text)});
    if (dong || moc !== soDoi) return;
    if (kq?.dat) { moi(); apDung(kq); banNhapLoi = false; }
    else { banXuat = null; ketQua.textContent = "Chưa có bản xuất đã kiểm."; apDung(kq); }
  }));
  veBang();
  if (tham_so) {
    banNhapLoi = true;
    await thucHien(async () => { const kq = await cong.thao_tac("soan_bo_tham_so", {lenh:"doc_bo",tham_so}); if (!dong && apDung(kq)) { banNhapLoi = false; nangCao.open = false; } });
  }
  return { xuat: xuatBo, dong() { dong = true; for (const [el,ten,ham] of [...suKien,...suKienBang]) el.removeEventListener(ten,ham); goc.replaceChildren(); } };
}

export default nap;
