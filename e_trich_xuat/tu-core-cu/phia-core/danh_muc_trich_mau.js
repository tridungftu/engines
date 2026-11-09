/* LOAI-HD-0: 3 màn "Danh mục trích xuất" (Loại hợp đồng · Import danh mục · Chạy thử),
 * DỮ LIỆU GIẢ CÓ NHÃN. Không gọi máy chủ, không ghi CSDL, không đọc tệp thật.
 * Chỉ dựng bằng createElement/textContent. Mở khi URL có ?du_lieu_gia=1.
 */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.KttDanhMucTrichMau = factory();
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const NHAN_BANG = 'DỮ LIỆU GIẢ ĐỂ XEM GIAO DIỆN — chưa nối engine trích xuất';
  const NHAN_MAU = 'Dữ liệu giả — chỉ để góp ý giao diện';
  const TABS = [['loai', 'Loại hợp đồng'], ['import', 'Import danh mục'], ['chay_thu', 'Chạy thử']];
  const LOAI0 = () => [
    { ma: 'XD', ten: 'Hợp đồng xây dựng', mo_ta: 'Hợp đồng thi công, xây lắp công trình.', tt: 'Đang dùng', so_tham_so: 37,
      logic: true, goc: true, dang_dung: 3, mau: 5 },
    { ma: 'DV', ten: 'Hợp đồng dịch vụ', mo_ta: 'Dịch vụ bản gọn — danh mục nháp, chưa đo độ chính xác.', tt: 'Nháp', so_tham_so: 30,
      logic: false, goc: false, dang_dung: 0, mau: 4 },
    { ma: 'MUA_HH', ten: 'Hợp đồng mua hàng hóa', mo_ta: 'Hợp đồng mua vật tư, hàng hóa.', tt: 'Nháp', so_tham_so: 0,
      logic: false, goc: false, dang_dung: 0, mau: 0 }
  ];
  const LS0 = () => ({
    XD: [{ so: 3, ngay: '05/11/2026', nguoi: 'Quản trị DEMO', tt: 'Đang dùng' },
         { so: 2, ngay: '28/10/2026', nguoi: 'Quản trị DEMO', tt: 'Đã thay' },
         { so: 1, ngay: '20/10/2026', nguoi: 'Quản trị DEMO', tt: 'Đã thay' }],
    DV: [{ so: 1, ngay: '04/11/2026', nguoi: 'Quản trị DEMO', tt: 'Nháp' }],
    MUA_HH: []
  });
  // Khác biệt giữa bản n-1 và bản n (dữ liệu giả).
  const DIFF = {
    2: [['Thêm', 'Thời hạn bảo hành', 'Mức 2'], ['Đổi', 'Mức phạt chậm tiến độ', 'Mức 2 → Mức 3']],
    3: [['Bỏ', 'Ghi chú cuối hợp đồng', 'Mức 1'], ['Đổi thứ tự', 'Điều kiện thanh toán', 'Vị trí 12 → 9']],
    4: [['Thêm', 'Bảo lãnh thực hiện hợp đồng', 'Mức 3'], ['Đổi', 'Tỷ lệ giữ lại bảo hành', 'Mức 1 → Mức 2'],
        ['Bỏ', 'Ghi chú cuối hợp đồng', 'Mức 1']]
  };
  const FILES = [
    ['dat', 'Tệp mẫu A (DEMO) — hợp lệ'],
    ['loi', 'Tệp mẫu B (DEMO) — có lỗi']
  ];
  const LOI_FILE = [
    ['1', 'Mức quan trọng', 'Thiếu cột bắt buộc "Mức quan trọng".', 'Thêm cột "Mức quan trọng" như tệp mẫu trống.'],
    ['12', 'Mã tham số', 'Mã tham số trùng với dòng 7.', 'Đổi một trong hai mã thành mã khác, không trùng.'],
    ['15', 'Mức quan trọng', 'Mức quan trọng là 5, ngoài khoảng 0–3.', 'Nhập số nguyên từ 0 đến 3.']
  ];
  const THAM_SO = ['Bên giao thầu', 'Bên nhận thầu', 'Giá trị hợp đồng (VND)', 'Thời hạn thực hiện', 'Tiến độ thanh toán',
    'Mức phạt chậm tiến độ', 'Thời hạn bảo hành', 'Bảo lãnh thực hiện'];
  // Toàn bộ dòng dưới đây là minh họa, không lấy từ danh mục hay tệp Excel thật.
  const thamSoGia = (ma, n) => Array.from({ length: n }, (_, i) => ({
    ma: `TT-${String(i + 1).padStart(2, '0')}`,
    nhom: i < 2 ? 'Các bên ký kết' : 'Điều khoản hợp đồng',
    ten: (ma === 'DV' ? ['Bên sử dụng dịch vụ', 'Bên cung cấp dịch vụ', 'Phí dịch vụ (VND)',
      'Thời hạn cung cấp dịch vụ', 'Điều kiện thanh toán', 'Tiêu chí nghiệm thu dịch vụ'] : THAM_SO)[i]
      || `Nội dung minh họa ${i + 1}`,
    dung: i < n - 2, muc: i < 9 ? 3 : 2, luon: i < 4
  }));
  const pad = n => String(n).padStart(2, '0');
  const ngayStr = d => `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;

  function dung(rootEl, { signal, bay_gio = () => new Date(), quyen_sua = true, quyen_kich_hoat = true } = {}) {
    if (signal?.aborted) return { san_sang: Promise.resolve(), dung() {} };
    const doc = rootEl.ownerDocument;
    const el = (tag, text, cls) => {
      const n = doc.createElement(tag); if (text !== undefined) n.textContent = text;
      if (cls) n.className = cls; return n;
    };
    let daDung = !!signal?.aborted;
    const nut = (t, f, off) => { const b = el('button', t); b.type = 'button'; b.disabled = !!off;
      b.addEventListener('click', () => { if (!daDung && !b.disabled) f(); }); return b; };
    const nutSua = (t, f, off = false) => { const b = nut(t, f, off || !quyen_sua);
      if (!quyen_sua) b.title = 'Chưa được cấp quyền sửa danh mục trích xuất.'; return b; };
    const chon = (opts, val, f, nhan) => {
      const s = el('select'); s.setAttribute('aria-label', nhan);
      opts.forEach(([v, t]) => { const o = el('option', t); o.value = v; s.append(o); });
      s.value = val; s.addEventListener('change', () => f(s.value)); return s;
    };
    const bang = (dau, hang) => {
      const t = el('table'), h = el('tr');
      dau.forEach(x => h.append(el('th', x))); t.append(h);
      hang.forEach(r => { const tr = el('tr'); (r.cells || r).forEach(c => tr.append(typeof c === 'object' && c ? c : el('td', c)));
        if (r.cls) tr.className = r.cls; t.append(tr); });
      return t;
    };
    const loai = LOAI0(), ls = LS0();
    let tab = 'loai', form = null, xemPB = null, xemTS = null;
    let imp = { ma: 'XD', file: 'dat', tep: null, kq: null, chon: [], so: null, thongbao: '' };
    let ct = { pb: null, chon: [], da_chay: false, o: null, hop: false, ly_do: '', thongbao: '', tt: {}, kich_ban: 'tot' };
    let tbLoai = '';
    const body = el('div'), wrap = el('div', undefined, 'dmt');
    const style = el('style', '.dmt{font:14px/1.4 system-ui,sans-serif}.dmt-bang-gia{background:#b3261e;color:#fff;font-weight:700;padding:6px 10px;text-align:center}.dmt-tab button{margin:6px 6px 6px 0;padding:6px 12px}.dmt-tab .dang{background:#175d48;color:#fff}.dmt table{border-collapse:collapse;width:100%;margin:8px 0}.dmt th,.dmt td{border:1px solid #cbd6cf;padding:3px 8px;text-align:left}.dmt th{background:#e9f0e8}.dmt .vang{background:#fff4c2}.dmt .xanh{background:#e1f2e5}.dmt .loi{background:#fde3e0}.dmt .nho{font-size:12px;color:#555}.dmt .nhan{background:#fff4c2;padding:2px 8px;display:inline-block}.dmt button{margin-right:8px;padding:4px 10px}.dmt .hop{position:fixed;inset:0;background:rgba(0,0,0,.4);display:flex;align-items:center;justify-content:center;z-index:20}.dmt .hop>div{background:#fff;padding:16px;min-width:420px;max-width:640px;max-height:80vh;overflow:auto;border-radius:6px}');
    style.textContent += '.dmt-bang-gia{background:#fff4c2;color:#523f00}.dmt .cuon{overflow-x:auto}.dmt input[type=file]{margin:8px 0}.dmt .nhan{margin:8px 0}';
    wrap.append(style, el('div', NHAN_BANG, 'dmt-bang-gia'), el('p', NHAN_MAU, 'nhan'),
      el('p', 'Danh mục dùng chung toàn hệ thống. Mọi thao tác chỉ mô phỏng trong phiên xem này.', 'nho'));
    if (!quyen_sua) wrap.append(el('p', 'Chưa được cấp quyền sửa danh mục trích xuất.', 'nhan'));
    const tabs = el('div', undefined, 'dmt-tab');
    wrap.append(el('h2', 'Danh mục trích xuất'), tabs, body); rootEl.append(wrap);

    const tenLoai = ma => loai.find(l => l.ma === ma)?.ten || ma;
    const nhanh = ma => ls[ma] || [];
    const bangDung = ma => nhanh(ma).find(v => v.tt === 'Đang dùng');
    const ganhDiff = (a, b) => { const r = []; for (let n = a + 1; n <= b; n++) r.push(...(DIFF[n] || [['Đổi', 'Tham số mẫu', `Bản ${n - 1} → Bản ${n}`]])); return r; };
    const bangDiff = rows => bang(['Thay đổi', 'Tham số', 'Chi tiết'], rows.map(r => ({ cells: r, cls: r[0] === 'Thêm' ? 'xanh' : r[0] === 'Bỏ' ? 'loi' : 'vang' })));
    function bangThamSo(ma) {
      const l = loai.find(x => x.ma === ma), ds = thamSoGia(ma, l.so_tham_so);
      const d = el('div', undefined, 'cuon');
      d.append(el('h3', `Danh mục tham số — ${l.ten}`), el('p', 'Dữ liệu giả — các dòng tham số chỉ minh họa, chưa dùng để trích xuất.', 'nhan'));
      d.append(ds.length ? bang(['STT', 'Nhóm', 'Nội dung cần trích xuất', 'Dùng', 'Mức quan trọng', 'Luôn hỏi'],
        ds.map((x, i) => [String(i + 1), x.nhom, x.ten, x.dung ? 'Có' : 'Không', x.muc, x.luon ? 'Có' : 'Không'])) : el('p', 'Chưa có danh mục tham số.'));
      return d;
    }

    function manLoai() {
      const d = el('div');
      if (tbLoai) d.append(el('p', tbLoai, 'nhan'));
      const rows = loai.map(l => {
        const pb = bangDung(l.ma);
        const tdTen = el('td'); tdTen.append(el('div', l.ten));
        if (l.goc) tdTen.append(el('div', 'Loại gốc — phải ra kết quả giống công cụ gốc', 'nho'));
        const tdNut = el('td');
        tdNut.append(nutSua('Sửa tên/mô tả', () => { form = { sua: l.ma, ten: l.ten, mo_ta: l.mo_ta }; render(); }),
          nutSua(l.tt === 'Ngừng' ? 'Dùng lại' : 'Ngừng', () => { l.tt = l.tt === 'Ngừng' ? 'Nháp' : 'Ngừng'; render(); }, l.tt === 'Đang dùng' && l.goc),
          nut('Xem tham số', () => { xemTS = l.ma; render(); }),
          nut('Xem phiên bản', () => { xemPB = l.ma; render(); }),
          ...(nhanh(l.ma).some(v => v.tt === 'Nháp') ? [nut('Chạy thử bản nháp', () => { const v = nhanh(l.ma).find(x => x.tt === 'Nháp'); ct = { pb: `${l.ma}:${v.so}`, chon: [], da_chay: false, o: null, hop: false, ly_do: '', thongbao: '', tt: {}, kich_ban: 'tot' }; tab = 'chay_thu'; render(); })] : []));
        return { cells: [tdTen, l.mo_ta, l.tt,
          pb ? `Phiên bản ${pb.so} · ${pb.ngay} · ${pb.nguoi}` : 'Chưa có phiên bản đang dùng',
          l.so_tham_so ? String(l.so_tham_so) : '—', l.logic ? 'Có' : 'Chưa có kiểm logic riêng', tdNut], cls: l.tt === 'Ngừng' ? 'nho' : '' };
      });
      d.append(bang(['Tên', 'Mô tả ngắn', 'Trạng thái', 'Danh mục đang dùng', 'Số tham số', 'Kiểm logic riêng', 'Thao tác'], rows));
      d.append(nutSua('Thêm loại', () => { form = { sua: null, ma: '', ten: '', mo_ta: '' }; render(); }));
      if (xemTS) { const b = bangThamSo(xemTS); b.append(nut('Đóng danh mục tham số', () => { xemTS = null; render(); })); d.append(b); }
      if (form) {
        const f = el('div'); f.append(el('h3', form.sua ? 'Sửa tên và mô tả' : 'Thêm loại hợp đồng'));
        const o = (nh, k, ro) => { const i = el('input'); i.setAttribute('aria-label', nh); i.value = form[k] || ''; i.disabled = !!ro;
          i.addEventListener('change', () => { form[k] = i.value; }); const l = el('label', nh + ': '); l.append(i); f.append(l, el('br')); };
        if (!form.sua) o('Mã loại', 'ma'); o('Tên', 'ten'); o('Mô tả', 'mo_ta');
        f.append(nutSua('Lưu', () => {
          if (form.sua) { const l = loai.find(x => x.ma === form.sua); l.ten = form.ten || l.ten; l.mo_ta = form.mo_ta; }
          else if (form.ma && form.ten) { loai.push({ ma: form.ma, ten: form.ten, mo_ta: form.mo_ta, tt: 'Nháp', so_tham_so: 0, logic: false, goc: false, dang_dung: 0, mau: 0 }); ls[form.ma] = []; }
          form = null; render();
        }), nut('Bỏ qua', () => { form = null; render(); }));
        d.append(f);
      }
      if (xemPB) {
        const f = el('div'); f.append(el('h3', `Các phiên bản của ${tenLoai(xemPB)}`));
        f.append(nhanh(xemPB).length ? bang(['Số', 'Ngày nạp', 'Người nạp', 'Trạng thái'], nhanh(xemPB).map(v => [`Phiên bản ${v.so}`, v.ngay, v.nguoi, v.tt]))
          : el('p', 'Chưa có phiên bản nào.'));
        f.append(nut('Đóng', () => { xemPB = null; render(); })); d.append(f);
      }
      return d;
    }

    function manImport() {
      const d = el('div'), ma = imp.ma;
      d.append(el('label', 'Loại hợp đồng: '), chon(loai.map(l => [l.ma, l.ten]), ma, v => { imp = { ma: v, file: imp.file, tep: null, kq: null, chon: [], so: null, thongbao: '' }; render(); }, 'Loại hợp đồng'));
      d.append(nut('Tải mẫu Excel trống', () => { imp.thongbao = `Mẫu trống cho "${tenLoai(ma)}" (minh họa, chưa tạo tệp thật).`; render(); }));
      const tep = el('input'); tep.type = 'file'; tep.accept = '.xlsx'; tep.disabled = !quyen_sua;
      tep.setAttribute('aria-label', 'Chọn tệp Excel danh mục');
      tep.addEventListener('change', () => {
        if (daDung || !quyen_sua) return;
        const f = tep.files?.[0];
        // Chỉ giữ tên/kích thước để minh họa; không đọc, tải lên hay phân tích nội dung.
        imp.tep = f ? { ten: f.name, kich_thuoc: f.size } : null;
        imp.kq = null; imp.thongbao = ''; render();
      });
      const lb = el('label', 'Chọn tệp Excel danh mục: '); lb.append(tep); d.append(el('br'), lb);
      if (imp.tep) d.append(el('p', `Tệp đã chọn: ${imp.tep.ten}`));
      d.append(el('p', 'Chỉ chọn tệp để xem giao diện; nội dung tệp không được đọc hoặc tải lên. Kết quả dưới đây là dữ liệu giả.', 'nhan'),
        el('label', 'Tình huống kiểm giả lập: '), chon(FILES, imp.file, v => { imp.file = v; imp.kq = null; imp.thongbao = ''; render(); }, 'Tệp danh mục'));
      d.append(nutSua('Kiểm tra', () => {
        imp.kq = !/\.xlsx$/i.test(imp.tep.ten) || imp.tep.kich_thuoc > 2 * 1024 * 1024 ? 'tep_loi' : imp.file;
        imp.thongbao = ''; render();
      }, !imp.tep));
      if (imp.kq === 'tep_loi') d.append(el('p', 'Chọn tệp Excel .xlsx, dung lượng không quá 2 MiB.', 'loi'), nutSua('Lưu thành phiên bản nháp', () => {}, true));
      if (imp.thongbao) d.append(el('p', imp.thongbao, 'nhan'));
      if (imp.kq === 'loi') {
        d.append(el('h3', 'Kết quả kiểm tra: có 3 lỗi'), bang(['Dòng', 'Cột', 'Lỗi', 'Cách sửa'], LOI_FILE.map(r => ({ cells: r, cls: 'loi' }))),
          nutSua('Lưu thành phiên bản nháp', () => {}, true), el('span', 'Cần sửa hết lỗi trước khi lưu.', 'nho'));
      } else if (imp.kq === 'dat') {
        const dung_ = bangDung(ma), n = loai.find(x => x.ma === ma).so_tham_so || 30;
        d.append(el('h3', 'Kết quả kiểm tra: đạt'),
          el('p', `Số tham số: ${n} · đang dùng: ${n - 2} · mức quan trọng 3: 9 · luôn hỏi: 4`));
        d.append(el('p', 'Quy tắc kiểm riêng: tùy chọn trong tệp Excel; tình huống này chưa có kiểm logic riêng.', 'nho'));
        d.append(el('h4', 'Khác biệt so với bản đang dùng'));
        d.append(dung_ ? bangDiff(DIFF[4]) : el('p', 'Loại này chưa có bản đang dùng; toàn bộ tham số là mới.'));
        d.append(nutSua('Lưu thành phiên bản nháp', () => {
          const so = Math.max(0, ...nhanh(ma).map(v => v.so)) + 1;
          ls[ma].unshift({ so, ngay: ngayStr(bay_gio()), nguoi: 'Quản trị DEMO', tt: 'Nháp' });
          imp.kq = null; imp.thongbao = `Đã lưu phiên bản ${so} ở trạng thái nháp (mô phỏng, không ghi dữ liệu). Bản đang dùng không bị ghi đè.`; render();
        }));
      }
      if (imp.kq === 'dat' || imp.kq === 'loi') {
        const n = loai.find(x => x.ma === ma).so_tham_so || 30;
        d.append(el('h3', 'Bảng kiểm từng dòng — dữ liệu giả'), bang(['Dòng', 'Nội dung cần trích xuất', 'Kết quả', 'Ghi chú'],
          thamSoGia(ma, n).map((x, i) => ({ cells: [i + 2, x.ten,
            imp.kq === 'loi' && [10, 13].includes(i) ? 'Có lỗi' : 'Đạt',
            imp.kq === 'loi' && i === 10 ? 'Trùng mã tham số với dòng 7.' : imp.kq === 'loi' && i === 13 ? 'Mức quan trọng ngoài khoảng 0–3.' : 'Minh họa, chưa kiểm nội dung tệp.'],
            cls: imp.kq === 'loi' && [10, 13].includes(i) ? 'loi' : 'xanh' }))));
      }
      d.append(el('h3', 'Lịch sử phiên bản'));
      const vs = nhanh(ma);
      if (!vs.length) d.append(el('p', 'Chưa có phiên bản nào.'));
      else {
        d.append(bang(['Chọn', 'Số', 'Ngày nạp', 'Người nạp', 'Trạng thái'], vs.map(v => {
          const c = el('input'); c.type = 'checkbox'; c.checked = imp.chon.includes(v.so); c.setAttribute('aria-label', `Chọn phiên bản ${v.so}`);
          c.addEventListener('change', () => { imp.chon = imp.chon.filter(x => x !== v.so); if (c.checked) imp.chon.push(v.so); imp.chon = imp.chon.slice(-2); imp.so = null; render(); });
          const td = el('td'); td.append(c); return [td, `Phiên bản ${v.so}`, v.ngay, v.nguoi, v.tt];
        })));
        d.append(nut('So sánh', () => { imp.so = [...imp.chon].sort((a, b) => a - b); render(); }, imp.chon.length !== 2));
        if (imp.so) d.append(el('h4', `Khác biệt giữa phiên bản ${imp.so[0]} và phiên bản ${imp.so[1]}`), bangDiff(ganhDiff(imp.so[0], imp.so[1])));
      }
      return d;
    }

    const moiCt = pb => ({ pb: pb || null, chon: [], da_chay: false, o: null, hop: false, ly_do: '', thongbao: '', tt: {}, kich_ban: 'tot' });
    const nhomNhap = () => { const r = []; loai.forEach(l => (ls[l.ma] || []).filter(v => v.tt === 'Nháp').forEach(v => r.push([`${l.ma}:${v.so}`, `${l.ten} — phiên bản ${v.so} (nháp)`]))); return r; };
    const TT_HD = { cho: 'Chờ', dang: 'Đang chạy', xong: 'Xong', loi: 'Lỗi' };
    const tienDo = () => { // mô phỏng: hợp đồng đang chạy xong (hoặc lỗi), hợp đồng kế tiếp bắt đầu chạy
      const ds = ct.chon, i = ds.findIndex(t => ct.tt[t] === 'dang');
      if (i < 0) return;
      ct.tt[ds[i]] = ct.kich_ban === 'loi' && i === ds.length - 1 ? 'loi' : 'xong';
      if (ds[i + 1]) ct.tt[ds[i + 1]] = 'dang';
    };
    function manChayThu() {
      const d = el('div'), ds = nhomNhap();
      if (!ds.length) { if (ct.thongbao) d.append(el('p', ct.thongbao, 'nhan')); d.append(el('p', 'Chưa có phiên bản nháp để chạy thử. Hãy import danh mục trước.')); return d; }
      if (!ct.pb || !ds.some(x => x[0] === ct.pb)) ct.pb = ds[0][0];
      const [ma, so] = ct.pb.split(':'), l = loai.find(x => x.ma === ma), mau = l.mau || 0;
      const dung_ = bangDung(ma);
      d.append(el('label', 'Phiên bản nháp: '), chon(ds, ct.pb, v => { ct = moiCt(v); render(); }, 'Phiên bản nháp'));
      d.append(el('p', `Phiên bản đang dùng: ${dung_ ? 'Phiên bản ' + dung_.so : 'chưa có'} → phiên bản nháp sẽ kích hoạt: Phiên bản ${so}.`, 'nho'));
      d.append(el('h3', 'Chọn 3–5 hợp đồng mẫu (DEMO)'));
      if (!mau) d.append(el('p', 'Loại này chưa có hợp đồng mẫu DEMO.'));
      const HD = Array.from({ length: mau }, (_, i) => `Hợp đồng mẫu số ${pad(i + 1)} — ${l.ten} (DEMO)`);
      HD.forEach(t => {
        const c = el('input'); c.type = 'checkbox'; c.checked = ct.chon.includes(t); c.disabled = ct.da_chay; c.setAttribute('aria-label', t);
        c.addEventListener('change', () => { if (ct.da_chay) return; ct.chon = ct.chon.filter(x => x !== t); if (c.checked && ct.chon.length < 5) ct.chon.push(t); ct.o = null; render(); });
        const lb = el('label'); lb.append(c, el('span', ` ${t}`)); d.append(lb, el('br'));
      });
      const du = ct.chon.length >= 3;
      d.append(el('label', 'Tình huống giả lập: '), chon([['tot', 'Mọi hợp đồng chạy xong'], ['loi', 'Một hợp đồng gặp lỗi']], ct.kich_ban,
        v => { ct.kich_ban = v; render(); }, 'Tình huống chạy thử'), el('br'));
      d.append(nut('Gửi chạy thử', () => { ct.da_chay = true; ct.o = null; ct.tt = {}; ct.chon.forEach((t, i) => { ct.tt[t] = i === 0 ? 'dang' : 'cho'; }); render(); }, !du || ct.da_chay),
        el('span', du ? `Đã chọn ${ct.chon.length} hợp đồng.` : 'Cần chọn ít nhất 3 hợp đồng.', 'nho'));
      if (ct.da_chay) {
        d.append(nut('Chọn lại hợp đồng', () => { ct = moiCt(ct.pb); render(); }));
        const xong = ct.chon.filter(t => ct.tt[t] === 'xong'), loiHd = ct.chon.filter(t => ct.tt[t] === 'loi'), conChay = ct.chon.some(t => ct.tt[t] === 'dang' || ct.tt[t] === 'cho');
        d.append(el('h3', 'Trạng thái từng hợp đồng'), bang(['Hợp đồng mẫu', 'Trạng thái'], ct.chon.map(t => ({ cells: [t, TT_HD[ct.tt[t]]],
          cls: ct.tt[t] === 'xong' ? 'xanh' : ct.tt[t] === 'loi' ? 'loi' : 'vang' }))));
        if (conChay) {
          const vt = ct.chon.filter(t => ct.tt[t] !== 'xong' && ct.tt[t] !== 'loi').length;
          d.append(el('p', `Việc ở vị trí thứ ${vt} trong hàng chờ — đang xử lý (mô phỏng).`, 'nhan'),
            nut('Cập nhật tiến độ (mô phỏng)', () => { tienDo(); render(); }));
        } else d.append(el('p', loiHd.length ? `Chạy thử kết thúc, ${loiHd.length} hợp đồng bị lỗi — chưa thể kích hoạt.` : 'Việc ở vị trí thứ 1 trong hàng chờ — đã chạy xong (mô phỏng).', loiHd.length ? 'loi' : 'nhan'));
        const vang = xong.map(() => 0);
        const rows = THAM_SO.map((ts, i) => {
          const cells = [el('td', ts)];
          xong.forEach((t, j) => {
            const v = (i * 7 + j * 3 + 1) % 5 === 0, doi = !!dung_ && (i + j) % 7 === 0;
            if (v) vang[j]++;
            const td = el('td', `${v ? 'Cần xem' : 'Giá trị ' + (i + 1)}${doi ? ' · đổi kết quả' : ''}`, v ? 'vang' : 'xanh');
            td.setAttribute('aria-label', `${ts} · ${t}`); td.addEventListener('click', () => { ct.o = { ts, t, v, doi }; render(); });
            cells.push(td);
          });
          return cells;
        });
        rows.push([el('td', 'Số ô cần xem'), ...vang.map(x => el('td', String(x)))]);
        if (xong.length) {
          d.append(el('p', `Hiển thị ${THAM_SO.length} tham số mẫu trong ${l.so_tham_so || 30}.`, 'nho'), bang(['Tham số', ...xong], rows));
          if (ct.o) d.append(el('p', `${ct.o.ts} — ${ct.o.t}: ${ct.o.v ? 'Lý do cần xem: giá trị có hai cách hiểu trong hợp đồng (mô phỏng).' : 'Đạt.'} Trích dẫn: "Điều 5, khoản 2 …" (mô phỏng).${ct.o.doi ? ' Kết quả khác với bản đang dùng.' : ''}`, 'nhan'));
        }
        ct._tong = vang.reduce((a, b) => a + b, 0); ct._ma = ma; ct._so = Number(so);
        const san = !conChay && !loiHd.length && xong.length >= 3;
        if (!quyen_kich_hoat) d.append(el('p', 'Chưa được cấp quyền kích hoạt danh mục trích xuất. Liên hệ người quản trị để được cấp quyền.', 'nhan'));
        else {
          const k = nut('Kích hoạt phiên bản này', () => { ct.hop = true; render(); }, !san);
          if (!san) k.title = 'Chỉ kích hoạt được khi ít nhất 3 hợp đồng chạy thử xong và không có hợp đồng lỗi.';
          d.append(k);
        }
      }
      if (ct.thongbao) d.append(el('p', ct.thongbao, 'nhan'));
      if (ct.hop && quyen_kich_hoat) {
        const h = el('div', undefined, 'hop'), b = el('div');
        b.append(el('h3', `Kích hoạt phiên bản ${ct._so} của ${tenLoai(ct._ma)}`),
          el('p', `Phiên bản đang dùng: ${bangDung(ct._ma) ? 'Phiên bản ' + bangDung(ct._ma).so : 'chưa có'} → phiên bản mới: Phiên bản ${ct._so}.`),
          el('p', `Tổng số ô cần xem: ${ct._tong}.`), el('h4', 'Khác biệt so với bản đang dùng'),
          bangDiff(bangDung(ct._ma) ? DIFF[4] : [['Thêm', 'Toàn bộ tham số', 'Loại chưa có bản đang dùng']]));
        const i = el('input'); i.setAttribute('aria-label', 'Lý do kích hoạt'); i.value = ct.ly_do;
        const ok = nut('Xác nhận kích hoạt', () => {
          const cu = bangDung(ct._ma), t = nhanh(ct._ma); t.forEach(v => { if (v.tt === 'Đang dùng') v.tt = 'Đã thay'; });
          const v = t.find(x => x.so === ct._so); if (v) v.tt = 'Đang dùng'; loai.find(x => x.ma === ct._ma).tt = 'Đang dùng';
          tbLoai = `Đã kích hoạt ${tenLoai(ct._ma)}: ${cu ? 'Phiên bản ' + cu.so : 'chưa có bản đang dùng'} → Phiên bản ${ct._so} ngày ${ngayStr(bay_gio())} (mô phỏng, không ghi dữ liệu).`;
          ct = moiCt(); tab = 'loai'; render();
        }, ct.ly_do.trim().length < 10);
        const capNhat = () => { ct.ly_do = i.value; ok.disabled = ct.ly_do.trim().length < 10; };
        i.addEventListener('input', capNhat); i.addEventListener('change', capNhat);
        const lb = el('label', 'Lý do (ít nhất 10 ký tự): '); lb.append(i);
        b.append(lb, el('br'), ok, nut('Bỏ qua', () => { ct.hop = false; render(); }));
        h.append(b); d.append(h);
      }
      return d;
    }

    function render() {
      if (daDung) return;
      tabs.replaceChildren(...TABS.map(([k, t]) => { const b = nut(t, () => { tab = k; render(); }); if (k === tab) b.className = 'dang'; return b; }));
      body.replaceChildren(tab === 'loai' ? manLoai() : tab === 'import' ? manImport() : manChayThu());
    }
    render();
    const stop = () => { daDung = true; rootEl.replaceChildren(); };
    signal?.addEventListener('abort', stop, { once: true });
    return { san_sang: Promise.resolve(), dung: stop };
  }
  return { dung, NHAN_BANG, NHAN_MAU };
});
