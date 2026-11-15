// Màn module: Core truyền phần tử gốc và SDK trình duyệt khi nạp.
export default async function cauHinh(goc, KttCore = globalThis.KttCore) {
  const api = KttCore.engine("e_hoi_ai");
  const doc = goc.ownerDocument;
  function tao(the, chu, cha = goc) {
    const el = doc.createElement(the);
    if (chu !== undefined) el.textContent = chu;
    cha.appendChild(el);
    return el;
  }
  function oNhap(cha, ten, kieu = "text") {
    const nhan = tao("label", ten, cha);
    const o = tao("input", undefined, nhan);
    o.type = kieu;
    return o;
  }
  goc.replaceChildren();
  goc.classList.add("ktt-hoi-ai-cau-hinh");
  const css = tao("style");
  css.textContent = `.ktt-hoi-ai-cau-hinh{font-family:inherit;color:#20384a;max-width:72rem}
    .ktt-hoi-ai-cau-hinh fieldset{border:1px solid #b6c8d4;padding:1.25rem;margin:0 0 1.5rem}
    .ktt-hoi-ai-cau-hinh legend{font-size:1.25rem;font-weight:600;padding:0 .5rem}
    .ktt-hoi-ai-cau-hinh label{display:flex;flex-direction:column;gap:.4rem;margin:.75rem 0;flex:1;min-width:12rem}
    .ktt-hoi-ai-cau-hinh input,.ktt-hoi-ai-cau-hinh select{font:inherit;padding:.55rem;border:1px solid #7995a8;border-radius:3px;max-width:100%;box-sizing:border-box}
    .ktt-hoi-ai-cau-hinh button{font:inherit;padding:.55rem .9rem;margin:.4rem .5rem .4rem 0;cursor:pointer}
    .ktt-hoi-ai-cau-hinh button:focus-visible,.ktt-hoi-ai-cau-hinh input:focus-visible,.ktt-hoi-ai-cau-hinh select:focus-visible{outline:3px solid #1673aa;outline-offset:2px}
    .ktt-hoi-ai-cau-hinh .quy-tac{display:flex;gap:1rem;flex-wrap:wrap;border-top:1px solid #d3dee6;padding-top:.5rem}
    .ktt-hoi-ai-cau-hinh [role=alert]{color:#9b2323}
    .ktt-hoi-ai-cau-hinh p{max-width:75ch;line-height:1.5}`;
  const form = tao("form");
  const local = tao("fieldset", undefined, form);
  tao("legend", "Cổng Local AI", local);
  const url = oNhap(local, "Địa chỉ máy Local AI", "url");
  url.required = true;
  url.placeholder = "http://127.0.0.1:12345";
  const timeout = oNhap(local, "Thời hạn chờ (giây)", "number");
  timeout.required = true;
  timeout.min = "0.01";
  timeout.max = "600";
  timeout.step = "any";
  const trangThai = tao("p", "Đang tải trạng thái…", local);
  tao("h3", "Model đã phát hiện", local);
  const dsModel = tao("ul", undefined, local);
  tao("h3", "Model cho từng mẫu mã prompt", local);
  tao("p", "Xét theo thứ tự từ trên xuống. Có thể dùng * để khớp nhiều mã prompt.", local);
  const dsQuyTac = tao("div", undefined, local);
  const them = tao("button", "Thêm quy tắc", local);
  them.type = "button";
  const luu = tao("button", "Lưu", local);
  luu.type = "submit";
  luu.disabled = true;
  const thongBao = tao("p", "", local);
  thongBao.setAttribute("role", "status");
  thongBao.setAttribute("aria-live", "polite");
  const cloud = tao("fieldset", undefined, form);
  tao("legend", "Cổng Cloud AI", cloud);
  tao("p", "Chưa áp dụng ở bản 1", cloud);
  let phienBan = null;
  let models = [];
  let cacQuyTac = [];
  function themQuyTac(q = {}) {
    const hang = tao("div", undefined, dsQuyTac);
    hang.classList.add("quy-tac");
    const mau = oNhap(hang, "Mẫu mã prompt");
    mau.required = true;
    mau.value = q.mau_ma_prompt || "";
    const nhan = tao("label", "Model ưu tiên", hang);
    const model = tao("select", undefined, nhan);
    model.required = true;
    const trong = tao("option", "Chọn model", model);
    trong.value = "";
    const ids = [...new Set([...models.map(m => m.id_model), ...(q.uu_tien ? [q.uu_tien] : [])])];
    for (const id of ids) {
      const opt = tao("option", id, model);
      opt.value = id;
    }
    model.value = q.uu_tien || "";
    const duPhong = oNhap(hang, "Model dự phòng (cách nhau bằng dấu phẩy)");
    duPhong.value = (q.du_phong || []).join(", ");
    const bo = tao("button", "Bỏ quy tắc", hang);
    bo.type = "button";
    const quyTac = {mau, model, duPhong};
    cacQuyTac.push(quyTac);
    bo.addEventListener("click", () => {
      cacQuyTac = cacQuyTac.filter(qt => qt !== quyTac);
      hang.remove();
    });
  }
  them.addEventListener("click", () => themQuyTac());
  form.addEventListener("submit", async ev => {
    ev.preventDefault();
    if (luu.disabled || !form.reportValidity()) return;
    const giay = Number(timeout.value);
    if (!Number.isFinite(giay) || giay <= 0 || giay > 600) return;
    const giaTri = {local_ai: {url: url.value.trim(), timeout_giay: giay},
      quy_tac_model: cacQuyTac.map(q => ({mau_ma_prompt: q.mau.value.trim(),
        uu_tien: q.model.value, du_phong: q.duPhong.value.split(",").map(s => s.trim()).filter(Boolean)}))};
    luu.disabled = true;
    thongBao.textContent = "Đang lưu…";
    try {
      const kq = await api.cau_hinh.luu(giaTri, phienBan);
      phienBan = kq.phien_ban_cau_hinh;
      thongBao.setAttribute("role", "status");
      thongBao.textContent = "Đã lưu cấu hình. Trạng thái sẽ cập nhật sau lượt kiểm Local tiếp theo.";
    } catch (loi) {
      thongBao.setAttribute("role", "alert");
      thongBao.textContent = loi.ma === "NGAN_XUNG_DOT" || loi.code === "NGAN_XUNG_DOT" || loi.status === 409
        ? "Cấu hình đã được người khác thay đổi. Hãy tải lại màn hình trước khi lưu."
        : "Không lưu được cấu hình. Hãy kiểm tra các ô nhập và thử lại.";
    } finally {
      luu.disabled = false;
    }
  });
  try {
    const kq = await api.cau_hinh.doc();
    const ch = kq.cau_hinh || {};
    phienBan = kq.phien_ban_cau_hinh;
    url.value = ch.local_ai?.url || "";
    timeout.value = String(ch.local_ai?.timeout_giay ?? 60);
    let tiep = null;
    do {
      const trang = await api.ngan.tim("model_phat_hien", {loc: {url: url.value}, gioi_han: 500, tiep});
      models.push(...trang.danh_sach.map(b => b.gia_tri));
      tiep = trang.tiep;
    } while (tiep);
    models.sort((a, b) => a.thu_tu - b.thu_tu);
    trangThai.textContent = models.length
      ? (models.some(m => m.kha_dung)
        ? "Local có model khả dụng ở lần kiểm gần nhất."
        : "Local chưa có model khả dụng ở lần kiểm gần nhất. Hãy kiểm tra máy AI.")
      : "Chưa có kết quả kiểm Local cho địa chỉ này. Lưu cấu hình để engine kiểm khi nhận việc.";
    const lanKiem = models.map(m => m.kiem_luc).filter(Boolean).sort().at(-1);
    if (lanKiem && Number.isFinite(Date.parse(lanKiem))) {
      trangThai.textContent += " Kiểm lúc " + new Intl.DateTimeFormat("vi-VN", {
        day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
      }).format(new Date(lanKiem)) + ".";
    }
    url.addEventListener("input", () => {
      trangThai.textContent = "Địa chỉ đang sửa; lưu rồi tải lại màn hình để xem kết quả kiểm của địa chỉ mới.";
    });
    for (const m of models) tao("li", `${m.id_model}: ${m.kha_dung ? "Khả dụng ở lần kiểm gần nhất" : "Chưa khả dụng"}`, dsModel);
    for (const q of ch.quy_tac_model || []) themQuyTac(q);
    luu.disabled = false;
  } catch {
    trangThai.textContent = "Chưa đọc được cấu hình hoặc danh sách model. Hãy tải lại màn hình.";
    trangThai.setAttribute("role", "alert");
  }
}
