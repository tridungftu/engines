/* OCR-CR-8b: đối chiếu biên nhận ABBYY qua Core, không gọi engine hay hoàn sổ hạn mức.
 * Quyền chốt do GET xác minh; không suy từ vai Admin hoặc khai báo menu.
 */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.KttOCRDoiChieu = factory();
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const BASE = '/api/v1/quan-tri/ocr/chua-ro';
  const CANH_BAO = 'Chỉ đổi trạng thái lượt; hạn mức trang sẽ được cập nhật ở bước sau';
  const UUID = /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i;
  const MA = /^ocr:[a-f0-9]{1,124}$/;
  const TEN_MODULE = { core: 'Quản trị Core', crm: 'Quản lý quan hệ khách hàng',
    m2: 'Hợp đồng', m4: 'Nghiệm thu & chi phí dự án', m9: 'Vốn vay & đầu tư tài chính',
    e_ocr: 'Nhận dạng văn bản', e_mask: 'Che dữ liệu', e_trich_xuat: 'Trích xuất dữ liệu',
    e_hoi_ai: 'Hỏi AI', e_hoa_don: 'Xử lý hóa đơn' };
  const loi = () => Object.assign(new Error(), { ma: 'OCR_MAN_KET_QUA' });
  function ten(value, fallback = 'Pháp nhân được cấp quyền') {
    return typeof value === 'string' && value.trim() && value.length <= 255 &&
      !/[<>\p{Cc}\p{Cf}]/u.test(value) && !/^[\w@.:-]+$/.test(value) &&
      !/\b[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b|\b[a-f0-9]{32,}\b|_|:\/\/|[A-Za-z]:[\\/]|password|secret|token|\b(?:Anh|bạn)\b/i.test(value)
      ? value.trim() : fallback;
  }
  function kiemDong(row) {
    if (!row || typeof row.ma_tuong_quan !== 'string' || !MA.test(row.ma_tuong_quan) ||
        !Number.isSafeInteger(row.so_trang) || row.so_trang < 1 || row.so_trang > 2147483647 ||
        !['CHUA_RO', 'DANG_GIU'].includes(row.trang_thai) ||
        typeof row.giu_luc !== 'string' || !/^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}$/.test(row.giu_luc) ||
        typeof row.module !== 'string' || !/^[a-z][a-z0-9_]{0,30}$/.test(row.module) ||
        !Number.isSafeInteger(row.phien_ban) || row.phien_ban < 1 || row.phien_ban >= Number.MAX_SAFE_INTEGER) throw loi();
    return row;
  }
  function dung(root, { sdk_he_thong: sdk, khai_bao_da_loc_quyen: kb, signal, khi_quay_lai,
      tao_khoa = () => globalThis.crypto.randomUUID() } = {}) {
    const doc = root.ownerDocument, controller = new AbortController();
    const el = (tag, text) => { const n = doc.createElement(tag); if (text !== undefined) n.textContent = text; return n; };
    const page = el('section'), label = el('label', 'Pháp nhân '), select = el('select');
    const data = el('p'), note = el('div'), content = el('div'), dialog = el('div');
    page.className = 'core-main';
    select.setAttribute('aria-label', 'Pháp nhân'); select.setAttribute('data-pham-vi', 'phap-nhan');
    data.className = 'core-nhan-du-lieu'; data.setAttribute('role', 'status');
    note.setAttribute('role', 'status'); note.setAttribute('aria-live', 'polite');
    label.append(select); page.append(el('h3', 'Đối chiếu lượt nhận dạng chưa rõ'), label, data, note);
    const nav = el('nav'); page.append(nav, content, dialog);
    let companies = [], selected = null, version = 0, pending = new AbortController();
    let writing = false, draft = false, canClose = false, denied = false;
    let moduleNames = new Map(Object.entries(TEN_MODULE));
    const alive = () => !controller.signal.aborted;
    const current = turn => alive() && turn === version;
    const permitted = () => kb?.ma === 'quan_ly_engine' && !kb.khong_quyen && !denied;
    function stop() {
      if (!alive()) return;
      ++version; controller.abort(); pending.abort(); signal?.removeEventListener('abort', stop);
      selected = null; companies = []; moduleNames.clear(); draft = false; canClose = false; root.replaceChildren();
    }
    function button(parent, title, action) {
      const n = el('button', title); n.type = 'button';
      n.addEventListener('click', () => { if (alive() && !n.disabled && !writing) return action(); });
      parent.append(n); return n;
    }
    const reload = button(nav, 'Tải lại danh sách', () => load());
    if (khi_quay_lai) button(nav, 'Quay lại chi tiết engine', () => { stop(); khi_quay_lai(); });
    function lock() {
      select.disabled = writing || !companies.length || denied;
      reload.disabled = writing || !selected || denied;
      for (const n of [...walk(content), ...walk(dialog), ...walk(nav)]) {
        if (n.tagName?.toLowerCase() === 'button') n.disabled = writing || (n === reload && (!selected || denied));
        if (n.tagName?.toLowerCase() === 'textarea') n.disabled = writing;
      }
      page.setAttribute('aria-busy', String(writing));
    }
    function walk(n) { return [n, ...Array.from(n.children).flatMap(walk)]; }
    function support(error) {
      const details = el('details'); details.append(el('summary', 'Chi tiết hỗ trợ'));
      if (typeof error?.ma === 'string' && /^[A-Z][A-Z0-9_-]{0,63}$/.test(error.ma)) details.append(el('p', `Mã lỗi: ${error.ma}`));
      if (typeof error?.request_id === 'string' && /^[A-Za-z0-9_-]{1,128}$/.test(error.request_id))
        details.append(el('p', `request_id: ${error.request_id}`));
      return details;
    }
    function failure(error) {
      if (['NGU_CANH_DA_DOI', 'SAI_NGU_CANH'].includes(error?.ma)) { stop(); return; }
      canClose = false; draft = false; dialog.replaceChildren(); content.replaceChildren();
      if (error?.status === 401) denied = true;
      const text = error?.status === 409 ? 'Lượt vừa thay đổi, tải lại danh sách'
        : error?.status === 401 ? 'Phiên đăng nhập đã hết. Cần đăng nhập lại.'
        : error?.status === 403 ? 'Chưa được cấp quyền thực hiện thao tác này.'
        : 'Chưa xác nhận được kết quả. Tải lại danh sách để đối chiếu trước khi chốt.';
      note.replaceChildren(el('p', text), support(error));
    }
    async function call(request, turn) {
      const result = await sdk.api.goi({ ...request, signal: pending.signal });
      if (!current(turn)) throw Object.assign(new Error(), { name: 'AbortError' });
      return result;
    }
    function draw(rows, turn) {
      content.replaceChildren();
      if (!rows.length) { content.append(el('p', 'Không có lượt chưa rõ cần đối chiếu.')); return; }
      const table = el('table'), head = el('thead'), titles = el('tr'), body = el('tbody'), wrap = el('div');
      table.className = 'core-bang'; wrap.className = 'core-bang-cuon';
      table.append(el('caption', 'Lượt nhận dạng cần đối chiếu ABBYY'));
      for (const title of ['Lượt đối chiếu', 'Số trang', 'Trạng thái', 'Thời điểm giữ', 'Module gọi', 'Thao tác']) {
        const th = el('th', title); th.setAttribute('scope', 'col'); titles.append(th);
      }
      head.append(titles);
      rows.forEach((row, index) => {
        const tr = el('tr'), actions = el('td');
        // Mã rút gọn dùng đối chiếu; mã đầy đủ và băm chỉ nằm trong hỗ trợ thu gọn.
        const raw = row.ma_tuong_quan.slice(4);
        const short = `Lượt ${index + 1} · ${raw.length > 8 ? raw.slice(0, 4) + '…' + raw.slice(-4) : '…' + raw.slice(-4)}`;
        tr.append(el('td', short), el('td', `${row.so_trang} trang`),
          el('td', row.trang_thai === 'CHUA_RO' ? 'Chưa rõ' : 'Đang giữ quá hạn'),
          el('td', row.giu_luc.slice(0, 16)), el('td', moduleNames.get(row.module) || 'Module nghiệp vụ'), actions);
        if (canClose) {
          button(actions, 'Chốt đã tiêu trang', () => { if (current(turn)) open(row, 'da_tieu', turn); });
          button(actions, 'Chốt hoàn trang', () => { if (current(turn)) open(row, 'hoan_trang', turn); });
          actions.append(el('small', CANH_BAO));
        } else actions.append(el('span', 'Chỉ xem'));
        const details = el('details'); details.append(el('summary', 'Chi tiết hỗ trợ'), el('p', `Mã tương quan: ${row.ma_tuong_quan}`));
        if (typeof row.ma_bam_dau === 'string' && /^[a-f0-9]{1,8}$/.test(row.ma_bam_dau))
          details.append(el('p', `Băm rút gọn: ${row.ma_bam_dau}`));
        actions.append(details); body.append(tr);
      });
      table.append(head, body); wrap.append(table); content.append(wrap);
      if (rows.length === 100) content.append(el('p', 'Đang hiển thị tối đa 100 lượt. Chốt và tải lại để tiếp tục đối chiếu các lượt còn lại.'));
    }
    async function load(message = '') {
      if (!permitted() || !selected || writing) return;
      pending.abort(); pending = new AbortController(); const turn = ++version;
      canClose = false; draft = false; content.replaceChildren(); dialog.replaceChildren();
      note.replaceChildren(el('p', 'Đang tải danh sách đối chiếu…'));
      try {
        const result = await call({ duong_dan: `${BASE}?phap_nhan_id=${encodeURIComponent(selected.id)}&gioi_han=100`,
          phap_nhan_id: selected.id, module: 'core' }, turn);
        if (!Array.isArray(result?.danh_sach) || result.danh_sach.length > 100 ||
            new Set(result.danh_sach.map(r => r?.ma_tuong_quan)).size !== result.danh_sach.length) throw loi();
        const rows = result.danh_sach.map(kiemDong);
        canClose = result.co_quyen_chot === true; draw(rows, turn);
        note.replaceChildren(...(message ? [el('p', message)] : []));
      } catch (error) { if (current(turn)) failure(error); }
      finally { if (current(turn)) lock(); }
    }
    function open(row, result, turn) {
      if (!canClose || !permitted() || !current(turn)) return;
      draft = true; dialog.replaceChildren();
      const box = el('dialog'), title = result === 'da_tieu' ? 'Chốt đã tiêu trang' : 'Chốt hoàn trang';
      box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', 'Xác nhận ' + title.toLowerCase());
      const label = el('label', 'Bằng chứng đối chiếu ABBYY '), input = el('textarea'), validation = el('p');
      input.setAttribute('aria-label', 'Bằng chứng đối chiếu ABBYY'); input.required = true; input.maxLength = 500;
      validation.setAttribute('role', 'alert');
      label.append(input); box.append(el('h4', 'Xác nhận ' + title.toLowerCase()),
        el('p', `${selected.ten} — ${row.so_trang} trang.`), label, el('p', 'Bắt buộc nhập bằng chứng, tối đa 500 ký tự.'), validation);
      if (result === 'hoan_trang') box.append(el('p', CANH_BAO));
      button(box, 'Xác nhận chốt', async () => {
        if (!current(turn) || !canClose || !permitted() || !draft) return;
        const noteText = input.value;
        if (!noteText.trim() || Array.from(noteText).length > 500) {
          validation.textContent = 'Cần ghi bằng chứng đối chiếu ABBYY, không rỗng và tối đa 500 ký tự.'; input.focus?.(); return;
        }
        const company = selected.id; writing = true; lock();
        try {
          // MA đã giới hạn vào ocr: + hex; SDK từ chối percent-encoding trong path.
          const data = await call({ duong_dan: `${BASE}/${row.ma_tuong_quan}/chot`,
            phuong_thuc: 'POST', phap_nhan_id: company, module: 'core', khoa: tao_khoa(),
            du_lieu: { ket_qua: result, phien_ban: row.phien_ban, ghi_chu: noteText } }, turn);
          if (data?.ma_tuong_quan !== row.ma_tuong_quan || data.so_trang !== row.so_trang ||
              data.phien_ban !== row.phien_ban + 1 || data.trang_thai !== (result === 'da_tieu' ? 'DA_TIEU_TRANG' : 'HOAN_TRANG')) throw loi();
          draft = false; writing = false;
          await load(result === 'da_tieu' ? 'Đã chốt lượt đã tiêu trang.' : 'Đã chốt trạng thái hoàn trang. ' + CANH_BAO + '.');
        } catch (error) { if (current(turn)) failure(error); }
        finally { writing = false; if (alive()) lock(); }
      });
      button(box, 'Hủy', () => { draft = false; dialog.replaceChildren(); });
      box.addEventListener('cancel', event => { event.preventDefault(); if (!writing) { draft = false; dialog.replaceChildren(); } });
      dialog.append(box); box.showModal?.(); input.focus?.();
    }
    select.addEventListener('change', () => {
      if (!alive() || writing || select.disabled) return;
      pending.abort(); ++version; selected = companies[Number(select.value)] && select.value !== '' ? companies[Number(select.value)] : null;
      canClose = false; draft = false; content.replaceChildren(); dialog.replaceChildren(); note.replaceChildren();
      data.textContent = selected ? `${selected.ten} — ${selected.la_demo === true ? 'DEMO — dữ liệu thử' : 'Dữ liệu làm việc'}` : 'Chọn pháp nhân để tiếp tục';
      lock(); return load();
    });
    async function docTenModule() {
      const names = new Map(moduleNames), cursors = new Set(); let cursor;
      do {
        const result = await sdk.api.goi({ duong_dan: '/api/v1/quan-tri/module/ten' +
          (cursor ? '?con_tro=' + encodeURIComponent(cursor) : ''), signal: controller.signal });
        if (!alive()) return;
        if (!Array.isArray(result?.danh_sach) || typeof result.con_tiep !== 'boolean' ||
            (!result.con_tiep && result.con_tro_tiep !== null) || (result.con_tiep && !result.danh_sach.length)) throw loi();
        for (const row of result.danh_sach) {
          const name = ten(row?.ten, null);
          if (typeof row?.ma === 'string' && /^[a-z][a-z0-9_]{0,30}$/.test(row.ma) && name) names.set(row.ma, name);
        }
        cursor = result.con_tiep ? result.con_tro_tiep : null;
        if (result.con_tiep && (typeof cursor !== 'string' || !cursor || cursor.length > 4096 || cursors.has(cursor))) throw loi();
        if (cursor) cursors.add(cursor);
      } while (cursor);
      moduleNames = names;
    }
    async function start() {
      if (!permitted() || signal?.aborted) { stop(); return; }
      root.replaceChildren(page); select.disabled = true; reload.disabled = true;
      data.textContent = 'Chọn pháp nhân để tiếp tục'; note.textContent = 'Đang tải danh sách pháp nhân…';
      try {
        const ids = new Set(), cursors = new Set(), list = []; let cursor;
        do {
          const result = await sdk.phap_nhan.danh_sach({ con_tro: cursor, signal: controller.signal });
          if (!alive()) return;
          if (!Array.isArray(result?.danh_sach) || typeof result.con_tiep !== 'boolean' ||
              (!result.con_tiep && result.con_tro_tiep !== null) || (result.con_tiep && !result.danh_sach.length)) throw loi();
          for (const row of result.danh_sach) {
            if (!UUID.test(row?.id) || ids.has(row.id.toLowerCase())) throw loi();
            ids.add(row.id.toLowerCase()); list.push({ id: row.id, ten: ten(row.ten), la_demo: row.la_demo });
          }
          cursor = result.con_tiep ? result.con_tro_tiep : null;
          if (result.con_tiep && (typeof cursor !== 'string' || !cursor || cursor.length > 4096 || cursors.has(cursor))) throw loi();
          if (cursor) cursors.add(cursor);
        } while (cursor);
        // Tên module lấy từ registry đã xác minh; thiếu quyền đọc danh mục vẫn xem được lượt OCR.
        try { await docTenModule(); }
        catch (error) {
          if (error?.status === 401 || ['NGU_CANH_DA_DOI', 'SAI_NGU_CANH'].includes(error?.ma)) { failure(error); return; }
        }
        if (!alive()) return;
        companies = list; const empty = el('option', 'Chọn pháp nhân để tiếp tục'); empty.value = ''; select.append(empty);
        companies.forEach((row, i) => { const o = el('option', row.ten); o.value = String(i); select.append(o); });
        select.value = ''; note.textContent = companies.length ? '' : 'Chưa được cấp phạm vi pháp nhân.'; lock();
      } catch (error) { if (alive()) { failure(error); lock(); } }
    }
    signal?.addEventListener('abort', stop, { once: true });
    return { san_sang: start(), dung: stop, co_nhap: () => draft || writing };
  }
  return { dung };
});
