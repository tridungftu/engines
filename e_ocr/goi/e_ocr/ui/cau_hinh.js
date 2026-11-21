// Màn quản trị OCR; chỉ trao đổi qua KttCore, mọi nội dung dùng textContent.
const macDinh = {
  abbyy: {bat: false, thu_muc_vao: "", thu_muc_ra: "", thoi_han_giay: 900, han_muc_trang_30_ngay: 5000},
  tesseract: {duong_dan: "", ngon_ngu: "vie+eng"},
};
const ngonNgu = {vie: "Tiếng Việt", eng: "Tiếng Anh", "vie+eng": "Tiếng Việt + Tiếng Anh", "eng+vie": "Tiếng Anh + Tiếng Việt"};
const so = n => new Intl.NumberFormat("vi-VN").format(n);
const ngayGio = luc => new Intl.DateTimeFormat("vi-VN", {
  day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
}).format(new Date(luc));

export async function mount(goc, {
  KttCore = globalThis.KttCore, dongHo = () => Date.now(),
  lapLai = globalThis.setInterval, dungLap = globalThis.clearInterval,
} = {}) {
  const cong = KttCore.engine("e_ocr");
  const doc = goc.ownerDocument;
  let phien = null, cauHinh = structuredClone(macDinh), daDong = false;
  const o = {}, loiO = {}, trangThaiKiem = {}, nutKiem = {}, lanKiem = {};
  let dangLuu = false, dangTai = false;
  function nut(ten, text, cha = goc) {
    const n = doc.createElement(ten);
    if (text !== undefined) n.textContent = text;
    cha.appendChild(n);
    return n;
  }
  goc.replaceChildren();
  goc.className = "ocr-ui";
  const kieu = nut("style");
  kieu.textContent = `
    .ocr-ui{font:16px/1.5 "Segoe UI",Arial,sans-serif;color:#203850;max-width:1100px;margin:auto;padding:24px;box-sizing:border-box;background:#f4f6f9}
    .ocr-ui *{box-sizing:border-box}.ocr-ui h2{font-size:26px;margin:0 0 6px}.ocr-ui p{margin:8px 0 16px}.ocr-ui .ocr-mo-ta,.ocr-ui small{color:#60758b}
    .ocr-ui .ocr-the{background:white;border:1px solid #d9e2ec;border-radius:12px;margin:24px 0;overflow:hidden;min-width:0}
    .ocr-ui .ocr-dau{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:22px 28px;border-bottom:1px solid #d9e2ec;flex-wrap:wrap}
    .ocr-ui h3{font-size:21px;margin:0}.ocr-ui h4{font-size:17px;margin:18px 0 8px}.ocr-ui .ocr-than{padding:24px 28px}
    .ocr-ui .ocr-luoi{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px 28px}.ocr-ui label{display:block;font-weight:600}
    .ocr-ui input:not([type=checkbox]),.ocr-ui select{display:block;width:100%;margin:8px 0;padding:12px 14px;font:inherit;color:inherit;background:white;border:1px solid #cbd8e7;border-radius:7px;min-width:0}
    .ocr-ui input[type=checkbox]{accent-color:#203e5b;width:20px;height:20px;margin:0 10px 0 0;vertical-align:middle}
    .ocr-ui small{display:block;font-size:14px;font-weight:400}.ocr-ui .ocr-loi{color:#a12d26;min-height:0;font-size:14px;font-weight:400}
    .ocr-ui [aria-invalid=true]{border-color:#b63f35!important}.ocr-ui .ocr-nhan{border:1px solid #d9e2ec;border-radius:6px;padding:6px 10px;font-size:14px;background:#f4f6f9;color:#60758b}
    .ocr-ui .ocr-nhan[data-muc=dat]{color:#08736b;background:#edf8f1;border-color:#d0eadd}.ocr-ui .ocr-nhan[data-muc=loi]{color:#a12d26;background:#fff2ef;border-color:#efd2cd}
    .ocr-ui .ocr-nut{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:20px}.ocr-ui button{font:inherit;color:#203e5b;background:white;border:1px solid #cbd8e7;border-radius:7px;padding:11px 18px;cursor:pointer}
    .ocr-ui button[type=submit]{background:#203e5b;color:white;border-color:#203e5b}.ocr-ui button:disabled{opacity:.55;cursor:default}
    .ocr-ui button:focus-visible,.ocr-ui input:focus-visible,.ocr-ui select:focus-visible{outline:3px solid #588ac0;outline-offset:3px}
    .ocr-ui .ocr-canh-bao{padding:12px 16px;background:#fff8e8;border:1px solid #efdba9;border-radius:7px;color:#8f5a00;font-size:14px}
    .ocr-ui ul{padding-left:22px}.ocr-ui [role=status]{overflow-wrap:anywhere}
    @media(max-width:640px){.ocr-ui{padding:14px}.ocr-ui .ocr-luoi{grid-template-columns:1fr}.ocr-ui .ocr-dau,.ocr-ui .ocr-than{padding:18px}.ocr-ui .ocr-nhan{max-width:100%}}
  `;
  nut("h2", "Cấu hình OCR");
  nut("p", "Ưu tiên ABBYY; dùng Tesseract khi nguồn ưu tiên không xử lý được.").className = "ocr-mo-ta";
  const form = nut("form");
  form.noValidate = true;
  function the(tieuDe, bieuTuong, cha = form) {
    const the = nut("section", undefined, cha); the.className = "ocr-the";
    const dau = nut("div", undefined, the); dau.className = "ocr-dau";
    nut("h3", bieuTuong + "  " + tieuDe, dau);
    const nhan = nut("span", "Chưa kiểm tra", dau); nhan.className = "ocr-nhan";
    nhan.setAttribute("role", "status");
    const than = nut("div", undefined, the); than.className = "ocr-than";
    return {than, nhan};
  }
  function luoi(cha) { const n = nut("div", undefined, cha); n.className = "ocr-luoi"; return n; }
  function truong(ma, nhan, kieu, cha, huongDan, mau, min, max) {
    const khung = nut("div", undefined, cha);
    const label = nut("label", kieu === "checkbox" ? undefined : nhan, khung);
    const input = nut(kieu === "select" ? "select" : "input", undefined, label);
    if (kieu === "checkbox") nut("span", nhan, label);
    input.name = ma;
    input.id = "ocr-" + ma;
    if (kieu !== "select") input.type = kieu;
    else for (const [ma, ten] of Object.entries(ngonNgu)) nut("option", ten, input).value = ma;
    if (min !== undefined) input.min = String(min);
    if (max !== undefined) input.max = String(max);
    if (kieu === "number") input.step = "1";
    if (kieu !== "checkbox") input.required = kieu === "number" || ma === "ngon_ngu";
    if (kieu === "text") input.maxLength = 4096;
    input.placeholder = mau;
    const goiY = nut("small", huongDan + " Ví dụ: " + mau + ".", khung);
    goiY.id = input.id + "-goi-y";
    const loi = nut("p", "", khung); loi.className = "ocr-loi"; loi.id = input.id + "-loi";
    loi.setAttribute("aria-live", "polite");
    input.setAttribute("aria-describedby", goiY.id + " " + loi.id);
    o[ma] = input; loiO[ma] = loi;
    input.addEventListener("input", () => {
      const hopLe = kiemNhap();
      if (hopLe && thongBao.textContent === "Cần sửa các trường được đánh dấu trước khi lưu.") thongBao.textContent = "";
      const nhom = Object.hasOwn(macDinh.abbyy, ma) ? "abbyy" : "tesseract";
      lanKiem[nhom] = (lanKiem[nhom] ?? 0) + 1;
      trangThaiKiem[nhom].textContent = "Cấu hình đã đổi, cần kiểm tra lại";
      trangThaiKiem[nhom].setAttribute("data-muc", "cho");
      nutKiem[nhom].disabled = false;
    });
  }
  const abbyy = the("ABBYY Hot Folder", "▤");
  trangThaiKiem.abbyy = abbyy.nhan;
  truong("bat", "Bật ABBYY", "checkbox", abbyy.than, "Cho phép ưu tiên ABBYY khi đọc tài liệu.", "bật sau khi kiểm thư mục");
  const abbyyLuoi = luoi(abbyy.than);
  truong("thu_muc_vao", "Thư mục nhận tài liệu", "text", abbyyLuoi, "Đường dẫn tuyệt đối trên máy engine; không chứa tệp cấu hình hay khóa.", "C:/DEMO/OCR/nhan");
  truong("thu_muc_ra", "Thư mục trả kết quả", "text", abbyyLuoi, "Thư mục riêng, không trùng hoặc lồng với thư mục nhận.", "C:/DEMO/OCR/tra");
  truong("thoi_han_giay", "Thời hạn chờ (giây)", "number", abbyyLuoi, "Từ 1 đến 900 giây; hết hạn thì giữ lượt chưa rõ kết quả.", "900", 1, 900);
  const abbyyNut = nut("div", undefined, abbyy.than); abbyyNut.className = "ocr-nut";
  nutKiem.abbyy = nut("button", "Kiểm tra Hot Folder", abbyyNut); nutKiem.abbyy.type = "button";
  nut("p", "Chỉ kiểm truy cập thư mục; không gửi tài liệu, không xác nhận FineReader đang chạy.", abbyy.than).className = "ocr-mo-ta";
  const trangThai = nut("p", "Đang đọc trạng thái ABBYY…", abbyy.than);
  trangThai.setAttribute("role", "status");
  const tess = the("Tesseract dự phòng", "▧");
  trangThaiKiem.tesseract = tess.nhan;
  const tessLuoi = luoi(tess.than);
  truong("duong_dan", "Đường dẫn Tesseract", "text", tessLuoi, "Để trống để tự tìm bộ cài; nếu nhập, chọn đúng tesseract.exe hoặc tesseract.", "C:/DEMO/Tesseract-OCR/tesseract.exe");
  truong("ngon_ngu", "Ngôn ngữ", "select", tessLuoi, "Cần cài đủ các bộ ngôn ngữ đã chọn.", "Tiếng Việt + Tiếng Anh");
  const tessNut = nut("div", undefined, tess.than); tessNut.className = "ocr-nut";
  nutKiem.tesseract = nut("button", "Kiểm tra Tesseract", tessNut); nutKiem.tesseract.type = "button";
  nut("p", "Kiểm bộ cài và ngôn ngữ đã chọn; không nhận dạng tài liệu.", tess.than).className = "ocr-mo-ta";
  const muc = the("Hạn mức ABBYY", "◷"); muc.nhan.textContent = "30 ngày gần nhất";
  truong("han_muc_trang_30_ngay", "Hạn mức trang trong 30 ngày", "number", luoi(muc.than), "Từ 0 đến 5.000 trang; đặt 0 để chuyển sang nguồn dự phòng.", "5000", 0, 5000);
  const hanMuc = nut("p", "Đang đọc hạn mức…", muc.than); hanMuc.setAttribute("role", "status");
  nut("h4", "Các lượt đang chờ đối chiếu", muc.than);
  const danhSach = nut("ul", undefined, muc.than);
  nut("p", "Lượt chưa rõ kết quả vẫn giữ trang cho tới khi có căn cứ đối chiếu.", muc.than).className = "ocr-canh-bao";
  const hangNut = nut("div", undefined, form); hangNut.className = "ocr-nut";
  const luu = nut("button", "Lưu cấu hình", hangNut); luu.type = "submit"; luu.disabled = true;
  const taiLai = nut("button", "Tải lại cấu hình", hangNut); taiLai.type = "button";
  const thongBao = nut("p", ""); thongBao.setAttribute("role", "status");

  function kiemNhap(nhom, batBuocThuMuc = false) {
    let dat = true;
    function loi(ma, cau) {
      if (nhom && !Object.hasOwn(macDinh[nhom], ma)) return;
      loiO[ma].textContent = cau; o[ma].setAttribute("aria-invalid", cau ? "true" : "false");
      if (cau) dat = false;
    }
    for (const [ma, min, max, ten] of [["thoi_han_giay", 1, 900, "Thời hạn"], ["han_muc_trang_30_ngay", 0, 5000, "Hạn mức"]]) {
      const v = o[ma].value.trim();
      loi(ma, v === "" || !Number.isInteger(Number(v)) || Number(v) < min || Number(v) > max ? `${ten} phải là số nguyên từ ${min} đến ${so(max)}.` : "");
    }
    for (const ma of ["thu_muc_vao", "thu_muc_ra", "duong_dan"]) {
      const v = o[ma].value.trim();
      loi(ma, v.length > 4096 ? "Đường dẫn tối đa 4.096 ký tự." : ma !== "duong_dan" && (o.bat.checked || batBuocThuMuc) && !v ? "Cần nhập thư mục trước khi bật hoặc kiểm ABBYY." : "");
    }
    if (o.thu_muc_vao.value.trim() && o.thu_muc_vao.value.trim() === o.thu_muc_ra.value.trim()) loi("thu_muc_ra", "Thư mục trả kết quả phải khác thư mục nhận tài liệu.");
    loi("ngon_ngu", Object.hasOwn(ngonNgu, o.ngon_ngu.value) ? "" : "Cần chọn ngôn ngữ trong danh sách.");
    return dat;
  }
  function giaTriNhap() {
    return {abbyy: {bat: o.bat.checked, thu_muc_vao: o.thu_muc_vao.value.trim(), thu_muc_ra: o.thu_muc_ra.value.trim(),
      thoi_han_giay: Number(o.thoi_han_giay.value), han_muc_trang_30_ngay: Number(o.han_muc_trang_30_ngay.value)},
      tesseract: {duong_dan: o.duong_dan.value.trim(), ngon_ngu: o.ngon_ngu.value}};
  }
  const ketQuaKiem = {
    HOT_FOLDER_TRUY_CAP_DUOC: "Truy cập được thư mục · chưa xác nhận FineReader",
    HOT_FOLDER_KHONG_TRUY_CAP: "Không truy cập được thư mục · kiểm đường dẫn và quyền",
    TESSERACT_DU_NGON_NGU: "Dùng được · đủ ngôn ngữ đã chọn",
    TESSERACT_CHUA_DUNG_DUOC: "Chưa dùng được · kiểm bộ cài và ngôn ngữ đã chọn",
    TESSERACT_QUA_THOI_HAN: "Kiểm tra quá thời hạn · thử lại Tesseract",
  };
  for (const [nhom, ma] of [["abbyy", "kiem_hot_folder"], ["tesseract", "kiem_tesseract"]]) {
    nutKiem[nhom].addEventListener("click", async () => {
      if (nutKiem[nhom].disabled || !kiemNhap(nhom, nhom === "abbyy")) return;
      const lan = lanKiem[nhom] = (lanKiem[nhom] ?? 0) + 1;
      nutKiem[nhom].disabled = true;
      const nhan = trangThaiKiem[nhom]; nhan.textContent = "Đang kiểm tra…"; nhan.setAttribute("data-muc", "cho");
      try {
        const kq = await cong.thao_tac(ma, {[nhom]: giaTriNhap()[nhom]});
        if (daDong || lan !== lanKiem[nhom]) return;
        const maDat = nhom === "abbyy" ? "HOT_FOLDER_TRUY_CAP_DUOC" : "TESSERACT_DU_NGON_NGU";
        const maLoi = nhom === "abbyy" ? ["HOT_FOLDER_KHONG_TRUY_CAP"] : ["TESSERACT_CHUA_DUNG_DUOC", "TESSERACT_QUA_THOI_HAN"];
        const hopLe = (kq?.dat === true && kq?.ma === maDat) || (kq?.dat === false && maLoi.includes(kq?.ma));
        nhan.textContent = hopLe ? ketQuaKiem[kq.ma] : "Chưa nhận được kết quả kiểm tra hợp lệ. Thử lại.";
        nhan.setAttribute("data-muc", kq?.dat === true && kq?.ma === maDat ? "dat" : "loi");
      } catch (loi) {
        if (daDong || lan !== lanKiem[nhom]) return;
        nhan.textContent = typeof cong.thao_tac !== "function" || ["CHUA_HO_TRO", "THAO_TAC_CHUA_HO_TRO"].includes(loi?.ma)
          ? "Chờ Core hỗ trợ nút kiểm tra nguồn OCR."
          : "Không kiểm tra được nguồn. Kiểm tra engine rồi thử lại.";
        nhan.setAttribute("data-muc", "loi");
      } finally { if (!daDong && lan === lanKiem[nhom]) nutKiem[nhom].disabled = false; }
    });
  }

  async function taiCauHinh() {
    const data = await cong.cau_hinh.doc();
    phien = data?.phien_ban_cau_hinh ?? null;
    const giaTri = data?.gia_tri ?? {};
    cauHinh = {
      abbyy: {...macDinh.abbyy, ...giaTri.abbyy},
      tesseract: {...macDinh.tesseract, ...giaTri.tesseract},
    };
    for (const [ma, input] of Object.entries(o)) {
      const value = (ma in cauHinh.abbyy ? cauHinh.abbyy : cauHinh.tesseract)[ma];
      if (input.type === "checkbox") input.checked = value;
      else input.value = String(value);
    }
    for (const nhom of ["abbyy", "tesseract"]) {
      lanKiem[nhom] = (lanKiem[nhom] ?? 0) + 1;
      trangThaiKiem[nhom].textContent = "Chưa kiểm tra";
      trangThaiKiem[nhom].setAttribute("data-muc", "cho");
      nutKiem[nhom].disabled = false;
    }
    kiemNhap();
    luu.disabled = false;
  }

  async function timHet(bang, loc) {
    const ds = [];
    let tiep = null;
    do {
      const trang = await cong.ngan.tim(bang, {loc, gioi_han: 500, tiep});
      ds.push(...trang.danh_sach.map(b => b.gia_tri));
      tiep = trang.tiep;
    } while (tiep != null);
    return ds;
  }

  async function refresh() {
    await Promise.all([
      (async () => {
        try {
          const tt = await cong.ngan.doc("trang_thai_engine", {ma: "abbyy"});
          if (daDong) return;
          const b = tt?.gia_tri;
          const luc = Date.parse(b?.luc_kiem);
          if (!Number.isFinite(luc) || dongHo() - luc > 90000 || luc > dongHo() + 5000) {
            trangThai.textContent = "ABBYY: chưa có cập nhật gần đây.";
          } else {
            const lyDo = {chua_cau_hinh: "chưa cấu hình", dang_tat: "đã tắt trong cấu hình",
              khong_ket_noi: "không truy cập được thư mục", cau_hinh_loi: "cần kiểm tra cấu hình"};
            trangThai.textContent = `ABBYY: ${b.abbyy_bat ? "Bật" : "Tắt"}${lyDo[b.ly_do] ? " — " + lyDo[b.ly_do] : ""}. Kiểm tra lúc ${ngayGio(luc)}.`;
          }
        } catch {
          if (!daDong) trangThai.textContent = "Chưa đọc được trạng thái ABBYY.";
        }
      })(),
      (async () => {
        try {
          const [ngay, mocHanMuc] = await Promise.all([
            timHet("han_muc_ngay", {}), cong.ngan.doc("trang_thai_engine", {ma: "han_muc"}),
          ]);
          if (daDong) return;
          const moc = Math.floor(dongHo() / 1000) - 30 * 86400;
          let daDung = 0;
          const dangGiu = Object.values(JSON.parse(mocHanMuc?.gia_tri?.dang_giu ?? "{}"))
            .reduce((a, b) => a + b, 0);
          for (const b of ngay) {
            const dauNgay = Date.parse(b.ngay + "T00:00:00Z") / 1000;
            for (const [giay, n] of Object.entries(JSON.parse(b.da_nhan))) {
              if (dauNgay + Number(giay) > moc) daDung += n;
            }
          }
          const conLai = Math.max(0, cauHinh.abbyy.han_muc_trang_30_ngay - daDung - dangGiu);
          hanMuc.textContent = `Đã dùng ${so(daDung)} trang trong 30 ngày · Đang giữ ${so(dangGiu)} trang · Còn lại ${so(conLai)} trang`;
        } catch {
          if (!daDong) hanMuc.textContent = "Chưa đọc được hạn mức. Hãy tải lại màn hình.";
        }
      })(),
      (async () => {
        try {
          const tt = await cong.ngan.doc("trang_thai_engine", {ma: "chua_ro"});
          if (daDong) return;
          const b = tt?.gia_tri;
          danhSach.replaceChildren();
          const soLuot = Number(b?.so_luot ?? 0);
          if (!soLuot) nut("li", "Không có lượt chưa rõ kết quả.", danhSach);
          else {
            nut("li", `Có ${so(soLuot)} lượt chưa rõ kết quả.`, danhSach);
            let i = 0;
            for (const [ngay, dem] of Object.entries(JSON.parse(b.theo_ngay)).sort(([a], [b]) => a.localeCompare(b))) {
              for (let n = 0; n < dem; n++) {
                nut("li", `Lượt ${so(++i)} · ${ngay.split("-").reverse().join("/")} · Chưa rõ kết quả`, danhSach);
              }
            }
          }
        } catch {
          if (!daDong) {
            danhSach.replaceChildren();
            nut("li", "Chưa đọc được các lượt chưa rõ kết quả.", danhSach);
          }
        }
      })(),
    ]);
  }

  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (luu.disabled) return;
    if (dangLuu || dangTai) return;
    if (!kiemNhap()) {
      thongBao.textContent = "Cần sửa các trường được đánh dấu trước khi lưu.";
      return;
    }
    const moi = giaTriNhap();
    dangLuu = true; taiLai.disabled = true;
    luu.disabled = true;
    try {
      const ketQua = await cong.cau_hinh.luu(moi, phien);
      phien = ketQua.phien_ban_cau_hinh;
      cauHinh = moi;
      thongBao.textContent = "Đã lưu cấu hình OCR.";
      await refresh();
    } catch (loi) {
      if (loi?.ma === "NGAN_XUNG_DOT" || loi?.status === 409) {
        thongBao.textContent = "Cấu hình đã được người khác sửa. Hãy bấm Tải lại cấu hình trước khi lưu lại.";
        dangLuu = false; taiLai.disabled = false;
        return; // Giữ khóa Lưu cho tới khi đã đọc phiên mới.
      }
      thongBao.textContent = "Chưa lưu được cấu hình. Hãy thử lại.";
    }
    dangLuu = false; taiLai.disabled = false;
    if (!daDong) luu.disabled = false;
  });
  taiLai.addEventListener("click", async () => {
    if (dangTai || dangLuu || daDong) return;
    dangTai = true; taiLai.disabled = true; luu.disabled = true;
    try {
      await taiCauHinh();
      thongBao.textContent = "Đã tải lại cấu hình.";
      await refresh();
    } catch {
      thongBao.textContent = "Chưa đọc được cấu hình. Hãy thử lại.";
    } finally {
      dangTai = false;
      if (!daDong) taiLai.disabled = false;
    }
  });
  try {
    await taiCauHinh();
  } catch {
    thongBao.textContent = "Chưa đọc được cấu hình. Hãy bấm Tải lại cấu hình.";
  }
  await refresh();
  const chuKy = lapLai(() => { if (!daDong) void refresh(); }, 30000);
  return {refresh, destroy() { daDong = true; dungLap(chuKy); goc.replaceChildren(); }};
}

export default mount;
