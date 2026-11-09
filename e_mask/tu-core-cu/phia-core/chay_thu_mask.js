/* MASK-3I — màn thử văn bản DEMO, chỉ Admin; không tự gọi engine hay lưu dữ liệu.
 * api_mask có thể được tiêm: che_van_ban(payload, {signal}), mo_che_van_ban(payload, {signal}).
 * Mặc định POST/GET qua routes_mask.py, CSRF cả hai chiều, chỉ trong pháp nhân DEMO.
 * tests/test_mask5_seam.py kiểm khóa kết quả với engine thật.
 * Che: {van_ban,dinh_danh_da_biet:[{gia_tri,nhom}]} -> {ma_yeu_cau,van_ban_da_che,
 * so_cho_thay,bi_danh:[{bi_danh,nhom,nguon:'chinh_thuc'|'tam'}],cho_duyet:{so_cum_vua_them},
 * con_sot:[{nhom,vi_tri:{bat_dau,ket_thuc,dong,cot}}|{ly_do}],kiem_tien_ngay:boolean,gui_duoc,canh_bao}.
 * van_ban_da_che là null khi bị chặn; vị trí dòng/cột tính từ 1.
 * Mở: {ma_yeu_cau,van_ban_co_bi_danh,dong_viec:false} -> {van_ban_da_mo_che,so_cho_mo,
 * bi_danh_khong_ro:[{bi_danh,vi_tri:{bat_dau,ket_thuc,dong,cot}}],mo_day_du,
 * trang_thai_ma_yeu_cau:'DANG_XU_LY'|'DA_DONG'}.
 * Module/người gửi/nguồn phải do Core xác minh; không suy quyền từ payload trên màn.
 */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.KttChayThuMask = factory();
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const VAN_BAN = 'Hợp đồng DEMO — Dữ liệu giả.\nCông ty DEMO Ánh Dương.\nMST giả: 0000000000-DEMO.\nSố tiền thanh toán: 1.000.000 VND; ngày thanh toán: 30/10/2026.';
  const DINH_DANH = 'Công ty DEMO Ánh Dương | Tên tổ chức\n0000000000-DEMO | Mã số thuế';
  const TIEN_TO = '/api/v1/quan-tri/engine/e_mask/chay-thu';
  const laId = value => typeof value === 'string' && /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(value);
  const NHOM = { CONG_TY: 'Tên tổ chức', CA_NHAN: 'Cá nhân', EMAIL: 'Thư điện tử',
    DIEN_THOAI: 'Số điện thoại', MA_SO_THUE: 'Mã số thuế', MST: 'Mã số thuế', TAI_KHOAN: 'Tài khoản',
    GIAY_TO: 'Giấy tờ', HOP_DONG: 'Hợp đồng', DIA_CHI: 'Địa chỉ', DU_AN: 'Dự án', KHAC: 'Khác' };
  const nhom = value => Object.hasOwn(NHOM, value) ? NHOM[value]
    : Object.values(NHOM).includes(value) ? value : 'Thông tin định danh';
  const maNhom = value => Object.keys(NHOM).find(key => NHOM[key] === value) || value || 'KHAC';
  const biDanh = value => typeof value === 'string' && /^\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]$/.test(value)
    ? value : 'Bí danh chưa nhận diện';
  const so = value => Number.isSafeInteger(value) && value >= 0;
  const doDai = value => [...value].length;
  const viTri = value => value && so(value.bat_dau) && so(value.ket_thuc) && value.ket_thuc >= value.bat_dau &&
    so(value.dong) && value.dong > 0 && so(value.cot) && value.cot > 0
    ? `dòng ${value.dong}, cột ${value.cot}` : 'Chưa xác định vị trí';
  const LY_DO_CON_SOT = ['Chưa kiểm tra đầy đủ định danh.', 'Văn bản đầu vào đã chứa dấu bí danh cần kiểm tra.'];
  const conSot = value => typeof value?.nhom === 'string' ? `${viTri(value.vi_tri)} · ${nhom(value.nhom)}`
    : LY_DO_CON_SOT.includes(value?.ly_do) ? value.ly_do : 'Cần kiểm tra lại định danh.';
  const CSS = `.core-mask-demo{line-height:1.6}.core-mask-demo .mask-nhan{padding:12px 16px;border-left:4px solid var(--green,#315c4d);background:#eef4ed}.core-mask-demo .mask-bo-cuc{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,25rem),1fr));gap:24px;margin:20px 0}.core-mask-demo .mask-phan{min-width:0;padding:20px;border:1px solid var(--line,#e3e8e1);background:var(--white,#fff);border-radius:8px}.core-mask-demo label{display:grid;gap:6px;margin:16px 0;font-weight:600}.core-mask-demo textarea{box-sizing:border-box;width:100%;max-width:100%;padding:10px;border:1px solid #aab8ad;border-radius:5px;background:#fff;color:inherit;font:inherit;font-weight:400;resize:vertical}.core-mask-demo .mask-chon{display:flex;align-items:center;gap:8px}.core-mask-demo .mask-thao-tac{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0}.core-mask-demo pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;background:#f5f7f4;padding:12px}.core-mask-demo ul{padding-left:20px}.core-mask-demo :focus-visible{outline:3px solid #739763;outline-offset:3px}`;
  function dung(root, { sdk_he_thong, api_mask, khai_bao_da_loc_quyen: kb, signal, khi_quay_lai,
                        doc_phien, csrf_token, nguoi_dung_id,
                        fetch: guiHttp = globalThis.fetch?.bind(globalThis),
                        tao_khoa = () => globalThis.crypto.randomUUID() } = {}) {
    const doc = root.ownerDocument, controller = new AbortController();
    const el = (tag, text) => { const n = doc.createElement(tag); if (text !== undefined) n.textContent = text; return n; };
    const song = () => !controller.signal.aborted;
    const coQuyen = () => kb?.ma === 'quan_ly_engine' && !kb.khong_quyen && typeof sdk_he_thong?.api?.goi === 'function';
    const macDinh = !api_mask && typeof guiHttp === 'function' && (typeof doc_phien === 'function' || !!csrf_token);
    const docPhien = () => doc_phien ? doc_phien() : { csrf_token, nguoi_dung_id };
    const loiApi = (ma, status) => Object.assign(new Error(), { ma, status });
    let maYeuCau = null, dangGui = false, chuaBat = false, phienMask, phapNhan = null, cacDemo = [];
    function kiemPhien() {
      if (!song()) throw Object.assign(new Error(), { name: 'AbortError' });
      if (!coQuyen()) throw loiApi('MASK_THU_QUYEN', 403);
      const current = docPhien();
      if (!current?.csrf_token || current.csrf_token !== phienMask?.csrf_token ||
          current.nguoi_dung_id !== phienMask?.nguoi_dung_id) throw loiApi('NGU_CANH_DA_DOI');
    }
    function choHoiLai() {
      return new Promise((resolve, reject) => {
        const huy = () => {
          clearTimeout(timer); controller.signal.removeEventListener('abort', huy);
          reject(Object.assign(new Error(), { name: 'AbortError' }));
        };
        const timer = setTimeout(() => { controller.signal.removeEventListener('abort', huy); resolve(); }, 1000);
        controller.signal.addEventListener('abort', huy, { once: true });
      });
    }
    async function chay(suffix, payload) {
      kiemPhien();
      const company = phapNhan;
      if (!laId(company)) throw loiApi('MASK_THU_PHAM_VI');
      async function goi(path, method = 'GET') {
        kiemPhien();
        if (company !== phapNhan) throw loiApi('NGU_CANH_DA_DOI');
        const response = await guiHttp(path, { method,
          headers: { Accept: 'application/json', 'X-CSRF-Token': phienMask.csrf_token, 'X-Phap-Nhan-Id': company,
            ...(method === 'POST' ? { 'Content-Type': 'application/json', 'Idempotency-Key': tao_khoa() } : {}) },
          ...(method === 'POST' ? { body: JSON.stringify(payload) } : {}), signal: controller.signal,
          credentials: 'same-origin', mode: 'same-origin', redirect: 'error', cache: 'no-store' });
        kiemPhien();
        if (response.redirected || (response.status >= 300 && response.status < 400)) throw loiApi('MASK_THU_KET_QUA');
        if (response.status === 401 && typeof globalThis.dispatchEvent === 'function' &&
            typeof globalThis.CustomEvent === 'function') {
          globalThis.dispatchEvent(new globalThis.CustomEvent('ktt:het-phien', { detail: { nguoi_dung_id: phienMask.nguoi_dung_id } }));
          kiemPhien();
        }
        let data;
        try {
          if (!/^application\/json(?:\s*;|\s*$)/i.test(response.headers.get('Content-Type') || '')) throw new Error();
          data = await response.json();
        } catch (_) { throw loiApi('MASK_THU_KET_QUA'); }
        kiemPhien();
        if (!response.ok) throw loiApi(data?.ma === 'MASK_THU_CHUA_BAT' ? 'MASK_THU_CHUA_BAT' : 'MASK_THU_XU_LY', response.status);
        if (response.status !== (method === 'POST' ? 202 : 200) || !data || typeof data !== 'object') throw loiApi('MASK_THU_KET_QUA');
        return data;
      }
      const accepted = await goi(TIEN_TO + suffix, 'POST');
      if (!laId(accepted.viec_id) || accepted.trang_thai !== 'queued') throw loiApi('MASK_THU_KET_QUA');
      // Không dùng Location do server cung cấp làm đích gửi CSRF/văn bản.
      for (let lan = 0; lan < 30; lan++) {
        if (lan) await choHoiLai();
        const result = await goi(TIEN_TO + '/' + accepted.viec_id);
        if (result.viec_id !== accepted.viec_id) throw loiApi('MASK_THU_KET_QUA');
        if (result.trang_thai === 'succeeded') {
          if (!result.ket_qua || typeof result.ket_qua !== 'object' || Array.isArray(result.ket_qua)) throw loiApi('MASK_THU_KET_QUA');
          return result.ket_qua;
        }
        if (result.ket_qua !== null) throw loiApi('MASK_THU_KET_QUA');
        if (['failed', 'cancelled', 'cancel_requested'].includes(result.trang_thai)) throw loiApi('MASK_THU_DA_DUNG');
        if (!['queued', 'running'].includes(result.trang_thai)) throw loiApi('MASK_THU_KET_QUA');
      }
      throw loiApi('MASK_THU_HET_CHO');
    }
    if (macDinh) api_mask = { che_van_ban: payload => chay('/che-van-ban', payload),
      mo_che_van_ban: payload => chay('/mo-che-van-ban', payload) };
    async function docDemo() {
      const ids = new Set(), cursors = new Set(); let cursor;
      do {
        kiemPhien();
        const page = await sdk_he_thong.phap_nhan.danh_sach({ con_tro: cursor, signal: controller.signal });
        kiemPhien();
        if (!Array.isArray(page?.danh_sach) || typeof page.con_tiep !== 'boolean' ||
            (!page.con_tiep && page.con_tro_tiep !== null) || (page.con_tiep && !page.danh_sach.length)) throw loiApi('MASK_THU_PHAM_VI');
        for (const row of page.danh_sach) {
          if (!laId(row?.id) || ids.has(row.id.toLowerCase())) throw loiApi('MASK_THU_PHAM_VI');
          ids.add(row.id.toLowerCase());
          if (row.la_demo === true) cacDemo.push({ id: row.id, ten: row.ten });
        }
        cursor = page.con_tiep ? page.con_tro_tiep : null;
        if (cursor && (typeof cursor !== 'string' || cursor.length > 4096 || cursors.has(cursor))) throw loiApi('MASK_THU_PHAM_VI');
        if (page.con_tiep && !cursor) throw loiApi('MASK_THU_PHAM_VI');
        if (cursor) cursors.add(cursor);
      } while (cursor);
      phapNhan = cacDemo.length === 1 ? cacDemo[0].id : null;
    }
    const inputs = [], outputs = [];
    function xoaNoiDung() {
      maYeuCau = null; phapNhan = null; cacDemo = []; phienMask = null;
      for (const n of inputs) { n.value = ''; n.checked = false; }
      for (const n of outputs) n.replaceChildren();
    }
    function stop() {
      if (!song()) return;
      controller.abort(); xoaNoiDung(); root.replaceChildren(); signal?.removeEventListener('abort', stop);
    }
    function hoTro(parent, code) {
      const details = el('details'); details.append(el('summary', 'Chi tiết hỗ trợ'), el('p', `Mã hỗ trợ: ${code}`));
      parent.append(details);
    }
    function chan(text, error) {
      xoaNoiDung(); controller.abort(); signal?.removeEventListener('abort', stop);
      const p = el('p', text); p.setAttribute('role', 'alert'); root.replaceChildren(p);
      if (error) hoTro(root, 'MASK_DEMO_QUYEN', error);
    }
    function kiemQuyen() {
      if (!song()) return false;
      if (coQuyen()) return true;
      chan('Chỉ Admin Core được chạy thử DEMO Che định danh.'); return false;
    }
    function nut(text, action, primary = false) {
      const n = el('button', text); n.type = 'button'; n.className = `button ${primary ? 'primary' : 'secondary'}`;
      n.addEventListener('click', () => { if (kiemQuyen()) return action(); }); return n;
    }
    function quayLai() { stop(); khi_quay_lai?.(); }
    const matPhien = e => e?.status === 401 || ['NGU_CANH_DA_DOI', 'SAI_NGU_CANH'].includes(e?.ma);
    function loi(parent, error) {
      if (matPhien(error) || error?.status === 403) {
        chan(error?.status === 403 ? 'Chỉ Admin Core được chạy thử DEMO Che định danh.'
          : 'Phiên làm việc đã thay đổi. Đăng nhập lại để tiếp tục.', error); return;
      }
      if (error?.ma === 'MASK_THU_CHUA_BAT') chuaBat = true;
      const message = { MASK_THU_CHUA_BAT: 'Chức năng chạy thử chưa được bật.',
        MASK_THU_HET_CHO: 'Chưa nhận được kết quả trong thời gian chờ. Mở lại màn chạy thử để kiểm tra.',
        MASK_THU_DA_DUNG: 'Lượt chạy thử đã dừng. Có thể thử lại.' };
      parent.replaceChildren(el('p', Object.hasOwn(message, error?.ma) ? message[error.ma] : [404, 501, 503].includes(error?.status)
        ? 'Engine chưa sẵn sàng' : 'Chưa hoàn tất chạy thử. Kiểm tra lại kết nối rồi thử lại.'));
      hoTro(parent, 'MASK_DEMO_XU_LY', error);
    }
    signal?.addEventListener('abort', stop, { once: true });
    if (signal?.aborted) { stop(); return { dung: stop, san_sang: Promise.resolve() }; }
    async function tai() {
      if (!kiemQuyen()) return;
      root.replaceChildren(el('p', 'Đang kiểm tra quyền quản trị…'));
      try {
        const page = await sdk_he_thong.api.goi({ duong_dan: '/api/v1/quan-tri/engine/kiem-ke', signal: controller.signal });
        if (!kiemQuyen()) return;
        if (page?.phien_ban_quan_tri !== 2 || !Array.isArray(page.danh_sach)) throw new Error();
        if (macDinh) {
          const session = docPhien();
          if (typeof session?.csrf_token !== 'string' || !session.csrf_token) throw loiApi('THIEU_CSRF');
          if (nguoi_dung_id && session.nguoi_dung_id !== nguoi_dung_id) throw loiApi('NGU_CANH_DA_DOI');
          phienMask = { csrf_token: session.csrf_token, nguoi_dung_id: session.nguoi_dung_id };
          await docDemo();
        }
        if (!kiemQuyen()) return;
        hien();
      } catch (error) {
        if (!song()) return;
        if (matPhien(error) || error?.status === 403) { loi(root, error); return; }
        root.replaceChildren(el('p', 'Chưa chuẩn bị được màn chạy thử. Quay lại Che định danh rồi mở lại màn.'),
          nut('Quay lại Che định danh', quayLai)); hoTro(root, 'MASK_DEMO_KIEM_QUYEN', error);
      }
    }
    function hien() {
      const panel = el('section'); panel.className = 'core-mask-demo';
      const nhan = el('p', 'Dữ liệu giả — DEMO. Chỉ dán văn bản giả để thử che và mở che.'); nhan.className = 'mask-nhan';
      panel.append(el('style', CSS), nut('Quay lại Che định danh', quayLai), el('h3', 'Chạy thử DEMO — Che định danh'), nhan,
        el('p', 'Kết quả chỉ phục vụ chạy thử; không gửi ra Cloud. Thử tệp thuộc bước triển khai tiếp theo.'));
      if (typeof api_mask?.che_van_ban !== 'function' || typeof api_mask?.mo_che_van_ban !== 'function') {
        const notice = el('p', 'Engine chưa sẵn sàng'); notice.setAttribute('role', 'status'); panel.append(notice);
      }
      let chonDemo;
      if (macDinh) {
        const label = el('label', 'Pháp nhân DEMO'); chonDemo = el('select'); chonDemo.setAttribute('aria-label', 'Pháp nhân DEMO');
        const empty = el('option', 'Chọn pháp nhân DEMO'); empty.value = ''; chonDemo.append(empty);
        cacDemo.forEach((row, index) => {
          const ten = typeof row.ten === 'string' && row.ten.trim() && row.ten.length <= 255 &&
            !/_|[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}|[a-f0-9]{32,}/i.test(row.ten) ? row.ten : 'Pháp nhân DEMO được cấp quyền';
          const option = el('option', ten); option.value = String(index); chonDemo.append(option);
        });
        chonDemo.value = phapNhan ? '0' : ''; label.append(chonDemo); panel.append(label);
        if (!cacDemo.length) panel.append(el('p', 'Chưa có pháp nhân DEMO được cấp quyền để chạy thử.'));
      }
      const grid = el('div'); grid.className = 'mask-bo-cuc';
      function form(title) { const f = el('form'); f.className = 'mask-phan'; f.append(el('h4', title)); grid.append(f); return f; }
      function textInput(f, title, rows) {
        const label = el('label', title), n = el('textarea'); n.rows = rows; n.setAttribute('aria-label', title);
        label.append(n); f.append(label); inputs.push(n); return n;
      }
      function result(f, title) {
        const n = el('section'); n.setAttribute('aria-label', title); n.setAttribute('aria-live', 'polite');
        f.append(el('h5', title), n); outputs.push(n); return n;
      }
      const che = form('Che'), vanBan = textInput(che, 'Văn bản DEMO cần che', 7);
      vanBan.value = VAN_BAN;
      const known = textInput(che, 'Định danh đã biết (tùy chọn)', 3);
      che.append(el('p', 'Mỗi dòng một giá trị; có thể thêm nhóm sau dấu |, ví dụ: Công ty DEMO Ánh Dương | Tên tổ chức. Tối đa 500 mục.'));
      known.placeholder = DINH_DANH;
      const actions = el('div'); actions.className = 'mask-thao-tac';
      const send = el('button', 'Che'); send.type = 'submit'; send.className = 'button primary';
      const sample = nut('Dùng mẫu DEMO', () => {
        if (dangGui) return; vanBan.value = VAN_BAN; known.value = DINH_DANH; xoaKetQuaChe();
      });
      actions.append(send, sample); che.append(actions); const ketQuaChe = result(che, 'Kết quả che');
      const mo = form('Mở che'), coBiDanh = textInput(mo, 'Văn bản có bí danh', 7);
      mo.append(el('p', 'Sau khi che, có thể sửa văn bản có bí danh rồi mở che trong cùng lượt chạy thử.'));
      const dongViec = el('input'); dongViec.type = 'checkbox'; dongViec.checked = false;
      dongViec.setAttribute('aria-label', 'Đóng việc sau khi mở'); inputs.push(dongViec);
      const label = el('label'); label.className = 'mask-chon'; label.append(dongViec, el('span', 'Đóng việc sau khi mở')); mo.append(label);
      const open = el('button', 'Mở che'); open.type = 'submit'; open.className = 'button primary'; mo.append(open);
      const ketQuaMo = result(mo, 'Kết quả mở che'); panel.append(grid); root.replaceChildren(panel);
      function xoaKetQuaChe() {
        maYeuCau = null; coBiDanh.value = ''; dongViec.checked = false;
        ketQuaChe.replaceChildren(el('p', chuaBat ? 'Chức năng chạy thử chưa được bật.' : 'Chưa có kết quả che.'));
        ketQuaMo.replaceChildren(el('p', 'Chưa có kết quả mở che.'));
        if (chuaBat) hoTro(ketQuaChe, 'MASK_DEMO_XU_LY');
      }
      function khoa(value) {
        dangGui = value; che.setAttribute('aria-busy', String(value)); mo.setAttribute('aria-busy', String(value));
        for (const n of [...inputs, send, sample, open]) n.disabled = value;
        send.disabled = open.disabled = value || chuaBat || (macDinh && !phapNhan) ||
          typeof api_mask?.che_van_ban !== 'function' || typeof api_mask?.mo_che_van_ban !== 'function';
        if (chonDemo) chonDemo.disabled = value || !cacDemo.length;
      }
      function docDinhDanh() {
        const rows = known.value.split(/\r\n|\r|\n/).filter(s => s.trim());
        if (rows.length > 500) throw new Error('Chỉ nhập tối đa 500 định danh đã biết.');
        return rows.map(row => {
          const parts = row.split('|'), gia_tri = parts[0].trim(), group = (parts[1] || '').trim();
          if (parts.length > 2 || !gia_tri || doDai(gia_tri) > 300 || doDai(group) > 20) {
            throw new Error('Mỗi định danh cần giá trị tối đa 300 ký tự và nhóm tối đa 20 ký tự, ngăn bằng một dấu |.');
          }
          return { gia_tri, nhom: maNhom(group) };
        });
      }
      function kiemVanBan(value) {
        return !value.trim() ? 'Cần nhập văn bản DEMO trước khi xử lý.'
          : doDai(value) > 500000 ? 'Văn bản tối đa 500.000 ký tự; nội dung chưa được gửi.' : null;
      }
      function danhSach(parent, title, rows, format) {
        parent.append(el('h5', title));
        if (!rows.length) { parent.append(el('p', 'Không có.')); return; }
        const list = el('ul'); for (const row of rows) list.append(el('li', format(row))); parent.append(list);
      }
      function hienChe(r) {
        if (!r || typeof r.ma_yeu_cau !== 'string' || !r.ma_yeu_cau.trim() ||
            (r.van_ban_da_che !== null && typeof r.van_ban_da_che !== 'string') ||
            !so(r.so_cho_thay) || !Array.isArray(r.bi_danh) || r.bi_danh.some(b => !b || typeof b !== 'object') ||
            !Array.isArray(r.con_sot) || !so(r.cho_duyet?.so_cum_vua_them)) throw new Error();
        const duocHien = r.con_sot.length === 0 && r.gui_duoc === true && r.kiem_tien_ngay === true;
        if (duocHien && typeof r.van_ban_da_che !== 'string') throw new Error();
        maYeuCau = r.ma_yeu_cau;
        ketQuaChe.replaceChildren(el('p', r.con_sot.length ? 'Không được gửi: còn thông tin định danh chưa che'
          : r.kiem_tien_ngay !== true ? 'Không được gửi: kiểm tiền/ngày chưa đạt.'
          : r.gui_duoc !== true ? 'Không được gửi: kết quả che chưa được chấp nhận.' : 'Đã có kết quả che — DEMO.'));
        if (duocHien) ketQuaChe.append(el('h5', 'Văn bản đã che'), el('pre', r.van_ban_da_che));
        ketQuaChe.append(el('p', `Số chỗ thay: ${r.so_cho_thay}`),
          el('p', `Số cụm vừa vào chờ duyệt: ${r.cho_duyet.so_cum_vua_them}`),
          el('p', `Kiểm tiền/ngày: ${r.kiem_tien_ngay === true ? 'Đạt' : r.kiem_tien_ngay === false ? 'Không đạt' : 'Chưa kiểm'}`));
        danhSach(ketQuaChe, 'Bí danh đã dùng', r.bi_danh, b => `${biDanh(b.bi_danh)} · ${nhom(b.nhom)} · ${
          b.nguon === 'chinh_thuc' ? 'Chính thức' : b.nguon === 'tam' ? 'Tạm' : 'Chưa xác định nguồn'}`);
        danhSach(ketQuaChe, 'Còn sót', r.con_sot, conSot);
        // Không in cảnh báo thô: phản hồi cũ hoặc adapter lỗi có thể mang cụm gốc.
        if (Array.isArray(r.canh_bao) && r.canh_bao.length) ketQuaChe.append(el('p', `Có ${r.canh_bao.length} cảnh báo cần kiểm tra với bộ phận hỗ trợ.`));
        if (duocHien) coBiDanh.value = r.van_ban_da_che;
      }
      function hienMo(r) {
        if (!r || typeof r.van_ban_da_mo_che !== 'string' || !so(r.so_cho_mo) || !Array.isArray(r.bi_danh_khong_ro) ||
            typeof r.mo_day_du !== 'boolean' || !['DANG_XU_LY', 'DA_DONG'].includes(r.trang_thai_ma_yeu_cau)) throw new Error();
        ketQuaMo.replaceChildren(el('p', r.mo_day_du ? 'Đã mở che đầy đủ — DEMO.' : 'Chưa mở che đầy đủ. Cần kiểm tra lại bí danh.'),
          el('h5', 'Văn bản mở che'), el('pre', r.van_ban_da_mo_che), el('p', `Số chỗ mở: ${r.so_cho_mo}`),
          el('p', `Trạng thái yêu cầu: ${r.trang_thai_ma_yeu_cau === 'DA_DONG' ? 'Đã đóng' : 'Đang xử lý'}`));
        danhSach(ketQuaMo, 'Bí danh chưa mở được và vị trí', r.bi_danh_khong_ro, b => `${biDanh(b?.bi_danh)} · ${viTri(b?.vi_tri)}`);
        if (r.trang_thai_ma_yeu_cau === 'DA_DONG') maYeuCau = null;
      }
      async function gui(kieu) {
        if (!kiemQuyen() || dangGui || chuaBat) return;
        const laChe = kieu === 'che', output = laChe ? ketQuaChe : ketQuaMo;
        if (macDinh && !phapNhan) { output.replaceChildren(el('p', 'Chọn pháp nhân DEMO để tiếp tục chạy thử.')); return; }
        let payload;
        if (laChe) xoaKetQuaChe(); else output.replaceChildren();
        const validation = kiemVanBan(laChe ? vanBan.value : coBiDanh.value);
        if (validation) { output.replaceChildren(el('p', validation)); return; }
        if (!laChe && !maYeuCau) { output.replaceChildren(el('p', 'Cần che văn bản DEMO trước khi mở che; yêu cầu phải còn đang xử lý.')); return; }
        if (laChe) {
          try { payload = { van_ban: vanBan.value, dinh_danh_da_biet: docDinhDanh() }; }
          catch (error) { output.replaceChildren(el('p', error.message)); return; }
        } else payload = { ma_yeu_cau: maYeuCau, van_ban_co_bi_danh: coBiDanh.value, dong_viec: dongViec.checked === true };
        const method = laChe ? 'che_van_ban' : 'mo_che_van_ban';
        if (typeof api_mask?.[method] !== 'function') { output.replaceChildren(el('p', 'Engine chưa sẵn sàng')); return; }
        khoa(true); output.replaceChildren(el('p', laChe ? 'Đang che văn bản DEMO…' : 'Đang mở che văn bản DEMO…'));
        try {
          const r = await api_mask[method](payload, { signal: controller.signal });
          if (!kiemQuyen()) return;
          if (laChe) hienChe(r); else hienMo(r);
        } catch (error) { if (song() && kiemQuyen()) { if (laChe) maYeuCau = null; loi(output, error); } }
        finally { if (song()) khoa(false); }
      }
      che.addEventListener('submit', event => { event.preventDefault(); return gui('che'); });
      mo.addEventListener('submit', event => { event.preventDefault(); return gui('mo'); });
      for (const input of [vanBan, known]) input.addEventListener('input', () => { if (kiemQuyen() && !dangGui) xoaKetQuaChe(); });
      coBiDanh.addEventListener('input', () => { if (kiemQuyen() && !dangGui && !chuaBat) ketQuaMo.replaceChildren(el('p', 'Chưa có kết quả mở che.')); });
      chonDemo?.addEventListener('change', () => {
        if (!kiemQuyen() || dangGui) return;
        phapNhan = cacDemo.find((_, index) => String(index) === chonDemo.value)?.id || null;
        xoaKetQuaChe(); khoa(false);
      });
      xoaKetQuaChe(); khoa(false);
    }
    return { dung: stop, san_sang: tai() };
  }
  return { dung };
});
