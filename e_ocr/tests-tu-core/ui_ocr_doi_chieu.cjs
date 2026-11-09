'use strict';
// OCR-CR-8b: DOM và HTTP giả với SDK thật; không server, PG hay ABBYY.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const SDK = require('../src/kho_tri_thuc/sdk_core/trinh_duyet.js');
const ADMIN = require('../src/kho_tri_thuc/core/ui/quan_tri.js');
const asset = path.join(__dirname, '../src/kho_tri_thuc/core/ui/ocr_doi_chieu.js');
const UI = fs.existsSync(asset) ? require(asset) : null;
const BASE = '/api/v1/quan-tri/ocr/chua-ro';
const PN1 = '10000000-0000-4000-8000-000000000001';
const PN2 = '10000000-0000-4000-8000-000000000002';
const USER = '20000000-0000-4000-8000-000000000001';
const REQUEST = '30000000-0000-4000-8000-000000000001';
const MA = 'ocr:1234567890abcdef1234567890abcdef';
class Element {
  constructor(tag, doc) { this.tagName = tag; this.ownerDocument = doc; this.children = [];
    this.attrs = {}; this.events = {}; this._text = ''; this.value = ''; this.disabled = false; this.hidden = false; }
  set textContent(v) { this._text = String(v); this.children = []; }
  get textContent() { return this._text + this.children.map(n => n.textContent).join(' '); }
  set innerHTML(_) { assert.fail('Dữ liệu không được diễn giải thành HTML'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this._text = ''; this.children = nodes; }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  addEventListener(k, cb) { (this.events[k] ||= []).push(cb); }
  async emit(k) { for (const cb of this.events[k] || []) await cb({ preventDefault() {} }); }
  async click() { if (!this.disabled) await this.emit('click'); }
  async change(v) { if (!this.disabled) { this.value = v; await this.emit('change'); } }
  focus() { this.ownerDocument.activeElement = this; }
}
const all = n => [n, ...n.children.flatMap(all)];
const field = (root, label) => all(root).find(n => n.attrs['aria-label'] === label);
const button = (root, label) => all(root).find(n => ['button', 'a'].includes(n.tagName) && n.textContent === label);
const shown = root => root.tagName === 'details' ? '' : root._text + root.children.map(shown).join(' ');
const rows = () => [{ ma_tuong_quan: MA, so_trang: 3, trang_thai: 'CHUA_RO',
  giu_luc: '08/11/2026 10:04:05', module: 'crm', ma_bam_dau: 'deadbeef', phien_ban: 2 }];
const page = (values = rows(), permission = true) => ({ danh_sach: values, co_quyen_chot: permission });
const reply = (data, status = 200) => ({ status, ok: status === 200, redirected: false,
  headers: new Headers({ 'Content-Type': 'application/json', 'X-Request-Id': REQUEST }),
  json: async () => structuredClone(data) });
const gate = () => { let resolve; const promise = new Promise(r => { resolve = r; }); return { promise, resolve }; };
const flush = async () => { for (let i = 0; i < 8; i++) await new Promise(setImmediate); };
function setup(options = {}) {
  assert.equal(typeof UI?.dung, 'function', 'Chưa có màn đối chiếu');
  const doc = { createElement: tag => new Element(tag, doc) }; doc.head = doc.createElement('head');
  const root = doc.createElement('main'), calls = [];
  const sdk = SDK.tao({ tao_ma: () => REQUEST, fetch: async (url, init) => {
    calls.push({ url, ...init });
    assert.equal(init.credentials, 'same-origin'); assert.equal(init.mode, 'same-origin');
    assert.equal(init.redirect, 'error'); assert.equal(init.cache, 'no-store');
    if (options.http) { const result = await options.http(url, init, calls); if (result) return result; }
    if (url.startsWith('/api/v1/phap-nhan?')) return reply({ danh_sach: [
      { id: PN1, ten: 'Công ty DEMO Ánh Dương', la_demo: true },
      { id: PN2, ten: 'Công ty DEMO Bình Minh', la_demo: true }], con_tiep: false, con_tro_tiep: null });
    if (url.startsWith(BASE + '?')) return reply(options.data || page());
    if (init.method === 'POST') return reply({ ma_tuong_quan: MA, so_trang: 3,
      trang_thai: JSON.parse(init.body).ket_qua === 'da_tieu' ? 'DA_TIEU_TRANG' : 'HOAN_TRANG', phien_ban: 3 });
    throw new Error('Route ngoài dự kiến: ' + url);
  } });
  sdk.api.doi_ngu_canh({ nguoi_dung_id: USER }); sdk.api.gan_csrf('CSRF_DEMO');
  const view = UI.dung(root, { sdk_he_thong: sdk, khai_bao_da_loc_quyen: { ma: 'quan_ly_engine', thao_tac: [] },
    signal: options.signal, tao_khoa: () => 'OCR_DEMO_KHOA', khi_quay_lai: options.back });
  return { root, calls, view, doc };
}
const reads = ui => ui.calls.filter(c => c.url.startsWith(BASE + '?'));
const posts = ui => ui.calls.filter(c => c.method === 'POST');
async function choose(ui, index = '0') { await ui.view.san_sang; await field(ui.root, 'Pháp nhân').change(index); }
async function confirm(ui, result = 'hoan_trang', note = 'Đã đối chiếu sổ ABBYY DEMO.') {
  await button(ui.root, result === 'hoan_trang' ? 'Chốt hoàn trang' : 'Chốt đã tiêu trang').click();
  field(ui.root, 'Bằng chứng đối chiếu ABBYY').value = note;
  await button(ui.root, 'Xác nhận chốt').click();
}

test('chọn pháp nhân trước khi đọc; tên nghiệp vụ, ngày và mã tương quan rút gọn', async () => {
  const ui = setup(); await ui.view.san_sang; assert.equal(reads(ui).length, 0);
  await choose(ui); assert.match(reads(ui)[0].url, new RegExp('phap_nhan_id=' + PN1));
  assert.equal(reads(ui)[0].headers['X-Phap-Nhan-Id'], PN1);
  assert.match(shown(ui.root), /Chưa rõ/); assert.match(shown(ui.root), /08\/11\/2026 10:04/);
  assert.match(shown(ui.root), /Quản lý quan hệ khách hàng/);
  assert.doesNotMatch(shown(ui.root), /deadbeef|ocr:|1234567890abcdef|phien_ban|\bcrm\b|\b(?:Anh|bạn)\b|10:04:05/);
  assert.ok(button(ui.root, 'Chốt đã tiêu trang')); assert.ok(button(ui.root, 'Chốt hoàn trang'));
  assert.match(shown(ui.root), /Chỉ đổi trạng thái lượt; hạn mức trang sẽ được cập nhật ở bước sau/);
});
test('đang giữ quá hạn và module lạ dùng nhãn dự phòng', async () => {
  const data = page(); data.danh_sach[0].trang_thai = 'DANG_GIU'; data.danh_sach[0].module = 'mod_la';
  const ui = setup({ data }); await choose(ui);
  assert.match(shown(ui.root), /Đang giữ quá hạn/); assert.match(shown(ui.root), /Module nghiệp vụ/);
  assert.doesNotMatch(shown(ui.root), /mod_la|DANG_GIU/);
});
test('chỉ xem và API cũ thiếu thông tin quyền đều ẩn nút chốt', async () => {
  for (const data of [page(rows(), false), { danh_sach: rows() }]) {
    const ui = setup({ data }); await choose(ui); assert.match(shown(ui.root), /Chưa rõ/);
    assert.equal(button(ui.root, 'Chốt hoàn trang'), undefined); assert.equal(button(ui.root, 'Chốt đã tiêu trang'), undefined);
    assert.equal(posts(ui).length, 0);
  }
});
for (const result of ['da_tieu', 'hoan_trang']) test('chốt ' + result + ': xác nhận, CSRF, đúng phiên bản và tải lại', async () => {
  const ui = setup(); await choose(ui); await confirm(ui, result);
  assert.equal(posts(ui).length, 1); const call = posts(ui)[0];
  assert.equal(call.url, BASE + '/' + MA + '/chot');
  assert.equal(call.headers['X-CSRF-Token'], 'CSRF_DEMO'); assert.equal(call.headers['X-Phap-Nhan-Id'], PN1);
  assert.deepEqual(JSON.parse(call.body), { ket_qua: result, phien_ban: 2, ghi_chu: 'Đã đối chiếu sổ ABBYY DEMO.' });
  assert.equal(reads(ui).length, 2); assert.equal(field(ui.root, 'Bằng chứng đối chiếu ABBYY'), undefined);
  assert.match(shown(ui.root), /Đã chốt/); assert.doesNotMatch(shown(ui.root), /đã hoàn hạn mức/i);
});
for (const note of ['', ' \t\n ', 'ế'.repeat(501), ' ' + 'ế'.repeat(500)]) test('bằng chứng sai: không gửi (' + note.length + ')', async () => {
  const ui = setup(); await choose(ui); await confirm(ui, 'hoan_trang', note);
  assert.equal(posts(ui).length, 0); assert.ok(field(ui.root, 'Bằng chứng đối chiếu ABBYY'));
  assert.match(shown(ui.root), /bằng chứng|500/);
});
test('bằng chứng 500 ký tự và nút Hủy không gửi', async () => {
  const ui = setup(); await choose(ui); await button(ui.root, 'Chốt hoàn trang').click();
  assert.equal(field(ui.root, 'Bằng chứng đối chiếu ABBYY').maxLength, 500);
  await button(ui.root, 'Hủy').click(); assert.equal(posts(ui).length, 0);
  await confirm(ui, 'da_tieu', 'ế'.repeat(500)); assert.equal(JSON.parse(posts(ui)[0].body).ghi_chu.length, 500);
});
test('409 chặn chốt lại bản cũ, mã lỗi/request chỉ trong hỗ trợ thu gọn', async () => {
  const ui = setup({ http: (_, init) => init.method === 'POST'
    ? reply({ ma: 'OCR_ADMIN_XUNG_DOT', request_id: REQUEST, thong_diep: '<img src=x> bí mật' }, 409) : null });
  await choose(ui); await confirm(ui);
  assert.match(shown(ui.root), /Lượt vừa thay đổi, tải lại danh sách/);
  assert.doesNotMatch(shown(ui.root), /OCR_ADMIN_|30000000|<img|bí mật/);
  const support = all(ui.root).find(n => n.tagName === 'details'); assert.ok(support); assert.ok(!support.open);
  assert.match(support.textContent, new RegExp(REQUEST));
  assert.equal(button(ui.root, 'Chốt hoàn trang'), undefined); assert.equal(posts(ui).length, 1);
  await button(ui.root, 'Tải lại danh sách').click(); assert.equal(reads(ui).length, 2);
});
for (const status of [401, 403, 503]) test('POST ' + status + ': không tự gửi lại, không lộ lỗi máy chủ', async () => {
  const ui = setup({ http: (_, init) => init.method === 'POST'
    ? reply({ ma: 'OCR_ADMIN_LOI', request_id: REQUEST, thong_diep: 'SECRET DSN=demo' }, status) : null });
  await choose(ui); await confirm(ui); assert.equal(posts(ui).length, 1);
  assert.doesNotMatch(shown(ui.root), /SECRET|DSN|OCR_ADMIN_/);
  assert.equal(button(ui.root, 'Chốt hoàn trang'), undefined);
});
test('danh sách rỗng', async () => {
  const ui = setup({ data: page([]) }); await choose(ui); assert.match(shown(ui.root), /Không có lượt/);
});
for (const [key, value] of [['ma_tuong_quan', '<script>'], ['so_trang', 0], ['trang_thai', 'HOAN_TRANG'],
    ['giu_luc', '2026-11-08'], ['module', '<img>'], ['phien_ban', 0], ['phien_ban', Number.MAX_SAFE_INTEGER + 1]]) {
  test('DTO sai không dựng nút chốt: ' + key, async () => {
    const data = page(); data.danh_sach[0][key] = value; const ui = setup({ data }); await choose(ui);
    assert.equal(button(ui.root, 'Chốt hoàn trang'), undefined); assert.equal(posts(ui).length, 0);
  });
}
test('đổi pháp nhân xóa nháp và bỏ phản hồi muộn của pháp nhân cũ', async () => {
  const pending = gate(); const ui = setup({ http: url => url.includes('phap_nhan_id=' + PN1) ? pending.promise : null });
  await ui.view.san_sang; const old = field(ui.root, 'Pháp nhân').change('0');
  await flush(); await field(ui.root, 'Pháp nhân').change('1');
  pending.resolve(reply(page([{ ...rows()[0], so_trang: 999 }]))); await old;
  assert.doesNotMatch(shown(ui.root), /999/); assert.equal(reads(ui).at(-1).headers['X-Phap-Nhan-Id'], PN2);
  await button(ui.root, 'Chốt hoàn trang').click(); assert.equal(ui.view.co_nhap(), true);
  await field(ui.root, 'Pháp nhân').change('0'); assert.equal(field(ui.root, 'Bằng chứng đối chiếu ABBYY'), undefined);
});
test('gửi chốt khóa thao tác kép; đổi pháp nhân khóa trong khi ghi', async () => {
  const pending = gate(); const ui = setup({ http: (_, init) => init.method === 'POST' ? pending.promise : null });
  await choose(ui); const posting = confirm(ui); await flush();
  assert.equal(field(ui.root, 'Pháp nhân').disabled, true); assert.equal(posts(ui).length, 1);
  await button(ui.root, 'Xác nhận chốt')?.click(); assert.equal(posts(ui).length, 1);
  pending.resolve(reply({ ma_tuong_quan: MA, so_trang: 3, trang_thai: 'HOAN_TRANG', phien_ban: 3 })); await posting;
});
test('rời màn khi GET đang chờ bỏ phản hồi muộn và khóa nút cũ', async () => {
  const pending = gate(), controller = new AbortController();
  const ui = setup({ signal: controller.signal, http: url => url.startsWith(BASE) ? pending.promise : null });
  await ui.view.san_sang; const old = field(ui.root, 'Pháp nhân').change('0'); await flush();
  controller.abort(); pending.resolve(reply(page())); await old; assert.equal(ui.root.textContent, '');
});
test('tên pháp nhân không diễn giải markup hoặc hiện UUID trong nội dung nghiệp vụ', async () => {
  const ui = setup({ http: url => url.startsWith('/api/v1/phap-nhan?') ? reply({ danh_sach: [
    { id: PN1, ten: '<img onerror=alert(1)>', la_demo: true }], con_tiep: false, con_tro_tiep: null }) : null });
  await choose(ui); assert.doesNotMatch(shown(ui.root), /<img|onerror|10000000/);
});
test('tên module lấy từ registry hiện hành, kể cả module ngoài danh mục dự phòng', async () => {
  const data = page(); data.danh_sach[0].module = 'nghiep_vu_moi';
  const ui = setup({ data, http: url => url === '/api/v1/quan-tri/module/ten' ? reply({ danh_sach: [
    { ma: 'nghiep_vu_moi', ten: 'Quản lý công nợ DEMO', phien_ban: '1.0.0' }], con_tiep: false, con_tro_tiep: null }) : null });
  await choose(ui); assert.match(shown(ui.root), /Quản lý công nợ DEMO/);
  assert.doesNotMatch(shown(ui.root), /nghiep_vu_moi/);
});
test('SDK đổi ngữ cảnh thì đóng màn cũ, không tải lại dưới danh tính khác', async () => {
  const ui = setup({ http: url => { if (url.startsWith(BASE)) throw Object.assign(new Error(), { ma: 'NGU_CANH_DA_DOI' }); } });
  await choose(ui); assert.equal(ui.root.textContent, '');
});
test('GET 403 xóa bảng và mọi nút chốt cũ', async () => {
  let fail = false; const ui = setup({ http: url => url.startsWith(BASE) && fail
    ? reply({ ma: 'OCR_ADMIN_QUYEN', request_id: REQUEST }, 403) : null });
  await choose(ui); const old = button(ui.root, 'Chốt hoàn trang');
  fail = true; await button(ui.root, 'Tải lại danh sách').click(); await old.click();
  assert.equal(field(ui.root, 'Bằng chứng đối chiếu ABBYY'), undefined);
  assert.equal(button(ui.root, 'Chốt hoàn trang'), undefined); assert.equal(posts(ui).length, 0);
});
test('rời màn khi POST đang chờ: không vẽ lại, không gửi chốt lần nữa', async () => {
  const pending = gate(), controller = new AbortController();
  const ui = setup({ signal: controller.signal, http: (_, init) => init.method === 'POST' ? pending.promise : null });
  await choose(ui); const posting = confirm(ui); await flush(); controller.abort();
  pending.resolve(reply({ ma_tuong_quan: MA, so_trang: 3, trang_thai: 'HOAN_TRANG', phien_ban: 3 }));
  await posting; assert.equal(ui.root.textContent, ''); assert.equal(posts(ui).length, 1); assert.equal(reads(ui).length, 1);
});
test('đường vào từ chi tiết OCR dùng API thật qua SDK và rời chi tiết hủy màn con', async () => {
  assert.ok(UI); const doc = { createElement: tag => new Element(tag, doc) }; doc.head = doc.createElement('head');
  const root = doc.createElement('main'); const inventory = structuredClone(JSON.parse(fs.readFileSync(
    path.join(__dirname, '../src/kho_tri_thuc/core/contract/quan_tri_engine.json'), 'utf8'))['urn:ktt:contract:quan_tri_engine.v2'].examples[0]);
  const sdk = { api: { goi: async req => req.duong_dan.includes('kiem-ke') ? inventory : { danh_sach: [] } },
    phap_nhan: { danh_sach: async () => ({ danh_sach: [], con_tiep: false, con_tro_tiep: null }) } };
  const previous = globalThis.KttOCRDoiChieu; globalThis.KttOCRDoiChieu = UI;
  try {
    const view = ADMIN.dung(root, { sdk, loai: 'engine', khai_bao_da_loc_quyen: { ma: 'quan_ly_engine', thao_tac: [] } });
    await view.san_sang;
    const ocr = inventory.danh_sach.find(r => r.ma === 'e_ocr'); await button(root, 'Xem chi tiết ' + ocr.ten).click();
    await button(root, 'Đối chiếu lượt chưa rõ').click(); assert.match(shown(root), /Chọn pháp nhân/);
    await button(root, 'Quay lại chi tiết engine').click(); assert.equal(field(root, 'Bằng chứng đối chiếu ABBYY'), undefined);
    assert.ok(button(root, 'Đối chiếu lượt chưa rõ')); view.dung(); assert.equal(root.textContent, '');
  } finally { globalThis.KttOCRDoiChieu = previous; }
});
