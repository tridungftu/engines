// Màn module: chỉ dùng cổng Core; phiên bản CAS được giữ trong bộ nhớ.
export async function nap({ goc, KttCore = globalThis.KttCore }) {
  const doc = goc.ownerDocument;
  const cong = KttCore.engine("e_trich_xuat").cau_hinh;
  let phienBan = null;
  let daDong = false;
  const tao = (ten, chu) => {
    const el = doc.createElement(ten);
    if (chu !== undefined) el.textContent = chu;
    return el;
  };
  const form = tao("form");
  const nhan = tao("label", "Trần ngân sách đầu vào AI (token ước lượng)");
  const o = tao("input");
  o.type = "number";
  o.min = "1024";
  o.max = "100000";
  o.step = "1";
  o.required = true;
  o.value = "16000";
  o.id = "trich-ngan-sach";
  nhan.htmlFor = o.id;
  const luu = tao("button", "Lưu");
  luu.type = "submit";
  luu.disabled = true;
  const bao = tao("p");
  bao.setAttribute("role", "status");
  bao.setAttribute("aria-live", "polite");
  const huongDan = tao("p", "Giới hạn lượng nội dung gửi vào AI cho mỗi lần xử lý. Mặc định: 16.000 token; cho phép từ 1.024 đến 100.000 token.");
  const tieuDe = tao("h2", "▤  Ngân sách trích xuất");
  const trangThai = tao("span", "Cấu hình engine");
  const kieu = tao("style", `
    .tx-card{max-width:960px;background:#fff;border:1px solid #dce4ee;border-radius:14px;color:#18314d;font:16px system-ui,sans-serif;display:grid;grid-template-columns:1fr auto;gap:12px 24px;padding:28px}
    .tx-card h2{grid-column:1;margin:0 0 16px;font-size:22px;order:-3}.tx-card span{order:-2;color:#35644d;background:#edf7ef;border-radius:6px;padding:7px 12px;align-self:start}
    .tx-card label{grid-column:1/-1;font-weight:600}.tx-card input{grid-column:1/-1;box-sizing:border-box;width:100%;padding:14px;border:1px solid #cbd8e6;border-radius:7px;font:inherit;color:inherit}
    .tx-card .tx-guide{grid-column:1/-1;order:0;color:#61758c;margin:0 0 8px;line-height:1.5}.tx-card button{grid-column:1;justify-self:start;order:1;background:#204f80;color:white;border:0;border-radius:7px;padding:12px 24px;font:inherit;cursor:pointer}.tx-card button:disabled{opacity:.55;cursor:default}.tx-card .tx-status{grid-column:1/-1;order:2;margin:0;color:#914027}
    @media(max-width:600px){.tx-card{grid-template-columns:1fr;padding:20px}.tx-card span{grid-column:1}.tx-card h2{margin-bottom:0}}
  `);
  form.className = "tx-card";
  huongDan.className = "tx-guide";
  bao.className = "tx-status";
  o.setAttribute("aria-describedby", "tx-huong-dan tx-thong-bao");
  huongDan.id = "tx-huong-dan";
  bao.id = "tx-thong-bao";
  form.append(nhan, o, luu, bao, huongDan, tieuDe, trangThai, kieu);
  goc.replaceChildren(form);

  const khiLuu = async (suKien) => {
    suKien.preventDefault();
    if (luu.disabled || daDong) return;
    const n = Number(o.value);
    if (!/^\d+$/.test(o.value) || !Number.isInteger(n) || n < 1024 || n > 100000) {
      bao.textContent = "Nhập số nguyên từ 1.024 đến 100.000 token.";
      return;
    }
    luu.disabled = true;
    try {
      const kq = await cong.luu({ ngan_sach_token_vao_toi_da: n }, phienBan);
      if (daDong) return;
      if (kq?.phien_ban_cau_hinh == null) throw new Error();
      phienBan = kq.phien_ban_cau_hinh;
      bao.textContent = "Đã lưu cấu hình.";
    } catch (loi) {
      if (daDong) return;
      const ma = loi?.ma ?? loi?.code;
      bao.textContent = (ma === "NGAN_XUNG_DOT" || ma === "CAU_HINH_XUNG_DOT"
        || loi?.status === 409 || loi?.http_status === 409)
        ? "Cấu hình đã được người khác sửa, tải lại trước khi lưu."
        : "Không lưu được cấu hình. Hãy thử lại.";
    } finally {
      if (!daDong) luu.disabled = false;
    }
  };
  const khiNhap = () => {
    const n = Number(o.value);
    bao.textContent = /^\d+$/.test(o.value) && Number.isInteger(n) && n >= 1024 && n <= 100000
      ? "" : "Nhập số nguyên từ 1.024 đến 100.000 token.";
  };
  o.addEventListener("input", khiNhap);
  form.addEventListener("submit", khiLuu);
  try {
    const kq = await cong.doc();
    if (!daDong) {
      phienBan = kq?.phien_ban_cau_hinh ?? null;
      o.value = String(kq?.gia_tri?.ngan_sach_token_vao_toi_da ?? 16000);
      bao.textContent = kq?.gia_tri == null
        ? "Engine chưa được cấu hình. Giá trị đang hiển thị là đề xuất; bấm Lưu để áp dụng."
        : "";
      luu.disabled = false;
    }
  } catch {
    if (!daDong) bao.textContent = "Không đọc được cấu hình. Hãy mở lại màn hình.";
  }
  return () => {
    daDong = true;
    form.removeEventListener("submit", khiLuu);
    o.removeEventListener("input", khiNhap);
  };
}

export default nap;
