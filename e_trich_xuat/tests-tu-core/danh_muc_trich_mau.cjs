'use strict';
// LOAI-HD-0 + LHD-U1a: mở rộng tệp có sẵn. DOM giả; không máy chủ, không ghi.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const UI = require('../src/kho_tri_thuc/core/ui/danh_muc_trich_mau.js');

class El {
  constructor(tag) { this.tagName = tag; this.children = []; this.attrs = {}; this.events = {}; this._text = ''; this.disabled = false; this.className = ''; this.checked = false; this.value = ''; }
  set textContent(t) { this._text = String(t); this.children = []; }
  get textContent() { return this._text + this.children.map(c => c.textContent).join(' '); }
  set innerHTML(t) { throw new Error('Không được dùng innerHTML'); }
  append(...n) { this.children.push(...n); }
  replaceChildren(...n) { this._text = ''; this.children = n; }
  setAttribute(k, v) { this.attrs[k] = v; }
  addEventListener(k, f) { this.events[k] = f; }
  click() { if (!this.disabled) this.events.click?.(); }
  change(v) { if (v !== undefined) { this.value = v; this.checked = v; } this.events.change?.(); }
}
const all = r => [r, ...r.children.flatMap(all)];
const doc = { createElement: t => new El(t) };
function setup(options = {}) {
  const root = doc.createElement('div'); root.ownerDocument = doc;
  UI.dung(root, { bay_gio: () => new Date(2026, 10, 6, 18, 5), ...options }); return root;
}
const nut = (r, t) => all(r).find(n => n.tagName === 'button' && n.textContent === t);
const aria = (r, l) => all(r).find(n => n.attrs['aria-label'] === l);
const text = r => r.textContent;
function chonTep(r, name = 'Danh mục giả.xlsx', size = 1024) {
  const input = aria(r, 'Chọn tệp Excel danh mục');
  assert.equal(input.type, 'file'); assert.equal(input.accept, '.xlsx');
  input.files = [{ name, size, arrayBuffer() { throw new Error('Không được đọc nội dung tệp'); },
    text() { throw new Error('Không được đọc nội dung tệp'); } }];
  input.change();
}

test('màn Loại hợp đồng: nhãn, 3 loại, XD 37 tham số, không xưng hô', () => {
  const r = setup();
  assert.match(text(r), /DỮ LIỆU GIẢ ĐỂ XEM GIAO DIỆN — chưa nối engine trích xuất/);
  assert.match(text(r), /Dữ liệu giả — chỉ để góp ý giao diện/);
  assert.match(text(r), /Danh mục dùng chung toàn hệ thống/);
  assert.match(text(r), /Dịch vụ bản gọn/);
  assert.match(text(r), /Hợp đồng xây dựng/); assert.match(text(r), /37/);
  assert.match(text(r), /Loại gốc — phải ra kết quả giống công cụ gốc/);
  assert.match(text(r), /Chưa có kiểm logic riêng/);
  assert.doesNotMatch(text(r), /\bAnh\b|\bbạn\b/);
  assert.equal(all(r).filter(n => n.tagName === 'tr').length, 4);
});
test('thêm loại và ngừng/dùng lại', () => {
  const r = setup();
  nut(r, 'Thêm loại').click();
  aria(r, 'Mã loại').value = 'TV'; aria(r, 'Mã loại').change();
  aria(r, 'Tên').value = 'Hợp đồng tư vấn'; aria(r, 'Tên').change();
  nut(r, 'Lưu').click();
  assert.match(text(r), /Hợp đồng tư vấn/);
  all(r).filter(n => n.tagName === 'button' && n.textContent === 'Ngừng').pop().click();
  assert.ok(nut(r, 'Dùng lại'));
});
test('import: tệp lỗi khóa nút Lưu; tệp đạt lưu nháp và so sánh phiên bản', () => {
  const r = setup();
  nut(r, 'Import danh mục').click();
  assert.equal(nut(r, 'Kiểm tra').disabled, true);
  chonTep(r);
  nut(r, 'Tải mẫu Excel trống').click();
  assert.match(text(r), /Mẫu trống/);
  aria(r, 'Tệp danh mục').change('loi'); aria(r, 'Tệp danh mục').value = 'loi'; aria(r, 'Tệp danh mục').change();
  nut(r, 'Kiểm tra').click();
  assert.match(text(r), /Thiếu cột bắt buộc/); assert.match(text(r), /trùng/); assert.match(text(r), /ngoài khoảng 0–3/);
  assert.match(text(r), /Bảng kiểm từng dòng — dữ liệu giả/);
  assert.equal(nut(r, 'Lưu thành phiên bản nháp').disabled, true);
  aria(r, 'Tệp danh mục').value = 'dat'; aria(r, 'Tệp danh mục').change();
  nut(r, 'Kiểm tra').click();
  assert.match(text(r), /Khác biệt so với bản đang dùng/);
  nut(r, 'Lưu thành phiên bản nháp').click();
  assert.match(text(r), /Đã lưu phiên bản 4/);
  assert.match(text(r), /06\/11\/2026/);
  assert.equal(nut(r, 'So sánh').disabled, true);
  aria(r, 'Chọn phiên bản 4').change(true); aria(r, 'Chọn phiên bản 3').change(true);
  assert.equal(nut(r, 'So sánh').disabled, false);
  nut(r, 'So sánh').click();
  assert.match(text(r), /Khác biệt giữa phiên bản 3 và phiên bản 4/);
});

test('xem tham số XD 37, DV bản gọn 30 và loại chưa có danh mục', () => {
  const r = setup();
  for (const [i, n, ten] of [[0, 37, 'Hợp đồng xây dựng'], [1, 30, 'Hợp đồng dịch vụ'], [2, 0, 'Hợp đồng mua hàng hóa']]) {
    all(r).filter(x => x.tagName === 'button' && x.textContent === 'Xem tham số')[i].click();
    assert.match(text(r), new RegExp(`Danh mục tham số — ${ten}`));
    const tables = all(r).filter(x => x.tagName === 'table');
    if (n) assert.equal(all(tables.at(-1)).filter(x => x.tagName === 'tr').length, n + 1);
    else assert.match(text(r), /Chưa có danh mục tham số/);
    if (i === 1) assert.match(text(r), /Phí dịch vụ \(VND\)/);
    nut(r, 'Đóng danh mục tham số').click();
  }
});

test('nhập DV: tóm tắt và bảng từng dòng đúng 30, lưu nháp rồi xem lịch sử', () => {
  const r = setup(); nut(r, 'Import danh mục').click();
  aria(r, 'Loại hợp đồng').change('DV'); chonTep(r); nut(r, 'Kiểm tra').click();
  assert.match(text(r), /Số tham số: 30 · đang dùng: 28/);
  assert.match(text(r), /toàn bộ tham số là mới/);
  const table = all(r).find(x => x.tagName === 'table' && x.textContent.startsWith('Dòng Nội dung'));
  assert.equal(all(table).filter(x => x.tagName === 'tr').length, 31);
  nut(r, 'Lưu thành phiên bản nháp').click();
  assert.match(text(r), /Đã lưu phiên bản 2/);
  nut(r, 'Loại hợp đồng').click();
  const dv = all(r).find(x => x.tagName === 'tr' && x.textContent.startsWith('Hợp đồng dịch vụ'));
  nut(dv, 'Xem phiên bản').click();
  assert.match(text(r), /Phiên bản 2 06\/11\/2026 Quản trị DEMO Nháp/);
  assert.match(dv.textContent, /Chưa có phiên bản đang dùng/);
});

test('đổi tệp/loại xóa kết quả cũ; tệp sai định dạng/quá lớn không lưu nháp', () => {
  const r = setup(); nut(r, 'Import danh mục').click(); chonTep(r); nut(r, 'Kiểm tra').click();
  assert.ok(nut(r, 'Lưu thành phiên bản nháp'));
  for (const [name, size] of [['Sai.xls', 100], ['Lon.xlsx', 2 * 1024 * 1024 + 1]]) {
    chonTep(r, name, size); assert.equal(nut(r, 'Lưu thành phiên bản nháp'), undefined);
    nut(r, 'Kiểm tra').click();
    assert.match(text(r), /không quá 2 MiB/);
    assert.equal(nut(r, 'Lưu thành phiên bản nháp').disabled, true);
  }
  chonTep(r, 'Đúng.XLSX', 2 * 1024 * 1024); nut(r, 'Kiểm tra').click();
  assert.equal(nut(r, 'Lưu thành phiên bản nháp').disabled, false);
  aria(r, 'Loại hợp đồng').change('DV');
  assert.equal(nut(r, 'Kiểm tra').disabled, true);
  assert.equal(nut(r, 'Lưu thành phiên bản nháp'), undefined);
});

test('tên tệp và nội dung sửa chỉ là text; DOM không diễn giải HTML', () => {
  const r = setup(); nut(r, 'Import danh mục').click();
  chonTep(r, '<img src=x onerror=alert(1)>.xlsx');
  assert.match(text(r), /<img src=x onerror=alert\(1\)>\.xlsx/);
  assert.equal(all(r).some(x => ['img', 'script'].includes(x.tagName)), false);
  nut(r, 'Kiểm tra').click(); assert.match(text(r), /Bảng kiểm từng dòng/);
  nut(r, 'Loại hợp đồng').click(); nut(r, 'Sửa tên/mô tả').click();
  aria(r, 'Tên').value = '<script>giả</script>'; aria(r, 'Tên').change();
  nut(r, 'Lưu').click(); assert.match(text(r), /<script>giả<\/script>/);
  assert.equal(all(r).some(x => x.tagName === 'script'), false);
});

test('không có quyền sửa: nút mờ có chú thích, vẫn xem được lịch sử và tham số', () => {
  const r = setup({ quyen_sua: false });
  for (const t of ['Thêm loại', 'Sửa tên/mô tả', 'Ngừng']) {
    assert.equal(nut(r, t).disabled, true); assert.match(nut(r, t).title, /Chưa được cấp quyền/);
  }
  nut(r, 'Thêm loại').click(); assert.equal(aria(r, 'Tên'), undefined);
  nut(r, 'Xem tham số').click(); assert.match(text(r), /Danh mục tham số —/);
  nut(r, 'Import danh mục').click();
  assert.equal(aria(r, 'Chọn tệp Excel danh mục').disabled, true);
  assert.equal(nut(r, 'Kiểm tra').disabled, true);
  assert.ok(aria(r, 'Chọn phiên bản 3'));
});

test('đóng màn hủy thao tác cũ; dữ liệu giả chỉ tồn tại trong một lần mở', () => {
  const controller = new AbortController(), r = setup({ signal: controller.signal });
  const old = nut(r, 'Import danh mục'); controller.abort(); old.click(); assert.equal(text(r), '');
  const closed = new AbortController(); closed.abort(); assert.equal(text(setup({ signal: closed.signal })), '');
  const first = setup(); nut(first, 'Thêm loại').click();
  aria(first, 'Mã loại').change('TV'); aria(first, 'Tên').change('Tư vấn giả'); nut(first, 'Lưu').click();
  assert.match(text(first), /Tư vấn giả/); assert.doesNotMatch(text(setup()), /Tư vấn giả/);
});

const quanTri = fs.readFileSync(path.join(__dirname, '../src/kho_tri_thuc/core/ui/quan_tri.js'), 'utf8');
function shellMau(search = '?du_lieu_gia=1', kb = { module: { ma: 'core', phan: [] } }, page = {}) {
  const events = {}, calls = [], r = doc.createElement('div'); r.ownerDocument = doc;
  let options;
  const browser = { location: { search }, addEventListener: (n, f) => { events[n] = f; },
    KttDanhMucTrichMau: UI, KttShell: { dung: o => { options = o; } } };
  vm.runInNewContext(quanTri, { globalThis: browser, AbortController,
    fetch() { calls.push('fetch'); throw new Error('Không được gọi API'); } });
  events.DOMContentLoaded();
  browser.KttShell.dung({ khai_bao_da_loc_quyen: kb });
  options.mo_trang({ module: 'core', phan: { ma: 'danh_muc_trich', ...page }, root: r });
  return { options, r, calls };
}

test('ô quản trị dùng màn cũ, không trùng ô; chỉ mở dữ liệu giả và không gọi API', () => {
  const ui = shellMau();
  assert.equal(ui.options.khai_bao_da_loc_quyen.module.phan.filter(x => x.ma === 'danh_muc_trich').length, 1);
  assert.match(text(ui.r), /Danh mục trích xuất/);
  nut(ui.r, 'Import danh mục').click(); chonTep(ui.r); nut(ui.r, 'Kiểm tra').click();
  nut(ui.r, 'Lưu thành phiên bản nháp').click(); assert.deepEqual(ui.calls, []);
  for (const slot of ['phan', 'the']) {
    const dupe = shellMau('?du_lieu_gia=1', { module: { ma: 'core', [slot]: [{ ma: 'danh_muc_trich' }] } });
    const m = dupe.options.khai_bao_da_loc_quyen.module;
    assert.equal([...(m.phan || []), ...(m.the || [])].filter(x => x.ma === 'danh_muc_trich').length, 1);
  }
});

test('không mở màn giả nếu thiếu cờ hoặc khai báo từ chối quyền', () => {
  for (const s of ['', '?du_lieu_gia=10', '?du_lieu_gia=0']) assert.equal(text(shellMau(s).r), '');
  for (const kb of [{ khong_quyen: true, module: { ma: 'core' } },
    { module: { ma: 'core', khong_quyen: true } }, { module: { ma: 'crm' } },
    { module: { ma: 'core', phan: [{ ma: 'danh_muc_trich', khong_quyen: true }] } }]) {
    assert.equal(text(shellMau('?du_lieu_gia=1', kb).r), '');
  }
  assert.equal(text(shellMau('?du_lieu_gia=1', undefined, { khong_quyen: true }).r), '');
});
const hdTen = i => `Hợp đồng mẫu số 0${i} — Hợp đồng dịch vụ (DEMO)`;
function chayThuDV(r, { loi = false, xong = true } = {}) {
  nut(r, 'Loại hợp đồng').click();
  nut(all(r).find(x => x.tagName === 'tr' && x.textContent.startsWith('Hợp đồng dịch vụ')), 'Chạy thử bản nháp').click();
  assert.match(text(r), /Phiên bản đang dùng: chưa có → phiên bản nháp sẽ kích hoạt: Phiên bản 1/);
  if (loi) aria(r, 'Tình huống chạy thử').change('loi');
  [1, 2, 3].forEach(i => aria(r, hdTen(i)).change(true));
  nut(r, 'Gửi chạy thử').click();
  if (xong) for (let k = 0; k < 3; k++) nut(r, 'Cập nhật tiến độ (mô phỏng)')?.click();
}
test('chạy thử: cần 3 hợp đồng, trạng thái chờ/đang chạy/xong, ô vàng có lý do', () => {
  const r = setup();
  nut(r, 'Chạy thử').click();
  assert.equal(nut(r, 'Gửi chạy thử').disabled, true);
  aria(r, hdTen(1)).change(true); aria(r, hdTen(2)).change(true);
  assert.equal(nut(r, 'Gửi chạy thử').disabled, true);
  aria(r, hdTen(3)).change(true);
  nut(r, 'Gửi chạy thử').click();
  assert.match(text(r), /Đang chạy/); assert.match(text(r), /Chờ/);
  assert.equal(nut(r, 'Kích hoạt phiên bản này').disabled, true);
  nut(r, 'Cập nhật tiến độ (mô phỏng)').click(); assert.match(text(r), /Xong/);
  nut(r, 'Cập nhật tiến độ (mô phỏng)').click(); nut(r, 'Cập nhật tiến độ (mô phỏng)').click();
  assert.match(text(r), /Việc ở vị trí thứ 1/); assert.match(text(r), /Số ô cần xem/);
  assert.equal(nut(r, 'Cập nhật tiến độ (mô phỏng)'), undefined);
  const vang = all(r).find(n => n.tagName === 'td' && n.className === 'vang');
  assert.ok(vang); vang.click(); assert.match(text(r), /Lý do cần xem/);
  assert.equal(nut(r, 'Kích hoạt phiên bản này').disabled, false);
});
test('luồng danh sách → bản nháp → chạy thử → kích hoạt hai bước → danh sách có phiên bản mới', () => {
  const r = setup(); chayThuDV(r);
  nut(r, 'Kích hoạt phiên bản này').click();
  assert.match(text(r), /Tổng số ô cần xem/);
  assert.match(text(r), /Phiên bản đang dùng: chưa có → phiên bản mới: Phiên bản 1/);
  assert.equal(nut(r, 'Xác nhận kích hoạt').disabled, true);
  aria(r, 'Lý do kích hoạt').value = 'ngắn'; aria(r, 'Lý do kích hoạt').events.input();
  assert.equal(nut(r, 'Xác nhận kích hoạt').disabled, true);
  aria(r, 'Lý do kích hoạt').value = 'Đã chạy thử đạt yêu cầu'; aria(r, 'Lý do kích hoạt').events.input();
  assert.equal(nut(r, 'Xác nhận kích hoạt').disabled, false);
  nut(r, 'Bỏ qua').click(); assert.doesNotMatch(text(r), /Tổng số ô cần xem/);
  nut(r, 'Kích hoạt phiên bản này').click();
  aria(r, 'Lý do kích hoạt').value = 'Đã chạy thử đạt yêu cầu'; aria(r, 'Lý do kích hoạt').events.input();
  nut(r, 'Xác nhận kích hoạt').click();
  assert.match(text(r), /Đã kích hoạt Hợp đồng dịch vụ: chưa có bản đang dùng → Phiên bản 1 ngày 06\/11\/2026/);
  assert.match(text(r), /Phiên bản 1 · 04\/11\/2026/);
});
test('chạy thử có hợp đồng lỗi: không kích hoạt được', () => {
  const r = setup(); chayThuDV(r, { loi: true });
  assert.match(text(r), /Lỗi/); assert.match(text(r), /1 hợp đồng bị lỗi/);
  assert.equal(nut(r, 'Kích hoạt phiên bản này').disabled, true);
  nut(r, 'Kích hoạt phiên bản này').click(); assert.doesNotMatch(text(r), /Tổng số ô cần xem/);
});
test('không có quyền kích hoạt: ẩn nút, thông báo trung tính; vẫn chạy thử được', () => {
  const r = setup({ quyen_kich_hoat: false }); chayThuDV(r);
  assert.equal(nut(r, 'Kích hoạt phiên bản này'), undefined);
  assert.match(text(r), /Chưa được cấp quyền kích hoạt danh mục trích xuất/);
  assert.doesNotMatch(text(r), /\bAnh\b|\bbạn\b/);
});
test('hiển thị chỉ là text; nhãn dữ liệu giả; bảng loại không có mã kỹ thuật', () => {
  const r = setup(); chayThuDV(r);
  assert.match(text(r), /Dữ liệu giả — chỉ để góp ý giao diện/);
  assert.equal(all(r).some(n => ['img', 'script'].includes(n.tagName)), false);
  nut(r, 'Loại hợp đồng').click();
  const tbl = all(r).find(n => n.tagName === 'table');
  assert.equal(all(tbl).filter(n => n.tagName === 'th').some(n => /Mã loại/.test(n.textContent)), false);
  const cells = all(tbl).filter(n => n.tagName === 'td' || n.tagName === 'th').flatMap(n => [n._text]).filter(Boolean);
  assert.deepEqual(cells.filter(t => /^[A-Z_]{2,}$/.test(t.trim())), []);
  assert.doesNotMatch(tbl.textContent, /\b(MUA_HH|XD|DV)\b/);
  nut(r, 'Xem tham số').click();
  assert.doesNotMatch(text(r), /\bTT-\d+/);
});
