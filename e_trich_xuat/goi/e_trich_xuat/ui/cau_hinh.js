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
  form.append(nhan, o, luu, bao);
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
        ? "Cấu hình đã được người khác thay đổi. Hãy mở lại màn hình rồi lưu."
        : "Không lưu được cấu hình. Hãy thử lại.";
    } finally {
      if (!daDong) luu.disabled = false;
    }
  };
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
  };
}

export default nap;
