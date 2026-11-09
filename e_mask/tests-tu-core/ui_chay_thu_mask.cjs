'use strict';
// MASK-5: DOM/SDK/API được tiêm, chỉ dữ liệu DEMO, không mạng/CSDL/engine thật.
// Node không chạy Python; tests/test_mask5_seam.py đối chiếu khóa với engine thật.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const UI = require('../src/kho_tri_thuc/core/ui/chay_thu_mask.js');
const dir = path.join(__dirname, '../src/kho_tri_thuc/core');
const source = fs.readFileSync(path.join(dir, 'ui/chay_thu_mask.js'), 'utf8');
const adminSource = fs.readFileSync(path.join(dir, 'ui/quan_tri.js'), 'utf8');
const contract = JSON.parse(fs.readFileSync(path.join(dir, 'contract/quan_tri_engine.json'), 'utf8'));
const inventory = () => structuredClone(contract['urn:ktt:contract:quan_tri_engine.v2'].examples[0]);
class Element {
  constructor(tag, doc) {
    this.tagName = tag; this.ownerDocument = doc; this.children = []; this.events = {};
    this.attrs = {}; this._text = ''; this.value = ''; this.disabled = false; this.hidden = false;
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(n => n.textContent).join(' '); }
  set innerHTML(value) { assert.fail('Không diễn giải dữ liệu thành HTML'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; this._text = ''; }
  setAttribute(key, value) { this.attrs[key] = String(value); }
  addEventListener(type, callback) { this.events[type] = callback; }
  click() { if (!this.disabled && !this.hidden) return this.events.click?.({ preventDefault() {} }); }
}
const all = n => [n, ...n.children.flatMap(all)];
const find = (root, tag) => all(root).filter(n => n.tagName === tag);
const field = (root, label) => all(root).find(n => n.attrs['aria-label'] === label);
const button = (root, text) => all(root).find(n => ['button', 'a'].includes(n.tagName) && n.textContent === text);
const shown = n => n.hidden || n.tagName === 'style' ? '' : n._text + n.children.map(shown).join(' ');
const change = (n, value) => { n.value = value; return n.events.input?.(); };
const submit = (root, index = 0) => find(root, 'form')[index].events.submit({ preventDefault() {} });
function dom() {
  const doc = { createElement: tag => new Element(tag, doc) }; doc.head = doc.createElement('head');
  return doc.createElement('div');
}
const BI_DANH_TAM = '[[MASKTAM-0123456789abcdef0123456789abcdef]]';
// Nguồn: engines/e_mask/che_van_ban.py:500, 521–524 (mẫu 2).
const masked = () => ({
  ma_yeu_cau: 'YEUCau-DEMO-noi-bo', van_ban_da_che: '[[CT-0001]]; ' + BI_DANH_TAM + '; 1.000.000 VND; 30/10/2026.',
  so_cho_thay: 2, bi_danh: [{ bi_danh: '[[CT-0001]]', nhom: 'CONG_TY', nguon: 'chinh_thuc' },
    { bi_danh: BI_DANH_TAM, nhom: 'MA_SO_THUE', nguon: 'tam' }],
  cho_duyet: { so_cum_vua_them: 1 }, con_sot: [], kiem_tien_ngay: true, gui_duoc: true, canh_bao: []
});
// Nguồn: engines/e_mask/che_van_ban.py:631–633 (mẫu 4).
const unmasked = () => ({ van_ban_da_mo_che: 'Công ty DEMO Ánh Dương; 1.000.000 VND; 30/10/2026.',
  so_cho_mo: 2, bi_danh_khong_ro: [], mo_day_du: true, trang_thai_ma_yeu_cau: 'DANG_XU_LY' });
function setup(options = {}) {
  const root = dom(), calls = [], requests = [];
  const kb = options.kb === undefined ? { ma: 'quan_ly_engine', thao_tac: [] } : options.kb;
  const sdk = { api: { goi: async req => {
    calls.push(req); assert.equal(req.duong_dan, '/api/v1/quan-tri/engine/kiem-ke');
    assert.equal(req.phuong_thuc || 'GET', 'GET');
    return options.auth ? options.auth(req) : inventory();
  } } };
  const api = options.noApi ? undefined : {
    che_van_ban: async (body, opt) => { requests.push({ kind: 'che', body, opt }); return options.mask ? options.mask(body, opt) : masked(); },
    mo_che_van_ban: async (body, opt) => { requests.push({ kind: 'mo', body, opt }); return options.unmask ? options.unmask(body, opt) : unmasked(); }
  };
  const view = UI.dung(root, { sdk_he_thong: options.noSdk ? undefined : sdk, api_mask: api,
    khai_bao_da_loc_quyen: kb, signal: options.signal, khi_quay_lai: options.back });
  return { root, calls, requests, view, kb };
}
test('Admin mở DEMO sau GET xác minh, có đủ hai phần và nút mẫu đúng tiền/ngày/MST giả', async () => {
  const ui = setup(); await ui.view.san_sang;
  assert.equal(ui.calls.length, 1); assert.equal(ui.requests.length, 0);
  assert.match(shown(ui.root), /Chạy thử DEMO.*Che định danh/);
  assert.equal(find(ui.root, 'form').length, 2);
  change(field(ui.root, 'Văn bản DEMO cần che'), ''); await button(ui.root, 'Dùng mẫu DEMO').click();
  const text = field(ui.root, 'Văn bản DEMO cần che').value;
  for (const s of ['Công ty DEMO Ánh Dương', '1.000.000 VND', '30/10/2026', 'MST giả']) assert.ok(text.includes(s));
  assert.doesNotMatch(shown(ui.root), /\b(Anh|bạn)\b|ma_yeu_cau|request_id|e_mask/);
});
for (const kb of [null, { ma: 'quan_ly_engine', khong_quyen: true }, { ma: 'quan_ly_module' }]) {
  test(`Không Admin hoặc sai màn không gọi API: ${JSON.stringify(kb)}`, async () => {
    const ui = setup({ kb }); await ui.view.san_sang;
    assert.equal(ui.calls.length, 0); assert.equal(ui.requests.length, 0);
    assert.equal(find(ui.root, 'form').length, 0); assert.match(shown(ui.root), /Chỉ Admin Core/);
  });
}
test('Không SDK hoặc phản hồi quyền sai không dựng form', async () => {
  for (const opt of [{ noSdk: true }, { auth: () => ({ danh_sach: [] }) }]) {
    const ui = setup(opt); await ui.view.san_sang; assert.equal(find(ui.root, 'form').length, 0);
  }
});
for (const error of [{ status: 401 }, { status: 403 }, { ma: 'NGU_CANH_DA_DOI' }, { ma: 'SAI_NGU_CANH' }]) {
  test(`Quyền từ chối ${error.status || error.ma}: xóa form và không lộ lỗi gốc`, async () => {
    const ui = setup({ auth: () => { throw { ...error, message: 'CUM_GOC_DEMO' }; } }); await ui.view.san_sang;
    assert.equal(find(ui.root, 'form').length, 0); assert.equal(button(ui.root, 'Quay lại Che định danh'), undefined);
    assert.doesNotMatch(shown(ui.root), /CUM_GOC_DEMO|NGU_CANH|SAI_NGU_CANH/);
  });
}
test('Che gửi mẫu 1 qua lớp được tiêm; chỉ hiển thị trường mẫu 2 được phép', async () => {
  const ui = setup({ mask: () => ({ ...masked(), cum_moi: [{ cum: 'CUM_GOC_DEMO' }], mapping: 'BANG_DOI_CHIEU_DEMO' }) });
  await ui.view.san_sang;
  change(field(ui.root, 'Định danh đã biết (tùy chọn)'), 'Công ty DEMO Ánh Dương | Tên tổ chức\n0000000000-DEMO | Mã số thuế');
  await submit(ui.root);
  const req = ui.requests[0]; assert.equal(req.kind, 'che');
  assert.deepEqual(req.body.dinh_danh_da_biet, [
    { gia_tri: 'Công ty DEMO Ánh Dương', nhom: 'CONG_TY' }, { gia_tri: '0000000000-DEMO', nhom: 'MA_SO_THUE' }]);
  assert.deepEqual(Object.keys(req.body).sort(), ['dinh_danh_da_biet', 'van_ban']);
  assert.equal(req.opt.signal.aborted, false);
  const output = shown(field(ui.root, 'Kết quả che'));
  for (const s of ['[[CT-0001]]', BI_DANH_TAM, 'Tên tổ chức', 'Mã số thuế', 'Chính thức', 'Tạm',
    'Số chỗ thay: 2', 'Số cụm vừa vào chờ duyệt: 1', 'Kiểm tiền/ngày: Đạt', '1.000.000 VND', '30/10/2026']) assert.ok(output.includes(s), s);
  assert.doesNotMatch(shown(ui.root), /YEUCau-DEMO|CUM_GOC_DEMO|BANG_DOI_CHIEU_DEMO|CONG_TY|chinh_thuc/);
  assert.equal(field(ui.root, 'Văn bản có bí danh').value, masked().van_ban_da_che);
});
test('Còn sót chỉ hiện vị trí/loại và chặn gửi, không lộ giá trị cả trong văn bản kết quả', async () => {
  // Nguồn: che_van_ban.py:385–388, 419–420. Cố ý gửi cờ mâu thuẫn và gia_tri:
  // còn sót phải tự chặn, kể cả khi adapter nhầm gui_duoc = true.
  const ui = setup({ mask: () => ({ ...masked(), van_ban_da_che: 'CUM_GOC_DEMO chưa che',
    con_sot: [{ vi_tri: { bat_dau: 12, ket_thuc: 25, dong: 2, cot: 4 }, nhom: 'MA_SO_THUE', gia_tri: 'CUM_GOC_DEMO' }],
    gui_duoc: true }) });
  await ui.view.san_sang; await submit(ui.root);
  const output = shown(field(ui.root, 'Kết quả che'));
  assert.match(output, /Không được gửi: còn thông tin định danh chưa che/);
  assert.match(output, /dòng 2, cột 4.*Mã số thuế/); assert.doesNotMatch(output, /CUM_GOC_DEMO|gia_tri|MA_SO_THUE/);
  assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 0);
  assert.equal(field(ui.root, 'Văn bản có bí danh').value, '');
});
for (const value of [false, undefined]) test(`Kiểm tiền/ngày ${value} không công bố gửi được`, async () => {
  const ui = setup({ mask: () => ({ ...masked(), kiem_tien_ngay: value }) }); await ui.view.san_sang; await submit(ui.root);
  assert.doesNotMatch(shown(field(ui.root, 'Kết quả che')), /Đủ điều kiện/);
  assert.match(shown(field(ui.root, 'Kết quả che')), value === false ? /Kiểm tiền\/ngày: Không đạt/ : /Chưa kiểm/);
});
// Nguồn: che_van_ban.py:511, 514, 521–524: khi bị chặn, văn bản là null.
for (const ly_do of ['Chưa kiểm tra đầy đủ định danh.', 'Văn bản đầu vào đã chứa dấu bí danh cần kiểm tra.']) {
  test('Còn sót chỉ có lý do: ' + ly_do, async () => {
    const ui = setup({ mask: () => ({ ...masked(), van_ban_da_che: null, con_sot: [{ ly_do }], gui_duoc: false }) });
    await ui.view.san_sang; await submit(ui.root);
    const output = shown(field(ui.root, 'Kết quả che'));
    assert.ok(output.includes(ly_do)); assert.match(output, /Số chỗ thay: 2/);
    assert.doesNotMatch(output, /Chưa hoàn tất chạy thử|\bnull\b/);
    assert.equal(find(field(ui.root, 'Kết quả che'), 'pre').length, 0);
    assert.equal(field(ui.root, 'Văn bản có bí danh').value, '');
  });
}
for (const key of ['kiem_tien_ngay', 'gui_duoc']) for (const value of [false, undefined, 'true']) {
  test(key + ' = ' + value + ': ẩn hẳn văn bản dù còn sót rỗng', async () => {
    const ui = setup({ mask: () => ({ ...masked(), [key]: value, van_ban_da_che: 'CUM_GOC_DEMO chưa được chấp nhận' }) });
    await ui.view.san_sang; await submit(ui.root);
    const result = field(ui.root, 'Kết quả che'), output = shown(result);
    assert.match(output, /Không được gửi/); assert.doesNotMatch(output, /CUM_GOC_DEMO|Đã có kết quả che/);
    assert.equal(find(result, 'pre').length, 0);
    assert.equal(field(ui.root, 'Văn bản có bí danh').value, '');
    if (key === 'kiem_tien_ngay') assert.match(output, value === false ? /Kiểm tiền\/ngày: Không đạt/ : /Chưa kiểm/);
  });
}
test('Kiểm tiền/ngày không đạt với văn bản null vẫn hiện lý do và số chỗ thay', async () => {
  const ui = setup({ mask: () => ({ ...masked(), van_ban_da_che: null, kiem_tien_ngay: false, gui_duoc: false }) });
  await ui.view.san_sang; await submit(ui.root);
  const output = shown(field(ui.root, 'Kết quả che'));
  assert.match(output, /Không được gửi: kiểm tiền\/ngày chưa đạt/); assert.match(output, /Số chỗ thay: 2/);
  assert.doesNotMatch(output, /Chưa hoàn tất chạy thử|\bnull\b/);
});
test('Lý do/vị trí không hợp lệ không lộ dữ liệu phản hồi thô', async () => {
  const ui = setup({ mask: () => ({ ...masked(), van_ban_da_che: null, gui_duoc: false,
    con_sot: [{ ly_do: 'CUM_GOC_DEMO' }, { nhom: 'SECRET_DEMO', vi_tri: { dong: 'SECRET_DEMO', cot: 1 } }] }) });
  await ui.view.san_sang; await submit(ui.root);
  const output = shown(field(ui.root, 'Kết quả che'));
  assert.match(output, /Cần kiểm tra lại định danh/); assert.match(output, /Chưa xác định vị trí/);
  assert.doesNotMatch(output, /CUM_GOC_DEMO|SECRET_DEMO/);
});

test('Bí danh hợp lệ có dấu chấm và dài 100 ký tự được hiện nguyên vẹn', async () => {
  // Nguồn: che_van_ban.py:49, 495; mã chính thức có thể dài tới 100 ký tự.
  const bi_danh = '[[KH.' + 'A'.repeat(97) + ']]';
  const ui = setup({ mask: () => ({ ...masked(), van_ban_da_che: bi_danh, so_cho_thay: 1,
    bi_danh: [{ bi_danh, nhom: 'CONG_TY', nguon: 'chinh_thuc' }], cho_duyet: { so_cum_vua_them: 0 } }) });
  await ui.view.san_sang; await submit(ui.root);
  const result = field(ui.root, 'Kết quả che');
  assert.equal(find(result, 'li')[0].textContent, bi_danh + ' · Tên tổ chức · Chính thức');
  assert.equal(field(ui.root, 'Văn bản có bí danh').value, bi_danh);
});

test('Mở che bắt buộc có lần che thành công; giữ mã trong closure, văn bản sửa tay đi nguyên vẹn', async () => {
  const ui = setup(); await ui.view.san_sang;
  change(field(ui.root, 'Văn bản có bí danh'), '[[CT-0001]]'); await submit(ui.root, 1);
  assert.equal(ui.requests.length, 0); assert.match(shown(ui.root), /Cần che văn bản DEMO trước/);
  await submit(ui.root);
  const edited = '[[ct-0001]] được sửa tay <script>DEMO</script>';
  change(field(ui.root, 'Văn bản có bí danh'), edited); await submit(ui.root, 1);
  // Nguồn: che_van_ban.py:527–528 (mẫu 3).
  assert.deepEqual(ui.requests[1].body, { ma_yeu_cau: masked().ma_yeu_cau, van_ban_co_bi_danh: edited, dong_viec: false });
  assert.match(shown(field(ui.root, 'Kết quả mở che')), /Số chỗ mở: 2.*Đang xử lý/);
  assert.match(shown(field(ui.root, 'Kết quả mở che')), /Đã mở che đầy đủ/);
  assert.match(shown(ui.root), /Công ty DEMO Ánh Dương/); assert.doesNotMatch(shown(ui.root), /YEUCau-DEMO/);
});
test('Mở chưa đủ giữ kết quả, báo bí danh + vị trí, yêu cầu còn đang xử lý', async () => {
  // Nguồn: che_van_ban.py:616, 629–633: chưa mở đủ thì không đóng việc.
  const ui = setup({ unmask: () => ({ ...unmasked(), mo_day_du: false,
    bi_danh_khong_ro: [{ bi_danh: '[[LA-9999]]', vi_tri: { bat_dau: 21, ket_thuc: 32, dong: 3, cot: 5 } }] }) });
  await ui.view.san_sang; await submit(ui.root); await submit(ui.root, 1);
  const output = shown(field(ui.root, 'Kết quả mở che'));
  assert.match(output, /Chưa mở che đầy đủ/); assert.match(output, /\[\[LA-9999\]\].*dòng 3, cột 5/);
  assert.match(output, /Công ty DEMO Ánh Dương/); assert.match(output, /Đang xử lý/);
  await submit(ui.root, 1); assert.equal(ui.requests.length, 3);
});
test('Mở chưa đủ theo cờ engine dù danh sách bí danh chưa rõ rỗng', async () => {
  const ui = setup({ unmask: () => ({ ...unmasked(), mo_day_du: false }) });
  await ui.view.san_sang; await submit(ui.root); await submit(ui.root, 1);
  const output = shown(field(ui.root, 'Kết quả mở che'));
  assert.match(output, /Chưa mở che đầy đủ/); assert.doesNotMatch(output, /Đã mở che đầy đủ/);
});

test('Đóng việc được chọn rõ, gửi boolean; trạng thái đã đóng không cho mở lại', async () => {
  const ui = setup({ unmask: body => ({ ...unmasked(), trang_thai_ma_yeu_cau: body.dong_viec ? 'DA_DONG' : 'DANG_XU_LY' }) });
  await ui.view.san_sang; await submit(ui.root);
  field(ui.root, 'Đóng việc sau khi mở').checked = true; await submit(ui.root, 1);
  assert.equal(ui.requests[1].body.dong_viec, true);
  assert.match(shown(field(ui.root, 'Kết quả mở che')), /Đã đóng/);
  assert.doesNotMatch(shown(ui.root), /DANG_XU_LY|DA_DONG|trang_thai_ma_yeu_cau/);
  await submit(ui.root, 1); assert.equal(ui.requests.length, 2);
});
test('Thiếu kênh gọi hiện Engine chưa sẵn sàng, không gọi route tự dựng hoặc giả kết quả', async () => {
  const ui = setup({ noApi: true }); await ui.view.san_sang; await submit(ui.root);
  assert.match(shown(ui.root), /Engine chưa sẵn sàng/); assert.equal(ui.requests.length, 0);
  assert.equal(ui.calls.length, 1); assert.doesNotMatch(shown(ui.root), /Số chỗ thay: 2/);
});
for (const status of [404, 501, 503, 500]) test(`API lỗi ${status}: câu nghiệp vụ + hỗ trợ thu gọn, không lộ lỗi gốc`, async () => {
  const ui = setup({ mask: () => { throw { status, ma: 'CUM_GOC_DEMO', message: 'SECRET_DEMO',
    request_id: '11111111-2222-4333-8444-555555555555' }; } });
  await ui.view.san_sang; await submit(ui.root);
  assert.match(shown(ui.root), status === 500 ? /Chưa hoàn tất/ : /Engine chưa sẵn sàng/);
  const details = find(ui.root, 'details'); assert.equal(details.length, 1); assert.ok(!details[0].open);
  assert.equal(find(details[0], 'summary')[0].textContent, 'Chi tiết hỗ trợ');
  assert.doesNotMatch(shown(ui.root), /CUM_GOC_DEMO|SECRET_DEMO/);
});
test('Đầu vào không bị cắt ngầm: rỗng, quá trần văn bản/giá trị/nhóm/số mục đều không gửi', async () => {
  const ui = setup(); await ui.view.san_sang;
  const input = field(ui.root, 'Văn bản DEMO cần che'), known = field(ui.root, 'Định danh đã biết (tùy chọn)');
  for (const [text, ids] of [[' ', ''], ['x'.repeat(500001), ''], ['DEMO', 'x'.repeat(301)],
    ['DEMO', 'Tên DEMO | ' + 'x'.repeat(21)], ['DEMO', Array(501).fill('DEMO').join('\n')]]) {
    change(input, text); change(known, ids); await submit(ui.root); assert.equal(ui.requests.length, 0);
  }
  change(input, 'x'.repeat(500000)); change(known, ''); await submit(ui.root);
  assert.equal(ui.requests.length, 1); assert.equal(ui.requests[0].body.van_ban.length, 500000);
  change(field(ui.root, 'Văn bản có bí danh'), 'x'.repeat(500001)); await submit(ui.root, 1);
  assert.equal(ui.requests.length, 1);
});
test('Hai lần gửi chỉ một request; sửa đầu vào/mẫu bỏ kết quả và mã yêu cầu cũ', async () => {
  let resolve; const ui = setup({ mask: () => new Promise(r => { resolve = r; }) }); await ui.view.san_sang;
  const pending = submit(ui.root); await submit(ui.root); assert.equal(ui.requests.length, 1);
  assert.equal(button(ui.root, 'Che').disabled, true); resolve(masked()); await pending;
  change(field(ui.root, 'Định danh đã biết (tùy chọn)'), 'DEMO');
  assert.doesNotMatch(shown(field(ui.root, 'Kết quả che')), /Số chỗ thay/);
  change(field(ui.root, 'Văn bản có bí danh'), '[[CT-0001]]'); await submit(ui.root, 1);
  assert.equal(ui.requests.length, 1);
  await button(ui.root, 'Dùng mẫu DEMO').click(); assert.equal(field(ui.root, 'Văn bản có bí danh').value, '');
});
test('Rời màn khi đang gửi hủy signal, bỏ kết quả muộn và mọi nút cũ', async () => {
  let resolve; const ui = setup({ mask: () => new Promise(r => { resolve = r; }) }); await ui.view.san_sang;
  const oldForm = find(ui.root, 'form')[0], pending = submit(ui.root), oldBack = button(ui.root, 'Quay lại Che định danh');
  ui.view.dung(); assert.equal(ui.requests[0].opt.signal.aborted, true);
  resolve(masked()); await pending; await oldForm.events.submit({ preventDefault() {} }); await oldBack.events.click();
  assert.equal(ui.root.children.length, 0); assert.equal(ui.requests.length, 1);
});
test('Hủy lúc xác minh quyền không dựng lại màn; quyền bị thu hồi chặn cả Quay lại', async () => {
  let resolve; const controller = new AbortController();
  const pending = setup({ signal: controller.signal, auth: () => new Promise(r => { resolve = r; }) });
  controller.abort(); resolve(inventory()); await pending.view.san_sang; assert.equal(pending.root.children.length, 0);
  let backs = 0; const ui = setup({ back: () => { backs++; } }); await ui.view.san_sang; await submit(ui.root);
  ui.kb.khong_quyen = true; await button(ui.root, 'Quay lại Che định danh').click();
  assert.equal(backs, 0); assert.equal(find(ui.root, 'form').length, 0); assert.doesNotMatch(shown(ui.root), /CT-0001/);
});
test('API mất quyền lúc mở che xóa mọi nội dung và không giữ mã để thử lại', async () => {
  const ui = setup({ unmask: () => { throw { status: 403 }; } }); await ui.view.san_sang;
  await submit(ui.root); await submit(ui.root, 1);
  assert.equal(find(ui.root, 'form').length, 0); assert.doesNotMatch(shown(ui.root), /CT-0001|YEUCau-DEMO/);
});
test('Phản hồi hỏng không hiển thị như thành công và không giữ kết quả trước', async () => {
  let bad = false; const ui = setup({ mask: () => bad ? { ...masked(), so_cho_thay: 'SECRET_DEMO' } : masked() });
  await ui.view.san_sang; await submit(ui.root); bad = true; await submit(ui.root);
  assert.doesNotMatch(shown(field(ui.root, 'Kết quả che')), /Số chỗ thay: 2|SECRET_DEMO/);
  assert.equal(field(ui.root, 'Văn bản có bí danh').value, '');
});
function integration({ deny = false, load = 'ok', inject = false } = {}) {
  const root = dom(), context = vm.createContext({ AbortController, console, addEventListener() {} });
  context.fetch = () => assert.fail('Không gọi mạng'); vm.runInContext(adminSource, context);
  const append = root.ownerDocument.head.append.bind(root.ownerDocument.head);
  root.ownerDocument.head.append = script => {
    append(script); assert.equal(script.src, '/core/ui/chay_thu_mask.js');
    if (load === 'pending') return; if (load === 'error') return script.onerror();
    vm.runInContext(source, context); script.onload();
  };
  const sdk = { api: { goi: async req => {
    if (deny) throw { status: 403 };
    return req.duong_dan.endsWith('/kiem-ke') ? inventory() : { danh_sach: [], con_tiep: false };
  } } };
  const requests = [], api_mask = inject ? { che_van_ban: async body => { requests.push(body); return masked(); },
    mo_che_van_ban: async () => unmasked() } : undefined;
  const view = context.KttQuanTri.dung(root, { sdk, loai: 'engine', api_mask,
    khai_bao_da_loc_quyen: { ma: 'quan_ly_engine', thao_tac: [] } });
  return { root, context, view, requests };
}
test('Đường vào Quản lý engine → Mask → DEMO → quay lại; bản thật báo chưa sẵn sàng', async () => {
  const ui = integration(); await ui.view.san_sang;
  await button(ui.root, 'Xem chi tiết Che dữ liệu nhạy cảm').click(); await button(ui.root, 'Chạy thử DEMO').click();
  assert.ok(field(ui.root, 'Văn bản DEMO cần che')); assert.match(shown(ui.root), /Engine chưa sẵn sàng/);
  await button(ui.root, 'Quay lại Che định danh').click(); assert.equal(find(ui.root, 'form').length, 0);
  assert.ok(button(ui.root, 'Chạy thử DEMO')); ui.view.dung(); assert.equal(ui.root.children.length, 0);
});
test('Seam được truyền từ quản trị; link ngoài DEMO kết thúc view, form cũ không gửi tiếp', async () => {
  const ui = integration({ inject: true }); await ui.view.san_sang;
  await button(ui.root, 'Xem chi tiết Che dữ liệu nhạy cảm').click(); const backList = button(ui.root, 'Quay lại danh sách');
  await button(ui.root, 'Chạy thử DEMO').click(); await submit(ui.root); assert.equal(ui.requests.length, 1);
  const oldForm = find(ui.root, 'form')[0]; await backList.click();
  await oldForm.events.submit({ preventDefault() {} }); assert.equal(ui.requests.length, 1);
  assert.ok(button(ui.root, 'Xem chi tiết Che dữ liệu nhạy cảm'));
});
test('Nạp JS thất bại có lỗi nghiệp vụ và hỗ trợ thu gọn; 403 không có đường DEMO', async () => {
  const ui = integration({ load: 'error' }); await ui.view.san_sang;
  await button(ui.root, 'Xem chi tiết Che dữ liệu nhạy cảm').click(); await button(ui.root, 'Chạy thử DEMO').click();
  assert.match(shown(ui.root), /Chưa tải được màn Chạy thử DEMO/);
  assert.equal(find(ui.root, 'details').length, 1); assert.equal(find(ui.root, 'form').length, 0);
  const denied = integration({ deny: true }); await denied.view.san_sang;
  assert.equal(button(denied.root, 'Chạy thử DEMO'), undefined);
});
test('Đóng quản trị khi JS đang nạp không dựng màn muộn', async () => {
  const ui = integration({ load: 'pending' }); await ui.view.san_sang;
  await button(ui.root, 'Xem chi tiết Che dữ liệu nhạy cảm').click(); const pending = button(ui.root, 'Chạy thử DEMO').click();
  const script = ui.root.ownerDocument.head.children[0]; ui.view.dung();
  vm.runInContext(source, ui.context); script.onload(); await pending; assert.equal(ui.root.children.length, 0);
});
test('JS mới chỉ được phục vụ trong _TINH; không thêm đường gọi engine trực tiếp', () => {
  const app = fs.readFileSync(path.join(dir, 'ung_dung.py'), 'utf8');
  const section = app.slice(app.indexOf('_TINH = {'), app.indexOf('_LOI_NAP_MODULE ='));
  assert.ok(section.includes("'/core/ui/chay_thu_mask.js': (_CORE / 'ui/chay_thu_mask.js', 'text/javascript; charset=utf-8')"));
  assert.doesNotMatch(source, /\bfetch\s*\(|localStorage|sessionStorage|innerHTML|api\.openai|api\.anthropic/);
});
