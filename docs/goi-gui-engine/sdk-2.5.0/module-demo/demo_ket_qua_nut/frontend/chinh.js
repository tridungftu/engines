const DUONG = '/api/v1/module/demo_ket_qua_nut/dot-demo';
const TRAN_HOI_MS = 120_000;
const NHAN = { DA_GUI: 'Đang chờ kết quả', XONG: 'Hoàn tất', LOI: 'Lỗi' };

export async function hienThi(target, { sdk, signal }) {
  const doc = target.ownerDocument;
  const el = (tag, text) => {
    const node = doc.createElement(tag);
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const khung = el('section');
  khung.className = 'demo-ket-qua-nut';
  const bao = el('div'), bang = el('div');
  bao.setAttribute('role', 'status');
  khung.append(el('h2', 'Kết quả theo đợt DEMO'), bao, bang);
  target.replaceChildren(khung);

  let dung = false, timer, dangGui = false, choLuu = null, batDauCho = null;
  const huy = () => { dung = true; clearTimeout(timer); };
  const donDep = () => { huy(); signal?.removeEventListener('abort', huy); target.replaceChildren(); };
  signal?.addEventListener('abort', huy, { once: true });
  const chiTiet = (root, ma, requestId) => {
    if (!ma && !requestId) return;
    const details = el('details');
    details.append(el('summary', 'Chi tiết hỗ trợ'),
      el('p', [ma, requestId].filter(Boolean).join(' · ')));
    root.append(details);
  };
  const hienLoi = loi => {
    bao.replaceChildren(el('p', loi.thong_diep || 'Chưa thực hiện được. Hãy thử lại.'));
    chiTiet(bao, loi.ma, loi.request_id);
  };
  const chuaDuocDung = () => {
    bao.replaceChildren(el('p', 'Bạn chưa được dùng chức năng gửi tệp của màn này.'));
  };
  try {
    const quyen = await sdk.api.goi({ duong_dan: '/api/v1/module/demo_ket_qua_nut/nut', signal });
    if (dung || signal?.aborted) return donDep;
    if (!Array.isArray(quyen?.nut) || !quyen.nut.some(n => n?.ma === 'xuat_thong_ke')) {
      chuaDuocDung();
      return donDep;
    }
  } catch (loi) {
    if (!dung && !signal?.aborted) {
      chuaDuocDung();
      chiTiet(bao, loi.ma, loi.request_id);
    }
    return donDep;
  }
  const form = el('form'), chon = el('select'), tep = el('input');
  const gui = el('button', 'Gửi tệp của đợt'), taiLai = el('button', 'Cập nhật kết quả');
  tep.type = 'file'; tep.accept = '.txt,text/plain'; tep.required = true;
  chon.required = true; gui.type = 'submit'; taiLai.type = 'button';
  const nhanDot = el('label', 'Đợt DEMO'), nhanTep = el('label', 'Tệp văn bản UTF-8');
  nhanDot.append(chon); nhanTep.append(tep);
  form.append(nhanDot, nhanTep, gui, taiLai);
  khung.replaceChildren(el('h2', 'Kết quả theo đợt DEMO'),
    el('p', 'Chọn đợt, gửi tệp văn bản và xem thống kê sau khi xử lý.'), form, bao, bang);
  sdk.nut.dat('xuat_thong_ke', gui, { tu_ve: true });
  const hetHanCho = () => {
    bao.textContent = 'Chưa có kết quả. Xem chi tiết ở mục Việc của tôi.';
  };
  function ve(danhSach) {
    bang.replaceChildren();
    if (!danhSach.length) { bang.append(el('p', 'Chưa có kết quả nào.')); return; }
    const table = el('table'), head = el('tr');
    for (const ten of ['Đợt DEMO', 'Trạng thái', 'Số dòng', 'Số từ', 'Dòng đầu', 'Thông báo']) {
      const th = el('th', ten); th.scope = 'col'; head.append(th);
    }
    const thead = el('thead'); thead.append(head); table.append(thead);
    const tbody = el('tbody');
    for (const dong of [...danhSach].reverse()) {
      const tr = el('tr');
      for (const text of [dong.dot_demo, NHAN[dong.trang_thai] || 'Đang cập nhật',
        dong.so_dong ?? '—', dong.so_tu ?? '—', dong.dong_dau ?? '—']) tr.append(el('td', text));
      const td = el('td', dong.thong_diep || '');
      chiTiet(td, dong.ma_loi); tr.append(td); tbody.append(tr);
    }
    table.append(tbody); bang.append(table);
  }
  async function capNhat(tuDong = false) {
    clearTimeout(timer);
    if (dung || signal?.aborted) return;
    if (tuDong && batDauCho !== null && Date.now() - batDauCho >= TRAN_HOI_MS) {
      hetHanCho();
      return;
    }
    try {
      const kq = await sdk.api.goi({ duong_dan: DUONG, signal });
      if (dung || signal?.aborted) return;
      if (!chon.options.length) {
        for (const ma of kq.dot_demo) {
          const option = el('option', `Đợt ${ma}`); option.value = ma; chon.append(option);
        }
      }
      ve(kq.danh_sach);
      if (kq.danh_sach.some(d => d.trang_thai === 'DA_GUI')) {
        batDauCho ??= Date.now();
        const conLai = TRAN_HOI_MS - (Date.now() - batDauCho);
        if (conLai <= 0) hetHanCho();
        else timer = setTimeout(() => capNhat(true), Math.min(2500, conLai));
      } else batDauCho = null;
    } catch (loi) { if (!dung && !signal?.aborted) hienLoi(loi); }
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (dangGui || dung) return;
    const file = tep.files[0], dot = chon.value;
    if (!choLuu && (!file || !dot)) return;
    dangGui = true; gui.disabled = true; chon.disabled = true; tep.disabled = true;
    try {
      bao.textContent = choLuu ? 'Đang lưu liên kết với đợt đã chọn…' : 'Đang gửi tệp…';
      if (!choLuu) {
        const { viec_id } = await sdk.nut.chay('xuat_thong_ke', file, { signal });
        choLuu = { dot_demo: dot, viec_id, khoa: globalThis.crypto.randomUUID() };
      }
      const { khoa, ...du_lieu } = choLuu;
      await sdk.api.goi({ phuong_thuc: 'POST', duong_dan: `${DUONG}/viec`,
        du_lieu, khoa, signal });
      choLuu = null;
      if (dung || signal?.aborted) return;
      batDauCho = null;
      tep.value = ''; bao.textContent = 'Đã lưu việc vào đợt đã chọn.';
      await capNhat();
    } catch (loi) { if (!dung && !signal?.aborted) hienLoi(loi); }
    finally {
      dangGui = false;
      if (!dung) {
        gui.disabled = false;
        chon.disabled = Boolean(choLuu); tep.disabled = Boolean(choLuu);
        gui.textContent = choLuu ? 'Thử lưu liên kết lại' : 'Gửi tệp của đợt';
      }
    }
  });
  taiLai.addEventListener('click', () => capNhat());
  await capNhat();
  return donDep;
}
