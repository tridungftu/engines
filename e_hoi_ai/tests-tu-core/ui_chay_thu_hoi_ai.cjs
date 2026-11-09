'use strict';
// AI-LAT10b vòng 2: QD-TAM-20261108-02; DOM/SDK/HTTP/đồng hồ giả, không AI/mạng/CSDL.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const dir = path.join(__dirname, '../src/kho_tri_thuc/core');
const source = fs.readFileSync(path.join(dir, 'ui/chay_thu_hoi_ai.js'), 'utf8');
const quanTriSource = fs.readFileSync(path.join(dir, 'ui/quan_tri.js'), 'utf8');
const contract = JSON.parse(fs.readFileSync(path.join(dir, 'contract/quan_tri_engine.json'), 'utf8'));
const inventory = () => structuredClone(contract['urn:ktt:contract:quan_tri_engine.v2'].examples[0]);
const API = '/api/v1/quan-tri/hoi-ai/chay-thu';
const PN = '10000000-0000-4000-8000-000000000001';
const demoPage = () => ({ danh_sach: [{ id: PN, ten: 'Công ty DEMO Ánh Dương', la_demo: true }],
  con_tiep: false, con_tro_tiep: null });
const functions = [{ ma_module: 'hop_dong_demo', ten_module: 'Hợp đồng DEMO',
  ma_function: 'thanh_toan_demo', mo_ta: 'Tra cứu điều khoản thanh toán' }];
const completed = () => ({ trang_thai: 'xong',
  tra_loi: 'Số tiền thanh toán: 1.000.000 VND; ngày thanh toán: 30/10/2026.',
  model: 'Qwen DEMO', ly_do_chon: 'uu_tien',
  bat_dau: '2026-11-08T01:02:03Z', ket_thuc: '2026-11-08T01:02:05Z' });
const response = (body, status = 200) => ({ status, ok: status >= 200 && status < 300,
  headers: { get: key => key === 'Content-Type' ? 'application/json; charset=utf-8' : null },
  json: async () => body });
class Element {
  constructor(tag, doc) {
    this.tagName = tag; this.ownerDocument = doc; this.children = []; this.events = {};
    this.attrs = {}; this._text = ''; this.value = ''; this.disabled = false; this.hidden = false;
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(n => n.textContent).join(' '); }
  set innerHTML(value) { assert.fail('Không được diễn giải nội dung thành HTML'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; this._text = ''; }
  setAttribute(key, value) { this.attrs[key] = String(value); }
  addEventListener(type, callback) { this.events[type] = callback; }
  click() { if (!this.disabled && !this.hidden) return this.events.click?.({ preventDefault() {} }); }
}
const all = root => [root, ...root.children.flatMap(all)];
const find = (root, tag) => all(root).filter(n => n.tagName === tag);
const button = (root, text) => all(root).find(n => ['button', 'a'].includes(n.tagName) && n.textContent === text);
const field = (root, text) => all(root).find(n => n.attrs['aria-label'] === text);
const shown = root => root.hidden || root.tagName === 'style' ? '' : root._text + root.children.map(shown).join(' ');
const flush = async () => { for (let i = 0; i < 5; i++) await new Promise(setImmediate); };
function dom() {
  const doc = { createElement: tag => new Element(tag, doc) };
  doc.head = doc.createElement('head'); return doc.createElement('div');
}
function fakeClock() {
  let time = 0, key = 0; const jobs = new Map();
  return { jobs,
    setTimeout(callback, delay) { jobs.set(++key, { callback, at: time + delay }); return key; },
    clearTimeout(id) { jobs.delete(id); },
    async tick(ms) {
      const end = time + ms; let count = 0;
      while (true) {
        const next = [...jobs].filter(([, job]) => job.at <= end).sort((a, b) => a[1].at - b[1].at)[0];
        if (!next) break;
        assert.ok(++count < 1000, 'Không lặp đồng hồ vô hạn');
        jobs.delete(next[0]); time = next[1].at; next[1].callback(); await flush();
      }
      time = end; await flush();
    }
  };
}
function mockHttp(options = {}) {
  const httpCalls = [], history = []; let keys = 0;
  const fetch = async (url, init) => {
    httpCalls.push({ url, init });
    assert.ok([API, API + '/function', API + '?gioi_han=20'].includes(url) ||
      new RegExp('^' + API + '/luot_demo_[1-9][0-9]*$').test(url), 'Chỉ gọi route chạy thử của Core, không Cloud');
    assert.equal(init.method, url === API ? 'POST' : 'GET');
    assert.equal(init.mode, 'same-origin'); assert.equal(init.credentials, 'same-origin');
    assert.equal(init.redirect, 'error'); assert.equal(init.cache, 'no-store');
    if (init.method === 'POST') {
      assert.equal(init.headers['X-CSRF-Token'], 'CSRF_DEMO');
      assert.ok(init.headers['Idempotency-Key']);
      assert.deepEqual(Object.keys(JSON.parse(init.body)).sort(), ['cau_hoi', 'ma_function', 'ma_module', 'tai_lieu']);
    }
    if (options.httpHandler) {
      const result = await options.httpHandler(url, init, httpCalls);
      if (result !== undefined) return result;
    }
    if (url === API + '/function') return response({ function: functions });
    if (url === API + '?gioi_han=20') return response({ luot: history });
    if (url === API) {
      const ma_luot = 'luot_demo_' + ++keys;
      history.unshift({ ...completed(), ma_luot });
      return response({ ma_luot }, 202);
    }
    return response(completed());
  };
  return { fetch, httpCalls };
}
const posts = ui => ui.httpCalls.filter(c => c.init.method === 'POST');
function setup(options = {}) {
  const root = dom(), calls = [], kb = options.kb === undefined ? { ma: 'quan_ly_engine', thao_tac: [] } : options.kb;
  const clock = fakeClock(), http = mockHttp(options); let keys = 0;
  let session = { csrf_token: options.noCsrf ? '' : 'CSRF_DEMO', nguoi_dung_id: 'nguoi_demo' };
  const context = vm.createContext({ AbortController, setTimeout: clock.setTimeout, clearTimeout: clock.clearTimeout });
  vm.runInContext(source, context);
  const sdk = { api: { goi: async request => {
    calls.push(request); assert.equal(request.duong_dan, '/api/v1/quan-tri/engine/kiem-ke');
    assert.equal(request.phuong_thuc || 'GET', 'GET');
    return options.handler ? options.handler(request) : inventory();
  } }, phap_nhan: { danh_sach: async () => demoPage() } };
  const view = context.KttChayThuHoiAi.dung(root, { sdk_he_thong: options.noSdk ? undefined : sdk,
    khai_bao_da_loc_quyen: kb, signal: options.signal, khi_quay_lai: options.back,
    fetch: http.fetch, doc_phien: () => session, nguoi_dung_id: 'nguoi_demo',
    tao_khoa: () => 'khoa_demo_' + ++keys });
  return { root, calls, view, kb, clock, ...http, session(value) { session = value; } };
}
const historyCount = root => find(root, 'tbody')[0].children.length;
const send = async root => { await find(root, 'form')[0].events.submit({ preventDefault() {} }); await flush(); };
const change = (node, value) => { node.value = value; return (node.events.change || node.events.input)?.(); };
const choose = (root, value = '0') => change(field(root, 'Chức năng'), value);
const result = root => field(root, 'Kết quả chạy thử');

test('Admin mở màn: GET quyền, function và lịch sử Core; DEMO chỉ Local, chưa chọn chức năng', async () => {
  const ui = setup(); await ui.view.san_sang;
  assert.equal(ui.calls.length, 1);
  assert.equal(ui.calls[0].signal.aborted, false);
  assert.deepEqual(ui.httpCalls.map(c => c.url), [API + '/function', API + '?gioi_han=20']);
  for (const text of ['Chạy thử DEMO Hỏi AI', 'Chỉ dùng dữ liệu DEMO', 'máy AI Local', 'Lịch sử chạy thử',
    'Hợp đồng DEMO — Tra cứu điều khoản thanh toán']) assert.ok(shown(ui.root).includes(text));
  for (const name of ['Chức năng', 'Đoạn tài liệu giả', 'Câu hỏi']) assert.ok(field(ui.root, name));
  assert.equal(field(ui.root, 'Chức năng').value, '');
  assert.equal(find(ui.root, 'select').length, 2); assert.equal(find(ui.root, 'option').length, 4);
  assert.ok(button(ui.root, 'Gửi')); assert.equal(historyCount(ui.root), 0);
  assert.doesNotMatch(shown(ui.root), /Cloud|chưa nối engine|chưa kiểm lưu/);
  assert.equal(button(ui.root, 'Thử lại').hidden, true);
});

for (const [ten, kb] of [['không có khai báo', null], ['bị từ chối', { ma: 'quan_ly_engine', khong_quyen: true }],
  ['màn khác', { ma: 'quan_ly_module' }]]) test(`Chặn người không Admin: ${ten}, không gọi SDK`, async () => {
  const ui = setup({ kb }); await ui.view.san_sang;
  assert.equal(ui.calls.length, 0); assert.match(shown(ui.root), /Chỉ Admin Core/);
  assert.equal(ui.httpCalls.length, 0);
  assert.equal(find(ui.root, 'form').length, 0); assert.equal(button(ui.root, 'Gửi'), undefined);
});
test('Không có SDK xác minh thì không mở màn', async () => {
  const ui = setup({ noSdk: true }); await ui.view.san_sang;
  assert.equal(ui.calls.length, 0); assert.equal(find(ui.root, 'form').length, 0);
});
test('Thiếu CSRF: không tải function, không mở form hay gửi HTTP', async () => {
  const ui = setup({ noCsrf: true }); await ui.view.san_sang;
  assert.equal(ui.httpCalls.length, 0); assert.equal(find(ui.root, 'form').length, 0);
  assert.match(shown(ui.root), /Cần tải lại phiên đăng nhập/);
});
for (const error of [{ status: 403 }, { status: 401 }, { ma: 'NGU_CANH_DA_DOI' },
  { ma: 'SAI_NGU_CANH' }, { status: 500, message: 'SECRET_DEMO postgres://CANARY' }]) {
  test(`GET quyền thất bại ${error.status || error.ma}: không hiện dữ liệu/kỹ thuật`, async () => {
    const ui = setup({ handler: () => { throw error; } }); await ui.view.san_sang;
    assert.equal(find(ui.root, 'form').length, 0); assert.equal(find(ui.root, 'table').length, 0);
    assert.doesNotMatch(shown(ui.root), /SECRET_DEMO|postgres|CANARY|NGU_CANH|SAI_NGU_CANH/);
    if (error.status !== 500) assert.equal(button(ui.root, 'Quay lại Hỏi AI'), undefined);
  });
}
test('Response quyền không hợp lệ không được dùng làm bằng chứng Admin', async () => {
  const ui = setup({ handler: () => ({ danh_sach: [] }) }); await ui.view.san_sang;
  assert.equal(find(ui.root, 'form').length, 0); assert.equal(ui.httpCalls.length, 0);
  assert.match(shown(ui.root), /Chưa tải được chức năng chạy thử/);
});
// Bỏ tự trích dẫn tại trình duyệt: kiểm payload và câu trả lời đúng từ Core.
test('Gửi đoạn mẫu: POST nguyên văn, đọc ma_luot; tiền/ngày và model theo kết quả Core', async () => {
  const ui = setup(); await ui.view.san_sang;
  const documentInput = field(ui.root, 'Đoạn tài liệu giả');
  change(documentInput, 'Dòng bổ sung giả.\r\n' + documentInput.value);
  choose(ui.root); await send(ui.root);
  const output = result(ui.root), body = JSON.parse(posts(ui)[0].init.body);
  assert.equal(body.tai_lieu, documentInput.value); assert.equal(body.cau_hoi, field(ui.root, 'Câu hỏi').value);
  assert.equal(body.ma_module, functions[0].ma_module); assert.equal(body.ma_function, functions[0].ma_function);
  assert.match(shown(output), /1\.000\.000 VND/); assert.match(shown(output), /30\/10\/2026/);
  assert.match(shown(output), /Qwen DEMO.*Model ưu tiên.*08\/11\/2026 08:02:03/s);
  assert.ok(ui.httpCalls.some(c => c.url === API + '/luot_demo_1'));
  assert.equal(find(output, 'blockquote').length, 0);
  assert.equal(historyCount(ui.root), 1); assert.equal(ui.calls.length, 1);
});
for (const [ten, taiLieu, cauHoi] of [['tài liệu không có thông tin', 'Không có điều khoản thanh toán trong đoạn giả.', null],
  ['câu hỏi ngoài tài liệu', null, 'Thời hạn bảo hành là bao lâu?'],
  ['câu hỏi khác có chữ số tiền', null, 'Số tiền phạt vi phạm là bao nhiêu?']]) {
  test(`Core trả Không thấy căn cứ khi ${ten}: không bịa hoặc giữ kết quả cũ`, async () => {
    let noEvidence = false;
    const ui = setup({ httpHandler: url => /\/luot_demo_\d+$/.test(url)
      ? response({ ...completed(), tra_loi: noEvidence ? 'Không thấy căn cứ trong tài liệu DEMO.' : completed().tra_loi }) : undefined });
    await ui.view.san_sang; choose(ui.root); await send(ui.root);
    assert.match(shown(result(ui.root)), /1\.000\.000 VND/); noEvidence = true;
    if (taiLieu) change(field(ui.root, 'Đoạn tài liệu giả'), taiLieu);
    if (cauHoi) change(field(ui.root, 'Câu hỏi'), cauHoi);
    await send(ui.root);
    const body = JSON.parse(posts(ui)[1].init.body);
    assert.equal(body.tai_lieu, field(ui.root, 'Đoạn tài liệu giả').value);
    assert.equal(body.cau_hoi, field(ui.root, 'Câu hỏi').value);
    assert.match(shown(result(ui.root)), /Không thấy căn cứ/);
    assert.equal(find(result(ui.root), 'blockquote').length, 0);
    assert.doesNotMatch(shown(result(ui.root)), /1\.000\.000|30\/10\/2026/);
  });
}
test('Function ngoài danh sách hợp lệ từ Core bị chặn, không dùng function trước hay prompt mặc định', async () => {
  const ui = setup(); await ui.view.san_sang; choose(ui.root); await send(ui.root);
  choose(ui.root, 'thieu_huong_dan'); await send(ui.root);
  assert.match(shown(result(ui.root)), /Cần chọn chức năng trong danh sách/);
  assert.equal(find(result(ui.root), 'blockquote').length, 0);
  assert.doesNotMatch(shown(result(ui.root)), /1\.000\.000 VND/);
  assert.equal(posts(ui).length, 1); assert.equal(historyCount(ui.root), 1);
  const empty = setup({ httpHandler: url => url === API + '/function' ? response({ function: [] }) : undefined });
  await empty.view.san_sang; await send(empty.root);
  assert.match(shown(empty.root), /Chưa có chức năng có hướng dẫn hợp lệ/);
  assert.equal(button(empty.root, 'Gửi').disabled, true); assert.equal(posts(empty).length, 0);
});
for (const [tinhHuong, message] of [['mat_ket_noi', 'Mất kết nối máy AI Local. Cần thử lại.'],
  ['chua_san_sang', 'Mô hình Local chưa sẵn sàng. Cần thử lại.']]) test(`Core báo Local ${tinhHuong}: Thử lại sau phục hồi vẫn không Cloud`, async () => {
  let failed = true;
  const ui = setup({ httpHandler: url => /\/luot_demo_\d+$/.test(url)
    ? response(failed ? { trang_thai: 'loi', loi: { thong_diep_viet: message, ma_ho_tro: 'AI_LOCAL_DEMO' } } : completed()) : undefined });
  await ui.view.san_sang; choose(ui.root); await send(ui.root);
  assert.ok(shown(result(ui.root)).includes(message));
  const retry = button(ui.root, 'Thử lại'); assert.equal(retry.hidden, false);
  failed = false; await retry.click(); await flush();
  assert.match(shown(result(ui.root)), /Số tiền thanh toán: 1\.000\.000 VND/);
  assert.equal(retry.hidden, true); assert.equal(historyCount(ui.root), 2);
  assert.equal(posts(ui).length, 2);
  assert.notEqual(posts(ui)[0].init.headers['Idempotency-Key'], posts(ui)[1].init.headers['Idempotency-Key']);
  assert.doesNotMatch(shown(ui.root), /Cloud/); assert.equal(ui.calls.length, 1);
});
test('Kết quả Core thiếu tra_loi: không công bố thành công hoặc dùng trường trích dẫn ngoài hợp đồng', async () => {
  const ui = setup({ httpHandler: url => /\/luot_demo_\d+$/.test(url)
    ? response({ trang_thai: 'xong', trich_dan: 'Số tiền thanh toán: 9.000.000 VND', kiem_dat: true }) : undefined });
  await ui.view.san_sang; choose(ui.root); await send(ui.root);
  assert.match(shown(result(ui.root)), /Chưa đọc được kết quả/);
  assert.equal(find(result(ui.root), 'blockquote').length, 0);
  assert.doesNotMatch(shown(result(ui.root)), /Đã có kết quả|Số tiền thanh toán:/);
  assert.equal(button(ui.root, 'Xem lại').hidden, false); assert.equal(ui.clock.jobs.size, 0);
});
test('Hai lần gửi đồng thời chỉ POST một lượt; nút Gửi khóa trong lúc xử lý', async () => {
  let resolve;
  const ui = setup({ httpHandler: (_, init) => init.method === 'POST' ? new Promise(r => { resolve = r; }) : undefined });
  await ui.view.san_sang; choose(ui.root);
  const first = send(ui.root); assert.equal(button(ui.root, 'Gửi').disabled, true);
  const second = send(ui.root); assert.equal(posts(ui).length, 1);
  resolve(response({ ma_luot: 'luot_demo_1' }, 202)); await Promise.all([first, second]);
  assert.equal(posts(ui).length, 1); assert.equal(button(ui.root, 'Gửi').disabled, false);
});
test('Kiểm đầu vào: thiếu tài liệu/câu hỏi hoặc vượt giới hạn không tạo lượt', async () => {
  const ui = setup(); await ui.view.san_sang;
  for (const [name, value] of [['Đoạn tài liệu giả', ' '], ['Câu hỏi', ''],
    ['Đoạn tài liệu giả', 'x'.repeat(20001)], ['Câu hỏi', 'x'.repeat(2001)]]) {
    await button(ui.root, 'Dùng đoạn mẫu').click(); choose(ui.root); change(field(ui.root, name), value); await send(ui.root);
    assert.equal(posts(ui).length, 0); assert.equal(historyCount(ui.root), 0);
    assert.equal(find(result(ui.root), 'blockquote').length, 0);
    assert.match(shown(result(ui.root)), /Cần nhập|tối đa/);
  }
});
test('Thay nội dung bỏ kết quả/Thử lại cũ, Dùng đoạn mẫu chỉ đổi nội dung nhập', async () => {
  const ui = setup({ httpHandler: url => /\/luot_demo_\d+$/.test(url)
    ? response({ trang_thai: 'loi', loi: { thong_diep_viet: 'Mất kết nối máy AI Local.' } }) : undefined });
  await ui.view.san_sang; choose(ui.root); await send(ui.root);
  const retry = button(ui.root, 'Thử lại'); change(field(ui.root, 'Câu hỏi'), 'Câu hỏi mới giả');
  assert.equal(retry.hidden, true); await retry.events.click(); assert.equal(posts(ui).length, 1);
  assert.doesNotMatch(shown(result(ui.root)), /Mất kết nối/);
  await button(ui.root, 'Dùng đoạn mẫu').click(); assert.match(field(ui.root, 'Câu hỏi').value, /số tiền và ngày thanh toán/);
  assert.equal(posts(ui).length, 1); assert.equal(historyCount(ui.root), 1);
});
test('Chữ Việt, ngày, tiền đúng quy ước; nội dung chỉ qua textContent, không mã kỹ thuật', async () => {
  const hostile = '<img src=x onerror=alert(1)> Dữ liệu giả';
  let hostileAnswer = true;
  const ui = setup({ httpHandler: url => /\/luot_demo_\d+$/.test(url)
    ? response({ ...completed(), tra_loi: hostileAnswer ? hostile : completed().tra_loi,
      prompt: 'SECRET_DEMO', khoa: 'SECRET_DEMO' }) : undefined });
  await ui.view.san_sang; choose(ui.root);
  change(field(ui.root, 'Đoạn tài liệu giả'), hostile); change(field(ui.root, 'Câu hỏi'), hostile); await send(ui.root);
  assert.ok(shown(result(ui.root)).includes(hostile));
  assert.equal(JSON.parse(posts(ui)[0].init.body).tai_lieu, hostile);
  assert.equal(find(ui.root, 'img').length, 0); assert.equal(find(ui.root, 'script').length, 0);
  assert.doesNotMatch(shown(ui.root), /SECRET_DEMO/); hostileAnswer = false;
  await button(ui.root, 'Dùng đoạn mẫu').click(); await send(ui.root);
  assert.doesNotMatch(shown(ui.root), /\ufffd|\b(?:Anh|bạn)\b|e_hoi_ai|thieu_huong_dan|row_version|request_id|2026-11-08/u);
  assert.match(shown(ui.root), /08\/11\/2026/); assert.match(shown(ui.root), /1\.000\.000 VND/);
  assert.equal(/innerHTML|insertAdjacentHTML|\bfetch\s*\(|localStorage|sessionStorage|api\.openai|api\.anthropic/.test(source), false);
});
test('Rời màn khi đang gửi xóa nội dung và chặn mọi nút cũ', async () => {
  let resolve;
  const controller = new AbortController(), ui = setup({ signal: controller.signal,
    httpHandler: (_, init) => init.method === 'POST' ? new Promise(r => { resolve = r; }) : undefined });
  await ui.view.san_sang; choose(ui.root);
  const oldForm = find(ui.root, 'form')[0], oldSample = button(ui.root, 'Dùng đoạn mẫu');
  const pending = send(ui.root); controller.abort(); await pending;
  assert.equal(ui.root.children.length, 0); await oldForm.events.submit({ preventDefault() {} }); await oldSample.events.click();
  assert.equal(ui.root.children.length, 0);
  assert.equal(posts(ui)[0].init.signal.aborted, true); assert.equal(ui.clock.jobs.size, 0);
  resolve(response({ ma_luot: 'luot_demo_1' }, 202)); await flush();
  assert.equal(posts(ui).length, 1); assert.equal(ui.root.children.length, 0);
});
test('Hủy trước và trong lúc xác minh quyền không dựng lại màn từ phản hồi muộn', async () => {
  const c1 = new AbortController(); c1.abort(); const closed = setup({ signal: c1.signal }); await closed.view.san_sang;
  assert.equal(closed.calls.length, 0); assert.equal(closed.root.children.length, 0);
  let resolve; const c2 = new AbortController();
  const pending = setup({ signal: c2.signal, handler: () => new Promise(r => { resolve = r; }) });
  c2.abort(); resolve(inventory()); await pending.view.san_sang; assert.equal(pending.root.children.length, 0);
});
test('Cờ quyền bị thu hồi sau khi mở: nút cũ không gửi, không còn lịch sử/kết quả', async () => {
  let back = 0;
  const ui = setup({ back: () => { back++; } }); await ui.view.san_sang;
  choose(ui.root);
  const oldBack = button(ui.root, 'Quay lại Hỏi AI'); ui.kb.khong_quyen = true; await send(ui.root);
  assert.match(shown(ui.root), /Chỉ Admin Core/); assert.equal(find(ui.root, 'table').length, 0);
  assert.equal(button(ui.root, 'Quay lại Hỏi AI'), undefined);
  await oldBack.events.click(); assert.equal(back, 0);
  assert.equal(ui.calls.length, 1); assert.equal(posts(ui).length, 0);
});

test('Đổi phiên lúc chờ kết quả: xóa nháp/lịch sử và không gửi GET hoặc POST tiếp', async () => {
  const ui = setup({ httpHandler: url => /\/luot_demo_\d+$/.test(url) ? response({ trang_thai: 'dang_chay' }) : undefined });
  await ui.view.san_sang; choose(ui.root); await send(ui.root);
  const oldForm = find(ui.root, 'form')[0], before = ui.httpCalls.length;
  ui.session({ csrf_token: 'CSRF_KHAC', nguoi_dung_id: 'nguoi_khac' }); await ui.clock.tick(1000);
  assert.match(shown(ui.root), /Phiên làm việc đã thay đổi/);
  assert.equal(find(ui.root, 'form').length, 0); assert.equal(find(ui.root, 'table').length, 0);
  await oldForm.events.submit({ preventDefault() {} });
  assert.equal(ui.httpCalls.length, before); assert.equal(ui.clock.jobs.size, 0);
});
test('Quay lại hủy màn, mở mới không giữ tài liệu hay lịch sử của phiên trước', async () => {
  let count = 0; const ui = setup({ back: () => { count++; } }); await ui.view.san_sang;
  const oldBack = button(ui.root, 'Quay lại Hỏi AI'); choose(ui.root); await send(ui.root); await oldBack.click(); await oldBack.events.click();
  assert.equal(count, 1); assert.equal(ui.root.children.length, 0);
  const next = setup(); await next.view.san_sang; assert.equal(historyCount(next.root), 0);
  assert.equal(field(next.root, 'Chức năng').value, ''); assert.equal(posts(next).length, 0);
});
test('Thu hồi quyền rồi bấm ngay Quay lại không dựng snapshot quản trị cũ', async () => {
  let back = 0;
  const ui = setup({ back: () => { back++; } }); await ui.view.san_sang;
  const oldBack = button(ui.root, 'Quay lại Hỏi AI'); ui.kb.khong_quyen = true; await oldBack.click();
  assert.equal(back, 0); assert.match(shown(ui.root), /Chỉ Admin Core/);
  assert.equal(find(ui.root, 'form').length, 0); assert.equal(find(ui.root, 'table').length, 0);
});
function integration({ deny = false, load = 'ok', kb = { ma: 'quan_ly_engine', thao_tac: [] }, handler, tao_sdk } = {}) {
  const root = dom(), calls = [], responses = []; let scripts = 0, key = 0;
  const clock = fakeClock(), http = mockHttp();
  const context = vm.createContext({ AbortController, console, structuredClone, addEventListener() {},
    setTimeout: clock.setTimeout, clearTimeout: clock.clearTimeout });
  context.fetch = () => assert.fail('Không gọi mạng/AI');
  vm.runInContext(quanTriSource, context);
  const append = root.ownerDocument.head.append.bind(root.ownerDocument.head);
  root.ownerDocument.head.append = script => {
    scripts++; append(script); assert.equal(script.src, '/core/ui/chay_thu_hoi_ai.js');
    if (load === 'pending') return;
    if (load === 'error') return script.onerror();
    vm.runInContext(source, context); script.onload();
  };
  const sdk = { api: { goi: async req => {
    calls.push(req);
    if (deny) throw { status: 403 };
    const response = handler ? await handler(req)
      : req.duong_dan.endsWith('/kiem-ke') ? inventory() : { danh_sach: [], con_tiep: false };
    responses.push(structuredClone(response)); return response;
  } }, phap_nhan: { danh_sach: async () => demoPage() } };
  const view = context.KttQuanTri.dung(root, { sdk: tao_sdk ? tao_sdk(sdk) : sdk, loai: 'engine', khai_bao_da_loc_quyen: kb,
    fetch: http.fetch, csrf_token: 'CSRF_DEMO', nguoi_dung_id: 'nguoi_demo',
    doc_phien: () => ({ csrf_token: 'CSRF_DEMO', nguoi_dung_id: 'nguoi_demo' }),
    tao_khoa: () => 'demo-ai-man-ui-' + String(++key).padStart(16, '0') });
  return { root, calls, responses, view, context, clock, ...http, scripts: () => scripts };
}
test('Đường vào thật: Quản lý engine → Hỏi AI → tải JS cố định → DEMO → quay lại', async () => {
  const ui = integration(); await ui.view.san_sang;
  assert.equal(button(ui.root, 'Chạy thử DEMO'), undefined);
  await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click(); await button(ui.root, 'Chạy thử DEMO').click();
  assert.equal(ui.scripts(), 1); assert.ok(field(ui.root, 'Đoạn tài liệu giả')); choose(ui.root); await send(ui.root);
  assert.match(shown(result(ui.root)), /1\.000\.000 VND/);
  assert.equal(posts(ui)[0].init.headers['X-CSRF-Token'], 'CSRF_DEMO');
  assert.match(posts(ui)[0].init.headers['Idempotency-Key'], /^demo-ai-man-ui-/);
  await button(ui.root, 'Quay lại Hỏi AI').click(); assert.equal(field(ui.root, 'Đoạn tài liệu giả'), undefined);
  assert.ok(button(ui.root, 'Quay lại danh sách')); await button(ui.root, 'Chạy thử DEMO').click();
  assert.equal(ui.scripts(), 1); assert.equal(historyCount(ui.root), 1);
  assert.equal(ui.httpCalls.filter(c => c.url === API + '/function').length, 2);
  assert.equal(field(ui.root, 'Chức năng').value, '');
  ui.view.dung(); assert.equal(ui.root.children.length, 0);
});

test('Chạy thử dùng SDK danh mục pháp nhân 1.2 hiện có và chuyển phạm vi vào header HTTP', async () => {
  const SDK = require('../src/kho_tri_thuc/sdk_core/trinh_duyet.js'), sent = [];
  const ui = integration({ handler: req => req.duong_dan.startsWith('/api/v1/phap-nhan') ? demoPage() : inventory(),
    tao_sdk: fake => {
      const sdk = SDK.tao({ tao_ma: () => PN, fetch: async (url, init) => {
        sent.push({ url, init });
        return response(await fake.api.goi({ duong_dan: url }));
      } });
      sdk.api.doi_ngu_canh({ nguoi_dung_id: PN, phap_nhan_id: null, module: null, man: 'quan_ly_engine' });
      sdk.api.gan_csrf('CSRF_DEMO'); return sdk;
    } });
  await ui.view.san_sang;
  await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click(); await button(ui.root, 'Chạy thử DEMO').click();
  assert.equal(sent.filter(c => c.url === '/api/v1/phap-nhan?phien_ban_du_lieu=1.2').length, 1);
  choose(ui.root); await send(ui.root);
  for (const call of ui.httpCalls) assert.equal(call.init.headers['X-Phap-Nhan-Id'], PN);
  assert.equal(posts(ui).length, 1); assert.match(shown(result(ui.root)), /1\.000\.000 VND/);
  ui.view.dung();
});
test('Engine khác, GET 403 hoặc khai báo không quyền đều không có đường DEMO', async () => {
  const ui = integration(); await ui.view.san_sang; await button(ui.root, 'Xem chi tiết Nhận dạng văn bản').click();
  assert.equal(button(ui.root, 'Chạy thử DEMO'), undefined);
  for (const options of [{ deny: true }, { kb: { ma: 'quan_ly_engine', khong_quyen: true } },
    { kb: { ma: 'quan_ly_module' } }]) {
    const denied = integration(options); await denied.view.san_sang;
    if (button(denied.root, 'Xem chi tiết Hỏi đáp AI')) await button(denied.root, 'Xem chi tiết Hỏi đáp AI').click();
    assert.equal(button(denied.root, 'Chạy thử DEMO'), undefined); assert.equal(denied.scripts(), 0);
  }
});
test('Rời Quản lý engine khi đang tải tệp DEMO không dựng màn muộn', async () => {
  const ui = integration({ load: 'pending' }); await ui.view.san_sang;
  await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click(); const pending = button(ui.root, 'Chạy thử DEMO').click();
  const script = ui.root.ownerDocument.head.children[0]; ui.view.dung();
  vm.runInContext(source, ui.context); script.onload(); await pending; await flush();
  assert.equal(ui.root.children.length, 0);
});
test('Tải tệp DEMO thất bại báo nghiệp vụ, vẫn ở chi tiết và có thể mở lại', async () => {
  const ui = integration({ load: 'error' }); await ui.view.san_sang;
  await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click(); await button(ui.root, 'Chạy thử DEMO').click();
  assert.match(shown(ui.root), /Chưa tải được màn Chạy thử DEMO/);
  assert.doesNotMatch(shown(ui.root), /PHAN_HOI_KHONG_HOP_LE|request_id|Mã lỗi/);
  assert.ok(button(ui.root, 'Quay lại danh sách')); assert.equal(find(ui.root, 'form').length, 0);
  ui.root.ownerDocument.head.append = script => { vm.runInContext(source, ui.context); script.onload(); };
  await button(ui.root, 'Chạy thử DEMO').click(); assert.ok(field(ui.root, 'Đoạn tài liệu giả'));
});
test('Tệp mới được phục vụ bằng cả hai URL trong đúng _TINH', () => {
  const app = fs.readFileSync(path.join(dir, 'ung_dung.py'), 'utf8');
  const section = app.slice(app.indexOf('_TINH = {'), app.indexOf('_LOI_NAP_MODULE ='));
  for (const url of ['/chay_thu_hoi_ai.js', '/core/ui/chay_thu_hoi_ai.js']) {
    assert.ok(section.includes(`'${url}': (_CORE / 'ui/chay_thu_hoi_ai.js', 'text/javascript; charset=utf-8')`));
  }
});

// AI-MAN: hai cổng quản trị, dữ liệu/SDK giả; không dò mạng hoặc gọi AI.
const localPath = '/api/v1/quan-tri/engine/e_hoi_ai/local';
const profilePath = '/api/v1/quan-tri/engine/e_hoi_ai/ho-so-chay?phien_ban_du_lieu=1.2';
const savePath = localPath + '/quy-tac';
const addressCanary = 'http://192.168.90.123:11434';
const uuidModel = '10000000-0000-4000-8000-000000000123';
const localData = () => ({ row_version: '9007199254740993', da_cau_hinh: true, ket_noi: true,
  kiem_luc: '2026-11-07T01:02:03Z', do_tre_ms: 12, dia_chi_che: '192.168.*.*',
  thong_diep: 'Đã kết nối máy AI cục bộ', models: [
    { ma: uuidModel, ten: 'Qwen thử nghiệm', bat: true, trang_thai: 'san_sang' },
    { ma: 'cu-demo', ten: 'Mô hình cũ', bat: false, trang_thai: 'khong_con' },
    { ma: 'moi-demo', ten: 'Mô hình mới', bat: false, trang_thai: 'moi' }],
  quy_tac: [{ chuc_nang: 'hoi_dap', ten: 'Hỏi đáp tài liệu', che_do: 'tu_chon', uu_tien: uuidModel, du_phong: null }] });
function localIntegration(options = {}) {
  let current = localData(); const writes = [];
  const ui = integration({ ...options, handler: async req => {
    const method = req.phuong_thuc || 'GET';
    if (req.duong_dan.endsWith('/kiem-ke')) return options.inventory ? options.inventory() : inventory();
    if (req.duong_dan === '/api/v1/quan-tri/module/ten') return { danh_sach: options.modules || [], con_tiep: false };
    if (options.handler && [localPath, localPath + '/phat-hien', savePath, profilePath].includes(req.duong_dan)) {
      const result = await options.handler(req, current); if (result !== undefined) return result;
    }
    if (req.duong_dan === localPath) return structuredClone(current);
    if (req.duong_dan === localPath + '/phat-hien') {
      assert.equal(method, 'POST'); assert.ok(req.khoa); assert.equal(req.du_lieu.row_version, current.row_version);
      current.row_version = String(BigInt(current.row_version) + 1n);
      return structuredClone(current);
    }
    // Nếu màn quay lại đọc hồ sơ đầy đủ, canary phải bắt được cả response.
    if (req.duong_dan === profilePath) return { row_version: current.row_version,
      cau_hinh: { cloud_bat: false, local_ai: { dia_chi: addressCanary } } };
    if (req.duong_dan === savePath) {
      assert.equal(method, 'PUT'); assert.ok(req.khoa); writes.push(structuredClone(req));
      assert.equal(req.du_lieu.row_version, current.row_version);
      assert.deepEqual(Object.keys(req.du_lieu).sort(), ['models', 'quy_tac_model', 'row_version']);
      const flags = new Map(req.du_lieu.models.map(m => {
        assert.deepEqual(Object.keys(m).sort(), ['bat', 'ma']); return [m.ma, m.bat];
      }));
      current = { ...current, models: current.models.map(m => ({ ...m, bat: flags.get(m.ma),
        trang_thai: flags.get(m.ma) && m.trang_thai === 'moi' ? 'san_sang' : m.trang_thai })),
        quy_tac: structuredClone(req.du_lieu.quy_tac_model), row_version: String(BigInt(current.row_version) + 1n) };
      return structuredClone(current);
    }
    return { danh_sach: [], con_tiep: false };
  } });
  return { ...ui, writes, current: () => current };
}
async function openLocal(ui) {
  await ui.view.san_sang;
  await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click();
  await button(ui.root, 'Cổng Local AI').click();
}
function assertNoTechnical(root) {
  assert.doesNotMatch(shown(root), /\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b|row_version|ma_bam_schema|hoi_dap|e_hoi_ai|192\.168\.90\.123|\b(?:Anh|bạn)\b/u);
  for (const n of all(root)) assert.doesNotMatch(JSON.stringify(n.attrs), new RegExp(uuidModel));
}

test('AI-MAN: Local và Cloud luôn có cạnh DEMO kể cả engine mới dự kiến/chưa kết nối', async () => {
  for (const pending of [false, true]) {
    const ui = localIntegration({ inventory: () => {
      const data = inventory();
      if (pending) {
        const ai = data.danh_sach.find(r => r.ma === 'e_hoi_ai');
        Object.assign(ai, { nguon: 'du_kien', nhan_du_lieu: 'cho', ly_do: ['Chưa cài engine'],
          phien_ban_dang_dung: null, phien_ban_cho: [], van_hanh: null, kt: null }); delete ai.chuc_nang;
      }
      return data;
    } });
    await ui.view.san_sang; await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click();
    for (const title of ['Cổng Local AI', 'Cổng Cloud AI', 'Chạy thử DEMO']) assert.ok(button(ui.root, title));
    assertNoTechnical(ui.root);
  }
});

test('AI-MAN: Cloud khóa hoàn toàn, bản 2 chỉ đọc, công tắc tắt và hạn mức ghi USD', async () => {
  const ui = localIntegration({ modules: [{ ten: 'Tài liệu' }, { ten: 'Công nợ' }] }); await ui.view.san_sang;
  await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click(); const before = ui.calls.length;
  await button(ui.root, 'Cổng Cloud AI').click();
  assert.match(shown(ui.root), /Bản 1 chưa dùng Cloud/); assert.match(shown(ui.root), /Trạng thái Mask/);
  assert.equal(field(ui.root, 'Nhà cung cấp Cloud').disabled, true);
  for (const name of ['Tài liệu', 'Công nợ']) {
    const toggle = field(ui.root, `Cloud cho ${name} — mặc định tắt`);
    assert.equal(toggle.disabled, true); assert.equal(toggle.checked, false);
  }
  assert.equal(field(ui.root, 'Hạn mức chi phí (USD)').disabled, true);
  assert.equal(field(ui.root, 'Hạn mức chi phí (USD)').value, '0');
  assert.equal(find(ui.root, 'fieldset')[0].disabled, true);
  assert.equal(ui.calls.length, before + 1);
  assert.equal(ui.calls.at(-1).duong_dan, '/api/v1/quan-tri/module/ten', 'Chỉ đọc tên module bằng API quản trị hiện có');
  assert.equal(ui.calls.some(r => /\/cloud(?:\/|$)/.test(r.duong_dan)), false); assertNoTechnical(ui.root);
});

test('AI-MAN: bảng model đủ ba nhãn, quy tắc ưu tiên/dự phòng, ngày Việt và không UUID trong DOM', async () => {
  const ui = localIntegration(); await openLocal(ui);
  for (const text of ['Sẵn sàng', 'Không còn', 'Mới — chờ bật', '07/11/2026', '12 ms',
    '192.168.*.*', 'Hỏi đáp tài liệu', 'Tự chọn', 'Cố định', 'Model ưu tiên', 'Model dự phòng']) assert.ok(shown(ui.root).includes(text), text);
  for (const title of ['Thử kết nối', 'Dò lại', 'Lưu']) assert.ok(button(ui.root, title));
  assert.equal(field(ui.root, 'Sử dụng Mô hình cũ').disabled, true);
  assert.equal(field(ui.root, 'Sử dụng Mô hình mới').checked, false); assertNoTechnical(ui.root);
});

test('AI-MAN: toàn luồng Lưu chỉ dùng route riêng, giữ CAS và không có response chứa địa chỉ đầy đủ', async () => {
  const ui = localIntegration(); await openLocal(ui);
  await button(ui.root, 'Dò lại').click();
  const check = field(ui.root, 'Sử dụng Mô hình mới'); check.checked = true; check.events.change();
  assert.equal(ui.view.co_nhap(), true);
  change(field(ui.root, 'Chế độ — Hỏi đáp tài liệu'), 'co_dinh');
  change(field(ui.root, 'Model ưu tiên — Hỏi đáp tài liệu'), '2');
  change(field(ui.root, 'Model dự phòng — Hỏi đáp tài liệu'), '0');
  await button(ui.root, 'Lưu').click();
  assert.equal(ui.writes.length, 1);
  const body = ui.writes[0].du_lieu;
  assert.equal(body.row_version, '9007199254740994');
  assert.equal(ui.writes[0].duong_dan, savePath);
  assert.equal(body.models[2].bat, true);
  assert.equal(ui.current().models[2].trang_thai, 'san_sang');
  assert.equal(body.quy_tac_model[0].uu_tien, 'moi-demo');
  assert.equal(body.quy_tac_model[0].du_phong, uuidModel);
  assert.match(shown(ui.root), /Đã lưu cấu hình/); assert.equal(ui.view.co_nhap(), false); assertNoTechnical(ui.root);
  await button(ui.root, 'Tải lại cấu hình').click();
  assert.equal(field(ui.root, 'Sử dụng Mô hình mới').checked, true);
  assert.equal(ui.current().row_version, '9007199254740995');
  assert.equal(ui.calls.some(r => r.duong_dan.includes('/ho-so-chay')), false);
  for (const payload of [...ui.calls.map(r => r.du_lieu), ...ui.responses]) {
    assert.doesNotMatch(JSON.stringify(payload) || '', /http:\/\/192\.168\.90\.123:11434|192\.168\.90\.123/);
  }
});

test('AI-MAN: tắt model đang chọn chặn lưu quy tắc cho tới khi bỏ lựa chọn không còn dùng', async () => {
  const ui = localIntegration(); await openLocal(ui);
  const check = field(ui.root, 'Sử dụng Qwen thử nghiệm'); check.checked = false; check.events.change();
  await button(ui.root, 'Lưu').click(); assert.equal(ui.writes.length, 0);
  assert.match(shown(ui.root), /Chọn model đang bật và sẵn sàng/);
  change(field(ui.root, 'Model ưu tiên — Hỏi đáp tài liệu'), '');
  await button(ui.root, 'Lưu').click(); assert.equal(ui.writes.length, 1);
  assert.equal(ui.current().models[0].bat, false);
});

test('AI-MAN: Thử kết nối và Dò lại dùng dịch vụ qua Core, mỗi lần lấy CAS mới', async () => {
  const ui = localIntegration(); await openLocal(ui);
  await button(ui.root, 'Thử kết nối').click(); await button(ui.root, 'Dò lại').click();
  const requests = ui.calls.filter(r => r.duong_dan === localPath + '/phat-hien');
  assert.deepEqual(requests.map(r => r.du_lieu.row_version), ['9007199254740993', '9007199254740994']);
  assert.equal(ui.calls.some(r => /cloud|11434/.test(r.duong_dan)), false); assertNoTechnical(ui.root);
});

test('AI-MAN: dịch vụ None hiện câu Việt và vẫn có hai cổng, Cloud khóa', async () => {
  const ui = localIntegration({ handler: req => req.duong_dan === localPath + '/phat-hien'
    ? { ...localData(), ket_noi: false, thong_diep: 'Chưa kết nối máy AI cục bộ' } : undefined });
  await openLocal(ui); await button(ui.root, 'Dò lại').click();
  assert.match(shown(ui.root), /Chưa kết nối máy AI cục bộ/);
  assert.ok(button(ui.root, 'Cổng Cloud AI')); assertNoTechnical(ui.root);
});

test('AI-MAN: chưa có hồ sơ cấu hình vẫn mở màn, thử kết nối được và khóa Lưu khi chưa có CAS', async () => {
  const empty = { ...localData(), row_version: null, da_cau_hinh: false, ket_noi: false,
    kiem_luc: null, do_tre_ms: null, dia_chi_che: null, models: [], quy_tac: [] };
  const ui = localIntegration({ handler: req => req.duong_dan.startsWith(localPath) ? empty : undefined });
  await openLocal(ui);
  assert.match(shown(ui.root), /Chưa cấu hình máy AI cục bộ/); assert.equal(button(ui.root, 'Lưu').disabled, true);
  await button(ui.root, 'Thử kết nối').click();
  assert.equal(ui.calls.some(r => r.duong_dan.endsWith('/phat-hien')), false, 'Không tự tạo CAS khi chưa có cấu hình');
  assert.match(shown(ui.root), /Chưa kết nối máy AI cục bộ/); assertNoTechnical(ui.root);
});

test('AI-MAN: SDK trình duyệt thật gửi CSRF và CAS qua Core, không cần phạm vi pháp nhân', async () => {
  const SDK = require('../src/kho_tri_thuc/sdk_core/trinh_duyet.js'), sent = [];
  const ui = localIntegration({ tao_sdk: fake => {
    const sdk = SDK.tao({ tao_ma: () => uuidModel, fetch: async (url, init) => {
      sent.push({ url, init });
      const data = await fake.api.goi({ duong_dan: url, phuong_thuc: init.method,
        du_lieu: init.body ? JSON.parse(init.body) : undefined, khoa: init.headers['Idempotency-Key'] });
      return { status: 200, ok: true, bodyUsed: true,
        headers: { get: key => key === 'Content-Type' ? 'application/json' : null }, json: async () => data };
    } });
    sdk.api.doi_ngu_canh({ nguoi_dung_id: uuidModel, phap_nhan_id: null, module: null, man: 'quan_ly_engine' });
    sdk.api.gan_csrf('CSRF-DEMO-AI-MAN'); return sdk;
  } });
  await openLocal(ui); await button(ui.root, 'Dò lại').click(); await button(ui.root, 'Lưu').click();
  const writes = sent.filter(r => ['POST', 'PUT'].includes(r.init.method)); assert.equal(writes.length, 2);
  for (const { init } of writes) {
    assert.equal(init.headers['X-CSRF-Token'], 'CSRF-DEMO-AI-MAN'); assert.ok(init.headers['Idempotency-Key']);
    assert.equal(init.headers['X-Phap-Nhan-Id'], undefined); assert.equal(init.headers['X-Module-Ma'], undefined);
    assert.equal(typeof JSON.parse(init.body).row_version, 'string');
  }
  assert.match(shown(ui.root), /Đã lưu cấu hình/); assertNoTechnical(ui.root);
});

test('AI-MAN: 409 giữ nháp và khóa ghi/dò tới khi tải lại, lỗi có Chi tiết hỗ trợ thu gọn', async () => {
  const ui = localIntegration({ handler: req => {
    if (req.duong_dan === savePath && req.phuong_thuc === 'PUT') throw { status: 409, ma: 'XUNG_DOT_PHIEN_BAN', message: 'SECRET_DEMO' };
  } }); await openLocal(ui);
  change(field(ui.root, 'Chế độ — Hỏi đáp tài liệu'), 'co_dinh');
  await button(ui.root, 'Lưu').click();
  assert.match(shown(ui.root), /Dữ liệu đã thay đổi/);
  assert.equal(field(ui.root, 'Chế độ — Hỏi đáp tài liệu').value, 'co_dinh');
  for (const title of ['Lưu', 'Dò lại', 'Thử kết nối']) assert.equal(button(ui.root, title).disabled, true);
  const details = find(ui.root, 'details')[0]; assert.ok(details); assert.ok(!details.open);
  assert.equal(find(details, 'summary')[0].textContent, 'Chi tiết hỗ trợ');
  assert.doesNotMatch(shown(ui.root), /SECRET_DEMO/);
  await button(ui.root, 'Tải lại cấu hình').click(); assert.equal(button(ui.root, 'Lưu').disabled, false);
});

test('AI-MAN: Lưu nhận CAS mới ngay từ DTO đã che, lần lưu tiếp theo không đọc hồ sơ đầy đủ', async () => {
  const ui = localIntegration(); await openLocal(ui);
  change(field(ui.root, 'Chế độ — Hỏi đáp tài liệu'), 'co_dinh');
  await button(ui.root, 'Lưu').click();
  change(field(ui.root, 'Chế độ — Hỏi đáp tài liệu'), 'tu_chon');
  await button(ui.root, 'Lưu').click();
  assert.deepEqual(ui.writes.map(r => r.du_lieu.row_version), ['9007199254740993', '9007199254740994']);
  assert.equal(ui.calls.filter(r => r.duong_dan === localPath).length, 1);
  assert.equal(ui.calls.some(r => r.duong_dan.includes('/ho-so-chay')), false);
  assert.match(shown(ui.root), /Đã lưu cấu hình/); assertNoTechnical(ui.root);
});

test('AI-MAN: Lưu mất quyền xóa nháp và khóa nút cũ, response muộn sau rời màn không dựng lại', async () => {
  const denied = localIntegration({ handler: req => { if (req.duong_dan === savePath) throw { status: 403 }; } });
  await openLocal(denied); const oldSave = button(denied.root, 'Lưu');
  await oldSave.click(); assert.doesNotMatch(shown(denied.root), /Qwen thử nghiệm/);
  const before = denied.calls.length; await oldSave.click(); assert.equal(denied.calls.length, before);
  let resolve;
  const delayed = localIntegration({ handler: req => req.duong_dan === savePath ? new Promise(r => { resolve = r; }) : undefined });
  await openLocal(delayed); const pending = button(delayed.root, 'Lưu').click(); await flush();
  delayed.view.dung(); resolve(localData()); await pending;
  assert.equal(delayed.root.children.length, 0);
});

test('AI-MAN: lỗi đọc hoặc dò không lộ message thô, địa chỉ đầy đủ hoặc mã model trong tên', async () => {
  const data = localData(); data.models[0].ten = uuidModel; data.quy_tac[0].ten = uuidModel;
  data.dia_chi_che = 'http://192.168.90.123:11434';
  const ui = localIntegration({ handler: req => {
    if (req.duong_dan === localPath) return data;
    if (req.duong_dan.endsWith('/phat-hien')) throw { status: 503, ma: 'AI_LOCAL_CHUA_KET_NOI', message: 'SECRET_DEMO http://192.168.90.123' };
  } }); await openLocal(ui); assertNoTechnical(ui.root);
  await button(ui.root, 'Dò lại').click(); assert.match(shown(ui.root), /Chưa kết nối máy AI cục bộ/);
  assert.doesNotMatch(shown(ui.root), /SECRET_DEMO/); assertNoTechnical(ui.root);
});

test('AI-MAN: không Admin không có hai cổng; thu hồi quyền xóa model và bỏ nút lưu cũ', async () => {
  for (const options of [{ deny: true }, { kb: { ma: 'quan_ly_engine', khong_quyen: true } }, { kb: { ma: 'quan_ly_module' } }]) {
    const ui = localIntegration(options); await ui.view.san_sang;
    if (button(ui.root, 'Xem chi tiết Hỏi đáp AI')) await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click();
    assert.equal(button(ui.root, 'Cổng Local AI'), undefined); assert.equal(button(ui.root, 'Cổng Cloud AI'), undefined);
  }
  let deny = false;
  const ui = localIntegration({ handler: req => { if (deny && req.duong_dan === localPath) throw { status: 403 }; } });
  await openLocal(ui); const oldSave = button(ui.root, 'Lưu'); deny = true;
  await button(ui.root, 'Tải lại cấu hình').click();
  assert.doesNotMatch(shown(ui.root), /Qwen thử nghiệm/);
  const before = ui.calls.length; await oldSave.click(); assert.equal(ui.calls.length, before);
});

test('AI-MAN: rời màn hoặc đổi tab bỏ nháp/nút cũ; response chậm sau hủy không dựng màn lại', async () => {
  const ui = localIntegration(); await openLocal(ui);
  const oldSave = button(ui.root, 'Lưu'); await button(ui.root, 'Cổng Cloud AI').click();
  const before = ui.calls.length; await oldSave.click(); assert.equal(ui.calls.length, before);
  let resolve;
  const delayed = localIntegration({ handler: req => req.duong_dan === localPath ? new Promise(r => { resolve = r; }) : undefined });
  await delayed.view.san_sang; await button(delayed.root, 'Xem chi tiết Hỏi đáp AI').click();
  const pending = button(delayed.root, 'Cổng Local AI').click(); await flush();
  delayed.view.dung(); resolve(localData()); await pending;
  assert.equal(delayed.root.children.length, 0);
});
