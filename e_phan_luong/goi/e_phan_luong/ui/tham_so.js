import {NANG_LUC, TRAN, TEN_O, MAU, COT, CO, CHINH_SACH, SoJson, chuSo, sao,
  vietJson, docThamSo, doi, xuatThamSo, kiemThamSo, hienTien} from "./du_lieu_tham_so.js";

const TEN_NANG_LUC = {"audit.phan_luong@1": "Phân luồng kiểm tra", "audit.chuan_bi_phan_loai@1": "Chuẩn bị phân loại bằng Local AI",
  "audit.phan_luong_sau_ai@1": "Phân luồng sau Local AI", "audit.phan_luong_hoa_don@1": "Phân luồng hóa đơn", "audit.ghi_ket_qua@1": "Ghi kết quả kiểm"};
const HUONG_DAN = {
  danh_muc_loai_json: "Đặt tên các loại nghiệp vụ dùng trong bước. Bỏ thiết lập để dùng danh mục rỗng; tối đa 100 loại.",
  bo_phan_loai_json: "Xét từ trên xuống, quy tắc khớp đầu tiên được dùng. Module đã gán loại thì ưu tiên loại của module. Bỏ thiết lập để không dùng quy tắc.",
  nguong_json: "Ngưỡng trong tệp được ưu tiên. Bước dùng giá trị này khi tệp không có ngưỡng. Bỏ thiết lập thì tệp phải gửi đủ PM, TE, SAD.",
  chinh_sach_json: "Chỉ dành cho quản trị viên. Trường chưa chỉnh giữ giá trị mặc định của engine. Bỏ thiết lập để dùng toàn bộ mặc định.",
  khuon_cot_json: "Ánh xạ tiêu đề Excel/CSV vào trường nghiệp vụ. Bỏ thiết lập khi chỉ nhận lô JSON; Excel/CSV cần có khuôn cột.",
};
let soMan = 0;

// D2 chưa có trong SDK: doc_tham_so/luu_tham_so là callback của màn bước Core,
// không phải API mới của engine. Không ghi tham số bước vào cấu hình engine.
export async function mount(goc, {KttCore = globalThis.KttCore, nang_luc,
  tham_so = {}, phien_ban_tham_so = null, doc_tham_so, luu_tham_so} = {}) {
  const doc = goc.ownerDocument, tienTo = `pl-ts-${++soMan}`;
  let mo, phienBan = Number.isSafeInteger(phien_ban_tham_so) && phien_ban_tham_so >= 0 ? phien_ban_tham_so : null,
    daDong = false, dangXuLy = false, tranhChap = false,
    luot = 0, thongDiep = "", loaiThongBao = "", coCong = false, soO = 0;
  const oNhap = new Map(), loiNgoai = new Map(), chiTiet = new Map(), chonLoai = [];
  try { coCong = !!KttCore?.engine?.("e_phan_luong"); } catch { /* Core chưa cấp cổng. */ }
  function tao(ten, chu, cha, lop) {
    const e = doc.createElement(ten); if (chu !== undefined) e.textContent = chu;
    if (lop) e.className = lop; if (cha) cha.appendChild(e); return e;
  }
  const nut = (ten, cha, ham, lop = "") => {
    const e = tao("button", ten, cha, lop); e.type = "button";
    e.addEventListener("click", ham); return e;
  };
  function capNhat(k, ham, ve = false) {
    if (dangXuLy || daDong) return;
    ham(); mo.da_doi.add(k); delete mo.loi_doc[k]; thongDiep = ""; loaiThongBao = "";
    if (ve) veMan(); else {
      if (k === "danh_muc_loai_json") for (const {e, r} of chonLoai) {
        e.replaceChildren();
        for (const [ma, ten] of luaChonLoai(r)) { const op = tao("option", ten, e); op.value = ma; }
        e.value = r.loai;
      }
      kiem();
    }
  }
  function o(cha, k, d, ten, huongDan, giaTri, sua, {kieu = "text", mau = "", chon, rong = false, docChi = false} = {}) {
    const b = tao("div", undefined, cha, "pl-ts-o"), id = `${tienTo}-${++soO}`;
    const nhan = tao("label", ten, b); nhan.htmlFor = id;
    const e = tao(chon ? "select" : kieu === "textarea" ? "textarea" : "input", undefined, b);
    e.id = id; e.setAttribute("data-o", [k, ...d].join("."));
    if (chon) for (const [v, t] of chon) { const op = tao("option", t, e); op.value = v; }
    else if (kieu !== "textarea") e.type = kieu;
    if (kieu === "checkbox") e.checked = !!giaTri;
    else e.value = giaTri ?? "";
    if (kieu === "number") { e.step = "any"; e.inputMode = "decimal"; }
    e.placeholder = mau; e.readOnly = docChi;
    if (rong) b.className += " pl-ts-rong";
    const goiY = tao("small", huongDan, b); goiY.id = id + "-goiy";
    const loi = tao("small", "", b, "pl-ts-loi"); loi.id = id + "-loi";
    e.setAttribute("aria-describedby", `${goiY.id} ${loi.id}`);
    oNhap.set(JSON.stringify([k, ...d]), {e, loi});
    if (sua) e.addEventListener(chon || kieu === "checkbox" ? "change" : "input", () => {
      capNhat(k, () => sua(kieu === "checkbox" ? e.checked : e.value));
    });
    return e;
  }
  function dsTu(cha, k, d, ten, ds, sua, huongDan, mau) {
    // Mỗi từ một ô riêng: giữ nguyên từ khóa chứa dấu phẩy, dấu | hoặc xuống dòng.
    const n = tao("fieldset", undefined, cha, "pl-ts-tu"); tao("legend", ten, n);
    tao("p", huongDan, n, "pl-ts-goiy");
    ds.forEach((tu, i) => {
      const hang = tao("div", undefined, n, "pl-ts-hang-tu");
      o(hang, k, [...d, i], `Từ khóa ${i + 1}`, "Một cụm từ; giữ nguyên dấu câu.", tu, v => { ds[i] = v; sua(ds); }, {mau});
      nut("Xóa từ", hang, () => capNhat(k, () => sua(ds.filter((_, j) => j !== i)), true));
    });
    nut("Thêm từ khóa", n, () => capNhat(k, () => sua([...ds, ""]), true));
    return n;
  }
  function sapXep(cha, k, ds, i) {
    const len = nut("Lên", cha, () => capNhat(k, () => { [ds[i - 1], ds[i]] = [ds[i], ds[i - 1]]; }, true));
    len.disabled = i === 0; len.setAttribute("aria-label", `Đưa quy tắc ${i + 1} lên`);
    const xuong = nut("Xuống", cha, () => capNhat(k, () => { [ds[i + 1], ds[i]] = [ds[i], ds[i + 1]]; }, true));
    xuong.disabled = i === ds.length - 1; xuong.setAttribute("aria-label", `Đưa quy tắc ${i + 1} xuống`);
  }
  function veDanhMuc(cha, k, ds) {
    const bang = tao("div", undefined, cha, "pl-ts-danh-muc");
    ds.forEach((r, i) => {
      const hang = tao("fieldset", undefined, bang, "pl-ts-dong"); tao("legend", `Loại ${i + 1}`, hang);
      const luoi = tao("div", undefined, hang, "pl-ts-luoi");
      o(luoi, k, [i, "ten"], "Tên loại", "Tên dễ nhận ra khi chọn phân loại.", r.ten, v => { r.ten = v; }, {mau: "Thanh toán DEMO"});
      o(luoi, k, [i, "mo_ta"], "Mô tả", "Phạm vi dùng loại này; có thể để trống.", r.mo_ta, v => { r.mo_ta = v; }, {mau: "Thanh toán nhà cung cấp DEMO"});
      const nc = tao("details", undefined, hang); tao("summary", "Nâng cao · mã loại", nc);
      o(nc, k, [i, "ma"], "Mã loại", "Mã dùng để nối module và quy tắc. Đổi mã cần cập nhật các chỗ đang dùng.", r.ma, v => { r.ma = v; }, {mau: "thanh_toan_demo"});
      // Tham chiếu ngoài danh mục sẽ được đánh dấu, không tự đổi loại quy tắc.
      nut("Xóa loại", hang, () => capNhat(k, () => ds.splice(i, 1), true));
    });
    nut("Thêm loại", cha, () => capNhat(k, () => ds.push({ma: "", ten: "", mo_ta: ""}), true));
  }
  function luaChonLoai(r) {
    const danhMuc = (Array.isArray(mo.du_lieu.danh_muc_loai_json) ? mo.du_lieu.danh_muc_loai_json : []).filter(x => x && typeof x === "object");
    const ds = [["", "Chọn loại nghiệp vụ"], ...danhMuc.map(x => [x.ma, x.ten])];
    if (r.loai && !danhMuc.some(x => x.ma === r.loai)) ds.push([r.loai, "Loại đã không còn trong danh mục"]);
    return ds;
  }
  function veBo(cha, k, bo) {
    const danhMuc = (Array.isArray(mo.du_lieu.danh_muc_loai_json) ? mo.du_lieu.danh_muc_loai_json : []).filter(x => x && typeof x === "object");
    bo.quy_tac.forEach((r, i) => {
      const hang = tao("fieldset", undefined, cha, "pl-ts-dong"); tao("legend", `Quy tắc ${i + 1}`, hang);
      const e = o(hang, k, ["quy_tac", i, "loai"], "Gán vào loại", "Chọn từ danh mục loại ở trên.", r.loai, v => { r.loai = v; }, {chon: luaChonLoai(r)});
      chonLoai.push({e, r});
      r.khi.forEach((dk, j) => {
        const dkCha = tao("fieldset", undefined, hang, "pl-ts-dieu-kien"); tao("legend", `Điều kiện ${j + 1}${j ? " · hoặc" : ""}`, dkCha);
        tao("p", "Phải khớp ít nhất một từ trong mỗi nhóm bên dưới và không khớp từ loại trừ. Dùng = để khớp nguyên từ, # cho một hoặc nhiều chữ số; không dùng regex.", dkCha, "pl-ts-goiy");
        dk.tat_ca.forEach((nhom, m) => {
          dsTu(dkCha, k, ["quy_tac", i, "khi", j, "tat_ca", m], `Nhóm bắt buộc ${m + 1}`, nhom,
            v => { dk.tat_ca[m] = v; }, "Trong nhóm: chỉ cần một từ khớp. Giữa các nhóm: phải cùng khớp.", "=chi");
          nut("Xóa nhóm", dkCha, () => capNhat(k, () => dk.tat_ca.splice(m, 1), true));
        });
        nut("Thêm nhóm bắt buộc", dkCha, () => capNhat(k, () => dk.tat_ca.push([""]), true));
        dsTu(dkCha, k, ["quy_tac", i, "khi", j, "khong_co"], "Loại trừ", dk.khong_co ?? [], v => { dk.khong_co = v; }, "Có bất kỳ từ nào ở đây thì điều kiện không khớp.", "hủy");
        nut("Xóa điều kiện", dkCha, () => capNhat(k, () => r.khi.splice(j, 1), true));
      });
      const thaoTac = tao("div", undefined, hang, "pl-ts-thao-tac");
      nut("Thêm điều kiện hoặc", thaoTac, () => capNhat(k, () => r.khi.push({tat_ca: [[""]], khong_co: []}), true));
      sapXep(thaoTac, k, bo.quy_tac, i);
      nut("Xóa quy tắc", thaoTac, () => capNhat(k, () => bo.quy_tac.splice(i, 1), true));
    });
    nut("Thêm quy tắc", cha, () => capNhat(k, () => bo.quy_tac.push({loai: danhMuc[0]?.ma ?? "", khi: [{tat_ca: [[""]], khong_co: []}]}), true));
    const nc = tao("details", undefined, cha); tao("summary", "Nâng cao · phiên bản bộ", nc);
    o(nc, k, ["phien_ban"], "Phiên bản bộ", "Định dạng hiện hành: 1.", "1", null, {docChi: true});
  }
  function veNguong(cha, k, v) {
    const luoi = tao("div", undefined, cha, "pl-ts-luoi");
    const teKhac = [v.pm?.tien_te, v.te?.tien_te, v.sad?.tien_te].some(x => x !== v.pm?.tien_te);
    if (!teKhac) o(luoi, k, ["pm", "tien_te"], "Tiền tệ của ba ngưỡng", "Mã 3 chữ in hoa; không tự quy đổi tiền tệ.", v.pm?.tien_te ?? "", x => {
      for (const t of ["pm", "te", "sad"]) v[t].tien_te = x;
    }, {mau: "VND"});
    for (const [ten, nhan] of [["pm", "PM · Trọng yếu tổng thể"], ["te", "TE · Sai sót có thể chấp nhận"], ["sad", "SAD · Ngưỡng sai sót nhỏ"]]) {
      const r = v[ten];
      if (teKhac) o(luoi, k, [ten, "tien_te"], `Tiền tệ ${ten.toUpperCase()}`, "Sửa về cùng một mã tiền tệ cho ba ngưỡng.", r.tien_te, x => { r.tien_te = x; }, {mau: "VND"});
      const e = o(luoi, k, [ten, "so"], nhan, "Nhập đầy đủ số tiền; dùng dấu chấm cho phần lẻ, không gõ dấu phân cách hàng nghìn.", chuSo(r.so), x => { r.so = x; }, {kieu: "number", mau: "1000000"});
      const hien = tao("output", hienTien(r.so, r.tien_te), e.parentNode, "pl-ts-tien");
      hien.setAttribute("data-tien", ten);
    }
    tao("p", "Điều kiện: 0 < SAD < TE ≤ PM. Ngưỡng áp dụng theo trị tuyệt đối của số tiền.", cha, "pl-ts-goiy");
  }
  function veChinhSach(cha, k, v) {
    const giaTri = ten => Object.hasOwn(v, ten) ? v[ten]
      : ten === "ty_le_duoi_sad" && Object.hasOwn(mo.goc, ten) ? mo.goc[ten] : CHINH_SACH[ten];
    const dsSo = (chaCon, ten, nhan, huongDan, mau) => {
      const nhom = tao("fieldset", undefined, chaCon, "pl-ts-dong"); tao("legend", nhan, nhom);
      tao("p", huongDan, nhom, "pl-ts-goiy");
      const ds = giaTri(ten);
      ds.forEach((x, i) => {
        const dong = tao("div", undefined, nhom, "pl-ts-hang-tu");
        o(dong, k, [ten, i], `Mức ${i + 1}`, ten === "mau_toi_thieu" ? "Số nguyên dương." : "Tỷ lệ dạng số từ 0 đến 1 (0.30 = 30%).", chuSo(x), y => {
          v[ten] = sao(giaTri(ten)); v[ten][i] = new SoJson(y);
        }, {kieu: "number", mau});
        nut("Xóa mức", dong, () => capNhat(k, () => { v[ten] = sao(giaTri(ten)); v[ten].splice(i, 1); }, true));
      });
      nut("Thêm mức", nhom, () => capNhat(k, () => { v[ten] = sao(giaTri(ten)); v[ten].push(new SoJson("0")); }, true));
    };
    const luoi = tao("div", undefined, cha, "pl-ts-luoi");
    for (const [ten, nhan, huongDan, mau] of [
      ["ty_le_chua_phan_loai", "Tỷ lệ kiểm loại chưa phân loại", "Tỷ lệ từ 0 đến 1; 0.30 tương ứng 30%.", "0.30"],
      ["ty_le_duoi_sad", "Tỷ lệ kiểm dưới SAD", "Tỷ lệ từ 0 đến 1; JSON chính sách ưu tiên hơn ô tỷ lệ của bước.", "0.02"],
      ["mau_sach_toan_bo", "Mẫu sạch để rời kiểm toàn bộ", "Số nguyên dương; mặc định 30 mẫu.", "30"],
    ]) o(luoi, k, [ten], nhan, huongDan, chuSo(giaTri(ten)), x => { v[ten] = new SoJson(x); }, {kieu: "number", mau});
    const nc = tao("details", undefined, cha); tao("summary", "Nâng cao · bậc, thống kê và hệ số", nc);
    dsSo(nc, "bac", "Các bậc kiểm tra", "Xếp từ cao xuống thấp. Thêm hoặc xóa bậc cần sửa đồng thời hai danh sách bên dưới.", "0.30");
    dsSo(nc, "nguong_xuong", "Ngưỡng xuống bậc", "Số dòng bằng số bậc trừ 1; tỷ lệ từ 0 đến 1.", "0.10");
    dsSo(nc, "mau_toi_thieu", "Mẫu tối thiểu khi xuống bậc", "Số dòng bằng số bậc trừ 1; mỗi mức là số nguyên dương.", "30");
    const thongKe = tao("div", undefined, nc, "pl-ts-luoi");
    for (const [ten, nhan, huongDan, mau] of [
      ["nguong_diem_rui_ro", "Ngưỡng điểm rủi ro", "Từ 0 đến 1; 0.10 tương ứng 10%.", "0.10"],
      ["do_tin_cay", "Độ tin cậy", "Lớn hơn 0 và nhỏ hơn 1; 0.95 tương ứng 95%.", "0.95"],
      ["san", "Tỷ lệ sàn vùng chọn mẫu", "Từ 0 đến 1; 0.05 tương ứng 5%.", "0.05"],
      ["don_vi_so_tron", "Đơn vị nhận diện số tròn", "Số nguyên dương, theo tiền tệ ngưỡng của lô.", "10000000"],
      ["toi_thieu_ho_so_doi_tac_moi", "Nghiệp vụ tối thiểu xét đối tác mới", "Số nguyên từ 0; 0 nghĩa là xét ngay từ lượt đầu.", "0"],
    ]) o(thongKe, k, [ten], nhan, huongDan, chuSo(giaTri(ten)), x => { v[ten] = new SoJson(x); }, {kieu: "number", mau});
    for (const [co, ten] of Object.entries(CO)) o(thongKe, k, ["he_so", co], `Hệ số · ${ten}`, "Từ 1 trở lên; nhân tỷ lệ kiểm khi có cờ tương ứng.", chuSo(v.he_so?.[co] ?? CHINH_SACH.he_so[co]), x => {
      if (!v.he_so) v.he_so = {}; v.he_so[co] = new SoJson(x);
    }, {kieu: "number", mau: "1.5"});
    nut("Dùng lại mặc định", cha, () => capNhat(k, () => doi(mo, k, {}), true));
  }
  function veKhuon(cha, k, v) {
    o(cha, k, ["sheet"], "Tên sheet", "Để trống để tự dò sheet có tiêu đề phù hợp; CSV không cần tên sheet.", v.sheet ?? "", x => { v.sheet = x === "" ? null : x; }, {mau: "Nghiệp vụ DEMO"});
    v.cot.forEach((r, i) => {
      const hang = tao("fieldset", undefined, cha, "pl-ts-dong"); tao("legend", `Cột ${i + 1}`, hang);
      const luoi = tao("div", undefined, hang, "pl-ts-luoi");
      const custom = r.ma?.startsWith("thuoc_tinh.");
      const e = o(luoi, k, ["cot", i, "ma"], "Trường nghiệp vụ", "Mã, ngày và số tiền phải có và bật bắt buộc.", custom ? "thuoc_tinh" : r.ma,
        x => { r.ma = x === "thuoc_tinh" ? "thuoc_tinh." : x; }, {chon: [...Object.entries(COT), ["thuoc_tinh", "Thuộc tính bổ sung"]]});
      e.addEventListener("change", () => { if (!dangXuLy) veMan(); });
      if (custom) o(luoi, k, ["cot", i, "thuoc_tinh"], "Tên thuộc tính bổ sung", "Khóa trong thuoc_tinh; chỉ nhập phần sau dấu chấm.", r.ma.slice(11), x => { r.ma = "thuoc_tinh." + x; }, {mau: "bo_phan_demo"});
      o(luoi, k, ["cot", i, "bat_buoc"], "Cột bắt buộc", "Tệp thiếu cột này sẽ bị từ chối.", r.bat_buoc, x => { r.bat_buoc = x; }, {kieu: "checkbox"});
      dsTu(hang, k, ["cot", i, "tu_khoa"], "Các tên tiêu đề được chấp nhận", r.tu_khoa, x => { r.tu_khoa = x; }, "Mỗi ô là một tên tiêu đề; so sánh bỏ dấu và không phân biệt hoa thường.", "Số tiền");
      nut("Xóa cột", hang, () => capNhat(k, () => v.cot.splice(i, 1), true));
    });
    nut("Thêm cột", cha, () => capNhat(k, () => v.cot.push({ma: "", tu_khoa: [""], bat_buoc: false}), true));
    dsTu(cha, k, ["dong_dung"], "Dòng kết thúc bảng", v.dong_dung, x => { v.dong_dung = x; }, "Gặp giá trị này ở ô có nội dung đầu tiên của dòng thì dừng đọc bảng.", "Tổng cộng");
  }
  function kiem() {
    if (daDong || !mo) return [];
    for (const {e, loi} of oNhap.values()) { loi.textContent = ""; e.setAttribute("aria-invalid", "false"); }
    for (const e of loiNgoai.values()) e.replaceChildren();
    const ds = kiemThamSo(mo, nang_luc);
    for (const r of ds) {
      let gan;
      for (let i = r.duong_dan.length; i >= 0 && !gan; i--) gan = oNhap.get(JSON.stringify([r.truong, ...r.duong_dan.slice(0, i)]));
      if (gan) { gan.e.setAttribute("aria-invalid", "true"); gan.loi.textContent = r.thong_diep;
        let cha = gan.e.parentNode; while (cha && cha !== goc) { if (cha.tagName === "DETAILS") cha.open = true; cha = cha.parentNode; }
      }
      else tao("p", r.thong_diep, loiNgoai.get(r.truong), "pl-ts-loi");
    }
    for (const [k, e] of chiTiet) {
      try { e.textContent = mo.du_lieu[k] === null ? "(tham số để trống)" : vietJson(mo.du_lieu[k], true); }
      catch { e.textContent = "Có ô số chưa hợp lệ; sửa ô đánh dấu để xem JSON."; }
    }
    for (const ten of ["pm", "te", "sad"]) {
      const hien = goc.querySelector?.(`[data-tien="${ten}"]`);
      if (hien && mo.du_lieu.nguong_json?.[ten]) hien.textContent = hienTien(mo.du_lieu.nguong_json[ten].so, mo.du_lieu.nguong_json[ten].tien_te);
    }
    const bao = goc.querySelector?.("[data-thong-bao]");
    if (bao) { bao.textContent = thongDiep || (ds.length ? `Có ${ds.length} lỗi cần sửa trước khi lưu.` : "Các giá trị đang nhập hợp lệ."); bao.className = `pl-ts-bao ${loaiThongBao || (ds.length ? "pl-ts-bao-loi" : "")}`; }
    const luu = goc.querySelector?.("[data-luu]"); if (luu) luu.disabled = dangXuLy || tranhChap || !coCong || !luu_tham_so || phienBan === null || ds.length > 0;
    return ds;
  }
  function veMan() {
    if (daDong) return;
    goc.replaceChildren(); goc.classList.add("pl-ts"); soO = 0; oNhap.clear(); loiNgoai.clear(); chiTiet.clear(); chonLoai.length = 0;
    const dau = tao("header", undefined, goc, "pl-ts-dau");
    const ten = tao("div", undefined, dau); tao("h2", "Cài đặt bước", ten); tao("p", TEN_NANG_LUC[nang_luc] ?? "Phân luồng kiểm tra", ten);
    tao("span", "Chỉ quản trị viên", dau, "pl-ts-nhan");
    if (!coCong || !luu_tham_so || phienBan === null) tao("p", "Chưa nối bộ lưu tham số của Core. Có thể soạn và kiểm tra; thay đổi chỉ được giữ trong phiên này.", goc, "pl-ts-canh-bao");
    if (!mo) { tao("p", thongDiep, goc, "pl-ts-canh-bao"); return; }
    const form = tao("form", undefined, goc); form.noValidate = true;
    form.addEventListener("submit", async e => { e.preventDefault(); await luu(); });
    const toanBo = tao("fieldset", undefined, form, "pl-ts-toan-bo"); toanBo.disabled = dangXuLy || tranhChap;
    for (const k of NANG_LUC[nang_luc]) {
      const s = tao("section", undefined, toanBo, "pl-ts-the");
      const dauThe = tao("div", undefined, s, "pl-ts-dau-the");
      tao("h3", `▤  ${TEN_O[k]}`, dauThe);
      tao("span", mo.du_lieu[k] === null ? "Chưa thiết lập" : "Đã thiết lập", dauThe, "pl-ts-trang-thai");
      const than = tao("div", undefined, s, "pl-ts-than-the"); tao("p", HUONG_DAN[k], than, "pl-ts-goiy");
      loiNgoai.set(k, tao("div", undefined, than));
      const v = mo.du_lieu[k];
      // Dữ liệu cũ sai cấu trúc không bị đổ vào form và tự ghi đè. Giữ gốc ở Nâng cao.
      const laObj = x => x !== null && typeof x === "object" && !Array.isArray(x) && !(x instanceof SoJson);
      const loiCauTruc = v !== null && !({
        danh_muc_loai_json: () => Array.isArray(v) && v.every(laObj),
        bo_phan_loai_json: () => laObj(v) && Array.isArray(v.quy_tac) && v.quy_tac.every(r => laObj(r) && Array.isArray(r.khi) && r.khi.every(dk => laObj(dk) && Array.isArray(dk.tat_ca) && dk.tat_ca.every(Array.isArray) && (dk.khong_co === undefined || Array.isArray(dk.khong_co)))) && (mo.du_lieu.danh_muc_loai_json === null || Array.isArray(mo.du_lieu.danh_muc_loai_json)),
        nguong_json: () => laObj(v) && ["pm", "te", "sad"].every(t => laObj(v[t])),
        chinh_sach_json: () => laObj(v) && ["bac", "nguong_xuong", "mau_toi_thieu"].every(t => v[t] === undefined || Array.isArray(v[t])),
        khuon_cot_json: () => laObj(v) && Array.isArray(v.cot) && v.cot.every(r => laObj(r) && Array.isArray(r.tu_khoa)) && Array.isArray(v.dong_dung),
      }[k])();
      if (v !== null && !loiCauTruc) {
        const ve = {danh_muc_loai_json: veDanhMuc, bo_phan_loai_json: veBo, nguong_json: veNguong, chinh_sach_json: veChinhSach, khuon_cot_json: veKhuon}[k];
        ve(than, k, v);
        nut("Bỏ thiết lập", than, () => capNhat(k, () => doi(mo, k, null), true));
      } else if (v === null && !mo.loi_doc[k]) tao("p", "Chưa có giá trị riêng cho bước này.", than, "pl-ts-trong");
      if (v === null || loiCauTruc) nut("Chèn mẫu DEMO", than, () => capNhat(k, () => doi(mo, k, sao(MAU[k])), true));
      if (mo.loi_doc[k] || loiCauTruc) nut("Bỏ giá trị lỗi", than, () => capNhat(k, () => doi(mo, k, null), true));
      const nc = tao("details", undefined, than); tao("summary", "Nâng cao · xem JSON và giới hạn", nc);
      tao("p", "JSON chỉ đọc; biểu mẫu ở trên tạo đúng chuỗi tham số hiện hành. Giá trị để trống có ý nghĩa như hướng dẫn đầu thẻ.", nc, "pl-ts-goiy");
      tao("p", `Giới hạn: ${TRAN[k].toLocaleString("vi-VN")} ký tự và byte UTF-8. Vượt trần cần giảm nội dung; không tự cắt bớt.`, nc, "pl-ts-goiy");
      const raw = tao("pre", "", nc); chiTiet.set(k, raw);
      if (mo.loi_doc[k]) { chiTiet.delete(k); raw.textContent = String(mo.goc[k] ?? ""); }
    }
    const cuoi = tao("footer", undefined, form, "pl-ts-cuoi");
    const bao = tao("div", thongDiep, cuoi, "pl-ts-bao"); bao.setAttribute("role", "status"); bao.setAttribute("aria-live", "polite"); bao.setAttribute("data-thong-bao", "");
    const cacNut = tao("div", undefined, cuoi, "pl-ts-thao-tac");
    nut("Kiểm tra cài đặt", cacNut, () => { const ds = kiem(); thongDiep = ds.length ? `Kiểm tra chưa đạt: cần sửa ${ds.length} lỗi được đánh dấu.` : "Kiểm tra đạt. Cài đặt đúng cấu trúc hiện hành."; kiem(); });
    const tai = nut("Tải lại", cacNut, refresh); tai.disabled = dangXuLy || !doc_tham_so;
    const ghi = tao("button", dangXuLy ? "Đang xử lý…" : "Lưu vào bước", cacNut, "pl-ts-chinh"); ghi.type = "submit"; ghi.setAttribute("data-luu", "");
    kiem();
  }
  function getValue() {
    if (!mo || daDong) throw new Error("Màn soạn chưa có dữ liệu.");
    const ds = kiem();
    if (ds.length) throw Object.assign(new Error("Cài đặt bước chưa hợp lệ."), {ma: "THAM_SO_KHONG_HOP_LE", loi: ds});
    return xuatThamSo(mo);
  }
  async function luu() {
    if (daDong || dangXuLy || tranhChap || !coCong || !luu_tham_so || phienBan === null) return;
    const ds = kiem(); if (ds.length) { thongDiep = "Cần sửa các ô đánh dấu trước khi lưu."; kiem(); return; }
    let giaTri;
    try { giaTri = getValue(); } catch { kiem(); return; }
    dangXuLy = true; const phien = ++luot; veMan();
    try {
      const kq = await luu_tham_so(giaTri, phienBan);
      if (daDong || phien !== luot) return;
      if (!kq || !Number.isSafeInteger(kq.phien_ban_tham_so) || kq.phien_ban_tham_so <= phienBan) throw new Error();
      phienBan = kq.phien_ban_tham_so; mo = docThamSo(giaTri, nang_luc);
      thongDiep = "Đã lưu cài đặt vào bước."; loaiThongBao = "pl-ts-bao-dat";
    } catch (e) {
      if (daDong || phien !== luot) return;
      tranhChap = e?.status === 409 || ["NGAN_XUNG_DOT", "CAU_HINH_XUNG_DOT", "THAM_SO_XUNG_DOT"].includes(e?.ma);
      thongDiep = tranhChap ? "Cài đặt bước đã được người khác sửa, tải lại trước khi lưu. Bản đang nhập vẫn được giữ để đối chiếu."
        : "Không lưu được cài đặt bước. Thử lại sau; bản đang nhập vẫn được giữ.";
      loaiThongBao = "pl-ts-bao-loi";
    } finally { if (!daDong && phien === luot) { dangXuLy = false; veMan(); } }
  }
  async function refresh() {
    if (daDong || dangXuLy || !doc_tham_so) return;
    dangXuLy = true; const phien = ++luot; thongDiep = "Đang tải cài đặt bước…"; veMan();
    try {
      const kq = await doc_tham_so();
      if (daDong || phien !== luot) return;
      if (!kq || !Number.isSafeInteger(kq.phien_ban_tham_so) || kq.phien_ban_tham_so < 0) throw new Error();
      const moi = docThamSo(kq.tham_so, nang_luc);
      mo = moi; phienBan = kq.phien_ban_tham_so; tranhChap = false; thongDiep = "Đã tải cài đặt bước."; loaiThongBao = "";
    } catch {
      if (daDong || phien !== luot) return;
      thongDiep = "Không đọc được cài đặt bước. Bấm Tải lại để thử lại."; loaiThongBao = "pl-ts-bao-loi";
    } finally { if (!daDong && phien === luot) { dangXuLy = false; veMan(); } }
  }
  try { mo = docThamSo(tham_so, nang_luc); } catch { thongDiep = "Không mở được trình soạn cho năng lực hoặc dữ liệu này."; }
  veMan(); if (doc_tham_so && mo) await refresh();
  return {getValue, validate: kiem, refresh, save: luu,
    destroy() { daDong = true; ++luot; oNhap.clear(); loiNgoai.clear(); chiTiet.clear(); chonLoai.length = 0; goc.replaceChildren(); goc.classList.remove("pl-ts"); }};
}
