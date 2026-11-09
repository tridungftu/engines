/* AI-LAT10b — màn DEMO chỉ Admin, chỉ Local; Core xác minh pháp nhân la_demo.
 * Giữ khung AI-L10, thay phần minh họa bằng hợp đồng chay-thu của Core.
 * HTTP cùng nguồn vì SDK hiện tại chỉ nhận 202 có viec_id, không có ma_luot.
 */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.KttChayThuHoiAi = factory();
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const CAN_CU = 'Điều khoản thanh toán: Số tiền 1.000.000 VND; ngày thanh toán 30/10/2026.';
  const TAI_LIEU = `Công ty DEMO Ánh Dương.\nHợp đồng DEMO-001 — Dữ liệu giả.\n${CAN_CU}`;
  const CAU_HOI = 'Theo đoạn DEMO, số tiền và ngày thanh toán là bao nhiêu?';
  const API = '/api/v1/quan-tri/hoi-ai/chay-thu';
  const TRANG_THAI = { dang_cho: 'Đang chờ máy AI…', dang_chay: 'Máy AI đang xử lý…', xong: 'Đã có kết quả.', loi: 'Lượt chạy thử gặp lỗi.' };
  const CSS = `.core-ai-demo{line-height:1.6}.core-ai-demo .ai-bo-cuc{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,25rem),1fr));gap:24px;margin:20px 0}.core-ai-demo .ai-phan{min-width:0;padding:20px;border:1px solid var(--line,#e3e8e1);background:var(--white,#fff);border-radius:8px}.core-ai-demo label{display:grid;gap:6px;margin:16px 0;font-weight:600}.core-ai-demo select,.core-ai-demo textarea{width:100%;max-width:100%;padding:10px;border:1px solid #aab8ad;border-radius:5px;background:#fff;color:inherit;font-weight:400}.core-ai-demo textarea{resize:vertical}.core-ai-demo .ai-nhan{padding:12px 16px;border-left:4px solid var(--green,#315c4d);background:#eef4ed}.core-ai-demo .ai-thao-tac{display:flex;flex-wrap:wrap;gap:12px;margin-top:16px}.core-ai-demo blockquote{margin:12px 0;padding:12px 16px;border-left:3px solid #8a9d88;white-space:pre-wrap;overflow-wrap:anywhere}.core-ai-demo .ai-ket-qua{white-space:pre-wrap;overflow-wrap:anywhere;max-width:75ch}.core-ai-demo .ai-bang{overflow-x:auto}.core-ai-demo table{width:100%;border-collapse:collapse}.core-ai-demo th,.core-ai-demo td{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid var(--line,#e3e8e1)}.core-ai-demo :focus-visible{outline:3px solid #739763;outline-offset:3px}`;
  const laMa = value => typeof value === 'string' && /^[A-Za-z0-9_-]{1,128}$/.test(value);
  const laId = value => typeof value === 'string' && /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(value);
  const CHON_DEMO = 'Chọn pháp nhân DEMO để chạy thử.';
  function nhanViet(value, fallback = 'Chưa ghi nhận') {
    if (typeof value !== 'string' || !value.trim() || value.length > 1000 ||
        /[\p{Cc}\p{Cf}]|https?:|:\/\/|password|api[_-]?key|\brequest_id\b|\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b|\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b|\bAnh\b|(?:^|\s)bạn(?=\s|[.,!?]|$)/iu.test(value)) return fallback;
    return value.trim();
  }
  function ngay(value) {
    // Route chạy thử Core đã định dạng ngày Việt, khác thời gian ISO của SDK.
    if (typeof value === 'string' && /^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}$/.test(value)) return value;
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value) ||
        !Number.isFinite(Date.parse(value))) return 'Chưa ghi nhận';
    const parts = new Intl.DateTimeFormat('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh', year: 'numeric',
      month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit',
      hourCycle: 'h23' }).formatToParts(new Date(value));
    const part = type => parts.find(p => p.type === type).value;
    return part('day') + '/' + part('month') + '/' + part('year') + ' ' + part('hour') + ':' + part('minute') + ':' + part('second');
  }
  function lyDo(value) {
    if (typeof value === 'string' && !value.trim()) return '—';
    if (value === 'uu_tien') return 'Model ưu tiên';
    if (value === 'co_dinh') return 'Model cố định';
    const match = typeof value === 'string' && /^du_phong:([1-9]\d{0,2})$/.exec(value);
    return match ? 'Model dự phòng ' + Number(match[1]) : 'Chưa ghi nhận';
  }
  function dung(root, { sdk_he_thong, khai_bao_da_loc_quyen: kb, signal, khi_quay_lai,
                        doc_phien, csrf_token, nguoi_dung_id,
                        fetch: guiHttp = globalThis.fetch?.bind(globalThis),
                        tao_khoa = () => globalThis.crypto.randomUUID() } = {}) {
    const doc = root.ownerDocument, controller = new AbortController();
    const el = (tag, text) => { const n = doc.createElement(tag); if (text !== undefined) n.textContent = text; return n; };
    const song = () => !controller.signal.aborted;
    const coQuyen = () => kb?.ma === 'quan_ly_engine' && !kb.khong_quyen && typeof sdk_he_thong?.api?.goi === 'function';
    const docPhien = () => doc_phien ? doc_phien() : { csrf_token, nguoi_dung_id };
    const loi = (ma, status) => Object.assign(new Error(), { ma, status });
    let dangGui = false, dangTai = false, lanTruoc = null, biChan = false, phien, functions = [], man;
    let phapNhan = null, cacDemo = [];
    let luot = null, timer = null, han = null, theoDoiController = null, doi = 1000, lanLichSu = 0;
    function dungHoi() {
      clearTimeout(timer); clearTimeout(han); timer = han = null;
      theoDoiController?.abort(); theoDoiController = null;
    }
    function stop() {
      if (!song()) return;
      dungHoi(); controller.abort(); lanTruoc = luot = phien = phapNhan = null; functions = []; cacDemo = [];
      root.replaceChildren(); signal?.removeEventListener('abort', stop);
    }
    function nut(text, action, primary = false) {
      const n = el('button', text); n.type = 'button'; n.className = 'button ' + (primary ? 'primary' : 'secondary');
      n.addEventListener('click', () => { if (song() && !n.disabled && !n.hidden && kiemQuyen()) return action(); }); return n;
    }
    function quayLai() { if (!kiemQuyen()) return; stop(); khi_quay_lai?.(); }
    function thongBao(text, choQuayLai = true) {
      dungHoi(); ++lanLichSu; lanTruoc = luot = null; functions = []; man = null;
      if (!choQuayLai) { biChan = true; phien = null; controller.abort(); }
      const p = el('p', text); p.setAttribute('role', 'alert');
      root.replaceChildren(p, ...(choQuayLai ? [nut('Quay lại Hỏi AI', quayLai)] : []));
    }
    function kiemQuyen() {
      if (!song()) return false;
      if (biChan || !coQuyen()) { thongBao('Chỉ Admin Core được chạy thử DEMO Hỏi AI.', false); return false; }
      if (phien) {
        const current = docPhien();
        if (current?.csrf_token !== phien.csrf_token || current?.nguoi_dung_id !== phien.nguoi_dung_id) {
          thongBao('Phiên làm việc đã thay đổi. Đăng nhập lại để tiếp tục.', false); return false;
        }
      }
      return true;
    }
    function hoTro(parent, error) {
      const details = el('details'); details.append(el('summary', 'Chi tiết hỗ trợ'));
      const code = error?.ma_ho_tro || error?.ma;
      if (laMa(code)) details.append(el('p', 'Mã hỗ trợ: ' + code));
      if (laMa(error?.request_id)) details.append(el('p', 'Mã tra cứu: ' + error.request_id));
      parent.append(details);
    }
    function matQuyen(error) {
      if (!song()) return true;
      if (error?.ma === 'AI_THU_PHIEN') {
        thongBao(CHON_DEMO + ' Nếu đã chọn, đăng nhập lại rồi mở lại màn Chạy thử DEMO.');
        hoTro(root, error); return true;
      }
      if (error?.status === 401 || ['NGU_CANH_DA_DOI', 'SAI_NGU_CANH'].includes(error?.ma)) {
        thongBao('Phiên làm việc đã thay đổi. Đăng nhập lại để tiếp tục.', false); return true;
      }
      if (error?.status === 403) {
        thongBao('Chỉ Admin Core được chạy thử Hỏi AI trong pháp nhân DEMO.', false); return true;
      }
      return false;
    }
    async function goi(suffix = '', method = 'GET', payload, khoa, signalTheoDoi) {
      if (!kiemQuyen()) throw loi('NGU_CANH_DA_DOI');
      const company = phapNhan;
      if (!laId(company) || !cacDemo.some(row => row.id === company)) throw loi('AI_THU_PHAM_VI');
      // Chỉ URL cố định của Core; không dùng Location hoặc URL từ phản hồi.
      const request = new AbortController();
      let huyCho;
      const daHuy = new Promise((_, reject) => { huyCho = () => reject(loi('NGU_CANH_DA_DOI')); });
      const huy = () => { request.abort(); huyCho(); };
      controller.signal.addEventListener('abort', huy, { once: true });
      signalTheoDoi?.addEventListener('abort', huy, { once: true });
      let timeout;
      const hetHan = new Promise((_, reject) => {
        timeout = setTimeout(() => { request.abort(); reject(loi('AI_THU_HET_GIO')); }, 15000);
      });
      try {
        const response = await Promise.race([guiHttp(API + suffix, { method,
          headers: { Accept: 'application/json', 'X-Phap-Nhan-Id': company, 'X-CSRF-Token': phien.csrf_token,
            ...(method === 'POST' ? { 'Content-Type': 'application/json',
              'Idempotency-Key': khoa } : {}) },
          ...(method === 'POST' ? { body: JSON.stringify(payload) } : {}),
          signal: request.signal, credentials: 'same-origin', mode: 'same-origin', redirect: 'error', cache: 'no-store'
        }), hetHan, daHuy]);
        if (!kiemQuyen() || company !== phapNhan || signalTheoDoi?.aborted) throw loi('NGU_CANH_DA_DOI');
        if (response.status === 403) throw loi('AI_THU_QUYEN', response.status);
        if (response.redirected || !/^application\/json(?:\s*;|\s*$)/i.test(response.headers?.get('Content-Type') || '')) throw loi('AI_THU_PHAN_HOI');
        const data = await Promise.race([response.json(), hetHan, daHuy]);
        if (!kiemQuyen() || company !== phapNhan || signalTheoDoi?.aborted) throw loi('NGU_CANH_DA_DOI');
        if (!response.ok) throw Object.assign(loi(laMa(data?.ma) ? data.ma : 'AI_THU_XU_LY', response.status), {
          thong_diep_viet: data?.thong_diep, ma_ho_tro: data?.ma_ho_tro, request_id: data?.request_id
        });
        if (response.status !== (method === 'POST' ? 202 : 200) || !data || typeof data !== 'object' || Array.isArray(data)) throw loi('AI_THU_PHAN_HOI');
        return data;
      } finally {
        clearTimeout(timeout); controller.signal.removeEventListener('abort', huy);
        signalTheoDoi?.removeEventListener('abort', huy);
      }
    }
    signal?.addEventListener('abort', stop, { once: true });
    if (signal?.aborted) { stop(); return { dung: stop, san_sang: Promise.resolve() }; }
    async function docPhapNhanDemo() {
      // Dùng cùng API danh mục và kho phiên Core như màn Mask; không tự cấp phiên.
      const ids = new Set(), cursors = new Set();
      let cursor;
      do {
        const page = await sdk_he_thong.phap_nhan.danh_sach({ con_tro: cursor, signal: controller.signal });
        if (!kiemQuyen()) return;
        if (!Array.isArray(page?.danh_sach) || typeof page.con_tiep !== 'boolean' ||
            (page.con_tiep && !page.danh_sach.length) || (!page.con_tiep && page.con_tro_tiep !== null)) throw loi('AI_THU_PHAM_VI');
        for (const row of page.danh_sach) {
          if (!laId(row?.id) || ids.has(row.id.toLowerCase())) throw loi('AI_THU_PHAM_VI');
          ids.add(row.id.toLowerCase());
          if (row.la_demo === true) cacDemo.push({ id: row.id, ten: row.ten });
        }
        cursor = page.con_tro_tiep;
        if (page.con_tiep && (typeof cursor !== 'string' || !cursor || cursor.length > 4096 || cursors.has(cursor))) throw loi('AI_THU_PHAM_VI');
        if (cursor) cursors.add(cursor);
      } while (cursor);
      phapNhan = cacDemo.length === 1 ? cacDemo[0].id : null;
    }
    async function tai() {
      if (!kiemQuyen()) return;
      root.replaceChildren(el('p', 'Đang kiểm tra quyền quản trị…'));
      try {
        const page = await sdk_he_thong.api.goi({ duong_dan: '/api/v1/quan-tri/engine/kiem-ke', signal: controller.signal });
        if (!kiemQuyen()) return;
        if (page?.phien_ban_quan_tri !== 2 || !Array.isArray(page.danh_sach)) throw loi('AI_THU_QUYEN');
        const current = docPhien();
        if (!current?.csrf_token || typeof current.csrf_token !== 'string') throw loi('THIEU_CSRF');
        if (nguoi_dung_id && current.nguoi_dung_id !== nguoi_dung_id) throw loi('NGU_CANH_DA_DOI');
        phien = { csrf_token: current.csrf_token, nguoi_dung_id: current.nguoi_dung_id };
        if (typeof guiHttp !== 'function') throw loi('AI_THU_CHUA_SAN_SANG');
        await docPhapNhanDemo();
        if (!kiemQuyen()) return;
        await taiChucNang();
      } catch (error) {
        if (matQuyen(error)) return;
        thongBao(error?.ma === 'THIEU_CSRF' ? 'Cần tải lại phiên đăng nhập trước khi chạy thử.'
          : 'Chưa tải được chức năng chạy thử. Quay lại Hỏi AI rồi mở lại màn.');
        hoTro(root, error);
      }
    }
    async function taiChucNang() {
      dungHoi(); ++lanLichSu; functions = []; hien();
      if (!phapNhan) return;
      dangTai = true; khoa(false); man.status.textContent = 'Đang tải chức năng chạy thử…';
      try {
        const data = await goi('/function');
        const rows = data.danh_sach ?? data.function;
        if (!Array.isArray(rows) || rows.some(f => !laMa(f?.ma_module) || !laMa(f?.ma_function) ||
            typeof f.ten_module !== 'string' || typeof (f.ten_function ?? f.mo_ta) !== 'string')) throw loi('AI_THU_PHAN_HOI');
        functions = rows.map(f => ({ ma_module: f.ma_module, ma_function: f.ma_function,
          ten_module: f.ten_module, mo_ta: f.ten_function ?? f.mo_ta }));
        if (!kiemQuyen()) return;
        hien(); await taiLichSu();
      } catch (error) {
        if (matQuyen(error)) return;
        man.status.textContent = error?.ma === 'AI_THU_PHAM_VI' ? CHON_DEMO
          : 'Chưa tải được chức năng chạy thử. Chọn lại pháp nhân DEMO hoặc mở lại màn.';
        hoTro(man.errors, error);
      } finally {
        dangTai = false; if (song() && man) khoa(dangGui);
      }
    }
    function hien() {
      const panel = el('section'); panel.className = 'core-ai-demo';
      const nhan = el('p', 'Chỉ dùng dữ liệu DEMO'); nhan.className = 'ai-nhan'; nhan.setAttribute('role', 'status');
      panel.append(el('style', CSS), nut('Quay lại Hỏi AI', quayLai), el('h3', 'Chạy thử DEMO Hỏi AI'), nhan,
        el('p', 'Chạy bằng máy AI Local trong pháp nhân DEMO. Chỉ nhập tài liệu giả.'));
      const labelDemo = el('label', 'Pháp nhân DEMO'), chonDemo = el('select');
      chonDemo.setAttribute('aria-label', 'Pháp nhân DEMO');
      const emptyDemo = el('option', 'Chọn pháp nhân DEMO'); emptyDemo.value = ''; chonDemo.append(emptyDemo);
      cacDemo.forEach((row, index) => {
        const option = el('option', nhanViet(row.ten, 'Pháp nhân DEMO được cấp quyền'));
        option.value = String(index); chonDemo.append(option);
      });
      chonDemo.value = phapNhan ? String(cacDemo.findIndex(row => row.id === phapNhan)) : '';
      labelDemo.append(chonDemo); panel.append(labelDemo);
      if (!cacDemo.length) panel.append(el('p', 'Chưa có pháp nhân DEMO được cấp quyền để chạy thử.'));
      chonDemo.addEventListener('change', () => {
        if (!kiemQuyen() || dangGui || dangTai || man?.chonDemo !== chonDemo) return;
        phapNhan = chonDemo.value === '' ? null : cacDemo.find((_, index) => String(index) === chonDemo.value)?.id || null;
        return taiChucNang();
      });
      const grid = el('div'); grid.className = 'ai-bo-cuc';
      const form = el('form'); form.className = 'ai-phan'; form.append(el('h4', 'Nội dung chạy thử'));
      const select = el('select'), documentInput = el('textarea'), question = el('textarea');
      const label = (text, input) => { const l = el('label', text); l.append(input); input.setAttribute('aria-label', text); form.append(l); };
      select.append(el('option', 'Chọn chức năng')); select.children[0].value = ''; select.value = '';
      functions.forEach((item, i) => {
        const option = el('option', nhanViet(item.ten_module, 'Module chưa có tên hiển thị') + ' — ' + nhanViet(item.mo_ta, 'Chức năng chưa có mô tả'));
        option.value = String(i); select.append(option);
      });
      label('Chức năng', select);
      if (!functions.length) form.append(el('p', 'Chưa có chức năng có hướng dẫn hợp lệ trong các module đã cài.'));
      documentInput.rows = 7; documentInput.maxLength = 20000; documentInput.value = TAI_LIEU;
      question.rows = 3; question.maxLength = 2000; question.value = CAU_HOI;
      const countDocument = el('small'), countQuestion = el('small');
      countDocument.setAttribute('aria-live', 'polite'); countQuestion.setAttribute('aria-live', 'polite');
      label('Đoạn tài liệu giả', documentInput); form.append(countDocument);
      label('Câu hỏi', question); form.append(countQuestion);
      const result = el('section'); result.className = 'ai-phan'; result.setAttribute('aria-label', 'Kết quả chạy thử');
      const status = el('p'); status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
      const answer = el('p'); answer.className = 'ai-ket-qua';
      const metadata = el('div'), errors = el('div'); errors.setAttribute('role', 'alert');
      const retry = nut('Thử lại', () => luot && !luot.ket_thuc ? batDauHoi() : lanTruoc && gui(lanTruoc));
      const review = nut('Xem lại', batDauHoi); retry.hidden = review.hidden = true;
      result.append(el('h4', 'Kết quả chạy thử'), status, answer, metadata, errors, retry, review);
      const submit = el('button', 'Gửi'); submit.type = 'submit'; submit.className = 'button primary';
      const sample = nut('Dùng đoạn mẫu', () => {
        if (dangGui) return; documentInput.value = TAI_LIEU; question.value = CAU_HOI; doiNoiDung();
      });
      const actions = el('div'); actions.className = 'ai-thao-tac'; actions.append(submit, sample); form.append(actions);
      grid.append(form, result); panel.append(grid);
      const history = el('section'); history.className = 'ai-phan';
      const noteHistory = el('p'); noteHistory.setAttribute('role', 'status');
      const wrap = el('div'), table = el('table'), head = el('thead'), headers = el('tr'), body = el('tbody');
      wrap.className = 'ai-bang'; table.append(el('caption', '20 lượt chạy thử gần nhất'));
      for (const title of ['Bắt đầu', 'Kết thúc', 'Trạng thái', 'Model đã dùng', 'Lý do chọn']) {
        const th = el('th', title); th.setAttribute('scope', 'col'); headers.append(th);
      }
      head.append(headers); table.append(head, body); wrap.append(table);
      history.append(el('h4', 'Lịch sử chạy thử'), noteHistory, nut('Tải lại lịch sử', taiLichSu), wrap);
      panel.append(history); root.replaceChildren(panel);
      man = { form, chonDemo, select, documentInput, question, submit, sample, result, status, answer, metadata, errors,
        retry, review, body, noteHistory, countDocument, countQuestion };
      form.addEventListener('submit', event => {
        event.preventDefault();
        if (man?.form !== form) return;
        const item = select.value !== '' && functions[Number(select.value)];
        return gui({ ma_module: item?.ma_module, ma_function: item?.ma_function,
          tai_lieu: documentInput.value, cau_hoi: question.value });
      });
      for (const n of [select, documentInput, question]) n.addEventListener(n === select ? 'change' : 'input', () => {
        if (kiemQuyen() && !dangGui && man?.form === form) doiNoiDung();
      });
      doiNoiDung();
    }
    function khoa(value) {
      dangGui = value;
      if (!man) return;
      man.form.setAttribute('aria-busy', String(value));
      for (const n of [man.select, man.documentInput, man.question, man.sample, man.retry, man.review]) n.disabled = value;
      man.chonDemo.disabled = value || dangTai || !cacDemo.length;
      man.submit.disabled = value || dangTai || !phapNhan || !functions.length;
    }
    function doiNoiDung() {
      dungHoi(); luot = lanTruoc = null;
      man.retry.hidden = man.review.hidden = true;
      man.status.textContent = phapNhan ? 'Chưa gửi lượt chạy thử.' : CHON_DEMO; man.answer.textContent = '';
      man.metadata.replaceChildren(); man.errors.replaceChildren();
      man.countDocument.textContent = man.documentInput.value.length.toLocaleString('vi-VN') + ' / 20.000 ký tự';
      man.countQuestion.textContent = man.question.value.length.toLocaleString('vi-VN') + ' / 2.000 ký tự';
      khoa(false);
    }
    function hienLoi(error, fallback) {
      man.answer.textContent = ''; man.metadata.replaceChildren();
      man.status.textContent = nhanViet(error?.thong_diep_viet, fallback);
      man.errors.replaceChildren(); hoTro(man.errors, error);
      man.retry.hidden = false; man.review.hidden = !luot || luot.ket_thuc;
    }
    function kiemLuot(data) {
      if (data && Object.hasOwn(data, 'ket_qua')) {
        const result = data.ket_qua;
        if (['xong', 'loi'].includes(data.trang_thai) && (!result || typeof result !== 'object' || Array.isArray(result))) throw loi('AI_THU_PHAN_HOI');
        data = { ...result, trang_thai: data.trang_thai, bat_dau: data.bat_dau, ket_thuc: data.ket_thuc };
      }
      if (!data || !Object.hasOwn(TRANG_THAI, data.trang_thai) ||
          data.trang_thai === 'xong' && typeof data.tra_loi !== 'string' ||
          data.trang_thai === 'loi' && (!data.loi || typeof data.loi.thong_diep_viet !== 'string')) throw loi('AI_THU_PHAN_HOI');
      return data;
    }
    async function taiLichSu() {
      if (!kiemQuyen() || !man) return;
      if (!phapNhan) { man.noteHistory.textContent = CHON_DEMO; return; }
      const lan = ++lanLichSu;
      man.noteHistory.textContent = 'Đang tải lịch sử…';
      try {
        const data = await goi('?gioi_han=20');
        if (!kiemQuyen() || !man || lan !== lanLichSu) return;
        const rows = data.danh_sach ?? data.luot;
        if (!Array.isArray(rows) || rows.some(row => !row || !Object.hasOwn(TRANG_THAI, row.trang_thai))) throw loi('AI_THU_PHAN_HOI');
        man.body.replaceChildren();
        for (const row of rows.slice(0, 20)) {
          const tr = el('tr');
          for (const text of [ngay(row.bat_dau), ngay(row.ket_thuc), TRANG_THAI[row.trang_thai],
            nhanViet(row.ket_qua?.model ?? row.model), lyDo(row.ket_qua?.ly_do_chon ?? row.ly_do_chon)]) tr.append(el('td', text));
          man.body.append(tr);
        }
        man.noteHistory.textContent = rows.length ? 'Mới nhất trước.' : 'Chưa có lượt chạy thử.';
      } catch (error) {
        if (!man || lan !== lanLichSu || matQuyen(error)) return;
        man.noteHistory.textContent = 'Chưa tải được lịch sử. Bấm Tải lại lịch sử để xem lại.';
      }
    }
    async function gui(request) {
      if (!kiemQuyen() || dangGui || dangTai) return;
      if (!laId(phapNhan) || !cacDemo.some(row => row.id === phapNhan)) { man.status.textContent = CHON_DEMO; return; }
      if (!functions.some(f => f.ma_module === request.ma_module && f.ma_function === request.ma_function)) {
        man.status.textContent = 'Cần chọn chức năng trong danh sách.'; return;
      }
      if (!request.tai_lieu.trim() || !request.cau_hoi.trim() || request.tai_lieu.length > 20000 || request.cau_hoi.length > 2000) {
        man.status.textContent = 'Cần nhập tài liệu giả từ 1–20.000 ký tự và câu hỏi từ 1–2.000 ký tự.'; return;
      }
      const khoaGui = !luot?.ket_thuc && lanTruoc === request && request.khoa ? request.khoa : tao_khoa();
      lanTruoc = { ma_module: request.ma_module, ma_function: request.ma_function,
        tai_lieu: request.tai_lieu, cau_hoi: request.cau_hoi, khoa: khoaGui };
      dungHoi(); luot = null; khoa(true); man.retry.hidden = man.review.hidden = true;
      man.status.textContent = TRANG_THAI.dang_cho; man.answer.textContent = '';
      man.metadata.replaceChildren(); man.errors.replaceChildren();
      try {
        const { khoa: _, ...payload } = lanTruoc;
        const accepted = await goi('', 'POST', payload, khoaGui);
        if (!kiemQuyen()) return;
        if (!laMa(accepted.ma_luot)) throw loi('AI_THU_PHAN_HOI');
        luot = { ma: accepted.ma_luot, ket_thuc: false };
        batDauHoi(); void taiLichSu();
      } catch (error) {
        if (matQuyen(error)) return;
        hienLoi(error, 'Chưa xác nhận được lượt chạy thử. Bấm Thử lại để kiểm tra cùng yêu cầu.');
        khoa(false);
      }
    }
    function batDauHoi() {
      if (!kiemQuyen() || !luot) return;
      dungHoi(); khoa(true); man.retry.hidden = man.review.hidden = true;
      man.errors.replaceChildren(); man.status.textContent = TRANG_THAI.dang_cho;
      theoDoiController = new AbortController(); doi = 1000;
      const current = theoDoiController;
      han = setTimeout(() => {
        if (current !== theoDoiController || !kiemQuyen()) return;
        dungHoi(); khoa(false); man.review.hidden = false;
        man.status.textContent = 'Đã dừng tự cập nhật sau khoảng hai phút. Bấm Xem lại để đọc tiếp lượt đã gửi.';
      }, 120000);
      void hoi(current);
    }
    async function hoi(current) {
      try {
        const data = kiemLuot(await goi('/' + encodeURIComponent(luot.ma), 'GET', undefined, undefined, current.signal));
        if (current !== theoDoiController || !kiemQuyen()) return;
        man.status.textContent = TRANG_THAI[data.trang_thai];
        if (data.trang_thai === 'dang_cho' || data.trang_thai === 'dang_chay') {
          timer = setTimeout(() => { if (current === theoDoiController) void hoi(current); }, doi);
          doi = Math.min(doi * 2, 10000); return;
        }
        luot.ket_thuc = true; dungHoi(); khoa(false);
        if (data.trang_thai === 'loi') hienLoi(data.loi, 'Lượt chạy thử chưa hoàn tất. Bấm Thử lại.');
        else {
          man.answer.textContent = data.tra_loi;
          man.metadata.replaceChildren(el('p', 'Model đã dùng: ' + nhanViet(data.model)),
            el('p', lyDo(data.ly_do_chon)), el('p', 'Bắt đầu: ' + ngay(data.bat_dau)),
            el('p', 'Kết thúc: ' + ngay(data.ket_thuc)));
        }
        void taiLichSu();
      } catch (error) {
        if (current !== theoDoiController || matQuyen(error)) return;
        dungHoi(); khoa(false);
        hienLoi(error, 'Chưa đọc được kết quả. Bấm Xem lại để tiếp tục theo dõi lượt đã gửi.');
      }
    }
    return { dung: stop, san_sang: tai() };
  }
  return { dung };
});
