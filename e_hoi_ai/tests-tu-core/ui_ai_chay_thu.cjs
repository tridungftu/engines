'use strict';
// AI-LAT10b: HTTP, DOM và đồng hồ giả; không server, PostgreSQL hoặc máy AI.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const dir = path.join(__dirname, '../src/kho_tri_thuc/core');
const source = fs.readFileSync(path.join(dir, 'ui/chay_thu_hoi_ai.js'), 'utf8');
const adminSource = fs.readFileSync(path.join(dir, 'ui/quan_tri.js'), 'utf8');
const API = '/api/v1/quan-tri/hoi-ai/chay-thu';
const PN = '10000000-0000-4000-8000-000000000001';
const PN2 = '10000000-0000-4000-8000-000000000002';
const demoPage = (rows = [{ id: PN, ten: 'Công ty DEMO Ánh Dương', la_demo: true }]) =>
  ({ danh_sach: rows, con_tiep: false, con_tro_tiep: null });
const functions = [{ ma_module: 'module_demo', ten_module: 'Hợp đồng DEMO',
  ma_function: 'ham_demo', mo_ta: 'Tra cứu điều khoản thanh toán' }];
const done = (reason = 'uu_tien') => ({ trang_thai: 'xong', tra_loi: 'Số tiền DEMO: 1.000.000 VND.',
  model: 'Qwen DEMO', ly_do_chon: reason, bat_dau: '2026-11-08T01:02:03Z', ket_thuc: '2026-11-08T01:02:05Z' });
class Element {
  constructor(tag, doc) {
    this.tagName = tag; this.ownerDocument = doc; this.children = []; this.events = {};
    this.attrs = {}; this._text = ''; this.value = ''; this.disabled = false; this.hidden = false;
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(n => n.textContent).join(' '); }
  set innerHTML(_) { assert.fail('Nội dung chỉ được chèn bằng textContent'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this._text = ''; this.children = nodes; }
  setAttribute(key, value) { this.attrs[key] = String(value); }
  addEventListener(type, callback) { this.events[type] = callback; }
  click() { if (!this.disabled && !this.hidden) return this.events.click?.({ preventDefault() {} }); }
}
const all = root => [root, ...root.children.flatMap(all)];
const find = (root, tag) => all(root).filter(n => n.tagName === tag);
const button = (root, text) => all(root).find(n => ['button', 'a'].includes(n.tagName) && n.textContent === text);
const field = (root, text) => all(root).find(n => n.attrs['aria-label'] === text);
const shown = root => root.hidden || root.tagName === 'style' ? '' : root._text + root.children.map(shown).join(' ');
const flush = async () => { for (let i = 0; i < 6; i++) await new Promise(setImmediate); };
const change = (node, value) => { node.value = value; return (node.events.input || node.events.change)?.(); };
const send = ui => find(ui.root, 'form')[0].events.submit({ preventDefault() {} });
const output = ui => field(ui.root, 'Kết quả chạy thử');
const select = ui => change(field(ui.root, 'Chức năng'), '0');
const response = (body, status = 200, extra = {}) => ({ ok: status >= 200 && status < 300, status,
  headers: { get: key => key === 'Content-Type' ? 'application/json; charset=utf-8' : null },
  json: async () => body, ...extra });
function dom() {
  const doc = { createElement: tag => new Element(tag, doc) };
  doc.head = doc.createElement('head'); return doc.createElement('main');
}
function fakeClock() {
  let time = 0, id = 0; const jobs = new Map();
  return { jobs, get now() { return time; },
    setTimeout(callback, delay) { jobs.set(++id, { callback, at: time + delay }); return id; },
    clearTimeout(key) { jobs.delete(key); },
    async tick(ms) {
      const end = time + ms; let count = 0;
      while (true) {
        const next = [...jobs].filter(([, v]) => v.at <= end).sort((a, b) => a[1].at - b[1].at)[0];
        if (!next) break;
        assert.ok(++count < 1000, 'Đồng hồ không được lặp vô hạn');
        jobs.delete(next[0]); time = next[1].at; next[1].callback(); await flush();
      }
      time = end; await flush();
    }
  };
}
function setup(options = {}) {
  const root = dom(), calls = [], authCalls = [], companyCalls = [], clock = fakeClock(); let keys = 0;
  const kb = options.kb === undefined ? { ma: 'quan_ly_engine' } : options.kb;
  let session = { csrf_token: 'CSRF_DEMO', nguoi_dung_id: 'nguoi_demo' };
  const context = vm.createContext({ AbortController, console, structuredClone, addEventListener() {},
    setTimeout: clock.setTimeout, clearTimeout: clock.clearTimeout });
  vm.runInContext(source, context);
  const sdk = { api: { goi: async req => {
    authCalls.push(req);
    if (options.auth) return options.auth(req);
    return { phien_ban_quan_tri: 2, danh_sach: [] };
  } }, phap_nhan: { danh_sach: async request => {
    companyCalls.push(request); return options.companies ? options.companies(request) : demoPage();
  } } };
  const fetch = async (url, init) => {
    calls.push({ url, init, at: clock.now });
    assert.ok(url.startsWith(API), 'Chỉ gọi API chạy thử qua Core');
    assert.equal(init.mode, 'same-origin'); assert.equal(init.credentials, 'same-origin');
    assert.equal(init.redirect, 'error'); assert.equal(init.cache, 'no-store');
    if (options.handler) {
      const res = await options.handler(url, init, calls);
      if (res !== undefined) return res;
    }
    if (url === API + '/function') return response({ function: functions });
    if (url === API + '?gioi_han=20') return response({ luot: [] });
    if (init.method === 'POST') return response({ ma_luot: 'luot_demo' }, 202);
    return response(done());
  };
  const view = context.KttChayThuHoiAi.dung(root, {
    sdk_he_thong: options.noSdk ? undefined : sdk, khai_bao_da_loc_quyen: kb,
    csrf_token: options.noCsrf ? '' : 'CSRF_DEMO', nguoi_dung_id: 'nguoi_demo',
    ...(options.session ? { doc_phien: () => session } : {}),
    signal: options.signal, khi_quay_lai: options.back,
    tao_khoa: () => 'khoa_demo_' + ++keys, fetch
  });
  return { root, calls, authCalls, companyCalls, view, kb, clock, context, sdk, fetch, session(value) { session = value; } };
}
const posts = ui => ui.calls.filter(c => c.init.method === 'POST');
const polls = ui => ui.calls.filter(c => c.url === API + '/luot_demo');

for (const rows of [[], [
  { id: PN, ten: 'DEMO thứ nhất', la_demo: true }, { id: PN2, ten: 'DEMO thứ hai', la_demo: true }
]]) test('Chưa chọn pháp nhân: chặn HTTP trước tải chức năng, lịch sử và Gửi (' + rows.length + ' DEMO)', async () => {
  const ui = setup({ companies: () => demoPage(rows) }); await ui.view.san_sang;
  assert.equal(ui.calls.length, 0);
  assert.match(shown(ui.root), /Chọn pháp nhân DEMO để chạy thử/);
  assert.equal(button(ui.root, 'Gửi').disabled, true);
  await send(ui); await button(ui.root, 'Tải lại lịch sử').click();
  assert.equal(ui.calls.length, 0);
  if (rows.length) {
    await change(field(ui.root, 'Pháp nhân DEMO'), PN); // Không nhận ID tự chèn làm giá trị lựa chọn.
    await send(ui); assert.equal(ui.calls.length, 0);
  } else assert.match(shown(ui.root), /Chưa có pháp nhân DEMO được cấp quyền/);
  ui.view.dung();
});

test('Pháp nhân lấy đủ trang qua SDK chung, chỉ la_demo=true; chọn đúng header cho mọi GET/POST', async () => {
  const pages = [
    { danh_sach: [{ id: PN, ten: 'Công ty dữ liệu làm việc', la_demo: false }], con_tiep: true, con_tro_tiep: 'trang-2' },
    demoPage([{ id: PN2, ten: 'Công ty DEMO hợp lệ', la_demo: true },
      { id: '10000000-0000-4000-8000-000000000003', ten: 'Chưa rõ loại dữ liệu', la_demo: 'true' }])
  ];
  const ui = setup({ companies: request => pages[request.con_tro ? 1 : 0] }); await ui.view.san_sang;
  assert.equal(ui.companyCalls.length, 2); assert.equal(ui.companyCalls[1].con_tro, 'trang-2');
  const picker = field(ui.root, 'Pháp nhân DEMO');
  assert.equal(picker.children.length, 2); assert.match(picker.textContent, /Công ty DEMO hợp lệ/);
  assert.doesNotMatch(picker.textContent, /dữ liệu làm việc|Chưa rõ|10000000/);
  select(ui); await send(ui); await flush();
  assert.ok(polls(ui).length); assert.equal(posts(ui).length, 1);
  for (const { init } of ui.calls) {
    assert.equal(init.headers['X-Phap-Nhan-Id'], PN2);
    assert.equal(init.headers['X-CSRF-Token'], 'CSRF_DEMO');
  }
  assert.equal(JSON.parse(posts(ui)[0].init.body).phap_nhan_id, undefined);
  ui.view.dung();
});

for (const page of [demoPage([{ id: 'khong-hop-le', la_demo: true }]),
  { danh_sach: [{ id: PN, la_demo: true }], con_tiep: true, con_tro_tiep: 'lap-lai' }]) {
  test('Danh mục pháp nhân hỏng/trỏ lặp: không dùng danh sách dở dang để gửi HTTP', async () => {
    const ui = setup({ companies: () => page }); await ui.view.san_sang;
    assert.equal(ui.calls.length, 0); assert.equal(find(ui.root, 'form').length, 0);
    assert.ok(ui.companyCalls.length <= 2); ui.view.dung();
  });
}

test('Đổi pháp nhân bỏ tài liệu, kết quả và lịch sử cũ; nút/form cũ không gửi tiếp', async () => {
  const ui = setup({ companies: () => demoPage([
    { id: PN, ten: 'DEMO thứ nhất', la_demo: true }, { id: PN2, ten: 'DEMO thứ hai', la_demo: true }
  ]) }); await ui.view.san_sang;
  await change(field(ui.root, 'Pháp nhân DEMO'), '0');
  select(ui); await send(ui); await flush();
  const oldForm = find(ui.root, 'form')[0], oldReview = button(ui.root, 'Xem lại');
  change(field(ui.root, 'Đoạn tài liệu giả'), 'Bản nháp của pháp nhân thứ nhất');
  await change(field(ui.root, 'Pháp nhân DEMO'), '1');
  assert.doesNotMatch(shown(ui.root), /Số tiền DEMO|Bản nháp của pháp nhân thứ nhất/);
  assert.equal(find(ui.root, 'tbody')[0].children.length, 0);
  assert.equal(field(ui.root, 'Chức năng').value, '');
  const count = ui.calls.length;
  await oldForm.events.submit({ preventDefault() {} }); await oldReview.click(); await flush();
  assert.equal(ui.calls.length, count);
  select(ui); await send(ui); await flush();
  assert.equal(posts(ui).length, 2); assert.equal(posts(ui)[1].init.headers['X-Phap-Nhan-Id'], PN2);
  ui.view.dung();
});

for (const where of ['function', 'POST', 'poll', 'history']) test('401 thiếu phiên core ở ' + where + ': hướng dẫn chọn DEMO/đăng nhập lại, chặn nội dung cũ', async () => {
  const ui = setup({ handler: (url, init) => {
    const hit = where === 'function' ? url.endsWith('/function') : where === 'POST' ? init.method === 'POST'
      : where === 'poll' ? url.endsWith('/luot_demo') : url.includes('?gioi_han=');
    return hit ? response({ ma: 'AI_THU_PHIEN', thong_diep: 'SECRET_DEMO không đưa vào màn', request_id: 'ho-tro-demo' }, 401) : undefined;
  } }); await ui.view.san_sang;
  if (find(ui.root, 'form').length) { select(ui); await send(ui); await flush(); }
  assert.match(shown(ui.root), /Chọn pháp nhân DEMO để chạy thử/);
  assert.match(shown(ui.root), /đăng nhập lại/);
  assert.doesNotMatch(shown(ui.root), /Chưa tải được chức năng|SECRET_DEMO/);
  assert.equal(find(ui.root, 'form').length, 0);
  assert.equal(button(ui.root, 'Thử lại'), undefined);
  assert.equal(find(ui.root, 'details')[0].open, undefined);
  assert.ok(button(ui.root, 'Quay lại Hỏi AI')); ui.view.dung();
});

test('Hợp đồng route Core thật: danh_sach, ten_function, ket_qua lồng và ngày Việt', async () => {
  const row = { ma_luot: 'luot_demo', ma_module: functions[0].ma_module, ma_function: functions[0].ma_function,
    trang_thai: 'xong', tao_luc: '08/11/2026 08:02:03', bat_dau: '08/11/2026 08:02:03', ket_thuc: '08/11/2026 08:02:05',
    ket_qua: { tra_loi: 'Kết quả từ Core: 1.000.000 VND.', model: 'Model DEMO', ly_do_chon: 'uu_tien', loi: null } };
  const ui = setup({ handler: url => url.endsWith('/function') ? response({ danh_sach: [{
    ma_module: functions[0].ma_module, ma_function: functions[0].ma_function, ten_module: functions[0].ten_module,
    ten_function: 'Tra cứu thanh toán từ gói đã cài', ma_prompt: 'prompt_demo', phien_ban_prompt: '1'
  }] }) : url.includes('?gioi_han=') ? response({ danh_sach: [row] }) : url.endsWith('/luot_demo') ? response(row) : undefined });
  await ui.view.san_sang;
  assert.match(shown(ui.root), /Tra cứu thanh toán từ gói đã cài/);
  select(ui); await send(ui); await flush();
  assert.match(shown(output(ui)), /Kết quả từ Core: 1\.000\.000 VND/);
  assert.match(shown(output(ui)), /08\/11\/2026 08:02:05/);
  assert.match(find(ui.root, 'tbody')[0].textContent, /Model DEMO.*Model ưu tiên/);
  assert.doesNotMatch(shown(ui.root), /prompt_demo|luot_demo|phien_ban_prompt/);
  ui.view.dung();
});

test('Tải function qua Core: tên module + mô tả, chỉ Local, không dữ liệu giả lập hay mã kỹ thuật', async () => {
  const ui = setup(); await ui.view.san_sang;
  assert.equal(ui.authCalls.length, 1);
  assert.equal(ui.authCalls[0].duong_dan, '/api/v1/quan-tri/engine/kiem-ke');
  assert.deepEqual(ui.calls.map(c => c.url), [API + '/function', API + '?gioi_han=20']);
  assert.match(shown(ui.root), /Chỉ dùng dữ liệu DEMO/);
  assert.match(shown(ui.root), /Hợp đồng DEMO — Tra cứu điều khoản thanh toán/);
  assert.doesNotMatch(shown(ui.root), /module_demo|ham_demo|Cloud|chưa nối engine|\bAnh\b|bạn/);
  assert.equal(find(ui.root, 'select').length, 2);
  assert.equal(find(ui.root, 'tbody')[0].children.length, 0);
  assert.equal(field(ui.root, 'Câu hỏi').maxLength, 2000);
  assert.equal(field(ui.root, 'Đoạn tài liệu giả').maxLength, 20000);
  ui.view.dung(); assert.equal(ui.clock.jobs.size, 0);
});
for (const kb of [null, { ma: 'quan_ly_module' }, { ma: 'quan_ly_engine', khong_quyen: true }]) {
  test('Không Admin: chặn trước mọi API ' + JSON.stringify(kb), async () => {
    const ui = setup({ kb }); await ui.view.san_sang;
    assert.equal(ui.calls.length + ui.authCalls.length, 0); assert.equal(find(ui.root, 'form').length, 0);
  });
}
for (const option of [{ noSdk: true }, { noCsrf: true }, { auth: () => ({ danh_sach: [] }) }]) {
  test('Thiếu SDK/CSRF hoặc bằng chứng quyền không hợp lệ: khóa form ' + Object.keys(option), async () => {
    const ui = setup(option); await ui.view.san_sang;
    assert.equal(find(ui.root, 'form').length, 0); assert.equal(ui.calls.length, 0);
  });
}
for (const status of [401, 403]) {
  test('Core từ chối quyền hoặc phạm vi DEMO ' + status + ': không form, không Thử lại', async () => {
    const ui = setup({ handler: () => response({ ma: 'CANARY', thong_diep: 'SECRET_DEMO' }, status) });
    await ui.view.san_sang;
    assert.equal(find(ui.root, 'form').length, 0); assert.equal(button(ui.root, 'Thử lại'), undefined);
    assert.doesNotMatch(shown(ui.root), /CANARY|SECRET_DEMO/); assert.equal(ui.clock.jobs.size, 0);
  });
}
test('Không có function hợp lệ: khóa Gửi, không tự dựng chức năng mặc định', async () => {
  const ui = setup({ handler: url => url.endsWith('/function') ? response({ function: [] }) : undefined });
  await ui.view.san_sang; assert.equal(button(ui.root, 'Gửi').disabled, true);
  assert.match(shown(ui.root), /Chưa có chức năng có hướng dẫn hợp lệ/);
  await send(ui); assert.equal(posts(ui).length, 0);
});
test('Đếm ký tự khi nhập và Dùng đoạn mẫu, giới hạn hiện đủ 20.000/2.000', async () => {
  const ui = setup(); await ui.view.san_sang;
  change(field(ui.root, 'Đoạn tài liệu giả'), 'DEMO');
  change(field(ui.root, 'Câu hỏi'), 'Hỏi?');
  assert.match(shown(ui.root), /4 \/ 20\.000 ký tự/); assert.match(shown(ui.root), /4 \/ 2\.000 ký tự/);
  await button(ui.root, 'Dùng đoạn mẫu').click();
  assert.match(field(ui.root, 'Đoạn tài liệu giả').value, /Công ty DEMO Ánh Dương/);
});
test('Chưa chọn function không gửi; phản hồi dữ liệu thừa không đi vào POST', async () => {
  const ui = setup(); await ui.view.san_sang; await send(ui);
  assert.equal(posts(ui).length, 0); assert.match(shown(output(ui)), /Cần chọn chức năng/);
  select(ui); await send(ui); await flush();
  const post = posts(ui)[0], body = JSON.parse(post.init.body);
  assert.deepEqual(Object.keys(body).sort(), ['cau_hoi', 'ma_function', 'ma_module', 'tai_lieu']);
  assert.equal(body.ma_module, 'module_demo'); assert.equal(body.ma_function, 'ham_demo');
  assert.equal(post.init.headers['X-CSRF-Token'], 'CSRF_DEMO');
  assert.equal(post.init.headers['Idempotency-Key'], 'khoa_demo_1');
  assert.equal(ui.clock.jobs.size, 0);
});
for (const [name, value] of [['Đoạn tài liệu giả', ''], ['Câu hỏi', '  '],
  ['Đoạn tài liệu giả', 'x'.repeat(20001)], ['Câu hỏi', 'x'.repeat(2001)]]) {
  test('Đầu vào sai không gửi: ' + name + ' dài ' + value.length, async () => {
    const ui = setup(); await ui.view.san_sang; select(ui); change(field(ui.root, name), value);
    await send(ui); assert.equal(posts(ui).length, 0);
  });
}
test('Chấp nhận đúng biên 20.000 và 2.000 ký tự, không cắt nội dung', async () => {
  const ui = setup(); await ui.view.san_sang; select(ui);
  change(field(ui.root, 'Đoạn tài liệu giả'), 'x'.repeat(20000)); change(field(ui.root, 'Câu hỏi'), 'y'.repeat(2000));
  await send(ui); await flush(); const body = JSON.parse(posts(ui)[0].init.body);
  assert.equal(body.tai_lieu.length, 20000); assert.equal(body.cau_hoi.length, 2000);
});
test('Gửi hai lần chỉ POST một lần, khóa Gửi và hiện Đang chờ máy AI', async () => {
  let resolve;
  const ui = setup({ handler: (_, init) => init.method === 'POST' ? new Promise(r => { resolve = r; }) : undefined });
  await ui.view.san_sang; select(ui);
  const pending = send(ui); await send(ui);
  assert.equal(posts(ui).length, 1); assert.equal(button(ui.root, 'Gửi').disabled, true);
  assert.match(shown(output(ui)), /Đang chờ máy AI…/);
  resolve(response({ ma_luot: 'luot_demo' }, 202)); await pending; await flush();
  assert.equal(button(ui.root, 'Gửi').disabled, false);
});
test('Hỏi lại theo nhịp lùi, 120 giây dừng; Xem lại chỉ GET cùng ma_luot', async () => {
  let finished = false;
  const ui = setup({ handler: url => url === API + '/luot_demo'
    ? response(finished ? done() : { trang_thai: 'dang_cho', tra_loi: 'KHONG_HIEN_KHI_CHO' }) : undefined });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  await ui.clock.tick(15000);
  assert.deepEqual(polls(ui).map(c => c.at), [0, 1000, 3000, 7000, 15000]);
  assert.doesNotMatch(shown(ui.root), /KHONG_HIEN_KHI_CHO/);
  await ui.clock.tick(105000); const count = polls(ui).length;
  assert.match(shown(output(ui)), /hai phút/); assert.equal(button(ui.root, 'Xem lại').hidden, false);
  assert.equal(ui.clock.jobs.size, 0); await ui.clock.tick(60000); assert.equal(polls(ui).length, count);
  finished = true; await button(ui.root, 'Xem lại').click(); await flush();
  assert.equal(posts(ui).length, 1); assert.match(shown(output(ui)), /1\.000\.000 VND/);
  assert.equal(polls(ui).length, count + 1); assert.equal(ui.clock.jobs.size, 0);
});
for (const [reason, label] of [['uu_tien', 'Model ưu tiên'], ['du_phong:1', 'Model dự phòng 1'], ['co_dinh', 'Model cố định']]) {
  test('Kết quả: câu trả lời, model, lý do và thời gian Việt ' + reason, async () => {
    const ui = setup({ handler: url => url === API + '/luot_demo' ? response(done(reason)) : undefined });
    await ui.view.san_sang; select(ui); await send(ui); await flush();
    assert.match(shown(output(ui)), /Số tiền DEMO: 1\.000\.000 VND/);
    assert.match(shown(output(ui)), /Model đã dùng: Qwen DEMO/);
    assert.ok(shown(output(ui)).includes(label));
    assert.match(shown(output(ui)), /08\/11\/2026 08:02:03/); assert.match(shown(output(ui)), /08\/11\/2026 08:02:05/);
    assert.doesNotMatch(shown(output(ui)), /luot_demo|uu_tien|du_phong|co_dinh/);
  });
}
test('Lý do chọn rỗng hiện dấu — trong kết quả và lịch sử', async () => {
  const result = done('');
  const ui = setup({ handler: url => url === API + '/luot_demo' ? response(result)
    : url.endsWith('?gioi_han=20') ? response({ luot: [result] }) : undefined });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  assert.ok(find(output(ui), 'p').some(node => node.textContent === '—'));
  assert.equal(find(ui.root, 'tbody')[0].children[0].children[4].textContent, '—');
});
test('Lượt lỗi: thong_diep_viet và ma_ho_tro thu gọn; Thử lại tạo ý định mới', async () => {
  let failed = true;
  const ui = setup({ handler: url => url === API + '/luot_demo' ? response(failed
    ? { trang_thai: 'loi', loi: { thong_diep_viet: 'Máy AI chưa sẵn sàng. Cần thử lại.', ma_ho_tro: 'AI_DEMO_123' } }
    : done()) : undefined });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  assert.match(shown(output(ui)), /Máy AI chưa sẵn sàng/);
  const detail = find(output(ui), 'details')[0];
  assert.equal(detail.open, undefined); assert.equal(find(detail, 'summary')[0].textContent, 'Chi tiết hỗ trợ');
  assert.match(detail.textContent, /AI_DEMO_123/);
  assert.equal(button(ui.root, 'Thử lại').hidden, false);
  failed = false; await button(ui.root, 'Thử lại').click(); await flush();
  assert.equal(posts(ui).length, 2);
  assert.notEqual(posts(ui)[0].init.headers['Idempotency-Key'], posts(ui)[1].init.headers['Idempotency-Key']);
});
test('Lỗi chuẩn Core: chỉ đọc thong_diep, mã và request_id trong hỗ trợ; gửi lại giữ khóa', async () => {
  let failed = true;
  const ui = setup({ handler: (_, init) => init.method === 'POST' && failed ? response({
    ma: 'AI_DEMO_BAN', thong_diep: 'Máy AI đang bận. Thử lại sau.', request_id: 'tra_cuu_demo',
    message: 'SECRET_DEMO', chi_tiet: { password: 'SECRET_DEMO' }
  }, 503) : undefined });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  assert.match(shown(output(ui)), /Máy AI đang bận/); assert.doesNotMatch(shown(ui.root), /SECRET_DEMO|password/);
  assert.match(find(output(ui), 'details')[0].textContent, /AI_DEMO_BAN.*tra_cuu_demo/);
  failed = false; await button(ui.root, 'Thử lại').click(); await flush();
  assert.equal(posts(ui).length, 2);
  assert.equal(posts(ui)[0].init.headers['Idempotency-Key'], posts(ui)[1].init.headers['Idempotency-Key']);
});
test('Lỗi GET sau tiếp nhận: Thử lại/Xem lại đọc cùng lượt, không POST nữa', async () => {
  let failed = true;
  const ui = setup({ handler: url => {
    if (url === API + '/luot_demo' && failed) throw new Error('SECRET_DEMO');
  } });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  assert.equal(button(ui.root, 'Xem lại').hidden, false); assert.equal(ui.clock.jobs.size, 0);
  failed = false; await button(ui.root, 'Thử lại').click(); await flush();
  assert.equal(posts(ui).length, 1); assert.match(shown(output(ui)), /Đã có kết quả/);
});
test('Treo HTTP dừng sau 15 giây, hủy request và cho Xem lại', async () => {
  const ui = setup({ handler: url => url === API + '/luot_demo' ? new Promise(() => {}) : undefined });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  await ui.clock.tick(15000);
  assert.equal(polls(ui)[0].init.signal.aborted, true);
  assert.equal(button(ui.root, 'Xem lại').hidden, false); assert.equal(ui.clock.jobs.size, 0);
});
test('Lịch sử đọc 20 mới nhất từ API, không hiện trả lời hay UUID; mở lại đọc lại máy chủ', async () => {
  const history = Array.from({ length: 25 }, (_, i) => ({ ...done(i ? 'du_phong:1' : 'co_dinh'),
    tra_loi: 'KHONG_HIEN_LICH_SU', ma_luot: '00000000-0000-4000-8000-000000000001', model: 'Model DEMO ' + i }));
  const options = { handler: url => url.endsWith('?gioi_han=20') ? response({ luot: history }) : undefined };
  const ui = setup(options); await ui.view.san_sang;
  const rows = find(ui.root, 'tbody')[0].children; assert.equal(rows.length, 20);
  assert.match(rows[0].textContent, /Model DEMO 0/); assert.match(rows[19].textContent, /Model DEMO 19/);
  assert.doesNotMatch(shown(ui.root), /KHONG_HIEN_LICH_SU|00000000/);
  ui.view.dung(); const next = setup(options); await next.view.san_sang;
  assert.equal(find(next.root, 'tbody')[0].children.length, 20);
});
test('Lỗi lịch sử không khóa form; Tải lại lịch sử chỉ gửi GET', async () => {
  let failed = true;
  const ui = setup({ handler: url => {
    if (url.endsWith('?gioi_han=20') && failed) throw new Error('SECRET_DEMO');
  } });
  await ui.view.san_sang; assert.match(shown(ui.root), /Chưa tải được lịch sử/);
  assert.equal(button(ui.root, 'Gửi').disabled, false);
  failed = false; await button(ui.root, 'Tải lại lịch sử').click();
  assert.match(shown(ui.root), /Chưa có lượt chạy thử/); assert.equal(posts(ui).length, 0);
});
test('XSS: nhãn, câu trả lời và lỗi đều là textContent, bỏ trường ngoài hợp đồng', async () => {
  const canary = '<img src=x onerror=alert(1)>';
  const ui = setup({ handler: url => url.endsWith('/function') ? response({ function: [{ ...functions[0], mo_ta: canary }] })
    : url === API + '/luot_demo' ? response({ ...done(), tra_loi: canary, prompt: 'KHONG_HIEN_PROMPT', khoa: 'SECRET_DEMO' }) : undefined });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  assert.ok(shown(output(ui)).includes(canary)); assert.equal(find(ui.root, 'img').length, 0);
  assert.doesNotMatch(shown(ui.root), /KHONG_HIEN_PROMPT|SECRET_DEMO/);
  assert.doesNotMatch(source, /innerHTML|insertAdjacentHTML|localStorage|sessionStorage/);
});
for (const [name, result] of [['trạng thái lạ', { trang_thai: 'queued', tra_loi: 'KHONG_HIEN' }],
  ['thiếu trả lời', { trang_thai: 'xong' }], ['thiếu lỗi', { trang_thai: 'loi' }]]) {
  test('Phản hồi hỏng ' + name + ' dừng hỏi, không công bố thành công', async () => {
    const ui = setup({ handler: url => url === API + '/luot_demo' ? response(result) : undefined });
    await ui.view.san_sang; select(ui); await send(ui); await flush();
    assert.equal(ui.clock.jobs.size, 0); assert.equal(button(ui.root, 'Xem lại').hidden, false);
    assert.doesNotMatch(shown(output(ui)), /Đã có kết quả|KHONG_HIEN/);
  });
}
test('Không dùng URL từ ma_luot hoặc Location, không theo chuyển hướng', async () => {
  for (const res of [response({ ma_luot: 'https://evil.invalid/secret' }, 202),
    response({ ma_luot: 'luot_demo' }, 202, { redirected: true }),
    response({}, 302)]) {
    const ui = setup({ handler: (_, init) => init.method === 'POST' ? res : undefined });
    await ui.view.san_sang; select(ui); await send(ui); await flush();
    assert.equal(polls(ui).length, 0); assert.doesNotMatch(shown(ui.root), /evil\.invalid|secret/);
  }
});
for (const status of [401, 403]) {
  test('Mất quyền khi đang theo dõi ' + status + ': xóa tài liệu/kết quả, chặn nút cũ', async () => {
    const ui = setup({ handler: url => url === API + '/luot_demo' ? response({}, status) : undefined });
    await ui.view.san_sang; select(ui); const form = find(ui.root, 'form')[0];
    await send(ui); await flush();
    assert.equal(find(ui.root, 'form').length, 0); assert.equal(find(ui.root, 'table').length, 0);
    assert.equal(ui.clock.jobs.size, 0);
    await form.events.submit({ preventDefault() {} }); assert.equal(posts(ui).length, 1);
  });
}
test('Đổi phiên trong thời gian chờ: không GET tiếp, xóa nháp và lịch sử', async () => {
  const ui = setup({ session: true, handler: url => url === API + '/luot_demo' ? response({ trang_thai: 'dang_chay' }) : undefined });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  ui.session({ csrf_token: 'CSRF_KHAC', nguoi_dung_id: 'nguoi_khac' }); await ui.clock.tick(1000);
  assert.equal(polls(ui).length, 1); assert.match(shown(ui.root), /Phiên làm việc đã thay đổi/);
  assert.equal(find(ui.root, 'form').length, 0); assert.equal(ui.clock.jobs.size, 0);
});
test('Thu hồi khai báo quyền: nút cũ chặn gửi và Quay lại không mở snapshot cũ', async () => {
  let back = 0; const ui = setup({ back: () => back++ }); await ui.view.san_sang;
  const oldBack = button(ui.root, 'Quay lại Hỏi AI'); ui.kb.khong_quyen = true;
  await oldBack.click(); assert.equal(back, 0); assert.equal(find(ui.root, 'form').length, 0);
  assert.equal(posts(ui).length, 0);
});
test('Rời màn khi đang chờ hủy timer và mọi request tiếp theo', async () => {
  const ui = setup({ handler: url => url === API + '/luot_demo' ? response({ trang_thai: 'dang_chay' }) : undefined });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  ui.view.dung(); await ui.clock.tick(180000);
  assert.equal(polls(ui).length, 1); assert.equal(ui.clock.jobs.size, 0); assert.equal(ui.root.children.length, 0);
});
test('Abort khi HTTP chưa trả: bỏ phản hồi muộn dù transport phớt lờ signal', async () => {
  let resolve;
  const ui = setup({ handler: url => url === API + '/luot_demo' ? new Promise(r => { resolve = r; }) : undefined });
  await ui.view.san_sang; select(ui); await send(ui); await flush();
  ui.view.dung(); await flush(); assert.equal(polls(ui)[0].init.signal.aborted, true);
  assert.equal(ui.clock.jobs.size, 0);
  resolve(response(done())); await flush(); assert.equal(ui.root.children.length, 0);
});
test('Abort trước/trong tải function không dựng lại màn', async () => {
  const signal = new AbortController(); signal.abort();
  const ui = setup({ signal: signal.signal }); await ui.view.san_sang; assert.equal(ui.calls.length, 0);
  let resolve; const nextSignal = new AbortController();
  const next = setup({ signal: nextSignal.signal, handler: url => url.endsWith('/function') ? new Promise(r => { resolve = r; }) : undefined });
  await flush(); nextSignal.abort(); await next.view.san_sang; assert.equal(next.root.children.length, 0);
  resolve(response({ function: functions })); await flush(); assert.equal(next.root.children.length, 0);
  assert.equal(next.clock.jobs.size, 0);
});
test('Mở từ chi tiết Hỏi AI: HTTP/CSRF/phiên truyền đủ, quay lại và đọc lịch sử mới', async () => {
  const ui = setup({ session: true }); await ui.view.san_sang; ui.view.dung();
  vm.runInContext(adminSource, ui.context);
  const inventory = JSON.parse(fs.readFileSync(path.join(dir, 'contract/quan_tri_engine.json'), 'utf8'))['urn:ktt:contract:quan_tri_engine.v2'].examples[0];
  const sdk = { api: { goi: async () => inventory }, phap_nhan: ui.sdk.phap_nhan };
  const view = ui.context.KttQuanTri.dung(ui.root, { sdk, sdk_he_thong: sdk, loai: 'engine',
    khai_bao_da_loc_quyen: { ma: 'quan_ly_engine', thao_tac: [] },
    csrf_token: 'CSRF_DEMO', nguoi_dung_id: 'nguoi_demo',
    doc_phien: () => ({ csrf_token: 'CSRF_DEMO', nguoi_dung_id: 'nguoi_demo' }),
    fetch: ui.fetch, tao_khoa: () => 'khoa_tu_quan_tri' });
  await view.san_sang; assert.equal(button(ui.root, 'Chạy thử DEMO'), undefined);
  await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click();
  await button(ui.root, 'Chạy thử DEMO').click(); select(ui); await send(ui); await flush();
  assert.equal(posts(ui)[0].init.headers['X-CSRF-Token'], 'CSRF_DEMO');
  assert.equal(posts(ui)[0].init.headers['Idempotency-Key'], 'khoa_tu_quan_tri');
  assert.doesNotMatch(shown(ui.root), /Cloud/);
  await button(ui.root, 'Quay lại Hỏi AI').click();
  assert.ok(button(ui.root, 'Quay lại danh sách')); assert.equal(find(ui.root, 'form').length, 0);
  await button(ui.root, 'Chạy thử DEMO').click();
  assert.equal(field(ui.root, 'Chức năng').value, ''); view.dung();
  assert.equal(ui.clock.jobs.size, 0);
});
test('Rời Quản lý engine khi JS DEMO đang nạp: không dựng màn từ phản hồi muộn', async () => {
  const ui = setup(); await ui.view.san_sang; ui.view.dung();
  ui.context.KttChayThuHoiAi = undefined;
  vm.runInContext(adminSource, ui.context);
  const inventory = JSON.parse(fs.readFileSync(path.join(dir, 'contract/quan_tri_engine.json'), 'utf8'))['urn:ktt:contract:quan_tri_engine.v2'].examples[0];
  const sdk = { api: { goi: async () => inventory } };
  const view = ui.context.KttQuanTri.dung(ui.root, { sdk, loai: 'engine',
    khai_bao_da_loc_quyen: { ma: 'quan_ly_engine', thao_tac: [] }, fetch: ui.fetch, csrf_token: 'CSRF_DEMO' });
  await view.san_sang; await button(ui.root, 'Xem chi tiết Hỏi đáp AI').click();
  const opening = button(ui.root, 'Chạy thử DEMO').click();
  const script = ui.root.ownerDocument.head.children[0];
  assert.equal(script.src, '/core/ui/chay_thu_hoi_ai.js');
  view.dung();
  vm.runInContext(source, ui.context); script.onload(); await opening;
  assert.equal(ui.root.children.length, 0);
  assert.equal(field(ui.root, 'Đoạn tài liệu giả'), undefined);
});
