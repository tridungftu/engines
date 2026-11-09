'use strict';
// MASK-3I: chỉ DOM, đồng hồ và HTTP giả; không gọi engine, mạng hay CSDL.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const core = path.join(__dirname, '../src/kho_tri_thuc/core');
const source = fs.readFileSync(path.join(core, 'ui/chay_thu_mask.js'), 'utf8');
const adminSource = fs.readFileSync(path.join(core, 'ui/quan_tri.js'), 'utf8');
const contract = JSON.parse(fs.readFileSync(path.join(core, 'contract/quan_tri_engine.json'), 'utf8'));
const inventory = () => structuredClone(contract['urn:ktt:contract:quan_tri_engine.v2'].examples[0]);
const BASE = '/api/v1/quan-tri/engine/e_mask/chay-thu';
const JOB = '11111111-2222-4333-8444-555555555555';
const REQUEST = '66666666-7777-4888-8999-aaaaaaaaaaaa';
const MASK = 'bbbbbbbb-cccc-4ddd-8eee-ffffffffffff';
const COMPANY = '12345678-1234-4234-8234-123456789abc';
const USER = 'abcdef12-1234-4123-8123-abcdef123456';
const UUID = /\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b/i;

class Element {
  constructor(tag, doc) {
    this.tagName = tag; this.ownerDocument = doc; this.children = []; this.events = {};
    this.attrs = {}; this._text = ''; this.value = ''; this.disabled = false; this.hidden = false;
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(n => n.textContent).join(' '); }
  set innerHTML(_) { assert.fail('Không diễn giải dữ liệu thành HTML'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; this._text = ''; }
  setAttribute(key, value) { this.attrs[key] = String(value); }
  addEventListener(type, callback) { this.events[type] = callback; }
  click() { if (!this.disabled && !this.hidden) return this.events.click?.({ preventDefault() {} }); }
}
const all = root => [root, ...root.children.flatMap(all)];
const find = (root, tag) => all(root).filter(n => n.tagName === tag);
const field = (root, label) => all(root).find(n => n.attrs['aria-label'] === label);
const button = (root, label) => all(root).find(n => ['button', 'a'].includes(n.tagName) && n.textContent === label);
const submit = (root, index = 0) => find(root, 'form')[index].events.submit({ preventDefault() {} });
const noIds = root => {
  const domValues = all(root).map(n => [n._text, n.value, ...Object.values(n.attrs)].join(' ')).join(' ');
  assert.doesNotMatch(domValues, UUID);
  assert.doesNotMatch(root.textContent, /viec_id|request_id|ma_yeu_cau|MASK_THU_|\b(?:Anh|bạn)\b/);
};
const flush = async () => { for (let n = 0; n < 18; n++) await Promise.resolve(); };
function dom() {
  const doc = { createElement: tag => new Element(tag, doc) }; doc.head = doc.createElement('head');
  return doc.createElement('div');
}
const masked = () => ({ ma_yeu_cau: MASK, ma_luot: REQUEST,
  van_ban_da_che: '[[CT-0001]]; 1.000.000 VND; 30/10/2026.', so_cho_thay: 1,
  bi_danh: [{ bi_danh: '[[CT-0001]]', nhom: 'CONG_TY', nguon: 'chinh_thuc' }],
  cho_duyet: { so_cum_vua_them: 0 }, con_sot: [], kiem_tien_ngay: true, gui_duoc: true, canh_bao: [] });
const unmasked = () => ({ ma_yeu_cau: MASK, ma_luot: REQUEST,
  van_ban_da_mo_che: 'Công ty DEMO Ánh Dương; 1.000.000 VND; 30/10/2026.', so_cho_mo: 1,
  bi_danh_khong_ro: [], mo_day_du: true, trang_thai_ma_yeu_cau: 'DANG_XU_LY' });
const response = (status, body, extra = {}) => ({ status, ok: status >= 200 && status < 300,
  redirected: false, headers: { get: name => name.toLowerCase() === 'content-type'
    ? 'application/json; charset=utf-8' : name.toLowerCase() === 'x-request-id' ? REQUEST
      : name.toLowerCase() === 'location' && status === 202 ? BASE + '/' + JOB : null },
  json: async () => structuredClone(body), ...extra });
const accepted = () => response(202, { viec_id: JOB, trang_thai: 'queued', request_id: REQUEST });
const result = (state = 'succeeded', data = masked()) => response(200,
  { viec_id: JOB, trang_thai: state, ket_qua: state === 'succeeded' ? data : null, request_id: REQUEST });

function setup(options = {}) {
  const root = dom(), calls = [], delays = [], timers = new Map(); let seq = 0;
  const context = vm.createContext({ AbortController, console, structuredClone,
    crypto: { randomUUID: () => 'MASK_DEMO_KHOA_00001' },
    setTimeout: (callback, ms) => {
      const id = ++seq; delays.push(ms); timers.set(id, callback);
      if (options.autoTimer !== false) queueMicrotask(() => {
        if (timers.has(id)) { timers.delete(id); callback(); }
      });
      return id;
    },
    clearTimeout: id => timers.delete(id), addEventListener() {} });
  vm.runInContext(source, context);
  let session = { csrf_token: 'CSRF_DEMO', nguoi_dung_id: USER, phap_nhan_id: COMPANY };
  const sdk = { api: { goi: async req => {
    assert.equal(req.duong_dan, '/api/v1/quan-tri/engine/kiem-ke');
    if (options.auth) return options.auth(req);
    return inventory();
  } }, phap_nhan: { danh_sach: async () => ({ danh_sach: options.companies || [
    { id: COMPANY, ten: 'Công ty DEMO Ánh Dương', la_demo: true }], con_tiep: false, con_tro_tiep: null }) } };
  const guiHttp = async (url, req) => {
    calls.push({ url, req });
    if (options.http) return options.http(url, req, calls.length);
    return req.method === 'POST' ? accepted() : result();
  };
  const viewOptions = { sdk, sdk_he_thong: sdk, csrf_token: options.noToken ? undefined : 'CSRF_DEMO',
    nguoi_dung_id: USER, phap_nhan_id: COMPANY, fetch: guiHttp,
    tao_khoa: () => 'MASK_DEMO_KHOA_00001', khai_bao_da_loc_quyen: { ma: 'quan_ly_engine', thao_tac: [] },
    ...(options.liveSession ? { doc_phien: () => session } : {}),
    ...(options.api ? { api_mask: options.api } : {}), signal: options.signal };
  const view = context.KttChayThuMask.dung(root, viewOptions);
  return { root, calls, delays, timers, view, context, sdk, viewOptions,
    changeSession: value => { session = { ...session, ...value }; } };
}

test('POST rồi GET theo chu kỳ: chỉ công bố bản che sau khi việc hoàn tất', async () => {
  let reads = 0;
  const ui = setup({ http: (_, req) => req.method === 'POST' ? accepted()
    : result(['queued', 'running', 'succeeded'][reads++]) });
  await ui.view.san_sang; await submit(ui.root);
  assert.equal(ui.calls.length, 4); assert.equal(reads, 3);
  assert.equal(ui.calls[0].url, BASE + '/che-van-ban');
  assert.deepEqual(JSON.parse(ui.calls[0].req.body).dinh_danh_da_biet, []);
  assert.equal(ui.calls[0].req.headers['Idempotency-Key'], 'MASK_DEMO_KHOA_00001');
  for (const { url, req } of ui.calls) {
    assert.equal(req.headers['X-CSRF-Token'], 'CSRF_DEMO');
    assert.equal(req.headers['X-Phap-Nhan-Id'], COMPANY);
    assert.equal(req.credentials, 'same-origin'); assert.equal(req.mode, 'same-origin');
    assert.equal(req.redirect, 'error'); assert.equal(req.cache, 'no-store');
    if (req.method === 'GET') { assert.equal(url, BASE + '/' + JOB); assert.equal(req.body, undefined); }
  }
  assert.deepEqual(ui.delays, [1000, 1000]);
  assert.equal(find(field(ui.root, 'Kết quả che'), 'pre')[0].textContent, masked().van_ban_da_che);
  assert.equal(field(ui.root, 'Văn bản có bí danh').value, masked().van_ban_da_che); noIds(ui.root);
});

test('Bị chặn với văn bản null: hiện lý do và vị trí object, không hiện bản che', async () => {
  const blocked = { ...masked(), van_ban_da_che: null, gui_duoc: false,
    con_sot: [{ ly_do: 'Chưa kiểm tra đầy đủ định danh.' },
      { nhom: 'MA_SO_THUE', vi_tri: { bat_dau: 2, ket_thuc: 6, dong: 2, cot: 3 } }] };
  const ui = setup({ http: (_, req) => req.method === 'POST' ? accepted() : result('succeeded', blocked) });
  await ui.view.san_sang; await submit(ui.root);
  const output = field(ui.root, 'Kết quả che');
  assert.match(output.textContent, /Chưa kiểm tra đầy đủ định danh/);
  assert.match(output.textContent, /dòng 2, cột 3.*Mã số thuế/);
  assert.equal(find(output, 'pre').length, 0); assert.equal(field(ui.root, 'Văn bản có bí danh').value, ''); noIds(ui.root);
});

for (const changes of [{ con_sot: [{ ly_do: 'Chưa kiểm tra đầy đủ định danh.' }] },
  { kiem_tien_ngay: false }, { gui_duoc: false }]) {
  test('Mỗi kiểm chưa đạt đều chặn bản che: ' + Object.keys(changes)[0], async () => {
    const ui = setup({ http: (_, req) => req.method === 'POST' ? accepted()
      : result('succeeded', { ...masked(), ...changes, van_ban_da_che: 'NOI_DUNG_CHUA_DUOC_PHEP_DEMO' }) });
    await ui.view.san_sang; await submit(ui.root);
    assert.doesNotMatch(ui.root.textContent, /NOI_DUNG_CHUA_DUOC_PHEP_DEMO/);
    assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 0);
    assert.equal(field(ui.root, 'Văn bản có bí danh').value, ''); noIds(ui.root);
  });
}

test('Chưa bật: câu nghiệp vụ, hỗ trợ thu gọn và khóa cả hai nút gửi lâu dài', async () => {
  for (const failAt of ['che', 'mo']) {
    const ui = setup({ http: (url, req) => {
      if (failAt === 'mo' && !url.endsWith('/mo-che-van-ban')) return req.method === 'POST' ? accepted() : result();
      return response(503, { ma: 'MASK_THU_CHUA_BAT', request_id: REQUEST,
        thong_diep: 'THONG_DIEP_KHONG_TIN_CAY_DEMO' });
    } });
    await ui.view.san_sang; await submit(ui.root); if (failAt === 'mo') await submit(ui.root, 1);
    const count = failAt === 'che' ? 1 : 3;
    function stillDisabled() {
      assert.match(ui.root.textContent, /Chức năng chạy thử chưa được bật\./);
      assert.equal(button(ui.root, 'Che').disabled, true); assert.equal(button(ui.root, 'Mở che').disabled, true);
      const details = find(ui.root, 'details'); assert.equal(details.length, 1); assert.ok(!details[0].open);
      assert.equal(find(details[0], 'summary')[0].textContent, 'Chi tiết hỗ trợ');
      assert.equal(ui.calls.length, count); noIds(ui.root);
    }
    stillDisabled();
    for (const label of ['Văn bản có bí danh', 'Văn bản DEMO cần che', 'Định danh đã biết (tùy chọn)']) {
      const input = field(ui.root, label); input.value = 'DEMO đã sửa'; input.events.input(); stillDisabled();
    }
    await button(ui.root, 'Dùng mẫu DEMO').click(); stillDisabled();
    await submit(ui.root); await submit(ui.root, 1); stillDisabled();
    assert.doesNotMatch(ui.root.textContent, /THONG_DIEP_KHONG_TIN_CAY_DEMO/);
  }
});

test('Hết giới hạn 30 lần hỏi: dừng với câu tiếng Việt và không lộ mã việc', async () => {
  const ui = setup({ http: (_, req) => req.method === 'POST' ? accepted() : result('running') });
  await ui.view.san_sang; await submit(ui.root);
  assert.equal(ui.calls.filter(c => c.req.method === 'GET').length, 30);
  assert.equal(ui.delays.length, 29); assert.ok(ui.delays.every(ms => ms === 1000));
  assert.match(field(ui.root, 'Kết quả che').textContent, /Chưa.*(?:hoàn tất|kết quả)|quá.*(?:thời gian|lâu)|hết.*thời gian|thử.*lại/i);
  assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 0);
  assert.equal(find(ui.root, 'details').length, 1); assert.ok(!find(ui.root, 'details')[0].open); noIds(ui.root);
});

for (const state of ['failed', 'cancelled', 'cancel_requested']) {
  test('Việc kết thúc ' + state + ': ngừng hỏi, không dùng kết quả', async () => {
    const ui = setup({ http: (_, req) => req.method === 'POST' ? accepted() : result(state) });
    await ui.view.san_sang; await submit(ui.root);
    assert.equal(ui.calls.length, 2); assert.equal(ui.delays.length, 0);
    assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 0);
    assert.match(field(ui.root, 'Kết quả che').textContent, /Chưa|dừng|hủy/i); noIds(ui.root);
  });
}

test('Mở che gửi đúng mã trong closure, dùng đúng văn bản/trạng thái mới và đóng yêu cầu', async () => {
  let opening = false;
  const ui = setup({ http: (url, req) => {
    if (req.method === 'POST') { opening = url.endsWith('/mo-che-van-ban'); return accepted(); }
    return result('succeeded', opening ? { ...unmasked(), trang_thai_ma_yeu_cau: 'DA_DONG' } : masked());
  } });
  await ui.view.san_sang; await submit(ui.root);
  field(ui.root, 'Đóng việc sau khi mở').checked = true; await submit(ui.root, 1);
  const request = ui.calls.find(c => c.url.endsWith('/mo-che-van-ban'));
  assert.deepEqual(JSON.parse(request.req.body), { ma_yeu_cau: MASK,
    van_ban_co_bi_danh: masked().van_ban_da_che, dong_viec: true });
  const output = field(ui.root, 'Kết quả mở che');
  assert.match(output.textContent, /Đã mở che đầy đủ.*Đã đóng/);
  assert.equal(find(output, 'pre')[0].textContent, unmasked().van_ban_da_mo_che);
  await submit(ui.root, 1); assert.equal(ui.calls.length, 4); noIds(ui.root);
});

test('Rời màn lúc chờ chu kỳ hủy đồng hồ và không hỏi tiếp', async () => {
  const ui = setup({ autoTimer: false, http: (_, req) => req.method === 'POST' ? accepted() : result('running') });
  await ui.view.san_sang; const pending = submit(ui.root); await flush();
  assert.equal(ui.calls.length, 2); assert.equal(ui.timers.size, 1);
  ui.view.dung(); await pending;
  assert.equal(ui.timers.size, 0); assert.equal(ui.root.children.length, 0); assert.equal(ui.calls.length, 2);
});

test('Rời màn lúc fetch chưa xong hủy signal và bỏ phản hồi muộn', async () => {
  let finish;
  const ui = setup({ http: (_, req) => req.method === 'POST' ? accepted()
    : new Promise(resolve => { finish = resolve; }) });
  await ui.view.san_sang; const pending = submit(ui.root); await flush();
  assert.equal(ui.calls.length, 2); ui.view.dung();
  assert.equal(ui.calls[1].req.signal.aborted, true);
  finish(result()); await pending; assert.equal(ui.root.children.length, 0); assert.equal(ui.calls.length, 2);
});

test('Phiên đổi trong lúc chờ: dừng trước GET kế tiếp và xóa nội dung', async () => {
  const ui = setup({ liveSession: true, autoTimer: false,
    http: (_, req) => req.method === 'POST' ? accepted() : result('running') });
  await ui.view.san_sang; const pending = submit(ui.root); await flush();
  assert.equal(ui.calls.length, 2); assert.equal(ui.timers.size, 1);
  ui.changeSession({ nguoi_dung_id: REQUEST });
  const [id, callback] = ui.timers.entries().next().value; ui.timers.delete(id); callback(); await pending;
  assert.equal(ui.calls.length, 2); assert.equal(find(ui.root, 'form').length, 0); noIds(ui.root);
});

test('HTTP 403 lúc đọc kết quả xóa văn bản và không để UUID/lỗi gốc vào DOM', async () => {
  const ui = setup({ http: (_, req) => req.method === 'POST' ? accepted()
    : response(403, { ma: 'MA_LOI_KHONG_TIN_CAY_DEMO', thong_diep: 'CUM_GOC_DEMO', request_id: REQUEST }) });
  await ui.view.san_sang; await submit(ui.root);
  assert.equal(ui.calls.length, 2); assert.equal(find(ui.root, 'form').length, 0);
  assert.match(ui.root.textContent, /Chỉ Admin Core/); assert.doesNotMatch(ui.root.textContent, /CUM_GOC_DEMO|MA_LOI_KHONG_TIN_CAY_DEMO/);
  noIds(ui.root);
});

test('Phản hồi chuyển hướng hoặc mã việc sai: không theo URL lạ/không hiện nội dung thô', async () => {
  for (const bad of [response(202, { viec_id: 'https://ngoai.invalid/DEMO', trang_thai: 'queued' }),
    response(202, { viec_id: JOB, trang_thai: 'queued' }, { redirected: true })]) {
    const ui = setup({ http: () => bad }); await ui.view.san_sang; await submit(ui.root);
    assert.equal(ui.calls.length, 1); assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 0);
    assert.doesNotMatch(ui.root.textContent, /ngoai\.invalid|https:/); noIds(ui.root);
  }
});

test('Thiếu CSRF khóa gửi và không gọi HTTP; seam tiêm vẫn được ưu tiên', async () => {
  const missing = setup({ noToken: true }); await missing.view.san_sang;
  assert.equal(button(missing.root, 'Che').disabled, true); assert.equal(button(missing.root, 'Mở che').disabled, true);
  await submit(missing.root); assert.equal(missing.calls.length, 0);
  const ui = setup({ api: { che_van_ban: async () => masked(), mo_che_van_ban: async () => unmasked() } });
  await ui.view.san_sang; await submit(ui.root); assert.equal(ui.calls.length, 0);
  assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 1); noIds(ui.root);
});

test('Nhiều pháp nhân DEMO phải chọn; đổi pháp nhân bỏ kết quả và mã mở che cũ', async () => {
  const other = '12345678-9999-4999-8999-123456789abc';
  const ui = setup({ companies: [{ id: COMPANY, ten: 'DEMO Ánh Dương', la_demo: true },
    { id: REQUEST, ten: 'Công ty làm việc', la_demo: false },
    { id: other, ten: 'DEMO Mặt Trời', la_demo: true }] });
  await ui.view.san_sang;
  const scope = field(ui.root, 'Pháp nhân DEMO'); assert.ok(scope); assert.equal(scope.value, '');
  await submit(ui.root); assert.equal(ui.calls.length, 0);
  assert.doesNotMatch(ui.root.textContent, /Công ty làm việc/); noIds(ui.root);
  scope.value = '0'; scope.events.change(); await submit(ui.root);
  assert.equal(ui.calls[0].req.headers['X-Phap-Nhan-Id'], COMPANY);
  assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 1);
  scope.value = '1'; scope.events.change();
  assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 0);
  assert.equal(field(ui.root, 'Văn bản có bí danh').value, '');
  field(ui.root, 'Văn bản có bí danh').value = '[[CT-0001]]'; await submit(ui.root, 1);
  assert.equal(ui.calls.length, 2);
  await submit(ui.root); assert.equal(ui.calls[2].req.headers['X-Phap-Nhan-Id'], other); noIds(ui.root);
});

test('Không Admin bị chặn trước khi lấy phạm vi và gọi HTTP', async () => {
  const ui = setup({ auth: () => { throw { status: 403, request_id: REQUEST }; } });
  await ui.view.san_sang;
  assert.equal(find(ui.root, 'form').length, 0); assert.equal(ui.calls.length, 0); noIds(ui.root);
});

test('GET trả trạng thái lạ hoặc kết quả trước hoàn tất: dừng an toàn, không công bố bản che', async () => {
  for (const data of [{ viec_id: JOB, trang_thai: 'khong_ro', ket_qua: null },
    { viec_id: JOB, trang_thai: 'running', ket_qua: masked() }]) {
    const ui = setup({ http: (_, req) => req.method === 'POST' ? accepted() : response(200, data) });
    await ui.view.san_sang; await submit(ui.root);
    assert.equal(ui.calls.length, 2); assert.equal(ui.delays.length, 0);
    assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 0); noIds(ui.root);
  }
});

test('Quản trị truyền HTTP/CSRF tới DEMO và rời quản trị hủy lần hỏi đang chờ', async () => {
  const ui = setup({ autoTimer: false, http: (_, req) => req.method === 'POST' ? accepted() : result('running') });
  await ui.view.san_sang; ui.view.dung();
  vm.runInContext(adminSource, ui.context);
  const admin = ui.context.KttQuanTri.dung(ui.root, { ...ui.viewOptions, loai: 'engine' });
  await admin.san_sang;
  await button(ui.root, 'Xem chi tiết Che dữ liệu nhạy cảm').click();
  await button(ui.root, 'Chạy thử DEMO').click();
  const pending = submit(ui.root); await flush();
  assert.equal(ui.calls.length, 2); assert.equal(ui.calls[0].req.headers['X-CSRF-Token'], 'CSRF_DEMO');
  admin.dung(); await pending;
  assert.equal(ui.timers.size, 0); assert.equal(ui.root.children.length, 0); assert.equal(ui.calls.length, 2);
});
